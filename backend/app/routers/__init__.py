from flask import Flask, jsonify
from app.routers.recommend import recommend_blueprint
import socket
import os

INSTANCE_NAME = socket.gethostname()
MODEL_VERSION = os.getenv("MODEL_VERSION", "v0")

def register_blueprints(app):
    app.register_blueprint(recommend_blueprint)

    @app.route("/") # pragma: no cover
    def root():
        return jsonify({"message": f"Hello! This response is from instance: {INSTANCE_NAME}, Model Version: {MODEL_VERSION}"})
    @app.route('/healthz')
    def health():
        return jsonify({'status': 'ok'}), 200
