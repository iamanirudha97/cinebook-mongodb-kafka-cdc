import type { Movie, ShowSummary } from "../../types/cinebook";
import { formatShowTime } from "../../utils/formatters";

interface ShowSelectorProps {
  movie: Movie | null;
  shows: ShowSummary[];
  selectedShowId: string;
  onSelectShow: (showId: string) => void;
  onRefreshSeats: () => void;
}

export function ShowSelector({
  movie,
  shows,
  selectedShowId,
  onSelectShow,
  onRefreshSeats,
}: ShowSelectorProps) {
  return (
    <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-sm font-semibold tracking-wide text-slate-800 uppercase">
            2. Select Showtime {movie ? `— ${movie.title}` : ""}
          </h2>
          {movie && (
            <p className="mt-0.5 text-xs text-slate-500">
              {movie.language} • {movie.genres.join(", ")} • {movie.duration_min} mins
            </p>
          )}
        </div>

        {selectedShowId && (
          <button
            type="button"
            onClick={onRefreshSeats}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50 active:bg-slate-100"
          >
            Refresh Availability
          </button>
        )}
      </div>

      {shows.length === 0 ? (
        <p className="text-sm text-slate-500">
          No shows found for the selected movie and city.
        </p>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3">
          {shows.map((show) => {
            const isSelected = show.id === selectedShowId;
            const hasSeats = show.seats_available > 0;
            return (
              <button
                key={show.id}
                type="button"
                onClick={() => onSelectShow(show.id)}
                className={`rounded-xl border p-3.5 text-left transition-all ${
                  isSelected
                    ? "border-indigo-600 bg-indigo-50/70 ring-2 ring-indigo-600/20"
                    : "border-slate-200 bg-white hover:border-indigo-300 hover:bg-slate-50/80"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span
                    className={`text-sm font-bold ${
                      isSelected ? "text-indigo-700" : "text-slate-900"
                    }`}
                  >
                    {formatShowTime(show.start_time)}
                  </span>
                  {isSelected && (
                    <span className="rounded-full bg-indigo-600 px-2 py-0.5 text-[10px] font-bold tracking-wide text-white uppercase">
                      Active
                    </span>
                  )}
                </div>

                <p className="mt-1.5 text-xs text-slate-600">
                  Theater:{" "}
                  <span className="font-semibold text-slate-800">
                    {show.theater_id}
                  </span>{" "}
                  • Screen:{" "}
                  <span className="font-semibold text-slate-800">
                    {show.screen_id}
                  </span>
                </p>
                <p className="mt-0.5 font-mono text-[11px] text-slate-400">
                  {show.id} • {show.city}
                </p>

                <div className="mt-2.5 flex items-center gap-2">
                  <span
                    className={`rounded-md px-2 py-0.5 text-[11px] font-semibold ${
                      hasSeats
                        ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20"
                        : "bg-rose-50 text-rose-700 ring-1 ring-rose-600/20"
                    }`}
                  >
                    {show.seats_available}/{show.seats_total} available
                  </span>
                  <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">
                    {show.status}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}
