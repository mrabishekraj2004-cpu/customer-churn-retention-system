from src.config import Settings


def test_security_configuration_defaults() -> None:
    settings = Settings(
        _env_file=None,
    )

    assert settings.jwt_secret_key == ""
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 15


def test_security_configuration_can_be_overridden() -> None:
    settings = Settings(
        _env_file=None,
        jwt_secret_key="test-secret-key-that-is-at-least-32-bytes",
        jwt_algorithm="HS256",
        access_token_expire_minutes=30,
    )

    assert len(settings.jwt_secret_key) >= 32
    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_expire_minutes == 30
