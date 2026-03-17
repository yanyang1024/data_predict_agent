基于你的背景，我建议不要把 OpenWork 或 OpenCode 自带 UI 直接改成最终产品，而是做一个独立的 \*\*AI Portal\*\*。Portal 负责用户体验、目录、权限、知识库和统一会话；OpenCode 负责推理、session、message 和事件流；OpenWork server 负责技能、工作区和文件系统相关能力。这个划分和当前官方能力基本吻合：OpenCode server 已公开 OpenAPI、session、message、SSE event、CORS 与 basic auth 等接口，适合做多客户端会话引擎；OpenCode 的 skill 也是通过原生 `skill` 工具按需加载；而 OpenWork 的架构文档明确要求浏览器侧凡是读写 `.opencode/`、`SKILL.md`、`opencode.json`、打开目录等能力，都应走 `packages/server` 这样的 host-side service。(\[OpenCode]\[1])



OpenWork 自己也把现有 opencode CLI/GUI 描述为更偏开发者视角，关注 file diffs、tool names 等；OpenCode 官方 Web 页面当前重点仍是“会话”和“服务器状态”。所以你的目标如果是“面向普通用户、AI 原生、统一入口”，最佳路径是：复用它们的底层能力，但自己做一层更产品化的 Portal UI。另一个利好是，OpenWork 最近已经在 skill hub 方向增加了自定义 GitHub skill hub 仓库支持，这对你的“公共 skill + 个人 skill + 团队 skill 源”也很契合。(\[GitHub]\[2])



\## 一句话方案



\*\*做一个“统一 AI 门户”\*\*：



\* \*\*Portal WebUI\*\*：给普通用户用的简单入口

\* \*\*Portal BFF / Gateway\*\*：统一鉴权、会话编排、资源目录、权限控制

\* \*\*OpenCode Runtime\*\*：承接 skill 模式、普通对话、部分知识库对话

\* \*\*OpenWork Server\*\*：承接技能发现、技能同步、工作区文件侧能力

\* \*\*Legacy Agent Adapters\*\*：接你们已有的 API / WebSDK / URL 三种智能体应用

\* \*\*Knowledge Service\*\*：做公有/个人知识库、检索、引用和 ACL



---



\## 我建议的总体架构



```text

\[ Browser / WebUI ]

&nbsp;       |

&nbsp;       v

\[ Portal BFF / API Gateway ]

&nbsp;  |        |         |            |

&nbsp;  |        |         |            +--> \[ Auth / SSO / Token Broker ]

&nbsp;  |        |         +---------------> \[ ACL / Resource Policy ]

&nbsp;  |        +-------------------------> \[ Catalog / Registry ]

&nbsp;  +------------------------------+---> \[ Conversation Orchestrator ]

&nbsp;                                 |

&nbsp;                                 +---> \[ Knowledge Service / RAG ]

&nbsp;                                 |

&nbsp;                                 +---> \[ Integration Adapters ]

&nbsp;                                             |        |         |

&nbsp;                                             |        |         +--> URL / WebSDK Apps

&nbsp;                                             |        +------------> Legacy API Agents

&nbsp;                                             +---------------------> OpenCode Runtime

&nbsp;                                                                   + OpenWork Server



\[ PostgreSQL ] \[ Redis ] \[ Object Storage ] \[ pgvector ]

```



这里最关键的不是前端，而是 \*\*Portal BFF\*\*。

因为你真正要统一的，不只是入口，而是这四件事：



1\. 资源目录：智能体、skill、知识库都要能统一展示

2\. 会话编排：不同运行时的 session 要统一成一种用户体验

3\. 权限与鉴权：不同资源、不同用户、不同下游应用要统一控制

4\. 历史与审计：聊天记录、调用记录、授权记录都要能回溯



---



\## 最重要的架构原则



\### 1. 不要把 OpenWork 当最终产品 UI



OpenWork 更适合做 \*\*host-side capability layer\*\*，不是你的最终普通用户产品壳层。

你可以借它的能力，但不建议把它作为最终 Web 产品界面来重度 fork。



\### 2. Portal 要成为“系统真相层”



你的 Portal 必须拥有这些主数据：



\* 资源目录

\* 资源权限

\* 用户会话

\* 会话上下文

\* 外部运行时绑定关系

\* 审计日志



