import time
from surprise import SVD
from surprise.model_selection import train_test_split, GridSearchCV
import joblib

def train_svd(data):
    """Trains an SVD model with hyperparameter tuning."""
    train, test = train_test_split(data, test_size=0.2, shuffle=True)

    param_grid_svd = {
        'n_factors': [50, 100, 150],
        'n_epochs': [10, 20, 30],
        'lr_all': [0.002, 0.005, 0.01],
        'reg_all': [0.02, 0.05, 0.1]
    }

    svd = GridSearchCV(SVD, param_grid_svd, measures=['rmse', 'mae'], cv=4, n_jobs=-1)
    svd.fit(data)

    best_params_svd = svd.best_params['rmse']
    print("Best Parameters for SVD:", best_params_svd)
    joblib.dump(best_params_svd, "cf_svd_model.pkl") 

    best_svd = SVD(**best_params_svd)

    start_time = time.perf_counter()
    best_svd.fit(train)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed Training Time for SVD: {elapsed_time:.2f} seconds")

    return best_svd, test
