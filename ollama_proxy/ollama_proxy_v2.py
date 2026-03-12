from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Literal, Optional, Tuple

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field


# ============================================================================
# Configuration
# ============================================================================

APP_NAME = os.getenv("APP_NAME", "Ollama Proxy Service")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "11434"))
OLLAMA_VERSION = os.getenv("OLLAMA_VERSION", "0.12.6")
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "ollama_proxy_user")
EXTERNAL_BASE_URL = os.getenv("EXTERNAL_BASE_URL", f"http://localhost:{PORT}")
IMAGE_STORAGE_DIR = Path(os.getenv("IMAGE_STORAGE_DIR", "/tmp/ollama-proxy-images"))
IMAGE_BRIDGE_PREFIX = os.getenv("IMAGE_BRIDGE_PREFIX", "/bridge/files")
DEFAULT_SESSION_TTL_SECONDS = int(os.getenv("DEFAULT_SESSION_TTL_SECONDS", "1800"))
UPSTREAM_TIMEOUT_SECONDS = int(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "600"))
STRICT_COMPAT = os.getenv("STRICT_COMPAT", "false").lower() == "true"
USE_MOCK_UPSTREAM = os.getenv("USE_MOCK_UPSTREAM", "true").lower() == "true"
MAX_IMAGE_BYTES = int(os.getenv("MAX_IMAGE_BYTES", str(20 * 1024 * 1024)))

IMAGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Model registry
# In production, replace with configuration center / database.
# ============================================================================

MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "internal-chat": {
        "name": "internal-chat",
        "model": "internal-chat",
        "modified_at": "2026-03-12T00:00:00Z",
        "size": 0,
        "digest": "proxy-internal-chat",
        "details": {
            "format": "proxy",
            "family": "custom",
            "families": ["custom"],
            "parameter_size": "unknown",
            "quantization_level": "unknown",
        },
        "capabilities": ["completion", "vision"],
        "parameters": "temperature 0.7\n num_ctx 8192",
        "license": "Internal model proxy",
        "model_info": {
            "proxy.context_length": 8192,
        },
    }
}


# ============================================================================
# Pydantic request models compatible with Ollama's request shapes
# ============================================================================


class ToolFunction(BaseModel):
    name: str
    description: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    function: ToolFunction


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str = ""
    images: Optional[List[str]] = None
    thinking: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_name: Optional[str] = None


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: bool = True
    options: Optional[Dict[str, Any]] = None
    format: Optional[Any] = None
    think: Optional[Any] = None
    keep_alive: Optional[Any] = None
    logprobs: Optional[bool] = None
    top_logprobs: Optional[int] = None
    tools: Optional[List[Dict[str, Any]]] = None


class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: bool = True
    options: Optional[Dict[str, Any]] = None
    format: Optional[Any] = None
    think: Optional[Any] = None
    keep_alive: Optional[Any] = None
    logprobs: Optional[bool] = None
    top_logprobs: Optional[int] = None
    system: Optional[str] = None
    suffix: Optional[str] = None
    raw: Optional[bool] = None
    images: Optional[List[str]] = None


class ShowRequest(BaseModel):
    model: str


# ============================================================================
# Data classes
# ============================================================================


@dataclass
class BridgeFile:
    token: str
    file_path: Path
    rel_path: str
    url: str
    size: int
    name: str
    content_type: str
    sha256: str
    expires_at: float


@dataclass
class PrefixEntry:
    conversation_id: str
    expires_at: float
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass
class StreamAccumulator:
    content: str = ""
    thinking: str = ""
    done_reason: str = "stop"
    failed: bool = False
    task_id: Optional[str] = None
    message_id: Optional[str] = None
    raw_events: List[Dict[str, Any]] = field(default_factory=list)


