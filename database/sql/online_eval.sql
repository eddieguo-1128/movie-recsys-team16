\c "Project";

-- ==================================================
-- 1: CTR / Precision
-- ==================================================
WITH reference_ts AS (
    SELECT GREATEST(
        COALESCE((SELECT MAX(timestamp) FROM recommendations), NOW()),
        COALESCE((SELECT MAX(timestamp) FROM watch_events), NOW()),
        COALESCE((SELECT MAX(timestamp) FROM ratings), NOW())
    ) AS max_ts
),
watched_recommended AS (
    SELECT r.user_id, we.movie_id
    FROM recommendations r
    JOIN watch_events we 
      ON r.user_id = we.user_id 
    WHERE we.movie_id = ANY(r.recommended_movies)  
      AND r.timestamp < we.timestamp  
      AND r.timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
      AND we.timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
)
SELECT 
    COUNT(DISTINCT (user_id, movie_id)) * 1.0 /
    NULLIF(
      (
        SELECT SUM(array_length(recommended_movies, 1)) 
        FROM recommendations 
        WHERE timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
      ), 
      0
    ) 
    AS ctr_precision
FROM watched_recommended;


-- ==================================================
-- 2: Recall
-- ==================================================
WITH reference_ts AS (
    SELECT GREATEST(
        COALESCE((SELECT MAX(timestamp) FROM recommendations), NOW()),
        COALESCE((SELECT MAX(timestamp) FROM watch_events), NOW()),
        COALESCE((SELECT MAX(timestamp) FROM ratings), NOW())
    ) AS max_ts
),
watched_recommended AS (
    SELECT we.user_id, we.movie_id
    FROM watch_events we
    JOIN recommendations r 
      ON we.user_id = r.user_id 
    WHERE we.movie_id = ANY(r.recommended_movies)
      AND r.timestamp < we.timestamp
      AND r.timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
      AND we.timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
)
SELECT 
    COUNT(DISTINCT (user_id, movie_id)) * 1.0 /
    NULLIF(
      (
        SELECT COUNT(DISTINCT (user_id, movie_id)) 
        FROM watch_events 
        WHERE timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
      ),
      0
    ) 
    AS recall
FROM watched_recommended;


-- ==================================================
-- 3: Watch Rate
-- ==================================================
WITH reference_ts AS (
    SELECT GREATEST(
        COALESCE((SELECT MAX(timestamp) FROM recommendations), NOW()),
        COALESCE((SELECT MAX(timestamp) FROM watch_events), NOW()),
        COALESCE((SELECT MAX(timestamp) FROM ratings), NOW())
    ) AS max_ts
),
users_who_watched AS (
    SELECT DISTINCT r.user_id
    FROM recommendations r
    JOIN watch_events we 
      ON r.user_id = we.user_id 
    WHERE we.movie_id = ANY(r.recommended_movies)
      AND r.timestamp < we.timestamp
      AND r.timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
      AND we.timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
)
SELECT 
    COUNT(*) * 1.0 /
    NULLIF(
      (
        SELECT COUNT(DISTINCT user_id) 
        FROM recommendations 
        WHERE timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
      ),
      0
    ) 
    AS watch_rate
FROM users_who_watched;


-- ==================================================
-- 4: Average Rating of Recommended Movies
-- ==================================================
WITH reference_ts AS (
    SELECT GREATEST(
        COALESCE((SELECT MAX(timestamp) FROM recommendations), NOW()),
        COALESCE((SELECT MAX(timestamp) FROM watch_events), NOW()),
        COALESCE((SELECT MAX(timestamp) FROM ratings), NOW())
    ) AS max_ts
),
recommended_movies_ratings AS (
    SELECT r.user_id, ra.movie_id, ra.rating
    FROM recommendations r
    JOIN ratings ra 
      ON r.user_id = ra.user_id 
     AND ra.movie_id = ANY(r.recommended_movies)
    WHERE r.timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
      AND ra.timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '12 hour'
      AND r.timestamp < ra.timestamp
)
SELECT 
    AVG(rating) AS avg_recommended_rating
FROM recommended_movies_ratings;


-- ==================================================
-- 5: Latency
-- ==================================================
WITH reference_ts AS (
    SELECT GREATEST(
        COALESCE((SELECT MAX(timestamp) FROM recommendations), NOW()),
        COALESCE((SELECT MAX(timestamp) FROM watch_events), NOW()),
        COALESCE((SELECT MAX(timestamp) FROM ratings), NOW())
    ) AS max_ts
)
SELECT 
    AVG(response_time) AS avg_response_time
FROM recommendations
WHERE timestamp >= (SELECT max_ts FROM reference_ts) - INTERVAL '1 hour';
