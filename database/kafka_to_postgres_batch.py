import os
import psycopg2
from psycopg2.extras import execute_batch
from kafka import KafkaConsumer
import re
import signal
import sys
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

recommendation_pattern = re.compile(
    r"(?P<timestamp>[\d\-T:.]+),(?P<user_id>\d+),recommendation request.*?status (?P<status>\d+), result: (?P<movies>.+?), (?P<response_time>\d+) ms"
)
watch_pattern = re.compile(
    r"(?P<timestamp>[\d\-T:.]+),(?P<user_id>\d+),GET /data/m/(?P<movie_id>[\S]+)/(?P<minute>\d+).mpg"
)
rating_pattern = re.compile(
    r"(?P<timestamp>[\d\-T:.]+),(?P<user_id>\d+),GET /rate/(?P<movie_id>[\S]+)=(?P<rating>\d)"
)

BATCH_SIZE = 100

# Batches of data for each table
batch_data = {
    "recommendations": [],
    "watch_events": [],
    "ratings": []
}

def get_db_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    # Enable autocommit if desired, or manage transactions manually.
    conn.autocommit = True
    return conn

def flush_data(conn):
    """
    Inserts all accumulated batch_data into the database in a single set
    of statements. Clear the lists upon success.
    """
    global batch_data

    # Nothing to flush if all are empty
    total = len(batch_data["recommendations"]) + len(batch_data["watch_events"]) + len(batch_data["ratings"])
    if total == 0:
        return

    with conn.cursor() as cur:
        # Insert recommendations in one go
        if batch_data["recommendations"]:
            execute_batch(
                cur,
                """
                INSERT INTO recommendations (user_id, recommended_movies, response_time, timestamp)
                VALUES (%s, %s, %s, %s)
                """,
                batch_data["recommendations"]
            )

        # Insert watch events in one go, using ON CONFLICT
        if batch_data["watch_events"]:
            execute_batch(
                cur,
                """
                INSERT INTO watch_events (user_id, movie_id, minute_watched, timestamp)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, movie_id)
                DO UPDATE SET
                    minute_watched = GREATEST(watch_events.minute_watched, EXCLUDED.minute_watched),
                    timestamp = EXCLUDED.timestamp
                """,
                batch_data["watch_events"]
            )

        # Insert ratings in one go
        if batch_data["ratings"]:
            execute_batch(
                cur,
                """
                INSERT INTO ratings (user_id, movie_id, rating, timestamp)
                VALUES (%s, %s, %s, %s)
                """,
                batch_data["ratings"]
            )

    # If all inserts succeeded, clear the batches
    batch_data["recommendations"].clear()
    batch_data["watch_events"].clear()
    batch_data["ratings"].clear()

def process_kafka_message(message, conn):
    """
    Instead of inserting immediately, parse the log and append to batch_data.
    Then flush if we exceed BATCH_SIZE.
    """
    log = message.value
    if isinstance(log, bytes):
        log = log.decode("utf-8")
    log = log.strip()

    if match := recommendation_pattern.search(log):
        timestamp, user_id, status, result, response_time = (
            match.group("timestamp"),
            int(match.group("user_id")),
            int(match.group("status")),
            match.group("movies"),
            int(match.group("response_time")),
        )

        # Skip if not a 200 or if connection refused
        if status == 200:
            recommended_movies = result.split(", ")
            batch_data["recommendations"].append(
                (user_id, recommended_movies, response_time, timestamp)
            )

    elif match := watch_pattern.search(log):
        timestamp, user_id, movie_id, minute_watched = (
            match.group("timestamp"),
            int(match.group("user_id")),
            match.group("movie_id"),
            int(match.group("minute")),
        )
        batch_data["watch_events"].append((user_id, movie_id, minute_watched, timestamp))

    elif match := rating_pattern.search(log):
        timestamp, user_id, movie_id, rating = (
            match.group("timestamp"),
            int(match.group("user_id")),
            match.group("movie_id"),
            int(match.group("rating")),
        )
        batch_data["ratings"].append((user_id, movie_id, rating, timestamp))

    # Check if we should flush now
    total_batch_count = (
        len(batch_data["recommendations"])
        + len(batch_data["watch_events"])
        + len(batch_data["ratings"])
    )
    if total_batch_count >= BATCH_SIZE:
        flush_data(conn)

def consume_from_kafka():
    global consumer, conn

    try:
        conn = get_db_connection()
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset="latest",
            enable_auto_commit=True,
            value_deserializer=lambda x: x.decode("utf-8"),
        )
        print("Listening for Kafka messages...")

        for message in consumer:
            process_kafka_message(message, conn)

    except Exception as e:
        print(f"Service error: {e}")
        cleanup_and_exit()
    finally:
        # Flush any remaining data at shutdown
        flush_data(conn)

def cleanup_and_exit(signal_received=None, frame=None):
    print("Shutting down service...")
    if "consumer" in globals() and consumer:
        consumer.close()
        print("Kafka consumer closed.")
    if "conn" in globals() and conn:
        flush_data(conn)  # final flush if needed
        conn.close()
        print("PostgreSQL connection closed.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, cleanup_and_exit) # Handle Docker stop

if __name__ == "__main__":
    consume_from_kafka()
