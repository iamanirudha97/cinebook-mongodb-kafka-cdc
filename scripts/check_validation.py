"""Verify CineBook MongoDB collection validators without changing application data."""

import os
from uuid import uuid4

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure

COLLECTIONS = ("movies", "theaters", "shows", "bookings", "users")


def main() -> None:
    load_dotenv()
    uri = os.getenv("MONGODB_ADMIN_URI")
    if not uri:
        raise SystemExit("Set MONGODB_ADMIN_URI in .env first.")
    db_name = os.getenv("MONGODB_DB", "cinebook")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    try:
        db = client[db_name]
        for name in COLLECTIONS:
            info = list(db.list_collections(filter={"name": name}))
            if len(info) != 1:
                raise AssertionError(f"Missing collection: {name}")
            options = info[0].get("options", {})
            if (
                "$jsonSchema" not in options.get("validator", {})
                or options.get("validationLevel") != "strict"
                or options.get("validationAction") != "error"
            ):
                raise AssertionError(f"Validator missing or not strict: {name}")

            # Intentionally invalid: missing all required application fields.
            # A random _id avoids colliding with real documents.
            probe_id = f"VALIDATION-PROBE-{uuid4().hex}"
            try:
                db[name].insert_one({"_id": probe_id})
            except OperationFailure as exc:
                if exc.code != 121:  # DocumentValidationFailure
                    raise
            else:
                raise AssertionError(f"Invalid document accepted by {name}")
            finally:
                # Defensive cleanup if a server unexpectedly accepted the probe.
                db[name].delete_one({"_id": probe_id})
            print(f"PASS: {name} validator installed; invalid insert rejected")
        print("PASS: all five collection validators verified")
    finally:
        client.close()


if __name__ == "__main__":
    main()
