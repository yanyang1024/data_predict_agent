from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile

from ..config import settings


@dataclass(frozen=True)
class WorkspaceFile:
    path: str
    name: str
    type: str
    size: int
    updated_at: datetime | None


class WorkspaceManager:
    """Per-user sandbox workspace with strict path traversal protection."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or settings.workspace_root_path).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def workspace_dir(self, user_id: int, conversation_id: str) -> Path:
        base = (self.root / f"user-{user_id}" / conversation_id).resolve()
        base.mkdir(parents=True, exist_ok=True)
        return base

    def _not_found(self) -> HTTPException:
        return HTTPException(status_code=404, detail="Not found")

    def safe_path(self, user_id: int, conversation_id: str, rel_path: str | None) -> Path:
        """Four layers: null/absolute rejection, normalization, resolve, relative_to boundary check."""

        rel = rel_path or "."
        if "\x00" in rel:
            raise self._not_found()
        candidate = Path(rel)
        if candidate.is_absolute() or (os.name == "nt" and ":" in candidate.parts[0]):
            raise self._not_found()
        normalized = Path(os.path.normpath(str(candidate)))
        if str(normalized).startswith("..") or ".." in normalized.parts:
            raise self._not_found()
        base = self.workspace_dir(user_id, conversation_id)
        resolved = (base / normalized).resolve()
        try:
            resolved.relative_to(base)
        except ValueError as exc:
            raise self._not_found() from exc
        return resolved

    def list_tree(self, user_id: int, conversation_id: str, rel_path: str | None = ".") -> list[WorkspaceFile]:
        target = self.safe_path(user_id, conversation_id, rel_path)
        if not target.exists():
            raise self._not_found()
        if target.is_file():
            stat = target.stat()
            return [WorkspaceFile(path=str(Path(rel_path or target.name)), name=target.name, type="file", size=stat.st_size, updated_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc))]
        items: list[WorkspaceFile] = []
        base = self.workspace_dir(user_id, conversation_id)
        for child in sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            stat = child.stat()
            items.append(
                WorkspaceFile(
                    path=str(child.relative_to(base)),
                    name=child.name,
                    type="dir" if child.is_dir() else "file",
                    size=0 if child.is_dir() else stat.st_size,
                    updated_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc),
                )
            )
        return items

    def read_text(self, user_id: int, conversation_id: str, rel_path: str) -> tuple[str, str]:
        target = self.safe_path(user_id, conversation_id, rel_path)
        if not target.exists() or not target.is_file():
            raise self._not_found()
        data = target.read_bytes()
        for encoding in ("utf-8", "gbk", "latin-1"):
            try:
                return data.decode(encoding), encoding
            except UnicodeDecodeError:
                continue
        return data.decode("latin-1", errors="replace"), "latin-1"

    def write_text(self, user_id: int, conversation_id: str, rel_path: str, content: str, encoding: str = "utf-8") -> None:
        target = self.safe_path(user_id, conversation_id, rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding=encoding)

    async def save_upload(self, user_id: int, conversation_id: str, rel_path: str, upload: UploadFile) -> str:
        target = self.safe_path(user_id, conversation_id, rel_path or upload.filename or "upload.bin")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as f:
            while chunk := await upload.read(1024 * 1024):
                f.write(chunk)
        base = self.workspace_dir(user_id, conversation_id)
        return str(target.relative_to(base))

    def delete(self, user_id: int, conversation_id: str, rel_path: str) -> None:
        target = self.safe_path(user_id, conversation_id, rel_path)
        if not target.exists():
            raise self._not_found()
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()


workspace_manager = WorkspaceManager()
