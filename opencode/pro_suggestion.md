基于你的场景，我的建议很明确：**不要把 OpenWork 自带 WebUI 当成最终产品去硬改**，而是做一个你自己的企业级 Portal。把 **OpenCode 当“原生对话/会话引擎”**，把 **OpenWork server 或等价的 server-side 能力当“skills / config / 文件型能力管理层”**，再把你们已经做好的知识库对话、旧智能体应用、Skill 模块都接成统一的“资源”。这样最稳，也最符合你现在的产品目标。官方层面，OpenCode 已经稳定暴露 HTTP/OpenAPI、session/message、`prompt_async`、SSE 事件流等能力；OpenCode 的 skill 是通过本地/全局 `SKILL.md` 被原生 `skill` 工具按需加载并支持 `allow/deny/ask` 权限；OpenWork 当前官方架构也明确把 `.opencode/`、skills、config 这类文件系统操作收口到 server 侧，而 UI 通过官方 SDK + SSE 连接引擎。([OpenCode][1])

## 一句话方案

做一个 **AI Portal（统一入口）**：

* **前台**：像 Kimi / Minimax 的“聊天 + 资源切换”WebUI
* **中台**：统一鉴权、资源目录、Skill 商店、会话中心、权限中心、日志追踪
* **执行层**：

  * 原生对话 / Skill 对话：走 OpenCode
  * 知识库对话：走 iframe / websdk / URL 代理
  * 旧智能体应用：走 iframe / websdk / URL 代理
  * 文件型 skill/config 管理：走 OpenWork server 或你自己的等价服务

---

## 一、推荐的总体架构

```text
[企业统一SSO]
      │
      ▼
[AI Portal Web]
  ├─ 左侧：资源分组 / 最近会话 / 收藏 / 我的技能
  ├─ 中间：统一聊天工作区（原生聊天 or 嵌入应用）
  └─ 右侧：资源详情 / 权限提示 / 会话信息 / 调试信息(管理员)
      │
      ▼
[Portal BFF / API Gateway]
  ├─ Auth Bridge（SSO回调、工号解析、Portal Token）
  ├─ ACL / Policy（按工号、角色、部门、资源、Skill做授权）
  ├─ Resource Catalog（智能体、知识库、Skill、直聊）
  ├─ Skill Registry（公用/个人/共享/版本）
  ├─ Session Center（Portal Session 与底层 Session 映射）
  ├─ Conversation Gateway（统一发消息、流式返回、异步任务）
  ├─ Adapter Hub（iframe/websdk/url/native 四类适配）
  ├─ Audit & Trace（日志、审计、链路）
  └─ Admin API（资源上架、分组、权限配置）
      │
      ├────────► [OpenCode Runtime]
      ├────────► [知识库对话应用]
      ├────────► [已有智能体应用]
      └────────► [OpenWork server / 你的文件能力服务]
```

### 这套架构的两个核心原则

**1）UI 上可以“资源切换”，但技术上建议 V1 仍保持 `1 个 session = 1 个激活资源快照`。**
也就是用户看起来是在一个统一聊天壳里切换资源，但真正切到另一个 Skill / 知识库 / 应用时，默认新建 session 或 fork session，而不是把不同资源硬塞进同一上下文。这样历史、权限、审计、回溯都会清楚很多。

**2）Portal Session 和底层引擎 Session 分离。**
Portal 自己维护“用户看到的会话”；底层再绑定 OpenCode session 或外部应用 session。这样你才能同时兼容原生对话、Skill 对话、iframe 应用、websdk 应用。

---

## 二、模块拆分

### 1. 前端模块

**A. Portal Shell**

* 顶部：全局搜索、用户信息、设置
* 左侧：资源分组、最近使用、收藏、会话列表
* 中间：统一工作区
* 右侧：资源说明 / starter prompts / 权限状态 / 调试信息

**B. Resource Center**

* 资源分组展示：按部门、业务域、资源类型、最近使用
* 支持资源类型：

  * 直接对话
  * Skill
  * 知识库对话
  * 已有智能体应用
* 每个资源统一一张卡片：名称、说明、标签、权限状态、入口动作

**C. Chat Workspace**

* `NativeChatRenderer`：直聊、Skill 对话
* `EmbedRenderer`：iframe / websdk
* `RedirectLauncher`：只能跳转 URL 的旧应用
* 会话页顶部显示当前资源 badge、切换资源、退出当前模式

**D. Session Sidebar**

