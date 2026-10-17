
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.clients.postgres import get_db
from src.api.rest.handlers.auth_handler import (
    login_handler,
)

from src.api.rest.schemas.login_schema import (
    LoginRequest,
    LoginResponse,
)

#for Refresh token

from fastapi import Cookie
from src.api.rest.handlers.auth_handler import refresh_handler
from src.api.rest.schemas.refresh_schema import RefreshResponse

# for logout route
from src.api.rest.handlers.auth_handler import logout_handler
from src.api.rest.schemas.logout_schema import LogoutResponse

# Forgot_password route
from src.api.rest.handlers.auth_handler import forgot_password_handler
from src.api.rest.schemas.forgot_password_schema import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
)

from src.api.rest.handlers.auth_handler import reset_password_handler
from src.api.rest.schemas.reset_password_schema import (
    ResetPasswordRequest,
    ResetPasswordResponse,
)

from src.api.rest.schemas.invitation_schema import (
    AcceptInvitationRequest,
    AcceptInvitationResponse,
)
from src.core.services.invitation_service import accept_invitation

from src.api.rest.schemas.current_user_schema import CurrentUserResponse
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from src.data.models.user import User
from src.core.services.jwt_service import decode_access_token
from uuid import UUID



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
async def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    try:
        payload = decode_access_token(access_token)
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is unavailable.",
        )

    return CurrentUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role_id=user.role_id,
        status=user.status.value,
        is_active=user.is_active,
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

