import asyncio
from typing import Any

from backend.app.db.mongodb import mongodb


SHOW_ID = "SHW-000002"
INDEX_NAME = "idx_bookings_show"


def get_execution_stats(result: dict[str, Any]) -> dict[str, Any]:
    stats = result["executionStats"]

    return {
        "execution_time_ms": stats["executionTimeMillis"],
        "documents_returned": stats["nReturned"],
        "documents_examined": stats["totalDocsExamined"],
        "index_keys_examined": stats["totalKeysExamined"],
    }


async def explain_query(
    hint: str | dict[str, int],
) -> dict[str, Any]:
    database = mongodb.get_database()

    command = {
        "explain": {
            "find": "bookings",
            "filter": {
                "show_id": SHOW_ID,
            },
            "hint": hint,
        },
        "verbosity": "executionStats",
    }

    result = await database.command(command)

    return get_execution_stats(result)


async def main() -> None:
    await mongodb.connect()

    try:
        collection_scan = await explain_query(
            {"$natural": 1}
        )

        index_scan = await explain_query(
            INDEX_NAME
        )

        print(f"\nQuery: show_id = {SHOW_ID}")
        print(f"Index: {INDEX_NAME}\n")

        print(f"{'Metric':<25} {'COLLSCAN':>12} {'IXSCAN':>12}")
        print("-" * 51)

        metrics = [
            ("Documents returned", "documents_returned"),
            ("Documents examined", "documents_examined"),
            ("Index keys examined", "index_keys_examined"),
            ("Execution time (ms)", "execution_time_ms"),
        ]

        for label, key in metrics:
            print(
                f"{label:<25} "
                f"{collection_scan[key]:>12} "
                f"{index_scan[key]:>12}"
            )

        baseline = collection_scan["documents_examined"]
        indexed = index_scan["documents_examined"]

        if baseline > 0:
            reduction = (baseline - indexed) / baseline * 100
            print(
                f"\nDocument examination reduction: "
                f"{reduction:.2f}%"
            )

    finally:
        await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
