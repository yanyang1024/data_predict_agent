我先给结论：

**最适合你的路线，不是先硬改 OpenCode 核心，而是把 OpenCode 当“推理与会话引擎”，把 OpenWork 当“技能商店与业务壳层”。**
原因很直接：OpenWork 现在真正的交互 UI 在 `packages/app`，服务层在 `packages/server`；这个 server 已经是一个面向远程客户端的、基于文件系统的 API，而且已经有 `GET /workspace/:id/skills` / `POST /workspace/:id/skills` 这类技能接口。反过来，OpenCode 公开的 server 文档重点是 session、message、command、file、agent、event 等通用能力，没有把“技能商店”作为一等公民 API 暴露出来。([GitHub][1])

再补一个很关键的判断：**如果你想改 OpenCode 自带的 Web 前端，当前应该看的是 `anomalyco/opencode` 仓库里的 `packages/app`，不是 `packages/web`。** 现在这个仓库会跳转到 `anomalyco/opencode`；其中 `packages/app` 是 Solid + Vite 的前端应用，README 还明确提到它的 E2E 测试依赖本地 `localhost:4096` 的 opencode backend；而 `packages/web` 当前看起来是文档站而不是聊天 UI。OpenCode 文档里的“Web”页也只强调了会话和服务器状态。([GitHub][2])

---

## 我调研后的核心判断

### 1）OpenWork 其实已经“半只脚”做成了技能商店

OpenWork 自己就定位成一个“帮助你运行 agents / skills / MCP”的外壳；它强调 extensible、local/remote，还把 skills 和 opencode plugins 视为可安装模块。更重要的是，现有 `packages/app/src/app/pages/skills.tsx` 已经有这些能力：
已安装技能列表、hub 技能列表、导入本地 skill、安装 hub skill、读取/保存 skill，以及“新建 skill 时直接创建会话并预填 `/skill-creator`”。也就是说，你想要的“技能商店”并不是从 0 开始。缺的主要是：**把任意 skill 变成一种可进入的对话模式**。([GitHub][1])

### 2）OpenWork server 天生适合做“本地 skill 目录扫描器”

OpenWork 的架构文档写得很明确：浏览器运行时不能随便读写本地文件，所以凡是 `.opencode/`、`SKILL.md`、`opencode.json` 相关的读取、编辑、打开目录，都应该通过 host-side service，也就是 `packages/server` 来做。现有 `skills.ts` 还已经实现了不少你要的基础能力：
它会从当前工作目录一路向上扫到 git root，读取 `.opencode/skills`、`.claude/skills`，可选再加全局 `~/.config/opencode/skills`、`~/.claude/skills`、`~/.agents/skills`；还能从 frontmatter 或 “When to use” 段落里提取 trigger，并按 skill name 去重。([GitHub][3])

### 3）OpenCode 后端已经足够支撑“skill 模式对话”，第一版不必改核心

OpenCode 的 server API 文档显示，`POST /session/:id/message` 支持 `system`、`agent`、`tools` 等参数；同时它还有原生 `skill` 工具，可以把某个 `SKILL.md` 加载进对话。也就是说，**你完全可以在 OpenWork UI 里实现一个“skill mode”**：
当用户选择某个 skill 后，后续发送消息时自动附加一段 system prompt，明确要求模型优先加载并遵循该 skill。这个做法复用现有 OpenCode 能力，侵入性最低。([OpenCode][4])

### 4）但如果你要“官方级”的 skill-mode，会涉及 OpenCode 核心、SDK、Web App 三层联动

因为当前公开的 OpenCode API 列表里，没有单独的 `/skill` 列表接口；如果你希望“任何第三方客户端”都能原生支持 skill store，而不依赖 OpenWork server，就要在 OpenCode core 里补 skill 列表 / 详情 / 会话 skill-mode 的 API，然后更新 OpenAPI / SDK，再改它自己的 `packages/app`。OpenCode 仓库当前也确实有清晰的模块边界：`packages/opencode/src/server/routes`、`src/session`、`src/skill`、`packages/sdk/openapi.json`、`packages/app`。([OpenCode][4])

