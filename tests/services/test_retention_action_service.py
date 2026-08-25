import pytest
from sqlalchemy.orm import Session

from src.database.repositories import (
    CustomerRepository,
    PredictionRepository,
    RetentionActionRepository,
)
from src.services.retention_action_service import (
    InvalidRetentionActionUpdateError,
    RetentionActionNotFoundError,
    RetentionActionService,
)


def create_retention_action(
    db_session: Session,
    customer_id: str = "RETENTION-TEST-001",
):
    customers = CustomerRepository(db_session)
    predictions = PredictionRepository(db_session)
    actions = RetentionActionRepository(db_session)

    customer = customers.create(
        customer_id=customer_id,
        customer_data={
            "gender": "Male",
            "senior_citizen": 0,
            "partner": "No",
            "dependents": "No",
            "tenure": 5,
            "phone_service": "Yes",
            "multiple_lines": "No",
            "internet_service": "Fiber optic",
            "online_security": "No",
            "online_backup": "No",
            "device_protection": "No",
            "tech_support": "No",
            "streaming_tv": "Yes",
            "streaming_movies": "Yes",
            "contract": "Month-to-month",
            "paperless_billing": "Yes",
            "payment_method": "Electronic check",
            "monthly_charges": 89.50,
            "total_charges": 447.50,
        },
    )

    prediction = predictions.create(
        customer_id=customer.id,
        churn_probability=0.90,
        risk_level="critical",
        retention_action_required=True,
        operating_threshold=0.80,
        model_version="1.0.0",
    )

    return actions.create(
        prediction_id=prediction.id,
        action_type="contract_migration",
        description="Offer contract migration incentive.",
    )


def test_get_retention_action(
    db_session: Session,
) -> None:
    action = create_retention_action(db_session)

    service = RetentionActionService(RetentionActionRepository(db_session))

    result = service.get_action(action.id)

    assert result.id == action.id
    assert result.status == "recommended"
    assert result.action_type == "contract_migration"


def test_unknown_retention_action_raises_error(
    db_session: Session,
) -> None:
    service = RetentionActionService(RetentionActionRepository(db_session))

    with pytest.raises(
        RetentionActionNotFoundError,
        match="Retention action not found: 999999",
    ):
        service.get_action(999999)


def test_move_action_to_in_progress(
    db_session: Session,
) -> None:
    action = create_retention_action(db_session)

    service = RetentionActionService(RetentionActionRepository(db_session))

    result = service.update_action(
        action_id=action.id,
        status="in_progress",
    )

    assert result.status == "in_progress"
    assert result.outcome is None
    assert result.completed_at is None


def test_complete_action_with_outcome(
    db_session: Session,
) -> None:
    action = create_retention_action(db_session)

    service = RetentionActionService(RetentionActionRepository(db_session))

    service.update_action(
        action_id=action.id,
        status="in_progress",
    )

    result = service.update_action(
        action_id=action.id,
        status="completed",
        outcome="retained",
    )

    assert result.status == "completed"
    assert result.outcome == "retained"
    assert result.completed_at is not None


def test_cannot_complete_directly_from_recommended(
    db_session: Session,
) -> None:
    action = create_retention_action(db_session)

    service = RetentionActionService(RetentionActionRepository(db_session))

    with pytest.raises(
        InvalidRetentionActionUpdateError,
        match="Cannot change retention action from recommended to completed",
    ):
        service.update_action(
            action_id=action.id,
            status="completed",
            outcome="retained",
        )


def test_completed_action_requires_outcome(
    db_session: Session,
) -> None:
    action = create_retention_action(db_session)

    service = RetentionActionService(RetentionActionRepository(db_session))

    service.update_action(
        action_id=action.id,
        status="in_progress",
    )

    with pytest.raises(
        InvalidRetentionActionUpdateError,
        match="An outcome is required",
    ):
        service.update_action(
            action_id=action.id,
            status="completed",
        )


def test_outcome_not_allowed_before_completion(
    db_session: Session,
) -> None:
    action = create_retention_action(db_session)

    service = RetentionActionService(RetentionActionRepository(db_session))

    with pytest.raises(
        InvalidRetentionActionUpdateError,
        match="Outcome can only be provided",
    ):
        service.update_action(
            action_id=action.id,
            status="in_progress",
            outcome="retained",
        )


def test_get_actions_returns_retention_actions(
    db_session: Session,
) -> None:
    first_action = create_retention_action(
        db_session,
        customer_id="RETENTION-LIST-001",
    )

    second_action = create_retention_action(
        db_session,
        customer_id="RETENTION-LIST-002",
    )

    service = RetentionActionService(RetentionActionRepository(db_session))

    result = service.get_actions()

    action_ids = {action.id for action in result}

    assert len(result) == 2
    assert first_action.id in action_ids
    assert second_action.id in action_ids


def test_get_actions_filters_by_status(
    db_session: Session,
) -> None:
    recommended_action = create_retention_action(
        db_session,
        customer_id="RETENTION-STATUS-001",
    )

    completed_action = create_retention_action(
        db_session,
        customer_id="RETENTION-STATUS-002",
    )

    service = RetentionActionService(RetentionActionRepository(db_session))

    service.update_action(
        action_id=completed_action.id,
        status="in_progress",
    )

    service.update_action(
        action_id=completed_action.id,
        status="completed",
        outcome="retained",
    )

    result = service.get_actions(
        status="recommended",
    )

    assert len(result) == 1
    assert result[0].id == recommended_action.id
    assert result[0].status == "recommended"


def test_get_actions_returns_completed_actions(
    db_session: Session,
) -> None:
    create_retention_action(
        db_session,
        customer_id="RETENTION-COMPLETED-001",
    )

    completed_action = create_retention_action(
        db_session,
        customer_id="RETENTION-COMPLETED-002",
    )

    service = RetentionActionService(RetentionActionRepository(db_session))

    service.update_action(
        action_id=completed_action.id,
        status="in_progress",
    )

    service.update_action(
        action_id=completed_action.id,
        status="completed",
        outcome="retained",
    )

    result = service.get_actions(
        status="completed",
    )

    assert len(result) == 1
    assert result[0].id == completed_action.id
    assert result[0].status == "completed"
    assert result[0].outcome == "retained"


def test_get_actions_respects_limit(
    db_session: Session,
) -> None:
    for index in range(3):
        create_retention_action(
            db_session,
            customer_id=f"RETENTION-LIMIT-{index}",
        )

    service = RetentionActionService(RetentionActionRepository(db_session))

    result = service.get_actions(
        limit=2,
        offset=0,
    )

    assert len(result) == 2


def test_get_actions_respects_offset(
    db_session: Session,
) -> None:
    for index in range(3):
        create_retention_action(
            db_session,
            customer_id=f"RETENTION-OFFSET-{index}",
        )

    service = RetentionActionService(RetentionActionRepository(db_session))

    all_actions = service.get_actions(
        limit=100,
        offset=0,
    )

    offset_actions = service.get_actions(
        limit=100,
        offset=1,
    )

    assert len(all_actions) == 3
    assert len(offset_actions) == 2
    assert offset_actions == all_actions[1:]
