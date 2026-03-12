下面这版按**当前 OpenCode dev 分支的结构**来写，尽量做到“你照着文件一个个改，就能做出第一版”。我会把方案定成：**保留 OpenCode 原生 skill 发现与 session API，只额外加一个 `skill-store` 层**。这样最稳，因为当前服务端源码已经有 `GET /skill`，`Skill.Info` 里也已经带了 `name / description / location / content`；会话 API 也已经有 `POST /session`、`POST /session/:id/message`，并支持 `noReply` 注入上下文。另一个关键点是：当前 `opencode web` 的 catch-all 仍然会把未知路径代理到 `https://app.opencode.ai`，所以如果你要“改官方自带 WebUI”，只改 `packages/app` 还不够，还要一起改 `packages/opencode/src/server/server.ts` 的最后那段 fallback。([GitHub][1])

还有一个设计前提：我建议把商店 UI 元数据放在单独的 `store.json`，不要硬塞进 `SKILL.md` frontmatter。因为官方技能文档明确写了 frontmatter 只识别 `name`、`description`、`license`、`compatibility`、`metadata`，未知字段会被忽略。这样你既不破坏 OpenCode 原生 skill 规范，又能给商店页面单独做分类、标签、示例提问、封面图之类的 UI 元数据。([OpenCode][2])

---

## 一、建议你最终改成的文件结构

### 后端

```text
packages/opencode/src/skill/store.ts                 // 新增：技能商店层
packages/opencode/src/server/routes/skill-store.ts   // 新增：商店 API
packages/opencode/src/server/server.ts               // 修改：挂载 skill-store 路由；可选替换 web fallback
```

### 前端

```text
packages/app/src/lib/skill-store.ts                  // 新增：前端 API 封装
packages/app/src/pages/skills/index.tsx              // 新增：技能商店列表页
packages/app/src/pages/skills/detail.tsx             // 新增：技能详情页
packages/app/src/components/skill-card.tsx           // 新增：技能卡片
packages/app/src/components/skill-filter-bar.tsx     // 新增：搜索/筛选
packages/app/src/components/skill-mode-header.tsx    // 新增：聊天页顶部技能条
packages/app/src/app.tsx                             // 修改：新增 skills 路由
packages/app/src/pages/home.tsx                      // 修改：给最近项目增加“打开技能商店”
packages/app/src/pages/session.tsx                   // 修改：显示 skill mode header
```

### 测试

```text
packages/opencode/src/server/routes/skill-store.test.ts
packages/app/src/lib/skill-store.test.ts
packages/app/src/pages/skills/index.test.tsx
packages/app/e2e/skill-store.spec.ts
```

当前前端已经有 `pages/home.tsx`、`pages/session.tsx`，首页也确实在展示最近项目并通过 `openProject()` 跳目录；聊天页已经在用 `SessionHeader` / `NewSessionView` 这一套组件，所以把“技能商店”加成新的同级页面、把“技能模式头部”塞进 session 页，是比较顺着现有 UI 结构的改法。`packages/app` 也已经自带 Bun 单测和 Playwright E2E 脚本。([GitHub][3])

---

## 二、skill 目录里新增的 `store.json`

每个技能目录建议长这样：

```text
pr-review/
  SKILL.md
  store.json
  cover.png
```

`store.json` 示例：

```json
{
  "displayName": "PR Review",
  "category": "code-review",
  "tags": ["review", "git", "pr"],
  "icon": "shield-check",
  "cover": "cover.png",
  "starterPrompts": [
    "帮我审查当前改动",
    "总结这个 PR 的风险点",
    "按高/中/低风险列出问题"
  ],
  "entryPrompt": "进入 PR Review 技能模式后，请优先按审查、归类、给建议修复步骤的顺序回答。",
  "recommendedAgent": "plan",
  "hidden": false
}
```

这里的思路是：

* `SKILL.md` 继续给 OpenCode 的原生技能系统用。
* `store.json` 只给你的商店 UI 用。
* `hidden` 可以让你先把某些技能藏起来，不在商店展示。
* `starterPrompts` 给详情页做快捷问题按钮。

---

## 三、后端第一部分：`packages/opencode/src/skill/store.ts`

这个文件的职责只有 4 个：

1. 复用 `Skill.all()` 拿到已发现的技能。
2. 从 `location` 同目录里读取 `store.json`。
3. 组装出“适合商店页显示”的 catalog。
4. 提供一个 `buildBootstrapPrompt()`，让 `start-session` 能把 skill mode 注入到会话里。

当前 `Skill.Info` 已经包含 `location` 和 `content`，而当前技能加载器除了标准 `.opencode/skills`、`.claude/skills`、`.agents/skills` 这些目录外，dev 源码里还会额外扫描 `config.skills?.paths` 与 `config.skills?.urls`。所以你做商店层时，不需要再重写一次技能发现，直接站在 `Skill.all()` 上做二次加工最省事。([GitHub][4])

