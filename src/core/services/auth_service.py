
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.user_repository import (
    get_user_by_email,
    update_last_login,
)
from src.core.services.password_service import hash_password, verify_password
from src.core.services.jwt_service import create_access_token
from src.core.services.refresh_token_service import issue_refresh_token

from src.constants.user_status_enum import UserStatus

#for login
async def login_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> dict:
    """Authenticate an active account and issue its tokens."""

    user = await get_user_by_email(db, email.strip().lower())

    if user is None or not user.is_active:
        raise ValueError("Email or password is incorrect.")

    # Invited users must accept the invitation before logging in.
    if user.status == UserStatus.INVITE_SENT:
        raise ValueError("Please accept your email invitation first.")

    # A password is absent until an invitation is accepted.
    if not user.password_hash:
        raise ValueError("Email or password is incorrect.")

    if not verify_password(password, user.password_hash):
        raise ValueError("Email or password is incorrect.")

    # The first successful login activates a pending account.
    if user.status == UserStatus.PENDING:
        user.status = UserStatus.ACTIVE

    await update_last_login(db, user)

    access_token = create_access_token(user.id)
    refresh_token = await issue_refresh_token(db, user.id)

    await db.commit()

    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


