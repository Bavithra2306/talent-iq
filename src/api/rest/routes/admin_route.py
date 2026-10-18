
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.dependencies import get_current_admin
from src.api.rest.handlers.auth_handler import login_handler
from src.api.rest.schemas.invitation_schema import (
    InvitationRequest,
    InvitationResponse,
)
from src.api.rest.schemas.login_schema import LoginRequest, LoginResponse
from src.core.services.invitation_service import create_invitation
from src.data.clients.postgres import get_db
from src.data.models.user import User
from src.observability.metrics import metrics

AdminRouter = APIRouter(
    prefix="/internal",
    tags=["Internal Admin"],
)


@AdminRouter.post(
    "/login",
    response_model=LoginResponse,
)
async def admin_login(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Admin sign-in. Only admins can sign in here; everyone else uses /auth/login."""
    return await login_handler(
        data=data,
        response=response,
        db=db,
        admin_portal=True,
    )


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
        resent = await create_invitation(
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
        message="Invitation sent again with a new link." if resent else "Invitation sent successfully.",
    )


@AdminRouter.get(
    "/metrics",
    summary="Request metrics",
    description="Request counts, error counts and latency per route since the service started.",
)
async def request_metrics(_: User = Depends(get_current_admin)):
    """Per-route request statistics (admins only)."""
    return metrics.snapshot()
