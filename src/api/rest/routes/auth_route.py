
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.clients.postgres import get_db
from src.api.rest.handlers.auth_handler import (
    signup_handler,
    login_handler,
)
from src.api.rest.schemas.signup_schema import (
    SignupRequest,
    SignupResponse,
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


AuthRouter = APIRouter(prefix="/auth", tags=["Authentication"])

# For SignUP
@AuthRouter.post(
    "/signup",
    response_model=SignupResponse,
    status_code=201,
)
async def signup(
    data: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    return await signup_handler(data=data, db=db)

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

