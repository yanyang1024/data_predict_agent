# 实时语音转录翻译系统 - 架构设计文档

## 1. 系统概述

基于 Qwen3-ASR-1.7B + OpenAI 兼容 API 的实时中文语音转英文翻译系统，支持流式识别、增量修正和低延迟翻译。

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                               用户层 (Browser)                               │
│  ┌─────────────────┐  ┌─────────────────────────────────────────────────┐   │
│  │  麦克风采集模块   │  │           实时字幕 Dashboard                     │   │
│  │  Web Audio API  │  │  ┌──────────────┐  ┌──────────────────────────┐ │   │
│  │  • 16kHz PCM16  │  │  │  中文原文区   │  │      英文翻译区           │ │   │
│  │  • 100ms chunk  │  │  │  增量修正展示 │  │   流式打字机效果          │ │   │
│  │  • VAD 预处理   │  │  │  • confirmed │  │   • confirmed            │ │   │
│  │                 │  │  │  • pending   │  │   • streaming            │ │   │
│  └────────┬────────┘  │  │  • correcting│  │   • correcting           │ │   │
│           │           │  └──────────────┘  └──────────────────────────┘ │   │
│           │ WebSocket │                                              ↑      │
│           │ (binary)  │                                         自动滚动    │
└───────────┼───────────┴──────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         服务层 (FastAPI + WebSocket)                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Connection Manager                               │   │
│  │  • WebSocket 连接管理  • 会话状态维护  • 心跳检测                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐   │
│  │                    Audio Pipeline Processor                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │   │
│  │  │  PCM Buffer │→ │  VAD Engine │→ │    Sliding Window (4s)      │  │   │
│  │  │  (ring buf) │  │ Silero/WebRTC│  │    重叠 50% 滑动处理         │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐   │
│  │              ASR Engine (Qwen3-ASR-1.7B via vLLM)                    │   │
│  │  • init_streaming_state()                                            │   │
│  │  • streaming_transcribe(chunk, state)  ← 每 500ms 触发              │   │
│  │  • state.text 自动增量修正                                            │   │
│  │  • finish_streaming_transcribe()                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐   │
│  │              Translation Engine (OpenAI Compatible API)               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐     │   │
│  │  │               Translation State Machine                      │     │   │
│  │  │                                                              │     │   │
│  │  │   ASR 文本 ──→ [Sentence Buffer] ──→ [Translation Queue]  │     │   │
│  │  │     ↑              │                     │                  │     │   │
│  │  │     │         标点/停顿切分         LLM stream=True          │     │   │
│  │  │     │              │                     │                  │     │   │
│  │  │     └──────────────┘←────────────────────┘                  │     │   │
│  │  │              原文变化时触发重新翻译                            │     │   │
│  │  └─────────────────────────────────────────────────────────────┘     │   │
│  │                                                                       │   │
│  │  • 流式输出: stream=True (SSE/StreamResponse)                        │   │
│  │  • 上下文窗口: 最近 3 句已确认翻译                                    │   │
│  │  • 智能切分: 按句子边界触发翻译                                       │   │
│  │  • 修正传播: 仅重新翻译 pending 部分                                  │   │
│  │  • 并发控制: max_concurrent=2 防止翻译堆积                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────▼─────────────────────────────────────┐   │
│  │                    Event Dispatcher (WebSocket)                       │   │
│  │  • asr.partial     {text, is_final=false, segment_id}               │   │
│  │  • asr.final       {text, is_final=true, segment_id}                │   │
│  │  • asr.correction  {old_text, new_text, segment_id}                 │   │
│  │  • translation.partial    {text, segment_id, is_streaming}          │   │
│  │  • translation.final      {text, segment_id}                        │   │
│  │  • translation.correction {old_text, new_text, segment_id}          │   │
│  │  • status          {type: "buffering|processing|error"}             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

## 3. 核心数据流

### 3.1 音频流 → ASR 识别