# ============================================================================
# Utility functions
# ============================================================================


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_keep_alive_to_seconds(value: Any) -> int:
    if value in (None, ""):
        return DEFAULT_SESSION_TTL_SECONDS
    if value == 0 or value == "0":
        return 0
    if isinstance(value, (int, float)):
        return max(0, int(value))
    if isinstance(value, str):
        text = value.strip().lower()
        try:
            return int(text)
        except ValueError:
            pass
        units = {"ms": 0.001, "s": 1, "m": 60, "h": 3600}
        for unit, factor in units.items():
            if text.endswith(unit):
                num = float(text[: -len(unit)])
                return max(0, int(num * factor))
    return DEFAULT_SESSION_TTL_SECONDS


def guess_extension_and_mime(data: bytes) -> Tuple[str, str]:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg", "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png", "image/png"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp", "image/webp"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif", "image/gif"
    if data.startswith(b"BM"):
        return ".bmp", "image/bmp"
    return ".bin", "application/octet-stream"


def strip_data_url_prefix(value: str) -> str:
    if value.startswith("data:") and "," in value:
        return value.split(",", 1)[1]
    return value


def decode_b64_image(image_b64: str) -> bytes:
    cleaned = strip_data_url_prefix(image_b64).strip()
    try:
        data = base64.b64decode(cleaned, validate=True)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"invalid base64 image payload: {exc}") from exc
    if not data:
        raise HTTPException(status_code=400, detail="empty image payload")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail=f"image too large: {len(data)} bytes")
    return data


# ============================================================================
# Image bridge: converts Ollama base64 images into stable URLs for upstream QueryExtends.Files
# ============================================================================


class ImageBridge:
    def __init__(self, storage_dir: Path, external_base_url: str, url_prefix: str) -> None:
        self.storage_dir = storage_dir
        self.external_base_url = external_base_url.rstrip("/")
        self.url_prefix = url_prefix.rstrip("/")
        self._lock = threading.RLock()
        self._token_index: Dict[str, BridgeFile] = {}

    def put_images(self, images: Optional[List[str]], ttl_seconds: int) -> List[Dict[str, Any]]:
        if not images:
            return []
        out: List[Dict[str, Any]] = []
        for idx, image_b64 in enumerate(images, start=1):
            raw = decode_b64_image(image_b64)
            sha = hashlib.sha256(raw).hexdigest()
            ext, content_type = guess_extension_and_mime(raw)
            date_prefix = datetime.utcnow().strftime("%Y/%m/%d")
            file_dir = self.storage_dir / date_prefix
            file_dir.mkdir(parents=True, exist_ok=True)
            file_name = f"{sha}{ext}"
            file_path = file_dir / file_name
            if not file_path.exists():
                file_path.write_bytes(raw)
            token = uuid.uuid4().hex
            rel_path = f"bridge/{date_prefix}/{file_name}"
            url = f"{self.external_base_url}{self.url_prefix}/{token}/{file_name}"
            bridge_file = BridgeFile(
                token=token,
                file_path=file_path,
                rel_path=rel_path,
                url=url,
                size=len(raw),
                name=f"image_{idx}{ext}",
                content_type=content_type,
                sha256=sha,
                expires_at=time.time() + ttl_seconds,
            )
            with self._lock:
                self._token_index[token] = bridge_file
            out.append(
                {
                    "Name": bridge_file.name,
                    "Path": bridge_file.rel_path,
                    "Size": bridge_file.size,
                    "Url": bridge_file.url,
                }
            )
        return out

    def get(self, token: str) -> BridgeFile:
        self._cleanup_locked()
        with self._lock:
            item = self._token_index.get(token)
            if not item:
                raise HTTPException(status_code=404, detail="bridge file not found")
            return item

    def _cleanup_locked(self) -> None:
        now = time.time()
        with self._lock:
            expired = [token for token, item in self._token_index.items() if item.expires_at <= now]
            for token in expired:
                self._token_index.pop(token, None)


# ============================================================================
# Conversation store: maps stateless Ollama message history to stateful upstream conversations
# ============================================================================


