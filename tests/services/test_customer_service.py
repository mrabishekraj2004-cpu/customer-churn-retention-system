import pytest
from sqlalchemy.orm import Session

from src.database.repositories import (
    CustomerRepository,
    PredictionRepository,
)
from src.services.customer_service import (
    CustomerNotFoundError,
    CustomerService,
)


def create_customer(
    db_session: Session,
    customer_id: str = "CUSTOMER-SERVICE-001",
):
    repository = CustomerRepository(db_session)

    return repository.create(
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


def create_service(
    db_session: Session,
) -> CustomerService:
    return CustomerService(
        customer_repository=CustomerRepository(db_session),
        prediction_repository=PredictionRepository(db_session),
    )


def create_prediction(
    db_session: Session,
    customer_id: int,
    churn_probability: float,
    retention_action_required: bool,
    risk_level: str = "critical",
):
    repository = PredictionRepository(db_session)

    return repository.create(
        customer_id=customer_id,
        churn_probability=churn_probability,
        risk_level=risk_level,
        retention_action_required=retention_action_required,
        operating_threshold=0.80,
        model_version="1.0.0",
    )


def test_get_customer_without_prediction(
    db_session: Session,
) -> None:
    customer = create_customer(db_session)

    service = create_service(db_session)

    result = service.get_customer(customer.customer_id)

    assert result.customer_id == customer.customer_id
    assert result.tenure == 5
    assert result.contract == "Month-to-month"
    assert result.internet_service == "Fiber optic"
    assert result.monthly_charges == 89.50
    assert result.latest_prediction is None


def test_get_customer_with_latest_prediction(
    db_session: Session,
) -> None:
    customer = create_customer(db_session)

    create_prediction(
        db_session,
        customer_id=customer.id,
        churn_probability=0.45,
        retention_action_required=False,
        risk_level="medium",
    )

    latest_prediction = create_prediction(
        db_session,
        customer_id=customer.id,
        churn_probability=0.91,
        retention_action_required=True,
        risk_level="critical",
    )

    service = create_service(db_session)

    result = service.get_customer(customer.customer_id)

    assert result.latest_prediction is not None
    assert result.latest_prediction.prediction_id == latest_prediction.id
    assert result.latest_prediction.churn_probability == pytest.approx(0.91)
    assert result.latest_prediction.risk_level == "critical"
    assert result.latest_prediction.retention_action_required is True


def test_unknown_customer_raises_error(
    db_session: Session,
) -> None:
    service = create_service(db_session)

    with pytest.raises(
        CustomerNotFoundError,
        match="Customer not found: UNKNOWN-CUSTOMER",
    ):
        service.get_customer("UNKNOWN-CUSTOMER")


def test_get_customers_returns_customer_summaries(
    db_session: Session,
) -> None:
    first_customer = create_customer(
        db_session,
        customer_id="CUSTOMER-LIST-001",
    )

    second_customer = create_customer(
        db_session,
        customer_id="CUSTOMER-LIST-002",
    )

    prediction = create_prediction(
        db_session,
        customer_id=first_customer.id,
        churn_probability=0.88,
        retention_action_required=True,
        risk_level="critical",
    )

    service = create_service(db_session)

    result = service.get_customers(
        limit=100,
        offset=0,
    )

    assert result.count == 2
    assert result.limit == 100
    assert result.offset == 0

    customers_by_id = {customer.customer_id: customer for customer in result.customers}

    first_result = customers_by_id[first_customer.customer_id]
    second_result = customers_by_id[second_customer.customer_id]

    assert first_result.latest_prediction is not None
    assert first_result.latest_prediction.prediction_id == prediction.id
    assert first_result.latest_prediction.risk_level == "critical"

    assert second_result.latest_prediction is None


def test_get_customers_respects_limit_and_offset(
    db_session: Session,
) -> None:
    create_customer(
        db_session,
        customer_id="CUSTOMER-PAGE-001",
    )
    create_customer(
        db_session,
        customer_id="CUSTOMER-PAGE-002",
    )
    create_customer(
        db_session,
        customer_id="CUSTOMER-PAGE-003",
    )

    service = create_service(db_session)

    result = service.get_customers(
        limit=2,
        offset=0,
    )

    assert result.count == 2
    assert result.limit == 2
    assert result.offset == 0
    assert len(result.customers) == 2


def test_get_high_risk_customers_filters_non_actionable_customers(
    db_session: Session,
) -> None:
    high_risk_customer = create_customer(
        db_session,
        customer_id="HIGH-RISK-001",
    )

    low_risk_customer = create_customer(
        db_session,
        customer_id="LOW-RISK-001",
    )

    create_prediction(
        db_session,
        customer_id=high_risk_customer.id,
        churn_probability=0.92,
        retention_action_required=True,
        risk_level="critical",
    )

    create_prediction(
        db_session,
        customer_id=low_risk_customer.id,
        churn_probability=0.30,
        retention_action_required=False,
        risk_level="low",
    )

    service = create_service(db_session)

    result = service.get_high_risk_customers()

    assert result.count == 1
    assert len(result.customers) == 1

    customer = result.customers[0]

    assert customer.customer_id == "HIGH-RISK-001"
    assert customer.churn_probability == pytest.approx(0.92)
    assert customer.risk_level == "critical"


def test_high_risk_queue_uses_latest_prediction(
    db_session: Session,
) -> None:
    customer = create_customer(
        db_session,
        customer_id="LATEST-RISK-001",
    )

    create_prediction(
        db_session,
        customer_id=customer.id,
        churn_probability=0.95,
        retention_action_required=True,
        risk_level="critical",
    )

    create_prediction(
        db_session,
        customer_id=customer.id,
        churn_probability=0.25,
        retention_action_required=False,
        risk_level="low",
    )

    service = create_service(db_session)

    result = service.get_high_risk_customers()

    assert result.count == 0
    assert result.customers == []


def test_high_risk_customers_are_sorted_by_probability(
    db_session: Session,
) -> None:
    first_customer = create_customer(
        db_session,
        customer_id="RISK-SORT-001",
    )
    second_customer = create_customer(
        db_session,
        customer_id="RISK-SORT-002",
    )
    third_customer = create_customer(
        db_session,
        customer_id="RISK-SORT-003",
    )

    create_prediction(
        db_session,
        customer_id=first_customer.id,
        churn_probability=0.84,
        retention_action_required=True,
        risk_level="high",
    )

    create_prediction(
        db_session,
        customer_id=second_customer.id,
        churn_probability=0.97,
        retention_action_required=True,
        risk_level="critical",
    )

    create_prediction(
        db_session,
        customer_id=third_customer.id,
        churn_probability=0.90,
        retention_action_required=True,
        risk_level="critical",
    )

    service = create_service(db_session)

    result = service.get_high_risk_customers()

    probabilities = [customer.churn_probability for customer in result.customers]

    assert probabilities == pytest.approx(
        [
            0.97,
            0.90,
            0.84,
        ]
    )


def test_high_risk_queue_ignores_customers_without_predictions(
    db_session: Session,
) -> None:
    create_customer(
        db_session,
        customer_id="NO-PREDICTION-001",
    )

    high_risk_customer = create_customer(
        db_session,
        customer_id="HIGH-RISK-002",
    )

    create_prediction(
        db_session,
        customer_id=high_risk_customer.id,
        churn_probability=0.93,
        retention_action_required=True,
        risk_level="critical",
    )

    service = create_service(db_session)

    result = service.get_high_risk_customers()

    assert result.count == 1
    assert len(result.customers) == 1
    assert result.customers[0].customer_id == "HIGH-RISK-002"


def test_high_risk_queue_respects_limit_and_offset(
    db_session: Session,
) -> None:
    probabilities = [
        0.99,
        0.95,
        0.91,
    ]

    for index, probability in enumerate(probabilities):
        customer = create_customer(
            db_session,
            customer_id=f"HIGH-RISK-PAGE-{index}",
        )

        create_prediction(
            db_session,
            customer_id=customer.id,
            churn_probability=probability,
            retention_action_required=True,
            risk_level="critical",
        )

    service = create_service(db_session)

    result = service.get_high_risk_customers(
        limit=1,
        offset=1,
    )

    assert result.count == 1
    assert result.limit == 1
    assert result.offset == 1
    assert len(result.customers) == 1

    customer = result.customers[0]

    assert customer.customer_id == "HIGH-RISK-PAGE-1"
    assert customer.churn_probability == pytest.approx(0.95)
