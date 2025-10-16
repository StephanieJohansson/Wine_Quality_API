from flask import Blueprint, render_template

# Create a blueprint for the web (frontend) routes
web_bp = Blueprint("web", __name__)

@web_bp.get("/")
def index():
    # Renders the main HTML page for the root URL ("/")
    # Uses Flask's template engine to serve 'index.html' from the templates folder
    return render_template("index.html")
