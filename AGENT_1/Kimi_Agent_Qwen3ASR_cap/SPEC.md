# SPEC.md — 实时中文语音转英文字幕 Web App

## 项目信息
- **名称**: Realtime-ASR-Translate-Dashboard
- **技术栈**: Flask + Flask-SocketIO + qwen-asr + WebSocket
- **模型**: Qwen3-ASR-1.7B (本地路径加载)
- **Python**: 3.12
- **CUDA**: 12.4

## 环境约束 (严格遵循)
- torch == 2.6.0+cu124
- transformers == 5.9.0 (注: 如实际环境中transformers版本不同,以实际为准,但代码按此版本编写)
- 模型已下载到内网,通过本地路径加载
- 内网有 OpenAI 兼容格式的 LLM API (仅支持文本生成)
- 前端不能引用任何外部链接/CDN
- 只能使用 Qwen3-ASR-1.7B 模型

## 核心依赖
```
flask>=3.0.0
flask-socketio>=5.3.0
python-socketio>=5.9.0
qwen-asr>=0.1.0
numpy>=1.26.0
soundfile>=0.12.0
requests>=2.31.0
python-dotenv>=1.0.0
eventlet>=0.35.0  # 或 gevent, 用于 SocketIO 异步模式
openai>=1.0.0     # 用于调用内网 LLM API
```

## 项目结构
```
project/
├── app.py                  # Flask 主应用 + SocketIO 事件处理
├── config.py               # 全局配置
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── modules/
│   ├── __init__.py
│   ├── asr_engine.py       # ASR 引擎 (Qwen3-ASR-1.7B 封装)
│   ├── translate_engine.py # 翻译引擎 (OpenAI API 封装 + 增量修正)
│   └── audio_buffer.py     # 音频缓冲区管理
├── templates/
│   └── dashboard.html      # 主页面 (内联 CSS + JS,无外部依赖)
└── static/
    └── (空,所有资源内联在 HTML 中)
```

## 配置说明 (config.py)

所有可配置项通过 `.env` 文件 + `os.environ` 读取:

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MODEL_PATH` | `/models/Qwen3-ASR-1.7B` | 模型本地路径 |
| `LLM_API_BASE` | `http://localhost:8000/v1` | 内网 LLM API base URL |
| `LLM_API_KEY` | `EMPTY` | LLM API Key |
| `LLM_MODEL` | `Qwen2.5-7B-Instruct` | 翻译用的LLM模型名 |
| `ASR_LANGUAGE` | `Chinese` | ASR 强制识别语言 |
| `ASR_CHUNK_SEC` | `2.0` | ASR 处理窗口大小(秒) |
| `ASR_STEP_SEC` | `1.0` | ASR 处理步长(秒) |
| `TRANSLATE_MAX_HISTORY` | `10` | 翻译历史保留最大句数 |
| `SAMPLE_RATE` | `16000` | 音频采样率 |

## ASR 引擎 (modules/asr_engine.py)

### 类: `ASREngine`

#### 初始化 `__init__(self, model_path, device="cuda:0", dtype=torch.bfloat16)`
- 使用 `Qwen3ASRModel.from_pretrained()` 加载模型
- 参数: `max_inference_batch_size=32`, `max_new_tokens=256`
- `device_map=device`, `dtype=dtype`

#### 方法: `transcribe(self, audio_np, sample_rate=16000, context="", language="Chinese") -> str`
- 输入: `audio_np` (numpy float32 数组), `sample_rate` (采样率)
- 如果 `sample_rate != 16000`, 用 librosa 或 scipy 重采样到 16kHz
- 调用 `self.model.transcribe(audio=(audio_np, 16000), language=language, context=context)`
- 返回识别文本 `results[0].text`

#### 方法: `transcribe_bytes(self, audio_bytes, context="", language="Chinese") -> str`
- 将 bytes (假设为 WAV 格式) 用 soundfile 读取为 numpy 数组
- 调用 `transcribe()`

## 音频缓冲区 (modules/audio_buffer.py)

