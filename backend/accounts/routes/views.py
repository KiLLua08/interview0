"""DRF views for authentication routes."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.middleware.jwt_authentication import extract_bearer_token
from accounts.serializers.auth_serializers import LoginSerializer, RegisterSerializer
from accounts.services.auth_service import AuthService, AuthServiceError
from core.constants import errors
from core.logger import logger
from core.utils.response import error_response, success_response


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request: Request) -> Response:
    """Register a user account."""

    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning("Registration request failed serializer validation.")
        return error_response(
            code=errors.VALIDATION_ERROR,
            message="Invalid registration payload.",
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        data = AuthService().register(**serializer.validated_data)
    except AuthServiceError as exc:
        return error_response(
            code=exc.code,
            message=exc.message,
            status=status.HTTP_400_BAD_REQUEST,
        )

    return success_response(data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request: Request) -> Response:
    """Authenticate a user account."""

    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning("Login request failed serializer validation.")
        return error_response(
            code=errors.VALIDATION_ERROR,
            message="Invalid login payload.",
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        data = AuthService().login(**serializer.validated_data)
    except AuthServiceError as exc:
        return error_response(
            code=exc.code,
            message=exc.message,
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return success_response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def me(request: Request) -> Response:
    """Return the authenticated user's profile."""

    token = extract_bearer_token(request)
    if not token:
        logger.warning("Profile request missing bearer token.")
        return error_response(
            code=errors.AUTHENTICATION_REQUIRED,
            message="Bearer token is required.",
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        data = AuthService().get_profile(token)
    except AuthServiceError as exc:
        return error_response(
            code=exc.code,
            message=exc.message,
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return success_response(data)
