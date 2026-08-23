from fastapi.testclient import TestClient


def create_customer_with_prediction(
    client: TestClient,
    customer_payload: dict,
) -> dict:
    response = client.post(
        "/api/v1/predict",
        json=customer_payload,
    )

    assert response.status_code == 200

    return response.json()


def test_get_customers_returns_customer_list(
    client: TestClient,
    customer_payload: dict,
) -> None:
    prediction = create_customer_with_prediction(
        client,
        customer_payload,
    )

    response = client.get("/api/v1/customers")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert len(data["customers"]) == 1

    customer = data["customers"][0]

    assert customer["customer_id"] == customer_payload["customer_id"]
    assert customer["latest_prediction"] is not None
    assert (
        customer["latest_prediction"]["churn_probability"]
        == prediction["churn_probability"]
    )
    assert customer["latest_prediction"]["risk_level"] == prediction["risk_level"]


def test_get_customer_detail(
    client: TestClient,
    customer_payload: dict,
) -> None:
    create_customer_with_prediction(
        client,
        customer_payload,
    )

    customer_id = customer_payload["customer_id"]

    response = client.get(f"/api/v1/customers/{customer_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["customer_id"] == customer_id
    assert data["gender"] == customer_payload["gender"]
    assert data["tenure"] == customer_payload["tenure"]
    assert data["contract"] == customer_payload["Contract"]
    assert data["internet_service"] == customer_payload["InternetService"]
    assert data["monthly_charges"] == customer_payload["MonthlyCharges"]

    assert data["latest_prediction"] is not None


def test_customer_detail_contains_latest_prediction(
    client: TestClient,
    customer_payload: dict,
) -> None:
    first_prediction = create_customer_with_prediction(
        client,
        customer_payload,
    )

    updated_payload = customer_payload.copy()
    updated_payload["MonthlyCharges"] = customer_payload["MonthlyCharges"] + 10

    second_prediction = create_customer_with_prediction(
        client,
        updated_payload,
    )

    customer_id = customer_payload["customer_id"]

    response = client.get(f"/api/v1/customers/{customer_id}")

    assert response.status_code == 200

    latest_prediction = response.json()["latest_prediction"]

    assert latest_prediction is not None
    assert latest_prediction["prediction_id"] is not None
    assert (
        latest_prediction["churn_probability"] == second_prediction["churn_probability"]
    )

    assert first_prediction is not None


def test_unknown_customer_returns_404(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/customers/UNKNOWN-CUSTOMER")

    assert response.status_code == 404
    assert response.json()["detail"] == ("Customer not found: UNKNOWN-CUSTOMER")


def test_customer_list_respects_limit_and_offset(
    client: TestClient,
    customer_payload: dict,
) -> None:
    first_payload = customer_payload.copy()
    first_payload["customer_id"] = "API-PAGE-001"

    second_payload = customer_payload.copy()
    second_payload["customer_id"] = "API-PAGE-002"

    third_payload = customer_payload.copy()
    third_payload["customer_id"] = "API-PAGE-003"

    create_customer_with_prediction(
        client,
        first_payload,
    )
    create_customer_with_prediction(
        client,
        second_payload,
    )
    create_customer_with_prediction(
        client,
        third_payload,
    )

    response = client.get("/api/v1/customers?limit=2&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert len(data["customers"]) == 2


def test_customer_list_with_offset(
    client: TestClient,
    customer_payload: dict,
) -> None:
    for index in range(3):
        payload = customer_payload.copy()
        payload["customer_id"] = f"API-OFFSET-{index}"

        create_customer_with_prediction(
            client,
            payload,
        )

    response = client.get("/api/v1/customers?limit=2&offset=2")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["limit"] == 2
    assert data["offset"] == 2
    assert len(data["customers"]) == 1


def test_customer_list_rejects_zero_limit(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/customers?limit=0")

    assert response.status_code == 422


def test_customer_list_rejects_negative_offset(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/customers?offset=-1")

    assert response.status_code == 422


def test_customer_list_rejects_limit_above_maximum(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/customers?limit=501")

    assert response.status_code == 422


def test_high_risk_endpoint_returns_actionable_customer(
    client: TestClient,
    customer_payload: dict,
) -> None:
    payload = customer_payload.copy()
    payload["customer_id"] = "API-HIGH-RISK-001"

    prediction = create_customer_with_prediction(
        client,
        payload,
    )

    response = client.get("/api/v1/customers/high-risk")

    assert response.status_code == 200

    data = response.json()

    if prediction["retention_action_required"]:
        assert data["count"] == 1
        assert len(data["customers"]) == 1

        customer = data["customers"][0]

        assert customer["customer_id"] == (payload["customer_id"])
        assert customer["churn_probability"] == prediction["churn_probability"]
        assert customer["risk_level"] == prediction["risk_level"]
    else:
        assert data["count"] == 0
        assert data["customers"] == []


def test_high_risk_endpoint_excludes_non_actionable_customer(
    client: TestClient,
    customer_payload: dict,
) -> None:
    payload = customer_payload.copy()
    payload["customer_id"] = "API-LOW-RISK-001"

    payload["tenure"] = 72
    payload["Contract"] = "Two year"
    payload["InternetService"] = "DSL"
    payload["OnlineSecurity"] = "Yes"
    payload["TechSupport"] = "Yes"
    payload["PaymentMethod"] = "Credit card (automatic)"
    payload["MonthlyCharges"] = 25.0
    payload["TotalCharges"] = 1800.0

    prediction = create_customer_with_prediction(
        client,
        payload,
    )

    response = client.get("/api/v1/customers/high-risk")

    assert response.status_code == 200

    data = response.json()

    if not prediction["retention_action_required"]:
        customer_ids = {customer["customer_id"] for customer in data["customers"]}

        assert payload["customer_id"] not in customer_ids


def test_high_risk_endpoint_uses_latest_prediction(
    client: TestClient,
    customer_payload: dict,
) -> None:
    payload = customer_payload.copy()
    payload["customer_id"] = "API-LATEST-RISK-001"

    first_prediction = create_customer_with_prediction(
        client,
        payload,
    )

    updated_payload = payload.copy()
    updated_payload["tenure"] = 72
    updated_payload["Contract"] = "Two year"
    updated_payload["InternetService"] = "DSL"
    updated_payload["OnlineSecurity"] = "Yes"
    updated_payload["TechSupport"] = "Yes"
    updated_payload["PaymentMethod"] = "Credit card (automatic)"
    updated_payload["MonthlyCharges"] = 25.0
    updated_payload["TotalCharges"] = 1800.0

    second_prediction = create_customer_with_prediction(
        client,
        updated_payload,
    )

    response = client.get("/api/v1/customers/high-risk")

    assert response.status_code == 200

    customers = response.json()["customers"]

    matching_customers = [
        customer
        for customer in customers
        if customer["customer_id"] == payload["customer_id"]
    ]

    if second_prediction["retention_action_required"]:
        assert len(matching_customers) == 1

        assert (
            matching_customers[0]["prediction_id"] == second_prediction["prediction_id"]
        )
    else:
        assert matching_customers == []

    assert first_prediction is not None


def test_high_risk_endpoint_respects_limit_and_offset(
    client: TestClient,
    customer_payload: dict,
) -> None:
    for index in range(3):
        payload = customer_payload.copy()
        payload["customer_id"] = f"API-HIGH-RISK-PAGE-{index}"

        create_customer_with_prediction(
            client,
            payload,
        )

    response = client.get("/api/v1/customers/high-risk?limit=1&offset=1")

    assert response.status_code == 200

    data = response.json()

    assert data["limit"] == 1
    assert data["offset"] == 1
    assert len(data["customers"]) <= 1


def test_high_risk_endpoint_rejects_zero_limit(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/customers/high-risk?limit=0")

    assert response.status_code == 422


def test_high_risk_endpoint_rejects_negative_offset(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/customers/high-risk?offset=-1")

    assert response.status_code == 422
