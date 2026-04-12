结合你的目标和当前仓库，我建议下一版本做成一个**兼容式小改版**：不做资源注册中心重写，不切数据库大迁移，也不把现有运行时全推翻；而是在现在这套 `portal_sid` 本地 session、MemoryStore、`resources.generated.json`、`type + launch_mode + adapter` 之上，补一层 `entrypoint / user-state / openwork-meta`，把“用户会话管理、skill 管理、资源管理”先做稳。这和你在项目说明里提到的“短期 iframe、长期 skill/API 化、按用户权限展示资源、记录统计、搜索推荐”的方向是一致的。 ([GitHub][1])

先说范围控制：这版**不建议**直接上完整 Postgres 资源注册中心，也**不建议**立刻把所有 native chat 切到 OpenWork proxy。OpenWork 官方架构里，server 的确是 UI 侧 API surface，并可代理 OpenCode；OpenCode server 也已经暴露了 session、fork、diff、summarize、revert、prompt_async、command、shell、file 等更强运行时能力，但这些更适合下一阶段。下一版先把目录、会话和 skill 组织方式改顺。([GitHub][2])

## 版本目标

这版我建议只做四件事：

1. 会话侧把“资源 + 入口”关系补清楚。
2. skill 侧把“prompt skill”升级成“可管理的资源入口”。
3. 资源侧补搜索、最近使用、收藏、规则推荐。
4. OpenWork 侧把 adapter 从“列技能列表”扩到“workspace 读能力入口”。

---

## 按当前仓库目录的修改方案

### `backend/app/models.py`

现在的 `Resource` 还是 `type / launch_mode / adapter` 单入口模型；`SessionBinding` 只保存了 `adapter / engine_session_id / external_session_ref / workspace_id / skill_name`；`AuthSession` 只有基础用户字段；`SessionResumePayload` 也没有入口维度。下一版不要推翻这些字段，而是**增量加可选字段**，保持兼容。([GitHub][3])

建议新增这些结构：

```python
class ResourceEntrypoint(BaseModel):
    entrypoint_id: str
    title: str
    adapter: str
    launch_mode: LaunchMode
    enabled: bool = True
    is_default: bool = False
    skill_name: Optional[str] = None
    workspace_id: Optional[str] = None

class ResourceCapabilities(BaseModel):
    searchable: bool = True
    resumable: bool = True
    upload: bool = False
    auditable: bool = True
```

然后在现有模型上做小幅扩展：

* `Resource`

  * 新增 `resource_kind: Optional[str]`，例如 `chat | skill | kb | agent | integration`
  * 新增 `entrypoints: List[ResourceEntrypoint] = []`
  * 新增 `capabilities: Optional[ResourceCapabilities]`
  * 新增 `recommended_for: Optional[dict]`
* `SessionBinding`

  * 新增 `entrypoint_id: Optional[str]`
* `AuthSession`

  * 新增 `user_snapshot: Dict[str, Any]`
  * 新增 `profile_tags: List[str] = []`
* `SkillInfo`

  * 新增 `workspace_id / version / entrypoint_id / source / status`
* `SessionResumePayload`

  * 新增 `entrypoint_id / workspace_id / skill_name`

关键点是：**旧资源不改 JSON 也能继续跑**。`CatalogService` 在加载时，如果发现 `entrypoints` 为空，就自动根据旧的 `type + launch_mode + adapter` 补一个 `default` 入口。

---

### `backend/app/catalog/service.py`

当前 `CatalogService` 直接从 `settings.resources_path` 读 JSON 到内存，`reload_generated_resources()` 只是清缓存重载，`get_skill_resources()` 也只是按 `ResourceType.SKILL_CHAT` 做过滤。([GitHub][4])

这版在这里补三个方法最值钱：

* `normalize_legacy_resource(resource)`
  把老资源自动补成 `entrypoints=[default]`
* `resolve_entrypoint(resource, entrypoint_id=None)`
  统一 launch/resume 入口选择
* `get_skill_store_resources()`
  不再只看 top-level `type == skill_chat`，而是识别“拥有 `skill_chat` entrypoint 的资源”

这样以后一个旧应用可以默认是 iframe 资源，但仍然出现在 skill 商店里，因为它有 `assistant` 入口。

再补两个轻量能力：

* `search_resources(query, user)`
* `recommend_resources(user)`

搜索先做简单关键词匹配：`name + description + tags + group + skill_name`。推荐先做规则版，不碰 LLM 画像。

