import logging
import uuid
import numpy as np
from collections import namedtuple
from .vad import VADProcessor

logger = logging.getLogger(__name__)

SpeechSegment = namedtuple('SpeechSegment', ['id', 'audio'])


class AudioStreamBuffer:
    """环形音频缓冲区 + 智能语音分段。"""

    def __init__(self, config, vad: VADProcessor):
        self.sample_rate = config.SAMPLE_RATE
        self.max_duration = config.BUFFER_MAX_DURATION_S
        self.max_samples = int(self.max_duration * self.sample_rate)
        self.segment_min_duration = config.SEGMENT_MIN_DURATION_S
        self.segment_max_duration = config.SEGMENT_MAX_DURATION_S
        self.silence_timeout_ms = config.SILENCE_TIMEOUT_MS
        self.silence_samples = int(self.silence_timeout_ms / 1000 * self.sample_rate)

        self.vad = vad
        self.buffer = np.array([], dtype=np.float32)
        self.is_collecting = False
        self.silence_count = 0
        self.current_speech = np.array([], dtype=np.float32)

    def push(self, audio_array: np.ndarray) -> list:
        results = []

        if len(audio_array) == 0:
            return results

        is_speech = self.vad.is_speech(audio_array, self.sample_rate)

        if is_speech:
            self.is_collecting = True
            self.silence_count = 0
            self.current_speech = np.concatenate([self.current_speech, audio_array])

            current_duration = len(self.current_speech) / self.sample_rate
            if current_duration >= self.segment_max_duration:
                results.append(SpeechSegment(
                    id=str(uuid.uuid4()),
                    audio=self.current_speech.copy()
                ))
                self.current_speech = np.array([], dtype=np.float32)
                self.is_collecting = False

        elif self.is_collecting:
            self.silence_count += len(audio_array)
            self.current_speech = np.concatenate([self.current_speech, audio_array])

            if self.silence_count >= self.silence_samples:
                current_duration = len(self.current_speech) / self.sample_rate
                if current_duration >= self.segment_min_duration:
                    speech_end = len(self.current_speech) - self.silence_count
                    speech_end = max(speech_end, int(self.segment_min_duration * self.sample_rate))
                    results.append(SpeechSegment(
                        id=str(uuid.uuid4()),
                        audio=self.current_speech[:speech_end].copy()
                    ))

                self.current_speech = np.array([], dtype=np.float32)
                self.is_collecting = False
                self.silence_count = 0

        self.buffer = np.concatenate([self.buffer, audio_array])
        if len(self.buffer) > self.max_samples:
            self.buffer = self.buffer[-self.max_samples:]

        return results

    def flush(self) -> list:
        results = []

        if len(self.current_speech) > 0:
            duration = len(self.current_speech) / self.sample_rate
            if duration >= 0.5:
                results.append(SpeechSegment(
                    id=str(uuid.uuid4()),
                    audio=self.current_speech.copy()
                ))

        self.current_speech = np.array([], dtype=np.float32)
        self.is_collecting = False
        self.silence_count = 0
        self.buffer = np.array([], dtype=np.float32)

        return results

    def reset(self):
        self.buffer = np.array([], dtype=np.float32)
        self.is_collecting = False
        self.silence_count = 0
        self.current_speech = np.array([], dtype=np.float32)
