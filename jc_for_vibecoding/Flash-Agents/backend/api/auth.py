from __future__ import annotations

from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, upsert_user_from_claims
from ..config import settings
from ..database import get_db
from ..models import User
from ..schemas import DevLoginIn, SsoCallbackIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.get("/sso-url")
async def sso_url(state: str = "") -> dict[str, str]:
    if not settings.SSO_ENABLED:
        return {"url": "", "enabled": "false"}
    query = urlencode(
        {
            "client_id": settings.SSO_CLIENT_ID,
            "redirect_uri": settings.SSO_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid profile email",
            "state": state,
        }
    )
    return {"url": f"{settings.SSO_AUTHORIZE_URL}?{query}", "enabled": "true"}


@router.post("/callback", response_model=TokenOut)
async def sso_callback(payload: SsoCallbackIn, db: Session = Depends(get_db)) -> TokenOut:
    if not settings.SSO_ENABLED:
        raise HTTPException(status_code=400, detail="SSO is disabled")
    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(
            settings.SSO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": payload.code,
                "redirect_uri": settings.SSO_REDIRECT_URI,
                "client_id": settings.SSO_CLIENT_ID,
                "client_secret": settings.SSO_CLIENT_SECRET,
            },
        )
        token_resp.raise_for_status()
        access_token = token_resp.json().get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="SSO token response has no access_token")
        userinfo = await client.get(settings.SSO_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
        userinfo.raise_for_status()
        claims = userinfo.json()

    user = upsert_user_from_claims(db, claims)
    jwt_token, expires = create_access_token(user.external_id, {"email": user.email, "domain": user.domain, "display_name": user.display_name, "employee_no": user.employee_no, "roles": user.roles.get("roles", []), "is_admin": user.is_admin})
    return TokenOut(access_token=jwt_token, expires_in=expires, user=user)


@router.post("/dev-login", response_model=TokenOut)
async def dev_login(payload: DevLoginIn, db: Session = Depends(get_db)) -> TokenOut:
    if settings.ENV == "production" and settings.SSO_ENABLED:
        raise HTTPException(status_code=404, detail="Not found")
    claims = {
        "sub": payload.email.lower(),
        "email": payload.email.lower(),
        "display_name": payload.display_name or payload.email.split("@")[0],
        "domain": payload.domain,
        "employee_no": payload.employee_no,
        "roles": ["user"],
    }
    user = upsert_user_from_claims(db, claims)
    token, expires = create_access_token(user.external_id, {"email": user.email, "domain": user.domain, "display_name": user.display_name, "employee_no": user.employee_no, "roles": user.roles.get("roles", []), "is_admin": user.is_admin})
    return TokenOut(access_token=token, expires_in=expires, user=user)
