from typing import Any, Annotated

from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from backend.app.db.mongodb import mongodb
from backend.app.repositories.movie_repository import MovieRepository
from backend.app.services.movie_service import MovieService

from backend.app.repositories.show_repository import ShowRepository
from backend.app.services.show_service import ShowService

from backend.app.repositories.booking_repository import BookingRepository
from backend.app.services.booking_service import BookingService

from backend.app.repositories.user_repository import UserRepository
from backend.app.services.user_service import UserService


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


def get_booking_repository(
    database: Annotated[AsyncDatabase[dict[str, Any]], Depends(get_database)],
) -> BookingRepository:
    return BookingRepository(database)


def get_booking_service(
    repository: Annotated[
        BookingRepository, Depends(get_booking_repository)
    ],
) -> BookingService:
    return BookingService(repository)

def get_user_repository(
    database: Annotated[
        AsyncDatabase[dict[str, Any]],
        Depends(get_database),
    ],
) -> UserRepository:
    return UserRepository(database)


def get_user_service(
    user_repository: Annotated[
        UserRepository,
        Depends(get_user_repository),
    ],
    booking_repository: Annotated[
        BookingRepository,
        Depends(get_booking_repository),
    ],
) -> UserService:
    return UserService(
        user_repository=user_repository,
        booking_repository=booking_repository,
    )