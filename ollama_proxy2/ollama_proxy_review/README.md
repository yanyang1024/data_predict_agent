# Ollama Proxy Review - FastAPI v2

This project contains a reviewed and iterated FastAPI proxy that adapts a stateful internal SSE chat backend into Ollama-compatible `/api/chat` and `/api/generate` endpoints.

## Highlights

- Supports `messages[].images` by materializing base64 images to local files and exposing them under `/bridge/...`.
- Converts Ollama chat history, assistant tool calls, and tool role messages into a structured transcript instead of naive string concatenation.
- Persists full per-request local trace logs in JSONL, including:
  - inbound request body
  - created conversation id
  - backend request payload
  - raw SSE lines
  - parsed SSE events
  - emitted Ollama chunks
  - final response summary
- Includes mock backend and pytest tests for:
  - SSE parsing
  - simple text stream
  - tool-call message flow
  - image message flow
  - non-stream generate response

## Run tests

```bash
cd /mnt/data/ollama_proxy_review
PYTHONPATH=. pytest -q
```

## Run demo server

```bash
cd /mnt/data/ollama_proxy_review
python proxy_service.py
```

The demo server uses a mock backend by default.

## Integrating your real functions

Replace `create_conversation()` and `chat_query_v2_sse()` with your real implementations, or inject them via `DefaultBackend`:

```python
from proxy_service import create_app, DefaultBackend, ProxySettings
from your_module import create_conversation, chat_query_v2_sse

backend = DefaultBackend(create_conversation, chat_query_v2_sse)
app = create_app(backend, ProxySettings(runtime_root=Path('./runtime')))
```

Important: to support images, your `chat_query_v2_sse` wrapper must accept `query_extends` and pass it to the real HTTP request payload as `QueryExtends`.
