import { useEffect, useState } from "react";
import { HeaderBar } from "../components/layout/HeaderBar";
import { MovieGrid } from "../components/movies/MovieGrid";
import { SeatMap } from "../components/seats/SeatMap";
import { ShowSelector } from "../components/shows/ShowSelector";
import { DEFAULT_CITIES } from "../config/env";
import { createBooking } from "../services/bookingService";
import { fetchMovies } from "../services/movieService";
import {
  fetchShowById,
  fetchShowsByMovieAndCity,
} from "../services/showService";
import type {
  BookingResponse,
  Movie,
  ShowDetail,
  ShowSummary,
} from "../types/cinebook";
import { parseUtcMillis } from "../utils/formatters";

interface BookingPageProps {
  userId: string;
  onChangeUserId: (userId: string) => void;
  onBookingCreated: (booking: BookingResponse) => void;
  onNavigateMyBookings: () => void;
}

export function BookingPage({
  userId,
  onChangeUserId,
  onBookingCreated,
  onNavigateMyBookings,
}: BookingPageProps) {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [selectedCity, setSelectedCity] = useState<string>(DEFAULT_CITIES[0]);
  const [selectedMovieId, setSelectedMovieId] = useState<string>("");

  const [shows, setShows] = useState<ShowSummary[]>([]);
  const [selectedShowId, setSelectedShowId] = useState<string>("");

  const [showDetail, setShowDetail] = useState<ShowDetail | null>(null);
  const [selectedSeats, setSelectedSeats] = useState<string[]>([]);

  const [loadingMovies, setLoadingMovies] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [canRetrySameKey, setCanRetrySameKey] = useState<boolean>(false);
  const [idempotencyKey, setIdempotencyKey] = useState<string | null>(null);

  // 1. Load movies on mount
  useEffect(() => {
    setLoadingMovies(true);
    fetchMovies()
      .then((res) => {
        if (res.ok && res.data) {
          setMovies(res.data);
          if (res.data.length > 0) {
            const inCity = res.data.find((m) =>
              m.cities.includes(DEFAULT_CITIES[0]),
            );
            setSelectedMovieId((inCity ?? res.data[0]).id);
          }
        } else {
          setErrorMsg(res.error || "Failed to load movies");
        }
      })
      .catch(() => setErrorMsg("Unable to reach backend API"))
      .finally(() => setLoadingMovies(false));
  }, []);

  const cities = Array.from(new Set(movies.flatMap((m) => m.cities))).sort();
  const visibleMovies = movies.filter((m) => m.cities.includes(selectedCity));
  const selectedMovie =
    movies.find((m) => m.id === selectedMovieId) ?? null;

  // Ensure a valid movie in the current city is always selected
  useEffect(() => {
    if (
      visibleMovies.length > 0 &&
      !visibleMovies.some((m) => m.id === selectedMovieId)
    ) {
      setSelectedMovieId(visibleMovies[0].id);
    }
  }, [visibleMovies, selectedMovieId]);

  // 2. Load shows whenever selected movie or city changes
  useEffect(() => {
    if (!selectedMovieId || !selectedCity) return;

    setShows([]);
    setSelectedShowId("");
    setShowDetail(null);
    setSelectedSeats([]);
    setErrorMsg(null);

    fetchShowsByMovieAndCity(selectedMovieId, selectedCity).then((res) => {
      if (res.ok && res.data) {
        const nowUtc = Date.now();
        const upcomingShows = res.data.filter(
          (show) =>
            show.status === "SCHEDULED" &&
            parseUtcMillis(show.start_time) > nowUtc,
        );
        setShows(upcomingShows);
        if (upcomingShows.length > 0) {
          setSelectedShowId(upcomingShows[0].id);
        }
      } else {
        setErrorMsg(res.error || "Failed to load shows");
      }
    });
  }, [selectedMovieId, selectedCity]);

  // 3. Load / refresh seat map for selected show
  const loadSeatAvailability = async (showId: string) => {
    const res = await fetchShowById(showId);
    if (res.ok && res.data) {
      const detail = res.data;
      setShowDetail(detail);

      // Remove any selected seat that is now BOOKED
      const bookedSet = new Set(
        detail.seats.filter((s) => s.status === "BOOKED").map((s) => s.seat),
      );
      setSelectedSeats((prev) => prev.filter((s) => !bookedSet.has(s)));

      // Update summary card count
      setShows((prev) =>
        prev.map((sh) =>
          sh.id === detail.id
            ? { ...sh, seats_available: detail.seats_available }
            : sh,
        ),
      );
    } else {
      setErrorMsg(res.error || "Failed to load seat availability");
    }
  };

  useEffect(() => {
    if (!selectedShowId) return;
    setSelectedSeats([]);
    setErrorMsg(null);
    setIdempotencyKey(null);
    setCanRetrySameKey(false);
    void loadSeatAvailability(selectedShowId);
  }, [selectedShowId]);

  const handleToggleSeat = (seatId: string) => {
    setErrorMsg(null);
    setIdempotencyKey(null);
    setCanRetrySameKey(false);
    setSelectedSeats((prev) =>
      prev.includes(seatId)
        ? prev.filter((s) => s !== seatId)
        : [...prev, seatId].sort(),
    );
  };

  // 4. Submit booking with Idempotency-Key -> route to /bookings/:bookingId
  const handleBookSeats = async (reuseKey = false) => {
    if (!selectedShowId || selectedSeats.length === 0) return;

    const keyToUse =
      reuseKey && idempotencyKey ? idempotencyKey : crypto.randomUUID();
    setIdempotencyKey(keyToUse);
    setSubmitting(true);
    setErrorMsg(null);
    setCanRetrySameKey(false);

    try {
      const res = await createBooking(
        {
          user_id: userId.trim(),
          show_id: selectedShowId,
          seats: selectedSeats,
        },
        keyToUse,
      );

      if (res.ok && res.data) {
        const createdBooking = res.data;
        setSelectedSeats([]);
        setIdempotencyKey(null);
        onBookingCreated(createdBooking);
      } else if (res.status === 409) {
        // HTTP 409 Conflict -> refresh seat map immediately
        setIdempotencyKey(null);
        setErrorMsg(
          `HTTP 409 Conflict: ${res.error}. Seat availability has been refreshed.`,
        );
        await loadSeatAvailability(selectedShowId);
      } else if (res.status === 503) {
        // HTTP 503 Uncertain outcome -> allow retry with the same Idempotency-Key
        setErrorMsg(`HTTP 503: ${res.error}`);
        setCanRetrySameKey(true);
      } else {
        setIdempotencyKey(null);
        setErrorMsg(`Error (${res.status}): ${res.error}`);
      }
    } catch {
      setErrorMsg(
        "Network error while creating booking. You can retry with the same key.",
      );
      setCanRetrySameKey(true);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100/80 py-8 text-slate-900">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <HeaderBar
          cities={cities}
          selectedCity={selectedCity}
          onSelectCity={setSelectedCity}
          userId={userId}
          onChangeUserId={(val) => {
            onChangeUserId(val);
            setIdempotencyKey(null);
          }}
          activeTab="book"
          onNavigateHome={() => {}}
          onNavigateMyBookings={onNavigateMyBookings}
        />

        {loadingMovies && (
          <div className="mb-6 rounded-2xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
            Loading movies...
          </div>
        )}

        <MovieGrid
          movies={visibleMovies}
          selectedCity={selectedCity}
          selectedMovieId={selectedMovieId}
          onSelectMovie={setSelectedMovieId}
        />

        <ShowSelector
          movie={selectedMovie}
          shows={shows}
          selectedShowId={selectedShowId}
          onSelectShow={setSelectedShowId}
          onRefreshSeats={() => void loadSeatAvailability(selectedShowId)}
        />

        {errorMsg && (
          <div
            role="alert"
            className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800"
          >
            <span>{errorMsg}</span>
            {canRetrySameKey && (
              <button
                type="button"
                onClick={() => void handleBookSeats(true)}
                disabled={submitting}
                className="rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-rose-500 disabled:opacity-50"
              >
                Retry Same Key
              </button>
            )}
          </div>
        )}

        {showDetail && (
          <SeatMap
            movie={selectedMovie}
            showDetail={showDetail}
            selectedSeats={selectedSeats}
            submitting={submitting}
            onToggleSeat={handleToggleSeat}
            onClearSeats={() => {
              setSelectedSeats([]);
              setIdempotencyKey(null);
            }}
            onSubmitBooking={() => void handleBookSeats(false)}
          />
        )}
      </div>
    </div>
  );
}
