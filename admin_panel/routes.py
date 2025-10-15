from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")



def admin_required(fn):
    # Tiny decorator enforcing role=admin from JWT claims
    from functools import wraps
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Admin only"}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.get("model-info")
@admin_required
def admin_model_info():
    svc = current_app.config["MODEL_SERVICE"]
    return jsonify(svc.model_info())

@admin_bp.post("reload-model")
@admin_required
def reload_model():
    """Reload model from disk (hot-reload)."""
    svc = current_app.config["MODEL_SERVICE"]
    # Recreate the internal model by setting _model to None and touching .model
    svc._model = None
    _ = svc.model  # triggers reload
    return jsonify({"status": "reloaded", "model_file": svc.model_path})

@admin_bp.post("predict-batch")
@admin_required
def predict_batch():
    """
    Body: a JSON array of wine payloads.
    Returns predictions (and probs) for all.
    """
    svc = current_app.config["MODEL_SERVICE"]
    items = request.get_json(silent=True)
    if not isinstance(items, list) or not items:
        return jsonify({"error": "Send a non-empty JSON array"}), 400

    preds, probs = [], []
    for it in items:
        try:
            res = svc.predict_one(it)
            preds.append(res["prediction"])
            probs.append(res["proba"])
        except Exception as e:
            preds.append(None)
            probs.append(None)

    return jsonify({
        "count": len(items),
        "predictions": preds,
        "proba": probs,
        "classes": ["low","medium","high"]
    })
