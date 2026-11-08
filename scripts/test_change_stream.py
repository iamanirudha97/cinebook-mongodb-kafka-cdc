import asyncio

from backend.app.db.mongodb import mongodb


async def main() -> None:
    await mongodb.connect()

    try:
        database = mongodb.get_database()
        bookings = database["bookings"]

        print("Watching bookings collection for changes...")
        print("Create a booking through FastAPI to test CDC.")
        print("Press Ctrl+C to stop.\n")

        async with await bookings.watch(
            pipeline=[
                {
                    "$match": {
                        "operationType": {
                            "$in": ["insert", "update", "replace"]
                        }
                    }
                }
            ],
            full_document="updateLookup",
        ) as stream:
            async for change in stream:
                print("Change detected:")
                print("Operation:", change["operationType"])
                print("Document ID:", change["documentKey"]["_id"])
                print("Resume token:", change["_id"])
                print()

    finally:
        await mongodb.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nChange stream stopped.")
