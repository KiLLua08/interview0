"""Request serializers for authentication endpoints."""

from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    """Validate registration request payloads."""

    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=120, trim_whitespace=True)
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        trim_whitespace=False,
        write_only=True,
    )


class LoginSerializer(serializers.Serializer):
    """Validate login request payloads."""

    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=128,
        trim_whitespace=False,
        write_only=True,
    )

