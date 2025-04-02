### Create or Clean Database

- First you need to install Postgres Locally, and make sure you have a user named "team16"
- Use `create_db.sh` to create the db with table.
- Use `clean_db.sh` to clean the data in tables, db and tables will not be deleted.


### Table Schema

```sql
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
```

### Running as Docker Service

Creat .env:
```
DB_NAME=Project
DB_USER=team16
DB_PASSWORD=<password>
DB_HOST=localhost
DB_PORT=5432

KAFKA_TOPIC=movielog16
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

```shell
$ docker compose -f docker-compose.yml up --build
```

or in detach mode:

```shell
$ docker compose -f docker-compose.yml up --build -d
```

### Check Test Coverage
```shell
$ ./create_test_db.sh

$ pytest --cov=kafka_to_postgres --cov-report=term-missing --cov-report=annotate tests/
```

### Some Useful Commands

- Check CPU Usage: `mpstat -P ALL 1`

- Postgres:
```shell
$ sudo -u postgres psql -d Project

\l # List all databases

\c # Switch database

\dt # List all tables

# Check Table Size
SELECT 
    relname AS table_name,
    n_live_tup AS row_count,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_indexes_size(relid)) AS index_size,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

- Docker:
```shell
docker ps # Check all container

docker stop <id> # Stop container
```