from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return a secure Argon2 hash for a plaintext password."""

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Return whether a plaintext password matches its stored hash."""

    return password_hash.verify(
        plain_password,
        hashed_password,
    )
