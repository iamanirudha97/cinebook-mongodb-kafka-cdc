# CineBook — Implementation Plan for Antigravity

**Project:** CineBook — End-to-End Movie Booking Platform with MongoDB Atlas, FastAPI & Kafka CDC  
**Repository:** `cinebook-mongodb-kafka-cdc`  
**Source of requirements:** `MongoDB_Assignment.pdf` (10 pages). It is kept in the repo root locally only and **excluded from Git**, since it is third-party course material. **Read the PDF before implementing.** This plan puts Parts A–F into practice, with only the agreed reliability fixes.  
**Design source of truth:** `docs/data_model.md` (Revision 2, approved). Where this plan and the design doc differ on modeling details, the design doc wins.  
**Status:** Phase A complete (design approved). Phase B **not started**: it waits for explicit approval. Tick tasks off only after they are verified.

## 0. Operating instructions for the coding agent

1. Implement **one phase at a time**, in the order below. Do not build the whole project in one pass. At the end of each phase, report the files changed, commands to run, test evidence, blockers and any design decisions, then **wait for user approval** before starting the next phase. Do not create files belonging to a later phase in advance.
2. Stay within the assignment. The only intentional deviations are:
   - **React + TypeScript + Vite** for the simple frontend;
   - fixes for **booking-record consistency** (transaction, collision-resistant IDs, safe retries via `Idempotency-Key`);
   - **duplicate-safe CDC handling**.
   No authentication system, payment gateway, Kubernetes, warehouse, microservices, elaborate observability stack, or unrelated features.
3. Stack: **Python 3.12, FastAPI, PyMongo** (sync PyMongo in sync route handlers is fine), **MongoDB Atlas M0**, **Confluent Cloud Kafka**, `confluent-kafka`, React, TypeScript and Vite. Use minimal styling; do not introduce Tailwind unless explicitly approved.
4. **Python tooling is uv only.** There is one root-level uv project (`pyproject.toml`, `uv.lock`, `.python-version` pinned to 3.12).
   - Add dependencies with `uv add <pkg>`, and dev dependencies with `uv add --dev <pkg>`.
   - Run every Python command **from the repository root** with `uv run …`.
   - No `requirements.txt`, no `pip install`, no manual `python -m venv` or `source .venv/bin/activate`. uv manages `.venv/` itself.
5. **The frontend uses npm** inside `frontend/`, with its own `package.json` and `package-lock.json`.
6. Keep credentials in environment variables and commit only `.env.example`. Never log secrets. Never commit `.env`, `.venv/`, connector credentials or the assignment PDF. Ask the user to provision cloud resources manually; do not claim to have done so. Never ask for secrets in chat.
7. Provide commands and expected outputs for macOS local development. Use **deterministic** seed data and UTC-aware BSON dates. Setup scripts must be **idempotent**: safe to re-run without duplicating data or clobbering live booking state.
8. Do not invent benchmark numbers, test results, connector availability or screenshots. If a cloud limitation blocks a step, explain it and propose the **assignment-permitted** fallback before changing the architecture.
9. Treat the PDF's illustrative snippets as hints, not correct implementations. In particular, a successful seat update followed by a failed booking insert is an inconsistency, and the transaction design addresses it.

## 1. Architecture and scope

```text
React + TypeScript + Vite (local browser, npm)
          | HTTP (Idempotency-Key on POST /bookings)
          v
FastAPI backend (local, uv run)
          | PyMongo (transactions, majority writes)
          v
MongoDB Atlas M0 / cinebook
  movies | theaters | shows | bookings | users
          | bookings change stream (committed writes only)
          v
Confluent Cloud MongoDB Atlas Source Connector
          |
          v
Kafka topic: cdc.cinebook.bookings
          |
          v
Python Kafka consumer (local, uv run)
```