* 按资源分 session
* 历史会话回溯
* 标题自动生成/手动修改
* 最近会话 / 收藏 / 归档

**E. Skill Store**

* 公共 Skill
* 我的 Skill
* 与我共享
* 技能详情
* 直接“基于该 Skill 开始对话”

**F. Admin Console**

* 资源上架/下架
* 分组与排序
* 权限配置
* Skill 审核与发布
* 监控看板

---

### 2. 后端模块

**A. Auth Bridge**

* 统一 SSO 跳转
* 回调后拿到工号
* 生成 Portal 登录态
* 生成短时 `launch_token`

**B. ACL / Policy**

* 规则维度：

  * 用户
  * 角色
  * 部门
  * 资源类型
  * Skill owner / shared scope
* 支持动作：

  * view
  * use
  * manage
  * publish
  * share

**C. Resource Catalog**

* 统一资源模型：

```ts
type ResourceType = "direct_chat" | "skill" | "kb_chat" | "agent_app";
type LaunchMode = "native" | "websdk" | "iframe" | "redirect";

type Resource = {
  id: string;
  name: string;
  type: ResourceType;
  launchMode: LaunchMode;
  groupId: string;
  description: string;
  icon?: string;
  tags?: string[];
  visible: boolean;
  config: Record<string, any>;
};
```

**D. Skill Registry**

* 存公共 Skill、个人 Skill、共享 Skill
* 存版本、owner、描述、starter prompts、ACL
* Skill 正文建议版本化存储（DB + 对象存储 / Git）

**E. Session Center**

* PortalSession：用户侧会话
* SessionBinding：PortalSession 绑定到底层 OpenCode session / 外部 app session
* PortalMessage：至少给原生聊天落库；外部嵌入应用则存“会话索引 + resume 信息”

**F. Conversation Gateway**

* 对前端暴露统一消息接口
* 底层判断调用：

  * OpenCode message / SSE
  * 外部应用 launch/resume
  * 异步任务队列

**G. Adapter Hub**

* `OpenCodeAdapter`
* `SkillAdapter`
* `KnowledgeBaseAdapter`
* `WebSDKAdapter`
* `IframeAdapter`
* `RedirectAdapter`

**H. Audit / Trace**

* 统一 trace id
* 审计“谁在什么时间用了哪个资源”
* 错误定位“哪个资源、哪个 session、哪个底层引擎出错”

---

## 三、各部分实现方案

### 1. 原生直聊与 Skill 对话

这部分直接走 OpenCode。因为官方已经提供 session/message/async/SSE 能力，完全够你做一个自定义聊天前端。([OpenCode][1])

#### 直聊

* Portal 创建 `portal_session`
* 同时创建 `opencode_session`
* 发送消息时由 BFF 调 OpenCode：

  * `POST /session`
  * `POST /session/:id/message`
  * `GET /event` 订阅流式事件
* 需要高并发异步时，改走 `POST /session/:id/prompt_async`

#### Skill 对话

这里我建议你**不要把 OpenCode 本地 skill 发现机制直接当作企业 Skill 商店**，而是做**“中心化 Skill Registry + 运行时映射”**。因为 OpenCode 官方的 skill 发现本质上仍是从 `.opencode/skills`、`~/.config/opencode/skills` 等本地/全局目录扫描，再由 `skill` 工具按需加载，并通过 `opencode.json` 做模式级权限控制；这很好用，但更适合本地/项目级 skill，不够表达“企业部门级公用 + 个人 + ACL + 发布审核”的产品需求。([OpenCode][2])

所以 Skill 运行建议分两层：

**V1：Prompt/Mode 注入**

* 选中 Skill 后，Portal 生成 `activeSkillContext`
* 发消息时，BFF 在 `system` 里注入当前 skill mode
* 输入框上方展示 starter prompts
* 用户感知是“技能模式对话”

**V2：运行时物化**

* 把允许使用的 Skill 物化到运行环境 `.opencode/skills/<name>/SKILL.md`
* 让 OpenCode 原生 `skill` 工具真正发现并加载
* 这一步通过 OpenWork server 或你自己的文件能力服务来做，不让浏览器直接碰文件系统；这也符合 OpenWork 当前 server-owned filesystem 的方向。([GitHub][3])

---

### 2. 知识库对话

你这里已经说明知识库对话应用本身已完成，只需要集成 websdk / iframe / URL，不做知识管理，那它在你的架构里就应被视为一种 **`kb_chat` 资源**，而不是单独系统。

实现方式：

