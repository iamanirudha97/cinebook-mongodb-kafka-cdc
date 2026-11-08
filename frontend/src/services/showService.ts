import type { ShowDetail, ShowSummary } from "../types/cinebook";
import { apiRequest } from "./httpClient";

export function fetchShowsByMovieAndCity(movieId: string, city: string, limit = 50) {
  const params = new URLSearchParams({
    movie_id: movieId,
    city,
    skip: "0",
    limit: String(limit),
  });
  return apiRequest<ShowSummary[]>(`/shows?${params.toString()}`);
}

export function fetchShowById(showId: string) {
  return apiRequest<ShowDetail>(`/shows/${encodeURIComponent(showId)}`);
}

