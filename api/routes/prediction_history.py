from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.schemas.prediction_history import PredictionHistoryResponse
from src.database.session import get_db
from src.services.prediction_history_service import (
    CustomerNotFoundError,
    PredictionHistoryService,
)

router = APIRouter(
    prefix="/api/v1/customers",
    tags=["predictions"],
)


@router.get(
    "/{customer_id}/predictions",
    response_model=PredictionHistoryResponse,
)
def get_prediction_history(
    customer_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> PredictionHistoryResponse:
    service = PredictionHistoryService(db)

    try:
        result = service.get_customer_history(customer_id)
    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return PredictionHistoryResponse(**result)