from typing import Any

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from backend.app.core.config import get_settings
from backend.app.core.logging import get_logger


logger = get_logger(__name__)


class MongoDB:
    def __init__(self) -> None:
        self.client: AsyncMongoClient[dict[str, Any]] | None = None
        self.database: AsyncDatabase[dict[str, Any]] | None = None

    async def connect(self) -> None:
        settings = get_settings()

        logger.info("Connecting to MongoDB Atlas")

        client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
        )

        try:
            await client.admin.command("ping")
        except Exception:
            await client.close()
            logger.exception("MongoDB connection failed")
            raise

        self.client = client
        self.database = client[settings.mongodb_db]

        logger.info(
            "MongoDB connection established | database=%s",
            settings.mongodb_db,
        )

    async def disconnect(self) -> None:
        if self.client is not None:
            await self.client.close()
            logger.info("MongoDB connection closed")

        self.client = None
        self.database = None

    def get_database(self) -> AsyncDatabase[dict[str, Any]]:
        if self.database is None:
            raise RuntimeError("MongoDB connection is not initialized")

        return self.database


mongodb = MongoDB()