import { DEFAULT_CITIES } from "../../config/env";

interface HeaderBarProps {
  cities?: string[];
  selectedCity?: string;
  onSelectCity?: (city: string) => void;
  userId: string;
  onChangeUserId: (userId: string) => void;
  activeTab: "book" | "my-bookings";
  onNavigateHome: () => void;
  onNavigateMyBookings: () => void;
}

export function HeaderBar({
  cities = [],
  selectedCity,
  onSelectCity,
  userId,
  onChangeUserId,
  activeTab,
  onNavigateHome,
  onNavigateMyBookings,
}: HeaderBarProps) {
  const cityOptions = cities.length > 0 ? cities : DEFAULT_CITIES;

  return (
    <header className="mb-6 rounded-2xl border border-slate-200 bg-white px-6 py-4 shadow-xs">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div className="flex flex-wrap items-center gap-5">
          <button
            type="button"
            onClick={onNavigateHome}
            className="flex items-center gap-3 text-left focus:outline-none"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-sm font-bold tracking-tight text-white shadow-xs">
              CB
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-slate-900">
                CineBook
              </h1>
              <p className="text-xs text-slate-500">
                MongoDB Atlas + FastAPI + Confluent Kafka CDC
              </p>
            </div>
          </button>

          {/* Navigation Pills */}
          <nav className="flex items-center gap-1.5 rounded-xl bg-slate-100 p-1">
            <button
              type="button"
              onClick={onNavigateHome}
              className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
                activeTab === "book"
                  ? "bg-white text-indigo-600 shadow-2xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Book Tickets
            </button>
            <button
              type="button"
              onClick={onNavigateMyBookings}
              className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
                activeTab === "my-bookings"
                  ? "bg-white text-indigo-600 shadow-2xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              My Bookings
            </button>
          </nav>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {selectedCity !== undefined && onSelectCity && (
            <div className="flex items-center gap-2">
              <label
                htmlFor="city-select"
                className="text-xs font-medium text-slate-500"
              >
                City
              </label>
              <select
                id="city-select"
                value={selectedCity}
                onChange={(e) => onSelectCity(e.target.value)}
                className="rounded-lg border border-slate-300 bg-slate-50 px-3 py-1.5 text-sm font-medium text-slate-800 transition focus:border-indigo-500 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 focus:outline-none"
              >
                {cityOptions.map((city) => (
                  <option key={city} value={city}>
                    {city}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="flex items-center gap-2">
            <label
              htmlFor="user-id-input"
              className="text-xs font-medium text-slate-500"
            >
              User ID
            </label>
            <input
              id="user-id-input"
              type="text"
              value={userId}
              onChange={(e) => onChangeUserId(e.target.value.toUpperCase())}
              placeholder="USR-0001"
              className="w-32 rounded-lg border border-slate-300 bg-slate-50 px-3 py-1.5 font-mono text-sm font-medium text-slate-800 transition focus:border-indigo-500 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 focus:outline-none"
            />
          </div>
        </div>
      </div>
    </header>
  );
}
