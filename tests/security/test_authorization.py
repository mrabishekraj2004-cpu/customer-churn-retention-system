from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from src.database.models import User, UserRole
from src.security.authentication import get_current_user
from src.security.authorization import require_roles

AdminUser = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.ADMIN,
        )
    ),
]

RetentionUser = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.RETENTION_AGENT,
        )
    ),
]


@pytest.fixture
def authorization_app() -> FastAPI:
    app = FastAPI()

    @app.get("/admin")
    def admin_only(
        current_user: AdminUser,
    ) -> dict[str, str]:
        return {
            "email": current_user.email,
            "role": current_user.role,
        }

    @app.get("/retention")
    def retention_access(
        current_user: RetentionUser,
    ) -> dict[str, str]:
        return {
            "email": current_user.email,
            "role": current_user.role,
        }

    return app


def make_user(
    role: UserRole,
) -> User:
    return User(
        id=1,
        email="test@example.com",
        password_hash="not-used-in-authorization-test",
        role=role.value,
        is_active=True,
    )


def test_admin_can_access_admin_route(
    authorization_app: FastAPI,
) -> None:
    authorization_app.dependency_overrides[
        get_current_user
    ] = lambda: make_user(UserRole.ADMIN)

    with TestClient(authorization_app) as client:
        response = client.get("/admin")

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_analyst_cannot_access_admin_route(
    authorization_app: FastAPI,
) -> None:
    authorization_app.dependency_overrides[
        get_current_user
    ] = lambda: make_user(UserRole.ANALYST)

    with TestClient(authorization_app) as client:
        response = client.get("/admin")

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Insufficient permissions."
    }


def test_retention_agent_cannot_access_admin_route(
    authorization_app: FastAPI,
) -> None:
    authorization_app.dependency_overrides[
        get_current_user
    ] = lambda: make_user(
        UserRole.RETENTION_AGENT
    )

    with TestClient(authorization_app) as client:
        response = client.get("/admin")

    assert response.status_code == 403


def test_admin_can_access_retention_route(
    authorization_app: FastAPI,
) -> None:
    authorization_app.dependency_overrides[
        get_current_user
    ] = lambda: make_user(UserRole.ADMIN)

    with TestClient(authorization_app) as client:
        response = client.get("/retention")

    assert response.status_code == 200


def test_retention_agent_can_access_retention_route(
    authorization_app: FastAPI,
) -> None:
    authorization_app.dependency_overrides[
        get_current_user
    ] = lambda: make_user(
        UserRole.RETENTION_AGENT
    )

    with TestClient(authorization_app) as client:
        response = client.get("/retention")

    assert response.status_code == 200


def test_analyst_cannot_access_retention_route(
    authorization_app: FastAPI,
) -> None:
    authorization_app.dependency_overrides[
        get_current_user
    ] = lambda: make_user(UserRole.ANALYST)

    with TestClient(authorization_app) as client:
        response = client.get("/retention")

    assert response.status_code == 403
