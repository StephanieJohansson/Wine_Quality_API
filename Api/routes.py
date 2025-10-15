from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps

api_bp = Blueprint("api", __name__, url_prefix="/")

# Hjälpdekorator för att kräva admin
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


# Publik hälso-koll
@api_bp.get("health")
def health():
    svc = current_app.config["MODEL_SERVICE"]
    return jsonify({
        "status": "ok",
        "model_loaded": True,
        "features": svc.FEATURES
    })


# Gör model-info skyddad (admin-only)
@api_bp.get("model-info")
@admin_required_json()
def model_info():
    svc = current_app.config["MODEL_SERVICE"]
    return jsonify(svc.model_info())


# Prediktion 
@api_bp.post("predict")
def predict():
    svc = current_app.config["MODEL_SERVICE"]

    try:
        payload = request.get_json(force=True)
        result = svc.predict_one(payload)
        result["input"] = payload

        # Logga prediktionen (oavsett inloggad eller ej)
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
        return jsonify({
            "error": str(e),
            "hint": f"Krävda features: {svc.FEATURES}"
        }), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
