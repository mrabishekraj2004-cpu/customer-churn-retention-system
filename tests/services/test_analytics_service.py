from sqlalchemy.orm import Session

from src.database.repositories import (
    AnalyticsRepository,
    CustomerRepository,
    PredictionRepository,
    RetentionActionRepository,
)
from src.services.analytics_service import AnalyticsService


def customer_data(
    monthly_charges: float = 80.0,
) -> dict:
    return {
        "gender": "Male",
        "senior_citizen": 0,
        "partner": "No",
        "dependents": "No",
        "tenure": 10,
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
        "monthly_charges": monthly_charges,
        "total_charges": monthly_charges * 10,
    }


def create_prediction(
    db_session: Session,
    customer_id: int,
    churn_probability: float,
    risk_level: str,
    retention_action_required: bool,
):
    predictions = PredictionRepository(db_session)

    return predictions.create(
        customer_id=customer_id,
        churn_probability=churn_probability,
        risk_level=risk_level,
        retention_action_required=retention_action_required,
        operating_threshold=0.5,
        model_version="1.0.0",
    )


def test_empty_analytics_summary(
    db_session: Session,
) -> None:
    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.total_customers == 0
    assert summary.total_monthly_revenue == 0.0
    assert summary.customers_with_predictions == 0
    assert summary.high_risk_customers == 0
    assert summary.average_churn_probability == 0.0

    assert summary.low_risk_customers == 0
    assert summary.medium_risk_customers == 0
    assert summary.high_risk_level_customers == 0
    assert summary.critical_risk_customers == 0

    assert summary.total_retention_actions == 0
    assert summary.recommended_actions == 0
    assert summary.in_progress_actions == 0
    assert summary.completed_actions == 0

    assert summary.retained_customers == 0
    assert summary.churned_customers == 0
    assert summary.unknown_outcomes == 0

    assert summary.retention_success_rate == 0.0
    assert summary.total_estimated_cost == 0.0


