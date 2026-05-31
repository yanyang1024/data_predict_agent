import logging
import numpy as np
import torch

logger = logging.getLogger(__name__)


class VADProcessor:
    """Silero VAD 语音活动检测。"""

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载 Silero VAD 模型。"""
        try:
            self.model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.model.eval()
            if torch.cuda.is_available():
                self.model = self.model.cuda()
            logger.info("VAD 模型加载成功")
        except Exception as e:
            logger.error(f"VAD 模型加载失败: {e}")
            self.model = None

    def is_speech(self, audio_array: np.ndarray, sample_rate: int = 16000) -> bool:
        """判断音频段是否包含语音。

        Args:
            audio_array: float32 numpy 数组
            sample_rate: 采样率

        Returns:
            bool, True 表示包含语音
        """
        if self.model is None or len(audio_array) == 0:
            return False

        try:
            # Silero VAD 要求特定采样率
            if sample_rate not in (8000, 16000):
                logger.warning(f"VAD 不支持 {sample_rate}Hz，使用 16kHz")
                return False

            tensor = torch.from_numpy(audio_array).float()
            if tensor.dim() == 1:
                tensor = tensor.unsqueeze(0)

            if torch.cuda.is_available():
                tensor = tensor.cuda()

            with torch.no_grad():
                speech_prob = self.model(tensor, sample_rate).item()

            return speech_prob > self.threshold

        except Exception as e:
            logger.error(f"VAD 检测失败: {e}")
            return False

    def get_speech_prob(self, audio_array: np.ndarray, sample_rate: int = 16000) -> float:
        """获取语音概率值。

        Args:
            audio_array: float32 numpy 数组
            sample_rate: 采样率

        Returns:
            float, 语音概率 (0-1)
        """
        if self.model is None or len(audio_array) == 0:
            return 0.0

        try:
            if sample_rate not in (8000, 16000):
                return 0.0

            tensor = torch.from_numpy(audio_array).float()
            if tensor.dim() == 1:
                tensor = tensor.unsqueeze(0)

            if torch.cuda.is_available():
                tensor = tensor.cuda()

            with torch.no_grad():
                return self.model(tensor, sample_rate).item()
        except Exception:
            return 0.0
