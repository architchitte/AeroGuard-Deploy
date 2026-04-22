import os
import json
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import keras
from fastapi import HTTPException

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

def safe_load_keras_model(model_path):
    """
    Helper to load Keras models with a fallback for 'quantization_config' version mismatches.
    """
    try:
        return keras.models.load_model(model_path)
    except TypeError as e:
        if "quantization_config" in str(e):
            # Fallback for Colab-to-Local Keras 3 migrations with unexpected keys
            print(f"DEBUG: Falling back to compile=False due to version mismatch: {e}")
            return keras.models.load_model(model_path, compile=False)
        raise e

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
        print(f"DEBUG: scaler_X loaded: {scaler_X is not None}")
        scaler_y = joblib.load(os.path.join(ARTIFACT_DIR, "scaler_y.joblib"))
        print(f"DEBUG: scaler_y loaded: {scaler_y is not None}")
        
        # Load XGBoost (.joblib) and LSTM (.keras) models
        model_xgboost = joblib.load(os.path.join(ARTIFACT_DIR, "xgb_model.joblib"))
        print(f"DEBUG: model_xgboost loaded: {model_xgboost is not None}")
        
        # Use native Keras 3 functional model loader with safe fallback
        model_lstm = safe_load_keras_model(os.path.join(ARTIFACT_DIR, "lstm_model.keras"))
        print(f"DEBUG: model_lstm loaded: {model_lstm is not None}")




        
        # Load SARIMA models iteratively based on TARGETS or target
        # Support both 'TARGETS' (list) and 'target' (string) for flexibility
        targets = pipeline_config.get("TARGETS", [])
        if not targets and "target" in pipeline_config:
            targets = [pipeline_config["target"]]
            
        for target in targets:
            # Try both sarima_{target}.pkl and sarima_model.pkl (fallback)
            paths_to_try = [
                os.path.join(ARTIFACT_DIR, f"sarima_AQI.pkl"),
                os.path.join(ARTIFACT_DIR, "sarima_model.pkl")
            ]
            
            loaded = False
            for sarima_path in paths_to_try:
                if os.path.exists(sarima_path):
                    with open(sarima_path, "rb") as f:
                        models_sarima[target] = pickle.load(f)
                    loaded = True
                    break
            
            if not loaded:
                print(f"Warning: SARIMA model for target {target} not found.")


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
    global scaler_X, scaler_y, pipeline_config, ensemble_weights, model_xgboost, model_lstm, models_sarima

    if scaler_X is None or scaler_y is None:
        raise HTTPException(status_code=503, detail="ML scalers failed to load. Check server artifacts.")

    if model_xgboost is None:
        raise HTTPException(status_code=503, detail="XGBoost model failed to load. Please check artifacts/xgb_model.joblib.")

    if model_lstm is None:
        raise HTTPException(status_code=503, detail="LSTM model failed to load. Please check artifacts/lstm_model.keras.")



    # Safety check: Ensure scalers are fitted before calling transform/inverse_transform

    if not hasattr(scaler_X, "n_features_in_") or not hasattr(scaler_y, "n_features_in_"):
        raise ValueError("Loaded scalers appear to be unfitted. Check if scaler_X.joblib and scaler_y.joblib are valid fitted objects.")


    # Support both 'TARGETS' (list) and 'target' (string)
    targets = pipeline_config.get("TARGETS", [])
    if not targets and "target" in pipeline_config:
        targets = [pipeline_config["target"]]
        
    if not targets:
        raise ValueError("Pipeline configuration is missing TARGETS list or 'target' key.")


    # 1. Convert features to a Pandas DataFrame to maintain feature names and avoid warnings
    # Input 'features' is expected to be a 2D array of shape (7, 11)
    feature_names = pipeline_config.get("feature_cols", [])
    if not feature_names:
        # Fallback to numpy if names are missing
        X_raw = np.array(features)
    else:
        X_raw = pd.DataFrame(features, columns=feature_names)
    
    # Scale directly on the 2D array/DataFrame (7 rows x 11 features)
    X_scaled = scaler_X.transform(X_raw)

    # 2. Run inference on LSTM
    # LSTM expects 3D input: (batch_size, timesteps, features) -> (1, 7, 11)
    lstm_input = X_scaled.reshape(1, 7, 11)
    lstm_pred_scaled = model_lstm.predict(lstm_input, verbose=0)
    
    # 3. Run inference on XGBoost
    # XGBoost expects a flattened 2D input for the full lookback -> (1, 77)
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
