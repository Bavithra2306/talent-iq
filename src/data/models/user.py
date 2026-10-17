
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.models.base import Base

from sqlalchemy import Enum
from src.constants.user_status_enum import UserStatus

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.data.models.role import Role
    from src.data.models.refresh_token import RefreshToken

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String, nullable=True)
    contact: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    email: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=False,
    )
    
    status: Mapped[UserStatus] = mapped_column(
    Enum(
        UserStatus,
        name="user_status",
        values_callable=lambda enum_cls: [
            member.value for member in enum_cls
        ],
    ),
    nullable=False,
    default=UserStatus.ACTIVE,
    server_default=text("'active'"),
    )
    
    invite_link: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    )

    invite_expires_at: Mapped[DateTime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    )
    
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("roles.id"),
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String, nullable=True)

    otp_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    otp_exp: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
        nullable=False,
    )
    last_login_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)

    role: Mapped["Role"] = relationship(back_populates="users")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
    )
