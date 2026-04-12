我把你的下一步方向收敛成一句话：

**把 AgentHub 从“资源 adapter 的聚合 UI”升级成“资源注册中心 + workspace 控制面 + skill 运行时平台”。**

你现在的 V2 已经把服务端 session（`portal_sid`）、统一 resume、SSE 流式消息，以及 native / embedded 多类资源接通了；但目录仍主要靠 `sync_resources.py` 把 OpenWork skills、static resources 和 overrides 合并成 `resources.generated.json`，再由 `CatalogService` 以内存方式加载，默认存储也还是 `MemoryStore`。这说明项目已经从“先跑起来”进入了“资源和运行时治理要升级”的阶段。你在补充说明里提出的“短期 iframe，长期 skill/API 化、按用户权限展示资源、做搜索/推荐/审计”的方向也是一致的。 ([GitHub][1])

## 1. 先把主抽象改掉：Resource 不是 adapter，Entrypoint 才是 adapter

你现在的 `Resource` 还是扁平模型：直接持有 `type`、`launch_mode`、`adapter`、`config`、`acl`；`SessionBinding` 也主要记录 `adapter`、`workspace_id`、`skill_name` 这些恢复信息。这个设计在“一个资源只有一种启动方式”时够用，但一旦同一个旧应用既要 iframe，又要以后 skill 化，就会把权限、收藏、推荐、统计、恢复全部拆散。([GitHub][2])

我建议你把模型收敛成下面这套：

```json
{
  "id": "hr-policy",
  "name": "HR 政策助手",
  "resource_kind": "application",
  "workspace_id": "hr",
  "owner": "hr-platform",
  "entrypoints": [
    {
      "id": "ui",
      "mode": "embedded",
      "adapter": "iframe",
      "default": true,
      "enabled": true,
      "capabilities": {
        "chat": false,
        "upload": true,
        "resume": false
      }
    },
    {
      "id": "assistant",
      "mode": "native",
      "adapter": "skill_chat",
      "skill_bundle_id": "legacy/hr-policy",
      "default": false,
      "enabled": false,
      "capabilities": {
        "chat": true,
        "tool_call": true,
        "resume": true,
        "auditable": true
      }
    }
  ],
  "acl": {
    "allowed_depts": ["HR"]
  },
  "governance": {
    "status": "active",
    "version": "2026.04",
    "owner": "hr-platform"
  }
}
```

这一步的价值很大：**同一个业务资源只有一个 resource_id，但可以拥有多个 entrypoints**。这样短期 iframe、长期 skill 化，不会裂成两个割裂资源；同一个资源的 ACL、最近使用、收藏、推荐、审计、owner、下线状态都沉在一处。

顺着这个思路，`SessionBinding` 下一步必须加 `entrypoint_id`，并建议同时冻结 `bundle_version`、`launch_token_id`、`capability_snapshot`。这样恢复会话时，你恢复的是“哪个资源的哪个入口”，而不是模糊地知道它曾经走过某个 adapter。

## 2. skill 不该只是 prompt，它应该是平台里的一级资源能力包

你现在 repo 里的 skill，本质上还是一种特殊资源：`sync_resources.py` 会把 OpenWork 里的 skills 规范化为 `type=skill_chat`、`launch_mode=native` 的 Portal resource，挂上 `config.skill_name`、`workspace_id`、`starter_prompts`，再写回统一目录。([GitHub][3])

但从 OpenCode 官方机制看，**skill 的本体其实是 `SKILL.md`**：它是可复用指令，通过原生 `skill` 工具按需加载；而真正的执行逻辑应该落在 **custom tools** 或 **MCP** 上，自定义工具放在 `.opencode/tools`，而且工具本身可以再调用 Python 脚本。([OpenCode][4])

所以你这里最重要的抽象升级是：

**不要把“skill = system prompt + 一个脚本”作为最终模型，而要把 skill 定义成三层对象：**

1. **SkillBundle**：平台级能力包
   包含 `SKILL.md`、桥接工具、examples、evals、owner、version、ACL 默认值、风险级别。

