from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import audit, get_current_user
from ..config import settings
from ..database import get_db
from ..models import User, UserSkill
from ..schemas import SkillOut

router = APIRouter(prefix="/skills", tags=["skills"])


def _skill_id(skill: UserSkill) -> int:
    return skill.id


def _safe_extract_zip(upload_path: Path, dest: Path) -> dict:
    manifest: dict = {}
    with zipfile.ZipFile(upload_path) as zf:
        for info in zf.infolist():
            name = info.filename
            target = (dest / name).resolve()
            try:
                target.relative_to(dest.resolve())
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="ZIP contains unsafe path") from exc
            if name.startswith("/") or ".." in Path(name).parts:
                raise HTTPException(status_code=400, detail="ZIP contains unsafe path")
            # Refuse symlinks in zip archives.
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise HTTPException(status_code=400, detail="ZIP contains symlink")
        zf.extractall(dest)
    for manifest_name in ("skill.json", "manifest.json"):
        path = dest / manifest_name
        if path.exists():
            manifest = json.loads(path.read_text(encoding="utf-8"))
            break
    if not (dest / "SKILL.md").exists() and "entrypoint" not in manifest:
        raise HTTPException(status_code=400, detail="Skill ZIP must include SKILL.md or manifest entrypoint")
    return manifest


def _read_manifest(skill_dir: Path) -> dict:
    for manifest_name in ("skill.json", "manifest.json"):
        path = skill_dir / manifest_name
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _skill_query(user_id: int | None, domain: str, name: str):
    query = select(UserSkill).where(UserSkill.domain == domain, UserSkill.name == name)
    if user_id is None:
        return query.where(UserSkill.user_id.is_(None))
    return query.where(UserSkill.user_id == user_id)


def _sync_skill_dir(db: Session, *, user: User, skill_dir: Path, source: str, user_id: int | None) -> None:
    if not skill_dir.is_dir():
        return
    manifest = _read_manifest(skill_dir)
    entrypoint = str(manifest.get("entrypoint") or "SKILL.md")
    if not (skill_dir / entrypoint).exists() and not (skill_dir / "SKILL.md").exists():
        return
    name = str(manifest.get("name") or skill_dir.name)
    version = str(manifest.get("version") or "0.1.0")
    skill = db.scalar(_skill_query(user_id, user.domain, name))
    if skill is None:
        skill = UserSkill(user_id=user_id, domain=user.domain, name=name, path=str(skill_dir.resolve()), source=source)
        db.add(skill)
        skill.enabled = True
    elif not skill.enabled and source == "user":
        return
    skill.version = version
    skill.source = source
    skill.entrypoint = entrypoint
    skill.path = str(skill_dir.resolve())
    skill.manifest = manifest


def _sync_filesystem_skills(db: Session, user: User) -> None:
    domain_root = settings.skill_root_path / "domains" / user.domain
    candidates = [
        (domain_root / "system" / "shared", "system", None),
        (domain_root / "users" / str(user.id), "user", user.id),
    ]
    changed = False
    for root, source, user_id in candidates:
        if not root.exists():
            continue
        for skill_dir in root.iterdir():
            before = len(db.new) + len(db.dirty)
            _sync_skill_dir(db, user=user, skill_dir=skill_dir, source=source, user_id=user_id)
            changed = changed or (len(db.new) + len(db.dirty) != before)
    if db.new or db.dirty or changed:
        db.commit()


def _storage_dir(user: User, name: str, source: str = "user") -> Path:
    safe_name = "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_", ".")).strip(".") or "skill"
    root = settings.skill_root_path / "domains" / user.domain / ("users" if source == "user" else "system") / (str(user.id) if source == "user" else "shared")
    root.mkdir(parents=True, exist_ok=True)
    return (root / safe_name).resolve()


@router.get("", response_model=list[SkillOut])
async def list_skills(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[UserSkill]:
    _sync_filesystem_skills(db, user)
    return list(
        db.scalars(
            select(UserSkill).where(
                UserSkill.domain == user.domain,
                UserSkill.enabled.is_(True),
                (UserSkill.user_id == user.id) | (UserSkill.user_id.is_(None)),
            )
        )
    )


@router.post("/upload", response_model=SkillOut)
async def upload_skill(request: Request, upload: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> UserSkill:
    if not upload.filename or not upload.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip skill packages are accepted")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / "skill.zip"
        with zip_path.open("wb") as f:
            while chunk := await upload.read(1024 * 1024):
                f.write(chunk)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()
        manifest = _safe_extract_zip(zip_path, extract_dir)
        name = manifest.get("name") or Path(upload.filename).stem
        version = manifest.get("version", "0.1.0")
        dest = _storage_dir(user, name)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(extract_dir, dest)

    skill = db.scalar(select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.domain == user.domain, UserSkill.name == name))
    if skill is None:
        skill = UserSkill(user_id=user.id, domain=user.domain, name=name, path=str(dest), source="user")
        db.add(skill)
    skill.version = version
    skill.entrypoint = manifest.get("entrypoint", "SKILL.md")
    skill.manifest = manifest
    skill.enabled = True
    db.commit()
    db.refresh(skill)
    audit(db, actor=user, action="skill.upload", resource_type="skill", resource_id=str(skill.id), domain=user.domain, request=request, details={"name": name, "version": version})
    return skill


@router.get("/{skill_id}", response_model=SkillOut)
async def get_skill(skill_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> UserSkill:
    skill = db.get(UserSkill, skill_id)
    if skill is None or skill.domain != user.domain or skill.enabled is False or (skill.user_id not in (None, user.id)):
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.delete("/{skill_id}")
async def delete_skill(skill_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, bool]:
    skill = db.get(UserSkill, skill_id)
    if skill is None or skill.user_id != user.id or skill.domain != user.domain:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill.enabled = False
    db.add(skill)
    db.commit()
    audit(db, actor=user, action="skill.delete", resource_type="skill", resource_id=str(skill.id), domain=user.domain, request=request)
    return {"ok": True}
