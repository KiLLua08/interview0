"""JWT generation and verification helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import Any, Dict

import jwt
from django.conf import settings
from jwt import ExpiredSignatureError, InvalidTokenError

from core.constants import errors


@dataclass(frozen=True)
class JWTError(Exception):
    """Raised when JWT creation or verification fails."""

    code: str
    message: str


def generate_access_token(user_id: str) -> str:
    """Generate a signed access token for a user."""

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
    )
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify a JWT access token and return its payload."""

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except ExpiredSignatureError as exc:
        raise JWTError(
            code=errors.TOKEN_EXPIRED,
            message="Token has expired.",
        ) from exc
    except InvalidTokenError as exc:
        raise JWTError(
            code=errors.INVALID_TOKEN,
            message="Token is invalid.",
        ) from exc

    if payload.get("type") != "access" or not payload.get("sub"):
        raise JWTError(
            code=errors.INVALID_TOKEN,
            message="Token is invalid.",
        )

    return payload
