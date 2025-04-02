def predict(model, user_id, movie_id):
    """Generates a prediction for a given user and movie."""
    prediction = model.predict(user_id, movie_id)
    return prediction.est  # Estimated rating