---

# 推荐落地方案

## 方案 A：推荐，改 OpenWork，不改 OpenCode 核心

这是我最建议你做的版本。

### 架构分层

```text
你的 Chatbot WebUI（基于 OpenWork packages/app）
        │
        ├─ 调 OpenWork Server（packages/server）
        │    ├─ 扫描技能目录
        │    ├─ 读取 SKILL.md
        │    ├─ 安装/卸载 hub skill
        │    ├─ 管理自定义 skill roots
        │    └─ 生成“skill mode”配置
        │
        └─ 调 OpenCode Server（opencode serve）
             ├─ 创建 session
             ├─ 发送消息
             ├─ SSE 流式事件
             ├─ 调用 skill tool
             └─ 使用 agent / tools / permissions
```

### 为什么这条路最好

第一，OpenWork 已经有 skills 页面和 server。
第二，OpenCode 已经有会话、消息、事件、skill tool。
第三，OpenWork 架构文档明确说，文件系统相关动作应该走 server。
所以你只要把两者拼好，就能很快做出一个可用版本。([GitHub][5])

---

# WebUI 交互逻辑

## 1. 左侧导航

建议保留 3 个一级入口：

* 对话
* 技能商店
* 设置

第一版不要把入口做太多。对新手用户来说，“对话”和“技能商店”分清楚就够了。

---

## 2. 技能商店页

### 页面结构

顶部一排筛选：

* 来源：当前工作区 / 全局 / Hub / 全部
* 路径：默认路径 / 自定义路径
* 搜索框：按 name / description / trigger 搜
* 排序：最近安装 / 名称 / 推荐

中间区域用卡片流展示 skill。

### 每个 skill 卡片建议显示

* skill 名称
* 一句话 description
* 来源标签：workspace / global / hub / custom
* trigger 或 “When to use” 摘要
* 操作按钮：

  * 查看详情
  * 安装 / 更新
  * 编辑
  * 开始技能对话

### 点击“查看详情”

右侧 Drawer 或 Modal 展示：

* skill 名
* description
* 来源路径
* `SKILL.md` 正文预览
* “适合什么时候用”
* “开始技能对话”
* “复制分享链接”或“导出”

这部分和 OpenWork 当前 `skills.tsx` 的交互很接近，只是你需要把“开始技能对话”做成一等按钮。OpenWork 现有 skills 页已经有 read/save/share/install 的骨架。([GitHub][6])

---

## 3. 进入“技能模式对话”

用户点“开始技能对话”后：

1. 如果当前没有会话，就新建一个 session。
2. 如果当前有会话，弹一个轻量选择：

   * 在新会话中打开
   * 在当前会话中切换到此技能
3. 成功后跳到会话页，并在顶部显示：

   * `技能模式：xxx`
   * `退出技能模式`
   * `切换技能`

### 会话页变化

在 skill mode 下：

* 标题栏显示 skill badge
* 输入框上方显示 2～4 个 starter prompts
* 第一条 assistant welcome message 可以说明：

  * 当前启用了哪个 skill
  * 这个 skill 适合做什么
  * 给用户几个示例提问

### 非常重要的产品约束

**V1 一次只允许一个活动 skill。**
不要一上来就做“多 skill 叠加”。这样逻辑会变得很难解释，也很难测。

---

## 4. 对话发送逻辑

当某个 session 处于 skill mode 时，每次发送消息前都做这件事：

* 把 `activeSkill` 从前端状态或 OpenWork server 取出来
* 拼一个稳定的 `system` 指令
* 发送到 OpenCode 的 message 接口

建议 system prompt 模板类似：

```text
You are in skill mode "<skill-name>".
Always treat this skill as the primary workflow for this session.
Load and follow the skill "<skill-name>" using the native skill tool when needed.
If the user asks for something outside this skill, explain that briefly and ask whether to exit skill mode.
Do not silently switch to another skill.
```

这样做的好处是：

