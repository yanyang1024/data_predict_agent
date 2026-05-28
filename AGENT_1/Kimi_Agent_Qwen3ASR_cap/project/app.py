"""
Flask 主应用 -- 实时中文语音转英文字幕 Dashboard

架构说明:
    - Flask 提供 HTTP 路由服务（首页、健康检查）
    - Flask-SocketIO 提供 WebSocket 实时通信
    - ASR 引擎负责语音识别（由 modules/asr_engine 提供）
    - 翻译引擎负责中译英（由 modules/translate_engine 提供）
    - 音频缓冲区管理实时音频流（由 modules/audio_buffer 提供）

并发模型:
    - 使用 threading 模式处理 SocketIO，兼容 ASR 的长耗时调用
    - 每个 WebSocket 会话（sid）拥有独立的翻译引擎和音频缓冲区
    - 全局 ASR 引擎在所有会话间共享
"""

import logging
from typing import Optional

import numpy as np
import torch
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from config import Config
from modules.audio_buffer import AudioBuffer
from modules.asr_engine import ASREngine
from modules.translate_engine import TranslateEngine

# ---------------------------------------------------------------------------
# 日志配置
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Flask 应用初始化
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = "asr-translate-secret-key"

# async_mode='threading' 使用原生线程模型，兼容性最好，
# 适合与 CPU/GPU 密集型的 ASR 推理配合使用
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
)

# ---------------------------------------------------------------------------
# 全局组件（会话隔离）
# ---------------------------------------------------------------------------

asr_engine: Optional[ASREngine] = None
# 每个 sid 对应一个翻译引擎，保证多客户端隔离
translate_engines: dict = {}  # sid -> TranslateEngine
# 每个 sid 对应一个音频缓冲区
audio_buffers: dict = {}  # sid -> AudioBuffer


# ---------------------------------------------------------------------------
# 引擎初始化
# ---------------------------------------------------------------------------


def init_engines() -> None:
    """初始化全局 ASR 引擎。

    应用在启动时调用一次，加载 ASR 模型到 GPU/CPU。
    如果初始化失败，应用仍能运行但 ASR 功能不可用。
    """
    global asr_engine
    try:
        cfg = Config()
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        asr_engine = ASREngine(
            model_path=cfg.MODEL_PATH,
            device=device,
        )
        logger.info(f"ASR 引擎初始化成功，设备: {device}")
    except Exception as e:
        logger.error(f"ASR 引擎初始化失败: {e}")
        asr_engine = None


# ---------------------------------------------------------------------------
# HTTP 路由
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """渲染 Dashboard 首页。"""
    return render_template("dashboard.html")


@app.route("/health")
def health():
    """健康检查端点。

    Returns:
        JSON 包含服务状态、ASR 加载状态、CUDA 可用性
    """
    return {
        "status": "ok",
        "asr_loaded": asr_engine.health_check() if asr_engine else False,
        "cuda_available": torch.cuda.is_available(),
    }


# ---------------------------------------------------------------------------
# WebSocket 事件处理
# ---------------------------------------------------------------------------


@socketio.on("connect")
def handle_connect():
    """客户端连接时触发。

    为每个会话创建独立的:
        - TranslateEngine: 隔离翻译上下文
        - AudioBuffer: 隔离音频缓冲区
    """
    from flask import request

    sid = request.sid
    logger.info(f"客户端连接: {sid}")

    cfg = Config()

    # 为该会话创建独立的翻译引擎
    translate_engines[sid] = TranslateEngine(
        api_base=cfg.LLM_API_BASE,
        api_key=cfg.LLM_API_KEY,
        model_name=cfg.LLM_MODEL,
        max_history=cfg.TRANSLATE_MAX_HISTORY,
    )

    # 为该会话创建独立的音频缓冲区
    audio_buffers[sid] = AudioBuffer(
        sample_rate=cfg.SAMPLE_RATE,
        chunk_sec=cfg.ASR_CHUNK_SEC,
        step_sec=cfg.ASR_STEP_SEC,
    )

    emit("connected", {"status": "ok", "message": "连接成功"})


@socketio.on("disconnect")
def handle_disconnect():
    """客户端断开时触发，清理会话资源。"""
    from flask import request

    sid = request.sid
    logger.info(f"客户端断开: {sid}")

    # 清理会话专属资源
    translate_engines.pop(sid, None)
    audio_buffers.pop(sid, None)


