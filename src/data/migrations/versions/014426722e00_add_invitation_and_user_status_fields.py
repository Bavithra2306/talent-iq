"""add invitation and user status fields

Revision ID: 014426722e00
Revises: 7ce174ea4ffe
Create Date: 2026-10-16 12:21:16.068731
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# PostgreSQL enum type
user_status_enum = postgresql.ENUM(
    "invite_sent",
    "pending",
    "active",
    name="user_status",
    create_type=False,
)


# Revision identifiers, used by Alembic.
revision: str = "014426722e00"
down_revision: Union[str, Sequence[str], None] = "7ce174ea4ffe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create the PostgreSQL enum before using it in a column.
    user_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "status",
            user_status_enum,
            server_default=sa.text("'active'"),
            nullable=False,
        ),
    )

    op.add_column(
        "users",
        sa.Column("invite_link", sa.String(), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column(
            "invite_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.alter_column(
        "users",
        "name",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )

    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )


def downgrade() -> None:
    """Revert invitation and user status fields."""

    # Remove columns that depend on the enum before dropping the enum.
    op.drop_column("users", "invite_expires_at")
    op.drop_column("users", "invite_link")
    op.drop_column("users", "status")

    user_status_enum.drop(op.get_bind(), checkfirst=True)

    # Restore the previous constraints.
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )

    op.alter_column(
        "users",
        "name",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )
