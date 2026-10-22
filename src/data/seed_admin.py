"""Create the first admin account from ADMIN_EMAIL and ADMIN_PASSWORD (in .env.docker).

Run once after the database is migrated:

    docker compose exec auth uv run --no-sync python -m src.data.seed_admin

* Does nothing when an admin already exists, so it is safe to run again.
* The password must follow the normal rule (8+ characters with a symbol). It is
  stored only as an argon2 hash and is never printed.
* After the admin exists, remove ADMIN_PASSWORD from .env.docker; the seed is not
  needed again.
"""

import asyncio
import sys

from sqlalchemy import func, select

from src.config.settings import settings
from src.constants.user_status_enum import UserStatus
from src.core.services.password_policy import password_problems
from src.core.services.password_service import hash_password
from src.data.clients.postgres import AsyncSessionLocal
from src.data.models.role import Role
from src.data.models.user import User
from src.data.seed_roles import seed_roles


async def seed_admin() -> int:
    """Returns a process exit code: 0 when an admin exists afterwards, 1 on bad input."""
    async with AsyncSessionLocal() as db:
        admin_role = (await db.execute(select(Role).where(Role.role == "admin"))).scalar_one_or_none()
        if admin_role is None:
            await seed_roles()
            admin_role = (await db.execute(select(Role).where(Role.role == "admin"))).scalar_one()

        admins = (await db.execute(
            select(func.count(User.id)).where(User.role_id == admin_role.id)
        )).scalar_one()
        if admins:
            print(f"An admin already exists ({admins}); nothing to do.")
            return 0

        email = (settings.admin_email or "").strip().lower()
        password = settings.admin_password.get_secret_value() if settings.admin_password else ""
        if not email or "@" not in email or not password:
            print("Set ADMIN_EMAIL and ADMIN_PASSWORD in .env.docker, then run this again.")
            return 1
        problems = password_problems(password)
        if problems:
            print("ADMIN_PASSWORD needs " + ", ".join(problems) + ".")
            return 1

        taken = (await db.execute(select(User).where(func.lower(User.email) == email))).scalar_one_or_none()
        if taken is not None:
            print("That email already belongs to a non-admin account; use a different ADMIN_EMAIL.")
            return 1

        db.add(User(
            name=settings.admin_name,
            email=email,
            role_id=admin_role.id,
            status=UserStatus.ACTIVE,
            is_active=True,
            password_hash=hash_password(password),
        ))
        await db.commit()
        print(f"Admin created: {email}. You can now remove ADMIN_PASSWORD from .env.docker.")
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(seed_admin()))
