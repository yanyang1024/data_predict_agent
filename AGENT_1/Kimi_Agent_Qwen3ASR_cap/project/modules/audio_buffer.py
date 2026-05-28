"""
音频缓冲区管理模块。

负责接收前端传来的音频 chunks，累积到足够长度后触发 ASR 处理。
使用滑动窗口机制：每次处理 chunk_sec 长度的音频，窗口前进 step_sec。
所有操作均为线程安全。
"""

from __future__ import annotations

import logging
import threading
from typing import Tuple

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


class AudioBuffer:
    """音频缓冲区，用于累积音频数据并管理 ASR 处理窗口。"""

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_sec: float = 2.0,
        step_sec: float = 1.0,
    ) -> None:
        """
        初始化音频缓冲区。

        Args:
            sample_rate: 音频采样率 (Hz)，默认 16000。
            chunk_sec: 每次 ASR 处理的音频长度 (秒)，默认 2.0。
            step_sec: ASR 处理窗口前进步长 (秒)，默认 1.0。
        """
        if sample_rate <= 0:
            raise ValueError("sample_rate 必须大于 0")
        if chunk_sec <= 0:
            raise ValueError("chunk_sec 必须大于 0")
        if step_sec <= 0 or step_sec > chunk_sec:
            raise ValueError("step_sec 必须在 (0, chunk_sec] 范围内")

        self.sample_rate: int = sample_rate
        self.chunk_samples: int = int(chunk_sec * sample_rate)
        self.step_samples: int = int(step_sec * sample_rate)

        self._buffer: NDArray[np.float32] = np.array([], dtype=np.float32)
        self._previous_context: str = ""
        self._lock: threading.Lock = threading.Lock()

        logger.debug(
            "AudioBuffer 初始化完成: chunk=%d samples, step=%d samples",
            self.chunk_samples,
            self.step_samples,
        )

    def add_audio(self, audio: NDArray[np.float32]) -> bool:
        """
        将新音频数据追加到缓冲区。

        Args:
            audio: numpy float32 数组，数值范围 [-1.0, 1.0]。

        Returns:
            bool: True 表示缓冲区已满，可以进行 ASR 处理。
        """
        audio = np.asarray(audio, dtype=np.float32)

        if audio.ndim == 0:
            raise ValueError("audio 不能为空数组")
        if audio.ndim > 1:
            # 多声道数据转单声道 (取平均)
            audio = audio.mean(axis=tuple(range(1, audio.ndim)))

        with self._lock:
            self._buffer = np.concatenate([self._buffer, audio])
            buffer_ready = self._buffer.shape[0] >= self.chunk_samples

        if buffer_ready:
            logger.debug(
                "缓冲区就绪: %d samples (>= %d)",
                self._buffer.shape[0],
                self.chunk_samples,
            )
        return buffer_ready

    def get_chunk_for_asr(self) -> Tuple[NDArray[np.float32], str]:
        """
        从缓冲区头部取出 chunk_samples 长度的音频用于 ASR。

        Returns:
            (audio_chunk, previous_context):
                audio_chunk: np.ndarray，长度为 chunk_samples。
                previous_context: str，上一次识别的文本，用于 ASR context。
        """
        with self._lock:
            chunk = self._buffer[: self.chunk_samples].copy()
            context = self._previous_context
            return chunk, context

    def set_context(self, context: str) -> None:
        """
        设置下一次 ASR 的上下文文本。

        Args:
            context: 上一次识别的文本。
        """
        with self._lock:
            self._previous_context = context

    @property
    def previous_context(self) -> str:
        """获取当前上下文文本。"""
        with self._lock:
            return self._previous_context

    def consume_step(self) -> None:
        """滑动窗口前进 step_samples。"""
        with self._lock:
            original_len = self._buffer.shape[0]
            self._buffer = self._buffer[self.step_samples :]
            logger.debug(
                "窗口前进 %d samples: %d -> %d",
                self.step_samples,
                original_len,
                self._buffer.shape[0],
            )

    def get_remaining(self) -> NDArray[np.float32]:
        """
        获取缓冲区中剩余的音频。

        Returns:
            剩余音频的 numpy 数组副本。
        """
        with self._lock:
            return self._buffer.copy()

    def clear(self) -> None:
        """清空缓冲区并重置上下文。"""
        with self._lock:
            self._buffer = np.array([], dtype=np.float32)
            self._previous_context = ""
            logger.debug("缓冲区已清空")

    @property
    def buffer_size(self) -> int:
        """当前缓冲区中的样本数。"""
        with self._lock:
            return self._buffer.shape[0]

    @property
    def buffer_duration_sec(self) -> float:
        """当前缓冲区中的音频时长 (秒)。"""
        return self.buffer_size / self.sample_rate
