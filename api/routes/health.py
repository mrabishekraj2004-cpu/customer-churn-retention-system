from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the liveness status of the API."""

    return {
        "status": "ok",
        "service": "customer-churn-api",
    }


@router.get(
    "/ready",
    response_model=None,
)
def readiness_check(
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str] | JSONResponse:
    """Check whether the API and database are ready to serve requests."""

    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "service": "customer-churn-api",
                "database": "unavailable",
            },
        )

    return {
        "status": "ready",
        "service": "customer-churn-api",
        "database": "available",
    }
