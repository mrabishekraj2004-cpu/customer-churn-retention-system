from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError

from src.config import settings

MINIMUM_SECRET_LENGTH = 32


class TokenConfigurationError(RuntimeError):
    """Raised when JWT security configuration is unsafe."""


class TokenDecodeError(ValueError):
    """Raised when an access token cannot be securely decoded."""


def _validate_jwt_configuration() -> None:
    """Ensure JWT configuration is safe before handling tokens."""

    if not settings.jwt_secret_key:
        raise TokenConfigurationError(
            "JWT_SECRET_KEY is not configured."
        )

    if len(settings.jwt_secret_key) < MINIMUM_SECRET_LENGTH:
        raise TokenConfigurationError(
            "JWT_SECRET_KEY must be at least 32 characters long."
        )

    if settings.jwt_algorithm != "HS256":
        raise TokenConfigurationError(
            "JWT_ALGORITHM must be HS256."
        )

    if settings.access_token_expire_minutes <= 0:
        raise TokenConfigurationError(
            "ACCESS_TOKEN_EXPIRE_MINUTES must be greater than zero."
        )


def create_access_token(
    *,
    subject: str,
    role: str,
) -> str:
    """Create a signed, short-lived JWT access token."""

    _validate_jwt_configuration()

    now = datetime.now(UTC)

    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now
        + timedelta(
            minutes=settings.access_token_expire_minutes,
        ),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(
    token: str,
) -> dict[str, Any]:
    """Decode and validate a signed JWT access token."""

    _validate_jwt_configuration()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={
                "require": [
                    "sub",
                    "role",
                    "iat",
                    "exp",
                ],
            },
        )
    except InvalidTokenError as exc:
        raise TokenDecodeError(
            "Invalid or expired access token."
        ) from exc

    return payload
