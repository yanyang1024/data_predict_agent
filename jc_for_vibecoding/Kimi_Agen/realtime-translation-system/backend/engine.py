#!/usr/bin/env python3
"""
核心引擎模块: ASR + 翻译 + 增量修正管理
"""

import asyncio
import difflib
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Dict, List, Optional, Tuple

import numpy as np
import torch

logger = logging.getLogger(__name__)


# ============ 配置 ============

@dataclass
class EngineConfig:
    # ASR
    asr_model_path: str = "Qwen/Qwen3-ASR-1.7B"
    asr_gpu_memory_utilization: float = 0.6
    asr_max_new_tokens: int = 32

    # Streaming
    streaming_chunk_ms: int = 500
    streaming_chunk_num: int = 2
    streaming_token_num: int = 5
    streaming_chunk_size_sec: float = 2.0

    # VAD
    vad_threshold: float = 0.02
    vad_min_silence_ms: int = 400
    vad_min_speech_ms: int = 250

    # Translation
    translation_api_base: str = "http://localhost:8000/v1"
    translation_model: str = "default"
    translation_max_context: int = 3
    translation_temperature: float = 0.3
    translation_max_concurrent: int = 2

    # Segmentation
    sentence_end_punctuation = "。！？.!?；;"
    max_segment_duration_sec: float = 10.0


# ============ 状态定义 ============

class TextStatus(str, Enum):
    STREAMING = "streaming"    # 正在识别/翻译中
    CORRECTING = "correcting"  # 正在被修正
    CONFIRMED = "confirmed"    # 已确认


@dataclass
class TextSegment:
    """文本片段（句子级别）"""
    id: str
    chinese_text: str
    english_text: str = ""
    chinese_status: TextStatus = TextStatus.STREAMING
    english_status: TextStatus = TextStatus.STREAMING
    start_time: float = 0.0
    end_time: Optional[float] = None
    version: int = 0
    is_final: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "chinese_text": self.chinese_text,
            "english_text": self.english_text,
            "chinese_status": self.chinese_status.value,
            "english_status": self.english_status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "version": self.version,
            "is_final": self.is_final,
        }


@dataclass
class StreamingSession:
    """流式会话状态"""
    session_id: str
    asr_state: any = None
    segments: List[TextSegment] = field(default_factory=list)
    current_segment: Optional[TextSegment] = None
    audio_buffer: List[np.ndarray] = field(default_factory=list)
    buffer_start_time: float = 0.0
    is_listening: bool = False
    total_audio_processed: int = 0

    # 翻译相关
    confirmed_history: List[Dict[str, str]] = field(default_factory=list)
    pending_translation: Optional[asyncio.Task] = None
    translation_semaphore: asyncio.Semaphore = field(
        default_factory=lambda: asyncio.Semaphore(2)
    )

    # 统计
    stats: Dict = field(default_factory=lambda: {
        "asr_calls": 0,
        "translation_calls": 0,
        "corrections": 0,
        "start_time": time.time(),
    })


# ============ VAD 处理器 ============

class SileroVAD:
    """Silero VAD 语音活动检测"""

    def __init__(self, threshold: float = 0.5, min_silence_ms: int = 400):
        self.threshold = threshold
        self.min_silence_ms = min_silence_ms
        self.model = None
        self.utils = None
        self._initialized = False

    async def initialize(self):
        """加载 Silero VAD 模型"""
        if self._initialized:
            return
        try:
            import torch
            model, utils = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False,
                onnx=False,
            )
            self.model = model
            self.utils = utils
            self._initialized = True
            logger.info("Silero VAD 加载完成")
        except Exception as e:
            logger.warning(f"Silero VAD 加载失败，使用能量 VAD: {e}")
            self._initialized = False

    def is_speech(self, audio_chunk: np.ndarray, sample_rate: int = 16000) -> bool:
        """检测是否为语音"""
        if not self._initialized:
            # 降级为能量检测
            rms = np.sqrt(np.mean(audio_chunk ** 2))
            return rms > 0.02

        import torch
        tensor = torch.from_numpy(audio_chunk).float()
        if tensor.dim() == 1:
            tensor = tensor.unsqueeze(0)

        with torch.no_grad():
            speech_prob = self.model(tensor, sample_rate).item()

        return speech_prob > self.threshold


