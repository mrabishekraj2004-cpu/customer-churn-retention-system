from src.database import models  # noqa: F401
from src.database.session import Base, engine


def init_database() -> None:
    """Create database tables for local development."""
    Base.metadata.create_all(bind=engine)

    table_names = sorted(Base.metadata.tables.keys())

    print("Database initialized successfully.")
    print(f"Tables: {table_names}")


if __name__ == "__main__":
    init_database()