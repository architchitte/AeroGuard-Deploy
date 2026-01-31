"""SARIMA forecasting model wrapper for AeroGuard.

Provides a lightweight interface to train a SARIMA model on an hourly
Pandas Series and forecast the next N hours. Includes evaluation helpers
and save/load via joblib.
"""
from __future__ import annotations

from typing import Optional, Tuple, Dict, Any, List
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import warnings
import joblib

logger = logging.getLogger(__name__)


class SARIMAModel:
    """SARIMA model wrapper.

    Usage:
        model = SARIMAModel()
        model.train(series)  # pandas Series, hourly
        preds = model.predict(6)

    Attributes:
        order: ARIMA (p,d,q) order
        seasonal_order: Seasonal (P,D,Q,s) order, default s=24 (daily seasonality)
    """

    def __init__(
        self,
        order: Tuple[int, int, int] = (1, 1, 1),
        seasonal_order: Tuple[int, int, int, int] = (1, 1, 1, 24),
    ) -> None:
        self.order = order
        self.seasonal_order = seasonal_order
        self._model: Optional[SARIMAX] = None
        self._results: Optional[Any] = None
        self._trained_on_length: Optional[int] = None

    def train(
        self,
        series: pd.Series,
        order: Optional[Tuple[int, int, int]] = None,
        seasonal_order: Optional[Tuple[int, int, int, int]] = None,
        enforce_stationarity: bool = False,
        enforce_invertibility: bool = False,
        maxiter: int = 50,
    ) -> None:
        """Train SARIMA model on a pandas Series.

        Args:
            series: One-dimensional `pd.Series` indexed by datetime (hourly).
            order: Optional (p,d,q) tuple to override default.
            seasonal_order: Optional (P,D,Q,s) tuple to override default.
            enforce_stationarity: Passed to SARIMAX.
            enforce_invertibility: Passed to SARIMAX.
            maxiter: Maximum optimizer iterations.

        Raises:
            ValueError: If input is invalid or too short.
            RuntimeError: If fitting fails.
        """
        if not isinstance(series, pd.Series):
            raise ValueError("`series` must be a pandas Series")
        if series.dropna().empty:
            raise ValueError("`series` contains no non-NaN values to train on")
        if len(series) < 24:
            raise ValueError("Require at least 24 observations (1 day hourly) to train SARIMA")

        order = order or self.order
        seasonal_order = seasonal_order or self.seasonal_order

        # build model
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                self._model = SARIMAX(
                    series,
                    order=order,
                    seasonal_order=seasonal_order,
                    enforce_stationarity=enforce_stationarity,
                    enforce_invertibility=enforce_invertibility,
                    freq=None,
                )
                res = self._model.fit(disp=False, maxiter=maxiter)
        except Exception as exc:  # pragma: no cover - surface errors
            logger.exception("SARIMA training failed")
            raise RuntimeError(f"SARIMA training failed: {exc}") from exc

        self._results = res
        self.order = order
        self.seasonal_order = seasonal_order
        self._trained_on_length = len(series)

    def predict(self, steps: int = 6) -> List[float]:
        """Forecast the next `steps` hours and return predictions as floats.

        Args:
            steps: Number of hours to forecast (default 6).

        Returns:
            List of predicted values (length == steps).

        Raises:
            RuntimeError: If model is not trained.
        """
        if self._results is None:
            raise RuntimeError("Model has not been trained. Call `train()` first.")
        if steps <= 0:
            return []

        try:
            forecast = self._results.get_forecast(steps=steps)
            preds = forecast.predicted_mean
            # convert to python floats
            return [float(x) for x in np.asarray(preds)]
        except Exception as exc:  # pragma: no cover - runtime exception
            logger.exception("SARIMA predict failed")
            raise RuntimeError(f"SARIMA predict failed: {exc}") from exc

    def evaluate_forecast(self, preds: List[float], actuals: List[float]) -> Dict[str, float]:
        """Compute MAE and RMSE between predictions and actuals.

        Args:
            preds: Predictions list.
            actuals: Ground-truth list; same length as preds.

        Returns:
            Dict with keys `mae` and `rmse`.

        Raises:
            ValueError: If lengths mismatch.
        """
        if len(preds) != len(actuals):
            raise ValueError("`preds` and `actuals` must have the same length")
        preds_arr = np.array(preds, dtype=float)
        actuals_arr = np.array(actuals, dtype=float)
        mae = float(np.mean(np.abs(preds_arr - actuals_arr)))
        rmse = float(np.sqrt(np.mean((preds_arr - actuals_arr) ** 2)))
        return {"mae": mae, "rmse": rmse}

    def save(self, filepath: str) -> None:
        """Save trained model object to disk using joblib.

        The saved object contains the fitted results and the model configuration.
        """
        if self._results is None:
            raise RuntimeError("No trained model to save")
        p = Path(filepath)
        data = {
            "order": self.order,
            "seasonal_order": self.seasonal_order,
            "trained_on_length": self._trained_on_length,
            "results": self._results,
        }
        try:
            joblib.dump(data, p)
        except Exception as exc:  # pragma: no cover - IO errors
            logger.exception("Failed to save SARIMA model")
            raise RuntimeError(f"Failed to save SARIMA model: {exc}") from exc

    @classmethod
    def load(cls, filepath: str) -> "SARIMAModel":
        """Load a saved SARIMA model from disk.

        Returns a `SARIMAModel` instance with `._results` populated.
        """
        p = Path(filepath)
        if not p.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        try:
            data = joblib.load(p)
        except Exception as exc:  # pragma: no cover - IO errors
            logger.exception("Failed to load SARIMA model")
            raise RuntimeError(f"Failed to load SARIMA model: {exc}") from exc

        inst = cls(order=tuple(data.get("order", (1, 1, 1))), seasonal_order=tuple(data.get("seasonal_order", (1, 1, 1, 24))))
        inst._results = data.get("results")
        inst._trained_on_length = data.get("trained_on_length")
        return inst


__all__ = ["SARIMAModel"]
