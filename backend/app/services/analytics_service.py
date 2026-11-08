from backend.app.repositories.analytics_repository import AnalyticsRepository
from backend.app.schemas.analytics import RevenuePerMovieResponse


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self.repository = repository

    async def get_revenue_per_movie(self) -> list[RevenuePerMovieResponse]:
        results = await self.repository.get_revenue_per_movie()

        return [
            RevenuePerMovieResponse.model_validate(result)
            for result in results
        ]
