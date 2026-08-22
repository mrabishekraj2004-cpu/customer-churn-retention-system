from typing import Any

from sqlalchemy.orm import Session

from src.database.repositories import (
    CustomerRepository,
    PredictionRepository,
)
from src.models.predict import PredictionService
from src.services.customer_mapper import (
    to_database_customer,
    to_model_features,
)


class CustomerPredictionService:
    """Coordinate customer persistence and churn prediction."""

    def __init__(
        self,
        db: Session,
        predictor: PredictionService,
    ) -> None:
        self.customers = CustomerRepository(db)
        self.predictions = PredictionRepository(db)
        self.predictor = predictor

    def predict(
        self,
        customer_data: dict[str, Any],
    ) -> dict[str, Any]:
        customer_id = customer_data["customer_id"]

        database_data = to_database_customer(customer_data)
        model_features = to_model_features(customer_data)

        customer = self.customers.get_by_customer_id(customer_id)

        if customer is None:
            customer = self.customers.create(
                customer_id=customer_id,
                customer_data=database_data,
            )
        else:
            customer = self.customers.update(
                customer,
                database_data,
            )

        result = self.predictor.predict(model_features)

        prediction = self.predictions.create(
            customer_id=customer.id,
            churn_probability=result["churn_probability"],
            risk_level=result["risk_level"],
            retention_action_required=result["retention_action_required"],
            operating_threshold=result["operating_threshold"],
            model_version=result["model_version"],
        )

        return {
            **result,
            "prediction_id": prediction.id,
            "customer_id": customer.customer_id,
        }
