import asyncio
from uuid import uuid4

import httpx

from backend.app.db.mongodb import mongodb


BASE_URL = "http://127.0.0.1:8000"
SHOW_ID = "SHW-000002"
USER_ID = "USR-0001"
SEATS = ["A8", "A9"]


async def main() -> None:
    idempotency_key = str(uuid4())

    headers = {"Idempotency-Key": idempotency_key}
    payload = {
        "user_id": USER_ID,
        "show_id": SHOW_ID,
        "seats": SEATS,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        async def book(name: str) -> tuple[str, int, dict]:
            response = await client.post(
                f"{BASE_URL}/bookings",
                headers=headers,
                json=payload,
            )
            return name, response.status_code, response.json()

        results = await asyncio.gather(
            book("Request 1"),
            book("Request 2"),
        )

    print("\nHTTP RESULTS")
    for name, status, body in results:
        print(f"{name}: HTTP {status}")
        print(body)

    await mongodb.connect()
    try:
        db = mongodb.get_database()

        show = await db["shows"].find_one({"_id": SHOW_ID})
        assert show is not None, f"Show {SHOW_ID} not found"

        bookings = await db["bookings"].find(
            {
                "user_id": USER_ID,
                "idempotency_key": idempotency_key,
            }
        ).to_list(length=3)

        print("\nDATABASE RESULTS")
        for seat in show["seats"]:
            if seat["seat"] in SEATS:
                print(
                    seat["seat"],
                    seat["status"],
                    seat.get("booking_id"),
                )

        print("Bookings created:", len(bookings))
        print("Seats available:", show["seats_available"])

        assert len(bookings) == 1, (
            "Expected exactly one booking document"
        )

        booking = bookings[0]
        assert set(booking["seats"]) == set(SEATS)

        for seat in show["seats"]:
            if seat["seat"] in SEATS:
                assert seat["status"] == "BOOKED"
                assert seat.get("booking_id") == booking["_id"]

        available_count = sum(
            seat["status"] == "AVAILABLE"
            for seat in show["seats"]
        )
        assert show["seats_available"] == available_count

        statuses = sorted(
            status for _, status, _ in results
        )
        assert statuses == [200, 201], (
            f"Unexpected HTTP statuses: {statuses}"
        )

        for _, _, body in results:
            assert body["id"] == booking["_id"]

        print("\nPASS: Concurrent idempotency verified")

    finally:
        await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