也就是说，\*\*OpenCode session id 和旧智能体自己的 session id，都只是外部绑定，不应成为你的唯一真相源\*\*。



\### 3. V1 只允许一个主模式



每个会话只允许一个主上下文：



\* 普通聊天

\* 智能体聊天

\* skill 聊天

\* 知识库聊天



知识库可以作为附加上下文，但 \*\*不要一开始就支持多 skill 叠加、多智能体混用\*\*。

对普通用户来说，这会很难理解，也很难排障。



---



\## 资源模型要统一



你表面上有三类东西：



\* 智能体应用

\* skill

\* 知识库



但系统里最好统一成一个抽象：`Resource`



```ts

type ResourceType = "agent" | "skill" | "knowledge";

type LaunchMode = "native\_chat" | "embedded\_websdk" | "external\_url";

type RuntimeType = "opencode" | "legacy\_api" | "websdk" | "url" | "rag";

type Visibility = "public" | "private" | "group" | "role";



interface Resource {

&nbsp; id: string;

&nbsp; type: ResourceType;

&nbsp; name: string;

&nbsp; description: string;

&nbsp; icon?: string;

&nbsp; groupId?: string;

&nbsp; ownerId?: string;

&nbsp; visibility: Visibility;

&nbsp; tags: string\[];

&nbsp; launchMode: LaunchMode;

&nbsp; runtimeType: RuntimeType;

&nbsp; integrationId?: string;

&nbsp; authPolicyId?: string;

&nbsp; status: "active" | "disabled" | "draft";

}

```



这样做有三个好处：



第一，前端首页可以统一展示。

第二，权限系统可以复用。

第三，后续“收藏、推荐、最近使用、分组展示、审核发布”都能统一做。



你真正的差异，只在于 \*\*启动方式\*\* 和 \*\*运行方式\*\*。



---



\## 会话模型怎么设计



你的需求里，最容易被低估的其实是会话。



因为你不只是“聊天 UI”，你是在做一个 \*\*统一会话编排层\*\*。



我建议会话模型这样定义：



```ts

type ConversationMode = "general" | "agent" | "skill" | "knowledge";



interface Conversation {

&nbsp; id: string;

&nbsp; userId: string;

&nbsp; title: string;

&nbsp; mode: ConversationMode;

&nbsp; primaryResourceId?: string;        // 当前智能体或 skill 或主知识库

&nbsp; attachedKnowledgeBaseIds: string\[];// 可选附加知识库

&nbsp; runtimeProvider: "opencode" | "legacy";

&nbsp; externalSessionId?: string;        // 绑定外部session

&nbsp; createdAt: string;

&nbsp; updatedAt: string;

}

```



再单独做一张运行时绑定表：



```ts

interface ConversationBinding {

&nbsp; conversationId: string;

&nbsp; provider: "opencode" | "legacy\_api" | "websdk" | "url";

&nbsp; integrationId: string;

&nbsp; externalSessionId?: string;

&nbsp; metadata?: Record<string, any>;

}

```



\### 为什么一定要这样做



因为你有三种旧应用接入方式：



1\. API 模式

2\. WebSDK 嵌入

3\. URL 跳转



它们的 session 语义完全不一样。

如果你不做一层内部会话抽象，后面历史、检索、分享、审计、跨端同步都会很乱。



---



\## 旧智能体应用的三种接入策略



\### A. API 接入：这是主路线



这是最值得做统一体验的一类。



因为你已经有：



\* 创建会话接口

\* 会话内对话接口



所以 Portal 完全可以自己接管 UI：



1\. 用户在 Portal 里点击某个智能体

2\. Portal 创建内部 conversation

3\. Adapter 去调用旧应用的“创建会话”，拿到 external session id

4\. 后续消息都由 Portal 代理发送

5\. Portal 存自己的规范化消息记录

6\. UI 展示的是统一聊天界面



这类接入能真正满足你要的：



\* 分组展示

\* session 管理

\* 历史回溯

\* 统一权限

\* 统一审计

\* 统一用户体验



\### B. WebSDK 嵌入：作为过渡态



这类可以快速统一入口，但\*\*很难天然统一消息级历史\*\*。



建议定义成：



\* 有统一壳层

\* 有统一鉴权

\* 有统一资源目录

\* 可能有统一启动记录

\* 但不保证统一消息细粒度回放