```
时间轴 →

[100ms] Audio Chunk 1 ──→ Buffer ──→ streaming_transcribe(chunk1, state)
                                                          ↓
[200ms] Audio Chunk 2 ──→ Buffer ──→ streaming_transcribe(chunk2, state)
                                                          ↓
                                                          state.text = "今天"
[300ms] Audio Chunk 3 ──→ Buffer ──→ streaming_transcribe(chunk3, state)
                                                          ↓
                                                          state.text = "今天的会议"
[400ms] Audio Chunk 4 ──→ Buffer ──→ streaming_transcribe(chunk4, state)
                                                          ↓
                                                          state.text = "今天的会议主题"
                                                          ↓
                                            检测到停顿 (400ms silence)
                                                          ↓
                                     finish_streaming_transcribe(state)
                                                          ↓
                                                触发翻译
```

### 3.2 增量修正机制

```
状态 1: state.text = "今天的会议"      → 前端显示: "今天的会议"
           ↓
状态 2: state.text = "今天记得会议"     → 检测到修正
           ↓
前端处理:  "今天<del>的</del><ins>记得</ins>会议"  → 高亮闪烁修正部分
           ↓
状态 3: state.text = "今天记得会议室"   → 继续增量
           ↓
检测到停顿 → finish → segment 确认 → 触发翻译
```

### 3.3 翻译流水线

```
已确认中文 Segments: ["大家好", "今天的会议主题是", "关于新产品的规划"]
                           ↓
Translation Context Window (最近3句):
  "大家好" → "Hello everyone"
  "今天的会议主题是" → "The theme of today's meeting is"
                           ↓
当前待翻译: "关于新产品的规划"
                           ↓
LLM Prompt:
  上下文: 已确认翻译
  当前: 待翻译中文
  指令: 翻译成英文，保持专业术语一致
                           ↓
流式输出: "About" → "About the" → "About the new" → "About the new product"
                           ↓
前端: 打字机效果逐词显示
```

## 4. 增量修正策略

### 4.1 ASR 层面
- Qwen3-ASR 的 `state.text` 自动维护增量修正
- 每次 `streaming_transcribe()` 调用后对比前后文本差异
- 使用 difflib.SequenceMatcher 计算文本差异
- 仅标记变化部分为 `correcting` 状态

### 4.2 翻译层面
- **句子级确认**: 检测到停顿(400ms)或标点符号后确认句子
- **修正传播策略**:
  - 已确认句子: 不重新翻译（避免闪烁）
  - 当前句子: 原文变化时重新翻译
  - 优化: 仅发送变化部分 + 上下文，而非全文

### 4.3 前端展示
- **三种视觉状态**:
  - `confirmed`: 灰色/正常色，稳定显示
  - `streaming`: 蓝色光标闪烁，逐字出现
  - `correcting`: 黄色高亮 + 淡入淡出动画

## 5. 延迟优化策略

| 优化点 | 策略 | 预期效果 |
|--------|------|----------|
| ASR 延迟 | vLLM backend + 500ms chunk | <300ms 首字延迟 |
| 翻译延迟 | Early Emit (句子未确认即开始翻译) | 并行流水线 |
| 传输延迟 | WebSocket binary PCM | 减少编码开销 |
| 感知延迟 | 流式输出 + 打字机效果 | 用户感知 <500ms |
| 修正延迟 | 仅重翻译 pending 部分 | 避免全文重翻 |

## 6. 关键配置参数

### ASR 配置
```python
ASR_CONFIG = {
    "model": "Qwen/Qwen3-ASR-1.7B",
    "gpu_memory_utilization": 0.6,      # L20 48GB 足够
    "max_new_tokens": 32,               # 流式小值
    "streaming": {
        "chunk_ms": 500,                # 每 500ms 处理一次
        "unfixed_chunk_num": 2,
        "unfixed_token_num": 5,
        "chunk_size_sec": 2.0,
    }
}
```

### 翻译配置
```python
TRANSLATION_CONFIG = {
    "api_base": "http://your-llm-server/v1",
    "model": "your-translation-model",
    "max_context_segments": 3,          # 上下文窗口
    "stream": True,
    "temperature": 0.3,                 # 低温度保证一致性
    "trigger_mode": "sentence_end",     # 句子结束触发
}
```

### VAD 配置
```python
VAD_CONFIG = {
    "threshold": 0.5,                   # 语音检测阈值
    "min_speech_duration_ms": 250,      # 最小语音长度
    "min_silence_duration_ms": 400,     # 停顿确认时间
    "max_speech_duration_s": 30,        # 最大单次语音长度
}
```
