from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps

# Create a blueprint for API endpoints, with root URL prefix
api_bp = Blueprint("api", __name__, url_prefix="/")

# Helper decorator to require admin role for certain endpoints (returns JSON error if not admin)
def admin_required_json():
    def deco(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if get_jwt().get("role") != "admin":
                return jsonify({"error": "Admin only"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return deco

# Public health check endpoint
@api_bp.get("health")
def health():
    svc = current_app.config["MODEL_SERVICE"]
    return jsonify({
        "status": "ok",
        "model_loaded": True,
        "features": svc.FEATURES
    })

# Model info endpoint (admin-only)
@api_bp.get("model-info")
@admin_required_json()
def model_info():
    svc = current_app.config["MODEL_SERVICE"]
    return jsonify(svc.model_info())

# Prediction endpoint (open to all)
@api_bp.post("predict")
def predict():
    svc = current_app.config["MODEL_SERVICE"]

    try:
        payload = request.get_json(force=True)
        result = svc.predict_one(payload)
        result["input"] = payload

        # Log the prediction (input + output) in the app's prediction log (for admin panel/history)
        log = current_app.config.get("PRED_LOG")
        if log is not None:
            log.append({
                "prediction": result.get("prediction"),
                "proba": result.get("proba"),
                "classes": result.get("classes"),
                "input": result.get("input")
            })

        return jsonify(result)

    except ValueError as e:
        # If required features are missing or invalid, return 400 with a hint
        return jsonify({
            "error": str(e),
            "hint": f"Required features: {svc.FEATURES}"
        }), 400

    except Exception as e:
        # Catch-all for unexpected errors
        return jsonify({"error": str(e)}), 500
