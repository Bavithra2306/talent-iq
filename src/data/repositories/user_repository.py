
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.role import Role
from src.data.models.user import User


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    """Find a user by email."""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_contact(
    db: AsyncSession,
    contact: str,
) -> User | None:
    """Find a user by contact number."""
    result = await db.execute(
        select(User).where(User.contact == contact)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(
    db: AsyncSession,
    user_id: UUID,
) -> User | None:
    """Find a user by UUID."""
    return await db.get(User, user_id)


async def get_role_name(
    db: AsyncSession,
    role_id: UUID,
) -> str:
    """Return the role name (admin / hiring_manager / recruiter) for a role id."""
    result = await db.execute(
        select(Role.role).where(Role.id == role_id)
    )
    return result.scalar_one()


async def create_user(
    db: AsyncSession,
    name: str,
    email: str,
    password_hash: str,
    role_id: UUID,
    contact: str | None = None,
    location: str | None = None,
    created_by: UUID | None = None,
) -> User:
    """Create a user record."""
    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        role_id=role_id,
        contact=contact,
        location=location,
        created_by=created_by,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


async def update_user(
    db: AsyncSession,
    user: User,
    name: str | None = None,
    contact: str | None = None,
    location: str | None = None,
) -> User:
    """Update a user's profile fields."""
    if name is not None:
        user.name = name

    if contact is not None:
        user.contact = contact

    if location is not None:
        user.location = location

    await db.flush()
    await db.refresh(user)

    return user

async def update_last_login(
    db: AsyncSession,
    user: User,
) -> None:
    """Update the user's last login timestamp."""
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()


async def update_password(
    db: AsyncSession,
    user: User,
    new_password_hash: str,
) -> None:
    """Update the user's password hash."""
    user.password_hash = new_password_hash
    user.otp_hash = None
    user.otp_exp = None

    await db.flush()




async def get_role_by_name(
    db: AsyncSession,
    role_name: str,
) -> Role | None:
    """Find a predefined role by name."""
    result = await db.execute(
        select(Role).where(Role.role == role_name)
    )
    return result.scalar_one_or_none()
