
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.user_repository import (
    get_role_name,
    get_user_by_email,
    update_last_login,
)
from src.core.services.password_service import hash_password, verify_password
from src.core.services.jwt_service import create_access_token
from src.core.services.refresh_token_service import issue_refresh_token

from src.constants.user_status_enum import UserStatus

class AccountBlockedError(Exception):
    """The password is right but an admin has blocked the account."""


class WrongPortalError(Exception):
    """Correct password, but this sign-in page is not for the user's role."""


#for login
async def login_user(
    db: AsyncSession,
    email: str,
    password: str,
    admin_portal: bool = False,
) -> dict:
    """Authenticate an active account and issue its tokens.

    Admins sign in only through the admin portal (/internal/login); recruiters and
    hiring managers only through /auth/login. The role is checked after the
    password, so a wrong password never reveals which portal an email belongs to.
    """

    user = await get_user_by_email(db, email.strip().lower())

    if user is None:
        raise ValueError("Email or password is incorrect.")

    # Invited users must accept the invitation before logging in.
    if user.status == UserStatus.INVITE_SENT:
        raise ValueError("Please accept your email invitation first.")

    # A password is absent until an invitation is accepted.
    if not user.password_hash:
        raise ValueError("Email or password is incorrect.")

    if not verify_password(password, user.password_hash):
        raise ValueError("Email or password is incorrect.")

    # Checked after the password, so a wrong password never reveals that an account exists.
    if not user.is_active:
        raise AccountBlockedError("Your account has been blocked. Please contact your admin.")

    role_name = await get_role_name(db, user.role_id)
    if admin_portal and role_name != "admin":
        raise WrongPortalError("This sign-in is for admins only. Please use the normal sign-in page.")
    if not admin_portal and role_name == "admin":
        raise WrongPortalError("Admins sign in on the admin sign-in page.")

    # The first successful login activates a pending account.
    if user.status == UserStatus.PENDING:
        user.status = UserStatus.ACTIVE

    await update_last_login(db, user)

    access_token = create_access_token(user.id, role_name)
    refresh_token = await issue_refresh_token(db, user.id)

    await db.commit()

    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


