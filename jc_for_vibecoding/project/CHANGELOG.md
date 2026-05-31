# Changelog — 实时语音翻译字幕优化

## 动机总览

原始项目是单阶段流水线：`音频 → VAD → SeamlessM4T → 推字幕`。每个语音段被独立翻译，没有上下文，没有修正机制，也无视觉反馈。

优化目标：面向**开会实时转录翻译**场景，引入上下文感知的两级翻译流水线，并重新设计前端以支持流式打字机效果和回溯修正显示。

---

## 一、修复：缺失的配置项（Bugfix）

### `config.py`

**变更**：新增 `VAD_THRESHOLD`、`SILENCE_TIMEOUT_MS`。

**动机**：`app.py:44` 引用了 `config.VAD_THRESHOLD`，`audio/stream_buffer.py:18` 引用了 `config.SILENCE_TIMEOUT_MS`，但这两个属性在 `Config` 类中均未定义，运行时必报 `AttributeError`。

| 新增属性 | 默认值 | 作用 |
|----------|--------|------|
| `VAD_THRESHOLD` | `0.5` | Silero VAD 语音检测阈值 (0-1) |
| `SILENCE_TIMEOUT_MS` | `500` | 静音多少毫秒后判定一个语音段结束 |

---

## 二、重构：VAD 语音段携带唯一 ID

### `audio/stream_buffer.py`

**变更**：
- 新增 `SpeechSegment = namedtuple('SpeechSegment', ['id', 'audio'])`
- `push()` 和 `flush()` 返回 `list[SpeechSegment]` 替代 `list[np.ndarray]`
- 每个段生成 `uuid4` 作为唯一标识
- 清理了未使用的 `deque` 导入

**动机**：LLM 回溯修正需要按 `segment_id` 定位历史段，没有 ID 就无法从客户端精准更新某条译文。

---

## 三、核心新功能：LLM Refiner 精炼引擎

### 新文件 `llm/__init__.py`

空包文件，使 `llm/` 成为 Python 包。

### 新文件 `llm/refiner.py`

**类 `LLMRefiner`**：

- **流式 API 调用**：调用 OpenAI 兼容接口（`stream=True`），逐个 token 通过 `on_token` 回调推送到客户端，实现打字机效果。
- **滑动上下文窗口**：维护最近 N 段（默认 10）的英文译文历史，每次精炼时拼接进 prompt。
- **回溯修正（CORRECT: 协议）**：LLM 在输出精炼译文后，可附加 `CORRECT:<segment_id>:<corrected_text>` 行，服务端解析后通过 `on_corrections` 回调推给前端。
- **修正权重（Prompt 调制）**：`_build_bias_instruction(maturity)` 根据 `maturity = history_size / context_window` 动态注入修正指令：

  | maturity | 指令 | 修正焦点 |
  |----------|------|---------|
  | `< 0.3` (早期) | "Earlier translations had very limited context... Review ALL previous segments" | 大胆修正早期段 |
  | `0.3~0.7` (过渡) | "Balance corrections across old and new segments" | 均衡修正 |
  | `> 0.7` (成熟) | "Focus refinement on the new segment" | 聚焦当前段 |

- **异常安全**：LLM 调用失败时 fallback 为原始 SeamlessM4T 译文。
- **线程安全**：`threading.Lock` 保护历史窗口的并发读写。
- **历史同步**：回溯修正被接受后，自动更新上下文历史中的对应译文，保证后续 prompt 的一致性。

---

## 四、事件系统扩展

### `websocket/emitters.py`

**新增 5 个事件方法**：

| 方法 | 事件名 | 载荷 | 触发时机 |
|------|--------|------|---------|
| `emit_segment_start` | `segment_start` | `{segment_id, timestamp}` | VAD 检测到完整语音段 |
| `emit_initial_translation` | `initial_translation` | `{segment_id, text}` | SeamlessM4T 初译完成 |
| `emit_stream_token` | `stream_token` | `{segment_id, token}` | LLM 逐 token 流式输出 |
| `emit_stream_end` | `stream_end` | `{segment_id}` | LLM 精炼结束或被跳过 |
| `emit_correction` | `correction` | `{segment_id, corrected_text}` | LLM 回溯修正历史段 |

保留原有 `emit_subtitle`、`emit_error`、`emit_status` 做向后兼容。

---

## 五、核心流水线改造

### `websocket/events.py`

**变更**：
- `register_socketio_events` 新增参数 `config`、`llm_refiner`
- `_process_segment_sync` 改写为两级流水线：

  ```
  segment.id + audio
    → emit_segment_start(client_id, seg_id, timestamp)
    → raw_text = inference_engine.infer(audio)
    → emit_initial_translation(client_id, seg_id, raw_text)
    → if LLM_ENABLED and llm_refiner and raw_text:
        llm_refiner.refine(on_token→stream_token, on_corrections→correction, on_done→stream_end)
      else:
        emit_stream_end(client_id, seg_id)
  ```

