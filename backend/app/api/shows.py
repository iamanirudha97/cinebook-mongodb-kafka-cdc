from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.db.dependencies import get_show_service
from backend.app.schemas.show import (
    ShowDetailResponse,
    ShowSummaryResponse,
)
from backend.app.services.show_service import ShowService


router = APIRouter(prefix="/shows", tags=["Shows"])


@router.get(
    "",
    response_model=list[ShowSummaryResponse],
    response_model_by_alias=False,
)
async def list_shows(
    service: Annotated[ShowService, Depends(get_show_service)],
    movie_id: str,
    city: str,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ShowSummaryResponse]:
    return await service.list_shows(
        movie_id=movie_id,
        city=city,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{show_id}",
    response_model=ShowDetailResponse,
    response_model_by_alias=False,
)
async def get_show(
    show_id: str,
    service: Annotated[ShowService, Depends(get_show_service)],
) -> ShowDetailResponse:
    show = await service.get_show(show_id)

    if show is None:
        raise HTTPException(
            status_code=404,
            detail="Show not found",
        )

    return show