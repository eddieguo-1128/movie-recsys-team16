import pytest
import psycopg2
from psycopg2.extensions import connection as psycopg2_connection
from kafka_to_postgres import get_db_connection, process_kafka_message

# Database credentials for testing (ensure these match your local test DB setup)
DB_NAME = "test_db"
DB_USER = "test_user"
DB_PASSWORD = "test_password"
DB_HOST = "localhost"
DB_PORT = "5432"

@pytest.fixture(scope="module")
def test_db():
    """Creates a real test database connection."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    yield conn
    conn.close()

@pytest.fixture
def test_cursor(test_db):
    """Resets test tables before each test."""
    with test_db.cursor() as cur:
        cur.execute("TRUNCATE recommendations, watch_events, ratings RESTART IDENTITY CASCADE")
    yield test_db.cursor()

def test_get_db_connection():
    """Ensure database connection is established successfully."""
    conn = get_db_connection()
    assert isinstance(conn, psycopg2_connection)
    conn.close()

def test_insert_recommendation(test_cursor):
    """Test inserting a recommendation log into the database."""
    message = type(
        "FakeMessage",
        (object,),
        {"value": "2025-03-14T12:34:56,101,recommendation request status 200, result: movieA, movieB, 100 ms".encode()},
    )
    process_kafka_message(message, test_cursor.connection)

    test_cursor.execute("SELECT user_id, recommended_movies, response_time FROM recommendations WHERE user_id = 101")
    result = test_cursor.fetchone()
    assert result is not None
    assert result[0] == 101
    assert result[1] == ["movieA", "movieB"]
    assert result[2] == 100  # response_time

def test_insert_watch_event(test_cursor):
    """Test inserting a watch event into the database."""
    message = type(
        "FakeMessage",
        (object,),
        {"value": "2025-03-14T12:34:56,202,GET /data/m/movieXYZ/45.mpg".encode()},
    )
    process_kafka_message(message, test_cursor.connection)

    test_cursor.execute("SELECT user_id, movie_id, minute_watched FROM watch_events WHERE user_id = 202")
    result = test_cursor.fetchone()
    assert result is not None
    assert result[0] == 202
    assert result[1] == "movieXYZ"
    assert result[2] == 45  # minute_watched

def test_insert_rating(test_cursor):
    """Test inserting a rating into the database."""
    message = type(
        "FakeMessage",
        (object,),
        {"value": "2025-03-14T12:34:56,303,GET /rate/movieABC=5".encode()},
    )
    process_kafka_message(message, test_cursor.connection)

    test_cursor.execute("SELECT user_id, movie_id, rating FROM ratings WHERE user_id = 303")
    result = test_cursor.fetchone()
    assert result is not None
    assert result[0] == 303
    assert result[1] == "movieABC"
    assert result[2] == 5  # rating
