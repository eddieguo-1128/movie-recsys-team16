# import os
# import pytest
# import tempfile
# from unittest.mock import patch, MagicMock
# from kafka import KafkaConsumer
# from model.data_processing.kafka_message_parser import parse_kafka_message
# from model.data_processing.data_storage import save_to_csv

# # Define a temporary directory for test data
# @pytest.fixture
# def temp_csv_file():
#     """Creates a temporary CSV file for testing."""
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmpfile:
#         yield tmpfile.name
#     os.remove(tmpfile.name)  # Cleanup after test


# @pytest.fixture
# def sample_kafka_message():
#     """Returns a sample Kafka message in the expected format."""
#     return "1700000000,1,GET /rate/50=4"


# @pytest.fixture
# def expected_parsed_data():
#     """Returns the expected parsed data from the sample Kafka message."""
#     return [("1700000000", "1", "50", 4)], [], []


# @patch("kafka.KafkaConsumer")
# def test_kafka_consumer(mock_kafka_consumer, sample_kafka_message, expected_parsed_data, temp_csv_file):
#     """Test if Kafka consumer correctly processes messages and saves ratings."""
    
#     # Mock KafkaConsumer messages
#     mock_message = MagicMock()
#     mock_message.value.decode.return_value = sample_kafka_message
#     mock_kafka_consumer.return_value.__iter__.return_value = [mock_message] * 3  # Simulate 3 messages
    
#     # Simulate message processing
#     ratings = []
#     consumer = KafkaConsumer("dummy_topic", bootstrap_servers="localhost:9092")
    
#     for message in consumer:
#         message = message.value.decode()
#         rating, _, _ = parse_kafka_message(message)
        
#         if len(rating) > 0:
#             ratings.append(rating[0])

#         if len(ratings) >= 3:  # Stop after processing 3 messages
#             break

#     # Ensure the ratings list contains expected data
#     assert len(ratings) == 3  # Should have processed 3 messages
#     assert ratings[0] == expected_parsed_data[0][0]  # First rating matches expected

#     # Test CSV saving functionality
#     save_to_csv(ratings, temp_csv_file, ["timestamp", "user_id", "movie_id", "rating"])

#     # Verify CSV file exists and contains correct data
#     assert os.path.exists(temp_csv_file)

#     # Read and verify saved data
#     with open(temp_csv_file, "r") as f:
#         lines = f.readlines()
    
#     # Header should be correct
#     assert lines[0].strip() == "timestamp,user_id,movie_id,rating"
    
#     # Verify saved data
#     assert lines[1].strip() == "1700000000,1,50,4"
