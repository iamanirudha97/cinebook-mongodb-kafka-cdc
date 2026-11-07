from backend.app.repositories.show_repository import ShowRepository
from backend.app.schemas.show import (
    ShowDetailResponse,
    ShowSummaryResponse,
)


class ShowService:
    def __init__(self, repository: ShowRepository) -> None:
        self.repository = repository

    async def list_shows(
        self,
        movie_id: str,
        city: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ShowSummaryResponse]:
        documents = await self.repository.list_shows(
            movie_id=movie_id,
            city=city,
            skip=skip,
            limit=limit,
        )

        return [
            ShowSummaryResponse.model_validate(document)
            for document in documents
        ]

    async def get_show(
        self,
        show_id: str,
    ) -> ShowDetailResponse | None:
        document = await self.repository.get_by_id(show_id)

        if document is None:
            return None

        return ShowDetailResponse.model_validate(document)
        