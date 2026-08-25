from fastapi.testclient import TestClient


def create_retention_action(
    client: TestClient,
    customer_payload: dict,
) -> int:
    response = client.post(
        "/api/v1/predict",
        json=customer_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["retention_action_required"] is True

    action_id = data["retention_recommendation"]["action_id"]

    assert action_id is not None

    return action_id


def test_get_retention_actions_returns_action_list(
    client: TestClient,
    customer_payload: dict,
) -> None:
    action_id = create_retention_action(
        client,
        customer_payload,
    )

    response = client.get("/api/v1/retention-actions")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert len(data["actions"]) == 1

    action = data["actions"][0]

    assert action["id"] == action_id
    assert action["status"] == "recommended"
    assert action["action_type"] == "contract_migration"


def test_get_retention_actions_filters_by_status(
    client: TestClient,
    customer_payload: dict,
) -> None:
    first_payload = customer_payload.copy()
    first_payload["customer_id"] = "ACTION-FILTER-001"

    second_payload = customer_payload.copy()
    second_payload["customer_id"] = "ACTION-FILTER-002"

    recommended_action_id = create_retention_action(
        client,
        first_payload,
    )

    completed_action_id = create_retention_action(
        client,
        second_payload,
    )

    response = client.patch(
        f"/api/v1/retention-actions/{completed_action_id}",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/retention-actions/{completed_action_id}",
        json={
            "status": "completed",
            "outcome": "retained",
        },
    )

    assert response.status_code == 200

    response = client.get("/api/v1/retention-actions?status=recommended")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert len(data["actions"]) == 1
    assert data["actions"][0]["id"] == recommended_action_id
    assert data["actions"][0]["status"] == "recommended"


def test_get_retention_actions_filters_completed_status(
    client: TestClient,
    customer_payload: dict,
) -> None:
    first_payload = customer_payload.copy()
    first_payload["customer_id"] = "ACTION-COMPLETED-001"

    second_payload = customer_payload.copy()
    second_payload["customer_id"] = "ACTION-COMPLETED-002"

    create_retention_action(
        client,
        first_payload,
    )

    completed_action_id = create_retention_action(
        client,
        second_payload,
    )

    response = client.patch(
        f"/api/v1/retention-actions/{completed_action_id}",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/retention-actions/{completed_action_id}",
        json={
            "status": "completed",
            "outcome": "retained",
        },
    )

    assert response.status_code == 200

    response = client.get("/api/v1/retention-actions?status=completed")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert len(data["actions"]) == 1

    action = data["actions"][0]

    assert action["id"] == completed_action_id
    assert action["status"] == "completed"
    assert action["outcome"] == "retained"


def test_get_retention_actions_respects_limit_and_offset(
    client: TestClient,
    customer_payload: dict,
) -> None:
    for index in range(3):
        payload = customer_payload.copy()
        payload["customer_id"] = f"ACTION-PAGE-{index}"

        create_retention_action(
            client,
            payload,
        )

    response = client.get("/api/v1/retention-actions?limit=2&offset=1")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["actions"]) == 2


def test_get_retention_actions_rejects_zero_limit(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/retention-actions?limit=0")

    assert response.status_code == 422


def test_get_retention_actions_rejects_negative_offset(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/retention-actions?offset=-1")

    assert response.status_code == 422


def test_get_retention_actions_rejects_limit_above_maximum(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/retention-actions?limit=501")

    assert response.status_code == 422


def test_get_retention_actions_rejects_invalid_status(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/retention-actions?status=invalid-status")

    assert response.status_code == 422
