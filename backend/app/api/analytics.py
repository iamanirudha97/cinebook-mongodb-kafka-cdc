from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.db.dependencies import get_analytics_service
from backend.app.schemas.analytics import RevenuePerMovieResponse
from backend.app.services.analytics_service import AnalyticsService


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/revenue",
    response_model=list[RevenuePerMovieResponse],
)
async def get_revenue_per_movie(
    service: Annotated[
        AnalyticsService,
        Depends(get_analytics_service),
    ],
) -> list[RevenuePerMovieResponse]:
    return await service.get_revenue_per_movie()