### 伪代码骨架

```ts
// packages/opencode/src/skill/store.ts
import z from "zod"
import path from "path"
import os from "os"
import { Skill } from "./skill"
import { Config } from "../config/config"
import { Filesystem } from "@/util/filesystem"
import { PermissionNext } from "@/permission/next"

export namespace SkillStore {
  export const Meta = z.object({
    displayName: z.string().min(1).optional(),
    category: z.string().default("uncategorized"),
    tags: z.array(z.string()).default([]),
    icon: z.string().optional(),
    cover: z.string().optional(),
    starterPrompts: z.array(z.string()).default([]),
    entryPrompt: z.string().optional(),
    recommendedAgent: z.string().optional(),
    hidden: z.boolean().default(false),
  }).passthrough()

  export type Meta = z.infer<typeof Meta>

  export const CatalogItem = z.object({
    name: z.string(),
    description: z.string(),
    displayName: z.string(),
    category: z.string(),
    tags: z.array(z.string()),
    icon: z.string().optional(),
    cover: z.string().optional(),
    starterPrompts: z.array(z.string()),
    recommendedAgent: z.string().optional(),

    permissionState: z.enum(["allow", "ask", "deny"]),
    canStart: z.boolean(),

    // 不建议把真实绝对路径直接回给前端
    hasDetail: z.boolean(),
  })

  export type CatalogItem = z.infer<typeof CatalogItem>

  async function loadStoreMeta(skill: Skill.Info): Promise<Meta> {
    const dir = path.dirname(skill.location)
    const file = path.join(dir, "store.json")

    if (!(await Filesystem.exists(file))) {
      return Meta.parse({})
    }

    try {
      const raw = await Bun.file(file).text()
      return Meta.parse(JSON.parse(raw))
    } catch (err) {
      // 不要让一个坏的 store.json 把整个商店打挂
      console.warn("[skill-store] invalid store.json", skill.name, err)
      return Meta.parse({})
    }
  }

  async function getStoreRoots(): Promise<string[]> {
    const config = await Config.get()
    return (config.skills?.paths ?? []).map((p) => {
      const expanded = p.startsWith("~/") ? path.join(os.homedir(), p.slice(2)) : p
      return path.resolve(expanded)
    })
  }

  function isUnderRoots(file: string, roots: string[]) {
    if (roots.length === 0) return true
    const resolved = path.resolve(file)
    return roots.some((root) => resolved.startsWith(root + path.sep) || resolved === root)
  }

  function permissionStateOf(skillName: string, agent?: { permission?: unknown }) {
    if (!agent) return "allow"
    return PermissionNext.evaluate("skill", skillName, agent.permission).action
  }

  export async function catalog(opts?: {
    q?: string
    agent?: { permission?: unknown }
    scope?: "store" | "all"
  }): Promise<CatalogItem[]> {
    const skills = await Skill.all()
    const roots = opts?.scope === "all" ? [] : await getStoreRoots()

    const rows = await Promise.all(
      skills.map(async (skill) => {
        if (!isUnderRoots(skill.location, roots)) return null

        const meta = await loadStoreMeta(skill)
        if (meta.hidden) return null

        const permissionState = permissionStateOf(skill.name, opts?.agent)

        const item: CatalogItem = {
          name: skill.name,
          description: skill.description,
          displayName: meta.displayName ?? skill.name,
          category: meta.category,
          tags: meta.tags,
          icon: meta.icon,
          cover: meta.cover,
          starterPrompts: meta.starterPrompts,
          recommendedAgent: meta.recommendedAgent,
          permissionState,
          canStart: permissionState !== "deny",
          hasDetail: true,
        }

        if (!opts?.q) return item

        const text = [
          item.name,
          item.displayName,
          item.description,
          item.category,
          ...item.tags,
        ].join(" ").toLowerCase()

        return text.includes(opts.q.toLowerCase()) ? item : null
      }),
    )

    return rows.filter(Boolean) as CatalogItem[]
  }

  export async function detail(name: string, agent?: { permission?: unknown }) {
    const skill = await Skill.get(name)
    if (!skill) return null

    const meta = await loadStoreMeta(skill)
    const permissionState = permissionStateOf(skill.name, agent)

    return {
      ...CatalogItem.parse({
        name: skill.name,
        description: skill.description,
        displayName: meta.displayName ?? skill.name,
        category: meta.category,
        tags: meta.tags,
        icon: meta.icon,
        cover: meta.cover,
        starterPrompts: meta.starterPrompts,
        recommendedAgent: meta.recommendedAgent,
        permissionState,
        canStart: permissionState !== "deny",
        hasDetail: true,
      }),
      entryPrompt: meta.entryPrompt,
      content: skill.content, // 详情页可选显示原文
    }
  }

  export function buildBootstrapPrompt(input: {
    name: string
    displayName: string
    description: string
    content: string
    entryPrompt?: string
  }) {
    return [
      "你现在处于专用技能模式。",
      `当前技能: ${input.displayName} (${input.name})`,
      `技能说明: ${input.description}`,
      "",
      "请把下面的技能内容视为当前会话的优先工作流。",
      "若用户后续要求与技能流程冲突，请先说明冲突点，再按用户明确意图继续。",
      "",
      input.entryPrompt ? `额外入口要求: ${input.entryPrompt}` : "",
      "",
      "===== SKILL CONTENT BEGIN =====",
      input.content,
      "===== SKILL CONTENT END =====",
    ].filter(Boolean).join("\n")
  }
}
```

