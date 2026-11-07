from typing import Any

from pymongo.asynchronous.database import AsyncDatabase


class UserRepository:
    def __init__(
        self,
        database: AsyncDatabase[dict[str, Any]],
    ) -> None:
        self.users = database["users"]

    async def get_user_by_id(
        self,
        user_id: str,
    ) -> dict[str, Any] | None:
        return await self.users.find_one(
            {"_id": user_id}
        )