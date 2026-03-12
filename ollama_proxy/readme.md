我先给结论：你现在这版更像一个 **PoC 级别的转发器**，还不是一个“能稳定伪装成 Ollama 原生服务”的兼容层。问题不在 FastAPI 本身，而在三层语义没有对齐：**Ollama 对外是无状态的 `messages/prompt` 接口、流式输出是 NDJSON、REST 侧多模态图片输入是 `images` 基于 base64；而你的上游是强依赖 `conversation_id` 的有状态 SSE 服务，并且图片要走 `QueryExtends.Files[].Url`。** 官方文档当前也明确了 `/api/chat`、`/api/generate` 的请求/响应结构、`thinking` 字段、流式 NDJSON 以及 vision 的 REST 输入方式。([Ollama 文档][1])

你现有代码里，最需要改的地方有六个。第一，**每次请求都 `create_conversation()`**，会把 Ollama 客户端一次次传来的连续会话打散成多个后端会话，等于主动丢失记忆。第二，**只取最后一条 user message**，在新建会话场景下会丢掉 system、assistant 和整个历史。第三，**SSE 解析不稳**：`strip("data:")` 不是去前缀，而是把两端所有 `d/a/t/:` 字符都剥掉，属于隐蔽 bug。第四，**`async def` + `requests.Response.iter_lines()` 会阻塞事件循环**。第五，**多模态只停留在“可能要桥接图片 URL”**，没有形成可控的文件桥接服务。第六，**兼容面太窄**：很多 Ollama 客户端除了 `/api/chat`、`/api/generate`，还会探测 `/api/tags`、`/api/show`、`/api/version`、`/api/ps`；这些都是官方 API 的现有端点。([Ollama 文档][2])

我建议你把方案升级成“**协议兼容层 + 会话映射层 + 图片桥接层 + 模型目录层**”四层架构，而不是只做一个薄转发。核心是：**对外完全说 Ollama 的语言，对内才说你现有模型服务的语言**。这样客户端看到的是 `/api/chat` / `/api/generate` 的标准 NDJSON/JSON，代理内部再决定什么时候复用已有 `conversation_id`，什么时候新建会话并把历史重建成单次输入。官方当前对流式的定义也是 `application/x-ndjson` 的逐行 JSON，而不是把下游 SSE 原样透传；`stream:false` 则应该返回一次性 JSON。([Ollama 文档][3])

我推荐的二版会话策略是：

1. **主路径：前缀哈希命中**

   * 对 `messages` 做规范化后计算“前缀哈希链”。
   * 代理维护一个“**会话 DAG 映射表**”：`消息前缀哈希 -> 后端 conversation_id`。
   * 新请求到来时，查找**最长已知前缀**。
   * 如果命中的前缀后面只剩“最后一条 user 消息”，就直接复用这个 `conversation_id`，把最后一句发给上游。

2. **回退路径：历史重建**

   * 一旦发现用户改历史、分叉、导入旧会话、或者找不到可复用前缀，就：

     * 新建后端会话；
     * 把完整 `messages` 渲染成结构化 prompt；
     * 把历史里所有还需要的图片重新桥接成 `Files[]`；
     * 再发给上游。
   * 这条路径不是 100% 语义等价，但在你当前只暴露了 `create_conversation()` 和 `chat_query_v2_sse()` 两个能力的前提下，是最稳的兼容回退。

这套设计的关键优点是：**线性对话时几乎不损失上游会话记忆；分叉/编辑/导入时也不会直接崩，而是退化成“带完整历史的单次重建”。**

多模态这块，你的直觉是对的：必须单独做“**图片桥接访问服务**”。因为 Ollama 官方当前在 REST API 里要求的是 `images` 数组，内容是 **base64 编码图像数据**；SDK 才可以接受路径、URL 或原始 bytes。你的上游反过来要求 `QueryExtends.Files[].Url`，所以代理层必须做这件事：**接收 base64 -> 落盘/对象存储 -> 生成可访问 URL -> 组装成 `QueryExtends.Files[]`。** ([Ollama 文档][4])

这个桥接层我建议分两档：

* 开发/单机：FastAPI 暴露 `GET /bridge/files/{token}/{filename}`，文件落本地磁盘即可。
* 生产/多实例：不要只靠本地磁盘。因为代理如果有多个 Pod/实例，图片请求可能打到另一个实例直接 404。生产更稳的是：

  * Nginx + 共享卷，或者
  * MinIO / S3 / OSS 预签名 URL。

同时一定加上这些约束：

* 只接受图片 MIME；
* 单图大小上限；
* URL token 随机化；
* TTL 过期清理；
* 不允许目录穿越；
* 日志里不要打印原始 base64。