### 这个文件为什么这样拆

这样拆的好处是：

* `Skill.all()` 还是原汁原味，不影响官方原生 skill 流程。
* 商店层只负责“展示”和“专用模式启动”。
* 后面你要加 `rating`、`author`、`version`、`examples`，都改 `store.json` 和 `SkillStore.Meta` 就行。

---

## 四、后端第二部分：`packages/opencode/src/server/routes/skill-store.ts`

这个路由文件建议做 3 个接口就够了：

* `GET /skill-store`：商店列表
* `GET /skill-store/:name`：技能详情
* `POST /skill-store/:name/start-session`：一键进入技能模式对话

我建议你**不要**让前端自己串联“先建 session，再注入上下文，再发首条消息”。这一步合成成一个后端接口，前端会简单很多，也不容易出现中间一步成功、中间一步失败的半残状态。当前服务器 API 本来就已经提供了 `POST /session` 建会话，以及 `POST /session/:id/message` + `noReply` 注入上下文。([OpenCode][5])

### 伪代码骨架

```ts
// packages/opencode/src/server/routes/skill-store.ts
import { Hono } from "hono"
import z from "zod"
import { describeRoute, resolver, validator } from "hono-openapi"
import { SkillStore } from "@/skill/store"
import { Session } from "@/session"
import { Agent } from "@/agent/agent"
// 这里的 Session / Agent 函数名按现有 namespace 风格写
// 是伪代码骨架，不保证与你本地分支 1:1

const StartBody = z.object({
  agent: z.string().optional(),
  model: z.string().optional(),
  initialUserMessage: z.string().optional(),
  confirmAsk: z.boolean().default(false),
  title: z.string().optional(),
})

export function SkillStoreRoutes() {
  const app = new Hono()

  app.get(
    "/",
    describeRoute({
      summary: "List skill store catalog",
      operationId: "skillStore.list",
      responses: {
        200: {
          description: "Catalog items",
          content: {
            "application/json": {
              schema: resolver(SkillStore.CatalogItem.array()),
            },
          },
        },
      },
    }),
    validator("query", z.object({
      q: z.string().optional(),
      agent: z.string().optional(),
      scope: z.enum(["store", "all"]).optional(),
    })),
    async (c) => {
      const { q, agent: agentName, scope } = c.req.valid("query")
      const agent = agentName ? await Agent.get(agentName) : undefined
      const list = await SkillStore.catalog({ q, agent, scope })
      return c.json(list)
    },
  )

  app.get(
    "/:name",
    describeRoute({
      summary: "Get skill store detail",
      operationId: "skillStore.detail",
      responses: {
        200: { description: "Skill detail" },
        404: { description: "Skill not found" },
      },
    }),
    validator("param", z.object({ name: z.string() })),
    validator("query", z.object({ agent: z.string().optional() })),
    async (c) => {
      const { name } = c.req.valid("param")
      const { agent: agentName } = c.req.valid("query")
      const agent = agentName ? await Agent.get(agentName) : undefined

      const detail = await SkillStore.detail(name, agent)
      if (!detail) return c.json({ message: "skill not found" }, 404)
      return c.json(detail)
    },
  )

  app.post(
    "/:name/start-session",
    describeRoute({
      summary: "Create a new session in skill mode",
      operationId: "skillStore.startSession",
      responses: {
        200: { description: "Session created" },
        403: { description: "Skill denied" },
        404: { description: "Skill not found" },
        409: { description: "Need confirmation" },
      },
    }),
    validator("param", z.object({ name: z.string() })),
    validator("json", StartBody),
    async (c) => {
      const { name } = c.req.valid("param")
      const body = c.req.valid("json")

      const agent = body.agent ? await Agent.get(body.agent) : undefined
      const detail = await SkillStore.detail(name, agent)

      if (!detail) {
        return c.json({ message: "skill not found" }, 404)
      }

      if (detail.permissionState === "deny") {
        return c.json({ message: "skill denied" }, 403)
      }

      if (detail.permissionState === "ask" && !body.confirmAsk) {
        return c.json({
          message: "need confirmation",
          requiresConfirmation: true,
        }, 409)
      }

      const title =
        body.title ??
        `[${detail.displayName}] ${detail.description}`.slice(0, 80)

      // 1) 创建 session
      const session = await Session.create({
        title,
      })

      // 2) 注入 skill mode bootstrap，不触发回复
      const bootstrap = SkillStore.buildBootstrapPrompt({
        name: detail.name,
        displayName: detail.displayName,
        description: detail.description,
        content: detail.content,
        entryPrompt: detail.entryPrompt,
      })

      await Session.prompt(session.id, {
        agent: body.agent ?? detail.recommendedAgent,
        model: body.model,
        noReply: true,
        parts: [
          {
            type: "text",
            text: bootstrap,
          },
        ],
      })

      // 3) 如果详情页点的是“示例问题”，可顺手再发第一条用户消息
      let firstResponse = null
      if (body.initialUserMessage?.trim()) {
        firstResponse = await Session.prompt(session.id, {
          agent: body.agent ?? detail.recommendedAgent,
          model: body.model,
          parts: [
            {
              type: "text",
              text: body.initialUserMessage.trim(),
            },
          ],
        })
      }

      return c.json({
        sessionID: session.id,
        title: session.title,
        skill: {
          name: detail.name,
          displayName: detail.displayName,
          description: detail.description,
          category: detail.category,
          tags: detail.tags,
          starterPrompts: detail.starterPrompts,
        },
        firstResponse,
      })
    },
  )

  return app
}
```

