from __future__ import annotations

import base64
import hashlib
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests

from .config import settings
from .models import UpstreamFile


def _guess_ext(media_type: Optional[str], filename_hint: str = "") -> str:
    if filename_hint and "." in filename_hint:
        return "." + filename_hint.rsplit(".", 1)[1]
    if media_type:
        ext = mimetypes.guess_extension(media_type)
        if ext:
            return ext
    return ".bin"


def _sanitize_filename(name: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in name)
    return safe or "file.bin"


def _build_storage_name(raw: bytes, ext: str, filename_hint: str = "") -> str:
    if filename_hint:
        hint = _sanitize_filename(filename_hint)
        stem, hint_ext = os.path.splitext(hint)
        final_ext = hint_ext or ext
        digest = hashlib.sha256(raw).hexdigest()[:12]
        return f"{stem}_{digest}{final_ext}"
    digest = hashlib.sha256(raw).hexdigest()[:16]
    return f"{settings.upload_filename_prefix}_{digest}{ext}"


def _store_bytes(raw: bytes, media_type: Optional[str], filename_hint: str = "") -> UpstreamFile:
    ext = _guess_ext(media_type, filename_hint)
    storage_name = _build_storage_name(raw, ext, filename_hint)
    relative_path = f"{settings.media_subdir}/{storage_name}" if settings.media_subdir else storage_name
    full_path = settings.media_dir / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    if not full_path.exists():
        full_path.write_bytes(raw)
    return UpstreamFile(
        name=storage_name,
        path=relative_path,
        size=full_path.stat().st_size,
        url=f"{settings.public_base_url}{settings.media_url_prefix}/{relative_path}",
    )


def save_base64_image(source: Dict[str, Any]) -> UpstreamFile:
    media_type = source.get("media_type", "application/octet-stream")
    raw = base64.b64decode(source["data"])
    filename_hint = source.get("filename") or ""
    return _store_bytes(raw, media_type=media_type, filename_hint=filename_hint)


def download_and_rehost(url: str) -> UpstreamFile:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    raw = response.content
    parsed = urlparse(url)
    filename_hint = Path(parsed.path).name
    return _store_bytes(raw, media_type=response.headers.get("Content-Type"), filename_hint=filename_hint)


def image_block_to_upstream_file(block: Dict[str, Any]) -> UpstreamFile:
    source = block.get("source", {})
    source_type = source.get("type")
    if source_type == "base64":
        return save_base64_image(source)
    if source_type == "url":
        url = source["url"]
        return download_and_rehost(url)
    if source_type == "file":
        raise ValueError("当前示例代理未实现 Anthropic Files API/file_id 到本地文件的映射，请改用 image.source.type=url 或 base64。")
    raise ValueError(f"不支持的图片 source.type: {source_type}")
