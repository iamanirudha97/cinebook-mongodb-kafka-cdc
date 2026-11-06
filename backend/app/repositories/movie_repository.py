from typing import Any

from pymongo.asynchronous.database import AsyncDatabase


class MovieRepository:
    def __init__(
        self,
        database: AsyncDatabase[dict[str, Any]],
    ) -> None:
        self.collection = database["movies"]

    async def list_movies(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        cursor = (
            self.collection.find({})
            .sort("_id", 1)
            .skip(skip)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def get_by_id(
        self,
        movie_id: str,
    ) -> dict[str, Any] | None:
        return await self.collection.find_one(
            {"_id": movie_id}
        )