import os
import json
import joblib
import pickle
import numpy as np
import tensorflow as tf

# Absolute pathing for cloud-agnostic execution
BASE_ML_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACT_DIR = os.path.join(BASE_ML_DIR, "artifacts")

# Global Variables
pipeline_config = {}
ensemble_weights = {}
scaler_X = None
scaler_y = None
model_xgboost = None
model_lstm = None
models_sarima = {}  # Dictionary to hold SARIMA models per target

def _load_artifacts():
    global pipeline_config, ensemble_weights, scaler_X, scaler_y
    global model_xgboost, model_lstm, models_sarima
    
    try:
        # Load configs
        with open(os.path.join(ARTIFACT_DIR, "pipeline_config.json"), "r") as f:
            pipeline_config = json.load(f)
            
        with open(os.path.join(ARTIFACT_DIR, "ensemble_weights.json"), "r") as f:
            ensemble_weights = json.load(f)
            
        # Load scalers (.joblib as requested)
        scaler_X = joblib.load(os.path.join(ARTIFACT_DIR, "scaler_X.joblib"))
        scaler_y = joblib.load(os.path.join(ARTIFACT_DIR, "scaler_y.joblib"))
        
        # Load XGBoost (.joblib) and LSTM (.keras) models
        model_xgboost = joblib.load(os.path.join(ARTIFACT_DIR, "xgb_multi_model.joblib"))
        model_lstm = tf.keras.models.load_model(os.path.join(ARTIFACT_DIR, "lstm_model.keras"))
        
        # Load SARIMA models iteratively based on TARGETS
        targets = pipeline_config.get("TARGETS", [])
        for target in targets:
            sarima_path = os.path.join(ARTIFACT_DIR, f"sarima_{target}.pkl")
            if os.path.exists(sarima_path):
                with open(sarima_path, "rb") as f:
                    models_sarima[target] = pickle.load(f)
            else:
                print(f"Warning: SARIMA model for target {target} not found at {sarima_path}")

        print("Successfully loaded all ML artifacts for the Weighted Ensemble.")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to load ML artifacts. Inference will fail. Error: {e}")

# Load artifacts when the module is imported
_load_artifacts()

async def generate_ensemble_forecast(features: list) -> dict:
    """
    Executes inference across LSTM, XGBoost, and SARIMA models for multi-pollutant targets.
    Scales inputs, inverse-transforms outputs, and calculates weighted ensemble predictions.
    """
    if scaler_X is None or scaler_y is None:
        raise ValueError("ML models or scalers are not loaded. Ensure artifacts exist in app/ml/artifacts.")

    targets = pipeline_config.get("TARGETS", [])
    if not targets:
        raise ValueError("Pipeline configuration is missing TARGETS list.")

    # 1. Convert features to a NumPy array and scale them using scaler_X
    X_raw = np.array(features)
    X_scaled = scaler_X.transform(X_raw)

    # 2. Run inference on LSTM
    # LSTM expects 3D input: (batch_size, timesteps, features)
    lstm_input = X_scaled.reshape(1, X_scaled.shape[0], X_scaled.shape[1])
    lstm_pred_scaled = model_lstm.predict(lstm_input, verbose=0)
    
    # 3. Run inference on XGBoost
    # XGBoost typically expects 2D flattened input for lookback windows
    xgb_input = X_scaled.flatten().reshape(1, -1)
    xgb_pred_scaled = model_xgboost.predict(xgb_input)
    # Ensure it's properly reshaped to 2D for inverse transform
    if xgb_pred_scaled.ndim == 1:
        xgb_pred_scaled = xgb_pred_scaled.reshape(1, -1)

    # 4. Inverse transform LSTM and XGBoost outputs
    lstm_pred_raw = scaler_y.inverse_transform(lstm_pred_scaled)[0]
    xgb_pred_raw = scaler_y.inverse_transform(xgb_pred_scaled)[0]

    final_predictions = {}
    
    for i, target in enumerate(targets):
        # Extract predictions for this specific target
        lstm_val = float(lstm_pred_raw[i])
        xgb_val = float(xgb_pred_raw[i])
        
        # 5. Run inference on SARIMA
        sarima_val = 0.0
        if target in models_sarima:
            sarima_model = models_sarima[target]
            sarima_pred_raw = sarima_model.forecast(steps=1)
            # SARIMA natively returns unscaled values if fit on raw targets
            sarima_val = float(sarima_pred_raw.iloc[0] if hasattr(sarima_pred_raw, "iloc") else sarima_pred_raw[0])
            
        # Extract specific dynamic weights for this target
        target_weights = ensemble_weights.get(target, {"lstm": 0.33, "xgboost": 0.33, "sarima": 0.34})
        w_lstm = target_weights.get("lstm", 0.33)
        w_xgb = target_weights.get("xgboost", 0.33)
        w_sarima = target_weights.get("sarima", 0.34)
        
        # Calculate weighted final prediction
        final_val = (lstm_val * w_lstm) + (xgb_val * w_xgb) + (sarima_val * w_sarima)
        
        final_predictions[target] = {
            "ensemble_prediction": float(final_val),
            "components": {
                "lstm": lstm_val,
                "xgboost": xgb_val,
                "sarima": sarima_val
            }
        }
        
    return final_predictions
