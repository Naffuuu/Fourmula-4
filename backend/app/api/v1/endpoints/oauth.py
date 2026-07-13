from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import _set_refresh_cookie
from app.db.session import get_db
from app.models.user import OAuthProvider
from app.schemas.auth import OAuthLoginRequest, TokenResponse, UserOut
from app.services import oauth_service

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.post("/google", response_model=TokenResponse)
async def google_login(payload: OAuthLoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user, access_token, raw_refresh = await oauth_service.login_via_oauth(
        db, OAuthProvider.google, payload.credential
    )
    _set_refresh_cookie(response, raw_refresh)
    return TokenResponse(access_token=access_token, user=UserOut.model_validate(user))


@router.post("/facebook", response_model=TokenResponse)
async def facebook_login(payload: OAuthLoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user, access_token, raw_refresh = await oauth_service.login_via_oauth(
        db, OAuthProvider.facebook, payload.credential
    )
    _set_refresh_cookie(response, raw_refresh)
    return TokenResponse(access_token=access_token, user=UserOut.model_validate(user))
