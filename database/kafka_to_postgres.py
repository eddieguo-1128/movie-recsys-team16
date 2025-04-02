import os
import psycopg2
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


def get_db_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    # Enable autocommit
    conn.autocommit = True
    return conn


def process_kafka_message(message, conn):
    log = message.value  # Get the message value

    if isinstance(log, bytes):  # Ensure it's a string
        log = log.decode("utf-8")

    log = log.strip()

    valid_recommendation = True

    if match := recommendation_pattern.search(log):
        timestamp, user_id, status, result, response_time = (
            match.group("timestamp"),
            int(match.group("user_id")),
            int(match.group("status")),
            match.group("movies"),
            int(match.group("response_time")),
        )

        if status != 200:
            print(f"Skipping invalid recommendation log: {log}")
            valid_recommendation = False

        if valid_recommendation:
            recommended_movies = result.split(", ")
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO recommendations (user_id, recommended_movies, response_time, timestamp)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, recommended_movies, response_time, timestamp),
                )

    if match := watch_pattern.search(log):
        timestamp, user_id, movie_id, minute_watched = (
            match.group("timestamp"),
            int(match.group("user_id")),
            match.group("movie_id"),
            int(match.group("minute")),
        )
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO watch_events (user_id, movie_id, minute_watched, timestamp)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, movie_id)
                DO UPDATE SET 
                    minute_watched = GREATEST(watch_events.minute_watched, EXCLUDED.minute_watched),
                    timestamp = EXCLUDED.timestamp;
                """,
                (user_id, movie_id, minute_watched, timestamp),
            )

    if match := rating_pattern.search(log):
        timestamp, user_id, movie_id, rating = (
            match.group("timestamp"),
            int(match.group("user_id")),
            match.group("movie_id"),
            int(match.group("rating")),
        )
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ratings (user_id, movie_id, rating, timestamp)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, movie_id, rating, timestamp),
            )


def consume_from_kafka():
    global consumer, conn  # Make them accessible for cleanup

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


def cleanup_and_exit(signal_received=None, frame=None):
    print("Shutting down service...")
    if "consumer" in globals() and consumer:
        consumer.close()
        print("Kafka consumer closed.")
    if "conn" in globals() and conn:
        conn.close()
        print("PostgreSQL connection closed.")
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup_and_exit)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, cleanup_and_exit)  # Handle Docker stop

if __name__ == "__main__":
    consume_from_kafka() # pragma: no cover
