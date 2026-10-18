
#for Refresh token
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.dependencies import get_current_user as current_user_dependency

# for logout route
# Forgot_password route
from src.api.rest.handlers.auth_handler import (
    forgot_password_handler,
    login_handler,
    logout_handler,
    refresh_handler,
    reset_password_handler,
)
from src.api.rest.schemas.current_user_schema import (
    CurrentUserResponse,
    ProfileUpdateRequest,
)
from src.api.rest.schemas.forgot_password_schema import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
)
from src.api.rest.schemas.invitation_schema import (
    AcceptInvitationRequest,
    AcceptInvitationResponse,
)
from src.api.rest.schemas.login_schema import (
    LoginRequest,
    LoginResponse,
)
from src.api.rest.schemas.logout_schema import LogoutResponse
from src.api.rest.schemas.refresh_schema import RefreshResponse
from src.api.rest.schemas.reset_password_schema import (
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from src.core.services.invitation_service import accept_invitation
from src.data.clients.postgres import get_db
from src.data.models.user import User

AuthRouter = APIRouter(prefix="/auth", tags=["Authentication"])

#For confirm password and Register
@AuthRouter.post(
    "/accept-invitation",
    response_model=AcceptInvitationResponse,
)
async def accept_user_invitation(
    data: AcceptInvitationRequest,
    db: AsyncSession = Depends(get_db),
):
    await accept_invitation(
        db=db,
        token=data.token,
        password=data.password,
        confirm_password=data.confirm_password,
    )

    return AcceptInvitationResponse(
        message="Invitation accepted. You can now log in.",
    )


#for LogIN
@AuthRouter.post(
    "/login",
    response_model=LoginResponse,
)
async def login(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    return await login_handler(
        data=data,
        response=response,
        db=db,
    )
    

@AuthRouter.get(
    "/me",
    response_model=CurrentUserResponse,
)
async def get_my_profile(
    user: User = Depends(current_user_dependency),
):
    """The signed-in user's profile, including their role name."""
    return _profile(user)


@AuthRouter.patch(
    "/me",
    response_model=CurrentUserResponse,
)
async def update_my_profile(
    data: ProfileUpdateRequest,
    user: User = Depends(current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Update your own name, phone number and location."""
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    user.updated_at = func.now()
    user.updated_by = user.id
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That phone number is already used by another account.",
        ) from exc
    await db.refresh(user, attribute_names=["updated_at", "role"])
    return _profile(user)


def _profile(user: User) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role_id=user.role_id,
        role=user.role.role,
        contact=user.contact,
        location=user.location,
        status=user.status.value,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


# For new Access token

@AuthRouter.post(
    "/refresh",
    response_model=RefreshResponse,
)
async def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await refresh_handler(
        response=response,
        db=db,
        refresh_token=refresh_token,
    )

# for Logout

@AuthRouter.post(
    "/logout",
    response_model=LogoutResponse,
)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await logout_handler(
        response=response,
        db=db,
        refresh_token=refresh_token,
    )
    
# Forgot password route

@AuthRouter.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    return await forgot_password_handler(
        data=data,
        db=db,
    )
    
#for reset-password 

@AuthRouter.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    return await reset_password_handler(
        data=data,
        db=db,
    )

