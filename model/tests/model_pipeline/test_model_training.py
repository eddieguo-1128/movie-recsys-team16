import pytest
import joblib
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from model.model_pipeline.model_training import train_svd
import pandas as pd
from io import StringIO

@pytest.fixture
def sample_data():
    """Creates a small sample dataset for testing without user input."""
    data_str = StringIO("""user item rating
                          1 101 5
                          1 102 3
                          1 103 4
                          2 101 4
                          2 102 2
                          2 103 1
                          3 101 3
                          3 102 5
                          3 103 4""")

    df = pd.read_csv(data_str, sep=r'\s+')
    
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['user', 'item', 'rating']], reader)
    return data


def test_train_svd_runs(sample_data):
    """Test that train_svd runs without errors and returns expected outputs."""
    model, test_set = train_svd(sample_data)

    assert isinstance(model, SVD), "The returned model should be an instance of SVD."
    assert len(test_set) > 0, "The test set should not be empty."

def test_best_params_saved():
    """Test that the best parameters are saved to a file."""
    params_file = "cf_svd_model.pkl"
    
    # Ensure the file is created
    best_params = joblib.load(params_file)
    assert isinstance(best_params, dict), "The saved best parameters should be a dictionary."
    assert all(param in best_params for param in ['n_factors', 'n_epochs', 'lr_all', 'reg_all']), "Best parameters should contain necessary keys."

if __name__ == "__main__":
    pytest.main()
