#!/usr/bin/env python3
"""
FastAPI WebSocket 服务器
"""

import asyncio
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager

import numpy as np
import uvicorn
from engine import (
    CorrectionManager,
    EngineConfig,
    SentenceSegmenter,
    StreamingPipeline,
    StreamingSession,
    TextDiffer,
    TextStatus,
)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

# ============ 全局状态 ============

pipeline: StreamingPipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global pipeline

    # 启动时初始化
    logger.info("=" * 60)
    logger.info("实时语音转录翻译系统启动中...")
    logger.info("=" * 60)

    config = EngineConfig()
    pipeline = StreamingPipeline(config)
    await pipeline.initialize()

    logger.info("系统就绪，等待连接...")
    yield

    # 关闭时清理
    logger.info("系统关闭中...")


# ============ FastAPI 应用 ============

app = FastAPI(
    title="实时语音转录翻译系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
import os

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ============ HTTP 路由 ============

@app.get("/")
async def root():
    return {
        "name": "实时语音转录翻译系统",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/ws/{session_id}",
            "health": "/health",
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "asr_ready": pipeline.asr.is_ready if pipeline else False,
        "translation_ready": pipeline.translator.is_ready if pipeline else False,
        "timestamp": time.time(),
    }


@app.get("/dashboard")
async def dashboard():
    """返回 Dashboard 页面"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Dashboard not built yet"}


# ============ WebSocket 路由 ============

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"[Session:{session_id}] WebSocket 连接已建立")

    # 创建会话
    session = pipeline.create_session(session_id)

    # 启动心跳和翻译消费者
    heartbeat_task = asyncio.create_task(heartbeat_loop(websocket, session))
    translation_queue = asyncio.Queue()
    translation_task = asyncio.create_task(
        translation_consumer(websocket, session, translation_queue)
    )

    # 当前处理的音频时间戳
    audio_timestamp_ms = 0

    try:
        while True:
            message = await websocket.receive()

            if "bytes" in message:
                # 二进制音频数据 (PCM16, 16kHz, mono)
                audio_bytes = message["bytes"]
                audio_array = (
                    np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
                    / 32768.0
                )

                if not session.is_listening:
                    continue

                # 更新 VAD
                vad_result = pipeline.vad.process(audio_array, audio_timestamp_ms)
                audio_timestamp_ms += 100  # 每个 chunk 100ms

                # 处理音频
                result = await pipeline.process_audio(session, audio_array)

                if result:
                    await websocket.send_json(result)

                    # 如果有新的 ASR 内容，触发翻译
                    if result["type"] in ("asr.new_segment", "asr.correction"):
                        await translation_queue.put({
                            "action": "translate",
                            "segment_id": result["segment"]["id"],
                        })

                # 检测语音结束
                if vad_result["event"] == "speech_end":
                    pass  # 可以在语音结束时触发 segment 确认

            elif "text" in message:
                # 文本控制消息
                data = json.loads(message["text"])
                await handle_control_message(
                    websocket, session, translation_queue, data
                )

    except WebSocketDisconnect:
        logger.info(f"[Session:{session_id}] WebSocket 断开")
    except Exception as e:
        logger.error(f"[Session:{session_id}] 错误: {e}")
    finally:
        # 清理
        heartbeat_task.cancel()
        translation_task.cancel()

        # 输出统计
        stats = pipeline.get_session_stats(session)
        logger.info(f"[Session:{session_id}] 会话统计: {stats}")

        try:
            await websocket.close()
        except:
            pass


async def handle_control_message(
    websocket: WebSocket,
    session: StreamingSession,
    translation_queue: asyncio.Queue,
    data: dict,
):
    """处理控制消息"""
    msg_type = data.get("type", "")

    if msg_type == "audio.start":
        # 开始监听
        session.is_listening = True
        session.audio_buffer = []
        session.asr_state = pipeline.asr.create_state()
        pipeline.vad.reset()

        await websocket.send_json({
            "type": "status",
            "status": "listening",
            "message": "开始监听",
        })
        logger.info(f"[Session:{session.session_id}] 开始监听")

    elif msg_type == "audio.stop":
        # 停止监听，确认当前 segment
        session.is_listening = False

        result = await pipeline.finalize_segment(session)
        await websocket.send_json(result)

        await websocket.send_json({
            "type": "status",
            "status": "idle",
            "message": "监听已停止",
        })

    elif msg_type == "segment.confirm":
        # 手动确认当前 segment
        if session.current_segment:
            result = await pipeline.finalize_segment(session)
            await websocket.send_json(result)

    elif msg_type == "config":
        # 更新配置
        logger.info(f"[Session:{session.session_id}] 配置更新: {data}")

    elif msg_type == "ping":
        await websocket.send_json({"type": "pong", "timestamp": time.time()})


async def heartbeat_loop(websocket: WebSocket, session: StreamingSession):
    """心跳循环"""
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": time.time(),
            })
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"心跳错误: {e}")


async def translation_consumer(
    websocket: WebSocket,
    session: StreamingSession,
    queue: asyncio.Queue,
):
    """翻译消费者 - 处理翻译队列"""
    try:
        while True:
            item = await queue.get()

            if item["action"] == "translate":
                segment_id = item["segment_id"]

                # 找到对应 segment
                segment = None
                if session.current_segment and session.current_segment.id == segment_id:
                    segment = session.current_segment

                if not segment:
                    continue

                # 执行翻译
                async with session.translation_semaphore:
                    try:
                        segment.english_status = TextStatus.STREAMING
                        translated_parts = []

                        async for chunk in pipeline.translator.translate(
                            segment.chinese_text,
                            session.confirmed_history,
                        ):
                            translated_parts.append(chunk)
                            segment.english_text = "".join(translated_parts)

                            # 发送流式翻译更新
                            await websocket.send_json({
                                "type": "translation.streaming",
                                "segment_id": segment.id,
                                "text": segment.english_text,
                                "is_final": False,
                            })

                        # 最终翻译
                        if not segment.is_final:
                            segment.english_status = TextStatus.STREAMING
                        else:
                            segment.english_status = TextStatus.CONFIRMED

                        await websocket.send_json({
                            "type": "translation.final",
                            "segment_id": segment.id,
                            "text": segment.english_text,
                        })

                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        logger.error(f"翻译消费者错误: {e}")

    except asyncio.CancelledError:
        pass


# ============ 启动入口 ============

def main():
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=False,
        workers=1,
    )


if __name__ == "__main__":
    main()