* `resource.type = kb_chat`
* `launchMode = websdk | iframe | redirect`
* Portal 只负责：

  * 权限校验
  * 会话索引
  * 启动 token
  * 页面壳层
  * 最近会话入口
* 不负责：

  * 文档导入
  * 分段
  * 检索配置
  * 知识库后台管理

这会极大降低你首版复杂度。

---

### 3. 已有智能体应用接入

你现有应用有三种方式：URL、websdk、iframe。本质上就是三类 Adapter。

#### A. WebSDKAdapter

适合已有 snippet 嵌入的应用。

前端封装一个组件：

* 动态加载 SDK script
* mount 容器
* 传入 `appKey / baseUrl / launchToken / sessionRef`
* 切换 session 时销毁并重建实例

#### B. IframeAdapter

适合已有独立 WebUI 且支持 iframe 的应用。

建议：

* 优先走**同域反向代理**，避免跨域 cookie / CSP / X-Frame-Options 问题
* 使用 `postMessage` 做握手：

  * Portal 下发用户上下文/launch token
  * 子应用回传 ready/sessionChanged/titleChanged/error

#### C. RedirectAdapter

仅能 URL 跳转时使用。

* Portal 先鉴权
* 生成短时 launch token
* 跳转到目标 URL
* 回流时带上 `portalSessionId`

### 统一接入协议建议

虽然你旧应用都能嵌进去，但**“嵌进去”和“统一会话能力”不是一回事**。
如果你希望真正做到“分 session、回溯历史、统一最近会话”，建议给所有旧应用补一个最小接入协议：

* `createSession`
* `resumeSession`
* `listSessions`
* `getMessages`（最好有）
* `exchangeLaunchToken`
* `getAppMeta`

没有 `listSessions/getMessages` 的应用，Portal 只能做到“入口统一 + 启动记录统一”，做不到真正的“消息级历史统一”。

---

## 四、会话与历史设计

这是你成败最关键的地方。

### 建议的数据模型

```ts
PortalSession {
  id;
  userId;
  resourceId;
  resourceType;
  title;
  status;
  createdAt;
  updatedAt;
}

SessionBinding {
  portalSessionId;
  engineType; // opencode | kb_app | agent_app
  engineSessionId; // 原生对话时有
  externalSessionRef; // 嵌入应用时有
}

PortalMessage {
  id;
  portalSessionId;
  role;
  content;
  traceId;
  engineMessageId?;
}
```

### 回溯策略

* **原生直聊 / Skill 对话**：完整消息落库；支持“从这里继续”
* **嵌入应用**：

  * 如果外部应用支持 history API，则做真正回溯
  * 如果不支持，则仅保留 resume 指针和入口记录

另外，OpenCode 原生就有 session list/create/fork/message 等能力，所以“从某条消息处分叉继续”这件事，在原生对话里是可以自然承接的。([OpenCode][1])

---

## 五、统一鉴权与权限控制

你提到的“先统一鉴权，拿工号，再根据工号控制应用访问”，非常适合做成下面这套：

### 登录链路

1. 用户打开 Portal 链接
2. 未登录则跳企业 SSO
3. Portal callback 拿到工号
4. BFF 签发 Portal 登录态（cookie 或 token）
5. Portal 拉取用户可访问资源列表

### 资源启动链路

1. 用户点击某个 Skill / KB / 智能体
2. BFF 做 ACL 判断
3. 生成短时 `launch_token`
4. Portal 打开原生对话页 / iframe / websdk / redirect
5. 下游应用拿 `launch_token` 换取用户身份上下文

### 关键建议

* **浏览器不要直接传工号给下游应用作为可信依据**
* 可信身份只在 Portal BFF 或服务间传递
* 下游只信 Portal 签名 token 或服务间 header

### Skill ACL

Skill 商店单独建权限：

* `public`
* `private`
* `shared`
* `department-shared`

同时把 OpenCode 自带的 `skill allow/deny/ask` 当成**引擎侧兜底权限**，但不要把它当产品主 ACL。因为企业权限一定要落在 Portal 自己的 ACL 服务里。([OpenCode][2])

---

## 六、高并发、异步与日志追踪

### 1. 并发架构

* Portal BFF 无状态，水平扩容
* SSE 网关独立部署
* Redis 做：

  * session cache
  * 幂等 key
  * stream/pubsub
* MQ（Redis Streams / RabbitMQ / Kafka）做异步任务
* PostgreSQL 存资源、权限、会话元数据

### 2. 异步任务

