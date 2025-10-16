from flask import Flask
from settings import Config
from Services.model_service import ModelService
from Api.routes import api_bp
from Web.routes import web_bp
from flask_jwt_extended import JWTManager
from admin_panel.routes import admin_bp
from auth.routes import auth_bp
from collections import deque


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration from Config class

    # Initialize ModelService and store in app config
    app.config["MODEL_SERVICE"] = ModelService(app.config["MODEL_PATH"])

    # Store the latest N predictions (input + output) in a deque
    app.config["PRED_LOG"] = deque(maxlen=200)

    # Initialize JWT manager for authentication
    jwt = JWTManager(app)

    # Register blueprints for different parts of the application
    app.register_blueprint(web_bp)      # "/" – main website
    app.register_blueprint(api_bp)      # "/health", "/model-info", "/predict", ...
    app.register_blueprint(auth_bp)     # "/auth" – authentication endpoints
    app.register_blueprint(admin_bp)    # "/admin" – admin panel endpoints

    return app

if __name__ == "__main__":
    app = create_app()
    # Run the Flask development server
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
