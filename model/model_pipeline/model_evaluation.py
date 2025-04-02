from surprise import accuracy

def evaluate_model(model, test):
    """Evaluates the trained model on test data."""
    predictions = model.test(test)
    rmse = accuracy.rmse(predictions)
    mae = accuracy.mae(predictions)
    return rmse, mae
