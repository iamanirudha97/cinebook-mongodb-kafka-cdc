from typing import Any

from pymongo.asynchronous.database import AsyncDatabase


class AnalyticsRepository:
    def __init__(
        self,
        database: AsyncDatabase[dict[str, Any]],
    ) -> None:
        self.collection = database["bookings"]

    async def get_revenue_per_movie(self) -> list[dict[str, Any]]:
        pipeline = [
            {
                "$match": {
                    "status": "CONFIRMED",
                }
            },
            {
                "$group": {
                    "_id": "$movie_id",
                    "movie_title": {"$first": "$movie_title"},
                    "total_revenue": {"$sum": "$amount"},
                    "total_bookings": {"$sum": 1},
                    "total_seats_sold": {
                        "$sum": {"$size": "$seats"}
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "movie_id": "$_id",
                    "movie_title": 1,
                    "total_revenue": 1,
                    "total_bookings": 1,
                    "total_seats_sold": 1,
                }
            },
            {
                "$sort": {
                    "total_revenue": -1,
                }
            },
        ]

        cursor = await self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
