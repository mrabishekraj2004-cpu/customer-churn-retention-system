from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from src.database.models import User, UserRole
from src.security.authentication import get_current_user


def require_roles(
    *allowed_roles: UserRole,
) -> Callable[..., User]:
    """Require the authenticated user to have an allowed database role."""

    allowed_role_values = {
        role.value
        for role in allowed_roles
    }

    def authorize(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
    ) -> User:
        if current_user.role not in allowed_role_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

        return current_user

    return authorize
