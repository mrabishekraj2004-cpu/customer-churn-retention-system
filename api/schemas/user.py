from typing import Literal

from pydantic import BaseModel

UserRoleValue = Literal[
    "admin",
    "analyst",
    "retention_agent",
]


class CurrentUserResponse(BaseModel):
    id: int
    email: str
    role: UserRoleValue
    is_active: bool