### 这里最值得注意的 3 个点

第一，`ask / allow / deny` 最好在这里统一处理。官方权限模型对 skill 就是这三种行为；`ask` 很适合映射成“用户点击按钮后二次确认一次”。([OpenCode][2])

第二，**建议每次加载技能都新建一个 session**，不要把 skill mode 直接塞进用户正在聊的旧会话。这样上下文最干净，技能边界也清晰。

第三，退出 skill mode 时，最好不是“只是把 badge 隐藏掉”，而是**fork 一个不带技能标识的新 session**。因为 skill bootstrap 已经进入会话历史了，单纯隐藏 UI 并不会真的让模型忘掉它。官方会话 API 本身就有 `POST /session/:id/fork`。([OpenCode][5])

---

## 五、后端第三部分：改 `packages/opencode/src/server/server.ts`

### 1）先挂载新路由

当前 `server.ts` 已经在用 Hono + `describeRoute`/`validator` 的风格挂 `project`、`session`、`provider` 等路由，也已经直接暴露了 `GET /skill`。所以你的新路由完全可以照这个风格加进去。([GitHub][1])

伪代码：

```ts
// server.ts
import { SkillStoreRoutes } from "./routes/skill-store"

export const createApp = (opts: { cors?: string[] }): Hono => {
  const app = new Hono()

  return app
    // ...已有中间件
    .route("/project", ProjectRoutes())
    .route("/session", SessionRoutes())
    .route("/skill-store", SkillStoreRoutes())   // <-- 新增
    // ...已有其他路由
}
```

### 2）如果你要深改 `opencode web`，必须改最后的 fallback

当前源码最后是：

* 对所有未命中的路径 `.all("/*")`
* `proxy("https://app.opencode.ai${path}")`

这意味着你只改前端源码，`opencode web` 也不一定会直接打开你的本地改版 UI。([GitHub][1])

你可以先做一个最简单的开发版：

```ts
// server.ts 最后那段 catch-all，伪代码
.all("/*", async (c) => {
  const devUI = process.env.OPENCODE_WEB_APP_URL

  if (devUI) {
    // 开发模式：代理到你自己的 Vite dev server
    return proxy(`${devUI}${c.req.path}`, {
      ...c.req,
      headers: {
        ...c.req.raw.headers,
      },
    })
  }

  // 生产模式：返回你打包好的 dist/index.html
  const distDir = "/absolute/path/to/packages/app/dist"
  const reqPath = c.req.path === "/" ? "/index.html" : c.req.path
  const filePath = path.join(distDir, reqPath)

  if (await Filesystem.exists(filePath)) {
    return c.body(await Bun.file(filePath).arrayBuffer())
  }

  return c.html(await Bun.file(path.join(distDir, "index.html")).text())
})
```

如果你暂时不想改这一段，另一条更轻的路是：先跑 `opencode serve --cors ...`，自己单独起一个前端。官方 web/server 文档都明确支持给浏览器客户端配 CORS，自定义前端是被支持的。([OpenCode][6])

---

## 六、前端 API 层：`packages/app/src/lib/skill-store.ts`

