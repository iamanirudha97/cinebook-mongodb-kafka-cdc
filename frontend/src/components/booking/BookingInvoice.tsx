import type { BookingResponse } from "../../types/cinebook";
import { formatCurrency, formatShowTime } from "../../utils/formatters";

interface BookingInvoiceProps {
  booking: BookingResponse;
  onClose?: () => void;
}

export function BookingInvoice({ booking, onClose }: BookingInvoiceProps) {
  return (
    <section className="mb-6 overflow-hidden rounded-2xl border border-emerald-500/40 bg-white shadow-sm">
      {/* Invoice Header */}
      <div className="flex flex-col justify-between gap-2 bg-emerald-700 px-6 py-4 text-white sm:flex-row sm:items-center">
        <div>
          <p className="text-[11px] font-semibold tracking-widest text-emerald-200 uppercase">
            CineBook Official Ticket & Tax Invoice
          </p>
          <h3 className="text-lg font-bold">Booking Confirmed</h3>
        </div>
        <span className="w-fit rounded-full bg-emerald-500/30 px-3 py-1 text-xs font-bold tracking-wide text-white ring-1 ring-emerald-300/40 uppercase">
          {booking.status}
        </span>
      </div>

      {/* Invoice Body */}
      <div className="space-y-5 p-6">
        {/* Top Metadata */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-4">
          <div>
            <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
              Invoice / Booking ID
            </p>
            <p className="mt-0.5 break-all font-mono text-xs font-bold text-slate-900">
              {booking.id}
            </p>
          </div>

          <div>
            <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
              Booked By (User ID)
            </p>
            <p className="mt-0.5 font-mono text-xs font-bold text-slate-900">
              {booking.user_id}
            </p>
          </div>

          <div>
            <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
              Issued At
            </p>
            <p className="mt-0.5 text-xs font-semibold text-slate-800">
              {formatShowTime(booking.created_at)}
            </p>
          </div>

          <div>
            <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
              Idempotency Key
            </p>
            <p className="mt-0.5 break-all font-mono text-[11px] text-slate-500">
              {booking.idempotency_key}
            </p>
          </div>
        </div>

        {/* Screening Summary Box */}
        <div className="grid grid-cols-1 gap-4 rounded-xl border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2 md:grid-cols-4">
          <div>
            <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
              Movie
            </p>
            <p className="mt-0.5 text-sm font-bold text-slate-900">
              {booking.movie_title}
            </p>
            <p className="font-mono text-xs text-slate-500">
              {booking.movie_id}
            </p>
          </div>

          <div>
            <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
              Theater & City
            </p>
            <p className="mt-0.5 text-sm font-bold text-slate-900">
              {booking.theater_id}
            </p>
            <p className="text-xs text-slate-500">City: {booking.city}</p>
          </div>

          <div>
            <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
              Screen & Show ID
            </p>
            <p className="mt-0.5 text-sm font-bold text-slate-900">
              Screen: {booking.screen_id}
            </p>
            <p className="font-mono text-xs text-slate-500">
              {booking.show_id}
            </p>
          </div>

          <div>
            <p className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
              Show Start Time
            </p>
            <p className="mt-0.5 text-sm font-bold text-slate-900">
              {formatShowTime(booking.show_start_time)}
            </p>
          </div>
        </div>

        {/* Itemized Seat Breakdown Table */}
        <div>
          <h4 className="mb-2 text-xs font-semibold tracking-wider text-slate-500 uppercase">
            Itemized Seat Breakdown ({booking.seats.length} Seat
            {booking.seats.length > 1 ? "s" : ""})
          </h4>
          <div className="overflow-hidden rounded-xl border border-slate-200">
            <table className="w-full border-collapse text-left text-xs">
              <thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-4 py-2.5 font-semibold">#</th>
                  <th className="px-4 py-2.5 font-semibold">Seat Number</th>
                  <th className="px-4 py-2.5 font-semibold">Category</th>
                  <th className="px-4 py-2.5 text-right font-semibold">
                    Unit Price
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {booking.price_breakdown.map((item, idx) => (
                  <tr key={item.seat}>
                    <td className="px-4 py-2.5 text-slate-500">{idx + 1}</td>
                    <td className="px-4 py-2.5 font-mono font-bold text-slate-900">
                      {item.seat}
                    </td>
                    <td className="px-4 py-2.5">
                      <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-700">
                        {item.category}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-right font-semibold text-slate-800">
                      {formatCurrency(item.price)}
                    </td>
                  </tr>
                ))}
                <tr className="bg-emerald-50/70">
                  <td
                    colSpan={3}
                    className="px-4 py-3 text-sm font-bold text-slate-900"
                  >
                    Total Amount Paid
                  </td>
                  <td className="px-4 py-3 text-right text-sm font-bold text-emerald-700">
                    {formatCurrency(booking.amount)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex flex-col justify-between gap-3 border-t border-slate-100 pt-3 sm:flex-row sm:items-center">
          <p className="text-xs text-slate-500">
            Seats{" "}
            <span className="font-mono font-semibold text-slate-700">
              [{booking.seats.join(", ")}]
            </span>{" "}
            are reserved under {booking.id}.
          </p>

          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={() => window.print()}
              className="rounded-lg border border-slate-300 bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              Print / Save PDF
            </button>
            {onClose && (
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg bg-emerald-600 px-4 py-1.5 text-xs font-semibold text-white transition hover:bg-emerald-500"
              >
                Dismiss Invoice
              </button>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
