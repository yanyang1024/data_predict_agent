下面给你一份可以直接当设计稿讨论的版本。

# AI Portal 执行层沙盒与环境管理方案（建议稿）

## 0. 结论

你现在最合适的不是在“环境写成 skill”与“容器隔离”之间二选一，而是把两者分工：**skill/模板负责环境定义与可复现，sandbox/容器/微 VM 负责真正的安全隔离。** 结合你仓库当前完成度，第一版不该重做 WebSDK 侧会话；你现在更应该新增的是一个 `SandboxBroker`/runner 层，把会执行 shell、写文件、联网、改 OpenWork workspace 的资源，从共享 OpenCode 里分流出来。你的 repo 已经是 V2 结构，BFF、OpenCode/OpenWork/WebSDK 的主链路都跑通了，服务测试与 Web UI 测试也已经覆盖到 `direct_chat`、`skill_chat`、`kb_websdk`、`agent_websdk` 等资源类型。([GitHub][1])

## 1. 基于你当前项目完成度的判断

你的门户骨架其实已经够用了。当前 FastAPI BFF 已经有 Auth、ACL、Catalog、Session Center、Launch Record Center，以及 OpenCode/SkillChat/WebSDK/OpenWorkAdapter；而且 OpenWorkAdapter 已经做到了 workspace 级别的 `config / commands / mcp / audit / events / opencode-proxy` 能力探测。这意味着你不需要推翻门户架构，只需要在 adapter 前面再插一层“执行策略 + runner 分配”。([GitHub][1])

更关键的是，你仓库里的实现说明已经把 WebSDK 一版边界写得很清楚：**统一入口 + 启动记录统一**，而不是 Portal 自己去托管 WebSDK 的历史/回溯。再加上你自己给的背景里，这批旧智能体应用和知识库应用本来就已经是成型应用，所以 v1 不应该把精力浪费在重做它们的会话控制，而是把“Portal 自己发起的执行型资源”隔离好。([GitHub][2])

不过上线前有三个基础坑得先补：Implementation 里仍把 `MemoryStore`/`RedisStore` 写成生产可选，但 `config.py` 已经写明 Redis 支持移除、当前总是 memory store；同一份 Implementation 还明确记录了 `launch_token` 仍是随机串，ACL 仍是“未配置即放行”。所以单靠加沙盒，并不能自动解决越权、审计和恢复这几类问题。([GitHub][2])

## 2. 你两个想法该怎么取舍

### 想法一：把环境写成 skill / workflow

这个想法应该保留，但**只能把它当“环境定义层”**，不能把它当安全边界。现在主流 coding agent 的做法，是一边用结构化环境定义保证可复现，一边再用 sandbox 去限制写权限、网络和命令执行范围。Dev Container 规范就是这种“环境即代码”的成熟形式：`devcontainer.json` 和生命周期脚本能确定性地创建开发容器；而 OpenAI 对 Codex 的定义也非常直接：sandbox 才是避免 agent 获得整机访问权限的边界。([容器开发][3])

我的建议是：**skill 描述环境，broker 强制执行环境。** 也就是 skill 里声明“需要什么镜像、什么工具链、是否可联网、是否允许写文件、工作区粒度是什么”，但真正执行时还是由容器/微 VM runtime 去 enforce。

### 想法二：每用户或每会话创建 Docker/容器环境

这才是真正的隔离机制，但不建议默认做到“每条消息都新建一个全新环境”。OpenAI 的 cloud environments 采用的是“环境定义 + setup 阶段 + agent 阶段 + 缓存复用”的模型；CLI/IDE 默认也是把写权限限制在当前 workspace，并把网络和审批拆开控制。对你的企业内研发门户，默认粒度更适合做成：**每用户 × 每项目/工作区一个 warm sandbox，空闲 TTL 回收；高风险任务再升到每会话/每任务单独 sandbox。** ([OpenAI开发者][4])

## 3. 推荐的目标架构

我建议你把执行路径拆成三条车道：

* `shared`：纯文本/纯模型型对话，继续复用共享 OpenCode。
* `embedded`：`kb_websdk / agent_websdk / iframe`，继续保持“统一入口 + 启动记录”，不把它们再拉进 Portal 的执行沙盒。
* `sandboxed`：会触发 shell、文件写入、包安装、联网、仓库修改、OpenWork workspace 变更的资源，统一走 `SandboxBroker -> Runner`。([GitHub][1])

可以把它理解成：