* 不需要把整个 `SKILL.md` 每轮都塞进 prompt
* token 更稳定
* 模型还能按需调用原生 `skill` tool 去读 skill 内容

这条路径成立，是因为 OpenCode 的 message API 支持 `system` 参数，而原生 `skill` tool 又能把 `SKILL.md` 加载进对话。([OpenCode][4])

---

# 设计方案

## 一、核心数据结构

建议你先定义这几个类型：

```ts
type SkillSource = "workspace" | "global" | "hub" | "custom";

type SkillSummary = {
  name: string;
  description: string;
  trigger?: string;
  path?: string;
  scope?: "project" | "global";
  source: SkillSource;
};

type SkillDetail = SkillSummary & {
  content: string;
  installed: boolean;
  editable: boolean;
};

type SessionSkillMode = {
  sessionId: string;
  skillName: string;
  skillPath?: string;
  source: SkillSource;
  enabledAt: number;
  starterPrompts: string[];
  pinned: boolean; // 是否每轮都注入 system
};
```

---

## 二、后端接口设计

### 尽量复用现有接口

OpenWork server 已经有：

* `GET /workspace/:id/skills`
* `POST /workspace/:id/skills`
* hub 安装相关能力
* `POST /workspace/:id/engine/reload`

所以不要重造轮子。([GitHub][5])

### 建议新增接口

我建议你新增 4 个：

#### 1）`GET /workspace/:id/skills/:name`

返回 skill 详情：

```json
{
  "name": "api-review",
  "description": "Review an API design and suggest improvements",
  "trigger": "Use when reviewing API contracts",
  "path": "/repo/.opencode/skills/api-review/SKILL.md",
  "scope": "project",
  "source": "workspace",
  "content": "--- ... ---\n# What I do ..."
}
```

#### 2）`POST /workspace/:id/skill-mode/resolve`

输入 skill name，输出会话模式配置：

```json
{
  "skill": { ...SkillSummary },
  "systemPrompt": "You are in skill mode ...",
  "starterPrompts": [
    "请用这个技能帮我分析...",
    "请按照这个技能的流程执行...",
    "先告诉我这个技能适不适合当前问题"
  ]
}
```

#### 3）`GET /workspace/:id/skill-roots`

读取自定义 skill 目录列表。

#### 4）`PATCH /workspace/:id/skill-roots`

允许用户配置额外扫描目录。

---

## 三、关于“特定路径下所有 skill”的实现建议

这里要分成两个层级。

### MVP

先支持这几类路径：

* 当前 workspace 下的 `.opencode/skills`
* 向上到 git root 的继承路径
* 全局路径
* hub

这其实 OpenWork 现有逻辑已经覆盖得差不多了。([GitHub][7])

### 增强版

如果你说的“特定路径”是任意自定义目录，比如：

* `/data/company-skills`
* `/mnt/shared/skills`
* `D:\team\skills`

那就不要直接让前端传一个本地路径然后浏览器去扫。
正确做法是：

1. 把这些目录保存到 OpenWork server 配置里
2. 由 server 负责扫描
3. 扫描结果返回给前端
4. 每个结果附带 `source: "custom"` 和 `rootLabel`

这样才符合 OpenWork 自己的“browser 不能直接读本地文件”的架构原则。([GitHub][3])

---

# 二次开发步骤：推荐版（基于 OpenWork，尽量不改 OpenCode 核心）

## 第 0 步：先把开发环境跑起来

### OpenWork

OpenWork README 现在建议在 repo 根目录：

```bash
git checkout dev
git pull --ff-only origin dev
pnpm install --frozen-lockfile
```

根目录脚本里也有 `dev:ui`，会启动 `@different-ai/openwork-ui`。([GitHub][1])

### OpenCode backend

你的自定义前端更适合连 `opencode serve`，因为它就是纯 HTTP server；如果是浏览器跨域访问，要加 `--cors`。如果不是纯本地回环，还应该加密码保护。([OpenCode][4])

例如：

```bash
opencode serve --port 4096 --cors http://localhost:5173
```

如果你想临时看官方 Web，也可以：

