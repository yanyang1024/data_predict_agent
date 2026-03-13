from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import re
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic_ns
from typing import Any, Dict, Generator, Iterable, List, Literal, Optional, Protocol, Union
from urllib.parse import urlsplit

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field


# =====================================================================
# 1) Protocols / Settings
# =====================================================================


class ResponseLike(Protocol):
    status_code: int

    def iter_lines(self, chunk_size: int = 512, decode_unicode: bool = False) -> Iterable[bytes | str]:
        ...


class BackendProtocol(Protocol):
    def create_conversation(self) -> str:
        ...

    def chat_query_v2_sse(
        self,
        *,
        user_id: str,
        app_conversation_id: str,
        content: str,
        query_extends: Optional[Dict[str, Any]] = None,
    ) -> ResponseLike:
        ...


@dataclass(slots=True)
class ProxySettings:
    runtime_root: Path = Path("./runtime")
    bridge_route: str = "/bridge"
    public_base_url: Optional[str] = None
    default_user_id: str = "ollama_proxy_user"
    log_payloads: bool = True
    max_images_per_request: int = 16
    max_single_image_bytes: int = 20 * 1024 * 1024
    pass_tool_message_as_thinking: bool = False

    @property
    def bridge_root(self) -> Path:
        return self.runtime_root / "bridge"

    @property
    def logs_root(self) -> Path:
        return self.runtime_root / "logs"

    def ensure_dirs(self) -> None:
        self.bridge_root.mkdir(parents=True, exist_ok=True)
        self.logs_root.mkdir(parents=True, exist_ok=True)


# =====================================================================
# 2) Helpers / Models
# =====================================================================


class ToolFunction(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    description: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = "function"
    function: ToolFunction


class OllamaMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[Union[str, List[Any]]] = ""
    images: Optional[List[str]] = None
    thinking: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_name: Optional[str] = None


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str
    messages: List[OllamaMessage] = Field(default_factory=list)
    tools: Optional[List[Dict[str, Any]]] = None
    format: Optional[Any] = None
    stream: bool = True
    think: Optional[Union[bool, str]] = None
    keep_alive: Optional[Union[str, int, float]] = None
    options: Optional[Dict[str, Any]] = None


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str
    prompt: str = ""
    images: Optional[List[str]] = None
    suffix: Optional[str] = None
    system: Optional[str] = None
    format: Optional[Any] = None
    raw: Optional[bool] = None
    stream: bool = True
    think: Optional[Union[bool, str]] = None
    keep_alive: Optional[Union[str, int, float]] = None
    options: Optional[Dict[str, Any]] = None


@dataclass(slots=True)
class ParsedSSEEvent:
    event_name: Optional[str]
    data_text: str
    data_json: Optional[Dict[str, Any]]
    raw_lines: List[str] = field(default_factory=list)


@dataclass(slots=True)
class StreamAggregate:
    content_parts: List[str] = field(default_factory=list)
    thinking_parts: List[str] = field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    task_id: Optional[str] = None
    message_id: Optional[str] = None
    backend_conversation_id: Optional[str] = None
    app_conversation_id: Optional[str] = None
    last_status: Optional[str] = None
    done_reason: str = "stop"


@dataclass(slots=True)
class BackendBuildResult:
    content: str
    query_extends: Optional[Dict[str, Any]]


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ProxyError(RuntimeError):
    pass


class BackendMessageFailed(ProxyError):
    pass


class TraceLogger:
    _lock = threading.Lock()

    def __init__(self, root: Path, trace_id: str) -> None:
        day = datetime.now(timezone.utc).strftime("%Y%m%d")
        self.path = root / day / f"{trace_id}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.trace_id = trace_id

    def log(self, stage: str, **payload: Any) -> None:
        record = {
            "ts": utcnow_iso(),
            "trace_id": self.trace_id,
            "stage": stage,
            **payload,
        }
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")


# =====================================================================
# 3) Image bridge
# =====================================================================


DATA_URI_RE = re.compile(r"^data:(?P<mime>[-\w.+/]+);base64,(?P<data>.+)$", re.DOTALL)
COMBINED_SSE_RE = re.compile(r"^event\s*:\s*(?P<event>[^\s]+)\s+data\s*:\s*(?P<data>.+)$")


MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/bmp": "bmp",
}


