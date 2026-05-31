import os


class Config:
    """全局配置类。"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Model
    MODEL_ID = "facebook/seamless-m4t-v2-large"
    MODEL_MIRROR = "https://hf-mirror.com"
    MODEL_CACHE_DIR = os.environ.get('MODEL_CACHE_DIR', './models')
    TORCH_DTYPE = "float16"
    DEVICE = "cuda:0"

    # Audio Processing
    SAMPLE_RATE = 16000
    CHUNK_DURATION_MS = 100
    BUFFER_MAX_DURATION_S = 10
    SEGMENT_MIN_DURATION_S = 1.5
    SEGMENT_MAX_DURATION_S = 4.0
    VAD_THRESHOLD = 0.5
    SILENCE_TIMEOUT_MS = 500

    # Inference
    INFERENCE_BATCH_SIZE = 1
    MAX_CONCURRENT_INFERENCE = 1
    INFERENCE_TIMEOUT_S = 30

    # WebSocket
    PING_TIMEOUT = 60
    PING_INTERVAL = 25

    # Logging
    LOG_LEVEL = "INFO"

    # LLM Refiner
    LLM_ENABLED = True
    LLM_API_BASE = os.environ.get('LLM_API_BASE', 'https://api.openai.com/v1')
    LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
    LLM_MODEL = 'gpt-4o-mini'
    LLM_TIMEOUT_S = 15
    LLM_CONTEXT_WINDOW = 10

    # Correction bias — controls where LLM focuses corrections as context grows
    # maturity = history_size / context_window
    # maturity < EARLY_THRESHOLD → aggressively correct early segments (little context existed)
    # maturity > MATURE_THRESHOLD → focus corrections on current/recent segments
    LLM_EARLY_THRESHOLD = 0.3
    LLM_MATURE_THRESHOLD = 0.7
