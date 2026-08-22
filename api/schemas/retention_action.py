from datetime import datetime
from typing import Literal

from pydantic import BaseModel

RetentionStatus = Literal[
    "recommended",
    "in_progress",
    "completed",
]

RetentionOutcome = Literal[
    "retained",
    "churned",
    "unknown",
]


class RetentionActionResponse(BaseModel):
    id: int
    prediction_id: int
    action_type: str
    description: str
    status: RetentionStatus
    outcome: str | None
    estimated_cost: float | None
    created_at: datetime
    completed_at: datetime | None


class RetentionActionStatusUpdate(BaseModel):
    status: RetentionStatus
    outcome: RetentionOutcome | None = None
