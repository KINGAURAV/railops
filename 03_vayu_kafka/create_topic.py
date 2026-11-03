"""Create the Vayu Kafka topics used by the RailOps pipeline.

Run from the repo root after your Kafka deployment is Ready:

    cd /home/jovyan/move-it
    python 03_vayu_kafka/create_topic.py

Set Kafka variables in the project root `.env` file.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME", "")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD", "")
TOPIC_NAMES = [
    os.getenv("KAFKA_TOPIC", "railway_telemetry"),
    os.getenv("KAFKA_COMMAND_TOPIC", "railway_commands"),
]
NUM_PARTITIONS = int(os.getenv("KAFKA_TOPIC_PARTITIONS", "1"))
REPLICATION_FACTOR = int(os.getenv("KAFKA_TOPIC_REPLICATION_FACTOR", "1"))

KAFKA_SECURITY = {
    "security_protocol": "SASL_PLAINTEXT",
    "sasl_mechanism": "SCRAM-SHA-512",
    "sasl_plain_username": KAFKA_USERNAME,
    "sasl_plain_password": KAFKA_PASSWORD,
}


def main() -> None:
    if not all([KAFKA_BROKER, KAFKA_USERNAME, KAFKA_PASSWORD]):
        raise ValueError("Set KAFKA_BROKER, KAFKA_USERNAME, and KAFKA_PASSWORD in .env")

    admin = KafkaAdminClient(
        bootstrap_servers=KAFKA_BROKER,
        **KAFKA_SECURITY,
    )
    try:
        for name in TOPIC_NAMES:
            topic = NewTopic(
                name=name,
                num_partitions=NUM_PARTITIONS,
                replication_factor=REPLICATION_FACTOR,
            )
            try:
                admin.create_topics([topic])
                print(f"Created topic: {name}")
            except TopicAlreadyExistsError:
                print(f"Topic already exists: {name}")
    finally:
        admin.close()


if __name__ == "__main__":
    main()
