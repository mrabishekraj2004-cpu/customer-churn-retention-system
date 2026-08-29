from fastapi.testclient import TestClient


def create_prediction(
    authenticated_client: TestClient,
    customer_payload: dict,
    customer_id: str,
) -> dict:
    payload = customer_payload.copy()
    payload["customer_id"] = customer_id

    response = authenticated_client.post(
        "/api/v1/predict",
        json=payload,
    )

    assert response.status_code == 200

    return response.json()


def test_analytics_summary_empty_database(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_customers"] == 0
    assert data["total_monthly_revenue"] == 0.0

    assert data["monthly_revenue_at_risk"] == 0.0
    assert data["annual_revenue_at_risk"] == 0.0

    assert data["expected_monthly_revenue_loss"] == 0.0
    assert data["expected_annual_revenue_loss"] == 0.0

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

    assert data["revenue_saved"] == 0.0
    assert data["net_retention_benefit"] == 0.0
    assert data["retention_roi"] == 0.0


def test_analytics_summary_contains_customer_metrics(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    create_prediction(
        authenticated_client,
        customer_payload,
        "ANALYTICS-CUSTOMER-001",
    )

    response = authenticated_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_customers"] == 1
    assert data["total_monthly_revenue"] == 89.5
    assert data["customers_with_predictions"] == 1
    assert data["high_risk_customers"] == 1
    assert 0.0 <= data["average_churn_probability"] <= 1.0


def test_analytics_summary_contains_risk_distribution(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    create_prediction(
        authenticated_client,
        customer_payload,
        "ANALYTICS-RISK-001",
    )

    response = authenticated_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()
    risk_distribution = data["risk_distribution"]

    assert set(risk_distribution) == {
        "low",
        "medium",
        "high",
        "critical",
    }

    assert sum(risk_distribution.values()) == 1


def test_analytics_summary_contains_retention_action_metrics(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    create_prediction(
        authenticated_client,
        customer_payload,
        "ANALYTICS-ACTION-001",
    )

    response = authenticated_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["retention_actions"]["total"] == 1
    assert data["retention_actions"]["recommended"] == 1
    assert data["retention_actions"]["in_progress"] == 0
    assert data["retention_actions"]["completed"] == 0

    assert data["retention_outcomes"]["retained"] == 0
    assert data["retention_outcomes"]["churned"] == 0
    assert data["retention_outcomes"]["unknown"] == 0
    assert data["retention_outcomes"]["success_rate"] == 0.0


def test_analytics_summary_updates_after_retention_completion(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    prediction_data = create_prediction(
        authenticated_client,
        customer_payload,
        "ANALYTICS-COMPLETED-001",
    )

    action_id = prediction_data["retention_recommendation"]["action_id"]

    in_progress_response = authenticated_client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "in_progress",
        },
    )

    assert in_progress_response.status_code == 200

    completed_response = authenticated_client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "completed",
            "outcome": "retained",
        },
    )

    assert completed_response.status_code == 200

    response = authenticated_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["retention_actions"]["total"] == 1
    assert data["retention_actions"]["recommended"] == 0
    assert data["retention_actions"]["in_progress"] == 0
    assert data["retention_actions"]["completed"] == 1

    assert data["retention_outcomes"]["retained"] == 1
    assert data["retention_outcomes"]["churned"] == 0
    assert data["retention_outcomes"]["success_rate"] == 100.0


def test_analytics_summary_uses_latest_prediction_only(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    customer_id = "ANALYTICS-LATEST-001"

    first_prediction = create_prediction(
        authenticated_client,
        customer_payload,
        customer_id,
    )

    assert first_prediction["retention_action_required"] is True

    second_payload = customer_payload.copy()
    second_payload["customer_id"] = customer_id

    second_response = authenticated_client.post(
        "/api/v1/predict",
        json=second_payload,
    )

    assert second_response.status_code == 200

    response = authenticated_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_customers"] == 1
    assert data["customers_with_predictions"] == 1

    risk_distribution = data["risk_distribution"]

    assert sum(risk_distribution.values()) == 1


def test_analytics_summary_contains_monthly_revenue_at_risk(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    high_risk_payload = customer_payload.copy()

    high_risk_payload["customer_id"] = "API-REVENUE-RISK-001"
    high_risk_payload["MonthlyCharges"] = 100.0
    high_risk_payload["TotalCharges"] = 1000.0

    response = authenticated_client.post(
        "/api/v1/predict",
        json=high_risk_payload,
    )

    assert response.status_code == 200
    assert response.json()["retention_action_required"] is True

    summary_response = authenticated_client.get("/api/v1/analytics/summary")

    assert summary_response.status_code == 200

    data = summary_response.json()

    assert data["total_monthly_revenue"] == 100.0
    assert data["monthly_revenue_at_risk"] == 100.0


def test_analytics_summary_monthly_revenue_at_risk_is_zero_when_empty(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["monthly_revenue_at_risk"] == 0.0


def test_analytics_summary_contains_expected_monthly_revenue_loss(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    high_risk_payload = customer_payload.copy()

    high_risk_payload["customer_id"] = "API-EXPECTED-LOSS-001"
    high_risk_payload["MonthlyCharges"] = 100.0
    high_risk_payload["TotalCharges"] = 1000.0

    prediction_response = authenticated_client.post(
        "/api/v1/predict",
        json=high_risk_payload,
    )

    assert prediction_response.status_code == 200

    prediction_data = prediction_response.json()

    assert prediction_data["retention_action_required"] is True

    churn_probability = prediction_data["churn_probability"]

    expected_loss = high_risk_payload["MonthlyCharges"] * churn_probability

    summary_response = authenticated_client.get("/api/v1/analytics/summary")

    assert summary_response.status_code == 200

    data = summary_response.json()

    assert data["total_monthly_revenue"] == 100.0
    assert data["monthly_revenue_at_risk"] == 100.0
    assert data["expected_monthly_revenue_loss"] == expected_loss


def test_analytics_summary_expected_monthly_revenue_loss_is_zero_when_empty(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["expected_monthly_revenue_loss"] == 0.0


def test_analytics_summary_contains_annual_revenue_metrics(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    payload = customer_payload.copy()

    payload["customer_id"] = "API-ANNUAL-REVENUE-001"
    payload["MonthlyCharges"] = 100.0
    payload["TotalCharges"] = 1000.0

    prediction_response = authenticated_client.post(
        "/api/v1/predict",
        json=payload,
    )

    assert prediction_response.status_code == 200

    prediction_data = prediction_response.json()

    assert prediction_data["retention_action_required"] is True

    churn_probability = prediction_data["churn_probability"]

    expected_monthly_loss = payload["MonthlyCharges"] * churn_probability

    summary_response = authenticated_client.get("/api/v1/analytics/summary")

    assert summary_response.status_code == 200

    data = summary_response.json()

    assert data["monthly_revenue_at_risk"] == 100.0
    assert data["annual_revenue_at_risk"] == 1200.0

    assert data["expected_monthly_revenue_loss"] == (expected_monthly_loss)

    assert data["expected_annual_revenue_loss"] == (expected_monthly_loss * 12)


def test_analytics_summary_annual_metrics_are_zero_when_empty(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["annual_revenue_at_risk"] == 0.0
    assert data["expected_annual_revenue_loss"] == 0.0


def test_analytics_summary_contains_retention_roi_metrics(
    authenticated_client: TestClient,
    customer_payload: dict,
) -> None:
    payload = customer_payload.copy()

    payload["customer_id"] = "API-ROI-001"
    payload["MonthlyCharges"] = 100.0
    payload["TotalCharges"] = 1000.0

    prediction_response = authenticated_client.post(
        "/api/v1/predict",
        json=payload,
    )

    assert prediction_response.status_code == 200

    prediction_data = prediction_response.json()

    assert prediction_data["retention_action_required"] is True

    action_id = prediction_data["retention_recommendation"]["action_id"]

    in_progress_response = authenticated_client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "in_progress",
        },
    )

    assert in_progress_response.status_code == 200

    completed_response = authenticated_client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "completed",
            "outcome": "retained",
        },
    )

    assert completed_response.status_code == 200

    summary_response = authenticated_client.get("/api/v1/analytics/summary")

    assert summary_response.status_code == 200

    data = summary_response.json()

    assert data["revenue_saved"] == 1200.0

    retention_cost = data["total_estimated_cost"]

    assert retention_cost >= 0.0

    assert data["net_retention_benefit"] == (data["revenue_saved"] - retention_cost)

    if retention_cost > 0:
        expected_roi = data["net_retention_benefit"] / retention_cost * 100

        assert data["retention_roi"] == expected_roi
    else:
        assert data["retention_roi"] == 0.0


def test_analytics_summary_roi_metrics_are_zero_when_empty(
    authenticated_client: TestClient,
) -> None:
    response = authenticated_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["revenue_saved"] == 0.0
    assert data["net_retention_benefit"] == 0.0
    assert data["retention_roi"] == 0.0
