import pytest
from fastapi.testclient import TestClient

from api.main import app
from src.config import settings
from src.security.tokens import TokenConfigurationError


def test_application_startup_rejects_missing_jwt_secret(
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
    ), TestClient(app):
        pass


def test_application_startup_rejects_weak_jwt_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        "too-short",
    )

    with pytest.raises(
        TokenConfigurationError,
        match="JWT_SECRET_KEY must be at least 32 characters long",
    ), TestClient(app):
        pass


def test_application_startup_rejects_unsupported_jwt_algorithm(
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
    ), TestClient(app):
        pass


def test_application_startup_rejects_invalid_token_expiration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "access_token_expire_minutes",
        0,
    )

    with pytest.raises(
        TokenConfigurationError,
        match=(
            "ACCESS_TOKEN_EXPIRE_MINUTES "
            "must be greater than zero"
        ),
    ), TestClient(app):
        pass
