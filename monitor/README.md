# Monitor Service

## Metrics Documentation

This document describes the key performance metrics used in our recommendation system evaluation.

### 1. Click-Through Rate (CTR) / Precision

**Definition**: Click-Through Rate (CTR) or “Precision” measures what fraction of the recommended movies (for each user) were actually watched by that user. Formally:

$\text{CTR} = \frac{\text{Number of recommended movies that were watched}}{\text{Total number of recommended movies}}$

**Interpretation**

- A higher CTR means more recommended items are actually watched.
- It focuses on how well the system’s recommendations align with user actions.

### 2. Recall

**Definition**: Recall is the fraction of all movies a user actually watched that were previously recommended. In other words, out of all watch events, how many were covered by a prior recommendation?

$\text{Recall} = \frac{\text{Number of watched movies that were recommended beforehand}}{\text{Total number of watched movies}}$

**Interpretation**

- A higher Recall means fewer “misses” (users watch things that weren’t recommended).
- It focuses on coverage: Are we recommending everything the user might watch?

### 3. Watch Rate

**Definition**: Watch Rate measures the fraction of users who watched **at least one** recommended movie after it was recommended.

$\text{Watch Rate} = \frac{\text{Number of users who watched at least one recommended movie}}{\text{Total number of users who received recommendations}}$

**Interpretation**

- A higher Watch Rate indicates that more users find recommendations compelling enough to watch something.
- It’s a user-level metric, rather than an item-level metric.

### 4. Average Rating of Recommended Movies

**Definition**: This is the mean rating (from user feedback) for recommended movies *that users actually rated after receiving the recommendation*.

$\text{Avg Recommended Rating} = \frac{\sum(\text{rating of recommended+watched movies})}{\text{number of recommended+watched movies}}$

**Interpretation**

- A higher value suggests users rate the recommended items positively (potentially indicating relevance or satisfaction).
- It depends on explicit user ratings, so it only applies when ratings are available.

### 5. Latency

**Definition**: Latency in this context typically refers to the **response time** of the recommendation system. It can be measured as:

$\text{Avg Response Time} = \frac{\sum(\text{time taken to produce each recommendation})}{\text{number of recommendations}}$

**Interpretation**

- Lower latency means users receive recommendations faster.
- It is particularly important for real-time or interactive recommendation scenarios.


## Running as Docker Service

Creat .env:
```
KAFKA_TOPIC=movielog16
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

```bash
$ docker compose -f docker-compose.yml up --build
```

or in detach mode:

```bash
$ docker compose -f docker-compose.yml up -d --build
```

### Local SSH
```
ssh -L 3000:localhost:3000 -L 8428:localhost:8428 <user>@<server-ip>
```

## Access Dashboard

Grafana URL: [localhost:3000](http://localhost:3000/), make sure you have local SSH setup.

## Useful Commands

- Check Memory Usage: `watch -n 1 free -m`
- Check CPU usage: `mpstat -P ALL 1`

```
docker volume ls

docker volume prune

docker volume rm
```

