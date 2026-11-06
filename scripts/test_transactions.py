import os
from uuid import uuid4

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(
    os.environ["MONGODB_URI"],
    serverSelectionTimeoutMS=10000,
)

db = client[os.getenv("MONGODB_DB", "cinebook")]

# Temporary collections, separate from application data
shows = db["_test_txn_shows"]
bookings = db["_test_txn_bookings"]

test_id = str(uuid4())


def count_documents():
    query = {"test_id": test_id}
    return (
        shows.count_documents(query),
        bookings.count_documents(query),
    )


def insert_pair(session):
    shows.insert_one(
        {"test_id": test_id, "seat": "A1"},
        session=session,
    )
    bookings.insert_one(
        {"test_id": test_id, "booking": "BKG-TEST"},
        session=session,
    )


try:
    client.admin.command("ping")

    # Test 1: Successful transaction
    with client.start_session() as session:
        with session.start_transaction():
            insert_pair(session)

    assert count_documents() == (1, 1)
    print("PASS: Committed transaction saved both documents")

    # Remove test documents before the next test
    shows.delete_many({"test_id": test_id})
    bookings.delete_many({"test_id": test_id})

    # Test 2: Explicit rollback
    with client.start_session() as session:
        session.start_transaction()
        try:
            insert_pair(session)
        finally:
            session.abort_transaction()

    assert count_documents() == (0, 0)
    print("PASS: Aborted transaction saved neither document")

    # Test 3: Second write fails
    with client.start_session() as session:
        try:
            with session.start_transaction():
                shows.insert_one(
                    {"test_id": test_id, "seat": "A2"},
                    session=session,
                )

                # Missing required _id value is not an error,
                # so deliberately use an invalid document type.
                bookings.insert_one(
                    "invalid document",
                    session=session,
                )
        except TypeError:
            pass

    assert count_documents() == (0, 0)
    print("PASS: Failed second write rolled back the first")

finally:
    shows.delete_many({"test_id": test_id})
    bookings.delete_many({"test_id": test_id})
    client.close()