import logging
import os
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS

from config import Config
from model.loader import load_model
from model.inference import InferenceEngine
from audio.processor import AudioProcessor
from audio.vad import VADProcessor
from audio.stream_buffer import AudioStreamBuffer
from websocket.events import register_socketio_events
from websocket.emitters import SubtitleEmitter
from llm.refiner import LLMRefiner


def create_app(config=None):
    """Flask 应用工厂函数。"""

    app = Flask(__name__)

    if config is None:
        config = Config()
    app.config.from_object(config)

    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # 日志
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # 加载模型
    logger.info("正在初始化模型...")
    processor, model = load_model(config)

    # 初始化组件
    inference_engine = InferenceEngine(processor, model, config)
    audio_processor = AudioProcessor(target_sample_rate=config.SAMPLE_RATE)
    vad = VADProcessor(threshold=config.VAD_THRESHOLD)

    # LLM refiner（可选，配置 API Key 后启用）
    llm_refiner = None
    if config.LLM_ENABLED and config.LLM_API_KEY:
        try:
            llm_refiner = LLMRefiner(config)
            logger.info("LLM refiner 初始化成功")
        except Exception as e:
            logger.warning(f"LLM refiner 初始化失败，将使用纯 SeamlessM4T: {e}")
    else:
        logger.info("LLM refiner 未配置")

    def stream_buffer_factory():
        """工厂函数：创建新的 AudioStreamBuffer。"""
        return AudioStreamBuffer(config, vad)

    # SocketIO
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        ping_timeout=config.PING_TIMEOUT,
        ping_interval=config.PING_INTERVAL,
        async_mode='threading'
    )

    subtitle_emitter = SubtitleEmitter(socketio)

    # 注册事件
    register_socketio_events(
        socketio, inference_engine, audio_processor,
        stream_buffer_factory, subtitle_emitter,
        config=config, llm_refiner=llm_refiner
    )

    # 路由
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/health')
    def health():
        return {'status': 'ok', 'model': config.MODEL_ID}

    logger.info("Flask 应用初始化完成")
    return app, socketio
