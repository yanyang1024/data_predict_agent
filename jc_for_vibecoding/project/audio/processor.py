import logging
import numpy as np
import torch
import torchaudio

logger = logging.getLogger(__name__)


class AudioProcessor:
    """音频格式转换与预处理。"""

    def __init__(self, target_sample_rate: int = 16000):
        self.target_sample_rate = target_sample_rate
        self._resamplers = {}

    def process(self, audio_bytes: bytes, source_sample_rate: int = 16000) -> np.ndarray:
        """将原始音频字节转换为模型可用的 numpy 数组。

        Args:
            audio_bytes: 前端传来的 PCM FLOAT32 音频原始字节
            source_sample_rate: 原始采样率

        Returns:
            float32 numpy 数组, shape [n_samples], 采样率为 target_sample_rate
        """
        try:
            audio_array = np.frombuffer(audio_bytes, dtype=np.float32)

            if len(audio_array) == 0:
                return np.array([], dtype=np.float32)

            # 重采样
            if source_sample_rate != self.target_sample_rate:
                key = source_sample_rate
                if key not in self._resamplers:
                    self._resamplers[key] = torchaudio.transforms.Resample(
                        orig_freq=source_sample_rate,
                        new_freq=self.target_sample_rate
                    )

                waveform = torch.from_numpy(audio_array).unsqueeze(0)
                resampled = self._resamplers[key](waveform)
                audio_array = resampled.squeeze(0).numpy()

            # 归一化到 [-1, 1]
            max_val = np.max(np.abs(audio_array))
            if max_val > 1.0:
                audio_array = audio_array / max_val
            elif max_val < 1e-10:
                audio_array = np.zeros_like(audio_array)

            return audio_array.astype(np.float32)

        except Exception as e:
            logger.error(f"音频处理失败: {e}")
            return np.array([], dtype=np.float32)

    def from_float32_array(self, audio_array: np.ndarray, source_sample_rate: int = 16000) -> np.ndarray:
        """将已有的 float32 数组重采样到目标采样率。

        Args:
            audio_array: float32 numpy 数组
            source_sample_rate: 原始采样率

        Returns:
            float32 numpy 数组, 采样率为 target_sample_rate
        """
        if source_sample_rate == self.target_sample_rate:
            return audio_array.astype(np.float32)

        if source_sample_rate not in self._resamplers:
            self._resamplers[source_sample_rate] = torchaudio.transforms.Resample(
                orig_freq=source_sample_rate,
                new_freq=self.target_sample_rate
            )

        waveform = torch.from_numpy(audio_array).unsqueeze(0).float()
        resampled = self._resamplers[source_sample_rate](waveform)
        return resampled.squeeze(0).numpy().astype(np.float32)