2. **SkillInstallation**：某个 workspace 中的安装态
   哪个 bundle 的哪个版本被安装到哪个 workspace，是否启用，是否需要审批。

3. **SkillEntrypoint**：某个 resource 暴露出来的 native 入口
   资源通过 entrypoint 引用某个 bundle/version，让它成为“聊天入口”或“助手入口”。

也就是说，**skill 商店不要维护另一套独立对象模型**。更合理的是：

* 资源目录：面向所有可发现资源
* skill 商店：同一注册中心里的一个视图，只展示“可安装 / 可启用 / 主入口为 native skill”的那部分资源

## 3. skill 机制怎么迭代：从 Prompt Skill 走到 Bridge Skill，再到 Managed Skill

这是我最建议你明确写进设计文档的一段。

### 第 1 阶段：Prompt Skill

这是你现在已经有的形态。
`skill_chat + skill_name + starter_prompts`，system prompt 负责把模型引到某种工作模式。它适合做快速验证，也适合做通用能力类 skill。([GitHub][3])

### 第 2 阶段：Bundle Skill

引入统一包规范，把 skill 从“会话入口”变成“可发布资产”。

我建议你的 bundle 目录长这样：

```text
skill-bundles/
  legacy/hr-policy/
    manifest.json
    SKILL.md
    bridge/
      tool.ts
      executor.py
    examples/
      ask-policy.md
    evals/
      smoke.yaml
    policy.json
    ui-hints.json
```

这里要注意一个关键点：**这是 AgentHub/OpenWork 的发布包格式，不一定等于 OpenCode 原生落盘格式**。
真正部署到 OpenCode workspace 时，应当被“物化”为：

* `.opencode/skills/hr-policy/SKILL.md`
* `.opencode/tools/hr-policy-query.ts`
* 以及必要的 MCP / commands / workspace config

这样你就同时兼容了你的平台发布逻辑和 OpenCode 的原生发现机制。([OpenCode][4])

### 第 3 阶段：Bridge Skill

这是旧智能体应用长期最关键的一步。

这里要坚持一个原则：**system prompt 只负责“选模式、控流程、限定边界”，不要把它当真正集成层。**
真正的旧平台调用，应由 bridge 来完成：

* `SKILL.md`：描述什么时候用这个 skill、输入输出约束、失败时怎么回退
* `tool.ts` / MCP：向 OpenCode 暴露真实工具
* `executor.py`：调用旧平台统一 API、处理鉴权、重试、结果清洗、结构化返回

这和 OpenCode 官方设计是对齐的：skill 是被 `skill` 工具加载的指令层，工具/MCP 才是执行层。([OpenCode][4])

### 第 4 阶段：Managed Skill

当 skill 成为企业平台能力后，它还应该具备：

* 发布 / 回滚
* 版本冻结
* owner / reviewer
* 审批
* 配额
* 审计
* 风险分级
* workspace 级启停

这时 OpenWork 就不该只当“skill 列表来源”，而应该升成真正的 workspace 控制面。OpenWork 官方 server 已经提供了 workspace config、skills、mcp、commands、audit、import/export、approvals，以及 workspace 级的 OpenCode proxy。([GitHub][5])

## 4. 旧智能体应用怎么接：不是都要 skill 化，而是分三类

你现在“短期 iframe、长期 API skill 化”的方向是对的，但建议更明确地分流：

1. **文本问答 / 查询型应用**
   优先 skill 化，做成 bridge skill。
   这类最适合 native chat 入口。

2. **工具 / API 型应用**
   做成 tool-first skill。
   让 `SKILL.md` 负责编排，tool/MCP 负责真调用。

3. **强 UI / 强状态机 / 多步骤表单型应用**
   不要强行 skill 化。长期继续保留 iframe entrypoint。
   但要把 launch token、权限、埋点、最近访问、上下文透传、审计统一起来。

真正要消灭的不是 iframe，而是**“未治理的 iframe”**。

## 5. OpenWork 的定位要升级：从“技能来源”升级成“workspace 控制面”

