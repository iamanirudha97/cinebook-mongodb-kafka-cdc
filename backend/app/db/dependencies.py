from typing import Any, Annotated

from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from backend.app.db.mongodb import mongodb
from backend.app.repositories.movie_repository import MovieRepository
from backend.app.services.movie_service import MovieService

from backend.app.repositories.show_repository import ShowRepository
from backend.app.services.show_service import ShowService


def get_database() -> AsyncDatabase[dict[str, Any]]:
    return mongodb.get_database()


def get_movie_repository(
    database: Annotated[
        AsyncDatabase[dict[str, Any]],
        Depends(get_database),
    ],
) -> MovieRepository:
    return MovieRepository(database)


def get_movie_service(
    repository: Annotated[
        MovieRepository,
        Depends(get_movie_repository),
    ],
) -> MovieService:
    return MovieService(repository)



def get_show_repository(
    database: Annotated[
        AsyncDatabase[dict[str, Any]],
        Depends(get_database),
    ],
) -> ShowRepository:
    return ShowRepository(database)


def get_show_service(
    repository: Annotated[
        ShowRepository,
        Depends(get_show_repository),
    ],
) -> ShowService:
    return ShowService(repository)
