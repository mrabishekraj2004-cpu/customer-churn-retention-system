from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import Prediction


class PredictionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        customer_id: int,
        churn_probability: float,
        risk_level: str,
        retention_action_required: bool,
        operating_threshold: float,
        model_version: str,
    ) -> Prediction:
        prediction = Prediction(
            customer_id=customer_id,
            churn_probability=churn_probability,
            risk_level=risk_level,
            retention_action_required=retention_action_required,
            operating_threshold=operating_threshold,
            model_version=model_version,
        )

        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)

        return prediction

    def get_customer_history(
        self,
        customer_id: int,
    ) -> list[Prediction]:
        statement = (
            select(Prediction)
            .where(Prediction.customer_id == customer_id)
            .order_by(Prediction.created_at.desc())
        )

        return list(self.db.scalars(statement).all())
