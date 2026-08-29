import pytest
from sqlalchemy.orm import Session

from src.database.models import UserRole
from src.database.repositories import UserRepository
from src.security.password import hash_password
from src.security.tokens import decode_access_token
from src.services.auth_service import (
    AuthenticationService,
    InvalidCredentialsError,
)

TEST_PASSWORD = "Strong-Test-Password-123!"


def create_user(
    db_session: Session,
    *,
    email: str = "admin@example.com",
    role: UserRole = UserRole.ADMIN,
):
    repository = UserRepository(db_session)

    return repository.create(
        email=email,
        password_hash=hash_password(
            TEST_PASSWORD
        ),
        role=role,
    )


def test_authenticate_valid_user(
    db_session: Session,
) -> None:
    user = create_user(db_session)

    service = AuthenticationService(
        UserRepository(db_session)
    )

    authenticated = service.authenticate(
        email="admin@example.com",
        password=TEST_PASSWORD,
    )

    assert authenticated.id == user.id


def test_authenticate_normalizes_email(
    db_session: Session,
) -> None:
    user = create_user(db_session)

    service = AuthenticationService(
        UserRepository(db_session)
    )

    authenticated = service.authenticate(
        email="  ADMIN@EXAMPLE.COM  ",
        password=TEST_PASSWORD,
    )

    assert authenticated.id == user.id


def test_authenticate_rejects_wrong_password(
    db_session: Session,
) -> None:
    create_user(db_session)

    service = AuthenticationService(
        UserRepository(db_session)
    )

    with pytest.raises(
        InvalidCredentialsError,
        match="Invalid email or password",
    ):
        service.authenticate(
            email="admin@example.com",
            password="Wrong-Password!",
        )


def test_authenticate_rejects_missing_user(
    db_session: Session,
) -> None:
    service = AuthenticationService(
        UserRepository(db_session)
    )

    with pytest.raises(
        InvalidCredentialsError,
        match="Invalid email or password",
    ):
        service.authenticate(
            email="missing@example.com",
            password=TEST_PASSWORD,
        )


def test_authenticate_rejects_disabled_user(
    db_session: Session,
) -> None:
    repository = UserRepository(db_session)

    user = create_user(db_session)

    repository.set_active(
        user,
        is_active=False,
    )

    service = AuthenticationService(repository)

    with pytest.raises(
        InvalidCredentialsError,
        match="Invalid email or password",
    ):
        service.authenticate(
            email="admin@example.com",
            password=TEST_PASSWORD,
        )


def test_create_token_contains_user_identity(
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        role=UserRole.ANALYST,
    )

    service = AuthenticationService(
        UserRepository(db_session)
    )

    token = service.create_token(user)
    payload = decode_access_token(token)

    assert payload["sub"] == str(user.id)
    assert payload["role"] == UserRole.ANALYST.value


def test_access_token_expiration_is_seconds(
    db_session: Session,
) -> None:
    service = AuthenticationService(
        UserRepository(db_session)
    )

    assert service.access_token_expires_in() > 0


def test_authenticate_missing_user_still_verifies_password(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = AuthenticationService(
        UserRepository(db_session)
    )

    verification_calls: list[
        tuple[str, str]
    ] = []

    def fake_verify_password(
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        verification_calls.append(
            (
                plain_password,
                hashed_password,
            )
        )
        return False

    monkeypatch.setattr(
        "src.services.auth_service.verify_password",
        fake_verify_password,
    )

    with pytest.raises(
        InvalidCredentialsError,
        match="Invalid email or password",
    ):
        service.authenticate(
            email="missing@example.com",
            password=TEST_PASSWORD,
        )

    assert len(verification_calls) == 1
    assert verification_calls[0][0] == TEST_PASSWORD


def test_authenticate_never_accepts_missing_user(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = AuthenticationService(
        UserRepository(db_session)
    )

    def fake_verify_password(
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        return True

    monkeypatch.setattr(
        "src.services.auth_service.verify_password",
        fake_verify_password,
    )

    with pytest.raises(
        InvalidCredentialsError,
        match="Invalid email or password",
    ):
        service.authenticate(
            email="missing@example.com",
            password=TEST_PASSWORD,
        )
