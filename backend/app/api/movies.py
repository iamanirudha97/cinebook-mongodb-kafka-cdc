from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.db.dependencies import get_movie_service
from backend.app.schemas.movie import MovieResponse
from backend.app.services.movie_service import MovieService


router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get(
    "",
    response_model=list[MovieResponse],
    response_model_by_alias=False,
)
async def list_movies(
    service: Annotated[MovieService, Depends(get_movie_service)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[MovieResponse]:
    return await service.list_movies(skip=skip, limit=limit)


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    response_model_by_alias=False,
)
async def get_movie(
    movie_id: str,
    service: Annotated[MovieService, Depends(get_movie_service)],
) -> MovieResponse:
    movie = await service.get_movie(movie_id)

    if movie is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        )

    return movie