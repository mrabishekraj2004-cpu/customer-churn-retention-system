from fastapi.testclient import TestClient

from api.main import app
from src.config import settings


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "customer-churn-api",
    }


def test_application_metadata_uses_settings() -> None:
    assert app.title == settings.app_name
    assert app.version == settings.app_version
