export interface Movie {
  id: string;
  title: string;
  genres: string[];
  language: string;
  duration_min: number;
  certification: string;
  cities: string[];
  release_date: string;
}

export interface Seat {
  seat: string;
  category: string;
  status: "AVAILABLE" | "BOOKED";
  booking_id?: string | null;
}

export interface ShowSummary {
  id: string;
  city: string;
  movie_id: string;
  theater_id: string;
  screen_id: string;
  start_time: string;
  status: "SCHEDULED" | "CANCELLED";
  prices: Record<string, number>;
  seats_total: number;
  seats_available: number;
}

export interface ShowDetail extends ShowSummary {
  seats: Seat[];
}

export interface BookingRequest {
  user_id: string;
  show_id: string;
  seats: string[];
}

export interface PriceBreakdownItem {
  seat: string;
  category: string;
  price: number;
}

export interface BookingResponse {
  id: string;
  idempotency_key: string;
  user_id: string;
  show_id: string;
  seats: string[];
  amount: number;
  status: "CONFIRMED" | "CANCELLED";
  created_at: string;
  movie_id: string;
  movie_title: string;
  theater_id: string;
  screen_id: string;
  city: string;
  show_start_time: string;
  price_breakdown: PriceBreakdownItem[];
}

export interface ApiResult<T> {
  ok: boolean;
  status: number;
  data?: T;
  error?: string;
}

