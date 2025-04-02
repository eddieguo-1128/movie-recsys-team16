from flask import Blueprint, jsonify
from app.model import get_recommendations

recommend_blueprint = Blueprint("recommend", __name__, url_prefix="/recommend")


@recommend_blueprint.route("/<int:userid>", methods=["GET"])
def recommend(userid):
    recommended_movies = get_recommendations(userid)
    return ",".join(recommended_movies)
