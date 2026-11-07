
from fastapi import HTTPException

from backend.app.repositories.booking_repository import BookingRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.booking import BookingResponse


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        booking_repository: BookingRepository,
    ) -> None:
        self.user_repository = user_repository
        self.booking_repository = booking_repository

    async def get_user_bookings(
        self,
        user_id: str,
        skip: int,
        limit: int,
    ) -> list[BookingResponse]:
        user = await self.user_repository.get_user_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        bookings = await self.booking_repository.get_bookings_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

        return [
            BookingResponse.model_validate(booking)
            for booking in bookings
        ]
