from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas.prediction import (
    CustomerFeatures,
    PredictionResponse,
)
from src.database.session import get_db
from src.models.predict import PredictionService
from src.services.prediction_service import CustomerPredictionService

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
    db: Annotated[Session, Depends(get_db)],
) -> PredictionResponse:
    service = CustomerPredictionService(
        db=db,
        predictor=prediction_service,
    )

    result = service.predict(customer.model_dump())

    return PredictionResponse(**result)
