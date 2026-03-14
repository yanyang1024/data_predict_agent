from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, List, Optional

from .config import settings
from .logging_utils import TraceLogger
from .models import MessagesRequest


@dataclass
class BridgeState:
    model: str
    upstream_message_id: Optional[str] = None
    upstream_conversation_id: Optional[str] = None
    anthropic_message_id: Optional[str] = None
    text_started: bool = False
    text_chunks: List[str] = field(default_factory=list)
    usage: Dict[str, int] = field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0})
    stop_reason: str = "end_turn"

    def message_id(self) -> str:
        if self.anthropic_message_id:
            return self.anthropic_message_id
        base = self.upstream_message_id or "unknown"
        self.anthropic_message_id = base if str(base).startswith("msg_") else f"msg_{base}"
        return self.anthropic_message_id


def _sse(event: str, data: Dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _emit(trace: TraceLogger, event: str, data: Dict[str, Any]) -> str:
    trace.log("anthropic_sse_out", {"event": event, "data": data})
    return _sse(event, data)


def _message_start_data(state: BridgeState) -> Dict[str, Any]:
    return {
        "type": "message_start",
        "message": {
            "id": state.message_id(),
            "type": "message",
            "role": "assistant",
            "model": state.model,
            "content": [],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        },
    }


def _message_delta_data(state: BridgeState) -> Dict[str, Any]:
    return {
        "type": "message_delta",
        "delta": {
            "stop_reason": state.stop_reason,
            "stop_sequence": None,
        },
        "usage": {
            "input_tokens": state.usage.get("input_tokens", 0),
            "output_tokens": state.usage.get("output_tokens", 0),
        },
    }


def _content_block_start() -> Dict[str, Any]:
    return {
        "type": "content_block_start",
        "index": 0,
        "content_block": {"type": "text", "text": ""},
    }


def _content_block_delta(text: str) -> Dict[str, Any]:
    return {
        "type": "content_block_delta",
        "index": 0,
        "delta": {
            "type": "text_delta",
            "text": text,
        },
    }


def _content_block_stop() -> Dict[str, Any]:
    return {
        "type": "content_block_stop",
        "index": 0,
    }


def _maybe_text_from_tool_message(event: Dict[str, Any]) -> str:
    for key in ("answer", "content", "message", "text"):
        val = event.get(key)
        if isinstance(val, str) and val:
            return f"\n[tool_message] {val}\n"
    compact = json.dumps(event, ensure_ascii=False, sort_keys=True)
    return f"\n[tool_message] {compact}\n"


def iter_anthropic_stream(
    req: MessagesRequest,
    upstream_events: Iterable[Dict[str, Any]],
    trace: TraceLogger,
) -> Iterator[str]:
    state = BridgeState(model=req.model)
    emitted_message_start = False

    for event in upstream_events:
        event_type = event.get("event") or event.get("type") or event.get("_sse_event_name")
        if event_type == "message_start":
            state.upstream_message_id = event.get("id") or event.get("task_id")
            state.upstream_conversation_id = event.get("conversation_id")
            emitted_message_start = True
            yield _emit(trace, "message_start", _message_start_data(state))
            continue

        if event_type in {"message", "tool_message"}:
            if not emitted_message_start:
                state.upstream_message_id = event.get("id") or event.get("task_id") or "late_start"
                state.upstream_conversation_id = event.get("conversation_id")
                emitted_message_start = True
                yield _emit(trace, "message_start", _message_start_data(state))

            if not state.text_started:
                state.text_started = True
                yield _emit(trace, "content_block_start", _content_block_start())

            text = event.get("answer", "") if event_type == "message" else _maybe_text_from_tool_message(event)
            if text:
                state.text_chunks.append(text)
                yield _emit(trace, "content_block_delta", _content_block_delta(text))
            continue

        if event_type == "message_cost":
            state.usage = {
                "input_tokens": int(event.get("input_tokens", 0) or 0),
                "output_tokens": int(event.get("output_tokens", 0) or 0),
            }
            continue

        if event_type in {"think_message", "agent_thought"}:
            trace.log("upstream_thinking_event", event)
            if settings.expose_thinking_as_text:
                if not emitted_message_start:
                    state.upstream_message_id = event.get("id") or event.get("task_id") or "thinking"
                    emitted_message_start = True
                    yield _emit(trace, "message_start", _message_start_data(state))
                if not state.text_started:
                    state.text_started = True
                    yield _emit(trace, "content_block_start", _content_block_start())
                thinking_text = event.get("answer") or event.get("content") or event.get("text") or ""
                if thinking_text:
                    state.text_chunks.append(thinking_text)
                    yield _emit(trace, "content_block_delta", _content_block_delta(thinking_text))
            continue

        if event_type == "message_failed":
            payload = {
                "type": "error",
                "error": {
                    "type": "api_error",
                    "message": json.dumps(event, ensure_ascii=False),
                },
            }
            trace.log("anthropic_sse_out", {"event": "error", "data": payload})
            yield _sse("error", payload)
            return

        if event_type == "message_end":
            if not emitted_message_start:
                state.upstream_message_id = event.get("id") or event.get("task_id") or "end_only"
                emitted_message_start = True
                yield _emit(trace, "message_start", _message_start_data(state))

            if state.text_started:
                yield _emit(trace, "content_block_stop", _content_block_stop())
            yield _emit(trace, "message_delta", _message_delta_data(state))
            yield _emit(trace, "message_stop", {"type": "message_stop"})
            return

        trace.log("upstream_event_ignored_for_output", event)

    if not emitted_message_start:
        state.upstream_message_id = "empty"
        yield _emit(trace, "message_start", _message_start_data(state))
    if state.text_started:
        yield _emit(trace, "content_block_stop", _content_block_stop())
    yield _emit(trace, "message_delta", _message_delta_data(state))
    yield _emit(trace, "message_stop", {"type": "message_stop"})


def build_non_streaming_message(
    req: MessagesRequest,
    upstream_events: Iterable[Dict[str, Any]],
    trace: TraceLogger,
) -> Dict[str, Any]:
    state = BridgeState(model=req.model)

    for event in upstream_events:
        event_type = event.get("event") or event.get("type") or event.get("_sse_event_name")
        if event_type == "message_start":
            state.upstream_message_id = event.get("id") or event.get("task_id")
            state.upstream_conversation_id = event.get("conversation_id")
        elif event_type == "message":
            text = event.get("answer", "")
            if text:
                state.text_chunks.append(text)
        elif event_type == "tool_message":
            state.text_chunks.append(_maybe_text_from_tool_message(event))
        elif event_type == "message_cost":
            state.usage = {
                "input_tokens": int(event.get("input_tokens", 0) or 0),
                "output_tokens": int(event.get("output_tokens", 0) or 0),
            }
        elif event_type == "message_failed":
            state.stop_reason = "error"
            state.text_chunks.append(f"\n[message_failed] {json.dumps(event, ensure_ascii=False)}")

    text = "".join(state.text_chunks)
    response = {
        "id": state.message_id(),
        "type": "message",
        "role": "assistant",
        "model": req.model,
        "content": [{"type": "text", "text": text}],
        "stop_reason": state.stop_reason,
        "stop_sequence": None,
        "usage": state.usage,
    }
    trace.log("anthropic_final_response", response)
    return response
