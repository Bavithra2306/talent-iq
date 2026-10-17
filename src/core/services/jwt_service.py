
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError

from src.config.settings import settings


def create_access_token(user_id: UUID, role: str) -> str:
    """Create a signed JWT access token for a user.

    The role claim lets other services (talent-iq-core) authorize without a DB lookup.
    """

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.access_token_expire_minutes
        ),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token


def decode_access_token(token: str) -> dict:
    """Verify a JWT and return its claims."""

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={
                "require": ["sub", "iat", "exp", "iss", "aud"]
            },
        )

        return payload

    except InvalidTokenError as exc:
        raise ValueError(
            "The access token is invalid or has expired."
        ) from exc
