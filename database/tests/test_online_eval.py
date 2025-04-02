import pytest
import psycopg2
import math

@pytest.fixture
def setup_test_db():
    """
    Connects to test_db, truncates tables, inserts a more complex sample dataset,
    and yields a psycopg2 connection for each test.
    """
    conn = psycopg2.connect("postgresql://test_user:test_password@localhost/test_db")
    # If desired, enable autocommit
    conn.autocommit = True

    with conn.cursor() as cur:
        # 1) Clean up existing data
        cur.execute(
            "TRUNCATE TABLE watch_events, ratings, recommendations RESTART IDENTITY CASCADE;"
        )

        # 2) Insert watch_events (10 rows)
        cur.execute(
            """
            INSERT INTO watch_events (user_id, movie_id, minute_watched, timestamp)
            VALUES
                -- User 1
                (1, 'm2',  10, '2025-03-14 09:35:00'),
                (1, 'm3',  15, '2025-03-14 09:40:00'),
                (1, 'm6',  20, '2025-03-14 09:29:00'),  -- Before rec #1 => won't count
                (1, 'm7',  25, '2025-03-14 10:45:00'),

                -- User 2
                (2, 'm1',  30, '2025-03-14 12:00:00'),
                (2, 'm2',  35, '2025-03-14 13:00:00'),
                (2, 'm6',  40, '2025-03-15 12:00:00'),

                -- User 3
                (3, 'm4',  45, '2025-03-14 16:00:00'),
                (3, 'm7',  50, '2025-03-14 14:00:00'),  -- Before rec #5 => won't count
                (3, 'm8',  60, '2025-03-15 13:00:00');
            """
        )

        # 3) Insert recommendations (6 rows) with response_time
        cur.execute(
            """
            INSERT INTO recommendations (user_id, recommended_movies, response_time, timestamp)
            VALUES
                -- User 1
                (1, ARRAY['m2','m3','m6'],   120, '2025-03-14 09:30:00'),
                (1, ARRAY['m7','m8'],       300, '2025-03-14 10:30:00'),

                -- User 2
                (2, ARRAY['m1','m2','m10'], 150, '2025-03-14 11:45:00'),
                (2, ARRAY['m6','m9'],       200, '2025-03-15 11:45:00'),

                -- User 3
                (3, ARRAY['m4','m7','m10'], 180, '2025-03-14 15:00:00'),
                (3, ARRAY['m2','m8'],       250, '2025-03-15 12:45:00');
            """
        )

        # 4) Insert ratings so that some recommended movies are rated after rec time
        cur.execute(
            """
            INSERT INTO ratings (user_id, movie_id, rating, timestamp)
            VALUES
                -- User 1 ratings
                (1, 'm2', 4, '2025-03-14 09:35:00'),  -- after rec #1 (09:30)
                (1, 'm3', 3, '2025-03-14 10:00:00'),  -- after rec #1
                (1, 'm6', 5, '2025-03-14 09:29:00'),  -- before rec #1 => won't count
                (1, 'm7', 5, '2025-03-14 10:45:00'),  -- after rec #2 (10:30)
                (1, 'm8', 2, '2025-03-14 10:20:00'),  -- before rec #2 => won't count

                -- User 2 ratings
                (2, 'm1', 4, '2025-03-14 12:00:00'),  -- after rec #3 (11:45)
                (2, 'm2', 5, '2025-03-14 12:30:00'),  -- after rec #3
                (2, 'm10', 3, '2025-03-14 11:44:00'), -- before rec #3 => won't count
                (2, 'm6', 4, '2025-03-15 12:00:00'),  -- after rec #4 (11:45)

                -- User 3 ratings
                (3, 'm4', 4, '2025-03-14 16:00:00'),  -- after rec #5 (15:00)
                (3, 'm7', 3, '2025-03-14 14:00:00'),  -- before rec #5 => won't count
                (3, 'm10', 1, '2025-03-14 14:30:00'), -- before rec #5 => won't count
                (3, 'm2', 4, '2025-03-15 13:00:00'),  -- after rec #6 (12:45)
                (3, 'm8', 5, '2025-03-15 12:40:00');  -- before rec #6 => won't count
            """
        )

    conn.commit()
    yield conn
    conn.close()


