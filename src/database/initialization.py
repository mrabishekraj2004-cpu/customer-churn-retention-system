import logging

from sqlalchemy import inspect

from src.database import models  # noqa: F401
from src.database.session import Base, engine

logger = logging.getLogger(__name__)


def initialize_database() -> None:
    """Create any missing application database tables."""

    Base.metadata.create_all(bind=engine)

    table_names = sorted(Base.metadata.tables.keys())

    logger.info(
        "Database schema initialized. tables=%s",
        table_names,
    )


def get_missing_tables() -> list[str]:
    """Return application tables that are missing from the database."""

    inspector = inspect(engine)

    existing_tables = set(inspector.get_table_names())
    required_tables = set(Base.metadata.tables.keys())

    return sorted(required_tables - existing_tables)


def database_schema_is_ready() -> bool:
    """Return whether all required application tables exist."""

    return not get_missing_tables()
