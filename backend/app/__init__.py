from flask import Flask
from app.routers import register_blueprints
from config.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register routes
    register_blueprints(app)

    return app
