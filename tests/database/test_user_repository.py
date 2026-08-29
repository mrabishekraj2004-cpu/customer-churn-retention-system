from sqlalchemy.orm import Session

from src.database.models import UserRole
from src.database.repositories import UserRepository
from src.security.password import (
    hash_password,
    verify_password,
)


def test_create_and_find_user(
    db_session: Session,
) -> None:
    repository = UserRepository(db_session)

    password = "Strong-Test-Password-123!"
    password_hash = hash_password(password)

    created = repository.create(
        email="admin@example.com",
        password_hash=password_hash,
        role=UserRole.ADMIN,
    )

    found = repository.get_by_email(
        "admin@example.com"
    )

    assert created.id is not None
    assert found is not None
    assert found.id == created.id
    assert found.email == "admin@example.com"
    assert found.role == UserRole.ADMIN.value
    assert found.is_active is True

    assert found.password_hash != password
    assert verify_password(
        password,
        found.password_hash,
    )


def test_email_is_normalized(
    db_session: Session,
) -> None:
    repository = UserRepository(db_session)

    repository.create(
        email="  Analyst@Example.COM  ",
        password_hash=hash_password(
            "Strong-Test-Password-123!"
        ),
        role=UserRole.ANALYST,
    )

    found = repository.get_by_email(
        "ANALYST@example.com"
    )

    assert found is not None
    assert found.email == "analyst@example.com"


def test_get_user_by_id(
    db_session: Session,
) -> None:
    repository = UserRepository(db_session)

    created = repository.create(
        email="agent@example.com",
        password_hash=hash_password(
            "Strong-Test-Password-123!"
        ),
        role=UserRole.RETENTION_AGENT,
    )

    found = repository.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.role == UserRole.RETENTION_AGENT.value


def test_get_missing_user_returns_none(
    db_session: Session,
) -> None:
    repository = UserRepository(db_session)

    assert repository.get_by_email(
        "missing@example.com"
    ) is None

    assert repository.get_by_id(999999) is None


def test_user_can_be_disabled(
    db_session: Session,
) -> None:
    repository = UserRepository(db_session)

    user = repository.create(
        email="disabled@example.com",
        password_hash=hash_password(
            "Strong-Test-Password-123!"
        ),
        role=UserRole.ANALYST,
    )

    updated = repository.set_active(
        user,
        is_active=False,
    )

    assert updated.is_active is False

    found = repository.get_by_email(
        "disabled@example.com"
    )

    assert found is not None
    assert found.is_active is False


def test_supported_user_roles() -> None:
    assert UserRole.ADMIN.value == "admin"
    assert UserRole.ANALYST.value == "analyst"
    assert (
        UserRole.RETENTION_AGENT.value
        == "retention_agent"
    )
