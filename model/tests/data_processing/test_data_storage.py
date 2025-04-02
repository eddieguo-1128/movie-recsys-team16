import os
import pandas as pd
import pytest
from model.data_processing.data_storage import save_to_csv

# Define test file path
TEST_OUTPUT_DIR = "tests/data_processing/test_data"
TEST_CSV_FILE = os.path.join(TEST_OUTPUT_DIR, "test_ratings.csv")

# Ensure the test directory exists
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

def test_save_to_csv_with_data():
    """Test saving valid data to a CSV file."""
    sample_data = [("2025-03-13 10:00:00", "user123", "movie456", 4)]
    expected_columns = ["timestamp", "user_id", "movie_id", "rating"]

    # Call function
    save_to_csv(sample_data, TEST_CSV_FILE, expected_columns)

    # Verify CSV file exists
    assert os.path.exists(TEST_CSV_FILE)

    # Load CSV and check content
    df = pd.read_csv(TEST_CSV_FILE)
    assert list(df.columns) == expected_columns  # Ensure correct columns
    assert df.shape[0] == 1  # Ensure one row is written
    assert df.iloc[0].tolist() == list(sample_data[0])  # Verify row data

    # Cleanup test file
    os.remove(TEST_CSV_FILE)

def test_save_to_csv_with_empty_data(capfd):
    """Test saving an empty dataset (should not create a file)."""
    empty_data = []
    save_to_csv(empty_data, TEST_CSV_FILE, ["timestamp", "user_id", "movie_id", "rating"])

    # Capture printed output
    captured = capfd.readouterr()
    assert "No data to save" in captured.out  # Ensure function warns about no data

    # File should not be created
    assert not os.path.exists(TEST_CSV_FILE)