---

### `backend/app/catalog/sync_service.py` 与 `scripts/sync_resources.py`

这是下一版最值得动的地方。当前同步链路是：`OpenWorkAdapter.list_skills()` → `normalize_skill()` → 合并 static resources 和 overrides → 写回 `resources.generated.json`；而且当 discovered skill 与 static resource 同 ID 时，脚本会直接保留 static、跳过 discovered。([GitHub][5])

下一版把这条规则从“跳过”改成“**合并 entrypoints**”：

* static 保留产品级字段：`name / group / acl / description`
* discovered skill 贡献 native assistant entrypoint
* overrides 继续覆盖 starter prompts、启停、ACL 等

建议把 `normalize_skill()` 扩成支持一个绑定字段：

* `portal_resource_id`

它的来源优先级可以这样定：

1. skill frontmatter `metadata.portal_resource_id`
2. overrides 配置
3. 默认回退 `skill-<skill_name>`

OpenCode 的 skill 规范本来就是 `SKILL.md` + YAML frontmatter，并且允许 `metadata` 字段，所以这个绑定方式和官方机制是对齐的。([OpenCode][6])

这样你就能把一个旧应用资源同步成这种形态：

```json
{
  "id": "hr-policy",
  "name": "HR 政策助手",
  "type": "iframe",
  "launch_mode": "iframe",
  "adapter": "iframe",
  "resource_kind": "agent",
  "entrypoints": [
    {
      "entrypoint_id": "ui",
      "title": "打开应用",
      "adapter": "iframe",
      "launch_mode": "iframe",
      "is_default": true
    },
    {
      "entrypoint_id": "assistant",
      "title": "聊天入口",
      "adapter": "skill_chat",
      "launch_mode": "native",
      "enabled": false,
      "skill_name": "hr-policy",
      "workspace_id": "hr"
    }
  ]
}
```

这就是“短期 iframe、长期 skill 化”最小代价的落地方式。

---

### `backend/app/adapters/skill_chat.py` 与 `backend/app/adapters/opencode.py`

当前 `SkillChatAdapter` 本质上还是 **prompt skill**：它用内存 `_session_skill_map` 记 `skill_name`，发消息时注入 system prompt，要求模型使用原生 `skill` 工具加载该 skill。`OpenCodeAdapter` 则主要调用 `/session` 和 `/session/:id/message`。([GitHub][7])

这版建议只做两步，不要贪大：

第一步，把 skill 元信息的可信来源改成 `SessionBinding`。
也就是发消息时优先读 `binding.skill_name / binding.workspace_id / binding.entrypoint_id`，不要依赖热缓存。

第二步，给 `OpenCodeAdapter.send_message()` 和 `send_message_stream()` 增加几个可选参数：

* `agent`
* `tools`
* `extra_body`

因为 OpenCode 的 `/session/:id/message` 本身就支持 `system`、`tools`、`agent` 这些字段。这样你现在仍然能保持 `prompt_only`，但下一版做 bridge skill 时，不需要再改 adapter 协议。([OpenCode][8])

同时在 resource config 里加一个最小运行时枚举：

* `skill_runtime = "prompt_only" | "bridge_api"`

这版默认全是 `prompt_only`。
只有个别旧应用想试 API bridge 时，才切到 `bridge_api`。

---

### `backend/app/adapters/openwork.py`

当前 `OpenWorkAdapter` 只包了三类接口：列 skills、查单个 skill 状态、reload engine。([GitHub][9])

而 OpenWork 官方定位不只是“skill 文件接口”，它本身就是 remote client 的 filesystem-backed API，server 还负责代理 OpenCode；源码里也已有 approvals、audit、commands、events、file-sessions、mcp 等模块。([GitHub][2])

所以这版建议把 `openwork.py` 做成两层：

* 底层 `_request(method, path, ...)`
* 上层轻量 wrapper：

  * `list_skills()`
  * `get_skill_status()`
  * `reload_engine()`
  * `get_workspace_summary()`
  * `list_workspace_commands()`
  * `list_workspace_mcp()`
  * `list_workspace_audit()`
  * `probe_opencode_proxy()`

注意，这版**不要求**你把聊天主链路切到 OpenWork proxy；但要把 adapter 准备好，skill 商店和管理端先用起来。

另外，`/api/skills` 的组装建议改成：
**按 workspace 分组，一次 `list_skills()` 拉全，再本地 merge 到 Portal skill resources**。这会比逐个查状态更稳，也更贴合你现在的 OpenWork 接法。

