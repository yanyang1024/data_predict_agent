/**
 * WebSocket 客户端类
 * 使用 Socket.IO 与 Flask 后端通信
 */
class WebSocketClient {
    constructor(options = {}) {
        this.serverUrl = options.serverUrl || window.location.origin;
        this.onConnect = options.onConnect || (() => {});
        this.onDisconnect = options.onDisconnect || (() => {});
        this.onSubtitle = options.onSubtitle || (() => {});
        this.onError = options.onError || (() => {});
        this.onStreamStarted = options.onStreamStarted || (() => {});
        this.onStreamStopped = options.onStreamStopped || (() => {});
        this.onSegmentStart = options.onSegmentStart || (() => {});
        this.onInitialTranslation = options.onInitialTranslation || (() => {});
        this.onStreamToken = options.onStreamToken || (() => {});
        this.onStreamEnd = options.onStreamEnd || (() => {});
        this.onCorrection = options.onCorrection || (() => {});

        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        this.socket = io(this.serverUrl, {
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: this.maxReconnectAttempts,
            reconnectionDelay: 1000
        });

        this.socket.on('connect', () => {
            console.log('WebSocket 已连接');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.onConnect();
        });

        this.socket.on('disconnect', () => {
            console.log('WebSocket 已断开');
            this.isConnected = false;
            this.onDisconnect();
        });

        this.socket.on('connected', (data) => {
            console.log('连接确认:', data);
        });

        this.socket.on('stream_started', (data) => {
            console.log('流已开始:', data);
            this.onStreamStarted(data);
        });

        this.socket.on('stream_stopped', (data) => {
            console.log('流已停止:', data);
            this.onStreamStopped(data);
        });

        this.socket.on('segment_start', (data) => {
            console.log('语音段开始:', data);
            this.onSegmentStart(data);
        });

        this.socket.on('initial_translation', (data) => {
            console.log('初译完成:', data);
            this.onInitialTranslation(data);
        });

        this.socket.on('stream_token', (data) => {
            this.onStreamToken(data);
        });

        this.socket.on('stream_end', (data) => {
            console.log('精炼完成:', data);
            this.onStreamEnd(data);
        });

        this.socket.on('correction', (data) => {
            console.log('修正:', data);
            this.onCorrection(data);
        });

        this.socket.on('subtitle', (data) => {
            console.log('收到字幕:', data);
            this.onSubtitle(data);
        });

        this.socket.on('error', (data) => {
            console.error('服务器错误:', data);
            this.onError(data.message);
        });

        this.socket.on('connect_error', (error) => {
            console.error('连接错误:', error);
            this.reconnectAttempts++;
            if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                this.onError('连接服务器失败，请检查网络');
            }
        });
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }

    startStream() {
        if (!this.isConnected) return false;
        this.socket.emit('start_stream');
        return true;
    }

    sendAudioChunk(base64Data, timestamp) {
        if (!this.isConnected) return false;
        this.socket.emit('audio_chunk', {
            data: base64Data,
            timestamp: timestamp
        });
        return true;
    }

    stopStream() {
        if (!this.isConnected) return false;
        this.socket.emit('stop_stream');
        return true;
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketClient;
}
