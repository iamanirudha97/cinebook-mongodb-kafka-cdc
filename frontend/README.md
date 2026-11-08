# CineBook Frontend (Part F)

React + TypeScript + Vite frontend using Material UI (MUI), Tailwind CSS, and the Fetch API.

## Folder Structure

```text
frontend/
├── .env.example
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
    ├── config/
    │   └── env.ts                          # Environment variable & default constants
    ├── types/
    │   └── cinebook.ts                     # TypeScript interfaces matching FastAPI Pydantic schemas
    ├── services/
    │   ├── httpClient.ts                   # Shared functional fetch wrapper
    │   ├── movieService.ts                 # GET /movies
    │   ├── showService.ts                  # GET /shows, GET /shows/{show_id}
    │   └── bookingService.ts               # POST /bookings with Idempotency-Key
    ├── utils/
    │   └── formatters.ts                   # Date, currency, and seat-row grouping helpers
    ├── components/
    │   ├── layout/
    │   │   └── HeaderBar.tsx               # App header with City and User ID controls
    │   ├── movies/
    │   │   └── MovieGrid.tsx               # Movie selection cards
    │   ├── shows/
    │   │   └── ShowSelector.tsx            # Showtime selection cards
    │   ├── seats/
    │   │   └── SeatMap.tsx                 # Interactive seat grid & checkout summary
    │   └── booking/
    │       └── BookingConfirmationCard.tsx # Confirmed booking banner
    ├── pages/
    │   └── BookingPage.tsx                 # Main page container
    ├── App.tsx
    ├── main.tsx
    └── index.css
```

## Setup & Run Instructions

1. **Create `.env` from `.env.example`:**
   ```bash
   cd frontend
   cp .env.example .env
   ```
   By default `VITE_API_BASE_URL=/api` uses Vite's dev proxy (`vite.config.ts`) to forward requests to `http://127.0.0.1:8000` so no CORS changes are needed in `backend/`.

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   Make sure the FastAPI backend is running on port 8000 (`uv run uvicorn backend.app.main:app --reload`), then run:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173`.

4. **Type-check and build for production:**
   ```bash
   npm run build
   ```
