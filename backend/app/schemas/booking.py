from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BookingRequest(BaseModel):
    user_id: str = Field(pattern=r"^USR-[0-9]{4}$")
    show_id: str = Field(pattern=r"^SHW-[0-9]{6}$")
    seats: list[str] = Field(min_length=1)

    @field_validator("seats")
    @classmethod
    def validate_seats(cls, seats: list[str]) -> list[str]:
        import re

        if any(
            re.fullmatch(r"[A-Z][0-9]{1,3}", seat) is None
            for seat in seats
        ):
            raise ValueError("Invalid seat identifier")

        if len(seats) != len(set(seats)):
            raise ValueError("Duplicate seats are not allowed")

        return seats


class PriceBreakdownItem(BaseModel):
    seat: str
    category: str
    price: int | float


class BookingResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    idempotency_key: str
    user_id: str
    show_id: str
    seats: list[str]
    amount: int | float
    status: Literal["CONFIRMED", "CANCELLED"]
    created_at: datetime

    movie_id: str
    movie_title: str
    theater_id: str
    screen_id: str
    city: str
    show_start_time: datetime
    price_breakdown: list[PriceBreakdownItem]