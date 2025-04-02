-- Step 1: Connect to the Project Database
\c "Project";

-- Step 2: Truncate All Tables (Fast Cleanup)
TRUNCATE TABLE recommendations, ratings, watch_events RESTART IDENTITY CASCADE;

-- Step 3: Verify Cleanup
SELECT COUNT(*) AS remaining_recommendations FROM recommendations;
SELECT COUNT(*) AS remaining_ratings FROM ratings;
SELECT COUNT(*) AS remaining_watch_events FROM watch_events;

-- Step 4: Exit
\q

