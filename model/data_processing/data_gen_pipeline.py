import os
from kafka_message_parser import parse_kafka_message
from data_storage import save_to_csv
from kafka import KafkaConsumer

# Kafka Configuration
KAFKA_SERVER = 'localhost:9092'
TOPIC = 'movielog16'

# Define the absolute path to 'model/data/'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get current script's directory
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data")  # Move up one level and go into 'data/'
os.makedirs(OUTPUT_DIR, exist_ok=True)  # ✅ Creates 'data/' if it doesn't exist

def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers = KAFKA_SERVER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
    )
    print(f"Connected to Kafka topic: ",TOPIC)
    print("Reading messages from Kafka...")
    ratings = []
    for message in consumer:
        message = message.value.decode()
        rating, watch_history, recommendation_request = parse_kafka_message(message)
        
        if len(rating)>0:
            ratings.append(rating[0])
        
        if(len(ratings)>10000):
            break
    '''
        We are choosing the rating stream as
        1. It provides explicit feedback (i.e., direct user preferences with a rating from 1 to 5).
        2. Most recommendation models (like collaborative filtering) work better with explicit ratings.
        3. Allows for better personalization since we know exactly how much a user liked a movie.
    '''
    save_to_csv(ratings, os.path.join(OUTPUT_DIR, "ratings.csv"), ["timestamp", "user_id", "movie_id", "rating"])
    # save_to_csv(watch_history, "watch_history.csv", ["timestamp", "user_id", "movie_id"])
    # save_to_csv(recommendation_requests, "recommendation_requests.csv", ["timestamp", "user_id", "rec_result"])

if __name__ == "__main__":
    main()
