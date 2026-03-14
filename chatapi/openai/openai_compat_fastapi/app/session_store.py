from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Dict, Optional


class FileSessionStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _load(self) -> Dict[str, str]:
        if not self.path.exists():
            return {}
        raw = self.path.read_text(encoding="utf-8").strip() or "{}"
        return json.loads(raw)

    def get(self, session_key: str) -> Optional[str]:
        with self._lock:
            data = self._load()
            return data.get(session_key)

    def set(self, session_key: str, conversation_id: str) -> None:
        with self._lock:
            data = self._load()
            data[session_key] = conversation_id
            self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
