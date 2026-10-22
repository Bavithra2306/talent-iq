"""The password rule for new passwords (accepting an invitation, resetting a password).

At least 8 characters and at least one symbol (anything that is not a letter, digit or
space, e.g. ! @ # $ % _ -). Sign-in does not apply it, so older passwords keep working.
"""

import re

MIN_LENGTH = 8
MAX_LENGTH = 128
RULE_TEXT = "Password must be at least 8 characters and contain at least one symbol (for example ! @ # $ %)."


def password_problems(password: str) -> list[str]:
    """Plain-language problems with a new password; empty when it is acceptable."""
    problems = []
    if len(password) < MIN_LENGTH:
        problems.append(f"at least {MIN_LENGTH} characters")
    if len(password) > MAX_LENGTH:
        problems.append(f"at most {MAX_LENGTH} characters")
    if not re.search(r"[^A-Za-z0-9\s]", password):
        problems.append("at least one symbol (for example ! @ # $ %)")
    if password != password.strip():
        problems.append("no spaces at the start or end")
    return problems


def check_new_password(password: str) -> str:
    """Pydantic validator body: returns the password or raises ValueError with the rule."""
    problems = password_problems(password)
    if problems:
        raise ValueError("Password needs " + ", ".join(problems) + ".")
    return password
