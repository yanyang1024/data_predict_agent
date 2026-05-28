# 实时语音转录翻译系统

基于 Qwen3-ASR-1.7B + OpenAI 兼容 API 的实时中文语音转英文翻译系统。

## 特性

- **实时流式 ASR**: 基于 Qwen3-ASR-1.7B (vLLM backend)，支持流式推理
- **增量修正**: 说话过程中自动修正已识别文本
- **流式翻译**: 通过 OpenAI 兼容 API 实时翻译
- **低延迟**: 双流水线并行架构，感知延迟 <500ms
- **Web Dashboard**: 实时展示原文和译文，支持修正高亮

## 系统架构

```
麦克风 → [VAD] → [ASR: Qwen3-ASR-1.7B] → [Translation: LLM API] → [Dashboard]
            ↓              ↓                        ↓
        语音检测    增量修正管理              流式输出
```

## 环境要求

- Python 3.12+
- CUDA 12.4+
- NVIDIA GPU (L20 推荐，显存 >= 24GB)

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
conda create -n asr-translation python=3.12 -y
conda activate asr-translation

# 安装 qwen-asr (vLLM backend)
pip install qwen-asr[vllm]

# 安装其他依赖
pip install fastapi uvicorn websockets numpy openai

# 可选: 安装 FlashAttention 加速
pip install flash-attn --no-build-isolation
```

### 2. 配置翻译 API

编辑 `config.yaml`：

```yaml
translation:
  api_base: "http://your-llm-server:8000/v1"  # 你的 OpenAI 兼容 API 地址
  model: "your-model-name"
```

### 3. 启动服务

```bash
cd backend
python server.py
```

服务启动后：
- API 地址: http://localhost:8080
- Dashboard: http://localhost:8080/dashboard
- WebSocket: ws://localhost:8080/ws/{session_id}

### 4. 使用 Dashboard

1. 打开浏览器访问 http://localhost:8080/dashboard
2. 点击麦克风按钮开始录音
3. 实时查看中文原文和英文翻译

## 核心概念

### 增量修正机制

系统通过以下策略实现平滑的增量修正：

1. **ASR 层面**: Qwen3-ASR 的 `state.text` 自动维护增量修正
2. **修正检测**: 使用 difflib.SequenceMatcher 计算文本差异
3. **视觉反馈**: 修正中的文本显示黄色高亮动画
4. **翻译同步**: 原文变化时自动重新翻译当前句子

### 句子确认策略

- **自动确认**: VAD 检测到 400ms 静音后自动确认当前句子
- **手动确认**: 点击停止按钮确认当前句子
- **最大长度**: 超过 10 秒的句子自动切分

### 翻译上下文窗口

翻译时携带最近 3 句已确认的翻译作为上下文，保证术语一致性。

## API 文档

### WebSocket 消息格式

**客户端 → 服务端**

| 类型 | 说明 |
|------|------|
| `audio.start` | 开始录音 |
| `audio.stop` | 停止录音 |
| `audio.chunk` | 音频数据 (binary) |
| `segment.confirm` | 手动确认当前句子 |
| `ping` | 心跳 |

**服务端 → 客户端**

| 类型 | 说明 |
|------|------|
| `asr.new_segment` | 新句子开始 |
| `asr.correction` | 文本修正 |
| `segment.finalized` | 句子确认完成 |
| `translation.streaming` | 流式翻译更新 |
| `translation.final` | 翻译完成 |
| `status` | 状态通知 |
| `heartbeat` | 心跳 |

### REST API

| 端点 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `GET /dashboard` | Dashboard 页面 |

## 性能优化

### 延迟优化

| 优化点 | 策略 | 效果 |
|--------|------|------|
| ASR | vLLM backend + 500ms chunk | ~200ms 首字延迟 |
| 翻译 | Early Emit + 流式输出 | 并行处理 |
| 传输 | WebSocket binary | 零拷贝 |
| 修正 | 仅重翻译 pending 部分 | 避免全文重翻 |

### 显存优化

- Qwen3-ASR-1.7B: ~10GB (vLLM)
- FlashAttention: 减少 30% 显存
- gpu_memory_utilization: 0.6 (预留显存给翻译)

## 目录结构

```
.
├── ARCHITECTURE.md           # 架构设计文档
├── README.md                 # 本文件
├── config.yaml               # 配置文件
├── backend/
│   ├── server.py             # FastAPI 服务
│   ├── engine.py             # 核心引擎
│   └── static/
│       └── index.html        # Dashboard
└── docs/
    └── deployment.md         # 部署指南
```

## 故障排查

### 模型加载失败

```bash
# 检查模型是否已下载
ls ~/.cache/huggingface/hub/Qwen3-ASR-1.7B

# 手动下载
huggingface-cli download Qwen/Qwen3-ASR-1.7B --local-dir ./Qwen3-ASR-1.7B
```

### vLLM 启动失败

```bash
# 检查 vLLM 版本
pip show vllm

# 确保使用正确版本
pip install vllm==0.7.1
```

### 翻译 API 连接失败

```bash
# 测试 API 连通性
curl http://your-llm-server:8000/v1/models
```

## License

Apache-2.0