```bash
opencode web --port 4096 --cors http://localhost:5173
```

但我不建议把 `opencode web` 当你自己的生产前端入口，因为它会拉起官方 UI。文档里也说明 `opencode web` 主打的是浏览器里查看会话和服务器状态。([OpenCode][8])

### OpenWork server

本地开发时，可以把 approvals 开到自动，否则每次写入都要审批：

```bash
OPENWORK_APPROVAL_MODE=auto pnpm --filter openwork-server dev
```

OpenWork server README 明确写了写操作默认受 host approval 保护，本地开发可以设 `OPENWORK_APPROVAL_MODE=auto`。([GitHub][5])

---

## 第 1 步：先补后端“技能详情”和“自定义目录”

### 改哪些文件

OpenWork 这边重点看这些文件：

* `packages/server/src/types.ts`
* `packages/server/src/skills.ts`
* `packages/server/src/server.ts`

这些路径和现有 skills 能力都已经在仓库里。([GitHub][9])

### 1.1 在 `types.ts` 增加类型

新增：

* `SkillDetail`
* `SkillRoot`
* `ResolvedSkillMode`

示例：

```ts
export interface SkillDetail extends SkillItem {
  content: string;
  source: "workspace" | "global" | "hub" | "custom";
  root?: string;
}

export interface ResolvedSkillMode {
  skill: SkillDetail;
  systemPrompt: string;
  starterPrompts: string[];
}
```

### 1.2 在 `skills.ts` 拆出更通用的扫描函数

现在 `listSkills()` 已经能扫约定目录。你可以继续抽一层：

* `scanSkillRoot(root, scope, source)`
* `getSkillDetail(workspaceRoot, name, options?)`
* `listSkillsFromConfiguredRoots(workspaceRoot, roots)`

### 1.3 新增“读取 skill 详情”

伪代码：

```ts
export async function getSkillDetail(workspaceRoot: string, name: string): Promise<SkillDetail> {
  const skills = await listSkills(workspaceRoot, true);
  const target = skills.find((x) => x.name === name);
  if (!target) throw new ApiError(404, "skill_not_found", `Skill not found: ${name}`);
  const content = await readFile(target.path, "utf8");
  return {
    ...target,
    content,
    source: target.scope === "global" ? "global" : "workspace",
  };
}
```

### 1.4 支持自定义 roots

最简单的做法：

* server 维护一个 `skillRoots: string[]`
* 每个 root 用和 `listSkillsInDir()` 类似的逻辑去扫
* 返回时给每个 skill 带上 `source: "custom"` 和 `root`

---

## 第 2 步：在 `server.ts` 暴露新接口

建议至少加两个：

### `GET /workspace/:id/skills/:name`

读 skill 详情。

### `POST /workspace/:id/skill-mode/resolve`

返回：

* skill 详情
* systemPrompt
* starterPrompts

伪代码：

```ts
app.post("/workspace/:id/skill-mode/resolve", async (req, res) => {
  const { name } = await req.json();
  const skill = await getSkillDetail(workspaceRoot, name);

  const systemPrompt = [
    `You are in skill mode "${skill.name}".`,
    `Treat this skill as the primary workflow for the session.`,
    `Load and follow the skill "${skill.name}" using the native skill tool when needed.`,
    `If the task is outside this skill, say so briefly and ask whether to exit skill mode.`,
  ].join(" ");

  const starterPrompts = buildStarterPrompts(skill);

  res.json({ skill, systemPrompt, starterPrompts });
});
```

### 一个很实用的小优化

OpenWork 现有 skills 逻辑已经会提取 `trigger`。你可以直接拿它来生成 starter prompts。([GitHub][7])

---

## 第 3 步：前端补“技能商店 → 技能模式”闭环

### 改哪些文件

建议从这些入口动手：

* `packages/app/src/app/types.ts`
* `packages/app/src/app/lib/openwork-server.ts`
* `packages/app/src/app/pages/skills.tsx`
* `packages/app/src/app/pages/session.tsx`
* `packages/app/src/app/context/session.ts`
* `packages/app/src/app/state/sessions.ts`

