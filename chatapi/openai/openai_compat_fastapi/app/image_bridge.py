from __future__ import annotations

import base64
import hashlib
import mimetypes
import re
from pathlib import Path
from typing import Optional
from urllib.parse import quote, unquote, urlparse

import httpx

from .config import Settings
from .schemas import BackendFile

DATA_URL_RE = re.compile(r"^data:(?P<mime>[-\w.+/]+);base64,(?P<data>.+)$", re.DOTALL)
SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


class BridgeResult:
    def __init__(self, backend_file: BackendFile, local_path: Optional[Path] = None):
        self.backend_file = backend_file
        self.local_path = local_path


class BridgedImageSource:
    def __init__(self, binary: bytes, mime: Optional[str], source_name: Optional[str], source: str):
        self.binary = binary
        self.mime = mime
        self.source_name = source_name
        self.source = source



def _guess_extension(mime: Optional[str], filename: Optional[str] = None) -> str:
    if filename:
        suffix = Path(filename).suffix
        if suffix:
            return suffix
    if mime:
        ext = mimetypes.guess_extension(mime.split(";", 1)[0].strip())
        if ext:
            return ext
    return ".bin"



def _filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    candidate = unquote(Path(parsed.path).name or "")
    return candidate or "image"



def _sanitize_filename(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    normalized = unquote(Path(name).name).strip().replace("\x00", "")
    normalized = SAFE_FILENAME_RE.sub("_", normalized)
    normalized = normalized.strip("._")
    return normalized or None



def _safe_relative_path(path: Path, base_parent: Path) -> str:
    try:
        return str(path.relative_to(base_parent))
    except ValueError:
        return str(path)



def _load_source_image(url: str, settings: Settings) -> BridgedImageSource:
    match = DATA_URL_RE.match(url)
    if match:
        mime = match.group("mime")
        binary = base64.b64decode(match.group("data"))
        return BridgedImageSource(binary=binary, mime=mime, source_name=None, source="data_url")

    if url.startswith("http://") or url.startswith("https://"):
        if not settings.download_remote_images:
            raise ValueError("Remote image download is disabled by DOWNLOAD_REMOTE_IMAGES=false")
        with httpx.Client(
            timeout=settings.remote_image_timeout_seconds,
            follow_redirects=True,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            mime = response.headers.get("content-type")
            source_name = _filename_from_url(url)
            return BridgedImageSource(
                binary=response.content,
                mime=mime,
                source_name=source_name,
                source="remote_url",
            )

    if url.startswith("file://"):
        parsed = urlparse(url)
        path = Path(unquote(parsed.path)).expanduser().resolve()
    else:
        path = Path(url).expanduser().resolve()

    if path.exists() and path.is_file():
        return BridgedImageSource(
            binary=path.read_bytes(),
            mime=mimetypes.guess_type(path.name)[0],
            source_name=path.name,
            source="local_file",
        )

    raise ValueError(f"Unsupported image url/path: {url[:256]}")



def _resolve_filename(
    source: BridgedImageSource,
    settings: Settings,
    preferred_name: Optional[str] = None,
) -> str:
    sha = hashlib.sha256(source.binary).hexdigest()
    candidate = _sanitize_filename(preferred_name) or _sanitize_filename(source.source_name)
    ext = _guess_extension(source.mime, candidate)
    if candidate:
        candidate_path = Path(candidate)
        stem = _sanitize_filename(candidate_path.stem) or f"{settings.generated_image_name_prefix}{sha[:12]}"
        suffix = candidate_path.suffix or ext
        return f"{stem}{suffix}"
    return f"{settings.generated_image_name_prefix}{sha[:12]}{ext}"



def _persist_file(binary: bytes, filename: str, settings: Settings) -> Path:
    local_path = settings.bridge_dir / filename
    if local_path.exists():
        try:
            if local_path.read_bytes() == binary:
                return local_path
        except OSError:
            pass
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        sha = hashlib.sha256(binary).hexdigest()[:12]
        local_path = settings.bridge_dir / f"{stem}_{sha}{suffix}"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(binary)
    return local_path



def _build_public_url(local_path: Path, relative_path: str, settings: Settings) -> str:
    url_base = settings.resolved_bridge_public_url_base.rstrip("/")
    if settings.bridge_use_relative_path_in_url:
        tail_parts = [quote(part) for part in Path(relative_path).parts]
    else:
        tail_parts = [quote(local_path.name)]
    return f"{url_base}/{'/'.join(tail_parts)}"



def bridge_image_url(url: str, settings: Settings, preferred_name: Optional[str] = None) -> BridgeResult:
    source = _load_source_image(url=url, settings=settings)
    filename = _resolve_filename(source=source, settings=settings, preferred_name=preferred_name)
    local_path = _persist_file(binary=source.binary, filename=filename, settings=settings)
    relative_path = _safe_relative_path(local_path, settings.bridge_dir.parent)
    public_url = _build_public_url(local_path=local_path, relative_path=relative_path, settings=settings)
    backend_file = BackendFile(
        Name=local_path.name,
        Path=relative_path,
        Size=len(source.binary),
        Url=public_url,
    )
    return BridgeResult(backend_file=backend_file, local_path=local_path)