Required assignment capabilities:
- **Part A:** embed/reference decisions, atomic seat design, `_id` choices, denormalization trade-offs. Done in `docs/data_model.md`.
- **Part B:** Atlas database, seed data, `$jsonSchema` validation on `shows` and `bookings`, ESR indexes, README index mapping.
- **Part C:** REST APIs, concurrency-safe all-or-nothing multi-seat reservation, consistent booking persistence.
- **Part D:** four aggregation pipelines and `explain("executionStats")` evidence before and after indexing.
- **Part E:** managed MongoDB Atlas Source Connector to Confluent Cloud, Kafka consumer, CDC delivery semantics and example events. Use the PDF's self-managed Dockerized Kafka Connect fallback **only if necessary**, with approval, and document it.
- **Part F:** minimal frontend. **React replaces the assignment's HTML/JS or Streamlit suggestion.**
- **Part G:** optional bonuses, **out of scope initially**.

## 2. Repository layout

```text
cinebook-mongodb-kafka-cdc/
├── pyproject.toml              # single root uv project (all Python deps)
├── uv.lock                     # committed
├── .python-version             # 3.12
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── api/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
│       ├── conftest.py
│       ├── test_concurrency.py
│       └── test_booking_consistency.py
├── frontend/                   # npm project (React + TS + Vite)
│   ├── src/
│   ├── package.json
│   └── package-lock.json
├── scripts/
│   ├── _common.py              # env loading, client, shared invariant checks
│   ├── schemas.py              # $jsonSchema definitions
│   ├── test_atlas_connection.py
│   ├── smoke_test_transactions.py
│   ├── apply_validation.py
│   ├── seed_data.py
│   ├── create_indexes.py
│   ├── check_setup.py
│   ├── generate_bookings.py    # after Phase C: ~100 bookings via the API
│   └── cdc_update_booking.py   # Phase E: controlled CDC update events
├── analytics/
│   └── aggregations.py
├── kafka/
│   ├── connector_config.example.json
│   └── consumer.py
├── docs/
│   ├── architecture.md
│   ├── data_model.md
│   ├── atlas_setup.md
│   └── evidence/
├── .env.example
├── .gitignore                  # excludes .env, .venv/, MongoDB_Assignment*.pdf
├── README.md
└── plan.md
```

Only change the internal module layout when there is a clear reason. Keep entry points and setup simple. Python packages are not installed into the project (`[tool.uv] package = false`). The backend is run with `--app-dir backend`, and pytest gets `pythonpath = ["backend"]` through `pyproject.toml`.

## 3. Setup and run commands (macOS)

Prerequisites: `uv` and Node.js/npm (Homebrew). uv downloads Python 3.12 itself if needed.

```bash
# One-time project bootstrap (Phase B, run by the agent once; later users just run `uv sync`)
uv init --bare --name cinebook       # creates pyproject.toml only
uv python pin 3.12                   # writes .python-version
uv add pymongo python-dotenv         # Phase B runtime deps
# Phase C: uv add fastapi "uvicorn[standard]" httpx ; uv add --dev pytest
# Phase E: uv add confluent-kafka

# Reproducing from a clone
uv sync                              # creates .venv/ from uv.lock
cp .env.example .env                 # then fill in values locally

# Phase B (from repo root)
uv run python scripts/test_atlas_connection.py
uv run python scripts/smoke_test_transactions.py
uv run python scripts/apply_validation.py
uv run python scripts/seed_data.py
uv run python scripts/create_indexes.py
uv run python scripts/check_setup.py

# Phase C
uv run uvicorn app.main:app --app-dir backend --reload
uv run pytest backend/tests

# After Phase C (API running)
uv run python scripts/generate_bookings.py

# Phase D / E
uv run python analytics/aggregations.py
uv run python kafka/consumer.py
uv run python scripts/cdc_update_booking.py --booking-id <BKG-…> --dry-run

# Phase F
cd frontend && npm install && npm run dev
```

Git hygiene (already verified with `git check-ignore`): `.env`, `.venv/` and `MongoDB_Assignment*.pdf` are ignored. `uv.lock`, `.python-version`, `pyproject.toml` and `frontend/package-lock.json` are committed.

## 4. Phase A — Data modeling ✅ (approved, `docs/data_model.md` Rev. 2)

