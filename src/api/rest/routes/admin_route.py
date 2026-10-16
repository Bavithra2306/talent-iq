
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth_dependency import get_current_admin
from src.api.rest.schemas.invitation_schema import (
    InvitationRequest,
    InvitationResponse,
)
from src.core.services.invitation_service import create_invitation
from src.data.clients.postgres import get_db
from src.data.models.user import User

AdminRouter = APIRouter(
    prefix="/internal",
    tags=["Internal Admin"],
)


@AdminRouter.get("/")
async def internal_dashboard(
    admin: User = Depends(get_current_admin),
):
    return {
        "message": "Welcome to the TalentIQ admin dashboard.",
        "admin_email": admin.email,
    }


@AdminRouter.post(
    "/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_user(
    data: InvitationRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        await create_invitation(
            db=db,
            email=str(data.email),
            role_name=data.role,
            admin=admin,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to send the invitation.",
        ) from exc

    return InvitationResponse(
        message="Invitation sent successfully.",
    )
