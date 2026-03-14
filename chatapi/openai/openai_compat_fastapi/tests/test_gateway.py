from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.sse_parser import parse_sse_lines


TINY_PNG_DATA_URL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9sQ5n/8AAAAASUVORK5CYII="
)


@pytest.fixture()
def client_and_dirs(tmp_path: Path):
    os.environ["USE_MOCK_BACKEND"] = "true"
    os.environ["LOG_DIR"] = str(tmp_path / "logs")
    os.environ["BRIDGE_DIR"] = str(tmp_path / "bridge")
    os.environ["SESSION_STORE_FILE"] = str(tmp_path / "sessions.json")
    os.environ["PUBLIC_BASE_URL"] = "http://testserver"

    import app.config as app_config
    import app.main as app_main

    importlib.reload(app_config)
    importlib.reload(app_main)
    client = TestClient(app_main.app)
    yield client, tmp_path



def _latest_trace_dir(log_dir: Path) -> Path:
    date_dirs = sorted([p for p in log_dir.iterdir() if p.is_dir()])
    assert date_dirs, f"no date dirs found under {log_dir}"
    trace_dirs = sorted([p for p in date_dirs[-1].iterdir() if p.is_dir()])
    assert trace_dirs, f"no trace dirs found under {date_dirs[-1]}"
    return trace_dirs[-1]



def test_sse_parser_basic() -> None:
    raw_lines = [
        'data:{"event":"message_start","task_id":"abc"}',
        'data:{"event":"message","answer":"大"}',
        'data:{"event":"message","answer":"模型"}',
        'data:{"event":"message_end"}',
    ]
    events = list(parse_sse_lines(raw_lines))
    assert [e.data["event"] for e in events if e.data and "event" in e.data] == [
        "message_start",
        "message",
        "message",
        "message_end",
    ]
    answer = "".join(e.data.get("answer", "") for e in events if e.data)
    assert answer == "大模型"



def test_non_stream_simple_text(client_and_dirs) -> None:
    client, tmp_path = client_and_dirs
    payload = {
        "model": "mock-model",
        "messages": [
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好"},
        ],
        "stream": False,
        "user": "u-1",
    }
    resp = client.post("/v1/chat/completions", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["object"] == "chat.completion"
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert "简单文本消息转发成功" in data["choices"][0]["message"]["content"]
    assert resp.headers["X-Trace-ID"]
    assert resp.headers["X-App-Conversation-ID"].startswith("mock-conv-")

    trace_dir = _latest_trace_dir(tmp_path / "logs")
    backend_request = json.loads((trace_dir / "backend_forward_request.json").read_text(encoding="utf-8"))
    assert backend_request["Query"].startswith("[message_0]")
    assert backend_request["AppConversationID"].startswith("mock-conv-")



def test_non_stream_tool_history_flattening(client_and_dirs) -> None:
    client, tmp_path = client_and_dirs
    payload = {
        "model": "mock-model",
        "messages": [
            {"role": "user", "content": "请查询北京天气"},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_123",
                        "type": "function",
                        "function": {"name": "get_weather", "arguments": '{"city":"北京"}'},
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "call_123", "content": '{"temp":26,"condition":"晴"}'},
            {"role": "user", "content": "继续总结"},
        ],
        "stream": False,
    }
    resp = client.post("/v1/chat/completions", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "tool call / tool message" in data["choices"][0]["message"]["content"]

    trace_dir = _latest_trace_dir(tmp_path / "logs")
    backend_request = json.loads((trace_dir / "backend_forward_request.json").read_text(encoding="utf-8"))
    assert "assistant(tool_calls)" in backend_request["Query"]
    assert "tool_call_id=call_123" in backend_request["Query"]
    assert "[tool_message_attached_to_query=true]" in backend_request["Query"]



def test_stream_with_image_data_url(client_and_dirs) -> None:
    client, tmp_path = client_and_dirs
    payload = {
        "model": "mock-model",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "帮我描述这张图"},
                    {"type": "image_url", "image_url": {"url": TINY_PNG_DATA_URL}},
                ],
            }
        ],
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    with client.stream("POST", "/v1/chat/completions", json=payload) as resp:
        assert resp.status_code == 200, resp.text
        lines = [line for line in resp.iter_lines() if line]

    assert any('"object": "chat.completion.chunk"' in line or '"object":"chat.completion.chunk"' in line for line in lines)
    assert any("[DONE]" in line for line in lines)
    assert any('"usage"' in line for line in lines)

    trace_dir = _latest_trace_dir(tmp_path / "logs")
    backend_request = json.loads((trace_dir / "backend_forward_request.json").read_text(encoding="utf-8"))
    assert len(backend_request["QueryExtends"]["Files"]) == 1
    file_info = backend_request["QueryExtends"]["Files"][0]
    assert file_info["Url"].startswith("http://testserver/bridge/files/")
    bridge_files = list((tmp_path / "bridge").glob("*"))
    assert bridge_files, "bridged image file should be saved locally"



def test_stateful_reuse_by_session_header(client_and_dirs) -> None:
    client, _tmp_path = client_and_dirs
    payload = {
        "model": "mock-model",
        "messages": [{"role": "user", "content": "第一轮"}],
    }
    resp1 = client.post("/v1/chat/completions", json=payload, headers={"X-Session-ID": "sess-A"})
    resp2 = client.post("/v1/chat/completions", json=payload, headers={"X-Session-ID": "sess-A"})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.headers["X-App-Conversation-ID"] == resp2.headers["X-App-Conversation-ID"]
