import os
import pytest
from model.data_processing.kafka_message_parser import parse_kafka_message

@pytest.mark.parametrize(
    "message, expected_ratings, expected_watch_history, expected_recommendations",
    [
        # ✅ Valid rating message
        ("1700000000,user123,GET /rate/50=4",
         [("1700000000", "user123", "50", 4)], [], []),

        # ✅ Valid watch history message
        ("1700000001,user456,GET /data/m/100",
         [], [("1700000001", "user456", "100")], []),

        # ✅ Valid recommendation request message
        ("1700000002,user789,recommendation request result: movie200",
         [], [], [("1700000002", "user789", "movie200")]),

        # ✅ Multiple messages in one
        ("1700000003,user999,GET /rate/25=3",
         [("1700000003", "user999", "25", 3)], [], []),

        # ⚠️ Malformed rating message (missing "=")
        ("1700000004,user321,GET /rate/60",
         [], [], []),

        # ⚠️ Malformed watch history message (wrong format)
        ("1700000005,user555,GET /data/",
         [], [], []),

        # ⚠️ Completely invalid message
        ("random_text",
         [], [], [])
    ]
)
def test_parse_kafka_message(message, expected_ratings, expected_watch_history, expected_recommendations):
    """Test parsing of different Kafka messages."""
    ratings, watch_history, recommendations = parse_kafka_message(message)

    assert ratings == expected_ratings
    assert watch_history == expected_watch_history
    assert recommendations == expected_recommendations

def test_parse_kafka_message_empty():
    """Test empty message input."""
    ratings, watch_history, recommendations = parse_kafka_message("")

    assert ratings == []
    assert watch_history == []
    assert recommendations == []

def test_parse_kafka_message_logs_to_file(monkeypatch):
    """Test if messages are logged correctly to a file (mocked os.system)."""
    test_message = "1700000006,user777,GET /rate/30=5"
    
    # Mock os.system to prevent actual file logging
    mock_os_system = lambda x: None
    monkeypatch.setattr(os, "system", mock_os_system)

    ratings, watch_history, recommendations = parse_kafka_message(test_message)

    assert ratings == [("1700000006", "user777", "30", 5)]
    assert watch_history == []
    assert recommendations == []
