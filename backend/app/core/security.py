import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# argon2 is the primary scheme (stronger, memory-hard); bcrypt kept as a
# verifiable legacy scheme so existing bcrypt hashes still validate if this
# app is ever migrated from an older auth system.
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def hash_roll_number(roll_number: str) -> str:
    """One-way HMAC of a roll number with a server-side pepper (never the DB
    itself), so a DB leak alone cannot be reversed back to a roll number
    without also compromising the app's secret configuration.
    """
    return hmac.new(
        key=settings.roll_number_pepper.encode("utf-8"),
        msg=roll_number.strip().lower().encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.app_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token_value() -> tuple[str, str]:
    """Refresh tokens are opaque random strings, not JWTs — we store only a
    hash of them (like a password) so stealing the DB doesn't hand over
    usable refresh tokens either. Returns (raw_token, token_hash)."""
    raw = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return raw, token_hash


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.app_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
    if payload.get("type") != "access":
        raise ValueError("Wrong token type")
    return payload


def generate_reset_token() -> tuple[str, str]:
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return raw, token_hash
