import asyncio

from sqlalchemy import select

from src.data.clients.postgres import AsyncSessionLocal
from src.data.models.role import Role


ROLES = ["recruiter", "hiring_manager", "admin"]


async def seed_roles() -> None:
    async with AsyncSessionLocal() as db:
        try:
            for role_name in ROLES:
                result = await db.execute(
                    select(Role).where(Role.role == role_name)
                )
                existing_role = result.scalar_one_or_none()

                if existing_role is None:
                    db.add(Role(role=role_name))
                    print(f"Created role: {role_name}")
                else:
                    print(f"Role already exists: {role_name}")

            await db.commit()
            print("Role seeding completed successfully!")

        except Exception:
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_roles())