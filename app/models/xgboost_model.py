"""XGBoost time-series forecasting model for AeroGuard.

Provides an XGBoost-based forecasting model that uses lag features and rolling
statistics as inputs. Supports iterative multi-step forecasting, evaluation,
and model persistence via joblib.
"""
from __future__ import annotations

from typing import Optional, Tuple, Dict, Any, List
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from xgboost import XGBRegressor
import joblib

logger = logging.getLogger(__name__)


class XGBoostModel:
    """XGBoost regression model for time-series AQI forecasting.

    Designed to work with lag features and rolling statistics created by
    TimeSeriesPreprocessor or DataPreprocessor. Supports iterative multi-step
    forecasting (e.g., predict next 6 hours one step at a time).

    Usage:
        model = XGBoostModel(target_col="PM2.5")
        model.train(df)  # DataFrame with lag/rolling features
        preds = model.predict(X_test, steps=6)
        metrics = model.evaluate(preds, y_test)

    Attributes:
        target_col: Name of the column to predict.
        lag_hours: List of lag hours used in feature engineering.
        rolling_windows: List of rolling window sizes used.
    """

    def __init__(
        self,
        target_col: str = "PM2.5",
        lag_hours: Optional[List[int]] = None,
        rolling_windows: Optional[List[int]] = None,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
    ) -> None:
        """Initialize XGBoost model.

        Args:
            target_col: Column name to predict.
            lag_hours: List of lag hours used in preprocessing (e.g., [1,3,6]).
                Used for feature selection during prediction.
            rolling_windows: List of rolling windows (e.g., [3,6]).
                Used for feature selection during prediction.
            n_estimators: Number of boosting rounds.
            max_depth: Maximum tree depth.
            learning_rate: Learning rate (eta).
        """
        self.target_col = target_col
        self.lag_hours = lag_hours or [1, 3, 6]
        self.rolling_windows = rolling_windows or [3, 6]
        
        self._model: Optional[XGBRegressor] = None
        self._feature_columns: Optional[List[str]] = None
        self._trained_shape: Optional[Tuple[int, int]] = None

        # XGBoost hyperparameters
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate

    def _get_expected_features(self) -> List[str]:
        """Generate expected feature column names based on config.

        Used to ensure consistency between train and inference.

        Returns:
            List of expected feature names.
        """
        features = [self.target_col]
        
        # Add lag features
        for h in self.lag_hours:
            features.append(f"{self.target_col}_lag_{h}h")
        
        # Add rolling statistics
        for w in self.rolling_windows:
            features.append(f"{self.target_col}_mean_{w}h")
            features.append(f"{self.target_col}_std_{w}h")
        
        return features

    def train(
        self,
        df: pd.DataFrame,
        split_ratio: float = 0.8,
        verbose: bool = False,
    ) -> Dict[str, float]:
        """Train XGBoost model on preprocessed time-series data.

        Args:
            df: DataFrame with lag/rolling features and target column.
            split_ratio: Train/test split (0.8 = 80% train, 20% test).
            verbose: Print training progress.

        Returns:
            Dictionary with train/test MAE and RMSE metrics.

        Raises:
            ValueError: If required columns are missing.
            RuntimeError: If model training fails.
        """
        if self.target_col not in df.columns:
            raise ValueError(f"Target column '{self.target_col}' not in DataFrame")

        expected_features = self._get_expected_features()
        missing = [f for f in expected_features if f not in df.columns]
        if missing:
            raise ValueError(f"Missing feature columns: {missing}")

        # Prepare data
        X = df[expected_features].copy()
        y = df[self.target_col].copy()

        # Remove rows with NaN
        valid_idx = X.notna().all(axis=1) & y.notna()
        X = X[valid_idx]
        y = y[valid_idx]

        if len(X) < 10:
            raise ValueError(f"Not enough valid samples: {len(X)}")

        # Split data
        split_point = int(len(X) * split_ratio)
        X_train, X_test = X[:split_point], X[split_point:]
        y_train, y_test = y[:split_point], y[split_point:]

        # Train model
        try:
            self._model = XGBRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                verbose=0,
                random_state=42,
            )
            self._model.fit(X_train, y_train, verbose=verbose)
            self._feature_columns = expected_features
            self._trained_shape = X_train.shape
        except Exception as exc:
            logger.exception("XGBoost training failed")
            raise RuntimeError(f"XGBoost training failed: {exc}") from exc

        # Evaluate on train and test sets
        y_train_pred = self._model.predict(X_train)
        y_test_pred = self._model.predict(X_test)

        metrics = {
            "train_mae": float(np.mean(np.abs(y_train - y_train_pred))),
            "train_rmse": float(np.sqrt(np.mean((y_train - y_train_pred) ** 2))),
            "test_mae": float(np.mean(np.abs(y_test - y_test_pred))),
            "test_rmse": float(np.sqrt(np.mean((y_test - y_test_pred) ** 2))),
        }

        return metrics

    def predict(
        self,
        X: pd.DataFrame,
        steps: int = 6,
        iterative: bool = True,
    ) -> List[float]:
        """Predict next values iteratively.

        For multi-step forecasting, this method:
        1. Makes a single-step prediction
        2. Updates lag features for the next step
        3. Repeats for `steps` iterations

        Args:
            X: Input DataFrame with lag/rolling features (single row or last row).
            steps: Number of steps to forecast ahead.
            iterative: If True, update features iteratively. If False, use initial features.

        Returns:
            List of predictions (length == steps).

        Raises:
            RuntimeError: If model is not trained.
            ValueError: If input features are invalid.
        """
        if self._model is None:
            raise RuntimeError("Model not trained. Call `train()` first.")
        if steps <= 0:
            return []

        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame")

        # Get the last row
        if len(X) > 1:
            X = X.iloc[-1:].copy()
        else:
            X = X.copy()

        expected = set(self._feature_columns)
        actual = set(X.columns)
        if not expected.issubset(actual):
            missing = expected - actual
            raise ValueError(f"Missing columns: {missing}")

        predictions = []
        current_row = X.iloc[0].copy()

        for _ in range(steps):
            # Get only expected features
            X_pred = current_row[self._feature_columns].to_frame().T
            pred = float(self._model.predict(X_pred)[0])
            predictions.append(pred)

            if not iterative or _ == steps - 1:
                continue

            # Update lag features for next step
            # Shift existing lags
            for h in sorted(self.lag_hours, reverse=True):
                lag_col = f"{self.target_col}_lag_{h}h"
                prev_lag_col = f"{self.target_col}_lag_{h-1}h" if h > 1 else self.target_col
                if prev_lag_col in current_row.index:
                    current_row[lag_col] = current_row[prev_lag_col]

            # Update target with prediction
            current_row[self.target_col] = pred

            # Update rolling statistics (simplified: use predicted value)
            for w in self.rolling_windows:
                mean_col = f"{self.target_col}_mean_{w}h"
                std_col = f"{self.target_col}_std_{w}h"
                current_row[mean_col] = pred
                current_row[std_col] = 0.0

        return predictions

    def evaluate(
        self,
        predictions: List[float],
        actuals: List[float],
    ) -> Dict[str, float]:
        """Evaluate predictions against ground truth.

        Args:
            predictions: List of predicted values.
            actuals: List of actual values (same length as predictions).

        Returns:
            Dict with keys: `mae`, `rmse`, `mean_actual`, `mean_pred`.

        Raises:
            ValueError: If lengths don't match.
        """
        if len(predictions) != len(actuals):
            raise ValueError(f"Length mismatch: {len(predictions)} vs {len(actuals)}")

        preds_arr = np.array(predictions, dtype=float)
        actuals_arr = np.array(actuals, dtype=float)

        mae = float(np.mean(np.abs(preds_arr - actuals_arr)))
        rmse = float(np.sqrt(np.mean((preds_arr - actuals_arr) ** 2)))

        return {
            "mae": mae,
            "rmse": rmse,
            "mean_actual": float(np.mean(actuals_arr)),
            "mean_pred": float(np.mean(preds_arr)),
        }

    def save(self, filepath: str) -> None:
        """Save trained model to disk using joblib.

        Args:
            filepath: Path to save the model.

        Raises:
            RuntimeError: If no model is trained.
        """
        if self._model is None:
            raise RuntimeError("No trained model to save")

        p = Path(filepath)
        data = {
            "model": self._model,
            "target_col": self.target_col,
            "lag_hours": self.lag_hours,
            "rolling_windows": self.rolling_windows,
            "feature_columns": self._feature_columns,
            "trained_shape": self._trained_shape,
        }

        try:
            joblib.dump(data, p)
            logger.info(f"Model saved to {filepath}")
        except Exception as exc:
            logger.exception("Failed to save XGBoost model")
            raise RuntimeError(f"Failed to save model: {exc}") from exc

    @classmethod
    def load(cls, filepath: str) -> "XGBoostModel":
        """Load a saved XGBoost model from disk.

        Args:
            filepath: Path to the saved model file.

        Returns:
            XGBoostModel instance with trained model.

        Raises:
            FileNotFoundError: If file doesn't exist.
            RuntimeError: If loading fails.
        """
        p = Path(filepath)
        if not p.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")

        try:
            data = joblib.load(p)
        except Exception as exc:
            logger.exception("Failed to load XGBoost model")
            raise RuntimeError(f"Failed to load model: {exc}") from exc

        inst = cls(
            target_col=data.get("target_col", "PM2.5"),
            lag_hours=data.get("lag_hours", [1, 3, 6]),
            rolling_windows=data.get("rolling_windows", [3, 6]),
        )
        inst._model = data.get("model")
        inst._feature_columns = data.get("feature_columns")
        inst._trained_shape = data.get("trained_shape")

        return inst

    def retrain(
        self,
        new_df: pd.DataFrame,
        keep_weights: bool = False,
    ) -> Dict[str, float]:
        """Retrain model with new data.

        Useful for updating the model with newly collected data while
        optionally preserving learned weights.

        Args:
            new_df: New DataFrame with target and feature columns.
            keep_weights: If True, use existing model state as starting point.

        Returns:
            Dictionary with updated train/test metrics.

        Raises:
            ValueError: If input is invalid.
        """
        if not keep_weights:
            # Full retrain
            return self.train(new_df)

        # Warm start: continue training
        if self._model is None:
            logger.warning("No existing model; performing full train instead")
            return self.train(new_df)

        if self.target_col not in new_df.columns:
            raise ValueError(f"Target column '{self.target_col}' not in DataFrame")

        expected = set(self._feature_columns or [])
        actual = set(new_df.columns)
        if not expected.issubset(actual):
            missing = expected - actual
            raise ValueError(f"Missing columns: {missing}")

        # Prepare data
        X = new_df[self._feature_columns].copy()
        y = new_df[self.target_col].copy()

        # Remove NaN
        valid_idx = X.notna().all(axis=1) & y.notna()
        X = X[valid_idx]
        y = y[valid_idx]

        if len(X) < 5:
            raise ValueError("Not enough valid samples for retraining")

        try:
            # Retrain with warm start
            self._model.fit(X, y, xgb_model=self._model)
            y_pred = self._model.predict(X)
            mae = float(np.mean(np.abs(y - y_pred)))
            rmse = float(np.sqrt(np.mean((y - y_pred) ** 2)))
            return {"mae": mae, "rmse": rmse}
        except Exception as exc:
            logger.exception("Retraining failed")
            raise RuntimeError(f"Retraining failed: {exc}") from exc

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importances from trained model.

        Returns:
            Dict mapping feature names to importance scores.
        """
        if self._model is None:
            raise RuntimeError("Model not trained")

        importances = self._model.feature_importances_
        return dict(zip(self._feature_columns, importances))


__all__ = ["XGBoostModel"]
