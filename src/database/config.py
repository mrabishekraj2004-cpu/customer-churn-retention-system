import os

DEFAULT_DATABASE_URL = "sqlite:///./customer_churn.db"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_DATABASE_URL,
)
