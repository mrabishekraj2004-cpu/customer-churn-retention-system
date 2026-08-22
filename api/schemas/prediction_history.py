from datetime import datetime

from pydantic import BaseModel


class PredictionHistoryItem(BaseModel):
    prediction_id: int
    churn_probability: float
    risk_level: str
    retention_action_required: bool
    operating_threshold: float
    model_version: str
    created_at: datetime


class PredictionHistoryResponse(BaseModel):
    customer_id: str
    predictions: list[PredictionHistoryItem]
