#!/usr/bin/env python3
"""
实时语音转录翻译系统 - 后端服务
FastAPI + WebSocket + Qwen3-ASR + OpenAI Translation API
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Dict, List, Optional

import numpy as np
import torch
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ============ 配置常量 ============

class Config:
    # ASR 配置
    ASR_MODEL_PATH = "Qwen/Qwen3-ASR-1.7B"
    ASR_GPU_MEMORY_UTILIZATION = 0.6
    ASR_MAX_NEW_TOKENS = 32
    ASR_DTYPE = "bfloat16"

    # 流式配置
    STREAMING_CHUNK_MS = 500
    STREAMING_UNFIXED_CHUNK_NUM = 2
    STREAMING_UNFIXED_TOKEN_NUM = 5
    STREAMING_CHUNK_SIZE_SEC = 2.0

    # VAD 配置
    VAD_THRESHOLD = 0.5
    VAD_MIN_SILENCE_MS = 400
    VAD_MIN_SPEECH_MS = 250

    # 翻译配置
    TRANSLATION_API_BASE = "http://localhost:8000/v1"  # 替换为你的 LLM API 地址
    TRANSLATION_MODEL = "default"
    TRANSLATION_MAX_CONTEXT = 3
    TRANSLATION_TEMPERATURE = 0.3

    # WebSocket 配置
    WS_HEARTBEAT_INTERVAL = 30
    MAX_AUDIO_BUFFER_SEC = 30


# ============ 数据模型 ============

class SegmentStatus(str, Enum):
    PENDING = "pending"       # 识别中，可能变化
    CONFIRMED = "confirmed"   # 已确认（停顿后）
    CORRECTING = "correcting" # 正在被修正


@dataclass
class TranscriptSegment:
    id: str
    chinese_text: str
    english_text: str = ""
    status: SegmentStatus = SegmentStatus.PENDING
    start_time: float = 0.0
    end_time: Optional[float] = None
    version: int = 0  # 用于追踪修正版本

    def to_dict(self):
        return {
            "id": self.id,
            "chinese_text": self.chinese_text,
            "english_text": self.english_text,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "version": self.version,
        }


@dataclass
class SessionState:
    session_id: str
    asr_state: any = None  # Qwen3-ASR streaming state
    segments: List[TranscriptSegment] = field(default_factory=list)
    current_segment: Optional[TranscriptSegment] = None
    audio_buffer: List[np.ndarray] = field(default_factory=list)
    is_streaming: bool = False
    last_activity: float = 0.0
    silence_start: Optional[float] = None

    # 翻译相关
    translation_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    confirmed_segments_history: List[dict] = field(default_factory=list)
    pending_translation_task: Optional[asyncio.Task] = None


# ============ VAD 处理器 ============

class VADProcessor:
    """简单的基于能量的 VAD 处理器"""

    def __init__(self, threshold=0.02, min_silence_ms=400, min_speech_ms=250):
        self.threshold = threshold
        self.min_silence_ms = min_silence_ms
        self.min_speech_ms = min_speech_ms
        self.is_speaking = False
        self.speech_start_time = 0.0
        self.silence_start_time = 0.0
        self.speech_buffer: List[np.ndarray] = []

    def process(self, audio_chunk: np.ndarray, timestamp_ms: float) -> dict:
        """
        处理音频块，返回 VAD 事件
        Returns: {"event": "speech_start|speech_end|silence|speaking", "audio": optional}
        """
        # 计算 RMS 能量
        rms = np.sqrt(np.mean(audio_chunk ** 2))

        result = {"event": "silence", "audio": None}

        if rms > self.threshold:
            # 检测到语音
            if not self.is_speaking:
                # 语音开始
                self.is_speaking = True
                self.speech_start_time = timestamp_ms
                self.speech_buffer = [audio_chunk]
                result["event"] = "speech_start"
            else:
                # 持续语音
                self.speech_buffer.append(audio_chunk)
                result["event"] = "speaking"
            self.silence_start_time = timestamp_ms
        else:
            # 检测到静音
            if self.is_speaking:
                silence_duration = timestamp_ms - self.silence_start_time
                if silence_duration >= self.min_silence_ms:
                    # 语音结束
                    speech_duration = self.silence_start_time - self.speech_start_time
                    if speech_duration >= self.min_speech_ms:
                        # 合并语音缓冲区
                        speech_audio = np.concatenate(self.speech_buffer)
                        result = {
                            "event": "speech_end",
                            "audio": speech_audio,
                            "duration_ms": speech_duration,
                        }
                    self.is_speaking = False
                    self.speech_buffer = []
                else:
                    # 短暂静音，继续缓冲
                    self.speech_buffer.append(audio_chunk)
                    result["event"] = "speaking"
            else:
                result["event"] = "silence"

        return result

    def reset(self):
        self.is_speaking = False
        self.speech_buffer = []


# ============ ASR 引擎 ============

class ASREngine:
    """Qwen3-ASR 流式识别引擎"""

    def __init__(self):
        self.model = None
        self._initialized = False

    async def initialize(self):
        """异步初始化模型"""
        if self._initialized:
            return

        logger.info("正在加载 Qwen3-ASR-1.7B 模型...")
        try:
            from qwen_asr import Qwen3ASRModel

            # 使用 vLLM backend (流式推理必需)
            self.model = Qwen3ASRModel.LLM(
                model=Config.ASR_MODEL_PATH,
                gpu_memory_utilization=Config.ASR_GPU_MEMORY_UTILIZATION,
                max_new_tokens=Config.ASR_MAX_NEW_TOKENS,
            )
            self._initialized = True
            logger.info("Qwen3-ASR-1.7B 模型加载完成")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise

    def create_streaming_state(self):
        """创建新的流式识别状态"""
        if not self._initialized:
            raise RuntimeError("ASR 引擎未初始化")
        return self.model.init_streaming_state(
            unfixed_chunk_num=Config.STREAMING_UNFIXED_CHUNK_NUM,
            unfixed_token_num=Config.STREAMING_UNFIXED_TOKEN_NUM,
            chunk_size_sec=Config.STREAMING_CHUNK_SIZE_SEC,
        )

    def streaming_transcribe(self, audio_chunk: np.ndarray, state) -> str:
        """
        流式识别音频块
        Returns: 当前识别文本
        """
        # 确保音频是 float32
        if audio_chunk.dtype != np.float32:
            audio_chunk = audio_chunk.astype(np.float32)

        # 调用 Qwen3-ASR 流式推理
        self.model.streaming_transcribe(audio_chunk, state)
        return state.text

    def finish_streaming(self, state) -> str:
        """结束流式识别，获取最终结果"""
        self.model.finish_streaming_transcribe(state)
        return state.text


# ============ 翻译引擎 ============

class TranslationEngine:
    """基于 OpenAI 兼容 API 的流式翻译引擎"""

    def __init__(self):
        self.client = None
        self._initialized = False

    async def initialize(self):
        """初始化 OpenAI 客户端"""
        if self._initialized:
            return

        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                base_url=Config.TRANSLATION_API_BASE,
                api_key="not-needed",  # 本地部署不需要
            )
            self._initialized = True
            logger.info("翻译引擎初始化完成")
        except Exception as e:
            logger.error(f"翻译引擎初始化失败: {e}")
            raise

    def _build_prompt(self, text: str, context: List[dict]) -> str:
        """构建翻译提示词"""
        system_msg = (
            "You are a professional conference interpreter. "
            "Translate the following Chinese text into English. "
            "Maintain professional terminology consistency. "
            "Output ONLY the translation, no explanations."
        )

        context_str = ""
        if context:
            context_str = "Previous translations for context:\n"
            for ctx in context[-Config.TRANSLATION_MAX_CONTEXT:]:
                context_str += f"  中文: {ctx['chinese']}\n"
                context_str += f"  英文: {ctx['english']}\n"
            context_str += "\n"

        user_msg = f"{context_str}Translate:\n{text}"

        return system_msg, user_msg

    async def translate_streaming(
        self,
        text: str,
        context: List[dict],
    ) -> AsyncIterator[str]:
        """
        流式翻译
        Yields: 翻译文本片段
        """
        if not self._initialized:
            yield "[Translation engine not ready]"
            return

        system_msg, user_msg = self._build_prompt(text, context)

        try:
            response = await self.client.chat.completions.create(
                model=Config.TRANSLATION_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                temperature=Config.TRANSLATION_TEMPERATURE,
                stream=True,
            )

            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"翻译失败: {e}")
            yield f"[Translation error: {str(e)}]"


# ============ 会话管理器 ============

class SessionManager:
    """WebSocket 会话管理器"""

    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
        self.asr_engine = ASREngine()
        self.translation_engine = TranslationEngine()

    async def initialize(self):
        """初始化引擎"""
        await self.asr_engine.initialize()
        await self.translation_engine.initialize()

    def create_session(self, session_id: str) -> SessionState:
        """创建新会话"""
        session = SessionState(
            session_id=session_id,
            asr_state=self.asr_engine.create_streaming_state(),
            last_activity=time.time(),
        )
        self.sessions[session_id] = session
        logger.info(f"会话创建: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"会话移除: {session_id}")

    def update_activity(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id].last_activity = time.time()


# ============ WebSocket 事件处理器 ============

class EventType(str, Enum):
    # 客户端 → 服务端
    AUDIO_CHUNK = "audio.chunk"
    AUDIO_START = "audio.start"
    AUDIO_STOP = "audio.stop"
    CLIENT_CONFIG = "client.config"

    # 服务端 → 客户端
    ASR_PARTIAL = "asr.partial"
    ASR_FINAL = "asr.final"
    ASR_CORRECTION = "asr.correction"
    TRANSLATION_PARTIAL = "translation.partial"
    TRANSLATION_FINAL = "translation.final"
    TRANSLATION_CORRECTION = "translation.correction"
    STATUS = "status"
    ERROR = "error"


# ============ 全局实例 ============

app = FastAPI(title="实时语音转录翻译系统", version="1.0.0")
session_manager = SessionManager()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ API 路由 ============

@app.on_event("startup")
async def startup_event():
    """服务启动时初始化"""
    logger.info("正在初始化系统...")
    await session_manager.initialize()
    logger.info("系统初始化完成")


@app.get("/")
async def root():
    return {"message": "实时语音转录翻译系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "asr_ready": session_manager.asr_engine._initialized,
        "translation_ready": session_manager.translation_engine._initialized,
        "active_sessions": len(session_manager.sessions),
    }


# ============ WebSocket 路由 ============

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket 连接: {session_id}")

    # 创建会话
    session = session_manager.create_session(session_id)
    vad_processor = VADProcessor(
        threshold=Config.VAD_THRESHOLD,
        min_silence_ms=Config.VAD_MIN_SILENCE_MS,
        min_speech_ms=Config.VAD_MIN_SPEECH_MS,
    )

    # 启动翻译消费者
    translation_task = asyncio.create_task(
        translation_consumer(session, websocket)
    )

    try:
        while True:
            # 接收消息
            message = await websocket.receive()

            if "bytes" in message:
                # 二进制音频数据
                audio_bytes = message["bytes"]
                await handle_audio_chunk(
                    audio_bytes, session, vad_processor, websocket
                )

            elif "text" in message:
                # 文本控制消息
                data = json.loads(message["text"])
                await handle_control_message(data, session, vad_processor, websocket)

    except WebSocketDisconnect:
        logger.info(f"WebSocket 断开: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
    finally:
        # 清理
        if translation_task:
            translation_task.cancel()
        session_manager.remove_session(session_id)
        try:
            await websocket.close()
        except:
            pass


# ============ 消息处理器 ============

async def handle_audio_chunk(
    audio_bytes: bytes,
    session: SessionState,
    vad: VADProcessor,
    websocket: WebSocket,
):
    """处理音频块"""
    session_manager.update_activity(session.session_id)

    # 将 bytes 转换为 numpy 数组 (PCM16 → float32)
    audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

    # 累积到缓冲区
    session.audio_buffer.append(audio_array)

    # 每 500ms 触发一次 ASR
    buffer_duration_ms = len(session.audio_buffer) * 100  # 每个 chunk 100ms

    if buffer_duration_ms >= Config.STREAMING_CHUNK_MS:
        # 合并缓冲区
        audio_to_process = np.concatenate(session.audio_buffer)
        session.audio_buffer = []

        # 流式 ASR
        try:
            current_text = session_manager.asr_engine.streaming_transcribe(
                audio_to_process, session.asr_state
            )

            # 处理 ASR 结果
            await process_asr_result(current_text, session, websocket)

        except Exception as e:
            logger.error(f"ASR 处理错误: {e}")
            await send_event(websocket, EventType.ERROR, {"message": str(e)})


async def process_asr_result(
    current_text: str,
    session: SessionState,
    websocket: WebSocket,
):
    """处理 ASR 识别结果，检测增量修正"""
    if not current_text:
        return

    # 获取或创建当前 segment
    if session.current_segment is None:
        session.current_segment = TranscriptSegment(
            id=str(uuid.uuid4())[:8],
            chinese_text=current_text,
            start_time=time.time(),
        )
        session.segments.append(session.current_segment)

        # 发送新 segment
        await send_event(websocket, EventType.ASR_PARTIAL, {
            "segment": session.current_segment.to_dict(),
        })

    elif current_text != session.current_segment.chinese_text:
        # 检测到文本变化（增量修正）
        old_text = session.current_segment.chinese_text
        session.current_segment.chinese_text = current_text
        session.current_segment.status = SegmentStatus.CORRECTING
        session.current_segment.version += 1

        # 发送修正事件
        await send_event(websocket, EventType.ASR_CORRECTION, {
            "segment_id": session.current_segment.id,
            "old_text": old_text,
            "new_text": current_text,
            "segment": session.current_segment.to_dict(),
        })

        # 短暂后恢复为 PENDING
        await asyncio.sleep(0.5)
        session.current_segment.status = SegmentStatus.PENDING
        await send_event(websocket, EventType.ASR_PARTIAL, {
            "segment": session.current_segment.to_dict(),
        })

        # 触发翻译更新
        await trigger_translation(session)


async def handle_control_message(
    data: dict,
    session: SessionState,
    vad: VADProcessor,
    websocket: WebSocket,
):
    """处理控制消息"""
    msg_type = data.get("type", "")

    if msg_type == EventType.AUDIO_START:
        # 开始新的识别流
        session.is_streaming = True
        session.audio_buffer = []
        session.asr_state = session_manager.asr_engine.create_streaming_state()
        vad.reset()
        await send_event(websocket, EventType.STATUS, {
            "type": "listening",
            "message": "开始监听...",
        })

    elif msg_type == EventType.AUDIO_STOP:
        # 停止识别，确认当前 segment
        session.is_streaming = False

        # 处理剩余音频
        if session.audio_buffer:
            audio_to_process = np.concatenate(session.audio_buffer)
            session.audio_buffer = []
            try:
                final_text = session_manager.asr_engine.streaming_transcribe(
                    audio_to_process, session.asr_state
                )
                session_manager.asr_engine.finish_streaming(session.asr_state)

                if final_text and session.current_segment:
                    session.current_segment.chinese_text = final_text

            except Exception as e:
                logger.error(f"最终 ASR 处理错误: {e}")

        # 确认当前 segment
        if session.current_segment:
            session.current_segment.status = SegmentStatus.CONFIRMED
            session.current_segment.end_time = time.time()

            # 发送最终 ASR
            await send_event(websocket, EventType.ASR_FINAL, {
                "segment": session.current_segment.to_dict(),
            })

            # 触发翻译
            await trigger_translation(session, is_final=True)

            # 保存到历史
            session.confirmed_segments_history.append({
                "chinese": session.current_segment.chinese_text,
                "english": session.current_segment.english_text,
            })

            # 创建新 segment
            session.current_segment = None

    elif msg_type == EventType.CLIENT_CONFIG:
        # 客户端配置
        logger.info(f"客户端配置: {data}")


async def trigger_translation(session: SessionState, is_final: bool = False):
    """触发翻译任务"""
    if not session.current_segment:
        return

    # 取消之前的翻译任务
    if session.pending_translation_task and not session.pending_translation_task.done():
        session.pending_translation_task.cancel()

    # 创建新翻译任务
    session.pending_translation_task = asyncio.create_task(
        translate_segment(session, is_final)
    )


async def translate_segment(session: SessionState, is_final: bool):
    """执行翻译"""
    segment = session.current_segment
    if not segment or not segment.chinese_text:
        return

    try:
        translated_parts = []
        async for chunk in session_manager.translation_engine.translate_streaming(
            segment.chinese_text,
            session.confirmed_segments_history,
        ):
            translated_parts.append(chunk)
            partial_translation = "".join(translated_parts)

            # 更新 segment
            segment.english_text = partial_translation

            # 发送流式翻译
            await send_event_to_session(
                session,
                EventType.TRANSLATION_PARTIAL if not is_final else EventType.TRANSLATION_FINAL,
                {
                    "segment_id": segment.id,
                    "text": partial_translation,
                    "is_streaming": not is_final,
                }
            )

    except asyncio.CancelledError:
        # 翻译被取消（原文变化）
        pass
    except Exception as e:
        logger.error(f"翻译错误: {e}")


async def translation_consumer(session: SessionState, websocket: WebSocket):
    """翻译队列消费者"""
    try:
        while True:
            # 这里可以实现更复杂的队列逻辑
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass


# ============ 辅助函数 ============

async def send_event(websocket: WebSocket, event_type: EventType, data: dict):
    """发送事件到客户端"""
    try:
        await websocket.send_json({
            "type": event_type.value,
            "timestamp": time.time(),
            "data": data,
        })
    except Exception as e:
        logger.error(f"发送事件失败: {e}")


async def send_event_to_session(session: SessionState, event_type: EventType, data: dict):
    """发送事件到指定会话"""
    # 这里可以扩展为支持多客户端
    pass


# ============ 主入口 ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=False,
    )
