import os

# This file centralizes configuration for my Flask app.
# By using a separate settings.py, I keep secrets, paths, and environment-specific options
# out of my main code, making it easier to manage, override, and keep secure.
# You can also easily switch configs for development, testing, and production.

class Config:
    MODEL_PATH = os.getenv("MODEL_PATH", "wine_rf_pipeline.pkl")
    DEBUG = True

    # JWT configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_in_production")
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # (seconds) 1 hour