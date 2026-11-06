from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SeatResponse(BaseModel):
    seat: str
    category: str
    status: Literal["AVAILABLE", "BOOKED"]
    booking_id: str | None = None


class ShowSummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    city: str
    movie_id: str
    theater_id: str
    screen_id: str
    start_time: datetime
    status: Literal["SCHEDULED", "CANCELLED"]
    prices: dict[str, int]
    seats_total: int
    seats_available: int


class ShowDetailResponse(ShowSummaryResponse):
    seats: list[SeatResponse]
