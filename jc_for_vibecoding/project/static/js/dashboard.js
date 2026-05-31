/**
 * Dashboard 主控制器
 * 管理段生命周期: pending → initial → refining → final / corrected
 */
class Dashboard {
    constructor() {
        this.audioCapture = null;
        this.wsClient = null;
        this.isStreaming = false;
        this.segments = new Map();
        this.currentSegmentId = null;
        this.maxHistoryItems = 50;

        this.init();
    }

    init() {
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.currentEl = document.getElementById('currentSubtitle');
        this.historyEl = document.getElementById('subtitleHistory');
        this.statusDot = document.getElementById('statusDot');
        this.statusLabel = document.getElementById('statusLabel');
        this.streamingStatus = document.getElementById('streamingStatus');
        this.audioMeter = document.getElementById('audioMeter');

        this.startBtn.addEventListener('click', () => this.startStreaming());
        this.stopBtn.addEventListener('click', () => this.stopStreaming());

        this.initWebSocket();
    }

    initWebSocket() {
        this.wsClient = new WebSocketClient({
            onConnect: () => this.onConnected(),
            onDisconnect: () => this.onDisconnected(),
            onError: (msg) => this.onError(msg),
            onStreamStarted: () => this.onStreamStarted(),
            onStreamStopped: (data) => this.onStreamStopped(data),
            onSegmentStart: (data) => this.onSegmentStart(data),
            onInitialTranslation: (data) => this.onInitialTranslation(data),
            onStreamToken: (data) => this.onStreamToken(data),
            onStreamEnd: (data) => this.onStreamEnd(data),
            onCorrection: (data) => this.onCorrection(data),
        });
        this.wsClient.connect();
    }

    // ─── 连接状态 ─────────────────────────────────

    onConnected() {
        this.statusDot.classList.add('connected');
        this.statusDot.classList.remove('disconnected');
        this.statusLabel.textContent = '已连接';
        this.startBtn.disabled = false;
    }

    onDisconnected() {
        this.statusDot.classList.remove('connected');
        this.statusDot.classList.add('disconnected');
        this.statusLabel.textContent = '已断开';
        this.startBtn.disabled = true;
        this.stopBtn.disabled = true;

        if (this.isStreaming) {
            this.stopStreaming();
        }
    }

    // ─── 流控制 ───────────────────────────────────

    async startStreaming() {
        this.audioCapture = new AudioCapture({
            onChunk: (base64, timestamp) => {
                this.wsClient.sendAudioChunk(base64, timestamp);
            },
            onVolumeChange: (volume) => {
                this.updateAudioMeter(volume);
            },
            onError: (error) => {
                this.onError('麦克风权限被拒绝: ' + error.message);
            }
        });

        const success = await this.audioCapture.start();
        if (!success) {
            this.onError('无法启动麦克风');
            return;
        }
        this.wsClient.startStream();
    }

    onStreamStarted() {
        this.isStreaming = true;
        this.startBtn.disabled = true;
        this.stopBtn.disabled = false;
        this.streamingStatus.style.display = 'flex';
        this.currentEl.innerHTML = '<span class="hint">聆听中...</span>';
    }

    stopStreaming() {
        if (this.audioCapture) {
            this.audioCapture.stop();
            this.audioCapture = null;
        }
        this.wsClient.stopStream();
        this.isStreaming = false;
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
        this.streamingStatus.style.display = 'none';
        this.audioMeter.style.width = '0%';
    }

    onStreamStopped(data) {
        this.isStreaming = false;
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
        this.streamingStatus.style.display = 'none';
        this.audioMeter.style.width = '0%';
    }

    // ─── 段生命周期 ───────────────────────────────

    onSegmentStart(data) {
        if (this.currentSegmentId) {
            this._moveToHistory(this.currentSegmentId);
        }
        const seg = {
            id: data.segment_id,
            timestamp: data.timestamp,
            text: '',
            status: 'pending',
        };
        this.segments.set(data.segment_id, seg);
        this.currentSegmentId = data.segment_id;
        this._renderCurrent();
    }

    onInitialTranslation(data) {
        const seg = this.segments.get(data.segment_id);
        if (!seg) return;
        seg.text = data.text || '…';
        seg.status = 'initial';
        this._renderCurrent();
    }

