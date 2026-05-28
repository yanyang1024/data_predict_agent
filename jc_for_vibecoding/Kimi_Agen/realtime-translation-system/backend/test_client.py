#!/usr/bin/env python3
"""
测试客户端 - 用于测试 WebSocket 连接和音频传输
支持麦克风输入和音频文件播放
"""

import argparse
import asyncio
import json
import logging
import struct
import time
from typing import Optional

import numpy as np
import soundfile as sf
import websockets

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


class TestClient:
    """WebSocket 测试客户端"""

    def __init__(self, uri: str, audio_file: Optional[str] = None):
        self.uri = uri
        self.audio_file = audio_file
        self.ws = None
        self.stats = {
            "messages_received": 0,
            "audio_sent_sec": 0,
            "start_time": None,
        }

    async def connect(self):
        """连接 WebSocket"""
        logger.info(f"连接到 {self.uri}")
        self.ws = await websockets.connect(self.uri)
        self.stats["start_time"] = time.time()
        logger.info("WebSocket 已连接")

    async def send_audio_start(self):
        """发送开始命令"""
        await self.ws.send(json.dumps({"type": "audio.start"}))
        logger.info("发送 audio.start")

    async def send_audio_stop(self):
        """发送停止命令"""
        await self.ws.send(json.dumps({"type": "audio.stop"}))
        logger.info("发送 audio.stop")

    async def send_audio_file(self):
        """发送音频文件"""
        if not self.audio_file:
            logger.warning("未指定音频文件")
            return

        # 读取音频文件
        data, samplerate = sf.read(self.audio_file, dtype="float32")

        # 重采样到 16kHz (如果需要)
        if samplerate != 16000:
            import librosa

            data = librosa.resample(data, orig_sr=samplerate, target_sr=16000)

        # 转换为 mono
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)

        # 转换为 PCM16
        pcm_data = (data * 32768).astype(np.int16)

        # 分块发送 (每块 100ms = 1600 samples)
        chunk_size = 1600
        total_samples = len(pcm_data)
        chunks_sent = 0

        logger.info(f"发送音频: {total_samples / 16000:.1f}秒, {total_samples} samples")

        for i in range(0, total_samples, chunk_size):
            chunk = pcm_data[i : i + chunk_size]

            # 确保 chunk 是完整的
            if len(chunk) < chunk_size:
                chunk = np.pad(chunk, (0, chunk_size - len(chunk)))

            # 发送二进制数据
            await self.ws.send(chunk.tobytes())

            chunks_sent += 1
            self.stats["audio_sent_sec"] = chunks_sent * 0.1

            # 模拟实时录音间隔
            await asyncio.sleep(0.1)

            # 每 5 秒打印一次进度
            if chunks_sent % 50 == 0:
                logger.info(f"发送进度: {self.stats['audio_sent_sec']:.1f}s")

        logger.info(f"音频发送完成: {chunks_sent} chunks")

    async def send_microphone(self):
        """从麦克风发送音频 (需要 sounddevice)"""
        try:
            import sounddevice as sd
        except ImportError:
            logger.error("请安装 sounddevice: pip install sounddevice")
            return

        logger.info("开始录音，按 Ctrl+C 停止...")

        chunk_duration = 0.1  # 100ms
        samplerate = 16000
        chunk_samples = int(samplerate * chunk_duration)

        # 开始录音
        stream = sd.InputStream(
            samplerate=samplerate,
            channels=1,
            dtype=np.int16,
            blocksize=chunk_samples,
        )
        stream.start()

        try:
            while True:
                # 读取音频块
                chunk, overflowed = stream.read(chunk_samples)
                if overflowed:
                    logger.warning("音频缓冲区溢出")

                # 发送
                await self.ws.send(chunk.tobytes())
                self.stats["audio_sent_sec"] += chunk_duration

        except KeyboardInterrupt:
            logger.info("录音停止")
        finally:
            stream.stop()
            stream.close()

    async def receive_messages(self):
        """接收服务端消息"""
        try:
            async for message in self.ws:
                if isinstance(message, bytes):
                    logger.info(f"收到二进制数据: {len(message)} bytes")
                else:
                    data = json.loads(message)
                    await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info("连接已关闭")

    async def handle_message(self, data: dict):
        """处理收到的消息"""
        self.stats["messages_received"] += 1
        msg_type = data.get("type", "")

        if msg_type == "asr.new_segment":
            segment = data.get("segment", {})
            logger.info(f"[ASR] 新句子: {segment.get('chinese_text', '')}")

        elif msg_type == "asr.correction":
            correction = data.get("correction", {})
            logger.info(
                f"[ASR] 修正: '{correction.get('old_text', '')}' -> "
                f"'{correction.get('new_text', '')}'"
            )

        elif msg_type == "segment.finalized":
            segment = data.get("segment", {})
            logger.info(f"[ASR] 确认: {segment.get('chinese_text', '')}")
            logger.info(f"[Translation] 翻译: {segment.get('english_text', '')}")

        elif msg_type == "translation.streaming":
            # 流式翻译更新，减少日志
            pass

        elif msg_type == "translation.final":
            logger.info(f"[Translation] 完成: {data.get('text', '')}")

        elif msg_type == "status":
            logger.info(f"[Status] {data.get('status', '')}: {data.get('message', '')}")

        elif msg_type == "heartbeat":
            pass  # 忽略心跳

        else:
            logger.debug(f"收到消息: {data}")

    async def run(self):
        """运行测试"""
        await self.connect()

        # 启动接收任务
        receive_task = asyncio.create_task(self.receive_messages())

        # 发送开始命令
        await self.send_audio_start()

        # 发送音频
        if self.audio_file:
            await self.send_audio_file()
        else:
            await self.send_microphone()

        # 发送停止命令
        await self.send_audio_stop()

        # 等待一段时间接收最终结果
        await asyncio.sleep(3)

        # 关闭连接
        await self.ws.close()
        receive_task.cancel()

        # 打印统计
        duration = time.time() - self.stats["start_time"]
        logger.info("=" * 50)
        logger.info("测试完成!")
        logger.info(f"运行时间: {duration:.1f}s")
        logger.info(f"音频发送: {self.stats['audio_sent_sec']:.1f}s")
        logger.info(f"消息接收: {self.stats['messages_received']}")
        logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="实时转录翻译测试客户端")
    parser.add_argument(
        "--server",
        default="localhost:8080",
        help="服务器地址 (默认: localhost:8080)",
    )
    parser.add_argument(
        "--session",
        default=f"test_{int(time.time())}",
        help="会话 ID",
    )
    parser.add_argument(
        "--audio",
        default=None,
        help="音频文件路径 (不指定则使用麦克风)",
    )
    parser.add_argument(
        "--mic",
        action="store_true",
        help="使用麦克风输入",
    )

    args = parser.parse_args()

    # 构建 WebSocket URI
    ws_uri = f"ws://{args.server}/ws/{args.session}"

    # 运行客户端
    client = TestClient(ws_uri, audio_file=args.audio)
    asyncio.run(client.run())


if __name__ == "__main__":
    main()
