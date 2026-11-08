import type { Movie } from "../types/cinebook";
import { apiRequest } from "./httpClient";

export function fetchMovies(limit = 50) {
  return apiRequest<Movie[]>(`/movies?skip=0&limit=${limit}`);
}

