from sqlalchemy.orm import Session

from src.database.repositories import (
    CustomerRepository,
    PredictionRepository,
    RetentionActionRepository,
)
from tests.database.test_customer_repository import customer_data


def create_prediction(
    db_session: Session,
    customer_id: str,
):
    customers = CustomerRepository(db_session)
    predictions = PredictionRepository(db_session)

    customer = customers.create(
        customer_id=customer_id,
        customer_data=customer_data(),
    )

    return predictions.create(
        customer_id=customer.id,
        churn_probability=0.91,
        risk_level="critical",
        retention_action_required=True,
        operating_threshold=0.8,
        model_version="1.0.0",
    )


def test_retention_action_lifecycle(
    db_session: Session,
) -> None:
    actions = RetentionActionRepository(db_session)

    prediction = create_prediction(
        db_session,
        customer_id="ACTION-0001",
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


def test_get_all_returns_retention_actions(
    db_session: Session,
) -> None:
    actions = RetentionActionRepository(db_session)

    first_prediction = create_prediction(
        db_session,
        customer_id="ACTION-LIST-001",
    )
    second_prediction = create_prediction(
        db_session,
        customer_id="ACTION-LIST-002",
    )

    first_action = actions.create(
        prediction_id=first_prediction.id,
        action_type="priority_outreach",
        description="Contact first customer.",
        estimated_cost=50.0,
    )

    second_action = actions.create(
        prediction_id=second_prediction.id,
        action_type="contract_migration",
        description="Offer contract migration.",
        estimated_cost=40.0,
    )

    result = actions.get_all()

    action_ids = {action.id for action in result}

    assert len(result) == 2
    assert first_action.id in action_ids
    assert second_action.id in action_ids


def test_get_all_filters_by_status(
    db_session: Session,
) -> None:
    actions = RetentionActionRepository(db_session)

    first_prediction = create_prediction(
        db_session,
        customer_id="ACTION-STATUS-001",
    )
    second_prediction = create_prediction(
        db_session,
        customer_id="ACTION-STATUS-002",
    )

    recommended_action = actions.create(
        prediction_id=first_prediction.id,
        action_type="priority_outreach",
        description="Recommended action.",
        estimated_cost=50.0,
    )

    completed_action = actions.create(
        prediction_id=second_prediction.id,
        action_type="contract_migration",
        description="Completed action.",
        estimated_cost=40.0,
    )

    actions.update_status(
        completed_action,
        status="completed",
        outcome="retained",
    )

    result = actions.get_all(
        status="recommended",
    )

    assert len(result) == 1
    assert result[0].id == recommended_action.id
    assert result[0].status == "recommended"


def test_get_all_returns_completed_actions(
    db_session: Session,
) -> None:
    actions = RetentionActionRepository(db_session)

    first_prediction = create_prediction(
        db_session,
        customer_id="ACTION-COMPLETED-001",
    )
    second_prediction = create_prediction(
        db_session,
        customer_id="ACTION-COMPLETED-002",
    )

    actions.create(
        prediction_id=first_prediction.id,
        action_type="priority_outreach",
        description="Recommended action.",
        estimated_cost=50.0,
    )

    completed_action = actions.create(
        prediction_id=second_prediction.id,
        action_type="contract_migration",
        description="Completed action.",
        estimated_cost=40.0,
    )

    actions.update_status(
        completed_action,
        status="completed",
        outcome="retained",
    )

    result = actions.get_all(
        status="completed",
    )

    assert len(result) == 1
    assert result[0].id == completed_action.id
    assert result[0].status == "completed"
    assert result[0].outcome == "retained"


def test_get_all_respects_limit(
    db_session: Session,
) -> None:
    actions = RetentionActionRepository(db_session)

    for index in range(3):
        prediction = create_prediction(
            db_session,
            customer_id=f"ACTION-LIMIT-{index}",
        )

        actions.create(
            prediction_id=prediction.id,
            action_type="priority_outreach",
            description=f"Action {index}.",
            estimated_cost=50.0,
        )

    result = actions.get_all(
        limit=2,
        offset=0,
    )

    assert len(result) == 2


def test_get_all_respects_offset(
    db_session: Session,
) -> None:
    actions = RetentionActionRepository(db_session)

    for index in range(3):
        prediction = create_prediction(
            db_session,
            customer_id=f"ACTION-OFFSET-{index}",
        )

        actions.create(
            prediction_id=prediction.id,
            action_type="priority_outreach",
            description=f"Action {index}.",
            estimated_cost=50.0,
        )

    all_actions = actions.get_all(
        limit=100,
        offset=0,
    )

    offset_actions = actions.get_all(
        limit=100,
        offset=1,
    )

    assert len(all_actions) == 3
    assert len(offset_actions) == 2

    assert offset_actions == all_actions[1:]
