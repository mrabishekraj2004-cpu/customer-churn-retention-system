from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.database.models import UserRole
from src.database.repositories import UserRepository
from src.security.password import hash_password
from src.security.tokens import decode_access_token

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


def test_login_returns_access_token(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(db_session)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["expires_in"] > 0

    payload = decode_access_token(
        data["access_token"]
    )

    assert payload["sub"] == str(user.id)
    assert payload["role"] == UserRole.ADMIN.value


def test_login_accepts_normalized_email(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "  ADMIN@EXAMPLE.COM  ",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200


def test_login_rejects_wrong_password(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "Wrong-Password!",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password."
    }

    assert (
        response.headers["www-authenticate"]
        == "Bearer"
    )


def test_login_rejects_missing_user(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "missing@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password."
    }


def test_login_rejects_disabled_user(
    client: TestClient,
    db_session: Session,
) -> None:
    repository = UserRepository(db_session)

    user = create_user(db_session)

    repository.set_active(
        user,
        is_active=False,
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password."
    }


def test_login_response_does_not_expose_password_hash(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(db_session)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "password" not in data
    assert "password_hash" not in data


def test_login_rejects_empty_password(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "",
        },
    )

    assert response.status_code == 422
