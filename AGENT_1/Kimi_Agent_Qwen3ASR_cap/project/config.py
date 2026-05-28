"""全局配置模块 — 从 .env 文件和环境变量读取配置。"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """应用配置类，所有配置项都有默认值。"""

    # ASR 模型路径
    MODEL_PATH: str = os.environ.get("MODEL_PATH", "/models/Qwen3-ASR-1.7B")

    # LLM API 配置
    LLM_API_BASE: str = os.environ.get("LLM_API_BASE", "http://localhost:8000/v1")
    LLM_API_KEY: str = os.environ.get("LLM_API_KEY", "EMPTY")
    LLM_MODEL: str = os.environ.get("LLM_MODEL", "Qwen2.5-7B-Instruct")

    # ASR 处理参数
    ASR_LANGUAGE: str = os.environ.get("ASR_LANGUAGE", "Chinese")
    ASR_CHUNK_SEC: float = float(os.environ.get("ASR_CHUNK_SEC", "2.0"))
    ASR_STEP_SEC: float = float(os.environ.get("ASR_STEP_SEC", "1.0"))

    # 翻译参数
    TRANSLATE_MAX_HISTORY: int = int(os.environ.get("TRANSLATE_MAX_HISTORY", "10"))

    # 音频参数
    SAMPLE_RATE: int = int(os.environ.get("SAMPLE_RATE", "16000"))

    # Flask 配置
    FLASK_HOST: str = os.environ.get("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.environ.get("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
