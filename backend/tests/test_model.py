import pytest
import pandas as pd
import random
from app.model import get_recommendations

@pytest.fixture
def mock_ratings_data(mocker):
    """Mock the ratings dataset with a valid DataFrame."""
    mock_ratings = pd.DataFrame({
        "user_id": [1, 1, 2, 2, 3, 3],
        "movie_id": ["movie1+2020", "movie2+2019", "movie3+2018", "movie4+2017", "movie5+2016", "movie6+2015"],
        "rating": [5, 4, 3, 5, 2, 5]
    })
    mocker.patch("app.model.df_ratings", mock_ratings)

def test_get_recommendations_valid_user(mock_ratings_data, mocker):
    """Ensure model returns a list for a known user."""
    mock_model = mocker.Mock()
    mock_model.predict.return_value.est = 4.5  # Simulated rating prediction
    mocker.patch("app.model.model", mock_model)

    recommendations = get_recommendations(1)
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0  # Should return some movies

def test_get_recommendations_new_user(mock_ratings_data, mocker):
    """Ensure new users get fallback movies."""
    mocker.patch("random.sample", return_value=["fallback1+2000", "fallback2+2001", "fallback3+2002"])

    recommendations = get_recommendations(9999)
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0  # Should return some fallback movies

def test_get_recommendations_empty_model(mocker):
    """Ensure missing model does not crash function."""
    mocker.patch("app.model.model", None)  # Simulate missing model

    recommendations = get_recommendations(1)
    assert isinstance(recommendations, list)  # Should return an empty list safely
