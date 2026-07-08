"""Password hashing helpers."""

import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Return whether a plaintext password matches a bcrypt hash."""

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )

