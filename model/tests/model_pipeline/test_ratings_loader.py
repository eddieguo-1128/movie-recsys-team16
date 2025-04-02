import pytest
import pandas as pd
from surprise import Dataset
from model.model_pipeline.ratings_loader import load_data  # Replace 'your_module' with the actual module name


@pytest.fixture
def create_csv(tmpdir):
    """Fixture to create a temporary CSV file."""
    def _create_csv(content):
        csv_path = tmpdir.join("test_data.csv")
        csv_path.write(content)
        return str(csv_path)
    return _create_csv  # Return the inner function so it can be used in tests


def test_load_valid_csv(create_csv):
    """Test loading a valid CSV file."""
    content = "user_id,movie_id,rating\n1,101,5\n2,102,4\n3,103,3"
    csv_path = create_csv(content)  # Call the fixture function

    data = load_data(csv_path)
    
    assert isinstance(data, Dataset), "Expected a Dataset object"

def test_missing_columns(create_csv):
    """Test CSV with missing required columns."""
    content = "user_id,rating\n1,5\n2,4"
    csv_path = create_csv(content)

    with pytest.raises(ValueError, match="CSV file is missing required columns"):
        load_data(csv_path)

def test_empty_csv(create_csv):
    """Test empty CSV file."""
    content = "user_id,movie_id,rating\n"
    csv_path = create_csv(content)

    data = load_data(csv_path)
    
    assert isinstance(data, Dataset), "Expected a Dataset object even if empty"

def test_invalid_data_types(create_csv):
    """Test CSV with invalid data types."""
    content = "user_id,movie_id,rating\nabc,101,5\n2,xyz,4\n3,103,three"
    csv_path = create_csv(content)

    with pytest.raises(ValueError):
        load_data(csv_path)

def test_out_of_range_ratings(create_csv):
    """Test CSV with out-of-range ratings."""
    content = "user_id,movie_id,rating\n1,101,6\n2,102,0\n3,103,3"
    csv_path = create_csv(content)

    data = load_data(csv_path)

    assert isinstance(data, Dataset), "Expected a Dataset object even with out-of-range ratings"

def test_single_row_csv(create_csv):
    """Test CSV with only one row of data."""
    content = "user_id,movie_id,rating\n1,101,5"
    csv_path = create_csv(content)

    data = load_data(csv_path)

    assert isinstance(data, Dataset), "Expected a Dataset object with a single row"
