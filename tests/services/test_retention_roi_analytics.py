from sqlalchemy.orm import Session

from src.database.repositories import (
    AnalyticsRepository,
    CustomerRepository,
    PredictionRepository,
    RetentionActionRepository,
)
from src.services.analytics_service import AnalyticsService


def customer_data(
    monthly_charges: float = 100.0,
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
    churn_probability: float = 0.90,
    risk_level: str = "critical",
    retention_action_required: bool = True,
):
    predictions = PredictionRepository(db_session)

    return predictions.create(
        customer_id=customer_id,
        churn_probability=churn_probability,
        risk_level=risk_level,
        retention_action_required=retention_action_required,
        operating_threshold=0.80,
        model_version="1.0.0",
    )


def create_completed_retained_action(
    db_session: Session,
    prediction_id: int,
    estimated_cost: float | None,
):
    actions = RetentionActionRepository(db_session)

    action = actions.create(
        prediction_id=prediction_id,
        action_type="priority_outreach",
        description="Contact high-risk customer.",
        estimated_cost=estimated_cost,
    )

    actions.update_status(
        action,
        status="in_progress",
    )

    return actions.update_status(
        action,
        status="completed",
        outcome="retained",
    )


def test_summary_calculates_revenue_saved(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)

    customer = customers.create(
        customer_id="ROI-REVENUE-SAVED-001",
        customer_data=customer_data(
            monthly_charges=100.0,
        ),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
    )

    create_completed_retained_action(
        db_session,
        prediction.id,
        estimated_cost=100.0,
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    # Retained monthly revenue = 100
    # Annual revenue saved = 100 * 12
    assert summary.revenue_saved == 1200.0


def test_summary_calculates_net_retention_benefit(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)

    customer = customers.create(
        customer_id="ROI-NET-BENEFIT-001",
        customer_data=customer_data(
            monthly_charges=100.0,
        ),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
    )

    create_completed_retained_action(
        db_session,
        prediction.id,
        estimated_cost=200.0,
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    # Revenue saved = 100 * 12 = 1200
    # Net benefit = 1200 - 200
    assert summary.revenue_saved == 1200.0
    assert summary.total_estimated_cost == 200.0
    assert summary.net_retention_benefit == 1000.0


def test_summary_calculates_retention_roi(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)

    customer = customers.create(
        customer_id="ROI-PERCENTAGE-001",
        customer_data=customer_data(
            monthly_charges=100.0,
        ),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
    )

    create_completed_retained_action(
        db_session,
        prediction.id,
        estimated_cost=200.0,
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    # Revenue saved = 1200
    # Cost = 200
    # Net benefit = 1000
    #
    # ROI = (1000 / 200) * 100
    # ROI = 500%
    assert summary.revenue_saved == 1200.0
    assert summary.net_retention_benefit == 1000.0
    assert summary.retention_roi == 500.0


def test_retention_roi_is_zero_when_cost_is_zero(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)

    customer = customers.create(
        customer_id="ROI-ZERO-COST-001",
        customer_data=customer_data(
            monthly_charges=100.0,
        ),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
    )

    create_completed_retained_action(
        db_session,
        prediction.id,
        estimated_cost=0.0,
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.revenue_saved == 1200.0
    assert summary.total_estimated_cost == 0.0
    assert summary.net_retention_benefit == 1200.0

    # Avoid division by zero.
    assert summary.retention_roi == 0.0


def test_retention_business_metrics_are_zero_when_database_is_empty(
    db_session: Session,
) -> None:
    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.revenue_saved == 0.0
    assert summary.net_retention_benefit == 0.0
    assert summary.retention_roi == 0.0


def test_revenue_saved_counts_only_retained_customers(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    actions = RetentionActionRepository(db_session)

    retained_customer = customers.create(
        customer_id="ROI-RETAINED-001",
        customer_data=customer_data(
            monthly_charges=100.0,
        ),
    )

    churned_customer = customers.create(
        customer_id="ROI-CHURNED-001",
        customer_data=customer_data(
            monthly_charges=50.0,
        ),
    )

    retained_prediction = create_prediction(
        db_session,
        retained_customer.id,
    )

    churned_prediction = create_prediction(
        db_session,
        churned_customer.id,
    )

    retained_action = actions.create(
        prediction_id=retained_prediction.id,
        action_type="priority_outreach",
        description="Contact retained customer.",
        estimated_cost=100.0,
    )

    actions.update_status(
        retained_action,
        status="in_progress",
    )

    actions.update_status(
        retained_action,
        status="completed",
        outcome="retained",
    )

    churned_action = actions.create(
        prediction_id=churned_prediction.id,
        action_type="priority_outreach",
        description="Contact churned customer.",
        estimated_cost=50.0,
    )

    actions.update_status(
        churned_action,
        status="in_progress",
    )

    actions.update_status(
        churned_action,
        status="completed",
        outcome="churned",
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    # Only the retained customer's revenue is saved.
    #
    # 100 * 12 = 1200
    assert summary.revenue_saved == 1200.0

    # Both retention actions still cost money.
    assert summary.total_estimated_cost == 150.0

    # 1200 - 150 = 1050
    assert summary.net_retention_benefit == 1050.0

    # (1050 / 150) * 100 = 700%
    assert summary.retention_roi == 700.0
