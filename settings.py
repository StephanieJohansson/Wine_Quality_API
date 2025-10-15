import os
class Config:
    MODEL_PATH = os.getenv("MODEL_PATH", "wine_rf_pipeline.pkl")
    DEBUG = True

# JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_in_production")
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # (seconds) 1 hour