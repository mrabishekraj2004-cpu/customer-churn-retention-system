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


def test_get_retention_action(
    client: TestClient,
    customer_payload: dict,
) -> None:
    action_id = create_retention_action(
        client,
        customer_payload,
    )

    response = client.get(f"/api/v1/retention-actions/{action_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == action_id
    assert data["action_type"] == "contract_migration"
    assert data["status"] == "recommended"
    assert data["outcome"] is None
    assert data["completed_at"] is None


def test_unknown_retention_action_returns_404(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/retention-actions/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == ("Retention action not found: 999999")


def test_move_retention_action_to_in_progress(
    client: TestClient,
    customer_payload: dict,
) -> None:
    action_id = create_retention_action(
        client,
        customer_payload,
    )

    response = client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == action_id
    assert data["status"] == "in_progress"
    assert data["outcome"] is None
    assert data["completed_at"] is None


def test_complete_retention_action_with_outcome(
    client: TestClient,
    customer_payload: dict,
) -> None:
    action_id = create_retention_action(
        client,
        customer_payload,
    )

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

    data = completed_response.json()

    assert data["id"] == action_id
    assert data["status"] == "completed"
    assert data["outcome"] == "retained"
    assert data["completed_at"] is not None


def test_cannot_complete_directly_from_recommended(
    client: TestClient,
    customer_payload: dict,
) -> None:
    action_id = create_retention_action(
        client,
        customer_payload,
    )

    response = client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "completed",
            "outcome": "retained",
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Cannot change retention action from recommended to completed."
    )


def test_completed_retention_action_requires_outcome(
    client: TestClient,
    customer_payload: dict,
) -> None:
    action_id = create_retention_action(
        client,
        customer_payload,
    )

    in_progress_response = client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "in_progress",
        },
    )

    assert in_progress_response.status_code == 200

    response = client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 409
    assert "An outcome is required" in response.json()["detail"]


def test_outcome_not_allowed_before_completion(
    client: TestClient,
    customer_payload: dict,
) -> None:
    action_id = create_retention_action(
        client,
        customer_payload,
    )

    response = client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "in_progress",
            "outcome": "retained",
        },
    )

    assert response.status_code == 409
    assert "Outcome can only be provided" in response.json()["detail"]


def test_invalid_retention_status_returns_422(
    client: TestClient,
    customer_payload: dict,
) -> None:
    action_id = create_retention_action(
        client,
        customer_payload,
    )

    response = client.patch(
        f"/api/v1/retention-actions/{action_id}",
        json={
            "status": "invalid-status",
        },
    )

    assert response.status_code == 422
