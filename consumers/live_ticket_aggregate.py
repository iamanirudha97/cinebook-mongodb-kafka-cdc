import json
import os
from collections import defaultdict

from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv

load_dotenv()

TOPIC = "cdc-prefix.cinebook.bookings"

tickets_by_movie = defaultdict(int)
processed_bookings = {}
movie_names = {}


def apply_change(event):
    operation = event.get("operationType")
    document = event.get("fullDocument") or {}
    document_key = event.get("documentKey") or {}

    booking_id = document.get("_id") or document_key.get("_id")

    if not booking_id:
        return

    if operation in ("insert", "update", "replace"):
        movie_id = document.get("movie_id")
        movie_title = document.get("movie_title")
        seats = document.get("seats", [])
        status = document.get("status")

        if movie_id and movie_title:
            movie_names[movie_id] = movie_title

        new_count = len(seats) if status == "CONFIRMED" else 0

        previous = processed_bookings.get(booking_id)

        if previous is not None:
            old_movie_id, old_count = previous
            tickets_by_movie[old_movie_id] -= old_count

        tickets_by_movie[movie_id] += new_count
        processed_bookings[booking_id] = (movie_id, new_count)

    elif operation == "delete":
        previous = processed_bookings.pop(booking_id, None)

        if previous is not None:
            old_movie_id, old_count = previous
            tickets_by_movie[old_movie_id] -= old_count

    else:
        return

    print("\nLIVE TICKETS SOLD PER MOVIE")
    print("-" * 40)

    for movie_id, count in sorted(tickets_by_movie.items()):
        movie_title = movie_names.get(movie_id, "Unknown Movie")
        print(f"{movie_title} ({movie_id}): {count} tickets")

    print("-" * 40)


def main():
    consumer = Consumer(
        {
            "bootstrap.servers": os.environ["KAFKA_BOOTSTRAP_SERVERS"],
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": os.environ["KAFKA_API_KEY"],
            "sasl.password": os.environ["KAFKA_API_SECRET"],
            "group.id": "cinebook-live-ticket-aggregate-v1",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )

    consumer.subscribe([TOPIC])
    print(f"Listening for booking changes on {TOPIC}...")

    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue

            error = message.error()
            if error is not None:
                if error.code() == KafkaError._PARTITION_EOF:
                    continue
                raise RuntimeError(error)

            value = message.value()

            if value is None:
                continue

            event = json.loads(value.decode("utf-8"))

            apply_change(event)

            consumer.commit(message=message, asynchronous=False)

    except KeyboardInterrupt:
        print("\nStopping live aggregate...")

    finally:
        consumer.close()


if __name__ == "__main__":
    main()