这些目录都在当前 OpenWork app 结构里。([GitHub][10])

### 3.1 在 `types.ts` 定义前端状态

```ts
export type SessionSkillMode = {
  skillName: string;
  skillPath?: string;
  source: "workspace" | "global" | "hub" | "custom";
  systemPrompt: string;
  starterPrompts: string[];
};
```

### 3.2 在 `lib/openwork-server.ts` 增加 API 封装

加两个方法：

* `getSkillDetail(workspaceId, name)`
* `resolveSkillMode(workspaceId, name)`

### 3.3 修改 `pages/skills.tsx`

当前 skills 页已经有这些 prop：

* `skills`
* `hubSkills`
* `installHubSkill`
* `readSkill`
* `saveSkill`
* `createSessionAndOpen`
* `setPrompt`

你要做的是再加一条主操作：

* `startSkillConversation(skillName)`

现有代码里“新建 skill”已经是：
先创建 session，再 `setPrompt("/skill-creator")`。
你可以用同样的思路做“开启 skill mode”，只是这里不是塞 `/skill-creator`，而是设置 session skill mode。([GitHub][6])

### 3.4 在 `context/session.ts` 保存 skill mode

推荐用：

* `sessionId -> SessionSkillMode` 的映射
* 本地持久化到 localStorage

第一版不用把这个状态写进 OpenCode session 里，因为公开 API 里没有现成的 session metadata 能力。先在 OpenWork 层解决最省事。

---

## 第 4 步：改发送消息逻辑

这是整件事的核心。

### 做法

找到当前发送消息的统一入口，把它包一层：

```ts
async function sendPromptWithSkillMode(sessionId: string, userText: string) {
  const mode = skillModeStore[sessionId];

  return client.session.message(sessionId, {
    system: mode?.systemPrompt,
    parts: [
      { type: "text", text: userText }
    ]
  });
}
```

如果你项目里现在用的是 SDK 封装方法，不一定正好叫这个名字，但原理一样：
**有 active skill mode 时，就附加 `system`。**
OpenCode 文档已经说明 message API 支持 `system` 参数。([OpenCode][4])

### 一个经验建议

不要把整份 `SKILL.md` 每轮都塞进去。
只要 system prompt 里点名当前 skill，并要求优先使用原生 `skill` tool 即可。

---

## 第 5 步：会话页加“技能模式”状态感知

在 `pages/session.tsx` 里加：

* 顶部 badge：`技能模式：api-review`
* 二级按钮：`退出技能模式`
* 二级按钮：`切换技能`
* 输入框上方 starter prompts

例如：

* “请按这个 skill 的步骤帮我分析这段需求”
* “判断当前问题是否适合这个 skill”
* “先给我执行计划，不要直接改代码”

这样用户会很清楚：
**我现在不是普通聊天，而是在一个“带工作流约束”的对话模式里。**

---

## 第 6 步：安装/卸载 skill 后，记得触发引擎重载

OpenWork 架构文档写得很清楚：修改 skills / plugins / MCP / config 后，可以通过 `POST /workspace/:id/engine/reload` 让 OpenCode 重新读取配置。([GitHub][3])

所以在这些动作后建议这样做：

* 安装 hub skill 成功 → `engine/reload`
* 删除 skill 成功 → `engine/reload`
* 编辑 `SKILL.md` 保存成功 → 先不一定 reload；如果你的 skill tool 是按读取文件即时生效，可以不 reload。若你发现缓存问题，再加 reload。

---

# 如果你坚持“真的改 OpenCode 代码”，我建议这样做

这是 **方案 B：深改 OpenCode 核心**。
只有在你满足下面其中一个条件时才建议走：

* 你不想依赖 OpenWork server
* 你希望未来别的客户端也能复用你的 skill store / skill mode
* 你要把“技能模式”做成 OpenCode 官方级能力

## 需要改哪些地方

### 1）OpenCode core

从仓库结构看，核心代码在：

* `packages/opencode/src/server/routes`
* `packages/opencode/src/skill`
* `packages/opencode/src/session`

