from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any, Dict, List, Sequence, Tuple

from .config import settings
from .media import image_block_to_upstream_file
from .models import MessageParam, MessagesRequest, SessionState, UpstreamQueryExtends, UpstreamRequestPayload
from .store import session_store


ROLE_LABEL = {
    "user": "USER",
    "assistant": "ASSISTANT",
}


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _system_to_text(system: Any) -> str:
    if system is None:
        return ""
    if isinstance(system, str):
        return system
    if isinstance(system, list):
        parts: List[str] = []
        for block in system:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            else:
                parts.append(_json(block))
        return "\n".join(part for part in parts if part)
    return str(system)


def _normalize_tool_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            else:
                parts.append(_json(block))
        return "\n".join(parts)
    return _json(content)


def serialize_content_blocks(role: str, content: Any) -> Tuple[str, List[Dict[str, Any]]]:
    if isinstance(content, str):
        return f"[{ROLE_LABEL[role]}]\n{content}\n", []

    text_parts: List[str] = [f"[{ROLE_LABEL[role]}]"]
    images: List[Dict[str, Any]] = []

    for block in content:
        block_type = block.get("type")
        if block_type == "text":
            text_parts.append(block.get("text", ""))
        elif block_type == "image":
            images.append(block)
            source = block.get("source", {})
            source_type = source.get("type", "unknown")
            text_parts.append(f"<image source_type=\"{source_type}\">见 QueryExtends.Files</image>")
        elif block_type == "tool_use":
            text_parts.append(
                "<assistant_tool_use "
                f"id=\"{block.get('id', '')}\" "
                f"name=\"{block.get('name', '')}\">"
                f"{_json(block.get('input', {}))}"
                "</assistant_tool_use>"
            )
        elif block_type == "tool_result":
            text_parts.append(
                "<user_tool_result "
                f"tool_use_id=\"{block.get('tool_use_id', '')}\" "
                f"is_error=\"{str(block.get('is_error', False)).lower()}\">"
                f"{_normalize_tool_content(block.get('content', ''))}"
                "</user_tool_result>"
            )
        else:
            text_parts.append(f"<unsupported_block type=\"{block_type}\">{_json(block)}</unsupported_block>")

    return "\n".join(part for part in text_parts if part) + "\n", images


def serialize_tools(tools: Sequence[Dict[str, Any]] | None) -> str:
    if not tools:
        return ""
    lines = ["[AVAILABLE_TOOLS]"]
    for tool in tools:
        lines.append(_json(tool))
    return "\n".join(lines) + "\n"


def _build_query_text(system: Any, messages: Sequence[MessageParam], tools: Sequence[Dict[str, Any]] | None) -> Tuple[str, UpstreamQueryExtends]:
    sections: List[str] = []
    system_text = _system_to_text(system)
    if system_text:
        sections.append(f"[SYSTEM]\n{system_text}\n")

    sections.append(serialize_tools(tools))

    extends = UpstreamQueryExtends(files=[])
    for msg in messages:
        serialized, image_blocks = serialize_content_blocks(msg.role, msg.content)
        sections.append(serialized)
        for block in image_blocks:
            extends.files.append(image_block_to_upstream_file(block))

    query_text = "\n".join(part for part in sections if part).strip()
    return query_text, extends


def _system_fingerprint(system: Any) -> str:
    return hashlib.sha256(_system_to_text(system).encode("utf-8")).hexdigest()


def build_upstream_request(req: MessagesRequest, user_id: str, proxy_conversation_id: str | None = None) -> UpstreamRequestPayload:
    if settings.conversation_mode == "stateless":
        query_text, query_extends = _build_query_text(req.system, req.messages, req.tools)
        return UpstreamRequestPayload(
            user_id=user_id,
            app_conversation_id="",
            content=query_text,
            query_extends=query_extends,
            proxy_conversation_id=proxy_conversation_id or str(uuid.uuid4()),
            mode="stateless",
        )

    proxy_id = proxy_conversation_id or str(uuid.uuid4())
    existing = session_store.get(proxy_id)

    if existing is None:
        new_messages = req.messages
        system_payload = req.system
    else:
        if len(req.messages) < existing.last_forwarded_message_count:
            new_messages = req.messages
            system_payload = req.system
        else:
            new_messages = req.messages[existing.last_forwarded_message_count :]
            system_payload = None
        if _system_fingerprint(req.system) != (existing.system_fingerprint or ""):
            new_messages = req.messages
            system_payload = req.system

    if not new_messages:
        new_messages = req.messages[-1:]

    query_text, query_extends = _build_query_text(system_payload, new_messages, req.tools)

    return UpstreamRequestPayload(
        user_id=user_id,
        app_conversation_id=existing.upstream_conversation_id if existing else "",
        content=query_text,
        query_extends=query_extends,
        proxy_conversation_id=proxy_id,
        mode="session",
    )


def update_session_after_success(proxy_conversation_id: str, upstream_conversation_id: str, req: MessagesRequest) -> None:
    if settings.conversation_mode != "session":
        return
    session_store.upsert(
        proxy_conversation_id,
        SessionState(
            upstream_conversation_id=upstream_conversation_id,
            last_forwarded_message_count=len(req.messages),
            system_fingerprint=_system_fingerprint(req.system),
        ),
    )
