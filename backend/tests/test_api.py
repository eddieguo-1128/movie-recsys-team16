import pytest
from app import create_app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_recommend_valid_user(client, mocker):
    """Ensure API returns a valid response for a known user."""
    mock_recommendations = ["movie1+2020", "movie2+2019", "movie3+2018"]

    mocker.patch("app.model.get_recommendations", return_value=mock_recommendations)

    response = client.get("/recommend/123")
    assert response.status_code == 200
    assert response.text  # Ensure response is not empty
    assert "," in response.text  # Ensure it's a comma-separated list

def test_recommend_invalid_user(client, mocker):
    """Ensure API returns fallback movies for an unknown user instead of an empty response."""
    mock_fallback_movies = ["fallback1+2000", "fallback2+2001"]

    mocker.patch("app.model.get_recommendations", return_value=mock_fallback_movies)

    response = client.get("/recommend/9999")
    assert response.status_code == 200
    assert response.text  # Ensure response is not empty
    assert len(response.text.split(",")) > 0  # Ensure some movies are returned

def test_recommend_non_integer_user(client):
    """Ensure API rejects non-integer user IDs."""
    response = client.get("/recommend/invalid")
    assert response.status_code == 404  # Flask should reject non-integer routes
