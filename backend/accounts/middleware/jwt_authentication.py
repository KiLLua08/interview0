"""JWT authentication middleware utilities."""

from __future__ import annotations

from typing import Optional

from django.http import HttpRequest

from accounts.utils.jwt import JWTError, verify_access_token
from core.logger import logger


class JWTAuthenticationMiddleware:
    """Attach JWT payload data to requests with bearer tokens."""

    def __init__(self, get_response):
        """Store the next middleware callable."""

        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Process a request and attach auth context when available."""

        token = extract_bearer_token(request)
        request.jwt_payload = None
        request.auth_user_id = None

        if token:
            try:
                payload = verify_access_token(token)
            except JWTError:
                logger.warning("Ignoring invalid bearer token in middleware.")
                payload = None

            request.jwt_payload = payload
            request.auth_user_id = payload.get("sub") if payload else None

        return self.get_response(request)


def extract_bearer_token(request: HttpRequest) -> Optional[str]:
    """Extract a bearer token from a Django request."""

    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        return None

    return token.strip()