```text
Portal UI / FastAPI BFF
  ├─ shared lane    -> shared OpenCode（只限低风险聊天）
  ├─ embedded lane  -> WebSDK / Iframe（只记 launch / audit）
  └─ sandboxed lane -> SandboxBroker -> Runner -> OpenCode / OpenWork in sandbox
```

这条线最适合你现在的原因，是它只在“危险执行面”加新层，不去打乱已经跑通的门户和 WebSDK 接入。

## 4. 三条可选路线

### 路线 A：独立 runner 节点/VM + rootless 容器

**这是我主推的路线。**

做法是：Portal BFF、SSO、OpenWork 控制面继续放在受信区；新增一个 `SandboxBroker`，把高风险资源调度到 runner。Runner 侧优先用 rootless Docker 或 Podman：Docker 官方说明 rootless 会把 daemon 和 container 都放到 user namespace 里，以 non-root 方式运行；Podman 是 daemonless，官方文档也单独给了 rootless 教程。对你这种“想简单有效、又想尽量吃满自有服务器资源”的场景，这条线性价比最高。([Docker Documentation][5])

这条线的重点不是“用了 Docker 就安全”，而是把默认基线收紧：根文件系统只读；可写目录只给 `/workspace` 和 `/tmp`；用 volume 而不是大范围 bind mount；限制 CPU / 内存 / PID；默认 `cap-drop all`；启用 seccomp 和 AppArmor/SELinux；容器内默认非 root 用户；**永远不要挂 host Docker socket**。Docker 文档明确给出了 `--read-only`、`--pids-limit`、`--memory` 等限制项，也明确说明 bind mount 默认可修改宿主文件，而 capabilities、seccomp、AppArmor 都应该按最小权限使用。([Docker Documentation][6])

### 路线 B：gVisor / Kata / Firecracker / 微 VM 强隔离

**适合高敏或高风险资源，作为二期升级。**

gVisor 的思路是把很多原本由 host kernel 提供的接口，搬进每个 sandbox 自己的 userspace application kernel；Kata Containers 走 lightweight VM，强调“容器体验 + 硬件虚拟化隔离”；Firecracker 是专门为安全多租户函数/容器服务做的 microVM。Docker Sandboxes 展示的也是这条路线：每个 agent 一台 microVM、独立 network、独立 inner Docker engine、host 侧 credential proxy，但官方文档同时标了 Experimental。对你来说，这条路线很适合 `allow_docker=true`、敏感代码仓库、或高价值内部数据集，但不必一上来全量使用。([gVisor][7])

### 路线 C：直接引入专门的 sandbox 平台

**适合不想自己维护 runner 调度层。**

Daytona 把自己定义为“open-source, secure and elastic infrastructure for running AI-generated code”，并且官方专门给了 OpenCode SDK 的接法：启动时创建 sandbox、在 sandbox 里安装 OpenCode、启动 server，退出时删除 sandbox。E2B 也有现成的 `opencode` template；企业版 BYOC 可以把模板、快照和运行日志都放到客户自己的 VPC 里。优点是上线快、少造轮子；代价是多一个平台依赖和新的控制面。([Daytona][8])

**综合建议顺序：A 为主线，B 做高风险增量，C 作为不想自建 runtime 的替代。**

## 5. 我建议你现在就落地的方案

### 5.1 资源策略模型

你当前已经有 `direct_chat / skill_chat / openai_compatible_v1` 和 `kb_websdk / agent_websdk / iframe` 这些资源类型，所以最省事的做法，是直接在资源元数据里加执行策略字段。([GitHub][1])

建议增加这样的字段：

```jsonc
{
  "execution_mode": "shared | embedded | sandboxed",
  "sandbox_template": "python-default",
  "workspace_scope": "user | project | session",
  "network_policy": "off | allowlist | internet",
  "persistence": "ephemeral | ttl | persistent",
  "allow_shell": true,
  "allow_file_write": true,
  "allow_docker": false,
  "approval_policy": "never | on-request | untrusted",
  "risk_level": "low | medium | high"
}
```

默认规则我建议这样定：

* `kb_websdk / agent_websdk / iframe` → `embedded`
* 纯问答类 `direct_chat` → `shared`
* 任何 `skill_chat` 只要涉及 shell / 文件写入 / 联网 / 仓库操作 → `sandboxed`
* OpenWork 的 workspace 读接口可共享，写接口与 reload 一律 `sandboxed`

### 5.2 环境怎么定义

环境定义建议用 **skill manifest + devcontainer / Dockerfile 模板** 两层表达。每个 skill 对应一个 `devcontainer.json` 或镜像模板，利用 `onCreateCommand / updateContentCommand / postCreateCommand` 去安装依赖、准备工具链和初始化 workspace。这样你想要的“环境稳定、少随机性”是能做到的，而且它是标准化的，不是靠 prompt 去约束。([容器开发][3])

