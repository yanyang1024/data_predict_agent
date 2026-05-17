from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from threading import Lock

from ..config import settings


@dataclass
class AgentConfig:
    id: str
    name: str
    description: str
    category: str = "general"
    domains: list[str] | None = None
    skills: list[str] | None = None
    icon: str = "bot"
    system_prompt: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["domains"] = data.get("domains") or []
        data["skills"] = data.get("skills") or []
        return data


class AgentManager:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or settings.agent_root_path).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._mtime_snapshot: dict[str, float] = {}
        self._cache: dict[str, AgentConfig] = {}

    def _frontmatter(self, text: str) -> tuple[dict[str, str], str]:
        if not text.startswith("---"):
            return {}, text
        end = text.find("\n---", 3)
        if end < 0:
            return {}, text
        raw = text[3:end].strip().splitlines()
        body = text[end + 4 :].strip()
        meta: dict[str, str] = {}
        for line in raw:
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
        return meta, body

    def _split_csv(self, value: str | None) -> list[str]:
        if not value:
            return []
        return [x.strip() for x in value.split(",") if x.strip()]

    def _load_file(self, path: Path) -> AgentConfig:
        meta, body = self._frontmatter(path.read_text(encoding="utf-8"))
        return AgentConfig(
            id=meta.get("id", path.stem),
            name=meta.get("name", path.stem),
            description=meta.get("description", ""),
            category=meta.get("category", "general"),
            domains=self._split_csv(meta.get("domains")),
            skills=self._split_csv(meta.get("skills")),
            icon=meta.get("icon", "bot"),
            system_prompt=body,
        )

    def _snapshot(self) -> dict[str, float]:
        return {str(p): p.stat().st_mtime for p in self.root.glob("*.md")}

    def reload_if_needed(self) -> None:
        snapshot = self._snapshot()
        if snapshot == self._mtime_snapshot and self._cache:
            return
        with self._lock:
            snapshot = self._snapshot()
            if snapshot == self._mtime_snapshot and self._cache:
                return
            loaded: dict[str, AgentConfig] = {}
            for path_str in sorted(snapshot):
                cfg = self._load_file(Path(path_str))
                loaded[cfg.id] = cfg
            self._cache = loaded
            self._mtime_snapshot = snapshot

    def list_agents(self, domain: str, locale: str = "zh-CN") -> list[dict]:
        self.reload_if_needed()
        upper = domain.upper()
        result = []
        for cfg in self._cache.values():
            domains = [d.upper() for d in (cfg.domains or [])]
            if not domains or upper in domains:
                result.append(cfg.to_dict())
        return result

    def get_agent(self, agent_id: str, domain: str) -> AgentConfig | None:
        self.reload_if_needed()
        cfg = self._cache.get(agent_id)
        if cfg is None:
            return None
        domains = [d.upper() for d in (cfg.domains or [])]
        if domains and domain.upper() not in domains:
            return None
        return cfg


agent_manager = AgentManager()
