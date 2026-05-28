# Plan: 实时中文语音转英文字幕 Web App

## 项目概述
基于 Qwen3-ASR-1.7B 的 Flask Web 应用，实现电脑实时中文语音→英文流式字幕，支持增量翻译修正。

## 技术栈
- **后端**: Flask + Flask-SocketIO (WebSocket 流式推送)
- **ASR 模型**: Qwen3-ASR-1.7B (本地已下载, ~4.37G)
- **翻译**: 内网 OpenAI 兼容格式 LLM API (文本生成)
- **音频处理**: WebRTC getUserMedia + Web Audio API (前端) + 后端处理
- **环境**: Python 3.12, CUDA 12.4, torch 2.6.0+cu124, transformers 5.9.0

## 阶段划分

### Stage 1 — 项目搭建与核心模块
- 创建 Flask 项目结构
- 集成 Qwen3-ASR-1.7B 模型 (本地路径加载)
- 实现 WebSocket 实时音频流传输
- 音频预处理 (PCM → 模型输入格式)

### Stage 2 — ASR 流式转录引擎
- 实现流式 ASR (chunk-based 实时识别)
- WebSocket 实时推送中文转录结果
- 音频缓冲区管理

### Stage 3 — 翻译引擎 (增量修正)
- OpenAI 兼容 API 调用封装
- 增量翻译 + 前文分段修正逻辑
- 翻译结果流式推送

### Stage 4 — 前端 Dashboard
- 纯前端实现 (无外部 CDN)
- WebRTC 音频采集
- 实时字幕显示 (流式输出效果)
- 双语字幕展示 (中文 + 英文)

### Stage 5 — 测试与部署
- 验证所有功能流程
- 确保无外部依赖

## 文件结构
```
project/
├── app.py                 # Flask 主入口
├── config.py              # 配置
├── requirements.txt       # 依赖 (严格版本)
├── asr_engine.py          # ASR 引擎
├── translate_engine.py    # 翻译引擎
├── audio_processor.py     # 音频处理
├── templates/
│   └── dashboard.html     # 前端页面
└── static/
    ├── css/
    │   └── style.css      # 样式
    └── js/
        └── app.js         # 前端逻辑
```

## 关键设计决策
1. **音频流**: 前端 Web Audio API 采集 + WebSocket 二进制传输
2. **ASR 处理**: 滑动窗口 chunk 处理，支持流式输出
3. **翻译增量修正**: 维护文本历史，调用 LLM 重新分段优化前文
4. **无外部链接**: 所有资源本地 served，不用 CDN
