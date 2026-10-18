from enum import Enum


class UserStatus(str, Enum):
    INVITE_SENT = "invite_sent"
    ACCEPTED = "accepted"
    ACTIVE = "active"