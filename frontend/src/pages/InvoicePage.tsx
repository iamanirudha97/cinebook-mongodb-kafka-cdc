import { useEffect, useState } from "react";
import { BookingInvoice } from "../components/booking/BookingInvoice";
import { fetchBookingById } from "../services/bookingService";
import type { BookingResponse } from "../types/cinebook";

interface InvoicePageProps {
  bookingId: string;
  initialBooking: BookingResponse | null;
  onNavigateHome: () => void;
}

export function InvoicePage({
  bookingId,
  initialBooking,
  onNavigateHome,
}: InvoicePageProps) {
  const [booking, setBooking] = useState<BookingResponse | null>(
    initialBooking,
  );
  const [loading, setLoading] = useState<boolean>(!initialBooking);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (initialBooking && initialBooking.id === bookingId) {
      setBooking(initialBooking);
      setLoading(false);
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    fetchBookingById(bookingId)
      .then((res) => {
        if (res.ok && res.data) {
          setBooking(res.data);
        } else {
          setErrorMsg(res.error || "Failed to load booking invoice");
        }
      })
      .catch(() => setErrorMsg("Unable to fetch booking details from server"))
      .finally(() => setLoading(false));
  }, [bookingId, initialBooking]);

  return (
    <div className="min-h-screen bg-slate-100/80 py-8 text-slate-900">
      <div className="mx-auto max-w-4xl px-4 sm:px-6">
        {/* Top Navigation Bar */}
        <div className="mb-6 flex items-center justify-between">
          <button
            type="button"
            onClick={onNavigateHome}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-2xs transition hover:bg-slate-50"
          >
            ← Back to Seat Booking
          </button>

          <span className="font-mono text-xs text-slate-500">
            /bookings/{bookingId}
          </span>
        </div>

        {loading && (
          <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500">
            Loading invoice {bookingId}...
          </div>
        )}

        {errorMsg && (
          <div className="rounded-2xl border border-rose-300 bg-rose-50 p-6 text-sm text-rose-800">
            <p className="font-semibold">Could not load invoice</p>
            <p className="mt-1">{errorMsg}</p>
            <button
              type="button"
              onClick={onNavigateHome}
              className="mt-4 rounded-lg bg-rose-600 px-4 py-2 text-xs font-semibold text-white hover:bg-rose-500"
            >
              Return Home
            </button>
          </div>
        )}

        {booking && (
          <BookingInvoice booking={booking} onClose={onNavigateHome} />
        )}
      </div>
    </div>
  );
}