关于 Ollama 兼容面的边界，我建议这样定：

* **应该支持**

  * `/api/chat`
  * `/api/generate`
  * `stream: true/false`
  * `think`
  * vision `images`
  * `/api/tags`
  * `/api/show`
  * `/api/version`
  * `/api/ps`

* **先明确标成 best-effort 或暂不支持**

  * `tools`
  * `tool_calls`
  * `logprobs`
  * 精确的 `total_duration/prompt_eval_count/eval_count`
  * 完整等价的 `keep_alive`
  * `format=json/schema` 的严格保证

这样定的原因很简单：官方 `/api/chat` 当前确实支持 `tools`、`thinking`、`tool_calls`、`logprobs` 等字段；如果你的上游根本没有结构化工具调用能力，代理就不该默默吞掉这些字段，最好走“严格模式 501 / 兼容模式忽略但记日志”的策略。([Ollama 文档][1])

我建议你实际暴露的端点集合是：

* `POST /api/chat`
* `POST /api/generate`
* `GET /api/tags`
* `POST /api/show`
* `GET /api/version`
* `GET /api/ps`
* `GET /bridge/files/{token}/{filename}`
* `GET /healthz`

这里特别说明一下模型目录端点：官方现在已经有 `/api/tags` 用于列模型、`/api/show` 看模型细节、`/api/version` 看版本、`/api/ps` 看运行中模型。很多 UI 会先打这些端点做能力探测，所以不补齐的话，常见 Ollama 客户端会表现成“能连上但模型列表空白”或者“功能开关不正确”。([Ollama 文档][2])

实现细节上，我建议你把当前代码改成下面这些原则：

* **FastAPI 路由先用同步 `def`**，因为你上游现在是 `requests` 风格阻塞流；不要在 `async def` 里直接 `iter_lines()`。
* **SSE 解析用标准事件解析器**，兼容 `event:` 和 `data:`，并容忍你现在这种近似 `data: {...}` 的单行 JSON。
* **不要再用 `strip("data:")`**，改成 `split("data:", 1)[1]` 或 `removeprefix("data:")`。
* **上游 thought 事件映射到 Ollama 的 `message.thinking` / `thinking`**，而不是偷塞到 `content`。
* **`message_end` 时输出最终 `done: true` 块**，不要只靠连接断开让客户端猜结束。
* **user_id 不要写死**，至少从 `X-User-Id`、Bearer Token 哈希、或客户端 IP 兜底推导。
* **模型名不要写死**，做一个 model registry，把 Ollama 的 `model` 映射到你内部的 app/model 路由。
* **会话映射和图片索引在生产放 Redis/共享存储**，不要只放进程内内存。

我已经按这个思路给你做了一份可直接改造的参考实现，默认带 mock upstream，替换适配器就能接你的真实函数：

* 代码参考实现：[ollama_proxy_v2.py](sandbox:/mnt/data/ollama_proxy_v2.py)
* 方案说明文档：[ollama_proxy_review_and_plan.md](sandbox:/mnt/data/ollama_proxy_review_and_plan.md)

这份实现里已经包含了这些关键点：

* `/api/chat`、`/api/generate` 的 NDJSON/JSON 双模式
* 会话 DAG 映射
* 历史回退重建
* 图片桥接下载路由
* `/api/tags`、`/api/show`、`/api/version`、`/api/ps`
* `thinking` 映射
* 严格/兼容两种字段处理思路
* 可替换的 `MockUpstreamClient / PlaceholderRealUpstreamClient`

你现在最值得优先迭代的顺序是：

1. 先把 **会话映射 + 历史重建** 做对。
2. 再把 **图片桥接** 从“临时 URL”升级为“有 TTL、有鉴权 token 的文件服务”。
3. 然后补齐 **`/api/tags` `/api/show` `/api/version` `/api/ps`**。
4. 最后再考虑 `tools / format / logprobs` 这些高级兼容。

按照这个顺序做，兼容性会从“单接口能跑”提升到“绝大多数 Ollama 客户端可接入、可持续演进”。如果你愿意，我下一步可以直接把你这份参考实现继续收敛成 **可部署的多文件生产版目录结构**（`main.py / adapters.py / sessions.py / bridge.py / config.py`）并补上 Dockerfile 与 Nginx/MinIO 部署建议。

[1]: https://docs.ollama.com/api/chat "https://docs.ollama.com/api/chat"
[2]: https://docs.ollama.com/api/tags "https://docs.ollama.com/api/tags"
[3]: https://docs.ollama.com/api/streaming "https://docs.ollama.com/api/streaming"
[4]: https://docs.ollama.com/capabilities/vision "https://docs.ollama.com/capabilities/vision"
