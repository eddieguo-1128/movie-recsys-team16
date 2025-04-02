import os
from dotenv import load_dotenv

env_file = ".env.prod" if os.getenv("FLASK_ENV", "dev") == "prod" else ".env"
load_dotenv(env_file)  # Load environment variables


class Config:
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8081))
    FLASK_ENV = os.getenv("FLASK_ENV", "dev")
    DEBUG = FLASK_ENV == "dev"  # Enables debug mode only if set to 'development'