def test_avg_recommended_rating(setup_test_db):
    """
    Tests the average rating for recommended movies, expecting 4.125.
    """
    expected = 4.125

    conn = setup_test_db
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH recommended_movies_ratings AS (
                SELECT r.user_id, ra.movie_id, ra.rating
                FROM recommendations r
                JOIN ratings ra
                  ON r.user_id = ra.user_id
                 AND ra.movie_id = ANY(r.recommended_movies)
                 AND ra.timestamp > r.timestamp
            )
            SELECT AVG(rating)
            FROM recommended_movies_ratings;
            """
        )
        raw_result = cur.fetchone()[0]

    result = float(raw_result) if raw_result is not None else 0.0
    assert math.isclose(
        result, expected, abs_tol=1e-6
    ), f"Expected {expected}, got {result}"


def test_latency(setup_test_db):
    """
    Tests the average recommendation response_time, which should be 200.0
    based on the sum (120+300+150+200+180+250=1200) / 6.
    """
    expected = 200.0

    conn = setup_test_db
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT AVG(response_time) AS avg_response_time
            FROM recommendations;
            """
        )
        raw_result = cur.fetchone()[0]

    result = float(raw_result) if raw_result else 0.0
    assert (
        pytest.approx(expected, abs=1e-6) == result
    ), f"Expected {expected}, got {result}"


def test_ctr_precision(setup_test_db):
    """
    Tests the click-through rate (CTR) / precision query.
    With the new data, we have 8 valid watches for 15 recommended => 8/15 ~ 0.5333.
    """

    expected_ctr = 8 / 15  # ~0.5333...

    conn = setup_test_db
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH watched_recommended AS (
                SELECT r.user_id, we.movie_id
                FROM recommendations r
                JOIN watch_events we 
                  ON r.user_id = we.user_id 
                 WHERE we.movie_id = ANY(r.recommended_movies)
                   AND r.timestamp < we.timestamp
            )
            SELECT 
                COUNT(DISTINCT (user_id, movie_id))::decimal
                / NULLIF((SELECT SUM(array_length(recommended_movies, 1)) 
                          FROM recommendations), 0) 
                AS ctr_precision
            FROM watched_recommended;
            """
        )
        raw_result = cur.fetchone()[0]

    result = float(raw_result) if raw_result else 0.0
    assert math.isclose(
        result, expected_ctr, abs_tol=1e-6
    ), f"Expected CTR {expected_ctr}, got {result}"


def test_recall(setup_test_db):
    """
    Tests the recall query. We remove the time filter for demonstration,
    so the result should be the fraction of watch_events that were in
    a prior recommendation (8/10 = 0.8).
    """
    expected_recall = 0.8

    conn = setup_test_db
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH watched_recommended AS (
                SELECT we.user_id, we.movie_id
                FROM watch_events we
                JOIN recommendations r 
                  ON we.user_id = r.user_id 
                 AND we.movie_id = ANY(r.recommended_movies)
                 WHERE r.timestamp < we.timestamp
            )
            SELECT 
                COUNT(DISTINCT (user_id, movie_id))::decimal
                /
                NULLIF((
                    SELECT COUNT(DISTINCT (user_id, movie_id))
                    FROM watch_events
                ), 0) 
                AS recall
            FROM watched_recommended;
            """
        )
        raw_result = cur.fetchone()[0]

    recall_value = float(raw_result) if raw_result is not None else 0.0
    assert math.isclose(
        recall_value, expected_recall, abs_tol=1e-6
    ), f"Expected recall {expected_recall}, got {recall_value}"


def test_watch_rate(setup_test_db):
    """
    Tests the watch rate query. All 3 users watched at least one recommended
    movie after it was recommended → watch_rate = 3/3 = 1.0.
    """
    expected_watch_rate = 1.0

    conn = setup_test_db
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH users_who_watched AS (
                SELECT DISTINCT r.user_id
                FROM recommendations r
                JOIN watch_events we 
                  ON r.user_id = we.user_id
                 WHERE we.movie_id = ANY(r.recommended_movies)
                   AND r.timestamp < we.timestamp
            )
            SELECT 
                COUNT(*) * 1.0 / NULLIF(
                    (SELECT COUNT(DISTINCT user_id) FROM recommendations), 
                0) AS watch_rate
            FROM users_who_watched;
            """
        )
        raw_result = cur.fetchone()[0]

    watch_rate = float(raw_result) if raw_result else 0.0
    assert math.isclose(
        watch_rate, expected_watch_rate, abs_tol=1e-6
    ), f"Expected watch_rate={expected_watch_rate}, got {watch_rate}"
