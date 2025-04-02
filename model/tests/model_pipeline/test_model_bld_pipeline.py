import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from model.model_pipeline.ratings_loader import load_data
from model.model_pipeline.model_training import train_svd
from model.model_pipeline.model_evaluation import evaluate_model
from model.model_pipeline.model_prediction import predict

@pytest.fixture(scope="module")
def test_csv():
    filename = "test_ratings.csv"
    data = pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5],
        'movie_id': [100, 101, 102, 103, 104],
        'rating': [4.0, 3.5, 5.0, 2.0, 4.5]
    })
    data.to_csv(filename, index=False)
    yield filename
    os.remove(filename)

# def test_load_data(test_csv):
#     data = load_data(test_csv)
#     assert isinstance(data, pd.DataFrame)
#     assert len(data) == 5

def test_train_svd(test_csv):
    data = load_data(test_csv)
    model, test_data = train_svd(data)
    assert model is not None
    assert len(test_data) > 0

def test_evaluate_model(test_csv):
    data = load_data(test_csv)
    model, test_data = train_svd(data)
    rmse, mae = evaluate_model(model, test_data)
    assert rmse >= 0
    assert mae >= 0

def test_predict(test_csv):
    data = load_data(test_csv)
    model, _ = train_svd(data)
    prediction = predict(model, 1, 100)
    assert 0 <= prediction <= 5

# @patch("builtins.print")
# def test_main_execution(mock_print, test_csv):
#     from main import main
#     with patch("model.model_pipeline.ratings_loader.load_data", return_value=pd.read_csv(test_csv)):
#         with patch("model.model_pipeline.model_training.train_svd", return_value=(MagicMock(), [(1, 100, 4.0)])):
#             with patch("model.model_pipeline.model_evaluation.evaluate_model", return_value=(1.0, 0.5)):
#                 with patch("model.model_pipeline.model_prediction.predict", return_value=3.8):
#                     main()
#                     mock_print.assert_any_call("Final Model Performance - RMSE: 1.0000, MAE: 0.5000")
#                     mock_print.assert_any_call("Predicted Rating for User 1 and Movie 100: 3.80")
