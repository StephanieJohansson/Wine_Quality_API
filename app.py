from flask import Flask
from settings import Config
from Services.model_service import ModelService
from Api.routes import api_bp
from Web.routes import web_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initiera ModelService och lägg i app-config
    app.config["MODEL_SERVICE"] = ModelService(app.config["MODEL_PATH"])

    # Registrera blueprints
    app.register_blueprint(web_bp)  # "/" – hemsida
    app.register_blueprint(api_bp)  # "/health", "/model-info", "/predict", ...

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