这些模块现在都已经存在。([GitHub][11])

### 2）SDK

OpenCode SDK 规范文件在 `packages/sdk/openapi.json`。
如果你加新 API，记得同步改这里并重新生成 SDK。([GitHub][12])

### 3）OpenCode 自带 Web 前端

如果你要把“技能商店”直接做进 OpenCode 自带 Web UI，要改：

* `packages/app/src/pages`
* `packages/app/src/context`
* 可能还要加新组件和新路由

这个 app 是 Solid + Vite，带单测和 Playwright。([GitHub][13])

---

## 深改 OpenCode 的建议改法

### A. 新增原生 skill API

在 `packages/opencode/src/server/routes` 下新增或扩展 skill route，例如：

* `GET /skill`
* `GET /skill/:name`
* `PUT /session/:id/skill-mode`
* `DELETE /session/:id/skill-mode`

### B. skill discovery 增强

在 `packages/opencode/src/skill/discovery.ts` 增加：

* `listDetailedSkills()`
* `findSkillByName()`
* `listSkillsByRoots(roots: string[])`

### C. session 持久化 skill mode

在 `packages/opencode/src/session` 里：

* 扩展 schema
* 增加 `activeSkill` 字段
* 在 `system.ts` 或 `instruction.ts` 里把 active skill 注入 session system

### D. 更新 SDK

改 `packages/sdk/openapi.json`，然后重新生成 JS SDK。

### E. 更新 OpenCode Web UI

在 `packages/app/src/pages/home.tsx` 或新增 `pages/skills.tsx`：

* 加技能商店入口
* 支持浏览已发现的 skills
* 点击 skill 后进入 skill mode 会话

### 这个方案的缺点

维护成本更高。
因为你每次跟上游 OpenCode 升级，都要一起处理：

* 路由变更
* session schema 变更
* SDK 变更
* Web UI 变更

所以我的建议仍然是：**第一版别深改 OpenCode core。**

---

# 单元测试与集成测试怎么做

## 一、如果你走 OpenWork 方案

### server 测试

OpenWork server 现在的 package 脚本就是 `bun test`。([GitHub][14])

建议加这些测试：

1. `skills.list.test.ts`

   * 能扫到 `.opencode/skills/<name>/SKILL.md`
   * 能扫到向上目录直到 git root
   * 能扫到 global skills
   * 非法 frontmatter 被忽略
   * 同名 skill 去重

2. `skills.detail.test.ts`

   * `GET /workspace/:id/skills/:name` 返回内容
   * 不存在 skill 返回 404

3. `skill-roots.test.ts`

   * 自定义 root 能正确扫描
   * 非法路径被拒绝
   * 重复 root 不重复返回

4. `skill-mode-resolve.test.ts`

   * 返回 `systemPrompt`
   * 返回 starter prompts
   * 空 trigger 时也有默认 starter prompts

### 前端测试

OpenWork UI 当前的测试风格不是 Vitest 组件测为主，而是很多 `node scripts/*.mjs` 的集成脚本。([GitHub][15])

所以对新手最友好的方式是：

* 延续现有风格
* 新增两个脚本：

  * `scripts/skill-store.mjs`
  * `scripts/skill-mode.mjs`

建议覆盖这些场景：

1. 技能商店页能显示 skills / hubSkills
2. 点击“开始技能对话”能创建或进入会话
3. 会话页能显示 skill badge
4. 发送消息时会附带 system skill mode
5. 切换 skill 后旧 skill 不再生效
6. 退出 skill mode 后恢复普通对话

---

## 二、如果你走 OpenCode 深改方案

### OpenCode core

`packages/opencode` 当前测试脚本就是 `bun test --timeout 30000`。([GitHub][16])

建议加：

* skill discovery 单测
* `/skill` route 测试
* `/session/:id/skill-mode` route 测试
* session schema 迁移测试
* system prompt 注入测试

### OpenCode app

`packages/app` 现在同时有：

* `bun run test:unit`
* `bun run test:e2e:local`