- [x] Define the `movies`, `theaters`, `shows`, `bookings` and `users` document shapes, keeping the PDF's field names.
- [x] Embed screens in theaters; reference movie/theater/screen from shows; reference show and user from bookings. Justified.
- [x] Embed each show's seat inventory (`seats[]`, plus `seats_total` and `seats_available`) in the show document. Every show has independent availability.
- [x] Booking fields, statuses (`CONFIRMED`, `CANCELLED`), price snapshot, `created_at`, `idempotency_key`, denormalized show/movie fields.
- [x] **Atomic all-or-nothing conditional update** (`$all` + `$elemMatch` filter, `arrayFilters` update, show status and start time in the same filter), with the concurrency argument.
- [x] **Cross-document consistency:** one multi-document transaction (seat update + booking insert) is the primary strategy.
- [x] `_id` choices, denormalization and trade-offs documented.

**Finalized decisions carried into later phases:**
- **Booking IDs** are collision-resistant: `BKG-` + `secrets.token_hex(16)` (128-bit CSPRNG).
- **Uncertain commit outcomes:**
  - rely on `with_transaction` commit retries;
  - if the outcome is still unknown, read the booking back by `_id` from the primary with majority read concern; found → 201, otherwise **503** "retry with the same `Idempotency-Key`";
  - a required `Idempotency-Key` header plus a unique `(user_id, idempotency_key)` index makes client retries safe.
- **No compensation fallback** unless Atlas M0 transactions **fail** Phase B verification. In that case, stop and present a compensation design for approval before coding.
- **Non-bookable show** (cancelled or already started) → HTTP **409**.
- **`release_date`** is a BSON `Date`.
- **No cancellation endpoint.** CDC update events come from a controlled script (Phase E).
- **Separate DB users:** `cinebook_setup` (dbAdmin + readWrite on `cinebook`), `cinebook_app` (readWrite), `cinebook_connector` (read, Phase E).

## 5. Phase B — Atlas, connectivity, seeding, validation, indexes (estimated 2–3 hours)

**Do not start until explicitly approved.**

- [ ] Bootstrap the root uv project (`pyproject.toml`, `uv.lock`, `.python-version` = 3.12) and add the Phase B deps with `uv add`. Create `.env.example` with placeholders only.
- [ ] Write `docs/atlas_setup.md`, guiding the user through:
  - the M0 cluster, IP allowlist (own IP) and Compass connection;
  - creating the `cinebook_setup` and `cinebook_app` users;
  - filling in `.env` locally.
  Never ask for secrets in chat or source files.
- [ ] `scripts/test_atlas_connection.py`:
  - pings the cluster with both the setup and app URIs;
  - reports the server version and replica-set status (`hello.setName`);
  - confirms the target database name.
  It must not print the URI or credentials and must fail with a clear message if `.env` is missing or incomplete.
- [ ] `scripts/smoke_test_transactions.py` uses scratch collections and cleans up after itself. It checks that:
  - an aborted two-collection transaction persists nothing;
  - a transaction whose second write is rejected by a `$jsonSchema` validator rolls back its first write;
  - a committed `with_transaction` persists both writes.
  It prints PASS/FAIL per check. **If transactions fail, stop and report** (see the compensation rule in §4).
- [ ] `scripts/apply_validation.py`: idempotently create the five collections and apply the `$jsonSchema` validators for `shows` and `bookings`:
  - required fields, BSON types and status enums;
  - `booking_id` present if and only if a seat is `BOOKED`;
  - booking ID and `Idempotency-Key` formats.
  Create when missing, `collMod` when present. Support `--action warn|error`; the final state is `error`.
