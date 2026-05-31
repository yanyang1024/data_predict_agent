/**
 * 音频采集类
 * 使用 getUserMedia + AudioContext 采集麦克风音频
 */
class AudioCapture {
    constructor(options = {}) {
        this.sampleRate = options.sampleRate || 16000;
        this.bufferSize = options.bufferSize || 4096;
        this.chunkDurationMs = options.chunkDurationMs || 100;
        this.onChunk = options.onChunk || (() => {});
        this.onVolumeChange = options.onVolumeChange || (() => {});
        this.onError = options.onError || (() => {});

        this.audioContext = null;
        this.mediaStream = null;
        this.sourceNode = null;
        this.processorNode = null;
        this.isCapturing = false;
        this.audioBuffer = [];
    }

    async start() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: this.sampleRate,
                    channelCount: 1,
                    echoCancellation: false,
                    noiseSuppression: false,
                    autoGainControl: false
                }
            });

            this.audioContext = new AudioContext({
                sampleRate: this.sampleRate
            });

            this.sourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);

            // 使用 ScriptProcessorNode（兼容性最好）
            this.processorNode = this.audioContext.createScriptProcessor(
                this.bufferSize, 1, 1
            );

            let chunkSamples = Math.floor(this.sampleRate * this.chunkDurationMs / 1000);
            let buffer = [];

            this.processorNode.onaudioprocess = (event) => {
                if (!this.isCapturing) return;

                const inputData = event.inputBuffer.getChannelData(0);
                const float32Data = new Float32Array(inputData);

                // 计算音量
                let sum = 0;
                for (let i = 0; i < float32Data.length; i++) {
                    sum += float32Data[i] * float32Data[i];
                }
                const volume = Math.sqrt(sum / float32Data.length);
                this.onVolumeChange(Math.min(volume * 10, 1));

                // 累积到 chunk buffer
                buffer.push(...float32Data);

                while (buffer.length >= chunkSamples) {
                    const chunk = new Float32Array(buffer.slice(0, chunkSamples));
                    buffer = buffer.slice(chunkSamples);

                    // 转换为 base64
                    const bytes = new Uint8Array(chunk.buffer);
                    let binary = '';
                    for (let i = 0; i < bytes.byteLength; i++) {
                        binary += String.fromCharCode(bytes[i]);
                    }
                    const base64 = btoa(binary);

                    this.onChunk(base64, Date.now());
                }
            };

            this.sourceNode.connect(this.processorNode);
            this.processorNode.connect(this.audioContext.destination);

            this.isCapturing = true;
            return true;

        } catch (error) {
            this.onError(error);
            return false;
        }
    }

    stop() {
        this.isCapturing = false;

        if (this.processorNode) {
            this.processorNode.disconnect();
            this.processorNode = null;
        }
        if (this.sourceNode) {
            this.sourceNode.disconnect();
            this.sourceNode = null;
        }
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioCapture;
}
