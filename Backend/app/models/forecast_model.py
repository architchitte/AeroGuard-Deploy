"""
Forecast Model Wrapper

Handles model loading, training, and predictions for air quality forecasting.
"""

import os
import json
from typing import Dict, List, Tuple, Optional
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor


class ForecastModel:
    """
    Air quality forecasting model wrapper.

    Handles training, saving, loading, and making predictions for
    air quality parameters using ensemble methods.
    """

    SUPPORTED_MODELS = ["random_forest", "xgboost", "ensemble"]
    SUPPORTED_PARAMETERS = ["pm25", "pm10", "no2", "o3", "so2", "co"]

    def __init__(self, model_type: str = "ensemble", random_state: int = 42):
        """
        Initialize the forecast model.

        Args:
            model_type: Type of model ('random_forest', 'xgboost', or 'ensemble')
            random_state: Random seed for reproducibility
        """
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(f"Model type must be one of {self.SUPPORTED_MODELS}")

        self.model_type = model_type
        self.random_state = random_state
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        self.feature_names = None

    def _create_model(self):
        """Create base model based on model_type."""
        if self.model_type == "random_forest":
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                random_state=self.random_state,
                n_jobs=-1,
            )
        elif self.model_type == "xgboost":
            return XGBRegressor(
                n_estimators=100,
                max_depth=7,
                learning_rate=0.1,
                random_state=self.random_state,
                n_jobs=-1,
            )
        else:  # ensemble
            return {
                "rf": RandomForestRegressor(
                    n_estimators=50,
                    max_depth=12,
                    random_state=self.random_state,
                    n_jobs=-1,
                ),
                "xgb": XGBRegressor(
                    n_estimators=50,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=self.random_state,
                    n_jobs=-1,
                ),
            }

    def train(
        self,
        X: np.ndarray,
        y_dict: Dict[str, np.ndarray],
        test_size: float = 0.2,
    ) -> Dict[str, float]:
        """
        Train the model on provided data.

        Args:
            X: Feature matrix (n_samples, n_features)
            y_dict: Dictionary of target variables {parameter: array}
            test_size: Proportion of data to use for testing

        Returns:
            Dictionary with training metrics for each parameter
        """
        if X.shape[0] == 0:
            raise ValueError("Training data cannot be empty")

        self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]
        metrics = {}

        for parameter, y in y_dict.items():
            if parameter not in self.SUPPORTED_PARAMETERS:
                continue

            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            self.scalers[parameter] = scaler

            # Create and train model
            if self.model_type == "ensemble":
                models = self._create_model()
                for model_name, model in models.items():
                    model.fit(X_scaled, y)
                self.models[parameter] = models
            else:
                model = self._create_model()
                model.fit(X_scaled, y)
                self.models[parameter] = model

            # Calculate R² score
            r2_score = self._calculate_r2(X_scaled, y, parameter)
            metrics[parameter] = r2_score

        self.is_trained = True
        return metrics

    def predict(
        self, X: np.ndarray, parameter: str = "pm25"
    ) -> np.ndarray:
        """
        Make predictions using the trained model.

        Args:
            X: Feature matrix for prediction
            parameter: Air quality parameter to predict

        Returns:
            Predicted values as numpy array
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")

        if parameter not in self.models:
            raise ValueError(
                f"Model not trained for parameter '{parameter}'. "
                f"Available: {list(self.models.keys())}"
            )

        # Scale features using parameter's scaler
        scaler = self.scalers[parameter]
        X_scaled = scaler.transform(X)

        # Make predictions
        if self.model_type == "ensemble":
            models = self.models[parameter]
            pred_rf = models["rf"].predict(X_scaled)
            pred_xgb = models["xgb"].predict(X_scaled)
            predictions = (pred_rf + pred_xgb) / 2
        else:
            model = self.models[parameter]
            predictions = model.predict(X_scaled)

        # Ensure predictions are non-negative for air quality
        predictions = np.clip(predictions, 0, None)

        return predictions

    def _calculate_r2(self, X_scaled: np.ndarray, y: np.ndarray, parameter: str) -> float:
        """Calculate R² score for the model."""
        model = self.models[parameter]
        if self.model_type == "ensemble":
            models = model
            pred_rf = models["rf"].score(X_scaled, y)
            pred_xgb = models["xgb"].score(X_scaled, y)
            return (pred_rf + pred_xgb) / 2
        else:
            return model.score(X_scaled, y)

    def save(self, model_path: str) -> bool:
        """
        Save the trained model to disk.

        Args:
            model_path: Path to save the model

        Returns:
            True if successful
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model")

        os.makedirs(os.path.dirname(model_path) or ".", exist_ok=True)

        # Save model, scalers, and metadata
        joblib.dump(self.models, f"{model_path}_models.pkl")
        joblib.dump(self.scalers, f"{model_path}_scalers.pkl")

        metadata = {
            "model_type": self.model_type,
            "feature_names": self.feature_names,
            "supported_parameters": list(self.models.keys()),
        }
        with open(f"{model_path}_metadata.json", "w") as f:
            json.dump(metadata, f)

        return True

    def load(self, model_path: str) -> bool:
        """
        Load a trained model from disk.

        Args:
            model_path: Path to load the model from

        Returns:
            True if successful
        """
        try:
            self.models = joblib.load(f"{model_path}_models.pkl")
            self.scalers = joblib.load(f"{model_path}_scalers.pkl")

            with open(f"{model_path}_metadata.json", "r") as f:
                metadata = json.load(f)

            self.model_type = metadata["model_type"]
            self.feature_names = metadata["feature_names"]
            self.is_trained = True

            return True
        except FileNotFoundError:
            raise FileNotFoundError(f"Model files not found at {model_path}")

    def get_feature_importance(self, parameter: str) -> Optional[Dict[str, float]]:
        """
        Get feature importance for a specific parameter.

        Args:
            parameter: Air quality parameter

        Returns:
            Dictionary of feature importance scores or None
        """
        if not self.is_trained or parameter not in self.models:
            return None

        model = self.models[parameter]

        if self.model_type == "ensemble":
            rf_importance = model["rf"].feature_importances_
            xgb_importance = model["xgb"].feature_importances_
            importance = (rf_importance + xgb_importance) / 2
        else:
            importance = model.feature_importances_

        return {
            name: float(score)
            for name, score in zip(self.feature_names or [], importance)
        }
