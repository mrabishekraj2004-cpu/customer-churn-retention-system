from pathlib import Path

from src.config import (
    DEFAULT_DATABASE_URL,
    DEFAULT_MODEL_METADATA_PATH,
    DEFAULT_MODEL_PATH,
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

    assert settings.model_path == DEFAULT_MODEL_PATH
    assert settings.model_metadata_path == DEFAULT_MODEL_METADATA_PATH

    assert settings.cors_origins == ("http://localhost:3000,http://localhost:5173")

    assert settings.cors_origin_list == [
        "http://localhost:3000",
        "http://localhost:5173",
    ]


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

    monkeypatch.setenv(
        "MODEL_PATH",
        "models/custom_model.joblib",
    )

    monkeypatch.setenv(
        "MODEL_METADATA_PATH",
        "models/custom_metadata.json",
    )

    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://example.com,https://admin.example.com",
    )

    settings = Settings(_env_file=None)

    assert settings.database_url == "sqlite:///test_override.db"
    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"

    assert settings.model_path == Path("models/custom_model.joblib")

    assert settings.model_metadata_path == Path("models/custom_metadata.json")

    assert settings.cors_origins == ("https://example.com,https://admin.example.com")

    assert settings.cors_origin_list == [
        "https://example.com",
        "https://admin.example.com",
    ]


def test_cors_origin_list_removes_whitespace_and_empty_values() -> None:
    settings = Settings(
        _env_file=None,
        cors_origins=(" http://localhost:3000, http://localhost:5173, , "),
    )

    assert settings.cors_origin_list == [
        "http://localhost:3000",
        "http://localhost:5173",
    ]


def test_get_settings_is_cached() -> None:
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert first is second

    get_settings.cache_clear()
