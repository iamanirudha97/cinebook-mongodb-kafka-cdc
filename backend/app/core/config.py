import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True, slots=True)
class Settings:
    mongodb_uri: str
    mongodb_db: str
    log_level: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db = os.getenv("MONGODB_DB", "cinebook")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    if not mongodb_uri:
        raise ValueError("MONGODB_URI is required")

    if not mongodb_db:
        raise ValueError("MONGODB_DB cannot be empty")

    return Settings(
        mongodb_uri=mongodb_uri,
        mongodb_db=mongodb_db,
        log_level=log_level,
    )
