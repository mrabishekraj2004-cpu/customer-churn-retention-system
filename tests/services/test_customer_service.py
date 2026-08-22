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

    predictions = PredictionRepository(db_session)

    predictions.create(
        customer_id=customer.id,
        churn_probability=0.45,
        risk_level="medium",
        retention_action_required=False,
        operating_threshold=0.80,
        model_version="1.0.0",
    )

    latest_prediction = predictions.create(
        customer_id=customer.id,
        churn_probability=0.91,
        risk_level="critical",
        retention_action_required=True,
        operating_threshold=0.80,
        model_version="1.0.0",
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

    predictions = PredictionRepository(db_session)

    prediction = predictions.create(
        customer_id=first_customer.id,
        churn_probability=0.88,
        risk_level="critical",
        retention_action_required=True,
        operating_threshold=0.80,
        model_version="1.0.0",
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