一个很实用的小建议：**你自己的 `skill-store` 接口先别强依赖 SDK codegen**，直接做一个薄薄的 `fetch` 封装。因为当前 SDK 文档里 `App` 下面列的是 `app.log()` 和 `app.agents()`，但当前服务端源码实际上已经有 `GET /skill`。也就是说，文档层和源码层在这里存在轻微不同步，你自己新增的 `/skill-store` 更没必要等 SDK 再生成一轮。([OpenCode][7])

### 伪代码骨架

```ts
// packages/app/src/lib/skill-store.ts
export type SkillCatalogItem = {
  name: string
  description: string
  displayName: string
  category: string
  tags: string[]
  icon?: string
  cover?: string
  starterPrompts: string[]
  recommendedAgent?: string
  permissionState: "allow" | "ask" | "deny"
  canStart: boolean
  hasDetail: boolean
}

export type SkillDetail = SkillCatalogItem & {
  entryPrompt?: string
  content: string
}

function withDirectory(url: string, directory?: string) {
  const u = new URL(url, window.location.origin)
  if (directory) u.searchParams.set("directory", directory)
  return u.toString()
}

export async function listSkillStore(input: {
  directory?: string
  q?: string
  agent?: string
  scope?: "store" | "all"
}) {
  const url = new URL("/skill-store", window.location.origin)
  if (input.q) url.searchParams.set("q", input.q)
  if (input.agent) url.searchParams.set("agent", input.agent)
  if (input.scope) url.searchParams.set("scope", input.scope)
  if (input.directory) url.searchParams.set("directory", input.directory)

  const res = await fetch(url)
  if (!res.ok) throw new Error("failed to list skill store")
  return (await res.json()) as SkillCatalogItem[]
}

export async function getSkillDetail(name: string, input: {
  directory?: string
  agent?: string
}) {
  const url = new URL(`/skill-store/${encodeURIComponent(name)}`, window.location.origin)
  if (input.agent) url.searchParams.set("agent", input.agent)
  if (input.directory) url.searchParams.set("directory", input.directory)

  const res = await fetch(url)
  if (!res.ok) throw new Error("failed to get skill detail")
  return (await res.json()) as SkillDetail
}

export async function startSkillSession(name: string, body: {
  directory?: string
  agent?: string
  model?: string
  initialUserMessage?: string
  confirmAsk?: boolean
  title?: string
}) {
  const url = new URL(`/skill-store/${encodeURIComponent(name)}/start-session`, window.location.origin)
  if (body.directory) url.searchParams.set("directory", body.directory)

  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  })

  if (res.status === 409) {
    return {
      requiresConfirmation: true,
      ...(await res.json()),
    }
  }

  if (!res.ok) throw new Error("failed to start skill session")
  return await res.json()
}
```

---

## 七、前端页面：技能商店列表页 `packages/app/src/pages/skills/index.tsx`

这个页面主要做 4 件事：

1. 拉列表
2. 搜索
3. 分类/标签筛选
4. 点卡片跳详情

### 伪代码骨架

```tsx
// packages/app/src/pages/skills/index.tsx
import { createMemo, createResource, createSignal, For, Show } from "solid-js"
import { useNavigate, useParams } from "@solidjs/router"
import { listSkillStore } from "@/lib/skill-store"
import { SkillCard } from "@/components/skill-card"
import { SkillFilterBar } from "@/components/skill-filter-bar"

export default function SkillsIndexPage() {
  const params = useParams()
  const navigate = useNavigate()

  const directory = createMemo(() => {
    // 这里用你项目里现有的目录解码工具
    // 例如 base64Decode(params.dir)
    return decodeDir(params.dir)
  })

  const [q, setQ] = createSignal("")
  const [catalog] = createResource(
    () => ({ directory: directory(), q: q(), scope: "store" as const }),
    listSkillStore,
  )

  return (
    <div class="flex flex-col gap-4 p-4">
      <h1 class="text-xl font-semibold">技能商店</h1>

      <SkillFilterBar
        value={q()}
        onInput={setQ}
      />

      <Show when={!catalog.loading} fallback={<div>加载中…</div>}>
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <For each={catalog() ?? []}>
            {(skill) => (
              <SkillCard
                skill={skill}
                onOpen={() => navigate(`/${params.dir}/skills/${skill.name}`)}
              />
            )}
          </For>
        </div>
      </Show>
    </div>
  )
}
```

---

## 八、前端页面：技能详情页 `packages/app/src/pages/skills/detail.tsx`

详情页要重点支持两个动作：

* `立即对话`
* 点一个 starter prompt 直接“创建 session + 发首问”

### 伪代码骨架

