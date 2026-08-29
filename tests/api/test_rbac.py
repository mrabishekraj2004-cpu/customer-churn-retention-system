from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.database.models import UserRole
from src.database.repositories import UserRepository
from src.security.password import hash_password
from src.security.tokens import create_access_token

TEST_PASSWORD = "Strong-Test-Password-123!"


def create_auth_headers(
    db_session: Session,
    *,
    role: UserRole,
    email: str,
) -> dict[str, str]:
    repository = UserRepository(db_session)

    user = repository.create(
        email=email,
        password_hash=hash_password(TEST_PASSWORD),
        role=role,
    )

    token = create_access_token(
        subject=str(user.id),
        role=user.role,
    )

    return {
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture
def auth_headers(
    db_session: Session,
) -> Callable[[UserRole, str], dict[str, str]]:
    counter = 0

    def build(
        role: UserRole,
        email: str | None = None,
    ) -> dict[str, str]:
        nonlocal counter
        counter += 1

        resolved_email = (
            email
            or f"{role.value}-{counter}@example.com"
        )

        return create_auth_headers(
            db_session,
            role=role,
            email=resolved_email,
        )

    return build


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/v1/customers"),
        ("POST", "/api/v1/predict"),
        ("GET", "/api/v1/customers/TEST/predictions"),
        ("GET", "/api/v1/retention-actions"),
        ("PATCH", "/api/v1/retention-actions/1"),
        ("GET", "/api/v1/analytics/summary"),
    ],
)
def test_business_routes_require_authentication(
    client: TestClient,
    method: str,
    path: str,
) -> None:
    response = client.request(
        method,
        path,
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials."
    }


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (UserRole.ADMIN, 200),
        (UserRole.ANALYST, 200),
        (UserRole.RETENTION_AGENT, 200),
    ],
)
def test_customer_list_allows_all_roles(
    client: TestClient,
    auth_headers: Callable[
        [UserRole, str],
        dict[str, str],
    ],
    role: UserRole,
    expected_status: int,
) -> None:
    headers = auth_headers(
        role,
        f"customers-{role.value}@example.com",
    )

    response = client.get(
        "/api/v1/customers",
        headers=headers,
    )

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (UserRole.ADMIN, 200),
        (UserRole.ANALYST, 200),
        (UserRole.RETENTION_AGENT, 403),
    ],
)
def test_analytics_role_access(
    client: TestClient,
    auth_headers: Callable[
        [UserRole, str],
        dict[str, str],
    ],
    role: UserRole,
    expected_status: int,
) -> None:
    headers = auth_headers(
        role,
        f"analytics-{role.value}@example.com",
    )

    response = client.get(
        "/api/v1/analytics/summary",
        headers=headers,
    )

    assert response.status_code == expected_status

    if expected_status == 403:
        assert response.json() == {
            "detail": "Insufficient permissions."
        }


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (UserRole.ADMIN, 404),
        (UserRole.ANALYST, 403),
        (UserRole.RETENTION_AGENT, 404),
    ],
)
def test_retention_patch_role_access(
    client: TestClient,
    auth_headers: Callable[
        [UserRole, str],
        dict[str, str],
    ],
    role: UserRole,
    expected_status: int,
) -> None:
    headers = auth_headers(
        role,
        f"retention-{role.value}@example.com",
    )

    response = client.patch(
        "/api/v1/retention-actions/999999",
        headers=headers,
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == expected_status

    if expected_status == 403:
        assert response.json() == {
            "detail": "Insufficient permissions."
        }
