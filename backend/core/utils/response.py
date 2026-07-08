"""Standard API response helpers."""

from __future__ import annotations

from typing import Any

from rest_framework.response import Response


def success_response(
    data: dict[str, Any] | None = None,
    message: str | None = None,
    status: int = 200,
) -> Response:
    """Build a standard successful API response."""

    body: dict[str, Any] = {
        "success": True,
        "data": data or {},
    }
    if message is not None:
        body["message"] = message

    return Response(body, status=status)


def error_response(code: str, message: str, status: int) -> Response:
    """Build a standard error API response."""

    return Response(
        {
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
        status=status,
    )

