import os
class Config:
    MODEL_PATH = os.getenv("MODEL_PATH", "wine_rf_pipeline.pkl")
    DEBUG = True
