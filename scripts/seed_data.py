"""Idempotently seed CineBook's initial functional dataset (no bookings)."""
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import TypedDict

from dotenv import load_dotenv
from faker import Faker
from pymongo import MongoClient, UpdateOne

class ShowSeed(TypedDict):
    _id: str
    movie_id: str
    theater_id: str
    screen_id: str
    city: str
    start_time: datetime
    status: str
    prices: dict[str, int]
    seats_total: int
    seats_available: int
    seats: list[dict[str, str]]


class MovieSeed(TypedDict):
    _id: str
    title: str
    language: str
    genres: list[str]
    duration_min: int
    certification: str
    release_date: datetime
    cities: list[str]


CITIES = ("Delhi", "Mumbai", "Bengaluru")
IST = ZoneInfo("Asia/Kolkata")
MOVIE_TITLES = (
    "Dune: Part Two", "Oppenheimer", "Jawan", "Kantara", "RRR",
    "The Last Horizon", "Monsoon Express", "City of Dreams", "Northern Lights",
    "The Hidden Valley", "Midnight Journey", "Beyond the River", "Parallel Lives",
    "The Final Signal", "Golden Hour", "Crossroads", "The Long Road",
    "Echoes of Tomorrow", "The Silent Witness", "Rising Tide",
)
MOVIE_IDS = (
    "MOV-DUNE2", "MOV-OPPENHEIMER", "MOV-JAWAN", "MOV-KANTARA", "MOV-RRR",
) + tuple(f"MOV-DEMO-{i:02d}" for i in range(6, 21))
THEATER_IDS = tuple(f"THR-{city.upper()}" for city in CITIES) + tuple(
    f"THR-DEMO-{i:02d}" for i in range(4, 11)
)


def seat_layout(size: int) -> list[dict[str, str]]:
    """Return 50 or 100 seats, each with a category and initial status."""
    return [
        {"seat": f"{chr(65 + row)}{number}",
         "category": "PREMIUM" if row < 2 else "STANDARD",
         "status": "AVAILABLE"}
        for row in range(size // 10)
        for number in range(1, 11)
    ]


def main() -> None:
    load_dotenv()
    uri = os.getenv("MONGODB_ADMIN_URI") or os.getenv("MONGODB_URI")
    if not uri:
        raise SystemExit("Set MONGODB_ADMIN_URI or MONGODB_URI in .env")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000, tz_aware=True)
    try:
        client.admin.command("ping")
        db = client[os.getenv("MONGODB_DB", "cinebook")]
        if not {"movies", "theaters", "shows", "bookings", "users"}.issubset(db.list_collection_names()):
            raise RuntimeError("Run apply_validation.py before seeding")

        fake = Faker("en_IN")
        fake.seed_instance(42)
        today = datetime.now(IST).date()
        theater_cities = [CITIES[i % 3] for i in range(10)]
        # Every movie appears in multiple cities. References are deterministic.
        shows: list[ShowSeed] = []
        for i in range(200):
            movie_idx = i % 20
            theater_idx = (i // 20 + movie_idx) % 10
            city = theater_cities[theater_idx]
            # For each theater, unique (day, hour) slots; no screen collisions.
            theater_show_number = i // 10
            day_offset = 1 + theater_show_number // 4
            hour = (10, 13, 17, 20)[theater_show_number % 4]
            local_start = datetime.combine(
                today + timedelta(days=day_offset),
                datetime.min.time(), tzinfo=IST,
            ).replace(hour=hour)
            size = 50 if i % 2 == 0 else 100
            shows.append({
                "_id": f"SHW-{i+1:06d}",
                "movie_id": MOVIE_IDS[movie_idx],
                "theater_id": THEATER_IDS[theater_idx],
                "screen_id": "SCR-1",
                "city": city,
                "start_time": local_start.astimezone(timezone.utc),
                "status": "SCHEDULED",
                "prices": {"STANDARD": 250, "PREMIUM": 400},
                "seats_total": size,
                "seats_available": size,
                "seats": seat_layout(size),
            })

        movie_cities: dict[str, list[str]] = {
            movie_id: sorted({s["city"] for s in shows if s["movie_id"] == movie_id})
            for movie_id in MOVIE_IDS
        }
        movies: list[MovieSeed] = [
            {"_id": movie_id, "title": title,
             "language": ("English", "Hindi", "Kannada", "Telugu")[i % 4],
             "genres": ["Drama", "Adventure"], "duration_min": 110 + (i % 7) * 10,
             "certification": "UA", "release_date": datetime(2024, 1, 1, tzinfo=timezone.utc),
             "cities": movie_cities[movie_id]}
            for i, (movie_id, title) in enumerate(zip(MOVIE_IDS, MOVIE_TITLES))
        ]
        theaters = []
        for i, theater_id in enumerate(THEATER_IDS):
            city = theater_cities[i]
            theaters.append({
                "_id": theater_id,
                "name": f"CineBook {city} {i+1}",
                "city": city,
                "screens": [{"screen_id": "SCR-1", "name": "Screen 1",
                             "rows": list("ABCDEFGHIJ"), "seats_per_row": 10,
                             "categories": {"A-B": "PREMIUM", "C-J": "STANDARD"}}],
            })
        now = datetime.now(timezone.utc)
        users = [
            {"_id": f"USR-{i:04d}", "name": fake.name(),
             "email": f"user{i:04d}@example.com",
             "city": fake.random_element(elements=CITIES), "created_at": now}
            for i in range(1, 501)
        ]

        for collection, docs in (("movies", movies), ("theaters", theaters),
                                 ("shows", shows), ("users", users)):
            # Only insert absent documents; never reset booked seats or existing metadata.
            result = db[collection].bulk_write([
                UpdateOne({"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True)
                for doc in docs
            ], ordered=False)
            print(f"{collection}: {len(docs)} target, {result.upserted_count} newly inserted")
        print(f"bookings: {db.bookings.count_documents({})} (untouched)")
        print("Seed complete. Existing documents were not overwritten.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
