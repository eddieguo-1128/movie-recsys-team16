import pandas as pd
from surprise import Dataset, Reader

def load_data(csv_file): # pragma: no cover
    """Loads ratings data from a CSV file."""
    df_ratings = pd.read_csv(csv_file)

    # Schema Enforcement
    required_columns = {"user_id", "movie_id", "rating"}
    if not required_columns.issubset(df_ratings.columns):
        raise ValueError(f"CSV file is missing required columns: {required_columns - set(df_ratings.columns)}")
    
    # Handle missing values
    if df_ratings.isnull().sum().sum() > 0:
        print("Warning: Missing values detected. Dropping rows with missing values.")
        df_ratings.dropna(inplace=True)

    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df_ratings[['user_id', 'movie_id', 'rating']], reader)
    return data
