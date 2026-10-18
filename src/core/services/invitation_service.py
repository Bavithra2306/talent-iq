
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.constants.user_status_enum import UserStatus
from src.core.services.email_service import send_invitation_email
from src.core.services.password_service import hash_password
from src.data.models.role import Role
from src.data.models.user import User
from src.data.repositories.user_repository import get_user_by_email


def hash_invitation_token(token: str) -> str:
    """Hash a high-entropy invitation token for database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def create_invitation(
    db: AsyncSession,
    email: str,
    role_name: str,
    admin: User,
) -> bool:
    """Invite someone by email. If they were invited before but haven't accepted,
    the invitation is sent again with a fresh link (the old link stops working).
    Returns True when it was a resend."""
    email = email.strip().lower()

    existing_user = await get_user_by_email(db, email)
    if existing_user is not None and existing_user.status != UserStatus.INVITE_SENT:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    result = await db.execute(
        select(Role).where(Role.role == role_name)
    )
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=500,
            detail=f"The {role_name} role is not configured.",
        )

    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_invitation_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=48)

    if existing_user is not None:
        # Resend: new link and expiry; the role can be corrected at the same time.
        existing_user.role_id = role.id
        existing_user.invite_link = token_hash
        existing_user.invite_expires_at = expires_at
        existing_user.updated_by = admin.id
    else:
        db.add(User(
            name=None,
            email=email,
            password_hash=None,
            role_id=role.id,
            status=UserStatus.INVITE_SENT,
            invite_link=token_hash,
            invite_expires_at=expires_at,
            is_active=True,
            created_by=admin.id,
        ))

    invitation_url = (
        f"{settings.invite_accept_url}"
        f"?token={raw_token}"
    )
    

    try:
        # Send first so a mail failure doesn't leave a committed
        # invitation that the recipient never received.
        await send_invitation_email(
            recipient_email=email,
            invitation_url=invitation_url,
        )
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return existing_user is not None


async def accept_invitation(
    db: AsyncSession,
    token: str,
    password: str,
    confirm_password: str,
) -> None:
    if password != confirm_password:
        raise HTTPException(
            status_code=422,
            detail="Password and confirmation do not match.",
        )

    token_hash = hash_invitation_token(token)

    result = await db.execute(
        select(User).where(User.invite_link == token_hash)
    )
    user = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if (
        user is None
        or user.status != UserStatus.INVITE_SENT
        or user.invite_expires_at is None
        or user.invite_expires_at <= now
    ):
        raise HTTPException(
            status_code=400,
            detail="Invitation is invalid, expired, or already used.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="This account is disabled. Contact an administrator.",
        )

    try:
        user.password_hash = hash_password(password)
        user.status = UserStatus.PENDING

        # A successful acceptance makes the invitation single-use.
        user.invite_link = None
        user.invite_expires_at = None

        await db.commit()
    except Exception:
        await db.rollback()
        raise