@socketio.on("start_recording")
def handle_start_recording():
    """客户端请求开始录音时触发。

    重置该会话的音频缓冲区和翻译引擎状态，准备接收新的音频流。
    """
    from flask import request

    sid = request.sid
    logger.info(f"开始录音: {sid}")

    # 重置音频缓冲区
    if sid in audio_buffers:
        audio_buffers[sid].clear()

    # 重置翻译引擎
    if sid in translate_engines:
        translate_engines[sid].reset()

    emit("recording_started", {"status": "ok"})


@socketio.on("stop_recording")
def handle_stop_recording():
    """客户端请求停止录音时触发。

    处理音频缓冲区中剩余的音频数据，确保最后的内容被识别和翻译。
    同时调用 finalize_all 确保所有 pending 段落被标记为最终。
    """
    from flask import request

    sid = request.sid
    logger.info(f"停止录音: {sid}")

    # 处理剩余音频（如果足够长）
    if sid in audio_buffers and sid in translate_engines and asr_engine is not None:
        remaining = audio_buffers[sid].get_remaining()
        # 至少 0.1 秒音频（1600 samples @ 16kHz）
        if len(remaining) > 1600:
            try:
                cfg = Config()
                # 获取前文上下文以保持识别连贯性
                context = audio_buffers[sid].previous_context
                text = asr_engine.transcribe(
                    remaining,
                    sample_rate=cfg.SAMPLE_RATE,
                    context=context,
                    language=cfg.ASR_LANGUAGE,
                )
                if text and text.strip():
                    changes = translate_engines[sid].add_asr_result(text)
                    # 强制结算所有 pending 段落
                    final_changes = translate_engines[sid].finalize_all()
                    changes.extend(final_changes)
                    if changes:
                        emit("subtitle_update", {"changes": changes})
            except Exception as e:
                logger.error(f"处理剩余音频失败: {e}")

    emit("recording_stopped", {"status": "ok"})


@socketio.on("audio_chunk")
def handle_audio_chunk(data: bytes):
    """接收前端发送的音频数据块。

    处理流程:
        1. 将二进制数据转换为 numpy float32 数组
        2. 添加到音频缓冲区
        3. 当缓冲区累积足够数据时，触发 ASR 识别
        4. 将识别结果交给翻译引擎
        5. 向前端发送字幕更新

    Args:
        data: 前端发送的 Float32Array ArrayBuffer
    """
    from flask import request

    sid = request.sid

    if sid not in audio_buffers or asr_engine is None:
        return

    try:
        # 前端发送的是 Float32Array 的 ArrayBuffer
        audio_np = np.frombuffer(data, dtype=np.float32)

        # 添加到缓冲区，返回值表示是否已达到 ASR 处理阈值
        should_process = audio_buffers[sid].add_audio(audio_np)

        if should_process:
            cfg = Config()

            # 获取音频块和前文上下文
            chunk, context = audio_buffers[sid].get_chunk_for_asr()

            # ASR 识别（中文）
            chinese_text = asr_engine.transcribe(
                chunk,
                sample_rate=cfg.SAMPLE_RATE,
                context=context,
                language=cfg.ASR_LANGUAGE,
            )

            if chinese_text and chinese_text.strip():
                # 更新上下文，供下一次识别使用
                audio_buffers[sid].set_context(chinese_text)

                # 翻译引擎处理，获取变更列表
                changes = translate_engines[sid].add_asr_result(chinese_text)

                if changes:
                    emit("subtitle_update", {"changes": changes})

            # 滑动窗口前进，准备接收下一段音频
            audio_buffers[sid].consume_step()

    except Exception as e:
        logger.error(f"处理音频 chunk 失败: {e}")


@socketio.on("force_finalize")
def handle_force_finalize():
    """用户手动触发结算（如需要立即确认当前字幕）。

    将当前 pending 段落强制标记为 final，适用于用户需要
    立即确认当前翻译的场景。
    """
    from flask import request

    sid = request.sid

    if sid in translate_engines:
        changes = translate_engines[sid].finalize_all()
        if changes:
            emit("subtitle_update", {"changes": changes})


# ---------------------------------------------------------------------------
# 应用入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_engines()
    cfg = Config()
    logger.info(
        f"启动服务: {cfg.FLASK_HOST}:{cfg.FLASK_PORT} "
        f"(debug={cfg.FLASK_DEBUG})"
    )
    socketio.run(
        app,
        host=cfg.FLASK_HOST,
        port=cfg.FLASK_PORT,
        debug=cfg.FLASK_DEBUG,
        allow_unsafe_werkzeug=True,
    )
