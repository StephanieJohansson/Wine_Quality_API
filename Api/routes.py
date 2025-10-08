from flask import Blueprint, jsonify, request, current_app

api_bp = Blueprint("api", __name__, url_prefix="/")

@api_bp.get("health")
def health():
    svc = current_app.config["MODEL_SERVICE"]
    return jsonify({"status": "ok", "model_loaded": True, "features": svc.FEATURES})

@api_bp.get("model-info")
def model_info():
    svc = current_app.config["MODEL_SERVICE"]
    return jsonify(svc.model_info())

@api_bp.post("predict")
def predict():
    svc = current_app.config["MODEL_SERVICE"]
    try:
        payload = request.get_json(force=True)
        result = svc.predict_one(payload)
        result["input"] = payload
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e), "hint": f"Krävda features: {svc.FEATURES}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
