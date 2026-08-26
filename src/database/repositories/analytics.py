from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.database.models import Customer, Prediction, RetentionAction


class AnalyticsRepository:
    """Provide aggregate data used by analytics services."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_total_customers(self) -> int:
        statement = select(func.count(Customer.id))

        return self.db.scalar(statement) or 0

    def get_total_monthly_revenue(self) -> float:
        statement = select(
            func.coalesce(
                func.sum(Customer.monthly_charges),
                0.0,
            )
        )

        return float(self.db.scalar(statement) or 0.0)

    def get_latest_predictions(self) -> list[Prediction]:
        latest_prediction_ids = (
            select(func.max(Prediction.id)).group_by(Prediction.customer_id).subquery()
        )

        statement = (
            select(Prediction)
            .where(Prediction.id.in_(select(latest_prediction_ids.c[0])))
            .order_by(Prediction.id)
        )

        return list(self.db.scalars(statement).all())

    def get_total_retention_actions(self) -> int:
        statement = select(func.count(RetentionAction.id))

        return self.db.scalar(statement) or 0

    def get_retention_action_count_by_status(
        self,
        status: str,
    ) -> int:
        statement = select(func.count(RetentionAction.id)).where(
            RetentionAction.status == status
        )

        return self.db.scalar(statement) or 0

    def get_retention_action_count_by_outcome(
        self,
        outcome: str,
    ) -> int:
        statement = select(func.count(RetentionAction.id)).where(
            RetentionAction.outcome == outcome
        )

        return self.db.scalar(statement) or 0

    def get_total_estimated_cost(self) -> float:
        statement = select(
            func.coalesce(
                func.sum(RetentionAction.estimated_cost),
                0.0,
            )
        )

        return float(self.db.scalar(statement) or 0.0)

    def get_monthly_revenue_at_risk(self) -> float:
        latest_prediction_ids = (
            select(func.max(Prediction.id)).group_by(Prediction.customer_id).subquery()
        )

        statement = (
            select(
                func.coalesce(
                    func.sum(Customer.monthly_charges),
                    0.0,
                )
            )
            .select_from(Prediction)
            .join(
                Customer,
                Customer.id == Prediction.customer_id,
            )
            .where(
                Prediction.id.in_(select(latest_prediction_ids.c[0])),
                Prediction.retention_action_required.is_(True),
            )
        )

        return float(self.db.scalar(statement) or 0.0)

    def get_expected_monthly_revenue_loss(self) -> float:
        latest_prediction_ids = (
            select(func.max(Prediction.id)).group_by(Prediction.customer_id).subquery()
        )

        statement = (
            select(
                func.coalesce(
                    func.sum(Customer.monthly_charges * Prediction.churn_probability),
                    0.0,
                )
            )
            .select_from(Prediction)
            .join(
                Customer,
                Customer.id == Prediction.customer_id,
            )
            .where(Prediction.id.in_(select(latest_prediction_ids.c[0])))
        )

        return float(self.db.scalar(statement) or 0.0)

    def get_retained_customer_monthly_revenue(self) -> float:
        retained_customer_ids = (
            select(Prediction.customer_id)
            .join(
                RetentionAction,
                RetentionAction.prediction_id == Prediction.id,
            )
            .where(
                RetentionAction.status == "completed",
                RetentionAction.outcome == "retained",
            )
            .distinct()
            .subquery()
        )

        statement = select(
            func.coalesce(
                func.sum(Customer.monthly_charges),
                0.0,
            )
        ).where(Customer.id.in_(select(retained_customer_ids.c.customer_id)))

        return float(self.db.scalar(statement) or 0.0)
