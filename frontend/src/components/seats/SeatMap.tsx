import type { Movie, ShowDetail } from "../../types/cinebook";
import {
  formatCurrency,
  formatShowTime,
  groupSeatsByRow,
} from "../../utils/formatters";

interface SeatMapProps {
  movie: Movie | null;
  showDetail: ShowDetail;
  selectedSeats: string[];
  submitting: boolean;
  onToggleSeat: (seatId: string) => void;
  onClearSeats: () => void;
  onSubmitBooking: () => void;
}

export function SeatMap({
  movie,
  showDetail,
  selectedSeats,
  submitting,
  onToggleSeat,
  onClearSeats,
  onSubmitBooking,
}: SeatMapProps) {
  const rows = groupSeatsByRow(showDetail.seats);

  const totalAmount = selectedSeats.reduce((sum, seatId) => {
    const seatObj = showDetail.seats.find((s) => s.seat === seatId);
    return sum + (seatObj ? (showDetail.prices[seatObj.category] ?? 0) : 0);
  }, 0);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
      {/* Section Header & Legend */}
      <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-sm font-semibold tracking-wide text-slate-800 uppercase">
            3. Select Seats ({showDetail.seats_available} of{" "}
            {showDetail.seats_total} available)
          </h2>
          <p className="mt-0.5 text-xs text-slate-500">
            Prices:{" "}
            {Object.entries(showDetail.prices)
              .map(
                ([category, price]) => `${category}: ${formatCurrency(price)}`,
              )
              .join(" • ")}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs font-medium text-slate-600">
          <span className="flex items-center gap-1.5">
            <span className="h-3.5 w-3.5 rounded-sm border border-emerald-500 bg-emerald-50" />
            Available
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-3.5 w-3.5 rounded-sm bg-indigo-600" />
            Selected
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-3.5 w-3.5 rounded-sm border border-slate-200 bg-slate-100" />
            Booked
          </span>
        </div>
      </div>

      {/* Movie, Theater, Screen & Showtime Details Banner */}
      <div className="mb-5 grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-slate-50/80 p-3.5 sm:grid-cols-2 md:grid-cols-4">
        <div>
          <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
            Movie
          </p>
          <p className="mt-0.5 text-sm font-bold text-slate-900">
            {movie ? movie.title : showDetail.movie_id}
          </p>
          {movie && (
            <p className="text-xs text-slate-500">
              {movie.language} • {movie.certification} • {movie.duration_min}m
            </p>
          )}
        </div>

        <div>
          <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
            Theater & City
          </p>
          <p className="mt-0.5 text-sm font-bold text-slate-900">
            {showDetail.theater_id}
          </p>
          <p className="text-xs text-slate-500">City: {showDetail.city}</p>
        </div>

        <div>
          <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
            Screen & Show ID
          </p>
          <p className="mt-0.5 text-sm font-bold text-slate-900">
            Screen: {showDetail.screen_id}
          </p>
          <p className="font-mono text-xs text-slate-500">{showDetail.id}</p>
        </div>

        <div>
          <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
            Showtime
          </p>
          <p className="mt-0.5 text-sm font-bold text-slate-900">
            {formatShowTime(showDetail.start_time)}
          </p>
          <p className="text-xs text-slate-500">Status: {showDetail.status}</p>
        </div>
      </div>

      {/* Screen Indicator */}
      <div className="mx-auto mb-6 max-w-xl">
        <div className="h-2 w-full rounded-t-full bg-gradient-to-r from-indigo-200 via-indigo-500 to-indigo-200" />
        <p className="mt-1.5 text-center text-[11px] font-semibold tracking-[0.2em] text-slate-400 uppercase">
          Screen This Way
        </p>
      </div>

      {/* Seat Grid Grouped by Row */}
      <div className="space-y-2 overflow-x-auto pb-2">
        {rows.map(({ row, seats }) => {
          const category = seats[0]?.category ?? "";
          const price = showDetail.prices[category];
          return (
            <div
              key={row}
              className="mx-auto flex w-fit items-center gap-2.5"
            >
              <span className="w-5 text-right text-xs font-bold text-slate-400">
                {row}
              </span>

              <div className="flex items-center gap-1.5">
                {seats.map((seat) => {
                  const isBooked = seat.status === "BOOKED";
                  const isSelected = selectedSeats.includes(seat.seat);

                  let seatClass =
                    "h-8 w-10 rounded-md text-xs font-semibold transition focus:outline-none ";
                  if (isBooked) {
                    seatClass +=
                      "cursor-not-allowed border border-slate-200 bg-slate-100 text-slate-400 line-through";
                  } else if (isSelected) {
                    seatClass +=
                      "border border-indigo-600 bg-indigo-600 text-white shadow-xs";
                  } else {
                    seatClass +=
                      "border border-emerald-500/70 bg-emerald-50/50 text-emerald-700 hover:border-emerald-600 hover:bg-emerald-100/70";
                  }

                  return (
                    <button
                      key={seat.seat}
                      type="button"
                      disabled={isBooked || submitting}
                      onClick={() => onToggleSeat(seat.seat)}
                      className={seatClass}
                    >
                      {seat.seat}
                    </button>
                  );
                })}
              </div>

              <span className="w-28 pl-2 text-[11px] font-medium text-slate-400">
                {category} {price !== undefined ? formatCurrency(price) : ""}
              </span>
            </div>
          );
        })}
      </div>

      {/* Checkout Bar */}
      <div className="mt-6 flex flex-col justify-between gap-4 border-t border-slate-200 pt-4 sm:flex-row sm:items-center">
        <div className="space-y-0.5 text-sm">
          <p className="text-slate-600">
            <span className="font-semibold text-slate-800">
              Selected Seats:
            </span>{" "}
            {selectedSeats.length > 0 ? (
              <span className="font-mono font-bold text-indigo-600">
                {selectedSeats.join(", ")}
              </span>
            ) : (
              <span className="text-slate-400">None</span>
            )}
          </p>
          <p className="text-slate-600">
            <span className="font-semibold text-slate-800">Total Amount:</span>{" "}
            <span className="text-base font-bold text-slate-900">
              {formatCurrency(totalAmount)}
            </span>
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {selectedSeats.length > 0 && (
            <button
              type="button"
              onClick={onClearSeats}
              disabled={submitting}
              className="rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
            >
              Clear
            </button>
          )}
          <button
            type="button"
            disabled={
              selectedSeats.length === 0 ||
              submitting ||
              showDetail.status !== "SCHEDULED"
            }
            onClick={onSubmitBooking}
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
          >
            {submitting
              ? "Booking..."
              : `Confirm Booking (${selectedSeats.length})`}
          </button>
        </div>
      </div>
    </section>
  );
}