- `handle_stop_stream` 调用 `_process_segment_sync(..., skip_llm=True)` 以在停止时跳过 LLM 阶段，避免延迟。
- 异常时确保 `emit_stream_end` 总是发出，不会造成前端段"卡住"。

**动机**：从"一次性翻译"变为"初译即显 + 异步精炼"模式，用户获得即时反馈的同时享受上下文修正。

---

## 六、应用初始化

### `app.py`

- 新增 `from llm.refiner import LLMRefiner`
- 条件初始化 LLM Refiner（仅 `LLM_API_KEY` 非空时创建，失败时 warn 降级）
- `register_socketio_events` 调用增加 `config=config, llm_refiner=llm_refiner`

---

## 七、依赖更新

### `requirements.txt`

添加 `openai>=1.0.0`（LLM API 客户端）。

---

## 八、前端：WebSocket 客户端扩展

### `static/js/websocket_client.js`

**新增事件回调**：`onSegmentStart`、`onInitialTranslation`、`onStreamToken`、`onStreamEnd`、`onCorrection`

**新增 SocketIO 监听**：`segment_start`、`initial_translation`、`stream_token`、`stream_end`、`correction` 五个事件。

---

## 九、前端：Dashboard 完整重写

### `static/js/dashboard.js`

**段生命周期管理**：`pending → initial → refining → final / corrected`

| 阶段 | 触发事件 | 显示 |
|------|---------|------|
| `pending` | `segment_start` | "..." + 脉冲动画 |
| `initial` | `initial_translation` | 灰色初译文本 + `fast` 徽章 |
| `refining` | `stream_token`（首个） | 清空，开始打字机追加 + 闪烁光标 |
| `final` | `stream_end` | 白色文本 + ✓ 徽章 |
| `corrected` | `correction` | 更新历史段 + ✏ 徽章 + 高亮动画 |

**核心变化**：
- `this.segments`（Map）替代旧的 `subtitleHistory`（数组），按 segment_id 索引
- `_renderCurrent()` — 渲染当前段（大字 + 时间戳 + 状态徽章 + 光标）
- `_renderHistory()` — 渲染历史列表（时间戳 + 译文 + 修正标记）
- `_moveToHistory()` — 当前段被新段取代时移入历史
- `_updateHistoryItem()` — 精准更新单条历史段（节点级操作，不重绘全部）

---

## 十、前端：CSS 样式重设计

### `static/css/dashboard.css`

**布局变更**：
- `subtitle-container` 改为纵向 flex，历史在上（自动滚动）、当前段在下（固定底部）
- 历史区使用 `mask-image` 实现顶底渐变淡出

**新样式模块**：
- `.segment-header` / `.segment-time` — 时间戳 + 徽章行
- `.segment-text.pending / .initial / .refining / .final / .corrected` — 各阶段颜色和动画
- `.cursor` — 闪烁光标 `▊`
- `.badge.*` — 5 种状态徽章（`⋯` / `fast` / `refining` / `✓` / `✏ corrected`）
- `.history-item.is-corrected` — 被修正的历史段金色底
- `.history-badge.corrected` — ✏ 修正标记
- `@keyframes highlightPulse` — 修正时的 2s 辉光动画

---

## 十一、HTML 结构调整

### `templates/index.html`

历史区 (`#subtitleHistory`) 和当前区 (`#currentSubtitle`) 的顺序对调，以匹配"历史在上、当前在下"的会议转录布局。

---

## 十二、文档更新

### `AGENTS.md`

从 15 行扩展到 51 行，新增：
- 两级翻译流水线概述
- LLM Refiner 的滑动窗口和修正权重机制
- 前端事件表（server → client 的 5 个事件）
- 段生命周期 `pending → initial → refining → final / corrected`

---

## 修改清单汇总

| 类型 | 文件 | 操作 |
|------|------|------|
| 🐛 | `config.py` | 修复缺失 `VAD_THRESHOLD`、`SILENCE_TIMEOUT_MS`；新增 LLM 配置 |
| ♻️ | `audio/stream_buffer.py` | `push()`/`flush()` 返回 `SpeechSegment`（带 UUID） |
| ✨ | `llm/__init__.py` | 新建空包文件 |
| ✨ | `llm/refiner.py` | 新建 LLM Refiner 类（流式 API + 滑动窗口 + 回溯修正 + 权重指令） |
| ✨ | `websocket/emitters.py` | 新增 5 个事件方法 |
| ♻️ | `websocket/events.py` | 两级流水线 + `segment.id` + `skip_llm` |
| ♻️ | `app.py` | 条件初始化 LLMRefiner，传入 events |
| ➕ | `requirements.txt` | 添加 `openai>=1.0.0` |
| ✨ | `static/js/websocket_client.js` | 新增 5 个事件回调 |
| ♻️ | `static/js/dashboard.js` | 完整重写段生命周期管理 |
| ♻️ | `static/css/dashboard.css` | 布局重设计 + 新样式模块 |
| ♻️ | `templates/index.html` | 历史/当前结构顺序调换 |
| 📝 | `AGENTS.md` | 扩展文档 |
