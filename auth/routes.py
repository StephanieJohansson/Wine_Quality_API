from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__, url_prefix="/")

# Hard-coded users
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user":  {"password": "user123",  "role": "user"},
}

@auth_bp.post("login")
def login():
    """
    Request JSON:
      { "username": "admin", "password": "admin123" }
    Response:
      { "token": "..." }
    """
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    # Include role as claim so we can do admin-only checks
    additional_claims = {"role": user["role"]}
    token = create_access_token(identity=username, additional_claims=additional_claims)
    return jsonify({"token": token, "role": user["role"]}), 200
