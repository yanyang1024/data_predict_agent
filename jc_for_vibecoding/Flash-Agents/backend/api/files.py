from __future__ import annotations

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..auth import audit, get_current_user
from ..database import get_db
from ..models import Conversation, User
from ..schemas import FileOut, FileReadOut, FileWriteIn
from ..services.workspace import workspace_manager

router = APIRouter(prefix="/files", tags=["files"])


def _own_conversation(db: Session, user: User, conversation_id: str) -> Conversation:
    conv = db.get(Conversation, conversation_id)
    if conv is None or conv.user_id != user.id or conv.deleted_at is not None:
        # 404 camouflage prevents workspace enumeration.
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found")
    return conv


@router.get("/{conversation_id}", response_model=list[FileOut])
async def list_files(conversation_id: str, path: str = Query(default="."), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list:
    _own_conversation(db, user, conversation_id)
    return [item.__dict__ for item in workspace_manager.list_tree(user.id, conversation_id, path)]


@router.get("/{conversation_id}/read", response_model=FileReadOut)
async def read_file(conversation_id: str, path: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> FileReadOut:
    _own_conversation(db, user, conversation_id)
    content, encoding = workspace_manager.read_text(user.id, conversation_id, path)
    return FileReadOut(path=path, content=content, encoding=encoding)


@router.get("/{conversation_id}/raw")
async def raw_file(conversation_id: str, path: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> FileResponse:
    _own_conversation(db, user, conversation_id)
    target = workspace_manager.safe_path(user.id, conversation_id, path)
    if not target.exists() or not target.is_file():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(target, filename=target.name)


@router.put("/{conversation_id}/write")
async def write_file(conversation_id: str, payload: FileWriteIn, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, bool]:
    conv = _own_conversation(db, user, conversation_id)
    workspace_manager.write_text(user.id, conversation_id, payload.path, payload.content, payload.encoding)
    audit(db, actor=user, action="file.write", resource_type="file", resource_id=f"{conversation_id}:{payload.path}", domain=conv.domain, request=request)
    return {"ok": True}


@router.post("/{conversation_id}/upload")
async def upload_file(conversation_id: str, request: Request, path: str = Query(default=""), upload: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, str]:
    conv = _own_conversation(db, user, conversation_id)
    saved_path = await workspace_manager.save_upload(user.id, conversation_id, path or upload.filename or "upload.bin", upload)
    audit(db, actor=user, action="file.upload", resource_type="file", resource_id=f"{conversation_id}:{saved_path}", domain=conv.domain, request=request)
    return {"path": saved_path}


@router.delete("/{conversation_id}")
async def delete_file(conversation_id: str, path: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, bool]:
    conv = _own_conversation(db, user, conversation_id)
    workspace_manager.delete(user.id, conversation_id, path)
    audit(db, actor=user, action="file.delete", resource_type="file", resource_id=f"{conversation_id}:{path}", domain=conv.domain, request=request)
    return {"ok": True}
