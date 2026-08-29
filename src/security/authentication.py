from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.models import User
from src.database.repositories import UserRepository
from src.database.session import get_db
from src.security.tokens import (
    TokenConfigurationError,
    TokenDecodeError,
    decode_access_token,
)

bearer_scheme = HTTPBearer(
    auto_error=False,
)


def _authentication_error() -> HTTPException:
    """Return the standard unauthorized response."""

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> User:
    """Return the active user represented by a bearer token."""

    if credentials is None:
        raise _authentication_error()

    if credentials.scheme.lower() != "bearer":
        raise _authentication_error()

    try:
        payload = decode_access_token(
            credentials.credentials
        )
    except TokenDecodeError as exc:
        raise _authentication_error() from exc
    except TokenConfigurationError:
        raise

    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise _authentication_error()

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise _authentication_error() from exc

    if user_id <= 0:
        raise _authentication_error()

    repository = UserRepository(db)

    user = repository.get_by_id(user_id)

    if user is None:
        raise _authentication_error()

    if not user.is_active:
        raise _authentication_error()

    return user
