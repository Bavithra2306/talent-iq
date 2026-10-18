"""rename user status pending to accepted

Status flow: invite_sent (invitation emailed) -> accepted (password set)
-> active (first sign-in).

Revision ID: a1c3e5f7b9d2
Revises: 014426722e00
Create Date: 2026-10-18 10:30:00
"""

from typing import Sequence, Union

from alembic import op

revision: str = "a1c3e5f7b9d2"
down_revision: Union[str, Sequence[str], None] = "014426722e00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE user_status RENAME VALUE 'pending' TO 'accepted'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE user_status RENAME VALUE 'accepted' TO 'pending'")