```tsx
// packages/app/src/pages/skills/detail.tsx
import { createMemo, createResource, For } from "solid-js"
import { useNavigate, useParams } from "@solidjs/router"
import { getSkillDetail, startSkillSession } from "@/lib/skill-store"

export default function SkillDetailPage() {
  const params = useParams()
  const navigate = useNavigate()

  const directory = createMemo(() => decodeDir(params.dir))
  const skillName = createMemo(() => params.name)

  const [detail] = createResource(
    () => ({ name: skillName(), directory: directory() }),
    ({ name, directory }) => getSkillDetail(name, { directory }),
  )

  async function handleStart(initialUserMessage?: string) {
    const result = await startSkillSession(skillName(), {
      directory: directory(),
      agent: detail()?.recommendedAgent,
      initialUserMessage,
      confirmAsk: true,
    })

    if ("requiresConfirmation" in result && result.requiresConfirmation) {
      const ok = window.confirm("这个技能当前需要确认后才能加载，继续吗？")
      if (!ok) return

      const secondTry = await startSkillSession(skillName(), {
        directory: directory(),
        agent: detail()?.recommendedAgent,
        initialUserMessage,
        confirmAsk: true,
      })

      navigate(`/${params.dir}/session/${secondTry.sessionID}?skill=${skillName()}`)
      return
    }

    navigate(`/${params.dir}/session/${result.sessionID}?skill=${skillName()}`)
  }

  return (
    <div class="flex flex-col gap-4 p-4">
      <h1 class="text-xl font-semibold">{detail()?.displayName}</h1>
      <p class="text-sm opacity-80">{detail()?.description}</p>

      <div class="flex gap-2">
        <button onClick={() => handleStart()}>立即对话</button>
      </div>

      <div class="flex flex-wrap gap-2">
        <For each={detail()?.starterPrompts ?? []}>
          {(prompt) => (
            <button onClick={() => handleStart(prompt)}>
              {prompt}
            </button>
          )}
        </For>
      </div>

      <details>
        <summary>查看技能原文</summary>
        <pre class="whitespace-pre-wrap">{detail()?.content}</pre>
      </details>
    </div>
  )
}
```

---

## 九、前端组件：技能卡片 `packages/app/src/components/skill-card.tsx`

```tsx
// packages/app/src/components/skill-card.tsx
import type { SkillCatalogItem } from "@/lib/skill-store"

export function SkillCard(props: {
  skill: SkillCatalogItem
  onOpen: () => void
}) {
  return (
    <button
      class="rounded-xl border p-4 text-left hover:bg-bg-secondary"
      onClick={props.onOpen}
    >
      <div class="flex items-center justify-between gap-2">
        <div class="font-medium">{props.skill.displayName}</div>
        <div class="text-xs opacity-70">{props.skill.permissionState}</div>
      </div>

      <div class="mt-2 text-sm opacity-80">
        {props.skill.description}
      </div>

      <div class="mt-3 flex flex-wrap gap-2">
        <span class="text-xs rounded px-2 py-1 bg-bg-tertiary">
          {props.skill.category}
        </span>

        {props.skill.tags.map((tag) => (
          <span class="text-xs rounded px-2 py-1 bg-bg-tertiary">
            {tag}
          </span>
        ))}
      </div>
    </button>
  )
}
```

---

## 十、前端组件：聊天页顶部技能条 `packages/app/src/components/skill-mode-header.tsx`

这个组件建议最小先做成：

* 显示当前 skill
* 显示“退出技能模式”
* 退出时最好 fork 新会话

因为上面说过，skill bootstrap 已经写进历史消息了，直接隐藏 badge 不是“真正退出”。官方 session API 有 fork，正好适合这里。([OpenCode][5])

### 伪代码骨架

```tsx
// packages/app/src/components/skill-mode-header.tsx
export function SkillModeHeader(props: {
  skillName: string
  skillDisplayName?: string
  onExit: () => void
}) {
  return (
    <div class="mb-3 flex items-center justify-between rounded-lg border px-3 py-2">
      <div class="flex items-center gap-2">
        <span class="text-xs rounded bg-bg-tertiary px-2 py-1">技能模式</span>
        <span class="text-sm font-medium">
          {props.skillDisplayName ?? props.skillName}
        </span>
      </div>

      <button class="text-sm opacity-80 hover:opacity-100" onClick={props.onExit}>
        退出技能模式
      </button>
    </div>
  )
}
```

---

## 十一、改 `packages/app/src/pages/session.tsx`

当前 session 页面已经在用 `useParams`、`useSearchParams`、`SessionHeader` 等，所以很适合直接从 query string 读一个 `?skill=pr-review`，然后在 `SessionHeader` 下方插一个 `SkillModeHeader`。([GitHub][8])

### 伪代码骨架

