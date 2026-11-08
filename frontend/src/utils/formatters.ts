import type { Seat } from "../types/cinebook";

/**
 * Normalize an ISO datetime string from the backend as UTC even if the trailing
 * `Z` or offset was omitted by naive datetime serialization.
 */
export function parseUtcMillis(isoDate: string): number {
  const hasTimezone = /(?:Z|[+-]\d{2}:\d{2})$/i.test(isoDate);
  return new Date(hasTimezone ? isoDate : `${isoDate}Z`).getTime();
}

export function formatShowTime(isoDate: string): string {
  const utcMillis = parseUtcMillis(isoDate);
  const formatted = new Date(utcMillis).toLocaleString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "UTC",
  });
  return `${formatted} UTC`;
}

export function formatCurrency(amount: number): string {
  return `₹${amount.toLocaleString("en-IN")}`;
}

export function groupSeatsByRow(
  seats: Seat[],
): Array<{ row: string; seats: Seat[] }> {
  const map = new Map<string, Seat[]>();

  for (const item of seats) {
    const row = item.seat.replace(/[0-9]/g, "") || "?";
    const list = map.get(row) ?? [];
    list.push(item);
    map.set(row, list);
  }

  return Array.from(map.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([row, rowSeats]) => ({
      row,
      seats: rowSeats.sort((a, b) => {
        const numA = Number.parseInt(a.seat.replace(/\D/g, ""), 10) || 0;
        const numB = Number.parseInt(b.seat.replace(/\D/g, ""), 10) || 0;
        return numA - numB;
      }),
    }));
}