- [ ] `scripts/seed_data.py`: **deterministic** fixed lists, **idempotent** upserts by natural `_id`:
  - **4–5 movies**, **3 theaters** (Delhi, Mumbai, Bengaluru; 1–2 screens each), **12–15 future shows** spread over the next days at varied IST times (stored as UTC BSON `Date`, relative to the run date, no overlaps on the same screen), and **50 synthetic users** (`USR-0001`…`USR-0050`, `example.com` emails).
  - `movies.cities` is derived from the shows. `release_date`, `start_time` and `created_at` are BSON `Date`.
  - Validate `seats_total == len(seats)` and `seats_available == count(AVAILABLE)` for every show before insert and after seeding.
  - Never overwrite a show that has booked seats unless `--reset` is given. `--reset` also deletes all bookings to keep the data consistent. **No bookings are seeded.**
- [ ] `scripts/create_indexes.py`: idempotently create named compound indexes following the ESR order, with no redundant indexes:
  - shows browse (`movie_id`, `city`, `start_time`);
  - movies filter;
  - user booking history (`user_id`, `created_at`);
  - **unique** `(user_id, idempotency_key)`;
  - unique `users.email`;
  - analytics support.
  Support `--drop` for controlled before/after explain runs in Phase D.
- [ ] `scripts/check_setup.py`:
  - collection counts versus expected;
  - validators present with `validationAction: "error"`;
  - index list;
  - seat-counter invariants on all shows;
  - **invalid show and booking documents rejected** (error 121), with any test documents cleaned up.
- [ ] Record each index, the exact query it serves and its creation command (README section draft).
- [ ] Save real outputs of the connection test, transaction smoke test and setup check to `docs/evidence/`, with no secrets.

**Gate:**
- the connection test passes with both users;
- **all transaction smoke tests pass**, or the blocker is reported;
- seed counts are confirmed (4–5 / 3 / 12–15 / 50 / 0 bookings) and seat invariants hold;
- invalid documents are rejected;
- indexes are visible in Atlas/Compass;
- re-running every script is a no-op.

## 6. Phase C — FastAPI and safe booking (estimated 3–5 hours)

Implement and document:

| Method | Route | Behavior |
|---|---|---|
| GET | `/movies` | Optional city, language, genre filters |
| GET | `/movies/{movie_id}/shows` | Optional city and date filters |
| GET | `/shows/{show_id}/seats` | Current availability |
| POST | `/bookings` | Requires `Idempotency-Key` header. Atomically reserves all requested seats and creates the booking in one transaction |
| GET | `/bookings/{booking_id}` | Retrieve one booking |
| GET | `/users/{user_id}/bookings` | Retrieve booking history |
| GET | `/analytics/revenue` | One Part D aggregation exposed as an API |

- [ ] Add Phase C deps with `uv add` / `uv add --dev`. Run with `uv run uvicorn app.main:app --app-dir backend --reload`.
- [ ] Pydantic request/response models and clear HTTP errors:
  - 400 invalid request (incl. missing or malformed `Idempotency-Key`);
  - 404 missing show or user;
  - **409 seats unavailable or show not bookable**;
  - 422 idempotency key reused with a different payload;
  - 503 commit outcome unconfirmed.
- [ ] Reject duplicate seat IDs, unknown seats, empty selections, nonexistent show/user and non-bookable shows.
- [ ] Calculate the amount **on the server** from show prices and seat categories. Never trust client-provided amounts.
- [ ] Reserve seats with the single conditional update (data_model.md §4.1). No read-then-write availability checks.
- [ ] Wrap the seat update and booking insert in `with_transaction` (snapshot read concern, majority write concern). Booking IDs are `BKG-` + `secrets.token_hex(16)`.
- [ ] Handle uncertain commits: read back by `_id` → 201 if present, else 503 with the booking ID and retry instructions. Idempotent replay with the same key returns the original booking (200).
- [ ] `pytest` + HTTPX tests with a clean, isolated show fixture:
  - 50–100 simultaneous attempts for one seat → exactly one success;
  - deliberate booking-insert failure → seats remain `AVAILABLE`, no booking;
  - the same `Idempotency-Key` retried (sequentially and concurrently) → exactly one booking;
  - key reuse with a different payload → 422;
  - seat invariants and booking↔seat cross-check hold after every test.
  These tests are an **agreed additional verification**, not a PDF-mandated framework.
