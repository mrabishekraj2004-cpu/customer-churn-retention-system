from sqlalchemy import inspect

from src.database.initialization import (
    database_schema_is_ready,
    get_missing_tables,
    initialize_database,
)
from src.database.session import Base, engine


def test_initialize_database_creates_required_tables() -> None:
    Base.metadata.drop_all(bind=engine)

    initialize_database()

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    assert set(Base.metadata.tables.keys()).issubset(existing_tables)


def test_get_missing_tables_returns_empty_after_initialization() -> None:
    Base.metadata.drop_all(bind=engine)

    initialize_database()

    assert get_missing_tables() == []


def test_database_schema_is_ready_after_initialization() -> None:
    Base.metadata.drop_all(bind=engine)

    initialize_database()

    assert database_schema_is_ready() is True
