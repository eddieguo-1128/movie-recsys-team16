import pytest
from unittest.mock import MagicMock, patch
from kafka_to_postgres import process_kafka_message, consume_from_kafka, cleanup_and_exit

@pytest.fixture
def mock_db_connection():
    """Fixture to mock a database connection."""
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = MagicMock()
    return conn

@pytest.fixture
def mock_kafka_message():
    """Creates a fake Kafka message with a `.value` attribute."""
    class FakeMessage:
        def __init__(self, value):
            self.value = value.encode('utf-8')

    return FakeMessage

def test_process_recommendation_message(mock_kafka_message, mock_db_connection):
    message = mock_kafka_message("2025-03-14T12:34:56,123,recommendation request status 200, result: movie1, movie2, 150 ms")
    
    process_kafka_message(message, mock_db_connection)

    cur = mock_db_connection.cursor.return_value.__enter__.return_value
    cur.execute.assert_called_once()
    assert "INSERT INTO recommendations" in cur.execute.call_args[0][0]

def test_process_watch_message(mock_kafka_message, mock_db_connection):
    message = mock_kafka_message("2025-03-14T12:34:56,456,GET /data/m/movie123/30.mpg")
    
    process_kafka_message(message, mock_db_connection)

    cur = mock_db_connection.cursor.return_value.__enter__.return_value
    cur.execute.assert_called_once()
    assert "INSERT INTO watch_events" in cur.execute.call_args[0][0]

def test_process_rating_message(mock_kafka_message, mock_db_connection):
    message = mock_kafka_message("2025-03-14T12:34:56,789,GET /rate/movie456=4")

    process_kafka_message(message, mock_db_connection)

    cur = mock_db_connection.cursor.return_value.__enter__.return_value
    cur.execute.assert_called_once()
    assert "INSERT INTO ratings" in cur.execute.call_args[0][0]

def test_skip_invalid_recommendation_message(mock_kafka_message, mock_db_connection):
    message = mock_kafka_message("2025-03-14T12:34:56,123,recommendation request status 500, result: Connection refused, 300 ms")

    process_kafka_message(message, mock_db_connection)

    cur = mock_db_connection.cursor.return_value.__enter__.return_value
    cur.execute.assert_not_called()

@patch("kafka_to_postgres.KafkaConsumer")
@patch("kafka_to_postgres.get_db_connection")
@patch("kafka_to_postgres.process_kafka_message")
def test_consume_from_kafka(mock_process_message, mock_db_conn, mock_kafka_consumer):
    """Test Kafka consumer reads messages and calls process_kafka_message."""
    mock_conn = mock_db_conn.return_value
    mock_consumer = mock_kafka_consumer.return_value
    mock_message = MagicMock(value="2025-03-14T12:34:56,123,recommendation request status 200, result: movie1, movie2, 150 ms")
    mock_consumer.__iter__.return_value = [mock_message]

    consume_from_kafka()

    mock_process_message.assert_called_once_with(mock_message, mock_conn)

@patch("kafka_to_postgres.KafkaConsumer")
@patch("kafka_to_postgres.get_db_connection")
@patch("kafka_to_postgres.cleanup_and_exit")
def test_consume_from_kafka_error(mock_cleanup, mock_db_conn, mock_kafka_consumer):
    """Test exception handling in consume_from_kafka."""
    mock_kafka_consumer.side_effect = Exception("Kafka failure")

    consume_from_kafka()

    mock_cleanup.assert_called_once()

@patch("kafka_to_postgres.consumer")
@patch("kafka_to_postgres.conn")
@patch("sys.exit")
def test_cleanup_and_exit(mock_sys_exit, mock_conn, mock_consumer):
    """Ensure cleanup_and_exit properly closes resources."""
    cleanup_and_exit()
    mock_consumer.close.assert_called_once()
    mock_conn.close.assert_called_once()
    mock_sys_exit.assert_called_once()
