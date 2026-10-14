
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.refresh_token import RefreshToken


async def create_refresh_token(
    db: AsyncSession,
    user_id: UUID,
    token_hash: str,
    exp_at: datetime,
    created_by: UUID | None = None,
) -> RefreshToken:
    """Save a new refresh-token record."""
    record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        exp_at=exp_at,
        created_by=created_by,
    )

    db.add(record)
    await db.flush()
    await db.refresh(record)

    return record


async def get_refresh_token_by_hash(
    db: AsyncSession,
    token_hash: str,
) -> RefreshToken | None:
    """Find a refresh-token record using its hash."""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )

    return result.scalar_one_or_none()


async def update_last_used(
    db: AsyncSession,
    record: RefreshToken,
) -> None:
    """Record when a refresh token was last used."""
    record.last_used_at = datetime.now(timezone.utc)
    await db.flush()


async def revoke_refresh_token(
    db: AsyncSession,
    record: RefreshToken,
    revoked_by: UUID | None = None,
) -> None:
    """Revoke a refresh token without deleting its record."""
    if record.revoked_at is None:
        record.revoked_at = datetime.now(timezone.utc)
        record.revoked_by = revoked_by
        await db.flush()


async def revoke_all_user_refresh_tokens(
    db: AsyncSession,
    user_id: UUID,
    revoked_by: UUID | None = None,
) -> int:
    """Revoke all active refresh tokens belonging to a user."""
    now = datetime.now(timezone.utc)

    result = await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(
            revoked_at=now,
            revoked_by=revoked_by,
        )
        .execution_options(synchronize_session=False)
    )

    return result.rowcount or 0
