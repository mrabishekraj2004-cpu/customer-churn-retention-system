import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
DATABASE_FILE = PROJECT_ROOT / "customer_churn.db"

load_dotenv(ENV_FILE)

DEFAULT_DATABASE_URL = f"sqlite:///{DATABASE_FILE.as_posix()}"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_DATABASE_URL,
)
