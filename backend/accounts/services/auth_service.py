"""Authentication use cases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from accounts.models import UserDocument
from accounts.repositories.user_repository import (
    UserAlreadyExistsError,
    UserRepository,
)
from accounts.utils.jwt import JWTError, generate_access_token, verify_access_token
from accounts.utils.password import hash_password, verify_password
from core.constants import errors
from core.logger import logger


@dataclass(frozen=True)
class AuthServiceError(Exception):
    """Application-level authentication error."""

    code: str
    message: str


class AuthService:
    """Coordinate authentication business logic."""

    def __init__(self, user_repository: UserRepository | None = None) -> None:
        """Create the service with its required dependencies."""

        self._user_repository = user_repository or UserRepository()

    def register(
        self,
        *,
        email: str,
        full_name: str,
        password: str,
    ) -> Dict[str, Any]:
        """Register a new user and return profile data with an access token."""

        normalized_email = email.strip().lower()
        if self._user_repository.find_by_email(normalized_email):
            logger.warning(
                "Registration rejected because email already exists: %s.",
                normalized_email,
            )
            raise AuthServiceError(
                code=errors.EMAIL_ALREADY_EXISTS,
                message="A user with this email already exists.",
            )

        password_hash = hash_password(password)

        try:
            user = self._user_repository.create_user(
                email=normalized_email,
                full_name=full_name.strip(),
                password_hash=password_hash,
            )
        except UserAlreadyExistsError as exc:
            logger.warning(
                "Registration collided with existing email: %s.",
                normalized_email,
            )
            raise AuthServiceError(
                code=errors.EMAIL_ALREADY_EXISTS,
                message="A user with this email already exists.",
            ) from exc

        logger.info("User registered successfully: %s.", normalized_email)
        return self._build_auth_payload(user)

    def login(self, *, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user and return profile data with an access token."""

        normalized_email = email.strip().lower()
        user = self._user_repository.find_by_email(normalized_email)

        if not user or not verify_password(password, user["password_hash"]):
            logger.warning("Login failed for email: %s.", normalized_email)
            raise AuthServiceError(
                code=errors.INVALID_CREDENTIALS,
                message="Invalid email or password.",
            )

        logger.info("User authenticated successfully: %s.", normalized_email)
        return self._build_auth_payload(user)

    def get_profile(self, token: str) -> Dict[str, Any]:
        """Return the authenticated user's profile from an access token."""

        try:
            payload = verify_access_token(token)
        except JWTError as exc:
            logger.warning("Profile retrieval failed because token is invalid.")
            raise AuthServiceError(
                code=exc.code,
                message=exc.message,
            ) from exc

        user = self._user_repository.find_by_id(str(payload["sub"]))
        if not user:
            logger.warning(
                "Profile retrieval failed because user was not found: %s.",
                payload["sub"],
            )
            raise AuthServiceError(
                code=errors.USER_NOT_FOUND,
                message="Authenticated user was not found.",
            )

        return {"user": self._serialize_user(user)}

    def _build_auth_payload(self, user: UserDocument) -> Dict[str, Any]:
        """Build a standard authentication response payload."""

        user_id = str(user["_id"])
        return {
            "user": self._serialize_user(user),
            "access_token": generate_access_token(user_id),
            "token_type": "Bearer",
        }

    def _serialize_user(self, user: UserDocument) -> Dict[str, Any]:
        """Serialize a user document for public API responses."""

        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
        }
