import base64
import json
from pathlib import Path

from fastapi.testclient import TestClient

from proxy_service import (
    ChatRequest,
    MockBackend,
    ProxySettings,
    SSEParser,
    TraceLogger,
    create_app,
)


def tiny_png_base64() -> str:
    blob = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Z5XQAAAAASUVORK5CYII="
    )
    return base64.b64encode(blob).decode("utf-8")


def test_sse_parser_can_parse_standard_frames(tmp_path: Path) -> None:
    trace = TraceLogger(tmp_path / "logs", "trace-parser")

    class FakeResp:
        status_code = 200

        def iter_lines(self, chunk_size: int = 512, decode_unicode: bool = False):
            lines = [
                "event: text",
                'data: {"event":"message_start","task_id":"task-1"}',
                "",
                "event: text",
                'data: {"event":"message","answer":"你"}',
                "",
                "event: text",
                'data: {"event":"message_end"}',
                "",
            ]
            for line in lines:
                yield line if decode_unicode else line.encode("utf-8")

    parser = SSEParser(trace)
    events = list(parser.parse(FakeResp()))
    assert len(events) == 3
    assert events[0].data_json["event"] == "message_start"
    assert events[1].data_json["answer"] == "你"
    assert events[2].data_json["event"] == "message_end"


def build_client(tmp_path: Path, backend: MockBackend | None = None) -> tuple[TestClient, MockBackend, ProxySettings]:
    backend = backend or MockBackend()
    settings = ProxySettings(runtime_root=tmp_path / "runtime", public_base_url="http://testserver")
    app = create_app(backend=backend, settings=settings)
    return TestClient(app), backend, settings


def test_chat_stream_simple_text(tmp_path: Path) -> None:
    client, backend, settings = build_client(tmp_path)

    with client.stream(
        "POST",
        "/api/chat",
        json={
            "model": "demo-model",
            "messages": [{"role": "user", "content": "你好"}],
            "stream": True,
        },
    ) as resp:
        assert resp.status_code == 200
        lines = [line for line in resp.iter_lines() if line]

    chunks = [json.loads(line) for line in lines]
    assert chunks[0]["message"]["content"] == "你好"
    assert chunks[-1]["done"] is True
    assert backend.calls

    request_log_files = list((settings.logs_root).rglob("*.jsonl"))
    assert request_log_files, "should create local trace logs"
    log_text = request_log_files[0].read_text(encoding="utf-8")
    assert "request_received" in log_text
    assert "backend_sse_event" in log_text
    assert "ollama_chunk_emitted" in log_text


def test_chat_structures_tool_messages_in_backend_query(tmp_path: Path) -> None:
    client, backend, _ = build_client(tmp_path)
    backend.response_lines = [
        "event: text data: {\"event\":\"tool_message\",\"tool_calls\":[{\"type\":\"function\",\"function\":{\"name\":\"get_weather\",\"arguments\":{\"city\":\"Hangzhou\"}}}]}",
        "event: text data: {\"event\":\"message_end\"}",
    ]

    payload = {
        "model": "demo-model",
        "messages": [
            {"role": "user", "content": "杭州天气怎么样？"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {"name": "get_weather", "arguments": {"city": "Hangzhou"}},
                    }
                ],
            },
            {"role": "tool", "tool_name": "get_weather", "content": "晴，24℃"},
        ],
        "stream": False,
    }
    resp = client.post("/api/chat", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"]["tool_calls"][0]["function"]["name"] == "get_weather"

    backend_query = backend.calls[-1]["content"]
    assert "<tool_calls>" in backend_query
    assert 'role="tool"' in backend_query
    assert "get_weather" in backend_query
    assert "晴，24℃" in backend_query


def test_chat_with_images_builds_query_extends_and_bridge_url(tmp_path: Path) -> None:
    client, backend, settings = build_client(tmp_path)
    image_b64 = tiny_png_base64()

    resp = client.post(
        "/api/chat",
        json={
            "model": "demo-model",
            "messages": [
                {"role": "user", "content": "帮我看图", "images": [image_b64]},
            ],
            "stream": False,
        },
    )
    assert resp.status_code == 200

    query_extends = backend.calls[-1]["query_extends"]
    assert query_extends is not None
    files = query_extends["Files"]
    assert len(files) == 1
    assert files[0]["Url"].startswith("http://testserver/bridge/")
    assert files[0]["Name"].startswith("msg001_img001")

    bridge_files = list(settings.bridge_root.rglob("*.png")) + list(settings.bridge_root.rglob("*.jpg"))
    assert bridge_files, "image should be materialized to local bridge dir"


def test_generate_non_stream_text_response(tmp_path: Path) -> None:
    client, backend, _ = build_client(tmp_path)
    backend.response_lines = [
        "event: text",
        'data: {"event":"message","answer":"Hello"}',
        "",
        "event: text",
        'data: {"event":"message","answer":" world"}',
        "",
        "event: text",
        'data: {"event":"message_end"}',
        "",
    ]

    resp = client.post(
        "/api/generate",
        json={"model": "demo-model", "prompt": "say hi", "stream": False},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["response"] == "Hello world"
    assert body["done"] is True
