from __future__ import annotations

import threading
from typing import Dict, Optional

from .models import SessionState


class InMemorySessionStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._data: Dict[str, SessionState] = {}

    def get(self, proxy_conversation_id: str) -> Optional[SessionState]:
        with self._lock:
            return self._data.get(proxy_conversation_id)

    def upsert(self, proxy_conversation_id: str, state: SessionState) -> None:
        with self._lock:
            self._data[proxy_conversation_id] = state

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


session_store = InMemorySessionStore()
