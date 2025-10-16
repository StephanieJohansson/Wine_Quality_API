import joblib
import pandas as pd
from typing import Dict, List, Any

class ModelService:
   
    # Encapsulates the model and all logic for transforming input data and making predictions.
    # This makes the prediction code object-oriented, reusable, and easy to test.
    

    # List of features expected by the model after preprocessing.
    # This ensures that input data is always in the correct format and order.
    FEATURES: List[str] = [
        "fixed acidity","volatile acidity","citric acid","residual sugar","chlorides",
        "free sulfur dioxide","total sulfur dioxide","density","pH","sulphates",
        "alcohol","type_white"
    ]

    def __init__(self, model_path: str):
        # Store the path to the trained model file.
        # This allows you to reload or swap models without changing code elsewhere.
        self.model_path = model_path
        self._model = None  # Internal cache for the loaded model (lazy loading).

    @property
    def model(self):
        # Loads the model from disk only once (lazy loading).
        # This avoids repeated disk reads and speeds up predictions.
        if self._model is None:
            self._model = joblib.load(self.model_path)
        return self._model

    def payload_to_df(self, payload: Dict[str, Any]) -> pd.DataFrame:
        
        # Converts incoming payload (dict) to a pandas DataFrame in the correct format for prediction.
        # - Handles one-hot encoding for wine type ("type_white").
        # - Raises ValueError if any required feature is missing.
        # This method ensures that all predictions use consistent, validated input data.
        
        data = dict(payload)
        # Convert "type" to "type_white" for model compatibility (one-hot encoding).
        if "type" in data and "type_white" not in data:
            t = str(data["type"]).strip().lower()
            data["type_white"] = 1 if t == "white" else 0
            del data["type"]
        # Ensure all required features are present in the input.
        for f in self.FEATURES:
            if f not in data:
                raise ValueError(f"Missing feature in payload: '{f}'")
        # Create DataFrame with correct feature order for the model.
        X = pd.DataFrame([[data[f] for f in self.FEATURES]], columns=self.FEATURES)
        # Ensure all values are numeric to avoid prediction errors.
        for c in X.columns:
            X[c] = pd.to_numeric(X[c], errors="raise")
        return X

    def predict_one(self, payload: dict) -> dict:
        
        # Runs a single prediction using the model.
        # - Converts input to DataFrame.
        # - Predicts class and probabilities.
        #  Normalizes class order for frontend consistency.
        # Returns a dict with prediction, probabilities, class labels, and feature order.
       # This method is the main entry point for API predictions.
     
        X = self.payload_to_df(payload)

        y = self.model.predict(X)[0]
        proba_fn = getattr(self.model, "predict_proba", None)
        probs = proba_fn(X)[0].tolist() if proba_fn else None
        # Get class labels from the RandomForest step in the pipeline.
        classes = getattr(self.model.named_steps["rf"], "classes_", None)
        classes = classes.tolist() if classes is not None else None

        # Normalize class order to ["low","medium","high"] for consistent frontend display.
        if probs is not None and classes is not None:
            desired = ["low", "medium", "high"]
            idx = {c: i for i, c in enumerate(classes)}
            if all(c in idx for c in desired):
                probs = [float(probs[idx[c]]) for c in desired]
                classes = desired

        return {
            "prediction": y,
            "proba": probs,
            "classes": classes,
            "features_order": self.FEATURES,
        }

    def model_info(self) -> Dict[str, Any]:
        
        # Returns metadata about the model:
        # - File path
        # - Pipeline steps
        # - Class labels
        # - Random Forest parameters
        # Useful for admin endpoints, debugging, and transparency.
        
        try:
            rf = self.model.named_steps["rf"]
            params = rf.get_params()
            classes = getattr(rf, "classes_", None)
        except Exception:
            params, classes = {}, None
        return {
            "model_file": self.model_path,
            "pipeline_steps": list(getattr(self.model, "named_steps", {}).keys()),
            "classes": list(classes) if classes is not None else None,
            "params": {k: (str(v) if not isinstance(v, (int, float, str, bool)) else v)
                       for k, v in params.items()}
        }
    
    def feature_importance(self):
        
       # Returns feature importances if supported by the model (Random Forest does).
       # - Output is sorted by importance descending.
       # - Useful for explainability and admin panel.
       # If not supported, returns a flag and error message.
        
        try:
            rf = self.model.named_steps.get("rf")
            importances = getattr(rf, "feature_importances_", None)
            if importances is None:
                return {"supports_importance": False}

            # Match feature names to importances (order after preprocessing).
            feats = list(self.FEATURES)
            out = [
                {"feature": f, "importance": float(i)}
                for f, i in zip(feats, importances)
            ]
            # Sort by importance, highest first for easier interpretation.
            out.sort(key=lambda x: x["importance"], reverse=True)
            return {"supports_importance": True, "importances": out}
        except Exception as e:
            # If anything goes wrong, return error info for debugging.
            return {"supports_importance": False, "error": str(e)}