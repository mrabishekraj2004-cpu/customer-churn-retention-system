from typing import Any

from sqlalchemy.orm import Session

from src.database.repositories import (
    CustomerRepository,
    PredictionRepository,
)


class CustomerNotFoundError(Exception):
    """Raised when a requested customer does not exist."""


class PredictionHistoryService:
    """Retrieve stored churn prediction history for customers."""

    def __init__(self, db: Session) -> None:
        self.customers = CustomerRepository(db)
        self.predictions = PredictionRepository(db)

    def get_customer_history(
        self,
        customer_id: str,
    ) -> dict[str, Any]:
        customer = self.customers.get_by_customer_id(customer_id)

        if customer is None:
            raise CustomerNotFoundError(f"Customer not found: {customer_id}")

        predictions = self.predictions.get_customer_history(customer.id)

        history = [
            {
                "prediction_id": prediction.id,
                "churn_probability": prediction.churn_probability,
                "risk_level": prediction.risk_level,
                "retention_action_required": (prediction.retention_action_required),
                "operating_threshold": prediction.operating_threshold,
                "model_version": prediction.model_version,
                "created_at": prediction.created_at,
            }
            for prediction in predictions
        ]

        return {
            "customer_id": customer.customer_id,
            "predictions": history,
        }
