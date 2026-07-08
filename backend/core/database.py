"""Lazy MongoDB connection management."""

from __future__ import annotations

from threading import Lock
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pymongo import MongoClient
from pymongo.database import Database

from core.logger import logger

_client: MongoClient[dict[str, Any]] | None = None
_client_lock = Lock()


def get_mongo_client() -> MongoClient[dict[str, Any]]:
    """Return a singleton MongoDB client with connection pooling enabled."""

    global _client

    if _client is None:
        with _client_lock:
            if _client is None:
                mongo_uri = getattr(settings, "MONGODB_URI", None)
                if not mongo_uri:
                    raise ImproperlyConfigured("MONGODB_URI is not configured.")

                logger.info("Initializing MongoDB client.")
                _client = MongoClient(
                    mongo_uri,
                    maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                    minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                    serverSelectionTimeoutMS=(
                        settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS
                    ),
                )

    return _client


def get_database() -> Database[dict[str, Any]]:
    """Return the configured MongoDB database lazily."""

    database_name = getattr(settings, "MONGODB_DB_NAME", None)
    if not database_name:
        raise ImproperlyConfigured("MONGODB_DB_NAME is not configured.")

    return get_mongo_client()[database_name]

