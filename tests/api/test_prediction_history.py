from fastapi.testclient import TestClient


def test_prediction_history_returns_saved_prediction(
    client: TestClient,
    customer_payload: dict,
) -> None:
    prediction_response = client.post(
        "/api/v1/predict",
        json=customer_payload,
    )

    assert prediction_response.status_code == 200

    response = client.get(
        f"/api/v1/customers/{customer_payload['customer_id']}/predictions"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_id"] == customer_payload["customer_id"]
    assert len(data["predictions"]) == 1

    prediction = data["predictions"][0]

    assert prediction["prediction_id"] is not None
    assert 0.0 <= prediction["churn_probability"] <= 1.0
    assert prediction["risk_level"] in {
        "low",
        "medium",
        "high",
        "critical",
    }
    assert isinstance(
        prediction["retention_action_required"],
        bool,
    )
    assert prediction["operating_threshold"] == 0.8
    assert prediction["model_version"] == "1.0.0"
    assert prediction["created_at"] is not None


def test_prediction_history_returns_404_for_unknown_customer(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/customers/DOES-NOT-EXIST/predictions")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Customer not found: DOES-NOT-EXIST"
