from sqlalchemy.orm import Session

from src.database.repositories import (
    AnalyticsRepository,
    CustomerRepository,
    PredictionRepository,
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


def test_summary_calculates_annual_revenue_at_risk(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)

    customer = customers.create(
        customer_id="ANNUAL-RISK-001",
        customer_data=customer_data(
            monthly_charges=100.0,
        ),
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

    assert summary.monthly_revenue_at_risk == 100.0
    assert summary.annual_revenue_at_risk == 1200.0


def test_summary_calculates_expected_annual_revenue_loss(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)

    customer_one = customers.create(
        customer_id="ANNUAL-EXPECTED-001",
        customer_data=customer_data(
            monthly_charges=100.0,
        ),
    )

    customer_two = customers.create(
        customer_id="ANNUAL-EXPECTED-002",
        customer_data=customer_data(
            monthly_charges=50.0,
        ),
    )

    create_prediction(
        db_session,
        customer_one.id,
        churn_probability=0.90,
        risk_level="critical",
        retention_action_required=True,
    )

    create_prediction(
        db_session,
        customer_two.id,
        churn_probability=0.20,
        risk_level="low",
        retention_action_required=False,
    )

    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.expected_monthly_revenue_loss == 100.0
    assert summary.expected_annual_revenue_loss == 1200.0


def test_annual_metrics_are_zero_when_database_is_empty(
    db_session: Session,
) -> None:
    service = AnalyticsService(AnalyticsRepository(db_session))

    summary = service.get_summary()

    assert summary.annual_revenue_at_risk == 0.0
    assert summary.expected_annual_revenue_loss == 0.0
