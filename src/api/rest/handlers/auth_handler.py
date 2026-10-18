
from fastapi import HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.schemas.login_schema import (
    LoginRequest,
    LoginResponse,
)
from src.core.services.auth_service import WrongPortalError, login_user


# for Refresh handler
from fastapi import Cookie
from src.api.rest.schemas.refresh_schema import RefreshResponse
from src.core.services.jwt_service import create_access_token
from src.core.services.refresh_token_service import validate_refresh_token
from src.data.repositories.user_repository import get_role_name, get_user_by_id

# For logout handler
from src.api.rest.schemas.logout_schema import LogoutResponse
from src.core.services.refresh_token_service import revoke_token, revoke_user_tokens

#
import secrets
from datetime import datetime, timedelta, timezone

from src.data.repositories.user_repository import get_user_by_email
from src.core.services.password_service import hash_password, verify_password
from src.api.rest.schemas.forgot_password_schema import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
)

from src.core.services.email_service import send_otp_email


from src.api.rest.schemas.reset_password_schema import (
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from src.data.repositories.user_repository import (
    get_user_by_email,
    update_password,
)

import logging

logger = logging.getLogger(__name__)


# for storing access token and refresh token in http only cookie using set_cookie model
def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    """Set authentication tokens in HTTP-only cookies."""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set True in production with HTTPS.
        samesite="lax",
        max_age=15 * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set True in production with HTTPS.
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )



#for login 
async def login_handler(
    data: LoginRequest,
    response: Response,
    db: AsyncSession,
    admin_portal: bool = False,
) -> LoginResponse:
    try:
        result = await login_user(
            db=db,
            email=str(data.email),
            password=data.password,
            admin_portal=admin_portal,
        )

        set_auth_cookies(
            response=response,
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
        )

        return LoginResponse(
            message="Login successful.",
        )

    except WrongPortalError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to complete login.",
        ) from exc
        
        
# for refresh handler

async def refresh_handler(
    response: Response,
    db: AsyncSession,
    refresh_token: str | None  = Cookie(default=None),
) -> RefreshResponse:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing.",
        )

    try:
        token_record = await validate_refresh_token(
            db=db,
            raw_token=refresh_token,
        )

        if token_record is None:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or expired. Please log in again.",
            )

        user = await get_user_by_id(db, token_record.user_id)
        if user is None or not user.is_active:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This account is unavailable.",
            )

        role_name = await get_role_name(db, user.role_id)
        access_token = create_access_token(user.id, role_name)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Local development only; use True in production HTTPS
            samesite="lax",
            max_age=15 * 60,
            path="/",
        )

        await db.commit()

        return RefreshResponse(
            message="Access token refreshed successfully.",
        )

    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to refresh the access token.",
        ) from exc
        
        
# For logout 

async def logout_handler(
    response: Response,
    db: AsyncSession,
    refresh_token: str | None,
) -> LogoutResponse:
    try:
        # Revoke the refresh token if the cookie exists.
        if refresh_token:
            await revoke_token(
                db=db,
                raw_token=refresh_token,
            )

        # Clear both authentication cookies.
        response.delete_cookie(
            key="access_token",
            path="/",
            httponly=True,
            secure=False,
            samesite="lax",
        )

        response.delete_cookie(
            key="refresh_token",
            path="/",
            httponly=True,
            secure=False,
            samesite="lax",
        )

        await db.commit()

        return LogoutResponse(
            message="Logout successful.",
        )

    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to complete logout.",
        ) from exc


#forgot_password handler

async def forgot_password_handler(
    data: ForgotPasswordRequest,
    db: AsyncSession,
) -> ForgotPasswordResponse:
    try:
        email = str(data.email)
        user = await get_user_by_email(db, email)

        # Return the same message whether or not the account exists.
        if user is None:
            return ForgotPasswordResponse()

        # Generate a cryptographically secure six-digit OTP.
        otp = f"{secrets.randbelow(1_000_000):06d}"

        # Store the OTP hash, never the raw OTP.
        user.otp_hash = hash_password(otp)

        # OTP expires after five minutes.
        user.otp_exp = datetime.now(timezone.utc) + timedelta(minutes=5)

        # Send the OTP to the user's registered email.
        await send_otp_email(
            recipient_email=email,
            otp=otp,
        )
        # Save the OTP hash and expiry.
        await db.commit()


        return ForgotPasswordResponse()

    
    except Exception:
        await db.rollback()
        logger.exception("Forgot-password request failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the password-reset request.",
        )
        

#For reset Password
async def reset_password_handler(
    data: ResetPasswordRequest,
    db: AsyncSession,
) -> ResetPasswordResponse:
    try:
        user = await get_user_by_email(db, str(data.email))

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP.",
            )

        # Ensure an OTP exists and has not expired.
        if (
            not user.otp_hash
            or not user.otp_exp
            or user.otp_exp <= datetime.now(timezone.utc)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP.",
            )

        # Compare the submitted OTP with its stored hash.
        try:
            otp_is_valid = verify_password(data.otp, user.otp_hash)
        except ValueError:
            otp_is_valid = False

        if not otp_is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP.",
            )

        # Hash the new password and clear the OTP fields.
        new_password_hash = hash_password(data.new_password)

        await update_password(
            db=db,
            user=user,
            new_password_hash=new_password_hash,
        )

        # Revoke all refresh tokens belonging to this user.
        await revoke_user_tokens(
            db=db,
            user_id=user.id,
            revoked_by=user.id,
        )

        await db.commit()

        return ResetPasswordResponse()

    except HTTPException:
        await db.rollback()
        raise

    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to reset the password.",
        ) from exc


