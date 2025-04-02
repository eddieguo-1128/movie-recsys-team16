-- Step 1: Drop the old database if it exists (optional)
SELECT pg_terminate_backend(pg_stat_activity.pid) 
FROM pg_stat_activity 
WHERE datname = 'Project' AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS "Project";

-- Step 2: Create a new database
CREATE DATABASE "Project" OWNER postgres;

-- Step 3: Connect to the Project database
\c "Project";

-- Step 4: Create Tables with Indexes
-- Table for storing movie recommendations given to users
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    recommended_movies VARCHAR(256)[], -- Array of Movie IDs
    response_time INT NOT NULL,  -- New Column for response time (milliseconds)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_recommendations_time ON recommendations(timestamp);

-- Table for storing movie ratings given by users
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id VARCHAR(256) NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ratings_time ON ratings(timestamp);

-- Create the updated watch_events table
CREATE TABLE watch_events (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id VARCHAR(256) NOT NULL,
    minute_watched INT NOT NULL, -- New column to store the last watched minute
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, movie_id) -- Ensures only one row per user-movie pair
);
CREATE INDEX idx_watch_time ON watch_events(timestamp);

---------------------------------------------------
-- Step 5: Create a Trigger Function to Enforce Row Limits
---------------------------------------------------

CREATE OR REPLACE FUNCTION enforce_table_size_limit() RETURNS TRIGGER AS $$
BEGIN
    -- Prevent negative LIMIT values using GREATEST()
    DELETE FROM recommendations WHERE id IN (
        SELECT id FROM recommendations ORDER BY timestamp ASC 
        LIMIT GREATEST(0, (SELECT COUNT(*) FROM recommendations) - 768000)
    );

    DELETE FROM ratings WHERE id IN (
        SELECT id FROM ratings ORDER BY timestamp ASC 
        LIMIT GREATEST(0, (SELECT COUNT(*) FROM ratings) - 1536000)
    );

    DELETE FROM watch_events WHERE id IN (
        SELECT id FROM watch_events ORDER BY timestamp ASC 
        LIMIT GREATEST(0, (SELECT COUNT(*) FROM watch_events) - 3072000)
    );

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

---------------------------------------------------
-- Step 6: Attach Triggers to Enforce Row Limits
---------------------------------------------------

CREATE TRIGGER auto_cleanup_recommendations
AFTER INSERT ON recommendations
EXECUTE FUNCTION enforce_table_size_limit();

CREATE TRIGGER auto_cleanup_ratings
AFTER INSERT ON ratings
EXECUTE FUNCTION enforce_table_size_limit();

CREATE TRIGGER auto_cleanup_watch_events
AFTER INSERT ON watch_events
EXECUTE FUNCTION enforce_table_size_limit();

---------------------------------------------------
-- Step 7: Grant Full Access to team16
---------------------------------------------------

GRANT ALL PRIVILEGES ON DATABASE "Project" TO team16;

GRANT ALL PRIVILEGES ON TABLE recommendations TO team16;
GRANT ALL PRIVILEGES ON TABLE ratings TO team16;
GRANT ALL PRIVILEGES ON TABLE watch_events TO team16;

GRANT ALL PRIVILEGES ON SEQUENCE recommendations_id_seq TO team16;
GRANT ALL PRIVILEGES ON SEQUENCE ratings_id_seq TO team16;
GRANT ALL PRIVILEGES ON SEQUENCE watch_events_id_seq TO team16;

-- Step 9: Exit
\q
