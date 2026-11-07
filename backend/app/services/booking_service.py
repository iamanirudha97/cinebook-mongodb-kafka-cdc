from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.write_concern import WriteConcern

from backend.app.repositories.booking_repository import BookingRepository
from backend.app.schemas.booking import BookingRequest, BookingResponse


class BookingService:
    def __init__(self, repository: BookingRepository) -> None:
        self.repository = repository

    @staticmethod
    def _same_request(
        booking: dict[str, Any],
        request: BookingRequest,
    ) -> bool:
        return (
            booking["user_id"] == request.user_id
            and booking["show_id"] == request.show_id
            and set(booking["seats"]) == set(request.seats)
        )

    async def create_booking(
        self,
        request: BookingRequest,
        idempotency_key: str,
    ) -> tuple[BookingResponse, bool]:
        existing = await self.repository.get_existing_booking(
            request.user_id,
            idempotency_key,
        )

        if existing is not None:
            return self._resolve_existing(existing, request), False

        booking_id = f"BKG-{uuid4().hex}"

        async def transaction(
            session: AsyncClientSession,
        ) -> tuple[dict[str, Any], bool]:
            previous = await self.repository.get_existing_booking(
                request.user_id,
                idempotency_key,
                session=session,
            )

            if previous is not None:
                if not self._same_request(previous, request):
                    raise HTTPException(
                        status_code=409,
                        detail="Idempotency key already used for another request",
                    )
                return previous, False

            user = await self.repository.get_user(
                request.user_id,
                session=session,
            )
            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User not found",
                )

            show = await self.repository.get_show(
                request.show_id,
                session=session,
            )
            if show is None:
                raise HTTPException(
                    status_code=404,
                    detail="Show not found",
                )

            if show["status"] != "SCHEDULED":
                raise HTTPException(
                    status_code=409,
                    detail="Show is not available for booking",
                )

            start_time = show["start_time"]
            if start_time.replace(tzinfo=timezone.utc) <= datetime.now(
                timezone.utc
            ):
                raise HTTPException(
                    status_code=409,
                    detail="Show has already started",
                )

            movie = await self.repository.get_movie(
                show["movie_id"],
                session=session,
            )
            if movie is None:
                raise HTTPException(
                    status_code=404,
                    detail="Movie referenced by show not found",
                )

            seats_by_id = {
                seat["seat"]: seat
                for seat in show["seats"]
            }

            if any(
                seat_id not in seats_by_id
                or seats_by_id[seat_id]["status"] != "AVAILABLE"
                for seat_id in request.seats
            ):
                raise HTTPException(
                    status_code=409,
                    detail="One or more requested seats are unavailable",
                )

            price_breakdown: list[dict[str, Any]] = []

            for seat_id in request.seats:
                category = seats_by_id[seat_id]["category"]
                price = show["prices"].get(category)

                if price is None:
                    raise HTTPException(
                        status_code=409,
                        detail="Seat category has no configured price",
                    )

                price_breakdown.append(
                    {
                        "seat": seat_id,
                        "category": category,
                        "price": price,
                    }
                )

            amount = sum(
                item["price"]
                for item in price_breakdown
            )

            booking: dict[str, Any] = {
                "_id": booking_id,
                "idempotency_key": idempotency_key,
                "user_id": request.user_id,
                "show_id": request.show_id,
                "seats": request.seats,
                "amount": amount,
                "status": "CONFIRMED",
                "created_at": datetime.now(timezone.utc),
                "movie_id": show["movie_id"],
                "movie_title": movie["title"],
                "theater_id": show["theater_id"],
                "screen_id": show["screen_id"],
                "city": show["city"],
                "show_start_time": show["start_time"],
                "price_breakdown": price_breakdown,
            }

            result = await self.repository.reserve_seats(
                show_id=request.show_id,
                seat_ids=request.seats,
                booking_id=booking_id,
                session=session,
            )

            if result.modified_count != 1:
                raise HTTPException(
                    status_code=409,
                    detail="One or more requested seats are unavailable",
                )

            await self.repository.create_booking(
                booking,
                session=session,
            )

            return booking, True

        client = self.repository.bookings.database.client

        try:
            async with client.start_session() as session:
                booking, created = await session.with_transaction(
                    transaction,
                    write_concern=WriteConcern("majority"),
                )

        except DuplicateKeyError:
            existing = await self.repository.get_existing_booking(
                request.user_id,
                idempotency_key,
            )

            if existing is None:
                raise

            return self._resolve_existing(existing, request), False

        except PyMongoError:
            # The transaction outcome may be uncertain.
            # Never claim that the booking failed or seats were released.
            existing = await self.repository.get_existing_booking(
                request.user_id,
                idempotency_key,
            )

            if existing is not None:
                return self._resolve_existing(existing, request), False

            raise HTTPException(
                status_code=503,
                detail=(
                    "Booking outcome could not be confirmed. "
                    "Retry using the same idempotency key."
                ),
            )

        return BookingResponse.model_validate(booking), created

    def _resolve_existing(
        self,
        existing: dict[str, Any],
        request: BookingRequest,
    ) -> BookingResponse:
        if not self._same_request(existing, request):
            raise HTTPException(
                status_code=409,
                detail="Idempotency key already used for another request",
            )

        return BookingResponse.model_validate(existing)

    async def get_booking(
        self,
        booking_id: str,
    ) -> BookingResponse:
        booking = await self.repository.get_booking_by_id(
            booking_id
        )

        if booking is None:
            raise HTTPException(
                status_code=404,
                detail="Booking not found",
            )

        return BookingResponse.model_validate(booking)

    