class ConversationStore:
    ROOT = "root"

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._prefix_map: Dict[str, PrefixEntry] = {}

    def set_prefix(self, prefix_hash: str, conversation_id: str, ttl_seconds: int) -> None:
        expires_at = time.time() + ttl_seconds if ttl_seconds > 0 else time.time()
        with self._lock:
            self._prefix_map[prefix_hash] = PrefixEntry(
                conversation_id=conversation_id,
                expires_at=expires_at,
                updated_at=time.time(),
            )
            self._cleanup_locked()

    def find_best_prefix(self, messages: List[Message]) -> Tuple[int, Optional[PrefixEntry], List[str]]:
        prefix_hashes = self.compute_prefix_hashes(messages)
        self._cleanup_locked()
        with self._lock:
            for idx in range(len(prefix_hashes) - 1, -1, -1):
                key = prefix_hashes[idx]
                entry = self._prefix_map.get(key)
                if entry and entry.expires_at > time.time():
                    return idx, entry, prefix_hashes
        return 0, None, prefix_hashes

    def compute_prefix_hashes(self, messages: List[Message]) -> List[str]:
        hashes = [self.ROOT]
        cursor = self.ROOT.encode("utf-8")
        for msg in messages:
            images = msg.images or []
            image_digests = [sha256_text(img) for img in images]
            payload = json.dumps(
                {
                    "role": msg.role,
                    "content": msg.content,
                    "thinking": msg.thinking or "",
                    "tool_name": msg.tool_name or "",
                    "tool_calls": [tc.model_dump() for tc in (msg.tool_calls or [])],
                    "images": image_digests,
                },
                sort_keys=True,
                ensure_ascii=False,
            ).encode("utf-8")
            cursor = hashlib.sha256(cursor + b"\n" + payload).hexdigest().encode("utf-8")
            hashes.append(cursor.decode("utf-8"))
        return hashes

    def _cleanup_locked(self) -> None:
        now = time.time()
        with self._lock:
            expired = [k for k, v in self._prefix_map.items() if v.expires_at <= now]
            for key in expired:
                self._prefix_map.pop(key, None)


# ============================================================================
# Upstream client wrappers
# Replace the body of create_conversation() and chat_query_v2_sse() with your real implementation.
# ============================================================================


