from __future__ import annotations

import asyncio
import os
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from ..config import settings
from ..models import InstanceLog, User


@dataclass
class RuntimeState:
    user_id: int
    service_name: str
    port: int
    running: bool
    last_seen: datetime
    mode: str


class InstanceManager:
    """Singleton manager for per-user OpenCode systemd user services."""

    _instance: "InstanceManager | None" = None

    def __new__(cls) -> "InstanceManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._states: dict[int, RuntimeState] = {}
        self._lock = asyncio.Lock()
        self._initialized = True

    def service_name(self, user_id: int) -> str:
        return settings.USER_SERVICE_NAME_TEMPLATE.format(user_id=user_id)

    def deterministic_port(self, user: User) -> int:
        if user.employee_no is not None and user.employee_no >= 0:
            return settings.OPENCODE_BASE_PORT + int(user.employee_no)
        # Stable fallback when employee_no is not supplied.
        return settings.OPENCODE_BASE_PORT + (zlib.crc32(user.email.encode("utf-8")) % 20000)

    def env_file_path(self, user_id: int) -> Path:
        env_dir = Path(settings.SYSTEMD_ENV_DIR).expanduser().resolve()
        env_dir.mkdir(parents=True, exist_ok=True)
        return env_dir / f"{user_id}.env"

    def write_env_file(self, user: User, port: int) -> None:
        workspace_root = settings.workspace_root_path / f"user-{user.id}"
        workspace_root.mkdir(parents=True, exist_ok=True)
        content = "\n".join(
            [
                f"OPENCODE_USER_ID={user.id}",
                f"OPENCODE_PORT={port}",
                f"OPENCODE_WORKSPACE_ROOT={workspace_root}",
                f"OPENCODE_BINARY={settings.OPENCODE_BINARY}",
                f"BWRAP_PATH={settings.BWRAP_PATH}",
                f"INSTANCE_MEMORY_MAX={settings.INSTANCE_MEMORY_MAX}",
                f"INSTANCE_CPU_QUOTA={settings.INSTANCE_CPU_QUOTA}",
                "",
            ]
        )
        self.env_file_path(user.id).write_text(content, encoding="utf-8")

    async def _run(self, *args: str) -> tuple[int, str, str]:
        proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out, err = await proc.communicate()
        return proc.returncode, out.decode(errors="replace"), err.decode(errors="replace")

    def _log(self, db: Session | None, *, user_id: int, port: int, service_name: str, status: str, reason: str = "", details: dict | None = None) -> None:
        if db is None:
            return
        db.add(InstanceLog(user_id=user_id, port=port, service_name=service_name, status=status, reason=reason, details=details or {}))
        db.commit()

    async def ensure_instance(self, user: User, db: Session | None = None) -> RuntimeState:
        async with self._lock:
            now = datetime.now(timezone.utc)
            current = self._states.get(user.id)
            if current and current.running:
                current.last_seen = now
                return current

            port = self.deterministic_port(user)
            service = self.service_name(user.id)
            self.write_env_file(user, port)
            mode = "systemd" if settings.SYSTEMD_ENABLED else "mock"
            running = True
            details: dict = {"systemd_enabled": settings.SYSTEMD_ENABLED}

            if settings.SYSTEMD_ENABLED:
                await self._run("systemctl", "--user", "daemon-reload")
                code, out, err = await self._run("systemctl", "--user", "start", service)
                running = code == 0
                details.update({"code": code, "stdout": out[-4000:], "stderr": err[-4000:]})

            state = RuntimeState(user_id=user.id, service_name=service, port=port, running=running, last_seen=now, mode=mode)
            self._states[user.id] = state
            self._log(db, user_id=user.id, port=port, service_name=service, status="start" if running else "start_failed", details=details)
            return state

    async def stop_instance(self, user_id: int, db: Session | None = None, reason: str = "manual") -> RuntimeState | None:
        async with self._lock:
            state = self._states.get(user_id)
            if state is None:
                return None
            details = {"reason": reason}
            if settings.SYSTEMD_ENABLED:
                code, out, err = await self._run("systemctl", "--user", "stop", state.service_name)
                details.update({"code": code, "stdout": out[-4000:], "stderr": err[-4000:]})
            state.running = False
            self._log(db, user_id=user_id, port=state.port, service_name=state.service_name, status="stop", reason=reason, details=details)
            return state

    def touch(self, user_id: int) -> None:
        state = self._states.get(user_id)
        if state:
            state.last_seen = datetime.now(timezone.utc)

    def status(self, user_id: int) -> RuntimeState | None:
        return self._states.get(user_id)

    def running_count(self) -> int:
        return sum(1 for s in self._states.values() if s.running)

    async def shutdown_idle(self, db_factory) -> None:
        now = datetime.now(timezone.utc)
        stale = [s for s in self._states.values() if s.running and (now - s.last_seen).total_seconds() > settings.IDLE_TIMEOUT_SECONDS]
        for state in stale:
            db = db_factory()
            try:
                await self.stop_instance(state.user_id, db=db, reason="idle_timeout")
            finally:
                db.close()


instance_manager = InstanceManager()


async def idle_reaper_loop(db_factory) -> None:
    while True:
        await asyncio.sleep(settings.IDLE_SCAN_SECONDS)
        await instance_manager.shutdown_idle(db_factory)


async def sync_systemd_template() -> None:
    if not settings.SYSTEMD_ENABLED:
        return
    project_root = Path(__file__).resolve().parents[2]
    source = project_root / "systemd" / settings.SYSTEMD_TEMPLATE_NAME
    target_dir = Path(settings.SYSTEMD_USER_DIR).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    if source.exists():
        target = target_dir / settings.SYSTEMD_TEMPLATE_NAME
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        await instance_manager._run("systemctl", "--user", "daemon-reload")
