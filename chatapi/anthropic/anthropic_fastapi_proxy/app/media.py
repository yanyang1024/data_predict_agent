from __future__ import annotations

import base64
import hashlib
import mimetypes
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


def save_base64_image(source: Dict[str, Any]) -> UpstreamFile:
    media_type = source.get("media_type", "application/octet-stream")
    raw = base64.b64decode(source["data"])
    digest = hashlib.sha256(raw).hexdigest()
    ext = _guess_ext(media_type)
    filename = f"{digest}{ext}"
    path = settings.media_dir / filename
    if not path.exists():
        path.write_bytes(raw)

    return UpstreamFile(
        name=filename,
        path=str(path),
        size=path.stat().st_size,
        url=f"{settings.public_base_url}/proxy/media/{filename}",
    )


def download_and_rehost(url: str) -> UpstreamFile:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    raw = response.content
    digest = hashlib.sha256(raw).hexdigest()
    parsed = urlparse(url)
    filename_hint = Path(parsed.path).name
    ext = _guess_ext(response.headers.get("Content-Type"), filename_hint)
    filename = _sanitize_filename(f"{digest}{ext}")
    path = settings.media_dir / filename
    if not path.exists():
        path.write_bytes(raw)
    return UpstreamFile(
        name=filename_hint or filename,
        path=str(path),
        size=path.stat().st_size,
        url=f"{settings.public_base_url}/proxy/media/{filename}",
    )


def image_block_to_upstream_file(block: Dict[str, Any]) -> UpstreamFile:
    source = block.get("source", {})
    source_type = source.get("type")
    if source_type == "base64":
        return save_base64_image(source)
    if source_type == "url":
        url = source["url"]
        if settings.media_proxy_mode == "download":
            return download_and_rehost(url)
        parsed = urlparse(url)
        name = Path(parsed.path).name or "remote-image"
        return UpstreamFile(name=name, path=url, size=0, url=url)
    if source_type == "file":
        raise ValueError("当前示例代理未实现 Anthropic Files API/file_id 到本地文件的映射，请改用 image.source.type=url 或 base64。")
    raise ValueError(f"不支持的图片 source.type: {source_type}")
