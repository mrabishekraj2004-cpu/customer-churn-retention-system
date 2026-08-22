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
        == (prediction["churn_probability"])
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
        latest_prediction["churn_probability"]
        == (second_prediction["churn_probability"])
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

    create_customer_with_prediction(client, first_payload)
    create_customer_with_prediction(client, second_payload)
    create_customer_with_prediction(client, third_payload)

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
