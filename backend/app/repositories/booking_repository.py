from typing import Any

from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.results import InsertOneResult, UpdateResult


class BookingRepository:
    def __init__(
        self,
        database: AsyncDatabase[dict[str, Any]],
    ) -> None:
        self.bookings = database["bookings"]
        self.shows = database["shows"]
        self.movies = database["movies"]
        self.users = database["users"]

    async def get_existing_booking(
        self,
        user_id: str,
        idempotency_key: str,
        session: AsyncClientSession | None = None,
    ) -> dict[str, Any] | None:
        return await self.bookings.find_one(
            {
                "user_id": user_id,
                "idempotency_key": idempotency_key,
            },
            session=session,
        )

    async def get_show(
        self,
        show_id: str,
        session: AsyncClientSession | None = None,
    ) -> dict[str, Any] | None:
        return await self.shows.find_one(
            {"_id": show_id},
            session=session,
        )

    async def get_movie(
        self,
        movie_id: str,
        session: AsyncClientSession | None = None,
    ) -> dict[str, Any] | None:
        return await self.movies.find_one(
            {"_id": movie_id},
            session=session,
        )

    async def get_user(
        self,
        user_id: str,
        session: AsyncClientSession | None = None,
    ) -> dict[str, Any] | None:
        return await self.users.find_one(
            {"_id": user_id},
            session=session,
        )

    async def reserve_seats(
        self,
        show_id: str,
        seat_ids: list[str],
        booking_id: str,
        session: AsyncClientSession,
    ) -> UpdateResult:
        return await self.shows.update_one(
            {
                "_id": show_id,
                "status": "SCHEDULED",
                "seats_available": {"$gte": len(seat_ids)},
                "seats": {
                    "$all": [
                        {
                            "$elemMatch": {
                                "seat": seat_id,
                                "status": "AVAILABLE",
                            }
                        }
                        for seat_id in seat_ids
                    ]
                },
            },
            {
                "$set": {
                    "seats.$[selected].status": "BOOKED",
                    "seats.$[selected].booking_id": booking_id,
                },
                "$inc": {
                    "seats_available": -len(seat_ids),
                },
            },
            array_filters=[
                {
                    "selected.seat": {"$in": seat_ids},
                    "selected.status": "AVAILABLE",
                }
            ],
            session=session,
        )

    async def create_booking(
        self,
        booking: dict[str, Any],
        session: AsyncClientSession,
    ) -> InsertOneResult:
        return await self.bookings.insert_one(
            booking,
            session=session,
        )


    async def get_booking_by_id(
        self,
        booking_id: str,
    ) -> dict[str, Any] | None:
        return await self.bookings.find_one(
        {"_id": booking_id}
    )

    async def get_bookings_by_user(
        self,
        user_id: str,
        skip: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        cursor = (
            self.bookings.find({"user_id": user_id})
            .sort([("created_at", -1), ("_id", -1)])
            .skip(skip)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)