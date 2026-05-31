import os
import torch
import logging
from transformers import AutoProcessor, SeamlessM4Tv2ForSpeechToText

logger = logging.getLogger(__name__)


def load_model(config):
    """加载 Seamless M4T v2 Large 模型。

    从 hf-mirror 镜像源加载模型，支持本地缓存。
    首次加载需要下载约 18GB 模型文件。

    Args:
        config: 配置对象，含 MODEL_ID, MODEL_CACHE_DIR, DEVICE 等属性

    Returns:
        Tuple[AutoProcessor, SeamlessM4Tv2ForSpeechToText]: (processor, model) 元组

    Raises:
        Exception: 模型加载失败时抛出
    """
    # 设置 Hugging Face 镜像源
    os.environ["HF_ENDPOINT"] = config.MODEL_MIRROR

    logger.info(f"正在从 {config.MODEL_MIRROR} 加载模型 {config.MODEL_ID}...")
    logger.info("首次加载需要下载约 18GB 模型文件，请耐心等待...")

    try:
        # 加载 processor（分词器 + 音频特征提取器）
        processor = AutoProcessor.from_pretrained(
            config.MODEL_ID,
            cache_dir=config.MODEL_CACHE_DIR
        )

        # 加载模型，使用 float16 加速，映射到指定 CUDA 设备
        model = SeamlessM4Tv2ForSpeechToText.from_pretrained(
            config.MODEL_ID,
            cache_dir=config.MODEL_CACHE_DIR,
            torch_dtype=torch.float16,
            device_map=config.DEVICE
        )

        logger.info("模型加载成功！")
        return processor, model

    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        raise