你现在后端的 `OpenWorkAdapter` 还比较薄，主要是 `list_skills`、`get_skill_status`、`reload_engine` 这一级。([GitHub][6])

但 OpenWork server 实际暴露的能力比这多得多：它不仅能管理 workspace 的 skills，还能管理 plugins、MCP、commands、audit，并且能用 `/w/:id/opencode/*` 代理 workspace 绑定的 OpenCode 调用。([GitHub][5])

所以后面的架构分工，我建议是：

* **Portal**：资源目录、权限裁剪、会话中心、推荐、审计展示
* **OpenWork**：workspace 控制面、安装发布、审批、审计、workspace 代理
* **OpenCode**：native 会话执行面，负责 session、message、fork、diff、summarize、revert、prompt_async、shell / command / file 能力

OpenCode server 已经有这些会话和运行时接口，所以后面你完全可以把“fork / diff / summarize / revert / prompt_async / shell / file”这些能力逐步透到 Portal 上，而不是只停留在“发消息”。([OpenCode][7])

## 6. 资源同步不要再是“生成最终目录”，而要变成“注册中心发布流程”

你现在的同步链路是对的，但角色要变：

**现在**：
OpenWork skills + static resources + overrides → `resources.generated.json` → CatalogService

**建议改成**：
OpenWork / bundle repo / manual entries → sync preview → diff review → publish → DB catalog → snapshot JSON 导出

因为你已经有静态资源、OpenWork skill、overrides 三类来源了，下一步如果还把 JSON 当唯一事实源，后面做 owner、disabled reason、灰度发布、审核、版本、推荐统计都会很重。当前 `CatalogService` 直接读文件缓存，`sync_resources.py` 直接输出生成目录，这正是应该升级的点。([GitHub][8])

我建议的存储分层是：

* **Postgres**：资源注册表、entrypoints、skill_bundles、installations、portal_sessions、session_bindings、messages、favorites、launches、usage_events、audit_logs
* **Redis**：缓存、短期 session、SSE cursor、分布式锁、限流
* **JSON snapshot**：导出产物、回滚快照，不再是事实源

## 7. 权限、搜索、推荐：先做确定性能力，再做画像

你提出“每个用户看到不同资源目录、公共资源 + 推荐资源、记录使用、做画像、资源搜索”的方向是对的，但我建议按三层推进。

第一层，先做最值钱也最稳定的：

* 搜索
* 最近使用
* 收藏
* 按部门/角色过滤后的资源目录

第二层，做规则推荐：

* 同部门高频
* 同角色常用
* 与当前资源共同使用最多
* 新上线且用户有权限的资源

第三层，再做用户画像：

* 先产**结构化标签**，比如 `prefers_native_chat`、`uses_hr_workspace`、`frequent_data_analysis`
* 再异步转成自然语言描述，不要一上来就靠 LLM 直接给用户下画像

还有两个原则要定死：

**一是 ACL-first。**
先过滤，再排序。推荐结果必须先过权限裁剪。你自己的高级配置文档也已经在往 workspace ACL、动态 ACL、配额、审批这些方向走。([GitHub][9])

**二是区分 discoverable 和 launchable。**
有些资源只能“知道有”，不能直接启动；有些则需要审批后启动。这样企业内场景更稳。

## 8. 前后端接口建议

你现在已经有 `/api/resources`、`/api/skills`、`/api/resources/{id}/launch`、admin 资源同步和 session resume 这些接口基础。([GitHub][10])

下一步我建议接口这样演进：

* `GET /api/resources`
  返回 resource 摘要 + 默认 entrypoint + capability badge

* `GET /api/resources/{id}`
  返回完整 entrypoints、governance、推荐理由、权限状态

* `POST /api/resources/{id}/launch`
  body 增加 `entrypoint_id`

* `POST /api/admin/catalog/sync/preview`

* `POST /api/admin/catalog/publish`

* `POST /api/admin/catalog/rollback`

* `POST /api/admin/skills/{bundle_id}/install`

* `POST /api/admin/skills/{bundle_id}/disable`

