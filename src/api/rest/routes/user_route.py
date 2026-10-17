
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth_dependency import get_current_user
from src.api.rest.schemas.user_directory_schema import DirectoryUser
from src.constants.user_status_enum import UserStatus
from src.data.clients.postgres import get_db
from src.data.models.role import Role
from src.data.models.user import User

UserRouter = APIRouter(prefix="/users", tags=["Users"])


@UserRouter.get("/directory", response_model=list[DirectoryUser])
async def user_directory(
    role: str | None = Query(default=None, description="admin / hiring_manager / recruiter"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Active users (optionally of one role), e.g. so a recruiter can pick a hiring manager.

    Users who have not accepted their invitation yet are left out.
    """
    query = (
        select(User.id, User.name, User.email, Role.role)
        .join(Role, Role.id == User.role_id)
        .where(User.is_active.is_(True), User.status != UserStatus.INVITE_SENT)
        .order_by(User.name, User.email)
    )
    if role:
        query = query.where(Role.role == role)
    rows = await db.execute(query)
    return [
        DirectoryUser(id=user_id, name=name, email=email, role=role_name)
        for user_id, name, email, role_name in rows.all()
    ]