---

### `backend/app/auth/deps.py`、`backend/app/auth/routes.py`、`backend/app/store/memory_store.py`

现在的认证流是：SSO code exchange / callback 时写 `portal_sid` cookie；请求进来后从 store 取 `AuthSession`，更新 `last_seen_at`，再去 `user_repo` 按工号查用户；底层 store 目前还是 `MemoryStore` 主实现。([GitHub][10])

这版可以做三个非常实用的小优化：

1. `AuthSession` 里固化 `user_snapshot`
   存 `emp_no / name / dept / email / roles / claims_digest`

2. `MemoryStore` 增加轻量用户态

   * `recent_resources`
   * `favorite_resources`
   * `usage_events`

3. `auth/deps.py` 优先用 `user_snapshot` 还原 `SessionUser`

   * 只有缺字段时才回查 `user_repo`

这样能立刻支撑：

* 最近使用
* 收藏
* 基础画像标签
* 搜索/推荐的用户上下文

用户画像这版也别上 LLM，总结成规则标签就够：

* `prefers_native_chat`
* `frequent_data_analysis`
* `uses_hr_workspace`

---

### `backend/app/main.py`

当前 `main.py` 已经有资源 ACL 过滤、`/api/resources/{id}/launch`、`/api/sessions/{id}/resume`，launch 时会为所有资源创建 `PortalSession + SessionBinding`，resume 时明确以 `binding.adapter` 作为恢复分发依据。([GitHub][11])

这版这里做最小但最值钱的改动：

1. 新增 `LaunchRequest`

```python
class LaunchRequest(BaseModel):
    entrypoint_id: Optional[str] = None
```

2. `POST /api/resources/{resource_id}/launch`

   * 解析 `entrypoint_id`
   * 用 `resolve_entrypoint()` 决定 adapter / launch_mode
   * 把 `binding.entrypoint_id` 写进去

3. `GET /api/sessions/{portal_session_id}/resume`

   * 返回 `entrypoint_id / workspace_id / skill_name`

4. 新增轻量接口

   * `GET /api/resources/search?q=`
   * `GET /api/resources/recent`
   * `GET /api/resources/favorites`
   * `POST /api/resources/{id}/favorite`
   * `DELETE /api/resources/{id}/favorite`
   * `GET /api/resources/recommended`
   * `GET /api/skills?workspace_id=&q=&installed=`

5. launch / resume / send_message 时记录 usage event

推荐逻辑要坚持一个原则：**ACL-first**。当前资源列表和 launch 路径本来就先做 ACL 过滤/校验，这个顺序不要变。([GitHub][11])

---

### `frontend/src/types.ts`、`frontend/src/api.ts`、`frontend/src/App.tsx`

当前前端类型还是旧的 `Resource / SkillInfo / SessionResumePayload`；API 里只有 grouped resources / launch / admin sync / listSkills；`App.tsx` 在点 native resource 时会先恢复最近活跃 session。([GitHub][12])

这版的改法很直接：

* `types.ts`

  * 给 `Resource` 增加 `entrypoints / capabilities / resource_kind`
  * 给 `SessionResumePayload` 增加 `entrypoint_id / workspace_id / skill_name`
  * 给 `SkillInfo` 增加 `workspace_id / version / entrypoint_id / source / status`

* `api.ts`

  * `launchResource(id, entrypointId?)`
  * 新增 `searchResources / listRecentResources / listFavoriteResources / toggleFavorite / listRecommendedResources`
  * `skillApi.listSkills(params)`

* `App.tsx`

  * `handleSelectResource(resource, entrypointId?)`
  * `applyResumePayload()` 根据 `entrypoint_id` 恢复
  * 有多个入口时，默认走 default entrypoint；需要时再弹一个小菜单选择“聊天 / 打开应用”

---

### `frontend/src/components/ResourceSidebar.tsx` 与 `SessionSidebar.tsx`

当前资源栏只有 group 折叠，没有搜索、最近、收藏；会话栏只分 native 和 embedded。([GitHub][13])

这版只补轻交互，不重做 UI：

* `ResourceSidebar`

  * 顶部加搜索框
  * 新增三个 section：推荐、最近、收藏
  * 资源卡片显示 badge：`skill / iframe / native`
  * 多入口资源显示一个小下拉动作

* `SessionSidebar`

  * 会话项加一个入口 badge，例如 `assistant / ui`
  * 当前资源过滤开关可选
  * skill 会话显示 `workspace_id` 或 `skill_name` 的简短提示