除非你给 WebSDK 容器补一层 `postMessage` 事件桥，把消息事件、session 事件、错误事件同步回 Portal。



所以对 WebSDK，我建议是：



\*\*先做“壳层统一 + 启动统一”，后做“事件桥统一”。\*\*



\### C. URL 跳转：最弱接入



这类本质上只是统一入口，不是统一体验。

适合先把旧应用挂进来，但不要把它当长期主形态。



如果某个应用只有 URL，没有 API、没有 WebSDK 事件桥，那你最多做到：



\* 目录统一

\* 权限统一

\* 单点跳转

\* 使用审计



但做不到统一消息历史。



\### 结论



\*\*要做真正统一的“智能体管理和应用界面”，优先级必须是：API > WebSDK > URL。\*\*



---



\## Skill 商店应该怎么落



你的想法里，skill 商店其实不只是个列表页，而是一个 \*\*可启动的对话模式中心\*\*。



\### 我建议 skill 分三层



1\. \*\*公共 skill\*\*



&nbsp;  \* 平台预置

&nbsp;  \* 团队共用

&nbsp;  \* 可审核发布



2\. \*\*个人 skill\*\*



&nbsp;  \* 用户自己创建

&nbsp;  \* 默认私有

&nbsp;  \* 可手动分享给组或角色



3\. \*\*外部/仓库 skill 源\*\*



&nbsp;  \* OpenWork/OpenCode 发现到的 skill

&nbsp;  \* GitHub skill hub

&nbsp;  \* workspace/global/custom roots



OpenCode 当前的 skill 机制本身就是基于 `SKILL.md`，并且按需通过原生 `skill` 工具加载；OpenWork 最近也在继续增强 skill hub 来源配置，这正好说明：\*\*你应该把“skill 发现与同步”交给底层能力，把“skill 目录、权限、发布、对话入口”放到 Portal 层。\*\* (\[OpenCode]\[3])



\### skill 启动流程



用户点击“开始 skill 对话”：



1\. Portal 校验 skill 使用权限

2\. 创建内部 conversation，mode = `skill`

3\. 调 OpenCode 创建 session

4\. Conversation context 里写入 `primaryResourceId = skillId`

5\. 发送第一轮 system 指令或 skill mode 指令

6\. 进入统一聊天页



\### V1 的实现方式



你不需要每轮都把整个 `SKILL.md` 塞进 prompt。

更合理的是：



\* 会话启动时注入稳定 system prompt

\* 明确当前 active skill

\* 明确“优先按该 skill 工作流回答”

\* 需要时让模型通过原生 `skill` 工具加载 skill 内容



这比“把 SKILL.md 硬塞到每次消息里”更稳，也更省 token。

因为 OpenCode 的 skill 就是原生按需加载的。(\[OpenCode]\[3])



---



\## 知识库应该独立成一条线



你的知识库不要直接做成“skill 的附属物”，要做成独立产品能力。



\### 我建议知识库结构是：



\* 公共知识库

\* 个人知识库

\* 团队知识库

\* 临时会话知识包



\### 后端模块



```text

Knowledge Service

&nbsp; ├─ Source Connectors

&nbsp; ├─ Parser / Chunker

&nbsp; ├─ Embedding Pipeline

&nbsp; ├─ Vector Index

&nbsp; ├─ ACL Filter

&nbsp; ├─ Retriever / Reranker

&nbsp; └─ Citation Builder

```



\### 数据存储建议



\* 原始文件：S3 / MinIO

\* 元数据：PostgreSQL

\* 向量索引：先用 pgvector

\* 缓存：Redis



\### 对话时的工作方式



当用户选择某个知识库开始对话时：



1\. Portal 校验知识库 ACL

2\. 创建 conversation，mode = `knowledge`

3\. 每次用户发消息

4\. 先走 query rewrite / retrieval / rerank

5\. 取回上下文

6\. 把检索结果作为上下文送给 OpenCode

7\. 生成答案和引用



\### 为什么知识库不要直接绑死在 OpenCode



因为 OpenCode 当前强项是会话与 agent/skill/tool runtime，不是“企业知识库治理平台”。

你需要的还有：



\* 文档上传

\* 分层权限

\* 来源管理

\* 文档状态

\* 引用与追溯

\* 个人/公共隔离