class UpstreamResponse:
    """Minimal adapter used by the mock mode."""

    def __init__(self, lines: Iterable[bytes], status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        self._lines = list(lines)
        self.status_code = status_code
        self.headers = headers or {}
        self.text = b"\n".join(self._lines).decode("utf-8", errors="replace")

    def iter_lines(self, chunk_size: int = 512, decode_unicode: bool = False):
        for line in self._lines:
            yield line.decode("utf-8") if decode_unicode else line

    def close(self) -> None:
        return None


class BaseUpstreamClient:
    def create_conversation(self, user_id: str, model: str) -> str:
        raise NotImplementedError

    def chat_query_v2_sse(
        self,
        *,
        user_id: str,
        app_conversation_id: str,
        content: str,
        query_extends: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        think: Optional[Any] = None,
    ) -> requests.Response | UpstreamResponse:
        raise NotImplementedError


class MockUpstreamClient(BaseUpstreamClient):
    def create_conversation(self, user_id: str, model: str) -> str:
        return f"mock-conv-{uuid.uuid4().hex[:12]}"

    def chat_query_v2_sse(
        self,
        *,
        user_id: str,
        app_conversation_id: str,
        content: str,
        query_extends: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        think: Optional[Any] = None,
    ) -> UpstreamResponse:
        task_id = uuid.uuid4().hex
        answer = f"[mock:{model or 'default'}] {content}"
        thinking = "[mock-thinking] 正在组织答案..." if think else ""
        lines: List[bytes] = []
        lines.append(f"data: {json.dumps({'event': 'message_start', 'task_id': task_id, 'id': task_id})}".encode())
        if thinking:
            lines.append(f"data: {json.dumps({'event': 'think_message_output_start', 'task_id': task_id})}".encode())
            lines.append(f"data: {json.dumps({'event': 'think_message', 'task_id': task_id, 'answer': thinking})}".encode())
            lines.append(f"data: {json.dumps({'event': 'think_message_output_end', 'task_id': task_id})}".encode())
        for ch in answer:
            lines.append(
                f"data: {json.dumps({'event': 'message', 'task_id': task_id, 'id': task_id, 'answer': ch, 'conversation_id': app_conversation_id})}".encode()
            )
        lines.append(
            f"data: {json.dumps({'event': 'message_end', 'task_id': task_id, 'id': task_id, 'conversation_id': app_conversation_id})}".encode()
        )
        return UpstreamResponse(lines)


class PlaceholderRealUpstreamClient(BaseUpstreamClient):
    """
    Replace with the real HTTP SDK integration.

    You said only two functions are currently available, so this class intentionally mirrors them.
    """

    def create_conversation(self, user_id: str, model: str) -> str:
        raise NotImplementedError(
            "请把 create_conversation() 的真实调用接到这里；可以按 model 做路由。"
        )

    def chat_query_v2_sse(
        self,
        *,
        user_id: str,
        app_conversation_id: str,
        content: str,
        query_extends: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        think: Optional[Any] = None,
    ) -> requests.Response:
        raise NotImplementedError(
            "请把 chat_query_v2_sse() 的真实调用接到这里，并把 QueryExtends 透传进去。"
        )


UPSTREAM_CLIENT: BaseUpstreamClient = MockUpstreamClient() if USE_MOCK_UPSTREAM else PlaceholderRealUpstreamClient()


# ============================================================================
# Payload building and compatibility strategy
# ============================================================================


def get_user_id(http_request: Request) -> str:
    header_user_id = http_request.headers.get("x-user-id")
    auth = http_request.headers.get("authorization", "")
    if header_user_id:
        return header_user_id
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        return f"bearer:{hashlib.sha256(token.encode()).hexdigest()[:16]}"
    client = http_request.client.host if http_request.client else DEFAULT_USER_ID
    return f"ip:{client}"


def resolve_model_or_raise(model: str) -> Dict[str, Any]:
    item = MODEL_REGISTRY.get(model)
    if not item:
        raise HTTPException(status_code=404, detail=f"model not found: {model}")
    return item


def validate_unsupported_fields_for_chat(req: ChatRequest) -> None:
    if req.tools and STRICT_COMPAT:
        raise HTTPException(status_code=501, detail="tools are not supported by the current upstream adapter")
    if req.logprobs and STRICT_COMPAT:
        raise HTTPException(status_code=501, detail="logprobs are not supported by the current upstream adapter")


def validate_unsupported_fields_for_generate(req: GenerateRequest) -> None:
    if req.logprobs and STRICT_COMPAT:
        raise HTTPException(status_code=501, detail="logprobs are not supported by the current upstream adapter")


def last_user_message(messages: List[Message]) -> Message:
    for msg in reversed(messages):
        if msg.role == "user":
            return msg
    raise HTTPException(status_code=400, detail="at least one user message is required")


def render_history_as_prompt(messages: List[Message]) -> str:
    """
    Fallback strategy used when the request cannot be attached to an existing upstream stateful conversation.
    It is not semantically perfect, but it preserves compatibility for edited / branched / imported chats.
    """
    lines = [
        "以下是完整对话历史。请基于这些历史继续回答最后一条用户消息。",
        "不要复述角色标签，不要解释你在读取历史。",
        "",
    ]
    for msg in messages:
        role = msg.role.upper()
        lines.append(f"[{role}]")
        if msg.thinking:
            lines.append(f"(thinking omitted in proxy replay) {msg.thinking}")
        if msg.tool_name:
            lines.append(f"tool_name: {msg.tool_name}")
        if msg.content:
            lines.append(msg.content)
        if msg.images:
            img_markers = [f"image:{sha256_text(img)[:12]}" for img in msg.images]
            lines.append("images: " + ", ".join(img_markers))
        if msg.tool_calls:
            lines.append("tool_calls: " + json.dumps([tc.model_dump() for tc in msg.tool_calls], ensure_ascii=False))
        lines.append("")
    return "\n".join(lines).strip()


def build_generate_content(req: GenerateRequest) -> str:
    if req.raw:
        return req.prompt
    chunks: List[str] = []
    if req.system:
        chunks.append(f"[SYSTEM]\n{req.system}")
    chunks.append(req.prompt)
    if req.suffix:
        chunks.append(f"[SUFFIX]\n请让输出和以下后缀自然衔接：\n{req.suffix}")
    return "\n\n".join(chunks)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()


# ============================================================================
# SSE parsing and Ollama NDJSON conversion
# ============================================================================


class UpstreamSseParser:
    @staticmethod
    def iter_events(resp: requests.Response | UpstreamResponse) -> Generator[Dict[str, Any], None, None]:
        pending_event_name: Optional[str] = None
        pending_data_lines: List[str] = []

        def flush() -> Optional[Dict[str, Any]]:
            if not pending_data_lines:
                return None
            data_str = "\n".join(pending_data_lines).strip()
            pending_data_lines.clear()
            if not data_str:
                return None
            try:
                payload = json.loads(data_str)
            except json.JSONDecodeError:
                return {"event": pending_event_name or "unknown", "raw": data_str}
            if isinstance(payload, dict) and "event" not in payload and pending_event_name:
                payload["event"] = pending_event_name
            return payload if isinstance(payload, dict) else {"event": pending_event_name or "unknown", "data": payload}

        try:
            for raw_line in resp.iter_lines(chunk_size=512, decode_unicode=True):
                line = (raw_line or "").strip()
                if not line:
                    event = flush()
                    if event is not None:
                        yield event
                    pending_event_name = None
                    continue
                if line.startswith(":"):
                    continue
                if line.startswith("event:") and "data:" in line:
                    before, after = line.split("data:", 1)
                    pending_event_name = before[len("event:") :].strip() or pending_event_name
                    pending_data_lines.append(after.strip())
                    event = flush()
                    if event is not None:
                        yield event
                    pending_event_name = None
                    continue
                if line.startswith("event:"):
                    pending_event_name = line[len("event:") :].strip() or pending_event_name
                    continue
                if line.startswith("data:"):
                    pending_data_lines.append(line[len("data:") :].strip())
                    # Upstream payload appears to be single-line JSON in practice.
                    event = flush()
                    if event is not None:
                        yield event
                    pending_event_name = None
                    continue
                if "data:" in line:
                    pending_data_lines.append(line.split("data:", 1)[1].strip())
                    event = flush()
                    if event is not None:
                        yield event
                    pending_event_name = None
                    continue
            event = flush()
            if event is not None:
                yield event
        finally:
            try:
                resp.close()
            except Exception:  # noqa: BLE001
                pass


# ============================================================================
# Proxy service
# ============================================================================


bridge = ImageBridge(IMAGE_STORAGE_DIR, EXTERNAL_BASE_URL, IMAGE_BRIDGE_PREFIX)
conversation_store = ConversationStore()
app = FastAPI(title=APP_NAME)


class ProxyService:
    def __init__(self, upstream: BaseUpstreamClient, image_bridge: ImageBridge, store: ConversationStore) -> None:
        self.upstream = upstream
        self.image_bridge = image_bridge
        self.store = store
        self.runtime_model_activity: Dict[str, float] = {}
        self._lock = threading.RLock()

    def _mark_model_active(self, model: str) -> None:
        with self._lock:
            self.runtime_model_activity[model] = time.time()

    def resolve_chat_session(
        self,
        req: ChatRequest,
        user_id: str,
    ) -> Tuple[str, str, int, List[str], List[Dict[str, Any]]]:
        ttl_seconds = parse_keep_alive_to_seconds(req.keep_alive)
        matched_prefix_len, prefix_entry, prefix_hashes = self.store.find_best_prefix(req.messages)
        remaining = req.messages[matched_prefix_len:]

        if prefix_entry and len(remaining) == 1 and remaining[0].role == "user":
            bridged_files = self.image_bridge.put_images(
                remaining[0].images, ttl_seconds or DEFAULT_SESSION_TTL_SECONDS
            )
            return prefix_entry.conversation_id, remaining[0].content, ttl_seconds, prefix_hashes, bridged_files

        conversation_id = self.upstream.create_conversation(user_id=user_id, model=req.model)
        if len(req.messages) == 1 and req.messages[0].role == "user":
            content = req.messages[0].content
            bridged_files = self.image_bridge.put_images(
                req.messages[0].images, ttl_seconds or DEFAULT_SESSION_TTL_SECONDS
            )
        else:
            content = render_history_as_prompt(req.messages)
            all_history_images: List[str] = []
            for message in req.messages:
                if message.images:
                    all_history_images.extend(message.images)
            bridged_files = self.image_bridge.put_images(
                all_history_images, ttl_seconds or DEFAULT_SESSION_TTL_SECONDS
            )
        return conversation_id, content, ttl_seconds, prefix_hashes, bridged_files

    def resolve_generate_session(
        self,
        req: GenerateRequest,
        user_id: str,
    ) -> Tuple[str, str, int, List[Dict[str, Any]]]:
        ttl_seconds = parse_keep_alive_to_seconds(req.keep_alive)
        bridged_files = self.image_bridge.put_images(req.images, ttl_seconds or DEFAULT_SESSION_TTL_SECONDS)
        content = build_generate_content(req)
        conversation_id = self.upstream.create_conversation(user_id=user_id, model=req.model)
        return conversation_id, content, ttl_seconds, bridged_files

    def _ollama_chunk_for_chat(
        self,
        *,
        model: str,
        content: str = "",
        thinking: str = "",
        done: bool = False,
        done_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        message: Dict[str, Any] = {"role": "assistant", "content": content}
        if thinking:
            message["thinking"] = thinking
        out: Dict[str, Any] = {
            "model": model,
            "created_at": now_iso(),
            "message": message,
            "done": done,
        }
        if done_reason:
            out["done_reason"] = done_reason
        return out

    def _ollama_chunk_for_generate(
        self,
        *,
        model: str,
        response: str = "",
        thinking: str = "",
        done: bool = False,
        done_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "model": model,
            "created_at": now_iso(),
            "response": response,
            "done": done,
        }
        if thinking:
            out["thinking"] = thinking
        if done_reason:
            out["done_reason"] = done_reason
        return out

    def stream_chat(self, req: ChatRequest, user_id: str) -> Generator[str, None, None]:
        self._mark_model_active(req.model)
        conversation_id, content, ttl_seconds, prefix_hashes, bridged_files = self.resolve_chat_session(req, user_id)
        query_extends = {"Files": bridged_files} if bridged_files else None
        resp = self.upstream.chat_query_v2_sse(
            user_id=user_id,
            app_conversation_id=conversation_id,
            content=content,
            query_extends=query_extends,
            model=req.model,
            options=req.options,
            think=req.think,
        )
        if getattr(resp, "status_code", 200) >= 400:
            raise HTTPException(status_code=502, detail=f"upstream error: {getattr(resp, 'text', '')}")

        accumulator = StreamAccumulator()
        for event in UpstreamSseParser.iter_events(resp):
            accumulator.raw_events.append(event)
            event_name = event.get("event", "")
            accumulator.task_id = accumulator.task_id or event.get("task_id")
            accumulator.message_id = accumulator.message_id or event.get("id")

            if event_name in {"message", "message_replace"}:
                text = str(event.get("answer", ""))
                if text:
                    accumulator.content += text
                    yield json.dumps(self._ollama_chunk_for_chat(model=req.model, content=text), ensure_ascii=False) + "\n"
                continue

            if event_name in {"agent_thought", "think_message"} and req.think:
                thought = str(event.get("answer") or event.get("thinking") or event.get("content") or "")
                if thought:
                    accumulator.thinking += thought
                    yield json.dumps(self._ollama_chunk_for_chat(model=req.model, thinking=thought), ensure_ascii=False) + "\n"
                continue

            if event_name in {"message_failed"}:
                accumulator.failed = True
                accumulator.done_reason = "error"
                yield json.dumps(
                    {
                        "error": {
                            "message": event.get("message") or event.get("answer") or "upstream message_failed",
                            "type": "upstream_error",
                        }
                    },
                    ensure_ascii=False,
                ) + "\n"
                break

            if event_name in {"message_end", "message_output_end"}:
                yield json.dumps(
                    self._ollama_chunk_for_chat(
                        model=req.model,
                        content="",
                        done=True,
                        done_reason=accumulator.done_reason,
                    ),
                    ensure_ascii=False,
                ) + "\n"
                break

        if not accumulator.failed and ttl_seconds > 0:
            full_messages = list(req.messages)
            full_messages.append(
                Message(role="assistant", content=accumulator.content, thinking=accumulator.thinking or None)
            )
            full_hash = self.store.compute_prefix_hashes(full_messages)[-1]
            self.store.set_prefix(full_hash, conversation_id, ttl_seconds)
            # Also keep the prefix ending at the request side, to support retry / trace lookup.
            self.store.set_prefix(prefix_hashes[-1], conversation_id, ttl_seconds)

    def collect_chat(self, req: ChatRequest, user_id: str) -> Dict[str, Any]:
        content = ""
        thinking = ""
        for chunk in self.stream_chat(req, user_id):
            obj = json.loads(chunk)
            if "error" in obj:
                raise HTTPException(status_code=502, detail=obj["error"]["message"])
            msg = obj.get("message", {})
            content += msg.get("content", "")
            thinking += msg.get("thinking", "")
        payload = self._ollama_chunk_for_chat(model=req.model, content=content, done=True, done_reason="stop")
        if thinking:
            payload["message"]["thinking"] = thinking
        return payload

    def stream_generate(self, req: GenerateRequest, user_id: str) -> Generator[str, None, None]:
        self._mark_model_active(req.model)
        conversation_id, content, ttl_seconds, bridged_files = self.resolve_generate_session(req, user_id)
        query_extends = {"Files": bridged_files} if bridged_files else None
        resp = self.upstream.chat_query_v2_sse(
            user_id=user_id,
            app_conversation_id=conversation_id,
            content=content,
            query_extends=query_extends,
            model=req.model,
            options=req.options,
            think=req.think,
        )
        if getattr(resp, "status_code", 200) >= 400:
            raise HTTPException(status_code=502, detail=f"upstream error: {getattr(resp, 'text', '')}")

        accumulator = StreamAccumulator()
        for event in UpstreamSseParser.iter_events(resp):
            accumulator.raw_events.append(event)
            event_name = event.get("event", "")
            accumulator.task_id = accumulator.task_id or event.get("task_id")
            accumulator.message_id = accumulator.message_id or event.get("id")

            if event_name in {"message", "message_replace"}:
                text = str(event.get("answer", ""))
                if text:
                    accumulator.content += text
                    yield json.dumps(self._ollama_chunk_for_generate(model=req.model, response=text), ensure_ascii=False) + "\n"
                continue

            if event_name in {"agent_thought", "think_message"} and req.think:
                thought = str(event.get("answer") or event.get("thinking") or event.get("content") or "")
                if thought:
                    accumulator.thinking += thought
                    yield json.dumps(self._ollama_chunk_for_generate(model=req.model, thinking=thought), ensure_ascii=False) + "\n"
                continue

            if event_name in {"message_failed"}:
                accumulator.failed = True
                accumulator.done_reason = "error"
                yield json.dumps(
                    {
                        "error": {
                            "message": event.get("message") or event.get("answer") or "upstream message_failed",
                            "type": "upstream_error",
                        }
                    },
                    ensure_ascii=False,
                ) + "\n"
                break

            if event_name in {"message_end", "message_output_end"}:
                yield json.dumps(
                    self._ollama_chunk_for_generate(
                        model=req.model,
                        response="",
                        done=True,
                        done_reason=accumulator.done_reason,
                    ),
                    ensure_ascii=False,
                ) + "\n"
                break

    def collect_generate(self, req: GenerateRequest, user_id: str) -> Dict[str, Any]:
        response = ""
        thinking = ""
        for chunk in self.stream_generate(req, user_id):
            obj = json.loads(chunk)
            if "error" in obj:
                raise HTTPException(status_code=502, detail=obj["error"]["message"])
            response += obj.get("response", "")
            thinking += obj.get("thinking", "")
        payload = self._ollama_chunk_for_generate(model=req.model, response=response, done=True, done_reason="stop")
        if thinking:
            payload["thinking"] = thinking
        return payload

    def running_models_payload(self) -> Dict[str, Any]:
        now = time.time()
        models = []
        for model_name, last_used in list(self.runtime_model_activity.items()):
            if now - last_used > DEFAULT_SESSION_TTL_SECONDS:
                continue
            registry_item = MODEL_REGISTRY.get(model_name)
            if not registry_item:
                continue
            models.append(
                {
                    "name": registry_item["name"],
                    "model": registry_item["model"],
                    "size": registry_item["size"],
                    "digest": registry_item["digest"],
                    "details": registry_item["details"],
                    "expires_at": datetime.fromtimestamp(last_used + DEFAULT_SESSION_TTL_SECONDS, tz=timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "size_vram": 0,
                    "context_length": registry_item.get("model_info", {}).get("proxy.context_length", 0),
                }
            )
        return {"models": models}


proxy_service = ProxyService(UPSTREAM_CLIENT, bridge, conversation_store)


# ============================================================================
# FastAPI routes
# ============================================================================


@app.get("/api/version")
def api_version() -> Dict[str, str]:
    return {"version": OLLAMA_VERSION}


@app.get("/api/tags")
def api_tags() -> Dict[str, Any]:
    return {"models": [MODEL_REGISTRY[name] for name in sorted(MODEL_REGISTRY.keys())]}


@app.get("/api/ps")
def api_ps() -> Dict[str, Any]:
    return proxy_service.running_models_payload()


@app.post("/api/show")
def api_show(req: ShowRequest) -> Dict[str, Any]:
    item = resolve_model_or_raise(req.model)
    return {
        "parameters": item.get("parameters", ""),
        "license": item.get("license", ""),
        "capabilities": item.get("capabilities", ["completion"]),
        "modified_at": item["modified_at"],
        "details": item["details"],
        "model_info": item.get("model_info", {}),
    }


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.get(f"{IMAGE_BRIDGE_PREFIX}/{{token}}/{{file_name}}")
def serve_bridge_file(token: str, file_name: str):
    item = bridge.get(token)
    if item.file_path.name != file_name:
        raise HTTPException(status_code=404, detail="bridge file name mismatch")
    media_type = item.content_type or mimetypes.guess_type(item.file_path.name)[0] or "application/octet-stream"
    return FileResponse(item.file_path, media_type=media_type, filename=item.name)


@app.post("/api/chat")
def api_chat(req: ChatRequest, http_request: Request):
    resolve_model_or_raise(req.model)
    validate_unsupported_fields_for_chat(req)
    user_id = get_user_id(http_request)
    if req.stream:
        return StreamingResponse(
            proxy_service.stream_chat(req, user_id),
            media_type="application/x-ndjson",
        )
    return JSONResponse(proxy_service.collect_chat(req, user_id))


@app.post("/api/generate")
def api_generate(req: GenerateRequest, http_request: Request):
    resolve_model_or_raise(req.model)
    validate_unsupported_fields_for_generate(req)
    user_id = get_user_id(http_request)
    if req.stream:
        return StreamingResponse(
            proxy_service.stream_generate(req, user_id),
            media_type="application/x-ndjson",
        )
    return JSONResponse(proxy_service.collect_generate(req, user_id))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ollama_proxy_v2:app", host=HOST, port=PORT, reload=False)