### 类: `AudioBuffer`

负责接收前端传来的音频 chunks,累积到足够长度后触发 ASR 处理。

#### 初始化 `__init__(self, sample_rate=16000, chunk_sec=2.0, step_sec=1.0)`
- `sample_rate`: 采样率 (16kHz)
- `chunk_sec`: 每次 ASR 处理的音频长度 (秒)
- `step_sec`: ASR 处理步长 (秒)
- `chunk_samples = chunk_sec * sample_rate`
- `step_samples = step_sec * sample_rate`
- 维护 `buffer` (numpy array) 和 `lock` (threading.Lock)

#### 方法: `add_audio(self, audio_np) -> bool`
- 将新音频数据追加到 buffer
- 如果 buffer 长度 >= chunk_samples, 返回 True (表示可以进行 ASR)
- 否则返回 False

#### 方法: `get_chunk_for_asr(self) -> (np.ndarray, str)`
- 从 buffer 头部取出 chunk_samples 长度的音频
- 返回: `(audio_chunk, previous_context)`
- `previous_context` 是上一次识别的文本,用于 ASR context 保持连贯性

#### 方法: `consume_step(self)`
- 将 buffer 前部移除 step_samples 长度 (滑动窗口前进)

#### 方法: `get_remaining(self) -> np.ndarray`
- 获取 buffer 中剩余的音频 (用于会话结束时最后处理)

#### 方法: `clear(self)`
- 清空 buffer

## 翻译引擎 (modules/translate_engine.py)

### 类: `TranslateEngine`

负责调用内网 LLM API 进行中文→英文翻译,支持增量修正。

#### 数据结构: `Segment`
```python
@dataclass
class Segment:
    id: int           # 段落 ID
    chinese: str      # 中文原文
    english: str      # 英文翻译
    is_final: bool    # 是否已稳定(不再修改)
```

#### 初始化 `__init__(self, api_base, api_key, model_name, max_history=10)`
- 创建 `OpenAI(api_base=api_base, api_key=api_key)` 客户端
- `model_name`: LLM 模型名称
- `max_history`: 最大保留历史段数
- `segments`: List[Segment] = [] (段落列表)
- `next_id`: int = 0 (下一段ID)
- `pending_chinese`: str = "" (当前未稳定的中文累积文本)

#### 方法: `_call_llm(self, prompt: str, temperature=0.3, max_tokens=512) -> str`
- 调用 `self.client.chat.completions.create()`
- `model=self.model_name`
- `messages=[{"role": "user", "content": prompt}]`
- 返回生成的文本

#### 方法: `add_asr_result(self, new_chinese_text: str) -> List[dict]`
这是核心方法,处理新的ASR结果并决定是否需要修正:

1. **累积新文本**: `self.pending_chinese += new_chinese_text`

2. **尝试分段**: 调用 `_detect_segments(self.pending_chinese)` 检测是否可以分成完整句子
   - 使用 LLM 判断文本中有哪些完整句子
   - 返回: `(completed_sentences, remaining_text)`

3. **处理完成的句子**:
   - 对每个新完成的句子:
     - 调用 `_translate_single(completed_sentences, previous_segments)` 翻译
     - previous_segments 提供上下文使翻译连贯
     - 创建新的 `Segment` 加入列表

4. **处理未稳定文本**: 
   - 对 remaining_text 进行临时翻译(可能后续会修正)
   - 返回给前端显示为"临时字幕"

5. **返回变更**: 返回所有新增/修改的段落列表,前端据此更新显示

#### 方法: `_detect_segments(self, text: str) -> (List[str], str)`
- 使用 LLM 判断文本中的完整句子和未完成片段
- Prompt 示例:
```
请分析以下中文文本,将其分成完整的句子。未完成或不完整的句子放在remaining中。
要求输出JSON格式: {"completed": ["句子1", "句子2"], "remaining": "未完成片段"}

文本: {text}
```

