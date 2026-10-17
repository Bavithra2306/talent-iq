
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plain-text password securely."""
    return _password_hasher.hash(password)



def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Return True if the password matches; otherwise False."""
    try:
        is_valid = _password_hasher.verify(
            hashed_password,
            plain_password,
        )

        if is_valid:
            return True

        return False

    except VerifyMismatchError:
        return False

    except (InvalidHashError, VerificationError) as exc:
        raise ValueError(
            "Unable to verify the password because the stored hash is invalid."
        ) from exc