- [ ] Document example requests and responses, idempotency/retry behavior and booking consistency.

**Gate:**
- all endpoints exercised;
- the concurrency, failure-injection and idempotency tests pass;
- invariants hold;
- no compensation code exists (unless approved after a Phase B transaction failure).

## 7. Phase D — Sample bookings, aggregations and performance (estimated 2–3 hours)

- [ ] **Sample bookings via the API:** `scripts/generate_bookings.py` creates **about 100 bookings** by calling `POST /bookings` on the running FastAPI server, **never by inserting into MongoDB directly**.
  - `random.Random(42)` chooses the user, a weighted show and 1–4 available seats.
  - Each request's `Idempotency-Key` is `uuid5(namespace, "cinebook-sample-<n>")`, so re-running replays instead of duplicating.
  - After generation, run the invariant and booking↔seat cross-check.

Implement MongoDB aggregation pipelines for:

- [ ] Revenue per movie (confirmed bookings only; at least one pipeline shows the PDF's shows→movies join).
- [ ] Occupancy per show (booked seats / total seats).
- [ ] Top movies by tickets sold or revenue.
- [ ] Peak showtime hours by bookings or revenue (hour in `Asia/Kolkata`).
- [ ] Put an indexed `$match` early and use a minimal `$project` where appropriate. Explain blocking stages such as `$group`.
- [ ] Capture **real** `explain("executionStats")` evidence for representative hot queries before and after indexing: `COLLSCAN` vs `IXSCAN`, documents and keys examined, and any avoidable `SORT`. Use a **controlled comparison** (`create_indexes.py --drop` for only the relevant index, record the baseline, recreate). Do not fake before/after output.
- [ ] Add the `/analytics/revenue` route backed by an actual pipeline.

**Gate:** about 100 API-created bookings exist with invariants holding; aggregations match hand-checked totals; saved query plans come from real executions.

## 8. Phase E — MongoDB CDC to Kafka (estimated 3–5 hours)

- [ ] Ask the user to provision a Confluent Cloud Kafka cluster, API key and topic `cdc.cinebook.bookings`, after checking cost/trial and connector availability.
- [ ] Ask the user to create the read-only `cinebook_connector` Atlas user (`read@cinebook`). Its credentials go only into the Confluent Cloud UI.
- [ ] Configure the managed **MongoDB Atlas Source Connector** to watch `cinebook.bookings`. Keep a placeholder-only config in `kafka/connector_config.example.json`. Configure Atlas network access as narrowly as possible, and remove any temporary broad access after testing.
- [ ] **Insert events:** create bookings through the FastAPI API.
- [ ] **Update events:** `scripts/cdc_update_booking.py`, a controlled script (**no cancellation endpoint**):
  - explicit `--booking-id` only, with `--dry-run`;
  - in one transaction, sets the booking to `CANCELLED` with `cancelled_at` and releases exactly the seats stamped with that ID;
  - refuses bookings that are already cancelled or whose seats don't match;
  - invariants hold afterwards.
- [ ] Verify the events in the Confluent Cloud console.
- [ ] Add `confluent-kafka` with `uv add`. Write `kafka/consumer.py` with safe config, graceful shutdown, event logging and explicit offset behavior.
- [ ] In the README, explain the event structure (`operationType`, `fullDocument`, resume token), at-least-once delivery, retries and practical downstream use cases. **Inspect the actual connector output format**, which may wrap or transform the change stream fields; do not assume an event shape without checking.
- [ ] **Duplicate-safe handling:** the required consumer only prints events, so duplicates are harmless when no counts are kept. If any local state is added, deduplicate by a stable event identity or make state updates idempotent, and commit offsets only after successful processing. Do not add the optional live aggregate just to demonstrate deduplication.
- [ ] If the managed connector is incompatible with the Atlas free tier or region, report the blocker and get approval before using the PDF-permitted Dockerized Kafka Connect fallback.

**Gate:** an API-created booking (insert) and a script-driven cancellation (update) both appear in Kafka; the consumer receives them; sample events and delivery notes are documented.

## 9. Phase F — React frontend (estimated 2–3 hours)

- [ ] Scaffold React + TypeScript + Vite in `frontend/` with **npm**, minimal CSS and an environment-based API base URL (`VITE_API_BASE_URL`).
- [ ] Movie listing/filtering and show selection.
- [ ] Seat map showing AVAILABLE vs BOOKED, with selectable seats and a price summary (display only; the server computes the amount).
- [ ] Booking submission with one `Idempotency-Key` per "Book" action, reused on retry. Success/confirmation view.
- [ ] Handle 409 (seat taken or show not bookable) and 503 (retry with the same key).
- [ ] Refresh availability after conflicts and avoid presenting stale seats as guaranteed.
- [ ] Keep the frontend intentionally simple; the assignment prioritizes backend and data engineering.

**Gate:** a user can browse, select seats, book, and see accurate success and conflict feedback in the browser.

## 10. Final verification and deliverables (estimated 2–3 hours)

- [ ] Run the complete end-to-end flow: frontend → FastAPI → Atlas → connector → Kafka → consumer.
- [ ] Capture real evidence in `docs/evidence/`: a successful booking, a rejected double-booking, an idempotent replay, analytics output, Kafka insert and update events, and before/after explain output.
- [ ] Write the README:
  - prerequisites (uv, Node/npm, Atlas, Confluent), environment variables, and `uv sync` / `uv run` / `npm` setup and run steps;
  - API reference (incl. `Idempotency-Key`);
  - data-modeling rationale, index/query mapping, explain evidence;
  - concurrency and consistency explanation (transaction, unknown commits, retries);
  - CDC configuration, event examples, delivery semantics;
  - limitations, and teardown/cost precautions.
- [ ] Include an accurate architecture diagram and the connector config with placeholders.
- [ ] Verify a clean repo: `git status`, secret scan/review, confirm `.env`, `.venv/` and the PDF are not tracked, `uv sync` from a fresh clone works, scripts run.
- [ ] State explicitly what is **not** implemented (e.g. payment processing, authentication, TTL holds, live aggregate, cancellation API).

**Gate:** another engineer can reproduce the project from the README with `uv sync` and `npm install`, without private credentials in the repository.

## 11. Final acceptance checklist

- [ ] Assignment Parts A–F satisfied (React substitution documented).
- [ ] All five collections present with documented relationships.
- [ ] Validations and relevant ESR indexes active.
- [ ] All six booking/browsing API routes plus one analytics route working.
- [ ] Multi-seat bookings are all-or-nothing; no double booking under concurrency.
- [ ] Booking documents and seat state stay consistent under tested failures; retries with the same `Idempotency-Key` never create duplicates.
- [ ] Seed data is deterministic and setup scripts are idempotent; about 100 sample bookings were created through the API.
- [ ] Four aggregation pipelines return correct results.
- [ ] Real before/after `explain` evidence included.
- [ ] Managed connector (or a documented, approved fallback) delivers booking insert and update events to Kafka.
- [ ] Python consumer works; delivery and duplicate semantics are explained.
- [ ] React UI handles success, seat conflicts and retryable errors.
- [ ] README, architecture diagram, screenshots and placeholder-only config committed. `.env`, `.venv/` and the assignment PDF are not tracked.

## 12. Next instruction to Antigravity

> Read `plan.md`, `docs/data_model.md` (Rev. 2) and the assignment PDF. Phase A is approved. **When I explicitly approve Phase B, execute Phase B only:** bootstrap the root uv project (Python 3.12, `uv add`), write `docs/atlas_setup.md`, and implement `test_atlas_connection.py`, `smoke_test_transactions.py`, `apply_validation.py`, `seed_data.py`, `create_indexes.py` and `check_setup.py` as specified in §5. Run everything with `uv run` from the repo root. Seed data must be deterministic and scripts idempotent; do not seed bookings. If the transaction smoke test fails, stop and report before designing any compensation. **Do not start Phase C until I review the Phase B evidence and approve.**
