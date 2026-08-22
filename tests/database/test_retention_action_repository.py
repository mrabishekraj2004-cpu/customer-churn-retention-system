from sqlalchemy.orm import Session

from src.database.repositories import (
    CustomerRepository,
    PredictionRepository,
    RetentionActionRepository,
)
from tests.database.test_customer_repository import customer_data


def test_retention_action_lifecycle(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    predictions = PredictionRepository(db_session)
    actions = RetentionActionRepository(db_session)

    customer = customers.create(
        customer_id="ACTION-0001",
        customer_data=customer_data(),
    )

    prediction = predictions.create(
        customer_id=customer.id,
        churn_probability=0.91,
        risk_level="critical",
        retention_action_required=True,
        operating_threshold=0.8,
        model_version="1.0.0",
    )

    action = actions.create(
        prediction_id=prediction.id,
        action_type="priority_outreach",
        description="Contact customer with a retention offer.",
        estimated_cost=60.0,
    )

    stored_actions = actions.get_by_prediction(prediction.id)

    assert action.id is not None
    assert len(stored_actions) == 1
    assert stored_actions[0].status == "recommended"

    updated = actions.update_status(
        action,
        status="completed",
        outcome="retained",
    )

    assert updated.status == "completed"
    assert updated.outcome == "retained"
    assert updated.completed_at is not None
