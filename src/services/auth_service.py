from src.config import settings
from src.database.models import User
from src.database.repositories import UserRepository
from src.security.password import hash_password, verify_password
from src.security.tokens import create_access_token

DUMMY_PASSWORD_HASH = hash_password(
    "dummy-password-used-only-for-timing-equalization"
)


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

        password_hash = (
            user.password_hash
            if user is not None
            else DUMMY_PASSWORD_HASH
        )

        password_is_valid = verify_password(
            password,
            password_hash,
        )

        if user is None or not password_is_valid:
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
