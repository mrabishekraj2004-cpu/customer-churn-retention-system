import logging

from src.logging_config import LOG_FORMAT, configure_logging


def test_log_format_contains_required_fields() -> None:
    assert "%(asctime)s" in LOG_FORMAT
    assert "%(levelname)s" in LOG_FORMAT
    assert "%(name)s" in LOG_FORMAT
    assert "%(message)s" in LOG_FORMAT


def test_configure_logging_sets_root_log_level() -> None:
    configure_logging()

    root_logger = logging.getLogger()

    assert root_logger.level == logging.INFO
