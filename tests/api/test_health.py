from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from api.main import app
from src.config import settings
from src.database.session import get_db


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "customer-churn-api",
    }


def test_readiness_check(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "customer-churn-api",
        "database": "available",
    }


def test_readiness_check_returns_503_when_database_is_unavailable(
    client: TestClient,
) -> None:
    class BrokenSession:
        def execute(self, statement: object) -> None:
            raise OperationalError(
                "SELECT 1",
                {},
                Exception("database unavailable"),
            )

    def override_get_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/ready")
    finally:
        app.dependency_overrides[get_db] = lambda: None

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "service": "customer-churn-api",
        "database": "unavailable",
    }


def test_application_metadata_uses_settings() -> None:
    assert app.title == settings.app_name
    assert app.version == settings.app_version
