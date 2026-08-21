from fastapi import APIRouter

from api.schemas.prediction import (
    CustomerFeatures,
    PredictionResponse,
)
from src.models.predict import PredictionService

router = APIRouter(
    prefix="/api/v1",
    tags=["predictions"],
)

prediction_service = PredictionService()


@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict_churn(
    customer: CustomerFeatures,
) -> PredictionResponse:
    result = prediction_service.predict(customer.model_dump())

    return PredictionResponse(**result)