\* 后续的失效、重建索引、版本管理



这些都更适合放到你自己的 Knowledge Service。



---



\## 权限与鉴权怎么设计



你提到“旧应用有自己的鉴权，可能直接转发用户信息”。

这里我建议你一定不要做“裸转发”。



\### 正确做法：身份翻译层



给每个下游应用配一份 `AuthPolicy`：



```ts

interface AuthPolicy {

&nbsp; strategy: "signed\_jwt" | "token\_exchange" | "header\_forward" | "signed\_launch\_url";

&nbsp; allowedClaims: string\[];           // 只允许透传哪些字段

&nbsp; headerMapping?: Record<string, string>;

&nbsp; audience?: string;

&nbsp; ttlSeconds?: number;

}

```



\### 推荐策略



\#### 1. API 智能体



Portal 生成短期 JWT，带最小 claims：



\* sub

\* user\_id

\* tenant\_id

\* email

\* roles

\* groups



只传白名单字段，不要传整包用户 session。



\#### 2. WebSDK



通过 Portal 生成一次性 launch token，SDK 初始化时换取短期访问令牌。



\#### 3. URL 跳转



通过签名 URL 或反向代理注入鉴权，不要把主平台 cookie 暴露给下游。



\### ACL 建议



资源层权限至少分：



\* view

\* use

\* edit

\* publish

\* share

\* admin



资源类型包括：



\* agent

\* skill

\* knowledge\_base

\* conversation



\### 规则模型



先用 \*\*RBAC + 资源归属 + 显式分享\*\* 即可：



\* public：所有登录用户可见

\* private：仅 owner

\* group：指定用户组

\* role：指定角色

\* explicit share：点对点授权



文档级别 ACL 可以二期再做，V1 先做到知识库级 ACL。



---



\## Portal 的核心后端模块



\### 1. Catalog / Registry Service



负责：



\* 智能体目录

\* skill 目录

\* 知识库目录

\* 分组、标签、排序、收藏、最近使用



\### 2. Conversation Orchestrator



负责：



\* 创建 conversation

\* 创建外部 runtime session

\* 绑定 external session id

\* 规范化消息

\* 流式转发

\* 历史回放

\* 摘要和标题生成



\### 3. Integration Adapter Layer



负责把不同类型的应用接成统一协议：



\* OpenCode adapter

\* Legacy API adapter

\* WebSDK adapter

\* URL adapter



\### 4. Knowledge Service



负责：



\* 文档导入

\* 切片、向量化

\* 检索和引用



\### 5. Auth / ACL / Audit



负责：



\* 单点登录

\* 令牌签发

\* 权限判断

\* 下游 claims 映射

\* 审计日志



---



\## 前端产品结构怎么做才像“AI 原生”



我建议前端不要照搬 OpenWork，而是更接近 \*\*Kimi / Minimax 那种低学习成本的“单入口 + 资源切换”\*\*。



\### 左侧一级导航



只保留 5 个：



\* 首页

\* 对话

\* 智能体

\* Skill

\* 知识库



管理员再多一个“管理台”。



\### 首页



首页不要像管理后台，要像 AI 入口：



\* 一个大输入框

\* 最近使用的智能体

\* 推荐 skill

\* 常用知识库

\* 分组卡片



分组建议按业务域，而不是按技术实现方式：



\* 研发助手

\* 运营助手

\* 销售助手

\* 法务助手

\* 数据分析



\### 对话页



顶部用 context chips 明确告诉用户自己现在在哪个模式：



\* 当前智能体：合同审查助手

\* 当前 skill：需求分析

\* 当前知识库：法务制度库



输入框上方可显示 3 个 starter prompts。



右侧上下文面板默认收起。

技术信息、raw logs、host URL、worker id 这类内容只放到二级详情里。OpenWork 架构文档也明确写了：技术诊断信息应该是 progressive disclosure，而不是默认 UI。(\[GitHub]\[4])



\### 对普通用户隐藏什么



默认隐藏：



\* tool names

\* file diffs

\* raw permissions

\* worker / runtime 细节

\* 底层 session id



OpenWork README 里也提到，它默认隐藏模型推理和敏感工具元数据；这个思路对你的普通用户产品同样合适。(\[GitHub]\[2])



---



\## 为什么我建议“模块化单体”而不是一上来微服务



