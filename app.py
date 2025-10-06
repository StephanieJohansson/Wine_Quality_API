from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# === 1) Ladda din SPARADE pipeline (scaler + RF) ===
# Byt filnamn här om du sparade baseline-varianten istället.
MODEL_PATH = "wine_rf_pipeline.pkl"
model = joblib.load(MODEL_PATH)

# === 2) Definiera exakt feature-ordning som modellen tränades på ===
# Du tränade på numeriska features + one-hot för 'type' (drop_first=True => 'type_white').
FEATURES = [
    "fixed acidity",
    "volatile acidity",
    "citric acid",
    "residual sugar",
    "chlorides",
    "free sulfur dioxide",
    "total sulfur dioxide",
    "density",
    "pH",
    "sulphates",
    "alcohol",
    "type_white"   # 1 = white, 0 = red
]

# Hjälpare för att bygga DataFrame korrekt
def payload_to_df(payload: dict) -> pd.DataFrame:
    """
    Accepterar antingen:
    - { ... alla kemiska värden ..., "type": "red"/"white" }
    - eller { ... alla kemiska värden ..., "type_white": 0/1 }
    Returnerar en DataFrame med exakt FEATURES-ordningen.
    """
    payload = payload.copy()

    # Stötta 'type' som sträng
    if "type" in payload and "type_white" not in payload:
        t = str(payload["type"]).strip().lower()
        payload["type_white"] = 1 if t == "white" else 0
        del payload["type"]

    # Säkerställ att alla features finns
    for f in FEATURES:
        if f not in payload:
            raise ValueError(f"Saknad feature i payload: '{f}'")

    # Bygg DF i exakt rätt kolumnordning
    X = pd.DataFrame([[payload[f] for f in FEATURES]], columns=FEATURES)

    # Konvertera till numeriskt (om tex pH kommer in som sträng)
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="raise")

    return X

@app.get("/health")
def health():
    return jsonify({"status": "ok", "model_loaded": True, "features": FEATURES})

@app.get("/model-info")
def model_info():
    # Klassenamn + ev. parametrar
    try:
        rf = model.named_steps["rf"]
        params = rf.get_params()
        classes = getattr(rf, "classes_", None)
    except Exception:
        params = {}
        classes = None
    return jsonify({
        "model_file": MODEL_PATH,
        "pipeline_steps": list(getattr(model, "named_steps", {}).keys()),
        "classes": list(classes) if classes is not None else None,
        "params": {k: (str(v) if not isinstance(v, (int, float, str, bool)) else v) for k, v in params.items()}
    })

@app.post("/predict")
def predict():
    """
    Exempel-JSON:
    {
      "fixed acidity": 7.2,
      "volatile acidity": 0.23,
      "citric acid": 0.32,
      "residual sugar": 8.5,
      "chlorides": 0.058,
      "free sulfur dioxide": 47,
      "total sulfur dioxide": 186,
      "density": 0.9956,
      "pH": 3.19,
      "sulphates": 0.40,
      "alcohol": 9.9,
      "type": "white"        // eller "type_white": 1
    }
    """
    try:
        payload = request.get_json(force=True)
        X = payload_to_df(payload)

        # Prediktion + sannolikheter (om stöds)
        y_pred = model.predict(X)
        proba = getattr(model, "predict_proba", None)
        probs = proba(X)[0].tolist() if proba else None
        classes = getattr(model.named_steps["rf"], "classes_", None)
        classes = classes.tolist() if classes is not None else None

        return jsonify({
            "input": payload,
            "features_order": FEATURES,
            "prediction": y_pred[0],
            "proba": probs,
            "classes": classes
        })
    except ValueError as e:
        return jsonify({"error": str(e), "hint": f"Krävda features: {FEATURES}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Starta lokalt
    app.run(host="0.0.0.0", port=5000, debug=True)