前端上，资源卡片和 skill 商店不要分成两套体系。
资源详情页里直接展示可用入口，比如：

* 聊天
* 打开应用
* 查看文档
* 安装/启用 skill

这样以后一个资源从 iframe 进化到 native skill，不需要重做 UI 心智模型。

## 9. 我建议的实施顺序

### 第一阶段：内核稳定

先完成四件事：

* `resource + entrypoints + capabilities + governance` 新模型
* `SessionBinding.entrypoint_id`
* Postgres 落地，Redis 做辅助
* `launch_token v2`

`launch_token v2` 建议包含：`resource_id`、`entrypoint_id`、`workspace_id`、匿名化 user 标识、scope、过期时间、trace_id。iframe 和 bridge skill 共用这一套。

### 第二阶段：资源治理

* 数据库注册中心
* sync preview / diff / publish / rollback
* owner / version / disabled_reason / lifecycle
* 管理后台：资源同步、workspace/skill 管理、审批队列、审计看板

### 第三阶段：skill 化和能力融合

* 定义 SkillBundle 规范
* 选 1~2 个最适合的旧应用做 bridge skill POC
* Portal native 入口切到 OpenWork workspace proxy
* 把 OpenCode 的 fork / diff / summarize / prompt_async 逐步透出

### 第四阶段：推荐和运营

* usage events 体系
* 部门热榜、协同使用推荐
* 用户标签
* skill/资源转化漏斗
* 审计和风控报表

## 10. 如果你现在只做三件事，最值钱的是这三件

第一，把当前 `resource.type + launch_mode + adapter` 升级成 **resource + entrypoints + capabilities**，同时给 `SessionBinding` 增加 `entrypoint_id`。
这是后面 iframe、skill 化、推荐、收藏、审计、恢复能否统一的基础。

第二，定义 **SkillBundle 规范**，并用一个旧智能体应用做出 **bridge skill** 的样板。
这一步能把“system prompt 引导”升级成“prompt 选模式 + tool 真调用”。

第三，把 OpenWork 从“同步 skill 列表”升级成 **workspace 控制面**，至少先把 workspace 级 proxy、审批、安装发布、审计接进来。
这一步做完，你的平台就不再只是资源展示层，而是真正开始具备企业级治理能力。

如果你愿意，我下一步可以直接按你这个仓库的目录，给你继续细化一版 **“数据模型 + API 变更 + 表结构 + 代码改造点（具体到哪些文件改什么）”**。

[1]: https://github.com/yuha19990602-maker/agenthub/blob/master/README.md?utm_source=chatgpt.com "agenthub/README.md at master · yuha19990602-maker/agenthub"
[2]: https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/models.py "agenthub/backend/app/models.py at master · yuha19990602-maker/agenthub · GitHub"
[3]: https://github.com/yuha19990602-maker/agenthub/blob/master/scripts/sync_resources.py "agenthub/scripts/sync_resources.py at master · yuha19990602-maker/agenthub · GitHub"
[4]: https://opencode.ai/docs/zh-cn/skills/ "代理技能 | OpenCode"
[5]: https://github.com/different-ai/openwork/tree/dev/apps/server "openwork/apps/server at dev · different-ai/openwork · GitHub"
[6]: https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/adapters/openwork.py "agenthub/backend/app/adapters/openwork.py at master · yuha19990602-maker/agenthub · GitHub"
[7]: https://opencode.ai/docs/zh-cn/server/ "服务器 | OpenCode"
[8]: https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/catalog/service.py "agenthub/backend/app/catalog/service.py at master · yuha19990602-maker/agenthub · GitHub"
[9]: https://github.com/yuha19990602-maker/agenthub/blob/master/V2_ADVANCED_CONFIGURATION.md "agenthub/V2_ADVANCED_CONFIGURATION.md at master · yuha19990602-maker/agenthub · GitHub"
[10]: https://github.com/yuha19990602-maker/agenthub/blob/master/API.md?utm_source=chatgpt.com "agenthub/API.md at master · yuha19990602-maker/agenthub · GitHub"
