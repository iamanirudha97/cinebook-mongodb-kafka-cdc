import json
import os

from confluent_kafka import Consumer, KafkaError

from dotenv import load_dotenv
load_dotenv()

TOPIC = "cdc-prefix.cinebook.bookings"


def main():
    consumer = Consumer(
        {
            "bootstrap.servers": os.environ["KAFKA_BOOTSTRAP_SERVERS"],
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": os.environ["KAFKA_API_KEY"],
            "sasl.password": os.environ["KAFKA_API_SECRET"],
            "group.id": "cinebook-cdc-consumer",
            "auto.offset.reset": "earliest",
        }
    )

    consumer.subscribe([TOPIC])

    print(f"Listening for MongoDB change events on {TOPIC}...")

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
                print("Received a null-value Kafka record")
                continue

            event = json.loads(value.decode("utf-8"))

            print("\nMongoDB change event:")
            print(json.dumps(event, indent=2, default=str))
            print(
                f"Kafka partition={message.partition()}, "
                f"offset={message.offset()}"
            )

    except KeyboardInterrupt:
        print("\nStopping consumer...")

    finally:
        consumer.close()


if __name__ == "__main__":
    main()