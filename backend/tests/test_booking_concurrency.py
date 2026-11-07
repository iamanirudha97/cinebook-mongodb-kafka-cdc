
import asyncio
from uuid import uuid4

import httpx

from backend.app.db.mongodb import mongodb


BASE_URL = "http://127.0.0.1:8000"
SHOW_ID = "SHW-000002"


async def main() -> None:
    sam_key = str(uuid4())
    charlie_key = str(uuid4())

    requests = [
        {
            "name": "Sam",
            "user_id": "USR-0001",
            "seats": ["A3", "A4"],
            "key": sam_key,
        },
        {
            "name": "Charlie",
            "user_id": "USR-0002",
            "seats": ["A4", "A5"],
            "key": charlie_key,
        },
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:

        async def book(request: dict) -> tuple[str, int, dict]:
            response = await client.post(
                f"{BASE_URL}/bookings",
                headers={"Idempotency-Key": request["key"]},
                json={
                    "user_id": request["user_id"],
                    "show_id": SHOW_ID,
                    "seats": request["seats"],
                },
            )

            return (
                request["name"],
                response.status_code,
                response.json(),
            )

        results = await asyncio.gather(
            *(book(request) for request in requests)
        )

    print("\nHTTP RESULTS")
    for name, status, body in results:
        print(f"{name}: HTTP {status}")
        print(body)

    await mongodb.connect()

    try:
        db = mongodb.get_database()

        show = await db["shows"].find_one(
            {"_id": SHOW_ID}
        )

        assert show is not None, f"Show {SHOW_ID} not found"

        bookings = await db["bookings"].find(
            {
                "idempotency_key": {
                    "$in": [sam_key, charlie_key]
                }
            }
        ).to_list(length=2)

        print("\nDATABASE RESULTS")

        for seat in show["seats"]:
            if seat["seat"] in {"A3", "A4", "A5"}:
                print(
                    seat["seat"],
                    seat["status"],
                    seat.get("booking_id"),
                )

        print("Bookings created:", len(bookings))
        print("Seats available:", show["seats_available"])

        statuses = sorted(status for _, status, _ in results)

        assert statuses == [201, 409], (
            f"Unexpected HTTP results: {statuses}"
        )

        assert len(bookings) == 1, (
            "Expected exactly one booking document"
        )

        winner = bookings[0]
        assert set(winner["seats"]) in (
            {"A3", "A4"},
            {"A4", "A5"},
        )

        booked_seats = {
            seat["seat"]: seat
            for seat in show["seats"]
            if seat["seat"] in {"A3", "A4", "A5"}
            and seat["status"] == "BOOKED"
        }

        assert set(booked_seats) == set(winner["seats"]), (
            "Partial booking or incorrect seat reservation detected"
        )

        assert all(
            seat["booking_id"] == winner["_id"]
            for seat in booked_seats.values()
        )

        available_count = sum(
            seat["status"] == "AVAILABLE"
            for seat in show["seats"]
        )

        assert show["seats_available"] == available_count

        print("\nPASS: Atomic concurrent booking verified")

    finally:
        await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
