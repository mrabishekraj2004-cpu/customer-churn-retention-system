import logging

from fastapi.testclient import TestClient


def test_request_logging_records_method_path_status_and_duration(
    authenticated_client: TestClient,
    caplog,
) -> None:
    with caplog.at_level(
        logging.INFO,
        logger="api.middleware.request_logging",
    ):
        response = authenticated_client.get("/health")

    assert response.status_code == 200

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "api.middleware.request_logging"
    ]

    assert any("GET /health status=200 duration_ms=" in message for message in messages)


def test_request_logging_does_not_log_query_values(
    authenticated_client: TestClient,
    caplog,
) -> None:
    sensitive_value = "do-not-log-this-value"

    with caplog.at_level(
        logging.INFO,
        logger="api.middleware.request_logging",
    ):
        response = authenticated_client.get(
            "/health",
            params={
                "token": sensitive_value,
            },
        )

    assert response.status_code == 200

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "api.middleware.request_logging"
    ]

    assert messages
    assert all(sensitive_value not in message for message in messages)


def test_request_logging_does_not_log_request_body(
    authenticated_client: TestClient,
    customer_payload: dict,
    caplog,
) -> None:
    sensitive_customer_id = "SENSITIVE-CUSTOMER-ID"
    customer_payload["customer_id"] = sensitive_customer_id

    with caplog.at_level(
        logging.INFO,
        logger="api.middleware.request_logging",
    ):
        response = authenticated_client.post(
            "/api/v1/predict",
            json=customer_payload,
        )

    assert response.status_code == 200

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "api.middleware.request_logging"
    ]

    assert messages
    assert all(sensitive_customer_id not in message for message in messages)
