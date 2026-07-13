import httpx
from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.user import OAuthProvider, User, UserRole
from app.services.auth_service import issue_refresh_token

settings = get_settings()

_google_request = google_requests.Request()


async def verify_google_credential(credential: str) -> dict:
    """Verifies the ID token's signature and audience against Google's own
    public keys server-side — we never trust anything the frontend claims
    about who the user is, only what Google's verification confirms."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured on this server.",
        )
    try:
        payload = google_id_token.verify_oauth2_token(
            credential, _google_request, audience=settings.google_client_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google credential.") from exc

    if payload.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token issuer.")

    return {
        "oauth_id": payload["sub"],
        "email": payload.get("email"),
        "name": payload.get("name") or payload.get("email", "Student"),
        "avatar_url": payload.get("picture"),
    }


async def verify_facebook_credential(access_token: str) -> dict:
    """Verifies the access token against the Graph API directly (rather than
    trusting the frontend), and cross-checks it was issued to our own app ID
    via the debug_token endpoint to prevent token substitution attacks."""
    if not settings.facebook_app_id or not settings.facebook_app_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Facebook sign-in is not configured on this server.",
        )

    app_token = f"{settings.facebook_app_id}|{settings.facebook_app_secret}"

    async with httpx.AsyncClient(timeout=10) as client:
        debug_resp = await client.get(
            "https://graph.facebook.com/debug_token",
            params={"input_token": access_token, "access_token": app_token},
        )
        debug_data = debug_resp.json().get("data", {})

        if not debug_data.get("is_valid") or debug_data.get("app_id") != settings.facebook_app_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Facebook credential.")

        profile_resp = await client.get(
            "https://graph.facebook.com/me",
            params={"fields": "id,name,email,picture", "access_token": access_token},
        )
        if profile_resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not verify Facebook profile.")
        profile = profile_resp.json()

    return {
        "oauth_id": profile["id"],
        "email": profile.get("email"),
        "name": profile.get("name", "Student"),
        "avatar_url": profile.get("picture", {}).get("data", {}).get("url"),
    }


async def find_or_create_oauth_user(
    db: AsyncSession, provider: OAuthProvider, profile: dict
) -> User:
    result = await db.execute(
        select(User).where(User.oauth_provider == provider, User.oauth_id == profile["oauth_id"])
    )
    user = result.scalar_one_or_none()
    if user:
        return user

    # Same email, different provider (or originally email/password) — link
    # accounts rather than creating a duplicate.
    if profile.get("email"):
        result = await db.execute(select(User).where(User.email == profile["email"].lower()))
        existing = result.scalar_one_or_none()
        if existing:
            existing.oauth_provider = existing.oauth_provider or provider
            existing.oauth_id = existing.oauth_id or profile["oauth_id"]
            existing.avatar_url = existing.avatar_url or profile.get("avatar_url")
            await db.flush()
            return existing

    user = User(
        name=profile["name"],
        email=(profile.get("email") or f"{profile['oauth_id']}@{provider.value}.oauth.local").lower(),
        password_hash=None,
        role=UserRole.student,
        oauth_provider=provider,
        oauth_id=profile["oauth_id"],
        avatar_url=profile.get("avatar_url"),
    )
    db.add(user)
    await db.flush()
    return user


async def login_via_oauth(db: AsyncSession, provider: OAuthProvider, credential: str) -> tuple[User, str, str]:
    from app.core.security import create_access_token

    if provider == OAuthProvider.google:
        profile = await verify_google_credential(credential)
    elif provider == OAuthProvider.facebook:
        profile = await verify_facebook_credential(credential)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported OAuth provider.")

    user = await find_or_create_oauth_user(db, provider, profile)
    access_token = create_access_token(subject=user.id, extra_claims={"role": user.role.value})
    raw_refresh, _ = await issue_refresh_token(db, user.id)
    await db.commit()
    await db.refresh(user)
    return user, access_token, raw_refresh