#### 方法: `_translate_single(self, sentences: List[str], context_segments: List[Segment]) -> List[str]`
- 构建翻译 prompt,包含上下文以保持连贯性
- Prompt 模板:
```
请将以下中文翻译成流利的英文。注意:
1. 保持上下文连贯
2. 返回JSON格式: {"translations": ["英文1", "英文2"]}

前文翻译:
{context_english}

待翻译中文:
{sentences_json}
```

#### 方法: `get_all_segments(self) -> List[dict]`
- 返回所有段落的中文+英文,用于前端完整显示

#### 方法: `reset(self)`
- 清空所有段落和历史

## Flask 主应用 (app.py)

### SocketIO 事件

#### `connect`
- 打印客户端连接
- 初始化该 session 的音频缓冲区和翻译状态

#### `disconnect`
- 清理资源

#### `audio_chunk` (接收前端音频数据)
- 接收二进制音频数据 (PCM float32)
- 调用 `audio_buffer.add_audio(audio_np)`
- 如果返回 True (buffer 足够):
  1. `chunk, context = audio_buffer.get_chunk_for_asr()`
  2. `chinese_text = asr_engine.transcribe(chunk, context=context)`
  3. `changes = translate_engine.add_asr_result(chinese_text)`
  4. `socketio.emit('subtitle_update', {'changes': changes})`
  5. `audio_buffer.consume_step()`

#### `start_recording`
- 重置音频缓冲区和翻译引擎
- 发射 `recording_started` 事件

#### `stop_recording`
- 处理剩余音频: `remaining = audio_buffer.get_remaining()`
- 如果 remaining 有数据,做最后一次 ASR + 翻译
- 发射 `recording_stopped` 和最终字幕

#### `force_finalize` (用户手动触发结算)
- 立即将 pending_chinese 中的文本作为完整句子处理
- 发射最终结果

### HTTP 路由

#### `GET /`
- 渲染 `dashboard.html`

#### `GET /health`
- 返回服务状态,包含模型是否加载成功

## 前端设计 (templates/dashboard.html)

### 页面布局

```
+------------------------------------------+
|  实时语音翻译字幕 Dashboard               |
+------------------------------------------+
|                                          |
|  +------------------------------------+  |
|  |  英文字幕显示区 (主区域)            |  |
|  |                                    |  |
|  |  Hello, welcome to today's        |  |
|  |  presentation. This is a demo     |  |
|  |  of real-time translation.        |  |
|  |                                    |  |
|  +------------------------------------+  |
|                                          |
|  +------------------------------------+  |
|  |  中文原文 (小字,参考用)             |  |
|  |  大家好,欢迎今天的演讲。这是实时   |  |
|  |  翻译演示。                        |  |
|  +------------------------------------+  |
|                                          |
|  [🎙️ 开始录音]  [⏹️ 停止录音]         |
|                                          |
|  状态: 🟢 连接正常 | ASR: 就绪          |
+------------------------------------------+
```

