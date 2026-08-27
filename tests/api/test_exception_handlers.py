import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.exception_handlers import register_exception_handlers


def create_test_app() -> FastAPI:
    app = FastAPI()

    register_exception_handlers(app)

    @app.get("/unexpected-error")
    def unexpected_error() -> None:
        raise RuntimeError("sensitive internal failure")

    return app


def test_unexpected_exception_returns_safe_500_response() -> None:
    app = create_test_app()

    with TestClient(
        app,
        raise_server_exceptions=False,
    ) as client:
        response = client.get("/unexpected-error")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error",
    }

    assert "sensitive internal failure" not in response.text


def test_unexpected_exception_is_logged(
    caplog,
) -> None:
    app = create_test_app()

    with (
        caplog.at_level(
            logging.ERROR,
            logger="api.exception_handlers",
        ),
        TestClient(
            app,
            raise_server_exceptions=False,
        ) as client,
    ):
        response = client.get("/unexpected-error")

    assert response.status_code == 500

    assert any(
        "Unhandled exception while processing GET /unexpected-error"
        in record.getMessage()
        for record in caplog.records
    )