你现在的主要难点不是吞吐量，而是 \*\*统一接入、统一会话、统一权限、统一体验\*\*。



所以第一版更适合：



\* 一个 Portal Web

\* 一个 Portal Backend

\* 一个 PostgreSQL

\* 一个 Redis

\* 一个对象存储

\* 一个 pgvector

\* 外加 OpenCode / OpenWork / Legacy adapters



也就是 \*\*模块化单体 + 适配器模式\*\*。



这样你实现成本最低，排障路径最短。

等以后知识库、编排、审计确实独立变重了，再拆服务。



---



\## 推荐技术栈



如果你没有既有强约束，我建议直接走 TypeScript：



\### 前端



\* Next.js 或 React SPA

\* TanStack Query

\* Zustand

\* SSE / WebSocket

\* 组件库用 shadcn/ui 或 Ant Design



\### 后端



\* NestJS 或 Hono

\* PostgreSQL

\* Redis

\* S3 / MinIO

\* pgvector

\* Casbin 或自定义 ACL 模块



\### 运行时接入



\* OpenCode：作为会话引擎

\* OpenWork server：作为 skills / workspace / config 文件侧桥

\* Legacy adapter：统一三种旧应用接入协议



因为 OpenWork 文档已经明确它自身就是通过 SDK 和 SSE 方式接 OpenCode，所以你沿用这个思路最顺。(\[GitHub]\[4])



---



\## 最关键的几张表



你后端至少要有这些表：



\* `users`

\* `groups`

\* `resources`

\* `resource\_permissions`

\* `integrations`

\* `knowledge\_bases`

\* `knowledge\_documents`

\* `conversations`

\* `conversation\_bindings`

\* `messages`

\* `favorites`

\* `audit\_logs`



其中最关键的是：



\### `resources`



统一存 agent / skill / knowledge



\### `conversations`



统一存用户视角会话



\### `conversation\_bindings`



统一存它绑定了哪个 OpenCode session 或哪个旧智能体 session



\### `messages`



统一存规范化消息



---



\## 你现在最值得先做的 MVP



\### 第一步



先把 \*\*资源目录 + 会话编排 + API 智能体接入\*\* 做通。

也就是：



\* 智能体分组展示

\* 统一聊天页面

\* session 列表和历史

\* 旧智能体 API 接入

\* Portal 自己持久化消息



\### 第二步



加上 \*\*skill 商店 + skill 模式对话\*\*：



\* 公共 / 个人 skill

\* skill 权限

\* 选中 skill 直接新建会话

\* skill 模式 starter prompts



\### 第三步



加 \*\*知识库选择对话\*\*：



\* 公共 / 个人知识库

\* 选择 KB 后对话

\* 引用和权限过滤



\### 第四步



再补 \*\*WebSDK / URL 接入\*\*：



\* 统一壳层

\* 统一启动入口

\* 能做事件桥的尽量补事件桥

\* 做不到统一历史的标记成“嵌入型应用”



---



\## 我对你这个项目的最终判断



你的方向是对的，但建议你把系统边界再收紧一点：



\*\*OpenCode = 推理与会话引擎\*\*

\*\*OpenWork server = skill / workspace / config 的 host-side bridge\*\*

\*\*你的 Portal = 真正的产品层\*\*



也就是说：



\* 不要把 OpenWork 当最终用户产品

\* 不要让旧智能体各自管理用户会话真相

\* 不要把知识库塞进 skill 体系里

\* 不要让浏览器直接碰本地 skill / config 文件

\* 不要一开始做多 skill、多智能体混合态



把这几条守住，你这个“统一智能体管理和应用界面”会很稳。



下一步最适合直接定的是 \*\*资源模型 + Conversation API + Legacy Adapter 协议\*\*。



\[1]: https://opencode.ai/docs/zh-cn/server/ "https://opencode.ai/docs/zh-cn/server/"

\[2]: https://github.com/different-ai/openwork/blob/dev/README.md "https://github.com/different-ai/openwork/blob/dev/README.md"

\[3]: https://opencode.ai/docs/zh-cn/skills/ "https://opencode.ai/docs/zh-cn/skills/"

\[4]: https://github.com/different-ai/openwork/blob/dev/ARCHITECTURE.md "https://github.com/different-ai/openwork/blob/dev/ARCHITECTURE.md"



