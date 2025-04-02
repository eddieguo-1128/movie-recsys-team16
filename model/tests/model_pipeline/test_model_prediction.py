import pytest
from unittest.mock import MagicMock
from model.model_pipeline.model_prediction import predict
from surprise import Prediction

@pytest.fixture
def mock_model():
    """Creates a mock model with a predict method."""
    mock = MagicMock()
    mock.predict.return_value = Prediction(uid=1, iid=100, r_ui=None, est=4.5, details={})
    return mock

def test_predict_valid(mock_model):
    """Test if predict() returns the correct estimated rating."""
    user_id, movie_id = 1, 100
    result = predict(mock_model, user_id, movie_id)

    # Expected estimated rating
    assert result == 4.5

    # Ensure the model's predict method was called with the correct parameters
    mock_model.predict.assert_called_once_with(user_id, movie_id)

def test_predict_invalid_user_movie(mock_model):
    """Test if predict() handles invalid user/movie IDs gracefully."""
    mock_model.predict.return_value = Prediction(uid=None, iid=None, r_ui=None, est=2.0, details={})

    result = predict(mock_model, None, None)

    # Should still return a valid estimated rating, but from a None user/movie
    assert result == 2.0

    # Ensure predict was called with None values
    mock_model.predict.assert_called_once_with(None, None)