class EnergyVAD:
    """基于能量的简单 VAD"""

    def __init__(self, threshold: float = 0.02, min_silence_ms: int = 400):
        self.threshold = threshold
        self.min_silence_ms = min_silence_ms
        self.is_speaking = False
        self.silence_start = 0.0

    def process(self, audio_chunk: np.ndarray, timestamp_ms: float) -> dict:
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        is_speech = rms > self.threshold

        if is_speech:
            if not self.is_speaking:
                self.is_speaking = True
                return {"event": "speech_start", "timestamp_ms": timestamp_ms}
            return {"event": "speeching", "timestamp_ms": timestamp_ms}
        else:
            if self.is_speaking:
                silence_duration = timestamp_ms - self.silence_start
                if silence_duration >= self.min_silence_ms:
                    self.is_speaking = False
                    return {"event": "speech_end", "timestamp_ms": timestamp_ms}
                return {"event": "silence_in_speech", "timestamp_ms": timestamp_ms}
            self.silence_start = timestamp_ms
            return {"event": "silence", "timestamp_ms": timestamp_ms}

    def reset(self):
        self.is_speaking = False
        self.silence_start = 0.0


# ============ ASR 引擎 ============

class StreamingASREngine:
    """Qwen3-ASR 流式识别引擎"""

    def __init__(self, config: EngineConfig):
        self.config = config
        self.model = None
        self._ready = False

    async def initialize(self):
        """初始化 ASR 模型"""
        if self._ready:
            return

        logger.info(f"正在加载 ASR 模型: {self.config.asr_model_path}")
        try:
            from qwen_asr import Qwen3ASRModel

            self.model = Qwen3ASRModel.LLM(
                model=self.config.asr_model_path,
                gpu_memory_utilization=self.config.asr_gpu_memory_utilization,
                max_new_tokens=self.config.asr_max_new_tokens,
            )
            self._ready = True
            logger.info("ASR 模型加载完成")

        except ImportError:
            logger.error("未安装 qwen-asr 包，请执行: pip install qwen-asr[vllm]")
            raise
        except Exception as e:
            logger.error(f"ASR 模型加载失败: {e}")
            raise

    def create_state(self):
        """创建流式状态"""
        if not self._ready:
            raise RuntimeError("ASR 引擎未初始化")
        return self.model.init_streaming_state(
            unfixed_chunk_num=self.config.streaming_chunk_num,
            unfixed_token_num=self.config.streaming_token_num,
            chunk_size_sec=self.config.streaming_chunk_size_sec,
        )

    def process(self, audio: np.ndarray, state) -> str:
        """处理音频块"""
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        self.model.streaming_transcribe(audio, state)
        return state.text

    def finalize(self, state) -> str:
        """结束识别"""
        self.model.finish_streaming_transcribe(state)
        return state.text

    @property
    def is_ready(self) -> bool:
        return self._ready


# ============ 翻译引擎 ============

class StreamingTranslationEngine:
    """流式翻译引擎"""

    def __init__(self, config: EngineConfig):
        self.config = config
        self.client = None
        self._ready = False

    async def initialize(self):
        """初始化翻译客户端"""
        if self._ready:
            return

        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                base_url=self.config.translation_api_base,
                api_key="not-needed",
            )
            self._ready = True
            logger.info("翻译引擎初始化完成")
        except ImportError:
            logger.error("未安装 openai 包，请执行: pip install openai")
            raise

    async def translate(
        self,
        text: str,
        context: List[Dict[str, str]],
    ) -> AsyncIterator[str]:
        """流式翻译"""
        if not self._ready or not text.strip():
            yield text
            return

        system_msg = (
            "You are an expert conference interpreter. Translate Chinese to English. "
            "Maintain terminology consistency. Output ONLY the translation."
        )

        context_parts = []
        for ctx in context[-self.config.translation_max_context:]:
            context_parts.append(f"源: {ctx['chinese']}")
            context_parts.append(f"译: {ctx['english']}")

        context_str = "\n".join(context_parts)
        user_msg = f"{context_str}\n\n源: {text}\n译:"

        try:
            response = await self.client.chat.completions.create(
                model=self.config.translation_model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=self.config.translation_temperature,
                stream=True,
                max_tokens=256,
            )

            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"翻译请求失败: {e}")
            yield f"[翻译失败: {e}]"

    @property
    def is_ready(self) -> bool:
        return self._ready


