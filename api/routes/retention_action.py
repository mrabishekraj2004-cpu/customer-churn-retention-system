from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.schemas.retention_action import (
    RetentionActionListResponse,
    RetentionActionResponse,
    RetentionActionStatusUpdate,
    RetentionStatus,
)
from src.database.repositories import RetentionActionRepository
from src.database.session import get_db
from src.services.retention_action_service import (
    InvalidRetentionActionUpdateError,
    RetentionActionNotFoundError,
    RetentionActionService,
)

router = APIRouter(
    prefix="/api/v1/retention-actions",
    tags=["retention-actions"],
)


def get_retention_action_service(
    db: Annotated[Session, Depends(get_db)],
) -> RetentionActionService:
    repository = RetentionActionRepository(db)

    return RetentionActionService(repository)


@router.get(
    "",
    response_model=RetentionActionListResponse,
)
def get_retention_actions(
    service: Annotated[
        RetentionActionService,
        Depends(get_retention_action_service),
    ],
    limit: Annotated[
        int,
        Query(ge=1, le=500),
    ] = 100,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
    status_filter: Annotated[
        RetentionStatus | None,
        Query(alias="status"),
    ] = None,
) -> RetentionActionListResponse:
    actions = service.get_actions(
        limit=limit,
        offset=offset,
        status=status_filter,
    )

    action_responses = [
        RetentionActionResponse.model_validate(
            action,
            from_attributes=True,
        )
        for action in actions
    ]

    return RetentionActionListResponse(
        actions=action_responses,
        count=len(action_responses),
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{action_id}",
    response_model=RetentionActionResponse,
)
def get_retention_action(
    action_id: int,
    service: Annotated[
        RetentionActionService,
        Depends(get_retention_action_service),
    ],
) -> RetentionActionResponse:
    try:
        action = service.get_action(action_id)
    except RetentionActionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return RetentionActionResponse.model_validate(
        action,
        from_attributes=True,
    )


@router.patch(
    "/{action_id}",
    response_model=RetentionActionResponse,
)
def update_retention_action(
    action_id: int,
    payload: RetentionActionStatusUpdate,
    service: Annotated[
        RetentionActionService,
        Depends(get_retention_action_service),
    ],
) -> RetentionActionResponse:
    try:
        action = service.update_action(
            action_id=action_id,
            status=payload.status,
            outcome=payload.outcome,
        )
    except RetentionActionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidRetentionActionUpdateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return RetentionActionResponse.model_validate(
        action,
        from_attributes=True,
    )
