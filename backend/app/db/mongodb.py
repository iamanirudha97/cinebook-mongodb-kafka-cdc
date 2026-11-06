from pymongo import MongoClient
from pymongo.database import Database

from backend.app.core.config import get_settings
from backend.app.core.logging import get_logger

logger = get_logger(__name__)


class MongoDB:
    def __init__(self) -> None:
        self.client: MongoClient | None = None
        self.database: Database | None = None

    
    def connect(self) -> None:
        settings = get_settings()

        logger.info("Connecting to MongoDB Atlas")

        client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
        )

        try:
            client.admin.command("ping")
        except Exception:
            client.close()
            logger.exception("MongoDB connection failed")
            raise

        self.client = client
        self.database = client[settings.mongodb_db]

        logger.info(
            "MongoDB connection established | database=%s",
            settings.mongodb_db,
        )


    def disconnect(self) -> None:
        if self.client is not None:
            self.client.close()
            logger.info("MongoDB connection closed")

        self.client = None
        self.database = None


    def get_database(self) -> Database:
        if self.database is None:
            raise RuntimeError("MongoDB connection is not initialized")

        return self.database


mongodb = MongoDB()