```tsx
// session.tsx 里新增的核心逻辑
import { SkillModeHeader } from "@/components/skill-mode-header"

export default function SessionPage() {
  const params = useParams()
  const navigate = useNavigate()
  const [search] = useSearchParams()
  const sdk = useSDK()

  const skillName = createMemo(() => search.skill)

  async function exitSkillMode() {
    const sessionID = params.id
    if (!sessionID) return

    // 真退出：fork 一个新会话，然后不带 ?skill= 跳转
    const next = await sdk.client.session.fork({
      path: { id: sessionID },
      body: {},
    })

    navigate(`/${params.dir}/session/${next.data.id}`)
  }

  return (
    <div>
      <SessionHeader />

      <Show when={skillName()}>
        <SkillModeHeader
          skillName={skillName()!}
          onExit={exitSkillMode}
        />
      </Show>

      {/* 原来的 MessageTimeline / Composer / Review 面板继续保留 */}
    </div>
  )
}
```

---

## 十二、改 `packages/app/src/pages/home.tsx`

当前首页已经有最近项目和 `openProject(project.worktree)` 逻辑，所以最省事的做法不是单独做“全局技能商店”，而是在最近项目卡片上加第二个按钮：`打开技能商店`。这样用户先选项目，再选 skill，路径上下文最清晰。([GitHub][3])

### 伪代码骨架

```tsx
// home.tsx 最近项目列表里，每个项目多一个按钮
<For each={recent()}>
  {(project) => (
    <div class="rounded-lg border p-3">
      <button onClick={() => openProject(project.worktree)}>
        {project.worktree.replace(homedir(), "~")}
      </button>

      <div class="mt-2 flex gap-2">
        <Button onClick={() => openProject(project.worktree)}>
          打开项目
        </Button>

        <Button
          variant="secondary"
          onClick={() => navigate(`/${base64Encode(project.worktree)}/skills`)}
        >
          打开技能商店
        </Button>
      </div>
    </div>
  )}
</For>
```

---

## 十三、改 `packages/app/src/app.tsx`

当前 app 入口已经 lazy load 了 `pages/home` 和 `pages/session`，并把页面挂在现有路由壳子里。你新增 `skills/index` 和 `skills/detail` 即可。([GitHub][9])

### 伪代码骨架

```tsx
// app.tsx
const SkillsIndex = lazy(() => import("@/pages/skills/index"))
const SkillDetail = lazy(() => import("@/pages/skills/detail"))

/*
<Route path="/:dir" component={DirectoryLayout}>
  <Route path="/" component={SessionIndexRoute} />
  <Route path="/session/:id?" component={SessionRoute} />
  <Route path="/skills" component={SkillsIndex} />
  <Route path="/skills/:name" component={SkillDetail} />
</Route>
*/
```

---

## 十四、单元测试怎么写

### 1）后端：`packages/opencode/src/server/routes/skill-store.test.ts`

先做 4 条最关键的：

#### 用例 A：能列出 catalog

* 建一个临时目录
* 写入：

  * `tmp/store/pr-review/SKILL.md`
  * `tmp/store/pr-review/store.json`
* 配置 `skills.paths = [tmp/store]`
* 发 `GET /skill-store`
* 断言：

  * 返回长度为 1
  * `name === "pr-review"`
  * `category === "code-review"`

#### 用例 B：坏掉的 `store.json` 不会把整个接口打挂

* 写一个非法 JSON
* 发 `GET /skill-store`
* 断言仍然 200
* `displayName` 回退为 `skill.name`

#### 用例 C：`deny` 时不允许 start-session

* agent permission 里把该 skill 设为 `deny`
* `POST /skill-store/pr-review/start-session`
* 断言 403

#### 用例 D：可以创建 session 并注入 bootstrap

* `POST /skill-store/pr-review/start-session`
* 断言返回 `sessionID`
* 再读 session message，确认第一条隐藏上下文已经写入

### 测试骨架示意

```ts
describe("skill-store routes", () => {
  test("list catalog", async () => {
    // 1. 建 temp dir
    // 2. 写 skill fixture
    // 3. 启 server app
    // 4. GET /skill-store
    // 5. expect(...)
  })

  test("invalid store.json falls back safely", async () => {
    // expect 200 + fallback fields
  })

  test("deny permission blocks start-session", async () => {
    // expect 403
  })

  test("start-session creates session and injects bootstrap", async () => {
    // expect sessionID
    // then read session messages
  })
})
```

---

## 十五、前端单测怎么写

`packages/app` 目前已经有 Bun + happydom 单测脚本，以及 Playwright E2E 脚本，所以你直接沿用即可。([GitHub][10])

### `packages/app/src/lib/skill-store.test.ts`

测 API wrapper：

* `listSkillStore()` 是否会把 `q` / `directory` 拼进 URL
* `startSkillSession()` 遇到 409 是否能返回 `requiresConfirmation`

### `packages/app/src/pages/skills/index.test.tsx`

测商店页：

* mock `fetch`
* 渲染后能看到 skill 卡片
* 输入搜索词后只剩匹配项
* 点击卡片会跳详情

### `packages/app/src/pages/skills/detail.test.tsx`

测详情页：

