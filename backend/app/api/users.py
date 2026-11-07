from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.db.dependencies import get_booking_service
from backend.app.schemas.booking import BookingResponse
from backend.app.services.booking_service import BookingService

from backend.app.db.dependencies import get_user_service
from backend.app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}/bookings",
    response_model=list[BookingResponse],
    response_model_by_alias=False,
)
async def get_user_bookings(
    user_id: str,
    service: Annotated[
    UserService,
    Depends(get_user_service),
    ],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[BookingResponse]:
    return await service.get_user_bookings(
        user_id=user_id,
        skip=skip,
        limit=limit,
    )