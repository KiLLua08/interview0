"""Consistent API response helpers."""

from typing import Any, Dict

from rest_framework.response import Response


def success_response(data: Dict[str, Any], status_code: int = 200) -> Response:
    """Build a successful API response."""

    return Response(
        {
            "success": True,
            "data": data,
        },
        status=status_code,
    )


def error_response(
    *,
    code: str,
    message: str,
    status_code: int,
) -> Response:
    """Build an error API response."""

    return Response(
        {
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
        status=status_code,
    )

