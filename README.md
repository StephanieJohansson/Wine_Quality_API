# Wine Quality - Maching Learning Project

This is an end-to-end maching learning workflow developed as a part of an exam assignment.

Built is using **Python**, **Scikit-learn** and **Flask**. The project predicts **wine quality** (low / medium / high) based on various chemical properties from the public *Wine Quality Dataset*.


## Project Overview

**Goal:**  
Predict wine quality (`low`, `medium`, `high`) from 11 chemical variables such as alcohol level, volatile acidity, and residual sugar.

**Technical workflow:**
1. Exploratory Data Analysis (EDA) using Jupyter Notebook  
   → distribution plots, correlations, feature relationships  
2. Model training (Linear Regression, Random Forest, Gradient Boosting)  
   → Random Forest achieved the best performance (F1 ≈ 0.80)  
3. Hyperparameter tuning with `GridSearchCV` and `RandomizedSearchCV`  
4. Model export using `joblib`  
5. RESTful API development in **Flask**  
   → serves predictions via JSON + user-friendly web UI

   -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   * GET /health
  Checks the API and model status.
  
  **Example response, used for service monitoring and debugging:**

   {
  "status": "ok",
  "model_loaded": true,
  "features": [
    "fixed acidity", "volatile acidity", "citric acid",
    "residual sugar", "chlorides", "free sulfur dioxide",
    "total sulfur dioxide", "density", "pH",
    "sulphates", "alcohol", "type_white"
  ]
}

* GET /model-info
Returns metadata about the trained model, including pipeline structure and hyperparameters.

**Example response, useful for transparency, documentration and reproducibility:**

{
  "model_file": "wine_rf_pipeline.pkl",
  "pipeline_steps": ["scaler", "rf"],
  "classes": ["low", "medium", "high"],
  "params": {
    "n_estimators": 400,
    "max_depth": null,
    "max_features": "sqrt",
    "min_samples_split": 2,
    "min_samples_leaf": 1
  }
}


* POST /predict
  Main prediction endpoint. Takes a wine sample's chemical properties as JSON and return predicted quality class.

  **Example request:**

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
  "type": "white"
}

  **Example response:**

  {
  "prediction": "medium",
  "proba": [0.0, 0.05, 0.95],
  "classes": ["low", "medium", "high"]
}
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Project structure:

Wine_Quality_API/
│

├── app.py                  # Main Flask app

├── settings.py             # Config class

├── Services/

│   └── model_service.py    # Handles model loading & prediction logic

├── Api/

│   └── routes.py           # Defines endpoints

├── templates/

│   └── index.html          # Web UI

├── static/

│   └── style.css           # Frontend styling

└── wine_rf_pipeline.pkl    # Saved trained model



`App.py` : Starting the API and load configurations. Import routes and model service

`config.py`/`settings.py` : configurations with global settings like file-routes, secret keys and debug.

`Api/routes.py` : Flask blueprint (routes). Defines endpoints (/predict, /health, /model-info). Every route describes a function which runs when the URL calls.

`Service/model_service.py` : Backend-logic. Storing all logics to read the model, handling input data, predicts results and return them.

`templates/index_html` : Frontend. The webbsite itself that a user can use like pick the wines properties and click "predict" to get a result. 

`static/style.css` : styling to the HTML page

`wine_rf_pipeline.pkl` : saved model
