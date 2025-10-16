from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

# Put auth endpoints under /auth so frontend /auth/login matches
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Hard-coded users for demo purposes (username, password, role)
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user":  {"password": "user123",  "role": "user"},
}

@auth_bp.post("login")
def login():
    # Handles login requests.
    # Expects JSON: { "username": "...", "password": "..." }
    # Returns JWT token and user role if credentials are valid.
    
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    user = USERS.get(username)
    if not user or user["password"] != password:
        # Invalid credentials: return 401 Unauthorized
        return jsonify({"error": "Invalid credentials"}), 401

    # Add user role as a JWT claim for role-based access
    additional_claims = {"role": user["role"]}
    token = create_access_token(identity=username, additional_claims=additional_claims)
    # Return token and role to frontend
    return jsonify({"token": token, "role": user["role"]}), 200
