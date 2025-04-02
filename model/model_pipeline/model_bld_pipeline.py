import os
from model.model_pipeline.ratings_loader import load_data
from model.model_pipeline.model_training import train_svd
from model.model_pipeline.model_evaluation import evaluate_model
from model.model_pipeline.model_prediction import predict
# from data_quality import check_schema, detect_data_drift
import pandas as pd

def main():
    # Get the absolute path of the project root (move up two levels)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Moves out of model-pipeline
    DATA_DIR = os.path.join(BASE_DIR, "data")  # Ensure 'data' is directly inside 'model'
    csv_file = os.path.join(DATA_DIR, "ratings.csv")  # Full path to ratings.csv


    # Ensure the file exists
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Error: '{csv_file}' not found. Ensure it is inside 'model/data/'.")

    # Load data
    data = load_data(csv_file)

    # Train model
    model, test = train_svd(data)

    # Evaluate model
    rmse, mae = evaluate_model(model, test)
    print(f"Final Model Performance - RMSE: {rmse:.4f}, MAE: {mae:.4f}")

    # Sample Prediction
    sample_user = 1
    sample_movie = 100
    predicted_rating = predict(model, sample_user, sample_movie)
    print(f"Predicted Rating for User {sample_user} and Movie {sample_movie}: {predicted_rating:.2f}")

    # Data Quality Checks
    # df_reference = pd.read_csv(csv_file)  # Assuming this is the reference dataset
    # df_new = pd.read_csv(csv_file)  # Load a new dataset to compare

    # required_columns = {"user_id", "movie_id", "rating"}
    # check_schema(df_new, required_columns)
    # detect_data_drift(df_new, df_reference, column="rating")

if __name__ == "__main__":
    main()