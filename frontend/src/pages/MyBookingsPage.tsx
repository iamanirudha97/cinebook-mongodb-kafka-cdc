import { useCallback, useEffect, useState } from "react";
import { HeaderBar } from "../components/layout/HeaderBar";
import { fetchUserBookings } from "../services/bookingService";
import type { BookingResponse } from "../types/cinebook";
import { formatCurrency, formatShowTime } from "../utils/formatters";

interface MyBookingsPageProps {
  userId: string;
  onChangeUserId: (userId: string) => void;
  onNavigateHome: () => void;
  onOpenInvoice: (booking: BookingResponse) => void;
}

export function MyBookingsPage({
  userId,
  onChangeUserId,
  onNavigateHome,
  onOpenInvoice,
}: MyBookingsPageProps) {
  const [bookings, setBookings] = useState<BookingResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadBookings = useCallback(async (targetUserId: string) => {
    const trimmed = targetUserId.trim();
    if (!/^USR-\d{4}$/.test(trimmed)) {
      setBookings([]);
      setErrorMsg("Enter a valid User ID in format USR-XXXX (e.g., USR-0001).");
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetchUserBookings(trimmed, 50);
      if (res.ok && res.data) {
        setBookings(res.data);
      } else {
        setBookings([]);
        setErrorMsg(res.error || "Could not load user bookings");
      }
    } catch {
      setBookings([]);
      setErrorMsg("Unable to reach backend API");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadBookings(userId);
  }, [userId, loadBookings]);

  const totalSpent = bookings
    .filter((b) => b.status === "CONFIRMED")
    .reduce((sum, b) => sum + b.amount, 0);

  return (
    <div className="min-h-screen bg-slate-100/80 py-8 text-slate-900">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <HeaderBar
          userId={userId}
          onChangeUserId={onChangeUserId}
          activeTab="my-bookings"
          onNavigateHome={onNavigateHome}
          onNavigateMyBookings={() => void loadBookings(userId)}
        />

        {/* Summary & Controls Card */}
        <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-xs">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Booking History for{" "}
                <span className="font-mono text-indigo-600">{userId}</span>
              </h2>
              <p className="mt-0.5 text-xs text-slate-500">
                Edit the User ID in the header above (e.g.{" "}
                <span className="font-mono">USR-0001</span> to{" "}
                <span className="font-mono">USR-0500</span>) to inspect any
                customer&apos;s bookings in real time.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-right">
                <p className="text-[10px] font-semibold tracking-wider text-slate-400 uppercase">
                  Total Bookings
                </p>
                <p className="text-sm font-bold text-slate-900">
                  {bookings.length}
                </p>
              </div>

              <div className="rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-right">
                <p className="text-[10px] font-semibold tracking-wider text-slate-400 uppercase">
                  Confirmed Spend
                </p>
                <p className="text-sm font-bold text-emerald-700">
                  {formatCurrency(totalSpent)}
                </p>
              </div>

              <button
                type="button"
                onClick={() => void loadBookings(userId)}
                disabled={loading}
                className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
              >
                {loading ? "Loading..." : "Refresh"}
              </button>
            </div>
          </div>
        </section>

        {errorMsg && (
          <div className="mb-6 rounded-xl border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800">
            {errorMsg}
          </div>
        )}

        {loading && (
          <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500">
            Fetching bookings for {userId}...
          </div>
        )}

        {!loading && !errorMsg && bookings.length === 0 && (
          <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center">
            <p className="text-sm font-semibold text-slate-700">
              No bookings found for {userId}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Book tickets or enter another User ID (such as USR-0001) to view
              existing reservations.
            </p>
            <button
              type="button"
              onClick={onNavigateHome}
              className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-indigo-500"
            >
              Browse Movies & Book Seats
            </button>
          </div>
        )}

        {!loading && bookings.length > 0 && (
          <div className="space-y-3">
            {bookings.map((booking) => {
              const isConfirmed = booking.status === "CONFIRMED";
              return (
                <div
                  key={booking.id}
                  className="flex flex-col justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-xs transition hover:border-indigo-300 sm:flex-row sm:items-center"
                >
                  <div className="space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold tracking-wide uppercase ${
                          isConfirmed
                            ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {booking.status}
                      </span>
                      <span className="font-mono text-xs font-semibold text-slate-500">
                        {booking.id}
                      </span>
                      <span className="text-xs text-slate-400">•</span>
                      <span className="text-xs text-slate-500">
                        Booked {formatShowTime(booking.created_at)}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-slate-900">
                      {booking.movie_title}{" "}
                      <span className="font-normal text-slate-500">
                        ({booking.city})
                      </span>
                    </h3>

                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600">
                      <span>
                        Theater:{" "}
                        <strong className="text-slate-800">
                          {booking.theater_id}
                        </strong>{" "}
                        ({booking.screen_id})
                      </span>
                      <span>
                        Show:{" "}
                        <strong className="font-mono text-slate-800">
                          {booking.show_id}
                        </strong>
                      </span>
                      <span>
                        Showtime:{" "}
                        <strong className="text-slate-800">
                          {formatShowTime(booking.show_start_time)}
                        </strong>
                      </span>
                    </div>

                    <div className="pt-1 text-xs">
                      <span className="text-slate-500">Seats: </span>
                      <span className="font-mono font-bold text-indigo-600">
                        {booking.seats.join(", ")}
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-row items-center justify-between gap-4 border-t border-slate-100 pt-3 sm:flex-col sm:items-end sm:border-t-0 sm:pt-0">
                    <div className="sm:text-right">
                      <p className="text-[11px] font-medium text-slate-400 uppercase">
                        Total Paid
                      </p>
                      <p className="text-lg font-bold text-slate-900">
                        {formatCurrency(booking.amount)}
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={() => onOpenInvoice(booking)}
                      className="rounded-lg bg-indigo-50 px-3.5 py-2 text-xs font-semibold text-indigo-700 transition hover:bg-indigo-100"
                    >
                      View Invoice →
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

