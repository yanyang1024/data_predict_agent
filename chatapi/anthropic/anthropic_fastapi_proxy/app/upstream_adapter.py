from __future__ import annotations

import importlib
import inspect
import json
from typing import Any, Dict, Iterable, Iterator, Optional

from .config import settings
from .logging_utils import TraceLogger, logger
from .models import UpstreamRequestPayload


class UpstreamBackend:
    def __init__(self) -> None:
        module_name = "app.mock_backend" if settings.use_mock_backend else "user_backend"
        module = importlib.import_module(module_name)
        self.create_conversation_fn = getattr(module, "create_conversation")
        self.chat_query_v2_sse_fn = getattr(module, "chat_query_v2_sse")

    def create_conversation(self) -> str:
        return self.create_conversation_fn()

    def chat_query_v2_sse(self, payload: UpstreamRequestPayload):
        fn = self.chat_query_v2_sse_fn
        signature = inspect.signature(fn)
        kwargs: Dict[str, Any] = {}
        query_extends = None
        if payload.query_extends.files:
            query_extends = {
                "Files": [
                    {
                        "Name": f.name,
                        "Path": f.path,
                        "Size": f.size,
                        "Url": f.url,
                    }
                    for f in payload.query_extends.files
                ]
            }

        if "query_extends" in signature.parameters:
            kwargs["query_extends"] = query_extends
            return fn(payload.user_id, payload.app_conversation_id, payload.content, **kwargs)

        if len(signature.parameters) >= 4:
            return fn(payload.user_id, payload.app_conversation_id, payload.content, query_extends)

        content = payload.content
        if query_extends:
            content += "\n\n[QUERY_EXTENDS_FILES]\n" + json.dumps(query_extends, ensure_ascii=False)
        return fn(payload.user_id, payload.app_conversation_id, content)


backend = UpstreamBackend()


def _safe_json_loads(data: str) -> Any:
    return json.loads(data)


class UpstreamSSEParser:
    def __init__(self, trace: TraceLogger):
        self.trace = trace

    def parse(self, response: Any) -> Iterator[Dict[str, Any]]:
        current_event_name: Optional[str] = None
        current_data_lines: list[str] = []

        def flush_buffer() -> Optional[Dict[str, Any]]:
            nonlocal current_event_name, current_data_lines
            if not current_data_lines:
                current_event_name = None
                return None
            raw = "\n".join(current_data_lines).strip()
            current_data_lines = []
            if not raw:
                current_event_name = None
                return None
            obj = _safe_json_loads(raw)
            if isinstance(obj, dict) and current_event_name and "_sse_event_name" not in obj:
                obj["_sse_event_name"] = current_event_name
            current_event_name = None
            return obj if isinstance(obj, dict) else {"event": "message", "answer": str(obj)}

        for raw_line in response.iter_lines(chunk_size=4):
            if raw_line is None:
                continue
            line = raw_line.decode("utf-8") if isinstance(raw_line, (bytes, bytearray)) else str(raw_line)
            self.trace.log("upstream_sse_raw_line", {"line": line})
            stripped = line.strip()
            if stripped == "":
                maybe = flush_buffer()
                if maybe is not None:
                    self.trace.log("upstream_sse_parsed_event", maybe)
                    yield maybe
                continue
            if stripped.startswith(":"):
                continue
            if stripped.startswith("event:"):
                current_event_name = stripped[len("event:") :].strip()
                continue
            if stripped.startswith("data:"):
                payload = stripped[len("data:") :].strip()
                if payload:
                    current_data_lines.append(payload)
                    if payload.startswith("{") and payload.endswith("}"):
                        maybe = flush_buffer()
                        if maybe is not None:
                            self.trace.log("upstream_sse_parsed_event", maybe)
                            yield maybe
                continue
            # fallback: some upstreams may emit one-line JSON without SSE prefix
            if stripped.startswith("{") and stripped.endswith("}"):
                maybe = _safe_json_loads(stripped)
                self.trace.log("upstream_sse_parsed_event", maybe)
                if isinstance(maybe, dict):
                    yield maybe
                continue
            logger.warning("Unhandled upstream SSE line: %s", stripped)
            self.trace.log("upstream_sse_unhandled_line", {"line": stripped})

        maybe = flush_buffer()
        if maybe is not None:
            self.trace.log("upstream_sse_parsed_event", maybe)
            yield maybe
