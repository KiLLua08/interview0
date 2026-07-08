"""MongoDB repository for user persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from accounts.models import UserDocument
from core.database import get_database
from core.logger import logger


class UserAlreadyExistsError(Exception):
    """Raised when a user with the requested unique fields already exists."""


class UserRepository:
    """Perform MongoDB operations for users.

    This class intentionally contains no business rules. It only knows how to
    read and write user documents.
    """

    def __init__(self) -> None:
        """Create a repository backed by the configured MongoDB database."""

        self._database = get_database()
        self._collection: Collection[UserDocument] = self._database.users
        self._ensure_indexes()

    def create_user(
        self,
        *,
        email: str,
        full_name: str,
        password_hash: str,
    ) -> UserDocument:
        """Create and return a user document."""

        now = datetime.now(timezone.utc).isoformat()
        document: UserDocument = {
            "email": email,
            "full_name": full_name,
            "password_hash": password_hash,
            "created_at": now,
            "updated_at": now,
        }

        try:
            result = self._collection.insert_one(document)
        except DuplicateKeyError as exc:
            logger.warning("User creation failed because email already exists.")
            raise UserAlreadyExistsError from exc

        document["_id"] = result.inserted_id
        logger.info("Created user document with id %s.", result.inserted_id)
        return document

    def find_by_email(self, email: str) -> Optional[UserDocument]:
        """Find a user by email address."""

        return self._collection.find_one({"email": email})

    def find_by_id(self, user_id: str) -> Optional[UserDocument]:
        """Find a user by MongoDB ObjectId string."""

        if not ObjectId.is_valid(user_id):
            return None

        return self._collection.find_one({"_id": ObjectId(user_id)})

    def _ensure_indexes(self) -> None:
        """Ensure repository-level MongoDB indexes exist."""

        self._collection.create_index(
            [("email", ASCENDING)],
            unique=True,
            name="users_email_unique",
        )
