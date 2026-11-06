from typing import Any

from pymongo.asynchronous.database import AsyncDatabase


class ShowRepository:
    def __init__(
        self,
        database: AsyncDatabase[dict[str, Any]],
    ) -> None:
        self.collection = database["shows"]

    async def list_shows(
        self,
        movie_id: str,
        city: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        cursor = (
            self.collection.find(
                {
                    "movie_id": movie_id,
                    "city": city,
                },
                {"seats": 0},
            )
            .sort([("start_time", 1), ("_id", 1)])
            .skip(skip)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def get_by_id(
        self,
        show_id: str,
    ) -> dict[str, Any] | None:
        return await self.collection.find_one(
            {"_id": show_id}
        )