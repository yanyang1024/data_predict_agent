from __future__ import annotations

import base64

from app.anthropic_mapper import build_upstream_request
from app.config import settings
from app.models import MessagesRequest


def test_build_upstream_request_with_tool_blocks():
    req = MessagesRequest.model_validate(
        {
            "model": "claude-sonnet-4-6",
            "max_tokens": 128,
            "messages": [
                {"role": "user", "content": "帮我查天气"},
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "我将调用天气工具。"},
                        {
                            "type": "tool_use",
                            "id": "toolu_123",
                            "name": "get_weather",
                            "input": {"location": "Beijing"},
                        },
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "toolu_123",
                            "content": "晴，25度",
                        }
                    ],
                },
            ],
            "tools": [
                {
                    "name": "get_weather",
                    "description": "获取天气",
                    "input_schema": {"type": "object"},
                }
            ],
        }
    )

    payload = build_upstream_request(req, user_id="u1", proxy_conversation_id="p1")
    assert "assistant_tool_use" in payload.content
    assert "user_tool_result" in payload.content
    assert "AVAILABLE_TOOLS" in payload.content
    assert payload.user_id == "u1"


def test_build_upstream_request_with_base64_image_generates_query_extends():
    png_1x1 = base64.b64encode(
        bytes.fromhex(
            "89504E470D0A1A0A0000000D4948445200000001000000010802000000907753DE0000000C4944415408D763F8FFFF3F0005FE02FEA7D605B30000000049454E44AE426082"
        )
    ).decode("utf-8")

    req = MessagesRequest.model_validate(
        {
            "model": "claude-sonnet-4-6",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": png_1x1,
                            },
                        },
                        {"type": "text", "text": "图里有什么"},
                    ],
                }
            ],
        }
    )

    payload = build_upstream_request(req, user_id="u2")
    assert payload.query_extends.files
    file_info = payload.query_extends.files[0]
    assert file_info.url.startswith(settings.public_base_url + "/proxy/media/")
    assert file_info.size > 0
    assert "QueryExtends.Files" in payload.content
