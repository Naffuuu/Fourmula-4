from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token_value,
    generate_reset_token,
    hash_password,
    hash_refresh_token,
    hash_roll_number,
    verify_password,
)
from app.models.token import PasswordResetToken, RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest

settings = get_settings()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def signup_user(db: AsyncSession, payload: SignupRequest) -> tuple[User, str, str]:
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

    user = User(
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        roll_number_hash=hash_roll_number(payload.roll_number) if payload.roll_number else None,
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token(subject=user.id, extra_claims={"role": user.role.value})
    raw_refresh, _ = await issue_refresh_token(db, user.id)
    await db.commit()
    await db.refresh(user)
    return user, access_token, raw_refresh


async def authenticate_user(db: AsyncSession, payload: LoginRequest) -> tuple[User, str, str]:
    user = await get_user_by_email(db, payload.email)
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")

    access_token = create_access_token(subject=user.id, extra_claims={"role": user.role.value})
    raw_refresh, _ = await issue_refresh_token(db, user.id)
    await db.commit()
    return user, access_token, raw_refresh


async def issue_refresh_token(db: AsyncSession, user_id: str) -> tuple[str, str]:
    raw, token_hash = create_refresh_token_value()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    db.add(RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at))
    return raw, token_hash


async def rotate_refresh_token(db: AsyncSession, raw_refresh_token: str) -> tuple[User, str, str]:
    """Validates the presented refresh token, revokes it, and issues a new
    access + refresh pair (rotation limits the blast radius of a stolen
    refresh token to a single use)."""
    token_hash = hash_refresh_token(raw_refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()

    if not stored or stored.revoked or stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired, please log in again.")

    stored.revoked = True

    user = await db.get(User, stored.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")

    access_token = create_access_token(subject=user.id, extra_claims={"role": user.role.value})
    new_raw, _ = await issue_refresh_token(db, user.id)
    await db.commit()
    return user, access_token, new_raw


async def revoke_refresh_token(db: AsyncSession, raw_refresh_token: str) -> None:
    token_hash = hash_refresh_token(raw_refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()
    if stored:
        stored.revoked = True
        await db.commit()


async def request_password_reset(db: AsyncSession, email: str) -> str | None:
    """Always looks like it succeeded to the caller (prevents account
    enumeration); returns the raw token only for internal/dev-console use."""
    user = await get_user_by_email(db, email)
    if not user:
        return None

    raw, token_hash = generate_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    db.add(PasswordResetToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at))
    await db.commit()
    return raw


async def reset_password(db: AsyncSession, raw_token: str, new_password: str) -> None:
    from app.core.security import hash_refresh_token as _hash  # sha256, reused for reset tokens too

    token_hash = _hash(raw_token)
    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()

    if not stored or stored.used or stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link is invalid or expired.")

    user = await db.get(User, stored.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset link is invalid or expired.")

    user.password_hash = hash_password(new_password)
    stored.used = True
    await db.commit()
