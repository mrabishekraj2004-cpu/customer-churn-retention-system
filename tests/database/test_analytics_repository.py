from sqlalchemy.orm import Session

from src.database.repositories import (
    AnalyticsRepository,
    CustomerRepository,
    PredictionRepository,
    RetentionActionRepository,
)


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
    risk_level: str = "high",
    retention_action_required: bool = True,
):
    repository = PredictionRepository(db_session)

    return repository.create(
        customer_id=customer_id,
        churn_probability=churn_probability,
        risk_level=risk_level,
        retention_action_required=retention_action_required,
        operating_threshold=0.5,
        model_version="1.0.0",
    )


def test_total_customers_is_zero_when_database_is_empty(
    db_session: Session,
) -> None:
    analytics = AnalyticsRepository(db_session)

    assert analytics.get_total_customers() == 0


def test_get_total_customers(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    analytics = AnalyticsRepository(db_session)

    customers.create(
        customer_id="ANALYTICS-CUSTOMER-001",
        customer_data=customer_data(),
    )

    customers.create(
        customer_id="ANALYTICS-CUSTOMER-002",
        customer_data=customer_data(),
    )

    assert analytics.get_total_customers() == 2


def test_get_total_monthly_revenue(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    analytics = AnalyticsRepository(db_session)

    customers.create(
        customer_id="ANALYTICS-REVENUE-001",
        customer_data=customer_data(50.0),
    )

    customers.create(
        customer_id="ANALYTICS-REVENUE-002",
        customer_data=customer_data(75.5),
    )

    assert analytics.get_total_monthly_revenue() == 125.5


def test_total_monthly_revenue_is_zero_when_database_is_empty(
    db_session: Session,
) -> None:
    analytics = AnalyticsRepository(db_session)

    assert analytics.get_total_monthly_revenue() == 0.0


def test_get_latest_predictions_returns_one_prediction_per_customer(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    analytics = AnalyticsRepository(db_session)

    first_customer = customers.create(
        customer_id="ANALYTICS-LATEST-001",
        customer_data=customer_data(),
    )

    second_customer = customers.create(
        customer_id="ANALYTICS-LATEST-002",
        customer_data=customer_data(),
    )

    create_prediction(
        db_session,
        first_customer.id,
        churn_probability=0.40,
        risk_level="medium",
        retention_action_required=False,
    )

    latest_first = create_prediction(
        db_session,
        first_customer.id,
        churn_probability=0.90,
        risk_level="critical",
    )

    latest_second = create_prediction(
        db_session,
        second_customer.id,
        churn_probability=0.75,
        risk_level="high",
    )

    predictions = analytics.get_latest_predictions()

    assert len(predictions) == 2

    prediction_ids = {prediction.id for prediction in predictions}

    assert latest_first.id in prediction_ids
    assert latest_second.id in prediction_ids


def test_latest_predictions_excludes_older_prediction(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    analytics = AnalyticsRepository(db_session)

    customer = customers.create(
        customer_id="ANALYTICS-HISTORY-001",
        customer_data=customer_data(),
    )

    older_prediction = create_prediction(
        db_session,
        customer.id,
        churn_probability=0.30,
        risk_level="low",
        retention_action_required=False,
    )

    latest_prediction = create_prediction(
        db_session,
        customer.id,
        churn_probability=0.95,
        risk_level="critical",
    )

    predictions = analytics.get_latest_predictions()

    assert len(predictions) == 1
    assert predictions[0].id == latest_prediction.id
    assert predictions[0].id != older_prediction.id


def test_get_total_retention_actions(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    actions = RetentionActionRepository(db_session)
    analytics = AnalyticsRepository(db_session)

    customer = customers.create(
        customer_id="ANALYTICS-ACTION-001",
        customer_data=customer_data(),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
        churn_probability=0.90,
        risk_level="critical",
    )

    actions.create(
        prediction_id=prediction.id,
        action_type="priority_outreach",
        description="Contact customer.",
        estimated_cost=25.0,
    )

    actions.create(
        prediction_id=prediction.id,
        action_type="contract_migration",
        description="Offer contract migration.",
        estimated_cost=50.0,
    )

    assert analytics.get_total_retention_actions() == 2


def test_get_retention_action_count_by_status(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    actions = RetentionActionRepository(db_session)
    analytics = AnalyticsRepository(db_session)

    customer = customers.create(
        customer_id="ANALYTICS-STATUS-001",
        customer_data=customer_data(),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
        churn_probability=0.90,
        risk_level="critical",
    )

    recommended_action = actions.create(
        prediction_id=prediction.id,
        action_type="priority_outreach",
        description="Contact customer.",
    )

    in_progress_action = actions.create(
        prediction_id=prediction.id,
        action_type="contract_migration",
        description="Offer contract migration.",
    )

    actions.update_status(
        in_progress_action,
        status="in_progress",
    )

    assert recommended_action.status == "recommended"
    assert analytics.get_retention_action_count_by_status("recommended") == 1
    assert analytics.get_retention_action_count_by_status("in_progress") == 1
    assert analytics.get_retention_action_count_by_status("completed") == 0


def test_get_retention_action_count_by_outcome(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    actions = RetentionActionRepository(db_session)
    analytics = AnalyticsRepository(db_session)

    customer = customers.create(
        customer_id="ANALYTICS-OUTCOME-001",
        customer_data=customer_data(),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
        churn_probability=0.90,
        risk_level="critical",
    )

    retained_action = actions.create(
        prediction_id=prediction.id,
        action_type="priority_outreach",
        description="Contact customer.",
    )

    churned_action = actions.create(
        prediction_id=prediction.id,
        action_type="contract_migration",
        description="Offer contract migration.",
    )

    actions.update_status(
        retained_action,
        status="completed",
        outcome="retained",
    )

    actions.update_status(
        churned_action,
        status="completed",
        outcome="churned",
    )

    assert analytics.get_retention_action_count_by_outcome("retained") == 1
    assert analytics.get_retention_action_count_by_outcome("churned") == 1
    assert analytics.get_retention_action_count_by_outcome("unknown") == 0


def test_get_total_estimated_cost(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    actions = RetentionActionRepository(db_session)
    analytics = AnalyticsRepository(db_session)

    customer = customers.create(
        customer_id="ANALYTICS-COST-001",
        customer_data=customer_data(),
    )

    prediction = create_prediction(
        db_session,
        customer.id,
        churn_probability=0.90,
        risk_level="critical",
    )

    actions.create(
        prediction_id=prediction.id,
        action_type="priority_outreach",
        description="Contact customer.",
        estimated_cost=25.5,
    )

    actions.create(
        prediction_id=prediction.id,
        action_type="contract_migration",
        description="Offer contract migration.",
        estimated_cost=40.0,
    )

    actions.create(
        prediction_id=prediction.id,
        action_type="support_followup",
        description="Provide support.",
        estimated_cost=None,
    )

    assert analytics.get_total_estimated_cost() == 65.5


def test_total_estimated_cost_is_zero_when_database_is_empty(
    db_session: Session,
) -> None:
    analytics = AnalyticsRepository(db_session)

    assert analytics.get_total_estimated_cost() == 0.0


def test_get_monthly_revenue_at_risk(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    predictions = PredictionRepository(db_session)
    analytics = AnalyticsRepository(db_session)

    high_risk_customer = customers.create(
        customer_id="REVENUE-RISK-001",
        customer_data=customer_data(
            monthly_charges=100.0,
        ),
    )

    low_risk_customer = customers.create(
        customer_id="REVENUE-RISK-002",
        customer_data=customer_data(
            monthly_charges=50.0,
        ),
    )

    predictions.create(
        customer_id=high_risk_customer.id,
        churn_probability=0.90,
        risk_level="critical",
        retention_action_required=True,
        operating_threshold=0.80,
        model_version="1.0.0",
    )

    predictions.create(
        customer_id=low_risk_customer.id,
        churn_probability=0.20,
        risk_level="low",
        retention_action_required=False,
        operating_threshold=0.80,
        model_version="1.0.0",
    )

    result = analytics.get_monthly_revenue_at_risk()

    assert result == 100.0


def test_monthly_revenue_at_risk_uses_latest_prediction(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    predictions = PredictionRepository(db_session)
    analytics = AnalyticsRepository(db_session)

    customer = customers.create(
        customer_id="REVENUE-RISK-LATEST-001",
        customer_data=customer_data(
            monthly_charges=75.0,
        ),
    )

    predictions.create(
        customer_id=customer.id,
        churn_probability=0.90,
        risk_level="critical",
        retention_action_required=True,
        operating_threshold=0.80,
        model_version="1.0.0",
    )

    predictions.create(
        customer_id=customer.id,
        churn_probability=0.20,
        risk_level="low",
        retention_action_required=False,
        operating_threshold=0.80,
        model_version="1.0.0",
    )

    result = analytics.get_monthly_revenue_at_risk()

    assert result == 0.0


def test_monthly_revenue_at_risk_is_zero_when_database_is_empty(
    db_session: Session,
) -> None:
    analytics = AnalyticsRepository(db_session)

    assert analytics.get_monthly_revenue_at_risk() == 0.0
