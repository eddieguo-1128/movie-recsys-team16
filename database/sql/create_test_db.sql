-- Terminate active connections before dropping the database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'test_db' AND pid <> pg_backend_pid();

-- Drop database if it exists
DROP DATABASE IF EXISTS test_db;

-- Revoke privileges before dropping the user
DO $$ 
DECLARE 
    role_exists BOOLEAN;
BEGIN 
    SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'test_user') INTO role_exists;
    
    IF role_exists THEN
        REVOKE ALL PRIVILEGES ON DATABASE postgres FROM test_user;
        DROP ROLE test_user;
    END IF;
END $$;

-- Create new user
CREATE USER test_user WITH PASSWORD 'test_password';

-- Create new database owned by test_user
CREATE DATABASE test_db OWNER test_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE test_db TO test_user;

-- Connect to test_db
\c test_db;

-- Create necessary tables
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

-- Ensure test_user owns all sequences
ALTER TABLE recommendations OWNER TO test_user;
ALTER TABLE watch_events OWNER TO test_user;
ALTER TABLE ratings OWNER TO test_user;

-- ALTER SEQUENCE recommendations_id_seq OWNER TO test_user;
-- ALTER SEQUENCE watch_events_id_seq OWNER TO test_user;
-- ALTER SEQUENCE ratings_id_seq OWNER TO test_user;

-- -- Ensure test_user has full privileges on sequences
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test_user;
-- GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO test_user;
