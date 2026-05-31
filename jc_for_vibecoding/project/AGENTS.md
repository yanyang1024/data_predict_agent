# AGENTS.md

## Entrypoint & Run

- `python run.py` starts the server on `0.0.0.0:5000`. Optional flags: `--port`, `--debug`, `--host`.
- `app.py` exports `create_app()` (Flask app factory) — not a standalone script.

## Model Download

- First run downloads ~18GB from `hf-mirror.com` (Chinese Hugging Face mirror) to `./models/`.
- Override cache dir with `MODEL_CACHE_DIR` env var.
- Model: `facebook/seamless-m4t-v2-large`, `float16` precision, CUDA only (`cuda:0`).

## Two-Stage Translation Pipeline

```
Audio → VAD → SeamlessM4T (fast init) → LLM Refiner (context-aware polish) → streaming to client
```

- **Stage 1 (SeamlessM4T)**: local GPU inference, ~hundreds ms. Gives instant raw translation.
- **Stage 2 (LLM Refiner)**: OpenAI-compatible API call, streaming tokens back. Uses a sliding window of conversation history to correct terminology, pronouns, and consistency.
- LLM can retroactively correct previous segments via `CORRECT:<segment_id>:<text>` lines in its output.
- Set `LLM_API_KEY` and `LLM_API_BASE` in `config.py` or via env vars. If unset, LLM is skipped and only SeamlessM4T is used.
- Correction bias is modulated by `context_maturity = history_size / context_window`:
  - `maturity < LLM_EARLY_THRESHOLD` (0.3): prompt tells LLM to aggressively correct earlier segments (which had little context)
  - `maturity > LLM_MATURE_THRESHOLD` (0.7): prompt tells LLM to focus refinement on the current/new segment
  - Between thresholds: balanced correction across old and new

## Architecture

- Flask factory + Socket.IO (`threading` async mode). gunicorn/eventlet commented out in `requirements.txt`.
- Audio pipeline: browser PCM float32 → base64 → SocketIO `audio_chunk` → `AudioProcessor` (resample) → Silero VAD (`torch.hub.load` from `snakers4/silero-vad`) → `AudioStreamBuffer` (ring buffer, VAD-gated segmentation) → `InferenceEngine` (`ThreadPoolExecutor`, max 1 worker) → `SubtitleEmitter` push.
- LLM refinement runs in the same thread as the SeamlessM4T inference (daemon thread per segment), streaming tokens via SocketIO without blocking the audio pipeline.
- Session state: in-memory `client_sessions` dict in `websocket/events.py:10`, keyed by SocketIO `sid`.

## Frontend Events (server → client)

| Event | Payload | When |
|-------|---------|------|
| `segment_start` | `{segment_id, timestamp}` | New VAD segment detected |
| `initial_translation` | `{segment_id, text}` | SeamlessM4T fast translation ready |
| `stream_token` | `{segment_id, token}` | One token from LLM streaming (typewriter) |
| `stream_end` | `{segment_id}` | LLM refinement finished (or skipped) |
| `correction` | `{segment_id, corrected_text}` | Retroactive correction of a prior segment |

Segment lifecycle on client: `pending → initial → refining → final / corrected`

## Style / Infra

- No linter, formatter, test framework, `.gitignore`, or CI — add these before making non-trivial changes.
- Frontend: vanilla JS (no framework), Socket.IO client from CDN, `getUserMedia` + `ScriptProcessorNode` for capture.
