import asyncio
import logging
import numpy as np
import torch
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class InferenceEngine:
    """Seamless M4T v2 推理引擎。

    线程安全的推理引擎，使用单线程线程池避免并发冲突。
    支持同步和异步两种推理模式。
    """

    def __init__(self, processor, model, config):
        """初始化推理引擎。

        Args:
            processor: AutoProcessor 实例，用于音频预处理和文本解码
            model: SeamlessM4Tv2ForSpeechToText 实例
            config: 配置对象
        """
        self.processor = processor
        self.model = model
        self.config = config
        self.device = config.DEVICE
        self._executor = ThreadPoolExecutor(max_workers=1)

    def infer(self, audio_array: np.ndarray, sample_rate: int = 16000) -> str:
        """同步推理。

        对输入音频执行语音到英文文本的翻译推理。
        自动验证音频长度，过短返回空字符串，过长自动截断。
        推理完成后清理 GPU 缓存。

        Args:
            audio_array: float32 numpy 数组, shape [n_samples]
            sample_rate: 采样率, 默认 16000

        Returns:
            英文翻译文本字符串
        """
        # 验证音频长度
        duration = len(audio_array) / sample_rate
        if duration < 0.5:
            return ""
        if duration > 30:
            audio_array = audio_array[:int(30 * sample_rate)]

        try:
            # 预处理音频
            inputs = self.processor(
                audios=audio_array,
                sampling_rate=sample_rate,
                return_tensors="pt"
            )

            # 将输入移到目标设备
            inputs = {
                k: v.to(self.device) if hasattr(v, 'to') else v
                for k, v in inputs.items()
            }

            # 推理（关闭梯度计算以节省显存）
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    tgt_lang="eng"
                )

            # 解码生成的 token 为文本
            result = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]

            # 清理 GPU 缓存
            torch.cuda.empty_cache()
            return result.strip()

        except Exception as e:
            logger.error(f"推理失败: {e}")
            torch.cuda.empty_cache()
            return ""

    async def infer_async(self, audio_array: np.ndarray, sample_rate: int = 16000) -> str:
        """异步推理包装。

        在线程池中执行同步推理，避免阻塞事件循环。

        Args:
            audio_array: float32 numpy 数组, shape [n_samples]
            sample_rate: 采样率, 默认 16000

        Returns:
            英文翻译文本字符串
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self.infer,
            audio_array,
            sample_rate
        )

    def shutdown(self):
        """关闭线程池。

        释放线程池资源，应在应用关闭时调用。
        """
        self._executor.shutdown(wait=True)
