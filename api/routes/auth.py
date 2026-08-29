from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.schemas.auth import LoginRequest, TokenResponse
from src.database.repositories import UserRepository
from src.database.session import get_db
from src.services.auth_service import (
    AuthenticationService,
    InvalidCredentialsError,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["authentication"],
)


def get_authentication_service(
    db: Annotated[Session, Depends(get_db)],
) -> AuthenticationService:
    return AuthenticationService(
        UserRepository(db)
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    credentials: LoginRequest,
    service: Annotated[
        AuthenticationService,
        Depends(get_authentication_service),
    ],
) -> TokenResponse:
    try:
        user = service.authenticate(
            email=credentials.email,
            password=credentials.password,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    access_token = service.create_token(user)

    return TokenResponse(
        access_token=access_token,
        expires_in=service.access_token_expires_in(),
    )
