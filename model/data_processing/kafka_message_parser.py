import os

def parse_kafka_message(message):
    watch_history, ratings, recommendation_requests = [], [], []
    
    # for message in messages:
    parts = message.split(",")
    if len(parts) >= 3:

        timestamp, user_id, action = parts[:3]

        if "recommendation request" in action:
            rec_result = action.split("result: ")[-1]
            recommendation_requests.append((timestamp, user_id, rec_result))
        elif "GET /data/m/" in action:
            movie_id = action.split("/")[3]
            watch_history.append((timestamp, user_id, movie_id))
        elif "GET /rate/" in action:
            rating_info = action.split("=")
            if len(rating_info) == 2:
                movie_id, rating = rating_info[0].split("/")[-1], rating_info[1]
                ratings.append((timestamp, user_id, movie_id, int(rating)))
                os.system(f"echo {message} >> ../data/kafka_ratings_log.csv")

    return ratings, watch_history, recommendation_requests
