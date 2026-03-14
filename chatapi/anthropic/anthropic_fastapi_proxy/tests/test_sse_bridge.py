from __future__ import annotations

from app.logging_utils import TraceLogger
from app.models import MessagesRequest
from app.sse_bridge import build_non_streaming_message, iter_anthropic_stream


def sample_events():
    return [
        {
            "event": "message_start",
            "task_id": "01KKK21",
            "id": "01KKK21",
            "conversation_id": "conv_1",
        },
        {
            "event": "message_output_start",
            "task_id": "01KKK21",
            "id": "01KKK21",
            "conversation_id": "conv_1",
        },
        {
            "event": "message",
            "task_id": "01KKK21",
            "id": "01KKK21",
            "answer": "大",
            "conversation_id": "conv_1",
        },
        {
            "event": "message",
            "task_id": "01KKK21",
            "id": "01KKK21",
            "answer": "模型",
            "conversation_id": "conv_1",
        },
        {
            "event": "message_cost",
            "task_id": "01KKK21",
            "id": "01KKK21",
            "input_tokens": 10,
            "output_tokens": 2,
            "conversation_id": "conv_1",
        },
        {
            "event": "message_end",
            "task_id": "01KKK21",
            "id": "01KKK21",
            "conversation_id": "conv_1",
        },
    ]


def test_non_streaming_bridge(tmp_path):
    trace = TraceLogger("bridge_non_stream")
    req = MessagesRequest.model_validate({"model": "claude-sonnet-4-6", "messages": [{"role": "user", "content": "hi"}]})
    out = build_non_streaming_message(req, sample_events(), trace)
    assert out["content"][0]["text"] == "大模型"
    assert out["usage"]["input_tokens"] == 10
    assert out["usage"]["output_tokens"] == 2


def test_streaming_bridge_emits_anthropic_events(tmp_path):
    trace = TraceLogger("bridge_stream")
    req = MessagesRequest.model_validate(
        {"model": "claude-sonnet-4-6", "stream": True, "messages": [{"role": "user", "content": "hi"}]}
    )
    chunks = list(iter_anthropic_stream(req, sample_events(), trace))
    joined = "".join(chunks)
    assert "event: message_start" in joined
    assert "event: content_block_start" in joined
    assert "event: content_block_delta" in joined
    assert "event: message_delta" in joined
    assert "event: message_stop" in joined
    assert "大" in joined and "模型" in joined
