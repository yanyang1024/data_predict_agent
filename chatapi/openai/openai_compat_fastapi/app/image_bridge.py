from __future__ import annotations

import base64
import hashlib
import mimetypes
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from .config import Settings
from .schemas import BackendFile

DATA_URL_RE = re.compile(r"^data:(?P<mime>[-\w.+/]+);base64,(?P<data>.+)$", re.DOTALL)


class BridgeResult:
    def __init__(self, backend_file: BackendFile, local_path: Optional[Path] = None):
        self.backend_file = backend_file
        self.local_path = local_path



def _guess_extension(mime: Optional[str]) -> str:
    if mime:
        ext = mimetypes.guess_extension(mime.split(";")[0].strip())
        if ext:
            return ext
    return ".bin"



def _filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    candidate = Path(parsed.path).name or "image"
    return candidate



def _safe_relative_path(path: Path, base_parent: Path) -> str:
    try:
        return str(path.relative_to(base_parent))
    except ValueError:
        return str(path)



def bridge_image_url(url: str, settings: Settings) -> BridgeResult:
    match = DATA_URL_RE.match(url)
    if match:
        mime = match.group("mime")
        binary = base64.b64decode(match.group("data"))
        sha = hashlib.sha256(binary).hexdigest()
        ext = _guess_extension(mime)
        filename = f"{sha}{ext}"
        local_path = settings.bridge_dir / filename
        if not local_path.exists():
            local_path.write_bytes(binary)
        public_url = f"{settings.public_base_url.rstrip('/')}{settings.bridge_route}/{filename}"
        backend_file = BackendFile(
            Name=filename,
            Path=_safe_relative_path(local_path, settings.bridge_dir.parent),
            Size=len(binary),
            Url=public_url,
        )
        return BridgeResult(backend_file=backend_file, local_path=local_path)

    if url.startswith("http://") or url.startswith("https://"):
        name = _filename_from_url(url)
        backend_file = BackendFile(Name=name, Path=name, Size=None, Url=url)
        return BridgeResult(backend_file=backend_file, local_path=None)

    # 非标准场景：本地绝对/相对文件路径
    path = Path(url).expanduser().resolve()
    if path.exists() and path.is_file():
        binary = path.read_bytes()
        sha = hashlib.sha256(binary).hexdigest()
        ext = path.suffix or ".bin"
        filename = f"{sha}{ext}"
        local_path = settings.bridge_dir / filename
        if not local_path.exists():
            local_path.write_bytes(binary)
        public_url = f"{settings.public_base_url.rstrip('/')}{settings.bridge_route}/{filename}"
        backend_file = BackendFile(
            Name=path.name,
            Path=_safe_relative_path(local_path, settings.bridge_dir.parent),
            Size=path.stat().st_size,
            Url=public_url,
        )
        return BridgeResult(backend_file=backend_file, local_path=local_path)

    raise ValueError(f"Unsupported image url/path: {url[:128]}")
