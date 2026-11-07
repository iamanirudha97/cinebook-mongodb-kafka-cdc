from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from backend.app.core.logging import configure_logging, get_logger
from backend.app.db.mongodb import mongodb

from fastapi import FastAPI, HTTPException
from pymongo.errors import PyMongoError

from backend.app.api.movies import router as movies_router
from backend.app.api.shows import router as shows_router
from backend.app.api.bookings import router as bookings_router

from backend.app.api.users import router as users_router

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting CineBook API")

    await mongodb.connect()

    try:
        logger.info("CineBook API startup complete")
        yield
    finally:
        logger.info("Shutting down CineBook API")
        await mongodb.disconnect()
        logger.info("CineBook API shutdown complete")


app = FastAPI(
    title="CineBook API",
    description="Movie booking system powered by MongoDB Atlas",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(movies_router)
app.include_router(shows_router)
app.include_router(bookings_router)
app.include_router(users_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to CineBook API"}


@app.get("/healthz")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/readyz")
async def readiness_check() -> dict[str, str]:
    try:
        database = mongodb.get_database()
        await database.command("ping")

    except (PyMongoError, RuntimeError) as exc:
        logger.warning("MongoDB readiness check failed")
        raise HTTPException(
            status_code=503,
            detail="MongoDB is unavailable",
        ) from exc

    return {"status": "ready", "database": "connected"}