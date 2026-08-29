from fastapi.testclient import TestClient

PREDICTION_URL = "/api/v1/predict"


def test_prediction_returns_valid_response(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    response = authenticated_client.post(
        PREDICTION_URL,
        json=customer_payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert 0 <= body["churn_probability"] <= 1

    assert body["risk_level"] in {
        "low",
        "medium",
        "high",
        "critical",
    }

    assert isinstance(
        body["retention_action_required"],
        bool,
    )

    assert body["operating_threshold"] == 0.8
    assert body["model_version"] == "1.0.0"


def test_missing_feature_returns_validation_error(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    customer_payload.pop("Contract")

    response = authenticated_client.post(
        PREDICTION_URL,
        json=customer_payload,
    )

    assert response.status_code == 422


def test_invalid_contract_returns_validation_error(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    customer_payload["Contract"] = "Five year"

    response = authenticated_client.post(
        PREDICTION_URL,
        json=customer_payload,
    )

    assert response.status_code == 422


def test_negative_tenure_returns_validation_error(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    customer_payload["tenure"] = -1

    response = authenticated_client.post(
        PREDICTION_URL,
        json=customer_payload,
    )

    assert response.status_code == 422


def test_negative_monthly_charges_returns_validation_error(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    customer_payload["MonthlyCharges"] = -10

    response = authenticated_client.post(
        PREDICTION_URL,
        json=customer_payload,
    )

    assert response.status_code == 422
