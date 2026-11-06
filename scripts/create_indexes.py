"""Create and verify CineBook indexes. Safe to rerun with unchanged definitions."""

import os
from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient

load_dotenv()

# Explicit names make the indexes easy to inspect in Atlas and in explain plans.
INDEXES = {
    "movies": [
        ([("cities", ASCENDING), ("language", ASCENDING)], "idx_movies_cities_language", False),
    ],
    "theaters": [
        ([("city", ASCENDING)], "idx_theaters_city", False),
    ],
    "shows": [
        ([("movie_id", ASCENDING), ("city", ASCENDING), ("start_time", ASCENDING)], "idx_shows_movie_city_start", False),
    ],
    "bookings": [
        ([("user_id", ASCENDING), ("created_at", DESCENDING)], "idx_bookings_user_created", False),
        ([("user_id", ASCENDING), ("idempotency_key", ASCENDING)], "uq_bookings_user_idempotency", True),
        ([("show_id", ASCENDING)], "idx_bookings_show", False),
    ],
}


def main() -> None:
    uri = os.getenv("MONGODB_ADMIN_URI")
    if not uri:
        raise SystemExit("Set MONGODB_ADMIN_URI in .env before creating indexes.")

    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    try:
        client.admin.command("ping")
        db = client[os.getenv("MONGODB_DB", "cinebook")]
        existing_collections = set(db.list_collection_names())
        missing = set(INDEXES) - existing_collections
        if missing:
            raise RuntimeError(f"Missing collections: {', '.join(sorted(missing))}. Run apply_validation.py first.")

        for collection_name, definitions in INDEXES.items():
            collection = db[collection_name]
            for keys, name, unique in definitions:
                try:
                    collection.create_index(keys, name=name, unique=unique)
                    actual = collection.index_information().get(name)
                    if not actual:
                        raise RuntimeError("Index was not found after creation")
                    if list(actual["key"]) != list(keys) or bool(actual.get("unique", False)) != unique:
                        raise RuntimeError("Existing index definition differs from requested definition")
                    print(f"PASS: {collection_name}.{name} (unique={unique})")
                except Exception as exc:
                    raise RuntimeError(f"Failed to create or verify {collection_name}.{name}") from exc
        print("PASS: all six CineBook indexes verified")
    finally:
        client.close()


if __name__ == "__main__":
    main()