# ============ 文本差异分析 ============

class TextDiffer:
    """文本差异分析器"""

    @staticmethod
    def compute_diff(old_text: str, new_text: str) -> List[dict]:
        """
        计算两个文本的差异
        Returns: [{"type": "equal|replace|insert|delete", "old": "...", "new": "..."}]
        """
        sm = difflib.SequenceMatcher(None, old_text, new_text)
        ops = []

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            ops.append({
                "type": tag,
                "old": old_text[i1:i2],
                "new": new_text[j1:j2],
            })

        return ops

    @staticmethod
    def find_word_boundaries(text: str, position: int) -> Tuple[int, int]:
        """找到位置所在词的边界"""
        # 向前找词首
        start = position
        while start > 0 and not text[start - 1].isspace():
            start -= 1

        # 向后找词尾
        end = position
        while end < len(text) and not text[end].isspace():
            end += 1

        return start, end


# ============ 句子切分器 ============

class SentenceSegmenter:
    """中文句子切分器"""

    SENTENCE_END = "。！？.!?；;"

    @classmethod
    def split(cls, text: str) -> List[str]:
        """切分句子"""
        sentences = []
        current = ""

        for char in text:
            current += char
            if char in cls.SENTENCE_END:
                stripped = current.strip()
                if stripped:
                    sentences.append(stripped)
                current = ""

        # 剩余部分
        remaining = current.strip()
        if remaining:
            sentences.append(remaining)

        return sentences if sentences else [text] if text.strip() else []

    @classmethod
    def is_sentence_end(cls, text: str) -> bool:
        """检查文本是否以句子结束符结尾"""
        if not text:
            return False
        return text[-1] in cls.SENTENCE_END


# ============ 增量修正管理器 ============

class CorrectionManager:
    """
    增量修正管理器
    负责管理 ASR 输出的增量修正和对应的翻译更新
    """

    def __init__(self):
        self.differ = TextDiffer()

    def detect_correction(
        self,
        segment: TextSegment,
        new_text: str,
    ) -> Optional[dict]:
        """
        检测修正
        Returns: None 如果没有变化，否则返回修正信息
        """
        old_text = segment.chinese_text
        if old_text == new_text:
            return None

        diff = self.differ.compute_diff(old_text, new_text)
        segment.chinese_text = new_text
        segment.version += 1

        return {
            "segment_id": segment.id,
            "old_text": old_text,
            "new_text": new_text,
            "diff": diff,
            "version": segment.version,
        }

    def should_retranslate(
        self,
        old_text: str,
        new_text: str,
    ) -> bool:
        """判断是否需要重新翻译"""
        if not old_text or not new_text:
            return True

        # 如果变化很小（仅修改了几个字符），可能需要重新翻译
        diff = self.differ.compute_diff(old_text, new_text)
        significant_changes = sum(
            1 for d in diff if d["type"] in ("replace", "insert", "delete")
        )
        return significant_changes > 0


# ============ 流式流水线 ============

