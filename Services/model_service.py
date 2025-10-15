import joblib
import pandas as pd
from typing import Dict, List, Any

class ModelService:
    """
    Kapslar in modellen och datatransform – objektorienterat & testbart.
    """
    FEATURES: List[str] = [
        "fixed acidity","volatile acidity","citric acid","residual sugar","chlorides",
        "free sulfur dioxide","total sulfur dioxide","density","pH","sulphates",
        "alcohol","type_white"
    ]

    def __init__(self, model_path: str):
        self.model_path = model_path
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = joblib.load(self.model_path)
        return self._model

    def payload_to_df(self, payload: Dict[str, Any]) -> pd.DataFrame:
        data = dict(payload)
        if "type" in data and "type_white" not in data:
            t = str(data["type"]).strip().lower()
            data["type_white"] = 1 if t == "white" else 0
            del data["type"]
        for f in self.FEATURES:
            if f not in data:
                raise ValueError(f"Saknad feature i payload: '{f}'")
        X = pd.DataFrame([[data[f] for f in self.FEATURES]], columns=self.FEATURES)
        for c in X.columns:
            X[c] = pd.to_numeric(X[c], errors="raise")
        return X

    def predict_one(self, payload: dict) -> dict:
        X = self.payload_to_df(payload)

        y = self.model.predict(X)[0]
        proba_fn = getattr(self.model, "predict_proba", None)
        probs = proba_fn(X)[0].tolist() if proba_fn else None
        classes = getattr(self.model.named_steps["rf"], "classes_", None)
        classes = classes.tolist() if classes is not None else None

    # --- normalisera ordningen till ["low","medium","high"] ---
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
        """Returnera feature importances om modellen stödjer det (RF gör det)."""
        try:
            rf = self.model.named_steps.get("rf")
            importances = getattr(rf, "feature_importances_", None)
            if importances is None:
                return {"supports_importance": False}

            # namnsätta enligt exakt FEATUR-ordningen efter scaler/one-hot
            feats = list(self.FEATURES)
            out = [
                {"feature": f, "importance": float(i)}
                for f, i in zip(feats, importances)
            ]
            # sortera viktigast först
            out.sort(key=lambda x: x["importance"], reverse=True)
            return {"supports_importance": True, "importances": out}
        except Exception as e:
            return {"supports_importance": False, "error": str(e)}