def detect_image_extension(blob: bytes) -> str:
    if blob.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if blob.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if blob.startswith(b"GIF87a") or blob.startswith(b"GIF89a"):
        return "gif"
    if len(blob) >= 12 and blob[:4] == b"RIFF" and blob[8:12] == b"WEBP":
        return "webp"
    if blob.startswith(b"BM"):
        return "bmp"
    return "bin"


def sanitize_filename(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return safe or "image"


@dataclass(slots=True)
class SavedBridgeFile:
    request_message_index: int
    file_index: int
    name: str
    relative_path: str
    abs_path: Path
    size: int
    url: str

    def to_query_extends_file(self) -> Dict[str, Any]:
        return {
            "Name": self.name,
            "Path": self.relative_path.replace(os.sep, "/"),
            "Size": self.size,
            "Url": self.url,
        }


class ImageBridgeService:
    def __init__(self, settings: ProxySettings) -> None:
        self.settings = settings
        self.settings.ensure_dirs()

    def _resolve_public_base_url(self, request: Request) -> str:
        if self.settings.public_base_url:
            return self.settings.public_base_url.rstrip("/")

        proto = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("x-forwarded-host", request.headers.get("host", request.url.netloc))
        if not host:
            return str(request.base_url).rstrip("/")
        return f"{proto}://{host}".rstrip("/")

    def _decode_base64_image(self, payload: str) -> tuple[bytes, Optional[str]]:
        mime_type: Optional[str] = None
        candidate = payload
        match = DATA_URI_RE.match(payload)
        if match:
            mime_type = match.group("mime")
            candidate = match.group("data")
        try:
            blob = base64.b64decode(candidate, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ProxyError("images 字段必须是 base64 字符串或 data URI") from exc
        return blob, mime_type

    def save_request_images(
        self,
        *,
        request: Request,
        messages: List[OllamaMessage],
        trace: TraceLogger,
    ) -> List[SavedBridgeFile]:
        public_base = self._resolve_public_base_url(request)
        saved: List[SavedBridgeFile] = []

        total_images = sum(len(msg.images or []) for msg in messages)
        if total_images > self.settings.max_images_per_request:
            raise ProxyError(f"图片数量超过限制: {total_images} > {self.settings.max_images_per_request}")

        for msg_index, msg in enumerate(messages, start=1):
            for file_index, image_payload in enumerate(msg.images or [], start=1):
                if image_payload.startswith("http://") or image_payload.startswith("https://"):
                    # 用户如果已经给了可访问 URL，直接桥接为外部地址，不再重新存储
                    split = urlsplit(image_payload)
                    name = sanitize_filename(Path(split.path).name or f"msg{msg_index:03d}_img{file_index:03d}.url")
                    saved.append(
                        SavedBridgeFile(
                            request_message_index=msg_index,
                            file_index=file_index,
                            name=name,
                            relative_path=f"remote/{name}",
                            abs_path=self.settings.bridge_root / "remote" / name,
                            size=0,
                            url=image_payload,
                        )
                    )
                    trace.log(
                        "image_bridge_reuse_remote_url",
                        message_index=msg_index,
                        file_index=file_index,
                        name=name,
                        url=image_payload,
                    )
                    continue

                blob, mime_type = self._decode_base64_image(image_payload)
                if len(blob) > self.settings.max_single_image_bytes:
                    raise ProxyError(
                        f"单张图片超过限制: {len(blob)} > {self.settings.max_single_image_bytes}"
                    )

                ext = MIME_TO_EXT.get(mime_type or "", detect_image_extension(blob))
                digest = hashlib.sha256(blob).hexdigest()
                day = datetime.now(timezone.utc).strftime("%Y/%m/%d")
                relative_path = Path(day) / f"{digest}.{ext}"
                abs_path = self.settings.bridge_root / relative_path
                abs_path.parent.mkdir(parents=True, exist_ok=True)
                if not abs_path.exists():
                    abs_path.write_bytes(blob)

                name = sanitize_filename(f"msg{msg_index:03d}_img{file_index:03d}.{ext}")
                url = f"{public_base}{self.settings.bridge_route.rstrip('/')}/{relative_path.as_posix()}"
                saved_file = SavedBridgeFile(
                    request_message_index=msg_index,
                    file_index=file_index,
                    name=name,
                    relative_path=str(relative_path),
                    abs_path=abs_path,
                    size=len(blob),
                    url=url,
                )
                saved.append(saved_file)
                trace.log(
                    "image_bridge_saved",
                    message_index=msg_index,
                    file_index=file_index,
                    name=name,
                    size=len(blob),
                    relative_path=str(relative_path),
                    url=url,
                )
        return saved


# =====================================================================
# 4) Message adaptation
# =====================================================================


def normalize_message_content(content: Optional[Union[str, List[Any]]]) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text" and isinstance(item.get("text"), str):
                    parts.append(item["text"])
                else:
                    parts.append(json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


def build_backend_query_from_chat(
    request: ChatRequest,
    saved_files: List[SavedBridgeFile],
) -> BackendBuildResult:
    files_by_message: Dict[int, List[SavedBridgeFile]] = {}
    for file in saved_files:
        files_by_message.setdefault(file.request_message_index, []).append(file)

    lines: List[str] = [
        "<ollama_proxy_request version=\"2\">",
        "<adapter_notice>",
        "本请求来自兼容 Ollama 的代理层。",
        "role=tool 表示工具执行结果，不是用户输入。",
        "assistant.tool_calls 表示模型提议调用的函数。",
        "若消息中引用了 attached_images，请结合 QueryExtends.Files 中同名文件理解。",
        "</adapter_notice>",
    ]

    if request.tools:
        lines.extend([
            "<available_tools>",
            json.dumps(request.tools, ensure_ascii=False),
            "</available_tools>",
        ])

    if request.format is not None:
        lines.extend([
            "<required_output_format>",
            json.dumps(request.format, ensure_ascii=False),
            "</required_output_format>",
        ])

    if request.think is not None:
        lines.extend([
            f"<reasoning_mode>{request.think}</reasoning_mode>",
        ])

    for index, msg in enumerate(request.messages, start=1):
        attrs = [f'index="{index}"', f'role="{msg.role}"']
        if msg.tool_name:
            attrs.append(f'tool_name="{sanitize_filename(msg.tool_name)}"')
        lines.append(f"<message {' '.join(attrs)}>")

        content = normalize_message_content(msg.content)
        if content:
            lines.append("<content>")
            lines.append(content)
            lines.append("</content>")

        if msg.thinking:
            lines.append("<thinking>")
            lines.append(msg.thinking)
            lines.append("</thinking>")

        if msg.tool_calls:
            lines.append("<tool_calls>")
            lines.append(
                json.dumps([call.model_dump(exclude_none=True) for call in msg.tool_calls], ensure_ascii=False)
            )
            lines.append("</tool_calls>")

        if files_by_message.get(index):
            image_names = [item.name for item in files_by_message[index]]
            lines.append("<attached_images>")
            lines.append(json.dumps(image_names, ensure_ascii=False))
            lines.append("</attached_images>")

        lines.append("</message>")

    lines.append("</ollama_proxy_request>")

    query_extends = None
    if saved_files:
        query_extends = {"Files": [item.to_query_extends_file() for item in saved_files]}

    return BackendBuildResult(content="\n".join(lines), query_extends=query_extends)


def build_backend_query_from_generate(
    request: GenerateRequest,
    saved_files: List[SavedBridgeFile],
) -> BackendBuildResult:
    messages: List[OllamaMessage] = []
    if request.system:
        messages.append(OllamaMessage(role="system", content=request.system))
    messages.append(OllamaMessage(role="user", content=request.prompt, images=request.images))

    synthetic_chat = ChatRequest(
        model=request.model,
        messages=messages,
        tools=None,
        format=request.format,
        stream=request.stream,
        think=request.think,
        keep_alive=request.keep_alive,
        options=request.options,
    )
    result = build_backend_query_from_chat(synthetic_chat, saved_files)

    extra_lines: List[str] = []
    if request.suffix:
        extra_lines.extend(["<suffix>", request.suffix, "</suffix>"])
    if request.raw is not None:
        extra_lines.append(f"<raw_mode>{str(request.raw).lower()}</raw_mode>")

    if extra_lines:
        return BackendBuildResult(
            content=result.content + "\n" + "\n".join(extra_lines),
            query_extends=result.query_extends,
        )
    return result


# =====================================================================
# 5) SSE parsing / Ollama chunk mapping
# =====================================================================


class SSEParser:
    def __init__(self, trace: TraceLogger) -> None:
        self.trace = trace

    def parse(self, resp: ResponseLike) -> Generator[ParsedSSEEvent, None, None]:
        current_event: Optional[str] = None
        data_lines: List[str] = []
        raw_lines: List[str] = []

        for raw in resp.iter_lines(chunk_size=4, decode_unicode=False):
            if raw is None:
                continue
            line = raw if isinstance(raw, str) else raw.decode("utf-8", errors="replace")
            self.trace.log("backend_sse_line", line=line)

            # 部分后端会把 event 和 data 压在同一行，做兼容解析
            combined = COMBINED_SSE_RE.match(line)
            if combined:
                current_event = combined.group("event")
                data_lines.append(combined.group("data"))
                raw_lines.append(line)
                yield self._flush(current_event, data_lines, raw_lines)
                current_event = None
                data_lines = []
                raw_lines = []
                continue

            if line == "":
                if data_lines or current_event or raw_lines:
                    yield self._flush(current_event, data_lines, raw_lines)
                    current_event = None
                    data_lines = []
                    raw_lines = []
                continue

            raw_lines.append(line)
            if line.startswith(":"):
                continue
            if line.startswith("event:"):
                current_event = line.split(":", 1)[1].strip()
                continue
            if line.startswith("data:"):
                data_lines.append(line.split(":", 1)[1].lstrip())
                continue

        if data_lines or current_event or raw_lines:
            yield self._flush(current_event, data_lines, raw_lines)

    def _flush(
        self,
        event_name: Optional[str],
        data_lines: List[str],
        raw_lines: List[str],
    ) -> ParsedSSEEvent:
        data_text = "\n".join(data_lines).strip()
        data_json: Optional[Dict[str, Any]] = None
        if data_text:
            try:
                loaded = json.loads(data_text)
                if isinstance(loaded, dict):
                    data_json = loaded
                else:
                    data_json = {"value": loaded}
            except json.JSONDecodeError:
                data_json = None

        event = ParsedSSEEvent(
            event_name=event_name,
            data_text=data_text,
            data_json=data_json,
            raw_lines=list(raw_lines),
        )
        self.trace.log(
            "backend_sse_event",
            event_name=event.event_name,
            data_text=event.data_text,
            data_json=event.data_json,
        )
        return event


def pick_first_text(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value:
            return value
    return ""


def normalize_tool_calls(candidate: Any) -> List[Dict[str, Any]]:
    if not candidate:
        return []

    if isinstance(candidate, dict):
        candidate = [candidate]
    if not isinstance(candidate, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for item in candidate:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "function" and isinstance(item.get("function"), dict):
            fn = dict(item["function"])
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {"raw": args}
            if not isinstance(args, dict):
                args = {"value": args}
            fn["arguments"] = args
            normalized.append({"type": "function", "function": fn})
            continue

        if "name" in item:
            args = item.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {"raw": args}
            if not isinstance(args, dict):
                args = {"value": args}
            normalized.append(
                {
                    "type": "function",
                    "function": {
                        "name": item["name"],
                        "description": item.get("description"),
                        "arguments": args,
                    },
                }
            )
            continue

    return normalized


def extract_tool_calls_from_backend_event(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ("tool_calls", "tools"):
        normalized = normalize_tool_calls(data.get(key))
        if normalized:
            return normalized

    for key in ("function_call", "function"):
        payload = data.get(key)
        if isinstance(payload, dict):
            normalized = normalize_tool_calls(payload)
            if normalized:
                return normalized

    if isinstance(data.get("tool_name"), str):
        arguments = data.get("arguments") or data.get("tool_args") or {}
        normalized = normalize_tool_calls(
            {
                "name": data["tool_name"],
                "description": data.get("description"),
                "arguments": arguments,
            }
        )
        if normalized:
            return normalized

    answer = data.get("answer")
    if isinstance(answer, str):
        try:
            loaded = json.loads(answer)
        except json.JSONDecodeError:
            return []
        return normalize_tool_calls(loaded)

    return []


def build_base_chunk(model_name: str, done: bool) -> Dict[str, Any]:
    return {
        "model": model_name,
        "created_at": utcnow_iso(),
        "done": done,
    }


def process_backend_event(
    *,
    event: ParsedSSEEvent,
    aggregate: StreamAggregate,
    model_name: str,
    mode: Literal["chat", "generate"],
    include_thinking: bool,
    pass_tool_message_as_thinking: bool,
    trace: TraceLogger,
) -> List[Dict[str, Any]]:
    data = event.data_json or {}
    semantic_event = pick_first_text(data.get("event"), event.event_name)
    aggregate.last_status = semantic_event or aggregate.last_status

    if isinstance(data.get("task_id"), str):
        aggregate.task_id = data["task_id"]
    if isinstance(data.get("id"), str):
        aggregate.message_id = data["id"]
    if isinstance(data.get("conversation_id"), str):
        aggregate.backend_conversation_id = data["conversation_id"]

    chunks: List[Dict[str, Any]] = []

    if semantic_event in {"message", "message_replace"}:
        text = pick_first_text(data.get("answer"), data.get("content"), data.get("message"))
        if text:
            aggregate.content_parts.append(text)
            chunk = build_base_chunk(model_name, done=False)
            if mode == "chat":
                chunk["message"] = {"role": "assistant", "content": text}
            else:
                chunk["response"] = text
            chunks.append(chunk)

    elif semantic_event in {"agent_thought", "think_message"}:
        thought = pick_first_text(
            data.get("agent_thought"),
            data.get("thinking"),
            data.get("answer"),
            data.get("content"),
        )
        if thought:
            aggregate.thinking_parts.append(thought)
            if include_thinking:
                chunk = build_base_chunk(model_name, done=False)
                if mode == "chat":
                    chunk["message"] = {"role": "assistant", "content": "", "thinking": thought}
                else:
                    chunk["response"] = ""
                    chunk["thinking"] = thought
                chunks.append(chunk)

    elif semantic_event == "tool_message":
        tool_calls = extract_tool_calls_from_backend_event(data)
        if tool_calls:
            aggregate.tool_calls.extend(tool_calls)
            if mode == "chat":
                chunk = build_base_chunk(model_name, done=False)
                chunk["message"] = {"role": "assistant", "content": "", "tool_calls": tool_calls}
                chunks.append(chunk)
        elif pass_tool_message_as_thinking:
            tool_text = pick_first_text(data.get("answer"), data.get("content"), data.get("message"))
            if tool_text and include_thinking:
                aggregate.thinking_parts.append(tool_text)
                chunk = build_base_chunk(model_name, done=False)
                if mode == "chat":
                    chunk["message"] = {"role": "assistant", "content": "", "thinking": tool_text}
                else:
                    chunk["response"] = ""
                    chunk["thinking"] = tool_text
                chunks.append(chunk)

    elif semantic_event == "message_failed":
        detail = pick_first_text(data.get("message"), data.get("answer"), event.data_text) or "backend returned message_failed"
        trace.log("backend_message_failed", detail=detail, raw=data)
        raise BackendMessageFailed(detail)

    trace.log(
        "backend_event_mapped",
        semantic_event=semantic_event,
        emitted_chunks=chunks,
        aggregate_status={
            "task_id": aggregate.task_id,
            "message_id": aggregate.message_id,
            "backend_conversation_id": aggregate.backend_conversation_id,
            "content_chars": sum(len(p) for p in aggregate.content_parts),
            "thinking_chars": sum(len(p) for p in aggregate.thinking_parts),
            "tool_calls": len(aggregate.tool_calls),
        },
    )
    return chunks


def make_final_chunk(
    *,
    model_name: str,
    mode: Literal["chat", "generate"],
    duration_ns: int,
) -> Dict[str, Any]:
    chunk = build_base_chunk(model_name, done=True)
    chunk["done_reason"] = "stop"
    chunk["total_duration"] = duration_ns
    if mode == "chat":
        chunk["message"] = {"role": "assistant", "content": ""}
    else:
        chunk["response"] = ""
    return chunk


# =====================================================================
# 6) FastAPI app factory
# =====================================================================


class DefaultBackend:
    """
    默认适配器：实际接入时把你的真实函数注入到这里。
    真实接入要求：chat_query_v2_sse 包装层必须能接收 query_extends。
    """

    def __init__(self, create_conversation_fn: Any, chat_query_v2_sse_fn: Any) -> None:
        self._create_conversation_fn = create_conversation_fn
        self._chat_query_v2_sse_fn = chat_query_v2_sse_fn

    def create_conversation(self) -> str:
        return self._create_conversation_fn()

    def chat_query_v2_sse(
        self,
        *,
        user_id: str,
        app_conversation_id: str,
        content: str,
        query_extends: Optional[Dict[str, Any]] = None,
    ) -> ResponseLike:
        try:
            return self._chat_query_v2_sse_fn(
                user_id=user_id,
                app_conversation_id=app_conversation_id,
                content=content,
                query_extends=query_extends,
            )
        except TypeError as exc:
            if query_extends:
                raise ProxyError(
                    "真实 chat_query_v2_sse 包装层尚未支持 query_extends；要支持图片，必须在你的底层包装层把 QueryExtends 透传到真实 HTTP 请求。"
                ) from exc
            return self._chat_query_v2_sse_fn(
                user_id=user_id,
                app_conversation_id=app_conversation_id,
                content=content,
            )


class MockRequestsResponse:
    def __init__(self, lines: List[str], status_code: int = 200) -> None:
        self._lines = lines
        self.status_code = status_code

    def iter_lines(self, chunk_size: int = 512, decode_unicode: bool = False) -> Iterable[bytes | str]:
        for line in self._lines:
            yield line if decode_unicode else line.encode("utf-8")


class MockBackend:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []
        self.response_lines: List[str] = [
            "event: text",
            'data: {"event":"message_start","task_id":"task-1"}',
            "",
            "event: text",
            'data: {"event":"message","answer":"你好","conversation_id":"backend-conv-1"}',
            "",
            "event: text",
            'data: {"event":"message_end","id":"msg-1"}',
            "",
        ]

    def create_conversation(self) -> str:
        return "mock-app-conversation-id"

    def chat_query_v2_sse(
        self,
        *,
        user_id: str,
        app_conversation_id: str,
        content: str,
        query_extends: Optional[Dict[str, Any]] = None,
    ) -> ResponseLike:
        self.calls.append(
            {
                "user_id": user_id,
                "app_conversation_id": app_conversation_id,
                "content": content,
                "query_extends": query_extends,
            }
        )
        return MockRequestsResponse(self.response_lines)


def create_app(
    backend: BackendProtocol,
    settings: Optional[ProxySettings] = None,
) -> FastAPI:
    settings = settings or ProxySettings()
    settings.ensure_dirs()
    image_bridge = ImageBridgeService(settings)

    app = FastAPI(title="Ollama Proxy Service V2", version="2.0.0")
    app.state.backend = backend
    app.state.settings = settings
    app.mount(settings.bridge_route, StaticFiles(directory=settings.bridge_root), name="bridge")

    def resolve_user_id(request: Request) -> str:
        return (
            request.headers.get("x-user-id")
            or request.headers.get("x-forwarded-user")
            or settings.default_user_id
        )

    def start_trace(request: Request, endpoint: str, payload: Dict[str, Any]) -> tuple[str, TraceLogger]:
        trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex
        trace = TraceLogger(settings.logs_root, trace_id)
        trace.log(
            "request_received",
            endpoint=endpoint,
            method=request.method,
            path=str(request.url.path),
            query=str(request.url.query),
            headers={
                "x-user-id": request.headers.get("x-user-id"),
                "x-forwarded-user": request.headers.get("x-forwarded-user"),
                "host": request.headers.get("host"),
                "content-type": request.headers.get("content-type"),
            },
            payload=payload if settings.log_payloads else "<hidden>",
        )
        return trace_id, trace

    def open_backend_stream(
        *,
        user_id: str,
        backend_payload: BackendBuildResult,
        trace: TraceLogger,
    ) -> tuple[str, ResponseLike]:
        try:
            app_conversation_id = app.state.backend.create_conversation()
            trace.log("conversation_created", app_conversation_id=app_conversation_id)
        except (ValueError, requests.RequestException) as exc:
            trace.log("conversation_create_failed", error=str(exc))
            raise HTTPException(status_code=502, detail=f"create_conversation failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            trace.log("conversation_create_failed", error=str(exc))
            raise HTTPException(status_code=500, detail=f"create_conversation failed: {exc}") from exc

        try:
            resp = app.state.backend.chat_query_v2_sse(
                user_id=user_id,
                app_conversation_id=app_conversation_id,
                content=backend_payload.content,
                query_extends=backend_payload.query_extends,
            )
            trace.log(
                "backend_request_sent",
                app_conversation_id=app_conversation_id,
                query_extends=backend_payload.query_extends,
                content=backend_payload.content if settings.log_payloads else "<hidden>",
                response_status=getattr(resp, "status_code", None),
            )
            if getattr(resp, "status_code", 200) >= 400:
                raise HTTPException(
                    status_code=502,
                    detail=f"backend returned status {getattr(resp, 'status_code', 'unknown')}",
                )
            return app_conversation_id, resp
        except HTTPException:
            raise
        except (ValueError, requests.RequestException, ProxyError) as exc:
            trace.log("backend_request_failed", error=str(exc))
            raise HTTPException(status_code=502, detail=f"chat_query_v2_sse failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            trace.log("backend_request_failed", error=str(exc))
            raise HTTPException(status_code=500, detail=f"chat_query_v2_sse failed: {exc}") from exc

    def ndjson_stream(
        *,
        resp: ResponseLike,
        trace: TraceLogger,
        model_name: str,
        mode: Literal["chat", "generate"],
        include_thinking: bool,
        app_conversation_id: str,
    ) -> Generator[str, None, None]:
        parser = SSEParser(trace)
        aggregate = StreamAggregate(app_conversation_id=app_conversation_id)
        start_ns = monotonic_ns()
        final_emitted = False

        try:
            for parsed_event in parser.parse(resp):
                chunks = process_backend_event(
                    event=parsed_event,
                    aggregate=aggregate,
                    model_name=model_name,
                    mode=mode,
                    include_thinking=include_thinking,
                    pass_tool_message_as_thinking=settings.pass_tool_message_as_thinking,
                    trace=trace,
                )
                for chunk in chunks:
                    serialized = json.dumps(chunk, ensure_ascii=False)
                    trace.log("ollama_chunk_emitted", chunk=chunk)
                    yield serialized + "\n"

            duration_ns = monotonic_ns() - start_ns
            final_chunk = make_final_chunk(
                model_name=model_name,
                mode=mode,
                duration_ns=duration_ns,
            )
            trace.log(
                "ollama_stream_completed",
                final_chunk=final_chunk,
                aggregate={
                    "content": "".join(aggregate.content_parts),
                    "thinking": "".join(aggregate.thinking_parts),
                    "tool_calls": aggregate.tool_calls,
                    "task_id": aggregate.task_id,
                    "message_id": aggregate.message_id,
                    "backend_conversation_id": aggregate.backend_conversation_id,
                    "app_conversation_id": aggregate.app_conversation_id,
                    "last_status": aggregate.last_status,
                },
            )
            final_emitted = True
            yield json.dumps(final_chunk, ensure_ascii=False) + "\n"
        except BackendMessageFailed as exc:
            error_payload = {"error": str(exc)}
            trace.log("ollama_stream_failed", error=error_payload)
            yield json.dumps(error_payload, ensure_ascii=False) + "\n"
        except Exception as exc:  # noqa: BLE001
            error_payload = {"error": f"Internal Model Error: {exc}"}
            trace.log("ollama_stream_failed", error=error_payload)
            yield json.dumps(error_payload, ensure_ascii=False) + "\n"
        finally:
            trace.log("stream_generator_exit", final_emitted=final_emitted)

    def collect_non_stream_result(
        *,
        resp: ResponseLike,
        trace: TraceLogger,
        model_name: str,
        mode: Literal["chat", "generate"],
        include_thinking: bool,
        app_conversation_id: str,
    ) -> Dict[str, Any]:
        parser = SSEParser(trace)
        aggregate = StreamAggregate(app_conversation_id=app_conversation_id)
        start_ns = monotonic_ns()

        for parsed_event in parser.parse(resp):
            process_backend_event(
                event=parsed_event,
                aggregate=aggregate,
                model_name=model_name,
                mode=mode,
                include_thinking=include_thinking,
                pass_tool_message_as_thinking=settings.pass_tool_message_as_thinking,
                trace=trace,
            )

        total_duration = monotonic_ns() - start_ns
        if mode == "chat":
            message: Dict[str, Any] = {
                "role": "assistant",
                "content": "".join(aggregate.content_parts),
            }
            if include_thinking and aggregate.thinking_parts:
                message["thinking"] = "".join(aggregate.thinking_parts)
            if aggregate.tool_calls:
                message["tool_calls"] = aggregate.tool_calls
            payload: Dict[str, Any] = {
                "model": model_name,
                "created_at": utcnow_iso(),
                "message": message,
                "done": True,
                "done_reason": aggregate.done_reason,
                "total_duration": total_duration,
            }
        else:
            payload = {
                "model": model_name,
                "created_at": utcnow_iso(),
                "response": "".join(aggregate.content_parts),
                "done": True,
                "done_reason": aggregate.done_reason,
                "total_duration": total_duration,
            }
            if include_thinking and aggregate.thinking_parts:
                payload["thinking"] = "".join(aggregate.thinking_parts)

        trace.log(
            "ollama_non_stream_response",
            response=payload,
            aggregate={
                "task_id": aggregate.task_id,
                "message_id": aggregate.message_id,
                "backend_conversation_id": aggregate.backend_conversation_id,
                "app_conversation_id": aggregate.app_conversation_id,
                "last_status": aggregate.last_status,
            },
        )
        return payload

    @app.get("/healthz")
    async def healthz() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/version")
    async def api_version() -> Dict[str, str]:
        return {"version": app.version}

    @app.post("/api/chat")
    async def ollama_api_chat(request: Request, body: ChatRequest):
        trace_id, trace = start_trace(request, "/api/chat", body.model_dump(mode="json"))
        user_id = resolve_user_id(request)

        try:
            saved_files = image_bridge.save_request_images(request=request, messages=body.messages, trace=trace)
            backend_payload = build_backend_query_from_chat(body, saved_files)
            app_conversation_id, resp = open_backend_stream(
                user_id=user_id,
                backend_payload=backend_payload,
                trace=trace,
            )

            if body.stream:
                headers = {"x-trace-id": trace_id}
                return StreamingResponse(
                    ndjson_stream(
                        resp=resp,
                        trace=trace,
                        model_name=body.model,
                        mode="chat",
                        include_thinking=bool(body.think),
                        app_conversation_id=app_conversation_id,
                    ),
                    media_type="application/x-ndjson",
                    headers=headers,
                )

            response_payload = collect_non_stream_result(
                resp=resp,
                trace=trace,
                model_name=body.model,
                mode="chat",
                include_thinking=bool(body.think),
                app_conversation_id=app_conversation_id,
            )
            return JSONResponse(response_payload, headers={"x-trace-id": trace_id})

        except HTTPException as exc:
            trace.log("request_failed", error=exc.detail, status_code=exc.status_code)
            raise
        except ProxyError as exc:
            trace.log("request_failed", error=str(exc), status_code=400)
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001
            trace.log("request_failed", error=str(exc), status_code=500)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/api/generate")
    async def ollama_api_generate(request: Request, body: GenerateRequest):
        trace_id, trace = start_trace(request, "/api/generate", body.model_dump(mode="json"))
        user_id = resolve_user_id(request)

        try:
            synthetic_messages = [OllamaMessage(role="user", content=body.prompt, images=body.images)]
            saved_files = image_bridge.save_request_images(request=request, messages=synthetic_messages, trace=trace)
            backend_payload = build_backend_query_from_generate(body, saved_files)
            app_conversation_id, resp = open_backend_stream(
                user_id=user_id,
                backend_payload=backend_payload,
                trace=trace,
            )

            if body.stream:
                headers = {"x-trace-id": trace_id}
                return StreamingResponse(
                    ndjson_stream(
                        resp=resp,
                        trace=trace,
                        model_name=body.model,
                        mode="generate",
                        include_thinking=bool(body.think),
                        app_conversation_id=app_conversation_id,
                    ),
                    media_type="application/x-ndjson",
                    headers=headers,
                )

            response_payload = collect_non_stream_result(
                resp=resp,
                trace=trace,
                model_name=body.model,
                mode="generate",
                include_thinking=bool(body.think),
                app_conversation_id=app_conversation_id,
            )
            return JSONResponse(response_payload, headers={"x-trace-id": trace_id})

        except HTTPException as exc:
            trace.log("request_failed", error=exc.detail, status_code=exc.status_code)
            raise
        except ProxyError as exc:
            trace.log("request_failed", error=str(exc), status_code=400)
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:  # noqa: BLE001
            trace.log("request_failed", error=str(exc), status_code=500)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return app


# =====================================================================
# 7) Real integration example placeholders
# =====================================================================


def create_conversation() -> str:
    """
    TODO: 替换成你的真实函数导入。
    """
    raise NotImplementedError("请注入真实 create_conversation")



def chat_query_v2_sse(
    *,
    user_id: str,
    app_conversation_id: str,
    content: str,
    query_extends: Optional[Dict[str, Any]] = None,
) -> requests.models.Response:
    """
    TODO: 替换成你的真实函数导入。
    注意：若要支持图片，必须把 query_extends 透传到底层真实 HTTP 请求的 QueryExtends 字段。
    """
    raise NotImplementedError("请注入真实 chat_query_v2_sse")


if __name__ == "__main__":
    import uvicorn

    runtime_root = Path(os.environ.get("OLLAMA_PROXY_RUNTIME_ROOT", "./runtime"))
    public_base_url = os.environ.get("OLLAMA_PROXY_PUBLIC_BASE_URL")
    backend = MockBackend()
    settings = ProxySettings(runtime_root=runtime_root, public_base_url=public_base_url)
    app = create_app(backend=backend, settings=settings)
    uvicorn.run(app, host="0.0.0.0", port=11434)