def test_summary_calculates_customer_metrics(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)

    first_customer = customers.create(
        customer_id="SERVICE-ANALYTICS-001",
        customer_data=customer_data(50.0),
    )

    second_customer = customers.create(
        customer_id="SERVICE-ANALYTICS-002",
        customer_data=customer_data(100.0),
    )

    create_prediction(
        db_session,
        first_customer.id,
        churn_probability=0.20,
        risk_level="low",
        retention_action_required=False,
    )

    create_prediction(
        db_session,
        second_customer.id,
        churn_probability=0.80,
        risk_level="high",
        retention_action_required=True,
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.total_customers == 2
    assert summary.total_monthly_revenue == 150.0
    assert summary.customers_with_predictions == 2
    assert summary.high_risk_customers == 1
    assert summary.average_churn_probability == 0.5


def test_summary_uses_only_latest_prediction(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)

    customer = customers.create(
        customer_id="SERVICE-LATEST-001",
        customer_data=customer_data(),
    )

    create_prediction(
        db_session,
        customer.id,
        churn_probability=0.20,
        risk_level="low",
        retention_action_required=False,
    )

    create_prediction(
        db_session,
        customer.id,
        churn_probability=0.90,
        risk_level="critical",
        retention_action_required=True,
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.customers_with_predictions == 1
    assert summary.high_risk_customers == 1
    assert summary.average_churn_probability == 0.90

    assert summary.low_risk_customers == 0
    assert summary.critical_risk_customers == 1


def test_summary_calculates_risk_distribution(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)

    risk_levels = [
        ("low", 0.10, False),
        ("medium", 0.40, False),
        ("high", 0.70, True),
        ("critical", 0.95, True),
    ]

    for index, (
        risk_level,
        probability,
        action_required,
    ) in enumerate(risk_levels):
        customer = customers.create(
            customer_id=f"SERVICE-RISK-{index}",
            customer_data=customer_data(),
        )

        create_prediction(
            db_session,
            customer.id,
            churn_probability=probability,
            risk_level=risk_level,
            retention_action_required=action_required,
        )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.low_risk_customers == 1
    assert summary.medium_risk_customers == 1
    assert summary.high_risk_level_customers == 1
    assert summary.critical_risk_customers == 1

    assert summary.high_risk_customers == 2


def test_summary_calculates_retention_action_metrics(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    actions = RetentionActionRepository(db_session)

    customer = customers.create(
        customer_id="SERVICE-ACTIONS-001",
        customer_data=customer_data(),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
        churn_probability=0.90,
        risk_level="critical",
        retention_action_required=True,
    )

    actions.create(
        prediction_id=prediction.id,
        action_type="recommended_action",
        description="Recommended action.",
        estimated_cost=10.0,
    )

    in_progress = actions.create(
        prediction_id=prediction.id,
        action_type="in_progress_action",
        description="In progress action.",
        estimated_cost=20.0,
    )

    completed_retained = actions.create(
        prediction_id=prediction.id,
        action_type="retained_action",
        description="Completed retained action.",
        estimated_cost=30.0,
    )

    completed_churned = actions.create(
        prediction_id=prediction.id,
        action_type="churned_action",
        description="Completed churned action.",
        estimated_cost=40.0,
    )

    actions.update_status(
        in_progress,
        status="in_progress",
    )

    actions.update_status(
        completed_retained,
        status="completed",
        outcome="retained",
    )

    actions.update_status(
        completed_churned,
        status="completed",
        outcome="churned",
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.total_retention_actions == 4
    assert summary.recommended_actions == 1
    assert summary.in_progress_actions == 1
    assert summary.completed_actions == 2

    assert summary.retained_customers == 1
    assert summary.churned_customers == 1
    assert summary.unknown_outcomes == 0

    assert summary.retention_success_rate == 50.0
    assert summary.total_estimated_cost == 100.0


def test_retention_success_rate_excludes_unknown_outcomes(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    actions = RetentionActionRepository(db_session)

    customer = customers.create(
        customer_id="SERVICE-OUTCOME-001",
        customer_data=customer_data(),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
        churn_probability=0.90,
        risk_level="critical",
        retention_action_required=True,
    )

    retained = actions.create(
        prediction_id=prediction.id,
        action_type="retained_action",
        description="Retained customer.",
    )

    churned = actions.create(
        prediction_id=prediction.id,
        action_type="churned_action",
        description="Churned customer.",
    )

    unknown = actions.create(
        prediction_id=prediction.id,
        action_type="unknown_action",
        description="Unknown outcome.",
    )

    actions.update_status(
        retained,
        status="completed",
        outcome="retained",
    )

    actions.update_status(
        churned,
        status="completed",
        outcome="churned",
    )

    actions.update_status(
        unknown,
        status="completed",
        outcome="unknown",
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.retained_customers == 1
    assert summary.churned_customers == 1
    assert summary.unknown_outcomes == 1

    # Unknown outcomes do not affect the success-rate denominator.
    assert summary.retention_success_rate == 50.0


def test_retention_success_rate_is_zero_without_resolved_outcomes(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    actions = RetentionActionRepository(db_session)

    customer = customers.create(
        customer_id="SERVICE-NO-RESOLVED-001",
        customer_data=customer_data(),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
        churn_probability=0.90,
        risk_level="critical",
        retention_action_required=True,
    )

    unknown = actions.create(
        prediction_id=prediction.id,
        action_type="unknown_action",
        description="Unknown outcome.",
    )

    actions.update_status(
        unknown,
        status="completed",
        outcome="unknown",
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.retained_customers == 0
    assert summary.churned_customers == 0
    assert summary.unknown_outcomes == 1
    assert summary.retention_success_rate == 0.0

def test_summary_calculates_monthly_revenue_at_risk(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)

    high_risk_customer = customers.create(
        customer_id="SERVICE-REVENUE-RISK-001",
        customer_data=customer_data(
            monthly_charges=100.0,
        ),
    )

    low_risk_customer = customers.create(
        customer_id="SERVICE-REVENUE-RISK-002",
        customer_data=customer_data(
            monthly_charges=50.0,
        ),
    )

    create_prediction(
        db_session,
        high_risk_customer.id,
        churn_probability=0.90,
        risk_level="critical",
        retention_action_required=True,
    )

    create_prediction(
        db_session,
        low_risk_customer.id,
        churn_probability=0.20,
        risk_level="low",
        retention_action_required=False,
    )

    service = AnalyticsService(
        AnalyticsRepository(db_session)
    )

    summary = service.get_summary()

    assert summary.total_monthly_revenue == 150.0
    assert summary.monthly_revenue_at_risk == 100.0


def test_summary_monthly_revenue_at_risk_is_zero_when_empty(
    db_session: Session,
) -> None:
    service = AnalyticsService(
        AnalyticsRepository(db_session)
    )

    summary = service.get_summary()

    assert summary.monthly_revenue_at_risk == 0.0