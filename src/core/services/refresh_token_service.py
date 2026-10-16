
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.data.models.refresh_token import RefreshToken
from src.data.models.user import User
from src.data.repositories.refresh_token_repository import (
    create_refresh_token,
    get_refresh_token_by_hash,
    update_last_used,
    revoke_refresh_token,
    revoke_all_user_refresh_tokens,
)


def generate_refresh_token() -> str:
    """Generate a cryptographically secure refresh token."""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """Return the SHA-256 hash of a refresh token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_refresh_token_expiry() -> datetime:
    """Return the refresh token's expiry time in UTC."""
    return datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )


async def issue_refresh_token(
    db: AsyncSession,
    user_id: UUID,
) -> str:
    """Generate a refresh token and store only its hash in the database."""
    raw_token = generate_refresh_token()
    token_hash = hash_refresh_token(raw_token)
    expiry = get_refresh_token_expiry()

    await create_refresh_token(
        db=db,
        user_id=user_id,
        token_hash=token_hash,
        exp_at=expiry,
        created_by=user_id,
    )

    # Return the raw token to the caller for the HTTP-only cookie.
    return raw_token


async def validate_refresh_token(
    db: AsyncSession,
    raw_token: str,
) -> RefreshToken | None:
    """Validate a refresh token and update its last-used timestamp."""
    token_hash = hash_refresh_token(raw_token)

    record = await get_refresh_token_by_hash(
        db=db,
        token_hash=token_hash,
    )

    if record is None:
        return None

    if record.revoked_at is not None:
        return None

    now = datetime.now(timezone.utc)

    if record.exp_at <= now:
        return None

    user = await db.get(User, record.user_id)

    if user is None or not user.is_active:
        return None

    await update_last_used(db, record)

    return record


async def revoke_token(
    db: AsyncSession,
    raw_token: str,
    revoked_by: UUID | None = None,
) -> bool:
    """Revoke one refresh token if it exists and is not already revoked."""
    token_hash = hash_refresh_token(raw_token)

    record = await get_refresh_token_by_hash(
        db=db,
        token_hash=token_hash,
    )

    if record is None or record.revoked_at is not None:
        return False

    await revoke_refresh_token(
        db=db,
        record=record,
        revoked_by=revoked_by,
    )

    return True


async def revoke_user_tokens(
    db: AsyncSession,
    user_id: UUID,
    revoked_by: UUID | None = None,
) -> int:
    """Revoke all active refresh tokens belonging to a user."""
    return await revoke_all_user_refresh_tokens(
        db=db,
        user_id=user_id,
        revoked_by=revoked_by,
    )
