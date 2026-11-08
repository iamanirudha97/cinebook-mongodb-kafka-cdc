from pydantic import BaseModel


class RevenuePerMovieResponse(BaseModel):
    movie_id: str
    movie_title: str
    total_revenue: int | float
    total_bookings: int
    total_seats_sold: int
