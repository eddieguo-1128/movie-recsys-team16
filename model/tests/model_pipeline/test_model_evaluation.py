import pytest
from unittest.mock import MagicMock, patch
from model.model_pipeline.model_evaluation import evaluate_model
from surprise import Prediction, accuracy

@pytest.fixture
def mock_predictions():
    """Creates a list of mock predictions for testing."""
    return [
        Prediction(uid=1, iid=100, r_ui=4.0, est=3.8, details={}),
        Prediction(uid=2, iid=101, r_ui=5.0, est=4.7, details={}),
        Prediction(uid=3, iid=102, r_ui=2.0, est=2.5, details={}),
    ]

@patch("model_pipeline.model_evaluation.accuracy.rmse", return_value=0.3)
@patch("model_pipeline.model_evaluation.accuracy.mae", return_value=0.2)
def test_evaluate_model(mock_rmse, mock_mae, mock_predictions):
    """Test if evaluate_model correctly calculates RMSE and MAE."""
    
    # Mock model with test method
    mock_model = MagicMock()
    mock_model.test.return_value = mock_predictions

    # Call function
    rmse, mae = evaluate_model(mock_model, "mock_test_data")

    # Assertions
    assert rmse == 0.3
    assert mae == 0.2

    # Ensure the model's test method was called once
    mock_model.test.assert_called_once_with("mock_test_data")

    # Ensure accuracy functions were called
    mock_rmse.assert_called_once()
    mock_mae.assert_called_once()