也就是说，想法 1 不要丢，但它的职责是：

* 定义环境；
* 约束工作流；
* 固化依赖和工具链；
* 让不同用户、不同 runner 的行为尽量一致。

安全边界仍然由容器/微 VM 提供。

### 5.3 runner 的隔离基线

这里是最关键的部分。

第一，**优先把 runner 与 Portal/OpenWork 控制面分开。** 最好是独立 runner VM/节点；实在做不到，至少也要是同机不同受限用户、不同 runtime、不同资源组。

第二，runner 默认策略建议是：

* rootless Podman 或 rootless Docker；
* 非 root 容器用户；
* rootfs 只读；
* 只给 `/workspace` 和 `/tmp` 写权限；
* 不挂宿主大目录，只挂最小 workspace volume；
* `no-new-privileges`；
* `cap-drop all`，按需加白；
* 默认 seccomp / AppArmor；
* CPU / 内存 / PID 上限；
* 禁止 host PID/IPC/network namespace；
* 禁止 `privileged`；
* **禁止 host docker.sock**。([Docker Documentation][5])

这套基线的直接效果，是把你最担心的三类问题都压下去：

* 误删宿主文件：因为不再给大范围 host bind mount；
* 杀宿主稳定服务：因为 agent 只在自己的 namespace/cgroup 里活动，外加 PID/CPU/内存限制；
* 数据串读：因为不同用户/项目的 workspace 与凭证都不共用。

### 5.4 网络和凭证怎么管

主流做法已经很明确了：**出口代理 + allowlist + 短时凭证**。

Docker Sandboxes 的参考设计是：所有 HTTP/HTTPS 出口都先过 host proxy，只允许策略里列出的域名，直接拦截 raw TCP/UDP/ICMP、private IP、loopback 和 link-local；模型 API 的认证头由代理注入，而不是把长期密钥直接放进 sandbox。OpenAI 的 Codex cloud 也是 setup 可联网、agent 阶段默认断网，且 secrets 只在 setup 阶段可用，进入 agent 阶段前会移除。([Docker Documentation][9])

结合你的场景，我建议：

* 首次建环境或更新依赖时：允许 setup 阶段联网；
* 进入 agent phase 后：默认 `off` 或 `allowlist`；
* Git / 制品库 / 模型供应商 token：尽量走代理注入，不作为长期环境变量常驻；
* 禁止访问内网管理网段、metadata endpoint、宿主 localhost。

### 5.5 审批策略要和沙盒一起上

OpenAI 把安全控制分成 sandbox mode 和 approval policy 两层，这个思路很值得直接借鉴。你这里至少要把下面动作做成 `on-request`：

* 删除大量文件；
* 写工作区之外路径；
* 新域名联网；
* `docker` / `systemctl` / `kill` / `kubectl` 等高风险命令；
* OpenWork engine reload；
* 配置发布、插件安装、批量改文件。([OpenAI开发者][4])

你甚至可以把 `.git` 目录默认设成只读，只有显式批准才允许真正修改 Git metadata。Codex 的 `workspace-write` 默认也会保护 `.git`、`.agents`、`.codex` 这类路径。([OpenAI开发者][4])

### 5.6 OpenWork 怎么接

你 repo 的 OpenWorkAdapter 已经把 workspace 读接口和部分控制接口分得很细，所以非常适合“读共享、写隔离”的策略：

* `get_workspace_summary / list_workspace_commands / list_workspace_mcp / list_workspace_audit / list_workspace_events` 继续共享控制面；
* `reload_engine`、文件改动、插件安装、workspace 配置更新等，统一转进 `sandboxed maintenance runner`；
* 对这些 mutation 操作加审批、trace 和不可变审计。([GitHub][10])

这样做的好处是：Portal 自己不再持有“一步到位改生产 workspace”的直接执行面，高风险动作都收敛到 runner/审批里。

### 5.7 会话恢复怎么改，代价最小

你现在恢复链路已经统一到 `SessionBinding.adapter` 和 `/api/sessions/{id}/resume`，所以没必要推翻 OpenCodeAdapter。更简单的改法是：创建会话时额外保存一个 `runner_binding`，例如：

* `runner_id`
* `workspace_id`
* `sandbox_template`
* `opencode_base_url`
* `expires_at`

resume 时先恢复 `runner_binding`，再把请求转发给对应 runner。这比重写整套 adapter 家族要小得多。([GitHub][1])

## 6. 你现在最需要先补的底座