class StreamingPipeline:
    """
    流式转录翻译流水线
    协调 ASR → 修正检测 → 翻译 → 输出 的完整流程
    """

    def __init__(self, config: EngineConfig = None):
        self.config = config or EngineConfig()
        self.asr = StreamingASREngine(self.config)
        self.translator = StreamingTranslationEngine(self.config)
        self.correction = CorrectionManager()
        self.vad = EnergyVAD(
            threshold=self.config.vad_threshold,
            min_silence_ms=self.config.vad_min_silence_ms,
        )

    async def initialize(self):
        """初始化所有引擎"""
        await self.asr.initialize()
        await self.translator.initialize()

    def create_session(self, session_id: str) -> StreamingSession:
        """创建新的流式会话"""
        return StreamingSession(
            session_id=session_id,
            asr_state=self.asr.create_state(),
            translation_semaphore=asyncio.Semaphore(
                self.config.translation_max_concurrent
            ),
        )

    async def process_audio(
        self,
        session: StreamingSession,
        audio_chunk: np.ndarray,
    ) -> Optional[dict]:
        """
        处理音频块
        Returns: 事件字典或 None
        """
        if not session.is_listening:
            return None

        # 累积音频
        session.audio_buffer.append(audio_chunk)
        buffer_duration_ms = len(session.audio_buffer) * 100  # 100ms chunks

        # 达到处理阈值
        if buffer_duration_ms < self.config.streaming_chunk_ms:
            return None

        # 合并音频
        audio_to_process = np.concatenate(session.audio_buffer)
        session.audio_buffer = []

        # ASR 识别
        try:
            current_text = self.asr.process(audio_to_process, session.asr_state)
            session.stats["asr_calls"] += 1
        except Exception as e:
            logger.error(f"ASR 处理失败: {e}")
            return {"type": "error", "message": f"ASR error: {e}"}

        if not current_text:
            return None

        # 初始化或更新 segment
        if session.current_segment is None:
            return await self._create_new_segment(session, current_text)

        # 检测修正
        if current_text != session.current_segment.chinese_text:
            return await self._handle_correction(session, current_text)

        return None

    async def _create_new_segment(
        self,
        session: StreamingSession,
        text: str,
    ) -> dict:
        """创建新 segment"""
        import uuid
        segment = TextSegment(
            id=str(uuid.uuid4())[:8],
            chinese_text=text,
            start_time=time.time(),
        )
        session.current_segment = segment
        session.segments.append(segment)

        return {
            "type": "asr.new_segment",
            "segment": segment.to_dict(),
        }

    async def _handle_correction(
        self,
        session: StreamingSession,
        new_text: str,
    ) -> dict:
        """处理增量修正"""
        segment = session.current_segment

        # 检测差异
        correction_info = self.correction.detect_correction(segment, new_text)
        session.stats["corrections"] += 1

        # 标记为修正中
        segment.chinese_status = TextStatus.CORRECTING

        # 触发翻译更新
        asyncio.create_task(self._update_translation(session))

        return {
            "type": "asr.correction",
            "correction": correction_info,
            "segment": segment.to_dict(),
        }

    async def _update_translation(self, session: StreamingSession):
        """更新翻译"""
        segment = session.current_segment
        if not segment or not segment.chinese_text.strip():
            return

        async with session.translation_semaphore:
            try:
                segment.english_status = TextStatus.STREAMING
                translated_parts = []

                async for chunk in self.translator.translate(
                    segment.chinese_text,
                    session.confirmed_history,
                ):
                    translated_parts.append(chunk)
                    segment.english_text = "".join(translated_parts)

                    # 这里可以通过回调发送流式翻译更新
                    # 实际实现中应该通过 WebSocket 发送

                segment.english_status = (
                    TextStatus.CONFIRMED if segment.is_final else TextStatus.STREAMING
                )
                session.stats["translation_calls"] += 1

            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"翻译失败: {e}")
                segment.english_text = f"[翻译失败]"

    async def finalize_segment(self, session: StreamingSession) -> dict:
        """结束当前 segment"""
        if not session.current_segment:
            return {"type": "no_active_segment"}

        segment = session.current_segment

        # 最终 ASR
        try:
            final_text = self.asr.finalize(session.asr_state)
            if final_text:
                segment.chinese_text = final_text
        except Exception as e:
            logger.error(f"最终 ASR 失败: {e}")

        # 确认 segment
        segment.is_final = True
        segment.chinese_status = TextStatus.CONFIRMED
        segment.end_time = time.time()

        # 完成翻译
        async with session.translation_semaphore:
            try:
                translated_parts = []
                async for chunk in self.translator.translate(
                    segment.chinese_text,
                    session.confirmed_history,
                ):
                    translated_parts.append(chunk)
                    segment.english_text = "".join(translated_parts)
                segment.english_status = TextStatus.CONFIRMED
            except Exception as e:
                logger.error(f"最终翻译失败: {e}")

        # 保存到历史
        session.confirmed_history.append({
            "chinese": segment.chinese_text,
            "english": segment.english_text,
        })

        result = {
            "type": "segment.finalized",
            "segment": segment.to_dict(),
        }

        # 重置当前 segment
        session.current_segment = None
        session.asr_state = self.asr.create_state()

        return result

    def get_session_stats(self, session: StreamingSession) -> dict:
        """获取会话统计"""
        duration = time.time() - session.stats["start_time"]
        return {
            "duration_sec": round(duration, 2),
            "asr_calls": session.stats["asr_calls"],
            "translation_calls": session.stats["translation_calls"],
            "corrections": session.stats["corrections"],
            "total_segments": len(session.segments),
            "confirmed_segments": len(session.confirmed_history),
        }
