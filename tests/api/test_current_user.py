from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.config import settings
from src.database.models import UserRole
from src.database.repositories import UserRepository
from src.security.password import hash_password
from src.security.tokens import create_access_token

TEST_PASSWORD = "Strong-Test-Password-123!"


def create_user(
    db_session: Session,
    *,
    email: str = "admin@example.com",
    role: UserRole = UserRole.ADMIN,
):
    repository = UserRepository(db_session)

    return repository.create(
        email=email,
        password_hash=hash_password(
            TEST_PASSWORD
        ),
        role=role,
    )


def authorization_header(
    token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def test_current_user_returns_authenticated_user(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        role=UserRole.ANALYST,
    )

    token = create_access_token(
        subject=str(user.id),
        role=user.role,
    )

    response = client.get(
        "/api/v1/users/me",
        headers=authorization_header(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "id": user.id,
        "email": "admin@example.com",
        "role": UserRole.ANALYST.value,
        "is_active": True,
    }

    assert "password" not in data
    assert "password_hash" not in data


def test_current_user_rejects_missing_authorization(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/users/me"
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }

    assert (
        response.headers["www-authenticate"]
        == "Bearer"
    )


def test_current_user_rejects_malformed_bearer_credentials(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer",
        },
    )

    assert response.status_code == 401


def test_current_user_rejects_invalid_token(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": (
                "Bearer definitely-not-a-valid-jwt"
            ),
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }


def test_current_user_rejects_wrong_signature(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)

    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "iat": now,
            "exp": now + timedelta(minutes=15),
        },
        "different-secret-that-is-at-least-32-bytes",
        algorithm="HS256",
    )

    response = client.get(
        "/api/v1/users/me",
        headers=authorization_header(token),
    )

    assert response.status_code == 401


def test_current_user_rejects_expired_token(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)

    now = datetime.now(UTC)

    token = jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "iat": now - timedelta(minutes=30),
            "exp": now - timedelta(minutes=15),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/v1/users/me",
        headers=authorization_header(token),
    )

    assert response.status_code == 401


def test_current_user_rejects_non_integer_subject(
    client: TestClient,
) -> None:
    token = create_access_token(
        subject="not-a-user-id",
        role=UserRole.ADMIN.value,
    )

    response = client.get(
        "/api/v1/users/me",
        headers=authorization_header(token),
    )

    assert response.status_code == 401


def test_current_user_rejects_nonexistent_user(
    client: TestClient,
) -> None:
    token = create_access_token(
        subject="999999",
        role=UserRole.ADMIN.value,
    )

    response = client.get(
        "/api/v1/users/me",
        headers=authorization_header(token),
    )

    assert response.status_code == 401


def test_current_user_rejects_disabled_user(
    client: TestClient,
    db_session: Session,
) -> None:
    repository = UserRepository(db_session)

    user = create_user(db_session)

    token = create_access_token(
        subject=str(user.id),
        role=user.role,
    )

    repository.set_active(
        user,
        is_active=False,
    )

    response = client.get(
        "/api/v1/users/me",
        headers=authorization_header(token),
    )

    assert response.status_code == 401


def test_current_user_uses_database_role(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        role=UserRole.ANALYST,
    )

    token = create_access_token(
        subject=str(user.id),
        role=UserRole.ADMIN.value,
    )

    response = client.get(
        "/api/v1/users/me",
        headers=authorization_header(token),
    )

    assert response.status_code == 200
    assert (
        response.json()["role"]
        == UserRole.ANALYST.value
    )
