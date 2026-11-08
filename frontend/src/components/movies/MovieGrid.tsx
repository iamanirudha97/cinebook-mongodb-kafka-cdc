import type { Movie } from "../../types/cinebook";

interface MovieGridProps {
  movies: Movie[];
  selectedCity: string;
  selectedMovieId: string;
  onSelectMovie: (movieId: string) => void;
}

export function MovieGrid({
  movies,
  selectedCity,
  selectedMovieId,
  onSelectMovie,
}: MovieGridProps) {
  return (
    <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold tracking-wide text-slate-800 uppercase">
          1. Browse Movies in {selectedCity}
        </h2>
        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
          {movies.length} available
        </span>
      </div>

      {movies.length === 0 ? (
        <p className="text-sm text-slate-500">
          No movies available in {selectedCity}.
        </p>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-4">
          {movies.map((movie) => {
            const isSelected = movie.id === selectedMovieId;
            return (
              <button
                key={movie.id}
                type="button"
                onClick={() => onSelectMovie(movie.id)}
                className={`group flex flex-col justify-between rounded-xl border p-3.5 text-left transition-all ${
                  isSelected
                    ? "border-indigo-600 bg-indigo-50/70 ring-2 ring-indigo-600/20"
                    : "border-slate-200 bg-white hover:border-indigo-300 hover:bg-slate-50/80"
                }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h3
                      className={`text-sm font-semibold leading-snug ${
                        isSelected
                          ? "text-indigo-700"
                          : "text-slate-900 group-hover:text-indigo-600"
                      }`}
                    >
                      {movie.title}
                    </h3>
                    <span
                      className={`shrink-0 rounded-md px-1.5 py-0.5 text-[11px] font-semibold ${
                        isSelected
                          ? "bg-indigo-600 text-white"
                          : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {movie.certification}
                    </span>
                  </div>

                  <p className="mt-1.5 text-xs text-slate-500">
                    {movie.language} • {movie.duration_min} mins
                  </p>
                </div>

                <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-2">
                  <span className="truncate text-[11px] text-slate-500">
                    {movie.genres.join(", ")}
                  </span>
                  {isSelected && (
                    <span className="shrink-0 rounded-full bg-indigo-600 px-2 py-0.5 text-[10px] font-bold tracking-wide text-white uppercase">
                      Selected
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}
