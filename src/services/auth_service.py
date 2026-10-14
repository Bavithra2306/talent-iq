
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.user_repository import (
    get_user_by_email,
    get_user_by_contact,
    get_role_by_name,
    create_user,
    update_last_login,
)
from src.services.password_service import hash_password, verify_password
from src.services.jwt_service import create_access_token
from src.services.refresh_token_service import issue_refresh_token


async def signup_user(
    db: AsyncSession,
    name: str,
    email: str,
    password: str,
    contact: str | None = None,
    location: str | None = None,
):
    """Register a new recruiter account."""

    existing_user = await get_user_by_email(db, email)
    if existing_user:
        raise ValueError("An account with this email already exists.")

    if contact:
        existing_contact = await get_user_by_contact(db, contact)
        if existing_contact:
            raise ValueError("An account with this contact already exists.")

    role = await get_role_by_name(db, "recruiter")
    if role is None:
        raise ValueError("The recruiter role is not configured.")

    password_hash = hash_password(password)

    user = await create_user(
        db=db,
        name=name,
        email=email,
        password_hash=password_hash,
        role_id=role.id,
        contact=contact,
        location=location,
    )

    await db.commit()
    await db.refresh(user)

    return user


async def login_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> dict:
    """Authenticate a user and issue access and refresh tokens."""

    user = await get_user_by_email(db, email)

    if user is None or not verify_password(password, user.password_hash):
        raise ValueError("Email or password is incorrect.")

    if not user.is_active:
        raise ValueError("This account is inactive.")

    await update_last_login(db, user)

    access_token = create_access_token(user.id)
    refresh_token = await issue_refresh_token(db, user.id)

    await db.commit()

    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
