"""LSTM time-series forecasting model for AeroGuard.

Provides an LSTM-based forecasting model using TensorFlow/Keras.
Supports multi-step forecasting, evaluation, and model persistence.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

# Optional imports for TensorFlow
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from sklearn.preprocessing import MinMaxScaler
    HAS_TF = True
except ImportError:
    HAS_TF = False

logger = logging.getLogger(__name__)


class LSTMModel:
    """LSTM recurrent neural network for time-series AQI forecasting.

    Designed to work with sequential data or lag features. Uses MinMaxScaler
    to normalize data before training and inference.

    Attributes:
        target_col: Name of the column to predict.
        lookback: Number of previous time steps to use for prediction.
        n_features: Number of features per time step.
    """

    def __init__(
        self,
        target_col: str = "PM2.5",
        lookback: int = 24,
        n_features: int = 1,
        units: int = 50,
        dropout: float = 0.2,
        learning_rate: float = 0.001,
    ) -> None:
        """Initialize LSTM model.

        Args:
            target_col: Column name to predict.
            lookback: Number of previous hours to look back.
            n_features: Number of input features (default 1, the target itself).
            units: Number of LSTM units in the hidden layer.
            dropout: Dropout rate for regularization.
            learning_rate: Optimizer learning rate.
        """
        self.target_col = target_col
        self.lookback = lookback
        self.n_features = n_features
        self.units = units
        self.dropout = dropout
        self.learning_rate = learning_rate

        self._model: Optional[Sequential] = None
        self._scaler = MinMaxScaler(feature_range=(0, 1))
        self._is_fitted_scaler = False

        if not HAS_TF:
            logger.warning("TensorFlow/Keras not found. LSTMModel will not be functional.")

    def _check_tf(self):
        if not HAS_TF:
            raise ImportError(
                "TensorFlow is required for LSTMModel. "
                "Install it with `pip install tensorflow`"
            )

    def _prepare_data(
        self, 
        data: np.ndarray, 
        lookback: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert a 1D or 2D array into LSTM-ready (samples, lookback, features) format."""
        X, y = [], []
        for i in range(len(data) - lookback):
            X.append(data[i : (i + lookback)])
            y.append(data[i + lookback, 0])  # Assuming target is the first column
        return np.array(X), np.array(y)

    def train(
        self,
        df: pd.DataFrame,
        epochs: int = 50,
        batch_size: int = 32,
        split_ratio: float = 0.8,
        verbose: int = 0,
    ) -> Dict[str, float]:
        """Train LSTM model on time-series data.

        Args:
            df: DataFrame containing the target column.
            epochs: Number of training epochs.
            batch_size: Size of training batches.
            split_ratio: Train/test split ratio.
            verbose: Verbosity level (0, 1, or 2).

        Returns:
            Dictionary with train/test MAE and RMSE metrics.
        """
        self._check_tf()

        if self.target_col not in df.columns:
            raise ValueError(f"Target column '{self.target_col}' not in DataFrame")

        # Prepare 2D array [samples, features]
        # For now, we only use the target column itself if n_features=1
        if self.n_features == 1:
            data = df[[self.target_col]].values.astype('float32')
        else:
            # If multiple features, make sure they are in the DF
            # In a real scenario, we might want to pass feature names
            data = df.select_dtypes(include=[np.number]).values.astype('float32')
            self.n_features = data.shape[1]

        # Scale data
        scaled_data = self._scaler.fit_transform(data)
        self._is_fitted_scaler = True

        # Create windowed data
        X, y = self._prepare_data(scaled_data, self.lookback)
        
        # Train/test split
        split_idx = int(len(X) * split_ratio)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Build model
        model = Sequential([
            LSTM(self.units, input_shape=(self.lookback, self.n_features), return_sequences=False),
            Dropout(self.dropout),
            Dense(1)
        ])
        
        optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

        # Train
        model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            verbose=verbose,
            shuffle=False
        )

        self._model = model

        # Evaluate
        train_preds_scaled = model.predict(X_train, verbose=0)
        test_preds_scaled = model.predict(X_test, verbose=0)

        # Inverse scale for metrics
        # To inverse scale only the target, we need a dummy array if n_features > 1
        def inverse_transform_target(preds_scaled):
            if self.n_features == 1:
                return self._scaler.inverse_transform(preds_scaled).flatten()
            else:
                dummy = np.zeros((len(preds_scaled), self.n_features))
                dummy[:, 0] = preds_scaled.flatten()
                return self._scaler.inverse_transform(dummy)[:, 0]

        y_train_rescaled = inverse_transform_target(y_train.reshape(-1, 1))
        y_test_rescaled = inverse_transform_target(y_test.reshape(-1, 1))
        train_preds = inverse_transform_target(train_preds_scaled)
        test_preds = inverse_transform_target(test_preds_scaled)

        metrics = {
            "train_mae": float(np.mean(np.abs(y_train_rescaled - train_preds))),
            "train_rmse": float(np.sqrt(np.mean((y_train_rescaled - train_preds) ** 2))),
            "test_mae": float(np.mean(np.abs(y_test_rescaled - test_preds))),
            "test_rmse": float(np.sqrt(np.mean((y_test_rescaled - test_preds) ** 2))),
        }

        return metrics

    def predict(
        self,
        df: pd.DataFrame,
        steps: int = 6,
    ) -> List[float]:
        """Predict next values.

        Args:
            df: DataFrame containing at least `lookback` recent samples.
            steps: Number of steps to forecast ahead.

        Returns:
            List of predictions.
        """
        self._check_tf()
        if self._model is None:
            raise RuntimeError("Model not trained")
        
        if len(df) < self.lookback:
            raise ValueError(f"Need at least {self.lookback} samples, got {len(df)}")

        # Get relevant data
        if self.n_features == 1:
            current_batch = df[[self.target_col]].iloc[-self.lookback:].values.astype('float32')
        else:
            current_batch = df.select_dtypes(include=[np.number]).iloc[-self.lookback:].values.astype('float32')

        # Scale
        current_batch_scaled = self._scaler.transform(current_batch)
        
        predictions = []
        curr_x = current_batch_scaled.reshape(1, self.lookback, self.n_features)

        for _ in range(steps):
            pred_scaled = self._model.predict(curr_x, verbose=0)
            pred_val_scaled = pred_scaled[0, 0]
            
            # Inverse scale to get actual value for results
            if self.n_features == 1:
                pred_actual = self._scaler.inverse_transform(pred_scaled)[0, 0]
            else:
                dummy = np.zeros((1, self.n_features))
                dummy[0, 0] = pred_val_scaled
                pred_actual = self._scaler.inverse_transform(dummy)[0, 0]
            
            predictions.append(float(pred_actual))

            # Update curr_x for next step
            # Remove oldest, add newest
            new_row = np.zeros((1, 1, self.n_features))
            new_row[0, 0, 0] = pred_val_scaled
            # For other features, we keep them constant or shift them (here we keep constant for simplicity)
            if self.n_features > 1:
                new_row[0, 0, 1:] = curr_x[0, -1, 1:]
                
            curr_x = np.append(curr_x[:, 1:, :], new_row, axis=1)

        return predictions

    def save(self, filepath: str) -> None:
        """Save model and scaler to disk."""
        if self._model is None:
            raise RuntimeError("No trained model to save")
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save Keras model
        model_path = str(path.with_suffix('.h5'))
        self._model.save(model_path)
        
        # Save metadata and scaler
        meta_path = str(path.with_suffix('.joblib'))
        meta = {
            "target_col": self.target_col,
            "lookback": self.lookback,
            "n_features": self.n_features,
            "units": self.units,
            "dropout": self.dropout,
            "learning_rate": self.learning_rate,
            "scaler": self._scaler,
            "model_path": model_path
        }
        joblib.dump(meta, meta_path)
        logger.info(f"LSTM model saved to {meta_path} and {model_path}")

    @classmethod
    def load(cls, filepath: str) -> "LSTMModel":
        """Load model and scaler from disk."""
        path = Path(filepath)
        meta_path = str(path.with_suffix('.joblib'))
        
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Metadata file not found: {meta_path}")
            
        meta = joblib.load(meta_path)
        inst = cls(
            target_col=meta["target_col"],
            lookback=meta["lookback"],
            n_features=meta["n_features"],
            units=meta["units"],
            dropout=meta.get("dropout", 0.2),
            learning_rate=meta.get("learning_rate", 0.001)
        )
        inst._scaler = meta["scaler"]
        inst._is_fitted_scaler = True
        
        if HAS_TF:
            inst._model = load_model(meta["model_path"])
        else:
            logger.warning("TensorFlow not found. Model weights not loaded.")
            
        return inst


__all__ = ["LSTMModel"]