在真正引入 sandbox 前，我建议先做这三件事：

1. 把 `launch_token` 升级成签名票据。
2. 把 ACL 从“未配置即放行”改成默认拒绝或最小权限。
3. 把 `PortalSession`、`LaunchRecord`、未来的 `RunnerLease` 至少迁到一个真实持久层，不再继续依赖 memory store。([GitHub][2])

原因很简单：你的一版目标本来就依赖 `LaunchRecord` 做统一入口和启动记录；如果会话、启动记录和 runner 绑定都不持久，那么一旦实例漂移或服务重启，沙盒方案反而会让恢复与审计更脆。([GitHub][2])

## 7. 短期如果必须共机部署

如果短期只能在同一台生产机上跑，最低可接受的做法是：

* Portal/OpenWork 跑在受保护的 systemd service/slice；
* runner 跑在单独 Linux 用户下的 rootless runtime；
* 用 cgroups/systemd resource-control 单独限制 runner 资源；
* Portal 与 runner 不共享 runtime socket、不共享大范围文件系统。([自由桌面][11])

但这只是过渡方案，不应该被当成长期的多租户安全边界。真正要避免“稳定服务被 agent 伤到”，最稳的还是把执行面移到独立 runner VM/节点。

## 8. 明确不要做的事

下面这些我建议直接写进红线：

* 不要把“skill/workflow 约束”当成唯一安全机制；
* 不要把 host Docker socket 暴露给 agent；
* 不要把 `/`、`/home`、repo 根目录这类宿主路径直接 RW bind mount 进去；
* 不要把长期 API key / host token 常驻到 runner 环境变量；
* 不要让 agent 默认拥有全互联网和工作区外写权限。([Docker Documentation][12])

## 9. 推荐的实施顺序

### 阶段 0：先做生产基线

修 `launch_token`、ACL 默认拒绝、真实持久层、统一审计。([GitHub][2])

### 阶段 1：只引入最小 sandbox 分流

新增 `execution_mode`、`SandboxBroker`、`RunnerLease`，先只把高风险 `skill_chat` 和 OpenWork 写操作切进 runner。

### 阶段 2：补 runner 安全基线

rootless runtime、只读 rootfs、workspace volume、network proxy、allowlist、TTL 回收、中央 trace/audit。

### 阶段 3：高风险资源再升级

对 `allow_docker=true`、高敏 repo、强多租户场景，再引入 gVisor/Kata/Firecracker，或者直接换成 Daytona/E2B 这种平台化沙盒。([gVisor][7])

## 10. 最终建议

如果只能选一条主线，我建议你现在就定成这一句：

**skill 定义环境，sandbox 真正隔离执行；共享 OpenCode 只留给低风险聊天；WebSDK 继续只做统一入口和 launch 记录；OpenWork 的写路径与代码型 skill 一律走独立 runner。** 这条路线和你现有 repo 的结构最贴，改动最小，同时最直接回应你最担心的三件事：数据泄露、误删误操作、以及 agent 影响生产机稳定服务。([GitHub][1])

你下一步最值得先改的代码点，是给资源配置加 `execution_mode / sandbox_template / network_policy`，然后在 backend adapter 前补一个 `SandboxBroker`。

[1]: https://github.com/yuha19990602-maker/agenthub "https://github.com/yuha19990602-maker/agenthub"
[2]: https://github.com/yuha19990602-maker/agenthub/blob/master/IMPLEMENTATION.md "https://github.com/yuha19990602-maker/agenthub/blob/master/IMPLEMENTATION.md"
[3]: https://containers.dev/implementors/spec/ "https://containers.dev/implementors/spec/"
[4]: https://developers.openai.com/codex/agent-approvals-security "https://developers.openai.com/codex/agent-approvals-security"
[5]: https://docs.docker.com/engine/security/rootless/ "https://docs.docker.com/engine/security/rootless/"
[6]: https://docs.docker.com/reference/cli/docker/container/run/ "https://docs.docker.com/reference/cli/docker/container/run/"
[7]: https://gvisor.dev/docs/ "https://gvisor.dev/docs/"
[8]: https://www.daytona.io/docs/en/ "https://www.daytona.io/docs/en/"
[9]: https://docs.docker.com/ai/sandboxes/security/isolation/ "https://docs.docker.com/ai/sandboxes/security/isolation/"
[10]: https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/adapters/openwork.py "https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/adapters/openwork.py"
[11]: https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html "https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html"
[12]: https://docs.docker.com/engine/storage/bind-mounts/ "https://docs.docker.com/engine/storage/bind-mounts/"
