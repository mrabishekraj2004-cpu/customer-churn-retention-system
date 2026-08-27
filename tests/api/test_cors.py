from fastapi.testclient import TestClient

ALLOWED_ORIGIN = "http://localhost:5173"
DISALLOWED_ORIGIN = "https://not-allowed.example.com"


def test_cors_allows_configured_origin(
    client: TestClient,
) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


def test_cors_allows_credentials(
    client: TestClient,
) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_rejects_unconfigured_origin(
    client: TestClient,
) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": DISALLOWED_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
