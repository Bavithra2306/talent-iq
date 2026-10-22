"""Admin actions on user accounts: block and unblock.

A blocked account keeps its data but cannot sign in or refresh its session: blocking sets
``is_active`` to False and revokes every refresh token. An access token already issued
stays valid until it expires (at most ACCESS_TOKEN_EXPIRE_MINUTES).
"""

import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services.refresh_token_service import revoke_user_tokens
from src.data.models.role import Role
from src.data.models.user import User


async def _target(db: AsyncSession, user_id: uuid.UUID, admin: User) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == admin.id:
        raise HTTPException(status_code=409, detail="You can't block your own account.")
    role = await db.get(Role, user.role_id)
    if role is not None and role.role == "admin":
        raise HTTPException(status_code=409, detail="Admin accounts can't be blocked here.")
    return user


async def set_blocked(db: AsyncSession, user_id: uuid.UUID, admin: User, blocked: bool) -> User:
    """Block (or unblock) a recruiter or hiring manager. Returns the user."""
    user = await _target(db, user_id, admin)
    user.is_active = not blocked
    user.updated_by = admin.id
    if blocked:
        await revoke_user_tokens(db, user.id, revoked_by=admin.id)
    await db.commit()
    return user
