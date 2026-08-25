from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import RetentionAction


class RetentionActionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        prediction_id: int,
        action_type: str,
        description: str,
        estimated_cost: float | None = None,
    ) -> RetentionAction:
        action = RetentionAction(
            prediction_id=prediction_id,
            action_type=action_type,
            description=description,
            estimated_cost=estimated_cost,
        )

        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)

        return action

    def get_by_id(
        self,
        action_id: int,
    ) -> RetentionAction | None:
        return self.db.get(RetentionAction, action_id)

    def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
    ) -> list[RetentionAction]:
        statement = select(RetentionAction)

        if status is not None:
            statement = statement.where(
                RetentionAction.status == status
            )

        statement = statement.order_by(
            RetentionAction.created_at.desc()
        ).limit(limit).offset(offset)

        return list(self.db.scalars(statement).all())

    def get_by_prediction(
        self,
        prediction_id: int,
    ) -> list[RetentionAction]:
        statement = (
            select(RetentionAction)
            .where(
                RetentionAction.prediction_id == prediction_id
            )
            .order_by(RetentionAction.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def update_status(
        self,
        action: RetentionAction,
        status: str,
        outcome: str | None = None,
    ) -> RetentionAction:
        action.status = status
        action.outcome = outcome

        if status == "completed":
            action.completed_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(action)

        return action