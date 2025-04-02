import re
import os
import sys
import signal
import requests
from kafka import KafkaConsumer
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# === Load Configuration ===
load_dotenv()
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
RECOMMENDATION_TTL = timedelta(days=float(os.getenv("RECOMMENDATION_TTL", "30")))
VICTORIA_METRICS_URL = "http://localhost:8428/api/v1/import/prometheus"

# === Kafka Consumer ===
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset="latest",
    enable_auto_commit=True,
    value_deserializer=lambda x: x.decode("utf-8"),
)

# === In-memory state ===
user_recommendations = defaultdict(dict)
user_watched = defaultdict(dict)
last_cleanup_time = datetime.now(timezone.utc)

# === Regex Patterns ===
TIMESTAMP = r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?),"

recommendation_pattern = re.compile(
    TIMESTAMP
    + r"(?P<user_id>\d+),recommendation request.*?status (?P<status>\d+), result: (?P<movies>.+?), (?P<response_time>\d+) ms"
)

watch_pattern = re.compile(
    TIMESTAMP + r"(?P<user_id>\d+),GET /data/m/(?P<movie_id>[^/]+)/(?P<minute>\d+).mpg"
)

rating_pattern = re.compile(
    TIMESTAMP + r"(?P<user_id>\d+),GET /rate/(?P<movie_id>.+)=(?P<rating>\d)"
)


# === Utilities ===
def parse_time(ts_str):
    try:
        if "." in ts_str:
            date_part, frac = ts_str.split(".", 1)
            frac = frac[:6].ljust(6, "0")
            ts_str = f"{date_part}.{frac}"
            return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%f").replace(
                tzinfo=timezone.utc
            )
        elif len(ts_str) == 16:
            return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M").replace(
                tzinfo=timezone.utc
            )
        else:
            return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S").replace(
                tzinfo=timezone.utc
            )
    except Exception as e:
        print(f"[ERROR] Failed to parse timestamp: {ts_str} — {e}")
        raise


def to_unix_ms(ts):
    return int(ts.timestamp() * 1000)


def push_metric(name, labels, value, timestamp):
    labels_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
    metric_line = f"{name}{{{labels_str}}} {value} {to_unix_ms(timestamp)}\n"
    try:
        requests.post(VICTORIA_METRICS_URL, data=metric_line)
    except Exception as e:
        print(f"[ERROR] Failed to push metric: {e}")


def cleanup_old_recommendations():
    now = datetime.now(timezone.utc)

    for user_id in list(user_recommendations):
        filtered = {
            m: ts
            for m, ts in user_recommendations[user_id].items()
            if now - ts <= RECOMMENDATION_TTL
        }
        if filtered:
            user_recommendations[user_id] = filtered
        else:
            del user_recommendations[user_id]

    for user_id in list(user_watched):
        filtered = {
            m: ts
            for m, ts in user_watched[user_id].items()
            if now - ts <= RECOMMENDATION_TTL
        }
        if filtered:
            user_watched[user_id] = filtered
        else:
            del user_watched[user_id]

    print(f"[INFO] Cleanup performed at {now.isoformat()}")


def is_recommended_before(user_id, movie_id, current_ts):
    return (
        movie_id in user_recommendations.get(user_id, {})
        and user_recommendations[user_id][movie_id] < current_ts
    )


# === Log Processor ===
def process_message(message):
    global last_cleanup_time
    now = datetime.now(timezone.utc)

    if now - last_cleanup_time > timedelta(days=1):
        cleanup_old_recommendations()
        last_cleanup_time = now

    log = message.value.strip()

    if match := recommendation_pattern.match(log):
        ts = parse_time(match.group("timestamp"))
        user_id = match.group("user_id")
        status = int(match.group("status"))
        response_time = int(match.group("response_time"))
        movies = [m.strip() for m in match.group("movies").split(",")]

        if status == 200:
            newly_recommended = 0
            for movie_id in movies:
                if movie_id not in user_recommendations[user_id]:
                    user_recommendations[user_id][movie_id] = ts
                    newly_recommended += 1
            if newly_recommended > 0:
                push_metric(
                    "recommendation_movie_count",
                    {"user_id": user_id},
                    newly_recommended,
                    ts,
                )
            push_metric(
                "recommendation_latency_ms", {"user_id": user_id}, response_time, ts
            )
        else:
            push_metric("recommendation_failed_request", {"user_id": user_id}, 1, ts)

    elif match := watch_pattern.match(log):
        ts = parse_time(match.group("timestamp"))
        user_id = match.group("user_id")
        movie_id = match.group("movie_id")

        if movie_id not in user_watched[user_id]:
            user_watched[user_id][movie_id] = ts
            push_metric(
                "watched_movie", {"user_id": user_id, "movie_id": movie_id}, 1, ts
            )

        if is_recommended_before(user_id, movie_id, ts):
            push_metric(
                "watched_recommended", {"user_id": user_id, "movie_id": movie_id}, 1, ts
            )

    elif match := rating_pattern.match(log):
        ts = parse_time(match.group("timestamp"))
        user_id = match.group("user_id")
        movie_id = match.group("movie_id")
        rating = int(match.group("rating"))

        if is_recommended_before(user_id, movie_id, ts):
            push_metric(
                "recommended_rated",
                {"user_id": user_id, "movie_id": movie_id},
                rating,
                ts,
            )

    else:
        print(f"[WARN] Unmatched log: {log}")


# === Graceful Shutdown ===
def cleanup_and_exit(signal_received=None, frame=None):
    print("Shutting down service...")
    try:
        consumer.close()
        print("Kafka consumer closed.")
    except Exception as e:
        print(f"Error closing consumer: {e}")
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)


# === Main Loop ===
def consume():
    print("Listening for Kafka messages...")
    try:
        for message in consumer:
            process_message(message)
    except KeyboardInterrupt:
        cleanup_and_exit()


if __name__ == "__main__":
    consume()
