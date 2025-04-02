import random
import joblib
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.getenv("PROJECT_ROOT", os.getcwd())
MODEL_PATH = os.path.join(PROJECT_ROOT, "model/cf_svd_model.pkl")
DATA_PATH = os.path.join(PROJECT_ROOT, "model/ratings.csv")

model = joblib.load(MODEL_PATH)
df_ratings = pd.read_csv(DATA_PATH)


def get_recommendations(user_id):
    """Returns top 20 movie recommendations for a given user."""
    known_users = set(df_ratings["user_id"].unique())
    if user_id not in known_users:
        top_movies = (df_ratings.groupby("movie_id")["rating"].mean().sort_values(ascending=False).head(50).index.tolist())
        top_movies = random.sample(top_movies, 20)
    else:
        watched_movies = set(df_ratings[df_ratings["user_id"] == user_id]["movie_id"])
        all_movie_ids = df_ratings["movie_id"].unique()
        recommendations = []
        
        for movie_id in all_movie_ids:
            if movie_id not in watched_movies:
                est_rating = model.predict(user_id, movie_id).est
                recommendations.append((movie_id, est_rating))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        top_movies = [movie_id for movie_id, _ in recommendations[:20]]
    return top_movies
