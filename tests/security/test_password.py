from src.security.password import (
    hash_password,
    verify_password,
)


def test_hash_password_uses_argon2() -> None:
    password = "Strong-Test-Password-123!"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2")


def test_verify_password_accepts_correct_password() -> None:
    password = "Strong-Test-Password-123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_rejects_wrong_password() -> None:
    hashed = hash_password(
        "Strong-Test-Password-123!"
    )

    assert (
        verify_password(
            "Incorrect-Password-456!",
            hashed,
        )
        is False
    )
