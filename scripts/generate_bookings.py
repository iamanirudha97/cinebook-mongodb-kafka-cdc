import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import httpx


API_BASE_URL = "http://127.0.0.1:8000"
REQUESTS_FILE = Path(__file__).with_name("sample_booking_requests.json")
RANDOM_SEED = 42

TOTAL_SHOWS = 200
TOTAL_USERS = 500
DEFAULT_BOOKINGS = 100


def parse_start_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

    # The existing API returns UTC timestamps without an offset.
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def fetch_bookable_shows(client: httpx.Client) -> list[dict]:
    shows = []
    now = datetime.now(timezone.utc)

    for number in range(1, TOTAL_SHOWS + 1):
        show_id = f"SHW-{number:06d}"
        response = client.get(f"/shows/{show_id}")
        response.raise_for_status()

        show = response.json()

        if (
            show["status"] == "SCHEDULED"
            and parse_start_time(show["start_time"]) > now
            and show["seats_available"] > 0
        ):
            shows.append(show)

    return shows


def generate_requests(
    client: httpx.Client,
    count: int,
) -> list[dict]:
    rng = random.Random(RANDOM_SEED)
    shows = fetch_bookable_shows(client)

    # Each show maintains its own local planning inventory.
    inventories = {
        show["id"]: [
            seat["seat"]
            for seat in show["seats"]
            if seat["status"] == "AVAILABLE"
        ]
        for show in shows
    }

    requests = []

    for number in range(count):
        eligible = [
            show
            for show in shows
            if inventories[show["id"]]
        ]

        if not eligible:
            raise RuntimeError(
                "Insufficient available seats to plan "
                f"{count} bookings."
            )

        show = rng.choice(eligible)
        available = inventories[show["id"]]

        seat_count = min(rng.randint(1, 4), len(available))
        selected_seats = rng.sample(available, seat_count)

        # Prevent overlapping seats within the generated plan.
        selected_set = set(selected_seats)
        inventories[show["id"]] = [
            seat
            for seat in available
            if seat not in selected_set
        ]

        user_id = f"USR-{rng.randint(1, TOTAL_USERS):04d}"

        idempotency_key = str(
            uuid5(
                NAMESPACE_URL,
                f"cinebook-sample-{number}",
            )
        )

        requests.append(
            {
                "idempotency_key": idempotency_key,
                "body": {
                    "user_id": user_id,
                    "show_id": show["id"],
                    "seats": selected_seats,
                },
            }
        )

    return requests


def load_or_create_requests(
    client: httpx.Client,
    count: int,
) -> list[dict]:
    if REQUESTS_FILE.exists():
        with REQUESTS_FILE.open("r", encoding="utf-8") as file:
            requests = json.load(file)

        if len(requests) != count:
            raise ValueError(
                f"Saved plan contains {len(requests)} requests, "
                f"but --count={count}. Use the original count "
                "when replaying."
            )

        print(f"Loaded {len(requests)} saved requests.")
        return requests

    requests = generate_requests(client, count)

    # Exclusive creation prevents overwriting an existing plan.
    with REQUESTS_FILE.open("x", encoding="utf-8") as file:
        json.dump(requests, file, indent=2)
        file.write("\n")

    print(f"Saved {len(requests)} requests to {REQUESTS_FILE}")
    return requests


def submit_requests(
    client: httpx.Client,
    requests: list[dict],
) -> None:
    created = 0
    replayed = 0
    conflicts = 0
    failed = 0

    for number, request in enumerate(requests, start=1):
        try:
            response = client.post(
                "/bookings",
                json=request["body"],
                headers={
                    "Idempotency-Key": request["idempotency_key"]
                },
            )

        except httpx.RequestError as exc:
            failed += 1
            print(f"Request {number}: network error: {exc}")
            continue

        if response.status_code == 201:
            created += 1

        elif response.status_code == 200:
            replayed += 1

        elif response.status_code == 409:
            conflicts += 1
            print(
                f"Request {number}: conflict: "
                f"{response.text}"
            )

        else:
            failed += 1
            print(
                f"Request {number}: HTTP "
                f"{response.status_code}: {response.text}"
            )

    print("\nBooking generation summary")
    print(f"Planned:   {len(requests)}")
    print(f"Created:   {created}")
    print(f"Replayed:  {replayed}")
    print(f"Conflicts: {conflicts}")
    print(f"Failed:    {failed}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate CineBook sample bookings via FastAPI."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_BOOKINGS,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
    )
    parser.add_argument(
        "--api-url",
        default=API_BASE_URL,
    )

    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    with httpx.Client(
        base_url=args.api_url,
        timeout=30.0,
    ) as client:
        requests = load_or_create_requests(client, args.count)

        if args.dry_run:
            print("\nDry run: no bookings submitted.")
            print(f"Planned bookings: {len(requests)}")
            print("First three requests:")

            for request in requests[:3]:
                print(json.dumps(request, indent=2))

            return

        submit_requests(client, requests)


if __name__ == "__main__":
    main()
