from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.database.repositories import RetentionActionRepository


def test_high_risk_prediction_creates_retention_action(
    client: TestClient,
    customer_payload: dict,
    db_session: Session,
) -> None:
    response = client.post(
        "/api/v1/predict",
        json=customer_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["retention_action_required"] is True

    recommendation = data["retention_recommendation"]

    assert recommendation["action_id"] is not None
    assert recommendation["action_type"] == "contract_migration"
    assert recommendation["priority"] == "high"
    assert recommendation["suggested_offer"] == (
        "Discount for switching to a one-year contract"
    )

    repository = RetentionActionRepository(db_session)

    actions = repository.get_by_prediction(data["prediction_id"])

    assert len(actions) == 1

    action = actions[0]

    assert action.id == recommendation["action_id"]
    assert action.prediction_id == data["prediction_id"]
    assert action.action_type == "contract_migration"
    assert action.status == "recommended"


def test_retention_recommendation_contains_risk_factors(
    client: TestClient,
    customer_payload: dict,
) -> None:
    response = client.post(
        "/api/v1/predict",
        json=customer_payload,
    )

    assert response.status_code == 200

    recommendation = response.json()["retention_recommendation"]

    risk_factors = recommendation["risk_factors"]

    assert "Month-to-month contract" in risk_factors
    assert "Fiber optic service" in risk_factors
    assert "No technical support" in risk_factors
    assert "Electronic check payment" in risk_factors
    assert "Low customer tenure" in risk_factors
