from enum import Enum


class UserStatus(str, Enum):
    INVITE_SENT = "invite_sent"
    PENDING = "pending"
    ACTIVE = "active"