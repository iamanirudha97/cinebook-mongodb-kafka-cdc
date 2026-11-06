
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pymongo.errors import PyMongoError

from backend.app.core.logging import (
    configure_logging,
    get_logger,
)
from backend.app.db.mongodb import mongodb


configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting CineBook API")

    await run_in_threadpool(mongodb.connect)

    try:
        logger.info("CineBook API startup complete")
        yield
    finally:
        logger.info("Shutting down CineBook API")
        await run_in_threadpool(mongodb.disconnect)
        logger.info("CineBook API shutdown complete")


app = FastAPI(
    title="CineBook API",
    description="Movie booking system powered by MongoDB Atlas and Kafka",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to CineBook API"}


@app.get("/healthz")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/readyz")
def readiness_check() -> dict[str, str]:
    try:
        database = mongodb.get_database()
        database.command("ping")
    except (PyMongoError, RuntimeError) as exc:
        logger.warning("MongoDB readiness check failed")
        raise HTTPException(
            status_code=503,
            detail="MongoDB is unavailable",
        ) from exc

    return {"status": "ready", "database": "connected"}
