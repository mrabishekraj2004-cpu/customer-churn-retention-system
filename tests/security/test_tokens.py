from datetime import UTC, datetime, timedelta

import jwt
import pytest

from src.config import settings
from src.security.tokens import (
    TokenConfigurationError,
    TokenDecodeError,
    create_access_token,
    decode_access_token,
)

TEST_SECRET = "test-secret-key-that-is-at-least-32-bytes-long"


@pytest.fixture
def jwt_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        TEST_SECRET,
    )
    monkeypatch.setattr(
        settings,
        "jwt_algorithm",
        "HS256",
    )
    monkeypatch.setattr(
        settings,
        "access_token_expire_minutes",
        15,
    )


def test_create_and_decode_access_token(
    jwt_settings: None,
) -> None:
    token = create_access_token(
        subject="user-123",
        role="admin",
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "user-123"
    assert payload["role"] == "admin"
    assert "iat" in payload
    assert "exp" in payload


def test_decode_rejects_wrong_signature(
    jwt_settings: None,
) -> None:
    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": "user-123",
            "role": "analyst",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        "different-test-secret-that-is-at-least-32-bytes",
        algorithm="HS256",
    )

    with pytest.raises(
        TokenDecodeError,
        match="Invalid or expired access token",
    ):
        decode_access_token(token)


def test_decode_rejects_expired_token(
    jwt_settings: None,
) -> None:
    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": "user-123",
            "role": "admin",
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
        },
        TEST_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(
        TokenDecodeError,
        match="Invalid or expired access token",
    ):
        decode_access_token(token)


def test_decode_rejects_missing_required_claim(
    jwt_settings: None,
) -> None:
    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": "user-123",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        TEST_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(TokenDecodeError):
        decode_access_token(token)


def test_create_rejects_missing_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        "",
    )

    with pytest.raises(
        TokenConfigurationError,
        match="JWT_SECRET_KEY is not configured",
    ):
        create_access_token(
            subject="user-123",
            role="admin",
        )


def test_create_rejects_weak_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        "too-short",
    )

    with pytest.raises(
        TokenConfigurationError,
        match="at least 32 characters",
    ):
        create_access_token(
            subject="user-123",
            role="admin",
        )


def test_create_rejects_unsupported_algorithm(
    jwt_settings: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_algorithm",
        "HS512",
    )

    with pytest.raises(
        TokenConfigurationError,
        match="JWT_ALGORITHM must be HS256",
    ):
        create_access_token(
            subject="user-123",
            role="admin",
        )


def test_create_rejects_invalid_expiration(
    jwt_settings: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "access_token_expire_minutes",
        0,
    )

    with pytest.raises(
        TokenConfigurationError,
        match="must be greater than zero",
    ):
        create_access_token(
            subject="user-123",
            role="admin",
        )
