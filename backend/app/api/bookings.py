from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Response

from backend.app.db.dependencies import get_booking_service
from backend.app.schemas.booking import BookingRequest, BookingResponse
from backend.app.services.booking_service import BookingService


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingResponse,
    response_model_by_alias=False,
)
async def create_booking(
    request: BookingRequest,
    response: Response,
    service: Annotated[BookingService, Depends(get_booking_service)],
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
) -> BookingResponse:
    booking, created = await service.create_booking(
        request=request,
        idempotency_key=str(idempotency_key),
    )

    response.status_code = 201 if created else 200
    return booking

@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    response_model_by_alias=False,
)
async def get_booking(
    booking_id: str,
    service: Annotated[
        BookingService,
        Depends(get_booking_service),
    ],
) -> BookingResponse:
    return await service.get_booking(booking_id)
