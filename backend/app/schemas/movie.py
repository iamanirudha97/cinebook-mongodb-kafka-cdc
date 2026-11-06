from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MovieResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    title: str
    genres: list[str]
    language: str
    duration_min: int
    certification: str
    cities: list[str]
    release_date: datetime
