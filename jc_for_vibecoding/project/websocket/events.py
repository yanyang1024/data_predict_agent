import logging
import base64
import time
import numpy as np
from flask import request
from flask_socketio import SocketIO

logger = logging.getLogger(__name__)

# 客户端会话状态存储 (sid -> {buffer, is_streaming})
client_sessions = {}


def register_socketio_events(socketio, inference_engine, audio_processor,
                              stream_buffer_factory, subtitle_emitter,
                              config=None, llm_refiner=None):
    """注册所有 SocketIO 事件处理器。"""

    @socketio.on('connect')
    def handle_connect():
        client_id = request.sid
        logger.info(f"客户端连接: {client_id}")
        client_sessions[client_id] = {
            'buffer': None,
            'is_streaming': False
        }
        subtitle_emitter.emit_status(client_id, 'connected', 'ok', {'client_id': client_id})

    @socketio.on('disconnect')
    def handle_disconnect():
        client_id = request.sid
        logger.info(f"客户端断开: {client_id}")
        if client_id in client_sessions:
            del client_sessions[client_id]

    @socketio.on('start_stream')
    def handle_start_stream():
        client_id = request.sid
        logger.info(f"开始音频流: {client_id}")

        if client_id not in client_sessions:
            subtitle_emitter.emit_error(client_id, "会话不存在")
            return

        buffer = stream_buffer_factory()
        client_sessions[client_id]['buffer'] = buffer
        client_sessions[client_id]['is_streaming'] = True

        subtitle_emitter.emit_status(client_id, 'stream_started', 'ok')

    @socketio.on('audio_chunk')
    def handle_audio_chunk(data):
        client_id = request.sid

        if client_id not in client_sessions or not client_sessions[client_id].get('is_streaming'):
            return

        try:
            audio_bytes = base64.b64decode(data['data'])
            audio_array = np.frombuffer(audio_bytes, dtype=np.float32)

            if len(audio_array) == 0:
                return

            processed_audio = audio_processor.from_float32_array(audio_array)

            buffer = client_sessions[client_id]['buffer']
            segments = buffer.push(processed_audio)

            for seg in segments:
                _process_segment(client_id, seg)

        except Exception as e:
            logger.error(f"处理音频 chunk 失败: {e}")
            subtitle_emitter.emit_error(client_id, f"音频处理错误: {str(e)}")

    @socketio.on('stop_stream')
    def handle_stop_stream():
        client_id = request.sid
        logger.info(f"停止音频流: {client_id}")

        if client_id not in client_sessions:
            subtitle_emitter.emit_status(client_id, 'stream_stopped', 'ok')
            return

        client_sessions[client_id]['is_streaming'] = False

        buffer = client_sessions[client_id]['buffer']
        if buffer:
            segments = buffer.flush()
            final_texts = []
            for seg in segments:
                text = _process_segment_sync(client_id, seg, skip_llm=True)
                if text:
                    final_texts.append(text)
            buffer.reset()

            final_text = ' '.join(final_texts) if final_texts else ''
            subtitle_emitter.emit_status(client_id, 'stream_stopped', 'ok', {'final_text': final_text})
        else:
            subtitle_emitter.emit_status(client_id, 'stream_stopped', 'ok')

    def _process_segment(client_id, segment):
        """异步处理语音段（在线程中推理）。"""
        import threading
        thread = threading.Thread(target=_process_segment_sync, args=(client_id, segment))
        thread.daemon = True
        thread.start()

    def _process_segment_sync(client_id, segment, skip_llm=False):
        """同步处理语音段：SeamlessM4T → init → (LLM refine → tokens) → done."""
        seg_id = segment.id
        audio = segment.audio
        timestamp = int(time.time() * 1000)

        try:
            # 1) 通知前端新段开始
            subtitle_emitter.emit_segment_start(client_id, seg_id, timestamp)

            # 2) SeamlessM4T 初译
            raw_text = inference_engine.infer(audio)
            subtitle_emitter.emit_initial_translation(client_id, seg_id, raw_text)

            # 3) LLM 精炼（异步流式）
            if not skip_llm and config and config.LLM_ENABLED and llm_refiner and raw_text:
                def on_token(_, token):
                    subtitle_emitter.emit_stream_token(client_id, seg_id, token)

                def on_corrections(_, corrections):
                    for corr in corrections:
                        subtitle_emitter.emit_correction(
                            client_id,
                            corr['segment_id'],
                            corr['corrected_text'],
                        )

                def on_done(_):
                    subtitle_emitter.emit_stream_end(client_id, seg_id)

                llm_refiner.refine(
                    segment_id=seg_id,
                    raw_en_text=raw_text,
                    timestamp=timestamp,
                    on_token=on_token,
                    on_corrections=on_corrections,
                    on_done=on_done,
                )
            else:
                # 无 LLM → 直接结束
                subtitle_emitter.emit_stream_end(client_id, seg_id)

            return raw_text

        except Exception as e:
            logger.error(f"处理语音段失败: {e}")
            subtitle_emitter.emit_error(client_id, f"处理错误: {str(e)}")
            subtitle_emitter.emit_stream_end(client_id, seg_id)
            return ""
