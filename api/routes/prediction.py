from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas.prediction import (
    CustomerFeatures,
    PredictionResponse,
)
from src.database.models import UserRole
from src.database.session import get_db
from src.models.predict import PredictionService
from src.security.authorization import require_roles
from src.services.prediction_service import CustomerPredictionService

router = APIRouter(
    prefix="/api/v1",
    tags=["predictions"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.ANALYST,
                UserRole.RETENTION_AGENT,
            )
        )
    ],
)


def get_prediction_service() -> PredictionService:
    return PredictionService()


@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict_churn(
    customer: CustomerFeatures,
    db: Annotated[Session, Depends(get_db)],
    predictor: Annotated[
        PredictionService,
        Depends(get_prediction_service),
    ],
) -> PredictionResponse:
    service = CustomerPredictionService(
        db=db,
        predictor=predictor,
    )

    result = service.predict(customer.model_dump())

    return PredictionResponse(**result)