* 能渲染 starter prompts
* 点“立即对话”会调 `startSkillSession`
* 点示例 prompt 时 `initialUserMessage` 会带过去

---

## 十六、E2E 怎么写

`packages/app/e2e/skill-store.spec.ts`

推荐只先做一条最完整的 happy path：

1. 打开某个 fixture 项目
2. 进入 `/:dir/skills`
3. 看到 `PR Review`
4. 点进去详情页
5. 点“帮我审查当前改动”
6. 跳到 `/:dir/session/:id?skill=pr-review`
7. 页面出现 `技能模式` 条
8. 点“退出技能模式”
9. 发生 fork 并跳到新 session

### E2E 骨架

```ts
test("open skill store and start skill session", async ({ page }) => {
  await page.goto("/<encoded-dir>/skills")

  await expect(page.getByText("PR Review")).toBeVisible()
  await page.getByText("PR Review").click()

  await page.getByText("帮我审查当前改动").click()

  await expect(page.getByText("技能模式")).toBeVisible()
  await expect(page.getByText("PR Review")).toBeVisible()

  await page.getByText("退出技能模式").click()
  await expect(page.getByText("技能模式")).not.toBeVisible()
})
```

---

## 十七、实际开发顺序

我建议你按这个顺序做，最不容易乱：

1. 先手工建一个最小 skill fixture
   先别一上来接真实仓库，先让 `/tmp/opencode-skill-store/pr-review` 跑通。

2. 先写 `store.ts`
   先保证：

   * 读得到 `Skill.all()`
   * 读得到旁边的 `store.json`
   * 能返回 catalog

3. 再写 `skill-store.ts` 路由
   先只做 `GET /skill-store` 和 `GET /skill-store/:name`，浏览器里能看见列表/详情。

4. 再做 `start-session`
   跑通“创建 session + 注入 bootstrap + 可选首问”。

5. 再改前端列表页和详情页
   先把页面通了，不急着做漂亮。

6. 最后改 session 页的 skill badge 和退出逻辑。

7. 最后再决定要不要替换 `opencode web` 的 fallback
   如果你只是本地开发，先 `opencode serve --cors http://localhost:5173` 跑自定义前端更轻。官方文档明确支持这一模式。([OpenCode][6])

---

## 十八、你现在最容易踩的 4 个坑

第一，**只改 `packages/app`，结果 `opencode web` 还是打开官方托管前端**。这是因为当前 catch-all 还在代理 `app.opencode.ai`。([GitHub][1])

第二，**把 `store.json` 字段全塞进 `SKILL.md` frontmatter**。这样 UI 元数据不稳定，也和官方识别字段不一致。([OpenCode][2])

第三，**在旧会话里直接切 skill mode**。这样会话上下文很容易混。初版最好“一个 skill = 一个新 session”。

第四，**退出 skill mode 只是隐藏 UI**。模型上下文没清掉；更合理的是 fork 新会话。([OpenCode][5])

---

## 十九、最后给你一个可直接照抄的运行方式

### 本地前后端分离开发

```bash
# 后端
OPENCODE_SERVER_PASSWORD=secret \
opencode serve --hostname 0.0.0.0 --port 4096 --cors http://localhost:5173

# 前端
cd packages/app
bun install
bun run dev
```

### 运行测试

```bash
cd packages/app
bun run test:unit
bun run test:e2e:local
```

这些脚本是当前 `packages/app/package.json` 里已经有的。([GitHub][10])

如果你愿意，我下一条可以继续给你一份**“更像真实 patch 的版本”**：我直接按这几个文件分别写出更接近可复制的 TypeScript 代码。

[1]: https://raw.githubusercontent.com/anomalyco/opencode/dev/packages/opencode/src/server/server.ts "raw.githubusercontent.com"
[2]: https://opencode.ai/docs/zh-cn/skills/ "代理技能 | OpenCode"
[3]: https://raw.githubusercontent.com/anomalyco/opencode/dev/packages/app/src/pages/home.tsx "raw.githubusercontent.com"
[4]: https://raw.githubusercontent.com/anomalyco/opencode/dev/packages/opencode/src/skill/skill.ts "raw.githubusercontent.com"
[5]: https://opencode.ai/docs/zh-cn/server/ "服务器 | OpenCode"
[6]: https://opencode.ai/docs/zh-cn/web/ "Web | OpenCode"
[7]: https://opencode.ai/docs/zh-cn/sdk/ "SDK | OpenCode"
[8]: https://raw.githubusercontent.com/anomalyco/opencode/dev/packages/app/src/pages/session.tsx "raw.githubusercontent.com"
[9]: https://raw.githubusercontent.com/anomalyco/opencode/dev/packages/app/src/app.tsx "raw.githubusercontent.com"
[10]: https://raw.githubusercontent.com/anomalyco/opencode/dev/packages/app/package.json "raw.githubusercontent.com"
