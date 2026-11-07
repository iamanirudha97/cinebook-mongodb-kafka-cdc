from backend.app.repositories.movie_repository import MovieRepository
from backend.app.schemas.movie import MovieResponse


class MovieService:
    def __init__(self, repository: MovieRepository) -> None:
        self.repository = repository

    async def list_movies(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[MovieResponse]:
        documents = await self.repository.list_movies(
            skip=skip,
            limit=limit,
        )

        return [
            MovieResponse.model_validate(document)
            for document in documents
        ]

    async def get_movie(
        self,
        movie_id: str,
    ) -> MovieResponse | None:
        document = await self.repository.get_by_id(movie_id)

        if document is None:
            return None

        return MovieResponse.model_validate(document)
        