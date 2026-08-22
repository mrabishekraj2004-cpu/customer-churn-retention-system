from sqlalchemy.orm import Session

from src.database.repositories import CustomerRepository


def customer_data() -> dict:
    return {
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
    }


def test_create_and_find_customer(
    db_session: Session,
) -> None:
    repository = CustomerRepository(db_session)

    created = repository.create(
        customer_id="TEST-0001",
        customer_data=customer_data(),
    )

    found = repository.get_by_customer_id("TEST-0001")

    assert created.id is not None
    assert found is not None
    assert found.id == created.id
    assert found.customer_id == "TEST-0001"
    assert found.contract == "Month-to-month"


def test_update_customer(
    db_session: Session,
) -> None:
    repository = CustomerRepository(db_session)

    customer = repository.create(
        customer_id="TEST-0002",
        customer_data=customer_data(),
    )

    updated = repository.update(
        customer,
        {
            "tenure": 12,
            "contract": "One year",
        },
    )

    assert updated.tenure == 12
    assert updated.contract == "One year"
