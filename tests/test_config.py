from src.config import (
    DEFAULT_DATABASE_URL,
    ENV_FILE,
    PROJECT_ROOT,
    Settings,
    get_settings,
)


def test_project_root_exists() -> None:
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()


def test_env_file_is_in_project_root() -> None:
    assert ENV_FILE == PROJECT_ROOT / ".env"


def test_default_settings() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "Customer Churn Prediction API"
    assert settings.app_version == "1.0.0"
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.database_url == DEFAULT_DATABASE_URL


def test_settings_can_be_overridden_by_environment(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///test_override.db",
    )
    monkeypatch.setenv(
        "ENVIRONMENT",
        "test",
    )
    monkeypatch.setenv(
        "LOG_LEVEL",
        "DEBUG",
    )

    settings = Settings(_env_file=None)

    assert settings.database_url == "sqlite:///test_override.db"
    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"


def test_get_settings_is_cached() -> None:
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert first is second

    get_settings.cache_clear()
