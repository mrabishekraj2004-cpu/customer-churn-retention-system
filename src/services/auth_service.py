from src.config import settings
from src.database.models import User
from src.database.repositories import UserRepository
from src.security.password import verify_password
from src.security.tokens import create_access_token


class InvalidCredentialsError(Exception):
    """Raised when supplied authentication credentials are invalid."""


class AuthenticationService:
    """Authenticate application users and issue access tokens."""

    def __init__(
        self,
        repository: UserRepository,
    ) -> None:
        self.repository = repository

    def authenticate(
        self,
        *,
        email: str,
        password: str,
    ) -> User:
        user = self.repository.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        return user

    def create_token(
        self,
        user: User,
    ) -> str:
        return create_access_token(
            subject=str(user.id),
            role=user.role,
        )

    def access_token_expires_in(self) -> int:
        return settings.access_token_expire_minutes * 60
