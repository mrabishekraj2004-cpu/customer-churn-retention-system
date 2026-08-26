from fastapi.testclient import TestClient


def create_prediction(
    client: TestClient,
    customer_payload: dict,
) -> dict:
    response = client.post(
        "/api/v1/predict",
        json=customer_payload,
    )

    assert response.status_code == 200

    return response.json()


def test_analytics_summary_empty_database(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_customers"] == 0
    assert data["total_monthly_revenue"] == 0.0

    assert data["customers_with_predictions"] == 0
    assert data["high_risk_customers"] == 0
    assert data["average_churn_probability"] == 0.0

    assert data["risk_distribution"] == {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    assert data["retention_actions"] == {
        "total": 0,
        "recommended": 0,
        "in_progress": 0,
        "completed": 0,
    }

    assert data["retention_outcomes"] == {
        "retained": 0,
        "churned": 0,
        "unknown": 0,
        "success_rate": 0.0,
    }

    assert data["total_estimated_cost"] == 0.0


def test_analytics_summary_contains_customer_metrics(
    client: TestClient,
    customer_payload: dict,
) -> None:
    prediction = create_prediction(
        client,
        customer_payload,
    )

    response = client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_customers"] == 1
    assert data["customers_with_predictions"] == 1

    assert data["total_monthly_revenue"] == (customer_payload["MonthlyCharges"])

    assert data["average_churn_probability"] == (prediction["churn_probability"])


def test_analytics_summary_contains_risk_distribution(
    client: TestClient,
    customer_payload: dict,
) -> None:
    prediction = create_prediction(
        client,
        customer_payload,
    )

    response = client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    risk_level = prediction["risk_level"]

    assert data["risk_distribution"][risk_level] == 1

    assert sum(data["risk_distribution"].values()) == 1


def test_analytics_summary_contains_retention_action_metrics(
    client: TestClient,
    customer_payload: dict,
) -> None:
    prediction = create_prediction(
        client,
        customer_payload,
    )

    response = client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    if prediction["retention_action_required"]:
        assert data["high_risk_customers"] == 1

        assert data["retention_actions"]["total"] == 1
        assert data["retention_actions"]["recommended"] == 1
        assert data["retention_actions"]["in_progress"] == 0
        assert data["retention_actions"]["completed"] == 0
    else:
        assert data["high_risk_customers"] == 0
        assert data["retention_actions"]["total"] == 0


def test_analytics_summary_updates_after_retention_completion(
    client: TestClient,
    customer_payload: dict,
) -> None:
    prediction = create_prediction(
        client,
        customer_payload,
    )

    assert prediction["retention_action_required"] is True

    action_id = prediction["retention_recommendation"]["action_id"]

    in_progress_response = client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "in_progress",
        },
    )

    assert in_progress_response.status_code == 200

    completed_response = client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "completed",
            "outcome": "retained",
        },
    )

    assert completed_response.status_code == 200

    response = client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["retention_actions"]["total"] == 1
    assert data["retention_actions"]["recommended"] == 0
    assert data["retention_actions"]["in_progress"] == 0
    assert data["retention_actions"]["completed"] == 1

    assert data["retention_outcomes"]["retained"] == 1
    assert data["retention_outcomes"]["churned"] == 0
    assert data["retention_outcomes"]["unknown"] == 0

    assert data["retention_outcomes"]["success_rate"] == 100.0


def test_analytics_summary_uses_latest_prediction_only(
    client: TestClient,
    customer_payload: dict,
) -> None:
    first_prediction = create_prediction(
        client,
        customer_payload,
    )

    updated_payload = customer_payload.copy()
    updated_payload["MonthlyCharges"] = customer_payload["MonthlyCharges"] + 10

    second_prediction = create_prediction(
        client,
        updated_payload,
    )

    response = client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_customers"] == 1
    assert data["customers_with_predictions"] == 1

    assert data["average_churn_probability"] == (second_prediction["churn_probability"])

    assert sum(data["risk_distribution"].values()) == 1

    assert first_prediction is not None