原生对话建议分两类：

* **实时问答**：同步 message + SSE
* **长任务/高峰场景**：`prompt_async` + worker + 任务状态轮询/推送

OpenCode 官方已经支持 `prompt_async` 和 SSE，所以你不需要自己发明异步协议。([OpenCode][1])

### 3. Trace 字段建议

每条请求至少带：

* `trace_id`
* `portal_session_id`
* `engine_session_id`
* `resource_id`
* `employee_no_hash`
* `adapter_type`
* `latency_ms`
* `provider/model`
* `result_code`

### 4. 日志体系

如果你复用 OpenWork 侧运行能力，可以直接接它已有的统一日志思路：当前 orchestrator 文档写明支持统一日志流、JSON 格式、run id 关联，并且 openwork-server 会记录 method/path/status/duration。这个正好适合接入你的 Trace 平台。([GitHub][4])

---

## 七、产品层面的几个关键决定

### 我建议 V1 必须坚持的

1. **一个 session 只绑定一个资源快照**
2. **Portal 自己维护 session 索引，不依赖 OpenWork UI 本地状态**
3. **旧应用先统一入口，后统一消息协议**
4. **Skill 商店先做“可用可控”，再做“在线编辑器”**
5. **前端不直连 OpenCode**

### 不建议你一上来做的

1. 一个对话里叠加多个 Skill
2. 把所有 iframe/websdk 应用强行渲染成同一种消息样式
3. 直接深改 OpenWork 自带 UI 当主产品
4. 直接绑死 OpenWork / OpenCode 当前仓库内部目录结构

---

## 八、结合你当前版本的建议

你现在环境是 **OpenCode 1.2.24**、**OpenWork 0.11.142**。而截至今天，上游已经到 **OpenCode v1.3.0**、**OpenWork 0.11.18x**，而且 OpenWork 当前架构文档已经把 server canonical surface 指向 `/apps/server/` 这类新布局。我的建议是：**你的产品层一定要加一层 `EngineAdapter / ResourceAdapter` 兼容层，不要让业务代码直接依赖上游 repo 内部结构。** 这样你后面升级到新版本时，只改 adapter，不会把整个 Portal 一起拖进来。([GitHub][5])

还有一个现实风险：GitHub 上已经有一个 **OpenWork v0.11.142 在 Windows 11 下会话历史恢复异常** 的公开 issue。哪怕它只是在某些平台和场景出现，我也建议你**不要把最终历史会话能力寄托在 OpenWork 本地 UI 状态**，而是把 Portal 自己的 session index 和 binding table 作为主记录。([GitHub][6])

---

## 九、推荐落地顺序

**第一期**

* 统一鉴权
* 资源中心
* 原生直聊
* Skill 商店（浏览 + 直接对话）
* 知识库 iframe/websdk 接入
* Portal Session 中心
* 基础日志链路

**第二期**

* 旧智能体应用适配器
* 统一最近会话 / 收藏 / 搜索
* 技能权限与个人 Skill
* 管理台

**第三期**

* Skill 发布审核
* 运行时 skill 物化 / reload
* 异步长任务中心
* 资源推荐、使用分析、成本统计

---

## 最后给你的结论

**最适合你的不是“改 OpenWork 做最终产品”，而是“做一个企业 AI Portal，把 OpenCode/OpenWork 当底层能力层”。**

这样你能同时满足：

* 普通员工友好的聊天式入口
* 旧应用平滑接入
* Skill 商店与权限控制
* 知识库对话统一入口
* 会话分 session 与历史回溯
* 高并发与可追踪运维

下一步最值得直接细化的是：**接口清单 + 表结构 + 前端页面路由/组件树**。

[1]: https://opencode.ai/docs/zh-cn/server/ "https://opencode.ai/docs/zh-cn/server/"
[2]: https://opencode.ai/docs/zh-cn/skills/ "https://opencode.ai/docs/zh-cn/skills/"
[3]: https://github.com/different-ai/openwork/blob/dev/ARCHITECTURE.md "https://github.com/different-ai/openwork/blob/dev/ARCHITECTURE.md"
[4]: https://github.com/different-ai/openwork/blob/dev/packages/orchestrator/README.md "https://github.com/different-ai/openwork/blob/dev/packages/orchestrator/README.md"
[5]: https://github.com/anomalyco/opencode/releases "https://github.com/anomalyco/opencode/releases"
[6]: https://github.com/different-ai/openwork/issues/860 "https://github.com/different-ai/openwork/issues/860"
