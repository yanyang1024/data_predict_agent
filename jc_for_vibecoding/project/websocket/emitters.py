import logging
import time
from flask_socketio import SocketIO

logger = logging.getLogger(__name__)


class SubtitleEmitter:
    """管理向客户端推送字幕。"""

    def __init__(self, socketio: SocketIO):
        self.socketio = socketio

    def emit_subtitle(self, client_id: str, text: str, timestamp: int = None, is_final: bool = True):
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        try:
            self.socketio.emit('subtitle', {
                'text': text,
                'timestamp': timestamp,
                'is_final': is_final
            }, room=client_id)
        except Exception as e:
            logger.error(f"推送字幕失败: {e}")

    def emit_error(self, client_id: str, message: str):
        try:
            self.socketio.emit('error', {'message': message}, room=client_id)
        except Exception as e:
            logger.error(f"推送错误失败: {e}")

    def emit_status(self, client_id: str, event: str, status: str, extra: dict = None):
        payload = {'status': status}
        if extra:
            payload.update(extra)
        try:
            self.socketio.emit(event, payload, room=client_id)
        except Exception as e:
            logger.error(f"推送状态失败: {e}")

    def emit_segment_start(self, client_id: str, segment_id: str, timestamp: int):
        try:
            self.socketio.emit('segment_start', {
                'segment_id': segment_id,
                'timestamp': timestamp,
            }, room=client_id)
        except Exception as e:
            logger.error(f"推送 segment_start 失败: {e}")

    def emit_initial_translation(self, client_id: str, segment_id: str, text: str):
        try:
            self.socketio.emit('initial_translation', {
                'segment_id': segment_id,
                'text': text,
            }, room=client_id)
        except Exception as e:
            logger.error(f"推送 initial_translation 失败: {e}")

    def emit_stream_token(self, client_id: str, segment_id: str, token: str):
        try:
            self.socketio.emit('stream_token', {
                'segment_id': segment_id,
                'token': token,
            }, room=client_id)
        except Exception as e:
            logger.error(f"推送 stream_token 失败: {e}")

    def emit_stream_end(self, client_id: str, segment_id: str):
        try:
            self.socketio.emit('stream_end', {
                'segment_id': segment_id,
            }, room=client_id)
        except Exception as e:
            logger.error(f"推送 stream_end 失败: {e}")

    def emit_correction(self, client_id: str, segment_id: str, corrected_text: str):
        try:
            self.socketio.emit('correction', {
                'segment_id': segment_id,
                'corrected_text': corrected_text,
            }, room=client_id)
        except Exception as e:
            logger.error(f"推送 correction 失败: {e}")
