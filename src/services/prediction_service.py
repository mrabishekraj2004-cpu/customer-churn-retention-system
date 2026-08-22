from typing import Any

from sqlalchemy.orm import Session

from src.database.repositories import (
    CustomerRepository,
    PredictionRepository,
    RetentionActionRepository,
)
from src.models.predict import PredictionService
from src.retention.engine import RetentionEngine
from src.services.customer_mapper import (
    to_database_customer,
    to_model_features,
)


class CustomerPredictionService:
    """Coordinate customer persistence, prediction, and retention actions."""

    def __init__(
        self,
        db: Session,
        predictor: PredictionService,
    ) -> None:
        self.customers = CustomerRepository(db)
        self.predictions = PredictionRepository(db)
        self.retention_actions = RetentionActionRepository(db)
        self.predictor = predictor
        self.retention_engine = RetentionEngine()

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

        recommendation = self.retention_engine.recommend(
            customer=model_features,
            churn_probability=result["churn_probability"],
            operating_threshold=result["operating_threshold"],
        )

        retention_action_id: int | None = None

        if recommendation["retention_action_required"]:
            description = (
                f"{recommendation['reason']} "
                f"Suggested offer: {recommendation['suggested_offer']}"
            )

            retention_action = self.retention_actions.create(
                prediction_id=prediction.id,
                action_type=recommendation["action_type"],
                description=description,
            )

            retention_action_id = retention_action.id

        return {
            **result,
            "prediction_id": prediction.id,
            "customer_id": customer.customer_id,
            "retention_recommendation": {
                "action_id": retention_action_id,
                "risk_factors": recommendation["risk_factors"],
                "action_type": recommendation["action_type"],
                "suggested_offer": recommendation["suggested_offer"],
                "priority": recommendation["priority"],
                "reason": recommendation["reason"],
            },
        }
