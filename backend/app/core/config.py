
import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str
    mongodb_db: str


def get_settings() -> Settings:
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db = os.getenv("MONGODB_DB", "cinebook")

    if not mongodb_uri:
        raise ValueError("MONGODB_URI is missing from the environment")

    return Settings(
        mongodb_uri=mongodb_uri,
        mongodb_db=mongodb_db,
    )