    onStreamToken(data) {
        const seg = this.segments.get(data.segment_id);
        if (!seg) return;

        if (seg.status === 'initial' || seg.status === 'pending') {
            seg.text = '';
            seg.status = 'refining';
        }
        seg.text += data.token;
        this._renderCurrent();
    }

    onStreamEnd(data) {
        const seg = this.segments.get(data.segment_id);
        if (!seg) return;
        seg.status = 'final';
        this._renderCurrent();
    }

    onCorrection(data) {
        const seg = this.segments.get(data.segment_id);
        if (!seg) return;
        seg.text = data.corrected_text;
        seg.status = 'corrected';
        this._updateHistoryItem(data.segment_id);
    }

    // ─── 渲染 ─────────────────────────────────────

    _renderCurrent() {
        const seg = this.segments.get(this.currentSegmentId);
        if (!seg) {
            this.currentEl.innerHTML = this.isStreaming
                ? '<span class="hint">聆听中...</span>'
                : '<span class="hint">点击「开始采集」启动实时翻译</span>';
            return;
        }

        const badge = this._badgeHtml(seg.status);
        const timeStr = this._formatTime(seg.timestamp);
        const escapedText = this.escapeHtml(seg.text || (seg.status === 'pending' ? '...' : ''));
        const cursor = seg.status === 'refining' ? '<span class="cursor">▊</span>' : '';

        this.currentEl.innerHTML = `
            <div class="current-segment">
                <div class="segment-header">
                    <span class="segment-time">${timeStr}</span>
                    ${badge}
                </div>
                <div class="segment-text ${seg.status}">${escapedText}${cursor}</div>
            </div>
        `;
    }

    _renderHistory() {
        let html = '';
        for (const [id, seg] of this.segments) {
            if (id === this.currentSegmentId) continue;
            if (!seg.text || seg.text === '…') continue;

            const timeStr = this._formatTime(seg.timestamp);
            const badge = seg.status === 'corrected'
                ? '<span class="history-badge corrected">✏</span>'
                : '';

            html += `
                <div class="history-item ${seg.status === 'corrected' ? 'is-corrected' : ''}"
                     data-segment-id="${id}">
                    <span class="history-time">${timeStr}</span>
                    <span class="history-text">${this.escapeHtml(seg.text)}</span>
                    ${badge}
                </div>
            `;
        }
        this.historyEl.innerHTML = html;
        this.historyEl.scrollTop = this.historyEl.scrollHeight;
    }

    _moveToHistory(segmentId) {
        const seg = this.segments.get(segmentId);
        if (!seg) return;
        if (seg.status === 'pending' || seg.status === 'initial') {
            seg.status = 'final';
        }
        this._renderHistory();
        this.currentSegmentId = null;
    }

    _updateHistoryItem(segmentId) {
        const item = this.historyEl.querySelector(`[data-segment-id="${segmentId}"]`);
        if (!item) {
            this._renderHistory();
            return;
        }
        const seg = this.segments.get(segmentId);
        if (!seg) return;

        const textEl = item.querySelector('.history-text');
        if (textEl) textEl.textContent = seg.text;

        item.classList.add('is-corrected');
        let badge = item.querySelector('.history-badge');
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'history-badge corrected';
            badge.textContent = '✏';
            item.appendChild(badge);
        }
    }

    // ─── 工具方法 ────────────────────────────────

    _badgeHtml(status) {
        switch (status) {
            case 'pending':   return '<span class="badge pending">⋯</span>';
            case 'initial':   return '<span class="badge fast">fast</span>';
            case 'refining':  return '<span class="badge refining">refining</span>';
            case 'final':     return '<span class="badge final">✓</span>';
            case 'corrected': return '<span class="badge corrected">✏ corrected</span>';
            default:          return '';
        }
    }

    _formatTime(timestamp) {
        const d = new Date(timestamp);
        return d.toLocaleTimeString('zh-CN', { hour12: false });
    }

    updateAudioMeter(volume) {
        const percentage = Math.min(volume * 100, 100);
        this.audioMeter.style.width = percentage + '%';
    }

    onError(message) {
        console.error('Dashboard 错误:', message);
        this.statusLabel.textContent = '错误: ' + message;
        this.statusDot.classList.remove('connected');
        this.statusDot.classList.add('disconnected');

        setTimeout(() => {
            if (this.wsClient.isConnected) {
                this.statusLabel.textContent = '已连接';
                this.statusDot.classList.add('connected');
                this.statusDot.classList.remove('disconnected');
            }
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});