### 视觉风格
- 深色背景 (#1a1a2e 或类似暗色)
- 字幕区域: 高对比度白色/浅灰色文字
- 英文字幕: 24-32px, 字体清晰
- 中文字幕: 16-18px, 半透明
- 实时更新的文本有淡入动画
- 临时(未稳定)字幕显示为半透明或斜体

### 核心交互逻辑 (JavaScript)

#### WebSocket 连接
```javascript
const socket = io();
socket.on('connect', () => { ... });
socket.on('subtitle_update', (data) => { updateSubtitles(data.changes); });
```

#### 音频采集 (Web Audio API)
```javascript
let audioContext, mediaStream, processorNode;

async function startRecording() {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new AudioContext({ sampleRate: 16000 });
    const source = audioContext.createMediaStreamSource(mediaStream);
    processorNode = audioContext.createScriptProcessor(4096, 1, 1);
    
    processorNode.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0); // Float32 -1.0~1.0
        socket.emit('audio_chunk', inputData.buffer); // 发送 ArrayBuffer
    };
    
    source.connect(processorNode);
    processorNode.connect(audioContext.destination);
    socket.emit('start_recording');
}

function stopRecording() {
    processorNode?.disconnect();
    audioContext?.close();
    mediaStream?.getTracks().forEach(t => t.stop());
    socket.emit('stop_recording');
}
```

#### 字幕更新显示
```javascript
let segments = [];

function updateSubtitles(changes) {
    // changes: [{id, chinese, english, is_final, is_new}]
    for (const change of changes) {
        const existing = segments.find(s => s.id === change.id);
        if (existing) {
            existing.chinese = change.chinese;
            existing.english = change.english;
            existing.is_final = change.is_final;
        } else {
            segments.push(change);
        }
    }
    renderSubtitles();
}

function renderSubtitles() {
    const englishEl = document.getElementById('english-subtitles');
    const chineseEl = document.getElementById('chinese-subtitles');
    
    // 只显示最近 N 段,滚动显示
    const recent = segments.slice(-5);
    
    englishEl.innerHTML = recent.map(s => 
        `<div class="seg ${s.is_final ? 'final' : 'pending'}">${escapeHtml(s.english)}</div>`
    ).join('');
    
    chineseEl.innerHTML = recent.map(s =>
        `<div class="seg ${s.is_final ? 'final' : 'pending'}">${escapeHtml(s.chinese)}</div>`
    ).join('');
}
```

### 内联资源 (无外部依赖)
- 所有 CSS 内联在 `<style>` 标签中
- 所有 JS 内联在 `<script>` 标签中
- 使用内联 SVG 做图标
- Socket.IO 客户端 JS 从 Flask-SocketIO 提供: `/socket.io/socket.io.js`

## 数据流

```
[麦克风] --(Web Audio API)--> [前端 JS] --(WebSocket)--> [Flask]
                                                              |
                                                        [AudioBuffer]
                                                              |
                                                              v
                                                        [ASREngine]
                                                              |
                                                          中文文本
                                                              |
                                                              v
                                                        [TranslateEngine]
                                                              |
                                                          英文翻译
                                                              |
                                                              v
[前端字幕] <--(WebSocket: subtitle_update)-- [Flask/SocketIO]
```

## 翻译增量修正算法

### 问题
ASR 流式输出的中文文本会随着更多音频数据的到来而改变前文的分段方式。例如:
- t1 时刻 ASR 输出: "今天天气"
- t2 时刻 ASR 输出: "今天天气不错" → 可能分成 "今天天气" + "不错"
- 但更好的分段可能是 "今天天气不错,适合出游" → 重新分段

### 解决方案
1. **句子级稳定性**: 使用 LLM 判断一个句子是否"完整"(有明确的句末标点或语义完整)
2. **已稳定段落不修改**: 一旦一个 Segment 被标记为 `is_final=true`,不再修改
3. **未稳定文本可修正**: `pending` 状态的文本可以随着新ASR结果的到来重新翻译
4. **上下文连贯**: 翻译时提供前面已稳定段落的翻译作为上下文

### 具体流程
```
每收到 ASR 结果:
  1. 累积到 pending_chinese
  2. 调用 LLM 检测 completed sentences + remaining
  3. 对 completed sentences:
     - 如果这是新的 completed sentence → 翻译并添加为 final segment
     - 如果之前的 pending 变成了 completed → 修正翻译,标记为 final
  4. 对 remaining:
     - 翻译为临时字幕 (pending segment)
     - 下一次 ASR 结果到来时可能覆盖
  5. 发射所有变更给前端
```

## 启动方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env,填入实际的内网 LLM API 地址和模型路径

# 3. 启动服务
python app.py

# 4. 浏览器打开
# http://localhost:5000
```

## 性能考虑
- ASR 处理每 1-2 秒触发一次,保持低延迟
- 翻译使用 LLM API,可能有延迟,但只处理完整句子
- 临时(pending)字幕立即显示,不需要等 LLM 翻译完成
- 前端只保留最近 20-30 段字幕,防止DOM过大
- 后台线程处理 ASR,不阻塞 WebSocket 通信
