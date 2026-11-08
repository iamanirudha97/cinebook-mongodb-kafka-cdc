import type { BookingRequest, BookingResponse } from "../types/cinebook";
import { apiRequest } from "./httpClient";

export function createBooking(payload: BookingRequest, idempotencyKey: string) {
  return apiRequest<BookingResponse>("/bookings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": idempotencyKey,
    },
    body: JSON.stringify(payload),
  });
}

export function fetchBookingById(bookingId: string) {
  return apiRequest<BookingResponse>(
    `/bookings/${encodeURIComponent(bookingId)}`,
  );
}

export function fetchUserBookings(userId: string, limit = 50) {
  return apiRequest<BookingResponse[]>(
    `/users/${encodeURIComponent(userId)}/bookings?skip=0&limit=${limit}`,
  );
}
