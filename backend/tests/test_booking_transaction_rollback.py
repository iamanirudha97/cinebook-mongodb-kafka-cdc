import asyncio
from uuid import uuid4

from pymongo.errors import DuplicateKeyError

from backend.app.db.mongodb import mongodb
from backend.app.repositories.booking_repository import BookingRepository


SHOW_ID = "SHW-000002"
SEATS = ["B1", "B2"]


async def main() -> None:
    await mongodb.connect()

    try:
        db = mongodb.get_database()
        repository = BookingRepository(db)

        show_before = await repository.get_show(SHOW_ID)
        assert show_before is not None, "Show not found"

        selected_before = {
            seat["seat"]: seat
            for seat in show_before["seats"]
            if seat["seat"] in SEATS
        }

        assert set(selected_before) == set(SEATS), (
            "One or more test seats do not exist"
        )
        assert all(
            seat["status"] == "AVAILABLE"
            for seat in selected_before.values()
        ), "Test seats must be available"

        available_before = show_before["seats_available"]
        booking_id = f"BKG-{uuid4().hex}"

        print("BEFORE TRANSACTION")
        print("Available seats:", available_before)
        print("Test seats:", SEATS)

        client = db.client

        try:
            async with client.start_session() as session:
                async with await session.start_transaction():
                    result = await repository.reserve_seats(
                        show_id=SHOW_ID,
                        seat_ids=SEATS,
                        booking_id=booking_id,
                        session=session,
                    )

                    assert result.modified_count == 1, (
                        "Seat reservation failed"
                    )

                    print("\nSeat update succeeded inside transaction")

                    await repository.create_booking(
                        {
                            "_id": booking_id,
                            "invalid_field": "Force schema validation failure",
                        },
                        session=session,
                    )

            raise AssertionError(
                "Invalid booking insertion unexpectedly succeeded"
            )

        except Exception as exc:
            if isinstance(exc, AssertionError):
                raise

            print("Booking insertion failed:", type(exc).__name__)

        show_after = await repository.get_show(SHOW_ID)
        assert show_after is not None

        booking_after = await db["bookings"].find_one(
            {"_id": booking_id}
        )

        selected_after = {
            seat["seat"]: seat
            for seat in show_after["seats"]
            if seat["seat"] in SEATS
        }

        print("\nAFTER TRANSACTION")
        for seat_id in SEATS:
            seat = selected_after[seat_id]
            print(
                seat_id,
                seat["status"],
                seat.get("booking_id"),
            )

        print("Available seats:", show_after["seats_available"])
        print("Booking exists:", booking_after is not None)

        assert all(
            seat["status"] == "AVAILABLE"
            and seat.get("booking_id") is None
            for seat in selected_after.values()
        ), "Seat changes were not rolled back"

        assert show_after["seats_available"] == available_before, (
            "Seat inventory was not restored"
        )

        assert booking_after is None, (
            "Invalid booking was unexpectedly persisted"
        )

        print("\nPASS: Transaction rollback verified")

    finally:
        await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
