from sqlalchemy.orm import Session

from src.database.repositories import (
    CustomerRepository,
    PredictionRepository,
)
from tests.database.test_customer_repository import customer_data


def test_create_prediction_and_history(
    db_session: Session,
) -> None:
    customers = CustomerRepository(db_session)
    predictions = PredictionRepository(db_session)

    customer = customers.create(
        customer_id="PRED-0001",
        customer_data=customer_data(),
    )

    prediction = predictions.create(
        customer_id=customer.id,
        churn_probability=0.8932,
        risk_level="critical",
        retention_action_required=True,
        operating_threshold=0.8,
        model_version="1.0.0",
    )

    history = predictions.get_customer_history(customer.id)

    assert prediction.id is not None
    assert len(history) == 1
    assert history[0].id == prediction.id
    assert history[0].churn_probability == 0.8932
    assert history[0].risk_level == "critical"
