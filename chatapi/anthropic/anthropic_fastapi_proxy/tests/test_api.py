from __future__ import annotations

import base64
import json
from pathlib import Path

from app.config import settings


def test_messages_non_stream_text(client):
    resp = client.post(
        "/v1/messages",
        headers={"anthropic-version": "2023-06-01"},
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 128,
            "messages": [{"role": "user", "content": "你好"}],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["type"] == "message"
    assert body["role"] == "assistant"
    assert body["content"][0]["type"] == "text"
    assert "兼容代理已收到" in body["content"][0]["text"]
    assert resp.headers["anthropic-version"] == "2023-06-01"
    assert resp.headers["x-upstream-app-conversation-id"]


def test_messages_stream_text(client):
    with client.stream(
        "POST",
        "/v1/messages",
        headers={"anthropic-version": "2023-06-01"},
        json={
            "model": "claude-sonnet-4-6",
            "stream": True,
            "messages": [{"role": "user", "content": "你好"}],
        },
    ) as resp:
        assert resp.status_code == 200
        text = "".join(resp.iter_text())
    assert "event: message_start" in text
    assert "event: content_block_delta" in text
    assert "event: message_stop" in text


def test_messages_with_tool_history(client):
    resp = client.post(
        "/v1/messages",
        json={
            "model": "claude-sonnet-4-6",
            "messages": [
                {"role": "user", "content": "帮我查天气"},
                {
                    "role": "assistant",
                    "content": [
                        {"type": "tool_use", "id": "toolu_1", "name": "weather", "input": {"location": "北京"}}
                    ],
                },
                {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "晴 25 度"}]},
            ],
        },
    )
    assert resp.status_code == 200
    assert "工具结果" in resp.json()["content"][0]["text"]


def test_messages_with_image_url_bridge(client):
    png_1x1 = base64.b64encode(
        bytes.fromhex(
            "89504E470D0A1A0A0000000D4948445200000001000000010802000000907753DE0000000C4944415408D763F8FFFF3F0005FE02FEA7D605B30000000049454E44AE426082"
        )
    ).decode("utf-8")
    resp = client.post(
        "/v1/messages",
        json={
            "model": "claude-sonnet-4-6",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": png_1x1}},
                        {"type": "text", "text": "图片里是什么"},
                    ],
                }
            ],
        },
    )
    assert resp.status_code == 200
    assert "图片" in resp.json()["content"][0]["text"]
    media_files = list(settings.media_dir.glob("*"))
    assert media_files


def test_trace_log_written(client):
    resp = client.post(
        "/v1/messages",
        json={"model": "claude-sonnet-4-6", "messages": [{"role": "user", "content": "trace test"}]},
    )
    assert resp.status_code == 200
    trace_id = resp.headers["x-proxy-trace-id"]
    trace_files = list((settings.log_dir / "traces").rglob(f"trace_{trace_id}.jsonl"))
    assert len(trace_files) == 1
    content = trace_files[0].read_text(encoding="utf-8")
    assert "received_raw_request" in content
    assert "upstream_forward_request" in content
    assert "anthropic_final_response" in content
