from typing import Annotated

from fastapi import APIRouter, Depends

from api.schemas.user import CurrentUserResponse
from src.database.models import User
from src.security.authentication import get_current_user

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
)


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> CurrentUserResponse:
    return CurrentUserResponse.model_validate(
        current_user,
        from_attributes=True,
    )