skill 商店这版不要单独再造一套页面。**更合适的是：skill 商店 = 资源目录的一个过滤视图**。

---

## skill 机制这版怎么迭代

这部分我建议你在设计文档里直接定成一句话：

**skill 是资源的 native entrypoint，不一定是独立资源；这版运行时只分 `prompt_only` 和 `bridge_api`。**

原因很简单：

* 当前 `SkillChatAdapter` 已经是“system prompt 引导 + 原生 `skill` 工具加载”的模式。([GitHub][7])
* OpenCode 官方 skill 也是通过 `SKILL.md` 被原生 `skill` 工具按需加载。([OpenCode][6])
* OpenCode 的 message API 已支持 `tools` 字段，所以后面做 bridge skill 不需要再改协议。([OpenCode][8])

所以这版的 skill 标准目录可以先约定成：

```text
skills/<skill-name>/
  SKILL.md
  manifest.json
  executor.py        # 可选，bridge_api 时使用
  examples/
```

`manifest.json` 或 frontmatter metadata 里建议至少有：

* `portal_resource_id`
* `skill_runtime`
* `workspace_id`
* `display_name`

然后 Portal 的规则是：

* `prompt_only`：继续走现在的 skill_chat
* `bridge_api`：仍走 skill_chat，但允许后续加 tools / executor
* 强 UI 的旧应用：继续保留 iframe entrypoint，不强行 skill 化

---

## 这版最小交付物

如果按你“下一版本小幅优化”的口径，我会把交付物压成这 6 项：

1. `Resource.entrypoints` 与 `SessionBinding.entrypoint_id`
2. `sync_resources.py` 从“同 ID 跳过”改成“同 ID 合并 entrypoints”
3. `/api/resources/{id}/launch` 支持 `entrypoint_id`
4. `/api/resources/search / recent / favorites / recommended`
5. `/api/skills` 改成 workspace-aware 的 richer 视图
6. 资源栏加搜索、推荐、最近、收藏

这样改完，你的 Portal 还是现在这套架构，但会从“单入口资源门户”升级成“**可治理的多入口资源门户**”；skill 也会从“单纯一类资源”升级成“**资源体系里的重要入口能力**”。

下一步最适合把这个方案再拆成一个**按文件的 PR checklist**，比如先后端 schema / API，再 sync / openwork，再前端 sidebar。

[1]: https://github.com/yuha19990602-maker/agenthub "https://github.com/yuha19990602-maker/agenthub"
[2]: https://github.com/different-ai/openwork/blob/dev/ARCHITECTURE.md "openwork/ARCHITECTURE.md at dev · different-ai/openwork · GitHub"
[3]: https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/models.py "agenthub/backend/app/models.py at master · yuha19990602-maker/agenthub · GitHub"
[4]: https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/catalog/service.py "agenthub/backend/app/catalog/service.py at master · yuha19990602-maker/agenthub · GitHub"
[5]: https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/catalog/sync_service.py "agenthub/backend/app/catalog/sync_service.py at master · yuha19990602-maker/agenthub · GitHub"
[6]: https://opencode.ai/docs/zh-cn/skills/ "代理技能 | OpenCode"
[7]: https://raw.githubusercontent.com/yuha19990602-maker/agenthub/master/backend/app/adapters/skill_chat.py "raw.githubusercontent.com"
[8]: https://opencode.ai/docs/zh-cn/server/?utm_source=chatgpt.com "服务器 | OpenCode"
[9]: https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/adapters/openwork.py "agenthub/backend/app/adapters/openwork.py at master · yuha19990602-maker/agenthub · GitHub"
[10]: https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/auth/routes.py "agenthub/backend/app/auth/routes.py at master · yuha19990602-maker/agenthub · GitHub"
[11]: https://github.com/yuha19990602-maker/agenthub/blob/master/backend/app/main.py "agenthub/backend/app/main.py at master · yuha19990602-maker/agenthub · GitHub"
[12]: https://github.com/yuha19990602-maker/agenthub/blob/master/frontend/src/types.ts "agenthub/frontend/src/types.ts at master · yuha19990602-maker/agenthub · GitHub"
[13]: https://github.com/yuha19990602-maker/agenthub/blob/master/frontend/src/components/ResourceSidebar.tsx "agenthub/frontend/src/components/ResourceSidebar.tsx at master · yuha19990602-maker/agenthub · GitHub"