而且 README 明说 E2E 依赖 opencode backend 默认 `localhost:4096`。([GitHub][17])

你要加的测试：

1. 技能商店页渲染
2. 进入 skill mode 后 header badge 显示
3. 新建 session 默认应用 skill mode
4. refresh 后 skill mode 仍在
5. 退出后恢复普通模式

---

# 我建议你的开发顺序

按这个顺序最不容易翻车：

1. **先做 skill 详情接口**
2. **再做 skill mode 前端状态**
3. **再做发送消息时的 `system` 注入**
4. **再做技能商店 UI 按钮和详情抽屉**
5. **最后才做自定义 skill roots 和 hub 美化**

原因是前 3 步一通，你的核心价值就已经能跑起来了：
**“点一个 skill → 进入专用对话模式”**。

---

# 最后给你一个最实用的判断

如果你的目标是 **尽快做出一个可用的“技能商店 + skill 对话模式”产品**：

* **主战场放在 OpenWork**

  * `packages/app`
  * `packages/server`

* **把 OpenCode 当后端引擎**

  * `opencode serve`
  * session / message / event / skill tool

只有等第一版跑稳了，再考虑把 skill mode 下沉到 OpenCode core 里，做成更通用的原生能力。

如果你愿意，我下一条可以直接给你一份**按文件拆分的改动清单**，把每个文件要加什么函数、什么类型、什么按钮、什么测试样例逐个写出来。

[1]: https://github.com/different-ai/openwork "https://github.com/different-ai/openwork"
[2]: https://github.com/sst/opencode "GitHub - anomalyco/opencode: The open source coding agent. · GitHub"
[3]: https://github.com/different-ai/openwork/blob/dev/ARCHITECTURE.md "https://github.com/different-ai/openwork/blob/dev/ARCHITECTURE.md"
[4]: https://opencode.ai/docs/zh-cn/server/ "https://opencode.ai/docs/zh-cn/server/"
[5]: https://github.com/different-ai/openwork/tree/dev/packages/server "https://github.com/different-ai/openwork/tree/dev/packages/server"
[6]: https://github.com/different-ai/openwork/blob/dev/packages/app/src/app/pages/skills.tsx "https://github.com/different-ai/openwork/blob/dev/packages/app/src/app/pages/skills.tsx"
[7]: https://github.com/different-ai/openwork/blob/dev/packages/server/src/skills.ts "https://github.com/different-ai/openwork/blob/dev/packages/server/src/skills.ts"
[8]: https://opencode.ai/docs/zh-cn/web/ "https://opencode.ai/docs/zh-cn/web/"
[9]: https://github.com/different-ai/openwork/blob/dev/packages/server/src/types.ts "https://github.com/different-ai/openwork/blob/dev/packages/server/src/types.ts"
[10]: https://github.com/different-ai/openwork/tree/dev/packages/app/src/app "https://github.com/different-ai/openwork/tree/dev/packages/app/src/app"
[11]: https://github.com/anomalyco/opencode/tree/dev/packages/opencode/src "opencode/packages/opencode/src at dev · anomalyco/opencode · GitHub"
[12]: https://github.com/anomalyco/opencode/tree/dev/packages/sdk "opencode/packages/sdk at dev · anomalyco/opencode · GitHub"
[13]: https://github.com/anomalyco/opencode/tree/dev/packages/app "opencode/packages/app at dev · anomalyco/opencode · GitHub"
[14]: https://github.com/different-ai/openwork/blob/dev/packages/server/package.json "https://github.com/different-ai/openwork/blob/dev/packages/server/package.json"
[15]: https://github.com/different-ai/openwork/blob/dev/packages/app/package.json "https://github.com/different-ai/openwork/blob/dev/packages/app/package.json"
[16]: https://github.com/anomalyco/opencode/blob/dev/packages/opencode/package.json "opencode/packages/opencode/package.json at dev · anomalyco/opencode · GitHub"
[17]: https://github.com/anomalyco/opencode/blob/dev/packages/app/package.json "opencode/packages/app/package.json at dev · anomalyco/opencode · GitHub"
