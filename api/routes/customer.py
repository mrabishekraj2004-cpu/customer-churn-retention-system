from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.schemas.customer import (
    CustomerDetailResponse,
    CustomerListResponse,
    HighRiskCustomerListResponse,
)
from src.database.models import UserRole
from src.database.repositories import (
    CustomerRepository,
    PredictionRepository,
)
from src.database.session import get_db
from src.security.authorization import require_roles
from src.services.customer_service import (
    CustomerNotFoundError,
    CustomerService,
)

router = APIRouter(
    prefix="/api/v1/customers",
    tags=["customers"],
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


def get_customer_service(
    db: Annotated[Session, Depends(get_db)],
) -> CustomerService:
    return CustomerService(
        customer_repository=CustomerRepository(db),
        prediction_repository=PredictionRepository(db),
    )


@router.get(
    "",
    response_model=CustomerListResponse,
)
def get_customers(
    service: Annotated[
        CustomerService,
        Depends(get_customer_service),
    ],
    limit: Annotated[
        int,
        Query(ge=1, le=500),
    ] = 100,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
) -> CustomerListResponse:
    return service.get_customers(
        limit=limit,
        offset=offset,
    )


@router.get(
    "/high-risk",
    response_model=HighRiskCustomerListResponse,
)
def get_high_risk_customers(
    service: Annotated[
        CustomerService,
        Depends(get_customer_service),
    ],
    limit: Annotated[
        int,
        Query(ge=1, le=500),
    ] = 100,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
) -> HighRiskCustomerListResponse:
    return service.get_high_risk_customers(
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerDetailResponse,
)
def get_customer(
    customer_id: str,
    service: Annotated[
        CustomerService,
        Depends(get_customer_service),
    ],
) -> CustomerDetailResponse:
    try:
        return service.get_customer(customer_id)
    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
