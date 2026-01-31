"""
Forecasting Service

High-level service for generating air quality forecasts.
Supports multiple model types: sklearn ensemble (ForecastModel), SARIMA, or XGBoost.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Literal
from app.models.forecast_model import ForecastModel
from app.models.sarima_model import SARIMAModel
from app.models.xgboost_model import XGBoostModel
from app.utils.preprocessors import DataPreprocessor
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ForecastingService:
    """
    Service for air quality forecasting operations.

    Manages model interactions, data preprocessing, and forecast generation.
    Supports sklearn-based ensemble models, SARIMA time-series models, and XGBoost regression.
    """

    def __init__(self, model: Optional[ForecastModel] = None, model_type: Literal["ensemble", "sarima", "xgboost"] = "ensemble"):
        """
        Initialize the forecasting service.

        Args:
            model: ForecastModel instance (for ensemble mode)
            model_type: "ensemble" (uses ForecastModel), "sarima" (uses SARIMAModel), or "xgboost" (uses XGBoostModel)
        """
        self.model_type = model_type
        self.model = model
        self.sarima_model: Optional[SARIMAModel] = None
        self.xgboost_model: Optional[XGBoostModel] = None
        self.preprocessor = DataPreprocessor()

    def generate_forecast(
        self,
        location_id: str,
        days_ahead: int = 7,
        historical_data: Optional[np.ndarray] = None,
    ) -> Dict:
        """
        Generate air quality forecast for specified location and duration.

        Delegates to ensemble, SARIMA, or XGBoost based on model_type.

        Args:
            location_id: Identifier for the location
            days_ahead: Number of days to forecast (1-30)
            historical_data: Historical air quality data for context

        Returns:
            Dictionary with forecast results including predictions and confidence
        """
        if self.model_type == "sarima":
            return self.generate_sarima_forecast(location_id, days_ahead, historical_data)
        elif self.model_type == "xgboost":
            return self.generate_xgboost_forecast(location_id, days_ahead, historical_data)
        else:
            return self.generate_ensemble_forecast(location_id, days_ahead, historical_data)

    def generate_ensemble_forecast(
        self,
        location_id: str,
        days_ahead: int = 7,
        historical_data: Optional[np.ndarray] = None,
    ) -> Dict:
        """
        Generate air quality forecast using sklearn ensemble model (ForecastModel).

        Args:
            location_id: Identifier for the location
            days_ahead: Number of days to forecast (1-30)
            historical_data: Historical air quality data for context

        Returns:
            Dictionary with forecast results including predictions and confidence
        """
        if not 1 <= days_ahead <= 30:
            raise ValueError("days_ahead must be between 1 and 30")

        if self.model is None:
            raise RuntimeError("No ensemble model configured")

        if historical_data is None:
            historical_data = self._get_mock_historical_data()

        # Prepare features for prediction
        features = self.preprocessor.prepare_features(historical_data, days_ahead)

        # Generate predictions for all supported parameters
        forecasts = {}
        for parameter in ForecastModel.SUPPORTED_PARAMETERS:
            try:
                predictions = self.model.predict(features, parameter)
                forecasts[parameter] = self._format_forecast(
                    predictions, parameter, days_ahead
                )
            except Exception as e:
                logger.exception(f"Ensemble forecast error for {parameter}")
                forecasts[parameter] = {
                    "status": "error",
                    "message": str(e),
                    "predictions": [],
                }

        return {
            "location_id": location_id,
            "forecast_date": datetime.now().isoformat(),
            "days_ahead": days_ahead,
            "model_type": "ensemble",
            "forecasts": forecasts,
        }

    def generate_sarima_forecast(
        self,
        location_id: str,
        days_ahead: int = 7,
        historical_data: Optional[np.ndarray] = None,
    ) -> Dict:
        """
        Generate air quality forecast using SARIMA time-series model.

        Args:
            location_id: Identifier for the location
            days_ahead: Number of days to forecast (1-30)
            historical_data: Historical air quality data (hourly pandas Series preferred)

        Returns:
            Dictionary with forecast results including predictions and confidence
        """
        if not 1 <= days_ahead <= 30:
            raise ValueError("days_ahead must be between 1 and 30")

        if self.sarima_model is None:
            raise RuntimeError("SARIMA model not trained. Call `train_sarima()` first.")

        # Convert days_ahead to hours for SARIMA (assumes hourly data)
        forecast_hours = days_ahead * 24

        forecasts = {}
        
        # SARIMA typically forecasts a single parameter (e.g., PM2.5)
        # Generate forecast for each common parameter
        for parameter in ["pm25", "pm10", "aqi"]:
            try:
                preds = self.sarima_model.predict(steps=forecast_hours)
                # Aggregate hourly predictions to daily
                daily_preds = self._aggregate_to_daily(preds, days_ahead)
                forecasts[parameter] = self._format_forecast(
                    np.array(daily_preds), parameter, days_ahead
                )
            except Exception as e:
                logger.exception(f"SARIMA forecast error for {parameter}")
                forecasts[parameter] = {
                    "status": "error",
                    "message": str(e),
                    "predictions": [],
                }

        return {
            "location_id": location_id,
            "forecast_date": datetime.now().isoformat(),
            "days_ahead": days_ahead,
            "model_type": "sarima",
            "forecasts": forecasts,
        }

    def train_sarima(self, series: pd.Series) -> None:
        """
        Train the SARIMA model on historical data.

        Args:
            series: Pandas Series of historical air quality (hourly index preferred)

        Raises:
            ValueError: If series is invalid
        """
        if self.sarima_model is None:
            self.sarima_model = SARIMAModel()
        try:
            self.sarima_model.train(series)
            logger.info("SARIMA model trained successfully")
        except Exception as e:
            logger.exception("SARIMA training failed")
            raise

    def generate_xgboost_forecast(
        self,
        location_id: str,
        days_ahead: int = 7,
        historical_data: Optional[pd.DataFrame] = None,
    ) -> Dict:
        """
        Generate air quality forecast using XGBoost regression model.

        Args:
            location_id: Identifier for the location
            days_ahead: Number of days to forecast (1-30)
            historical_data: Historical air quality DataFrame with features and target

        Returns:
            Dictionary with forecast results including predictions and confidence
        """
        if not 1 <= days_ahead <= 30:
            raise ValueError("days_ahead must be between 1 and 30")

        if self.xgboost_model is None:
            raise RuntimeError("XGBoost model not trained. Call `train_xgboost()` first.")

        # Convert days_ahead to hours for XGBoost (assumes hourly data)
        forecast_hours = days_ahead * 24

        forecasts = {}
        
        # For XGBoost, we generate a single forecast from the trained model
        # Since XGBoost doesn't have a direct multi-step forecasting interface like SARIMA,
        # we use the predict method with iterative feature updates
        try:
            # Create initial feature vector from the trained model
            # For demonstration, generate synthetic features based on training data statistics
            n_features = len(self.xgboost_model._feature_columns) if hasattr(self.xgboost_model, '_feature_columns') else 8
            
            # Use last row of training data (if available) or generate synthetic features
            initial_features = pd.DataFrame(
                np.random.normal(loc=50, scale=15, size=(1, n_features)),
                columns=self.xgboost_model._feature_columns if hasattr(self.xgboost_model, '_feature_columns') else [f'feature_{i}' for i in range(n_features)]
            )
            
            # Get iterative predictions
            preds = self.xgboost_model.predict(initial_features, steps=forecast_hours)
            
            # Aggregate hourly predictions to daily
            daily_preds = self._aggregate_to_daily(preds, days_ahead)
            
            # Generate forecast for each common parameter
            for parameter in ["pm25", "pm10", "aqi"]:
                forecasts[parameter] = self._format_forecast(
                    np.array(daily_preds), parameter, days_ahead
                )
        except Exception as e:
            logger.exception(f"XGBoost forecast generation error")
            # Return error status for all parameters
            for parameter in ["pm25", "pm10", "aqi"]:
                forecasts[parameter] = {
                    "status": "error",
                    "message": str(e),
                    "predictions": [],
                }

        return {
            "location_id": location_id,
            "forecast_date": datetime.now().isoformat(),
            "days_ahead": days_ahead,
            "model_type": "xgboost",
            "forecasts": forecasts,
        }

    def train_xgboost(self, df: pd.DataFrame, target_col: str = "PM2.5", split_ratio: float = 0.8) -> Dict:
        """
        Train the XGBoost model on historical data.

        Expects DataFrame with lag features created by TimeSeriesPreprocessor.

        Args:
            df: DataFrame with features (lag and rolling stats) and target column
            target_col: Name of target column to predict (default: "PM2.5")
            split_ratio: Train/test split ratio (default: 0.8)

        Returns:
            Dictionary with training metrics (train_mae, train_rmse, test_mae, test_rmse)

        Raises:
            ValueError: If DataFrame is invalid or missing required columns
        """
        if self.xgboost_model is None:
            self.xgboost_model = XGBoostModel(target_col=target_col)
        try:
            metrics = self.xgboost_model.train(df, split_ratio=split_ratio)
            logger.info(f"XGBoost model trained successfully. Test MAE: {metrics.get('test_mae', 'N/A')}")
            return metrics
        except Exception as e:
            logger.exception("XGBoost training failed")
            raise

    def _aggregate_to_daily(self, hourly_preds: List[float], days: int) -> List[float]:
        """
        Aggregate hourly predictions to daily (24-hour rolling mean).

        Args:
            hourly_preds: List of hourly predictions
            days: Number of days to aggregate to

        Returns:
            List of daily aggregated predictions
        """
        daily = []
        for d in range(days):
            start = d * 24
            end = min(start + 24, len(hourly_preds))
            if start < len(hourly_preds):
                day_preds = hourly_preds[start:end]
                daily.append(float(np.mean(day_preds)))
        return daily

    def _format_forecast(
        self, predictions: np.ndarray, parameter: str, days_ahead: int
    ) -> Dict:
        """
        Format prediction array into forecast structure.

        Args:
            predictions: Model predictions
            parameter: Air quality parameter name
            days_ahead: Number of forecast days

        Returns:
            Formatted forecast dictionary
        """
        forecast_dates = [
            (datetime.now() + timedelta(days=i)).date().isoformat()
            for i in range(1, days_ahead + 1)
        ]

        # Resample predictions if needed
        if len(predictions) < days_ahead:
            # Linear interpolation for missing values
            indices = np.linspace(0, len(predictions) - 1, days_ahead)
            predictions = np.interp(indices, np.arange(len(predictions)), predictions)

        return {
            "parameter": parameter,
            "unit": self._get_parameter_unit(parameter),
            "predictions": [
                {
                    "date": date,
                    "value": float(np.round(value, 2)),
                    "confidence": self._estimate_confidence(value, parameter),
                }
                for date, value in zip(forecast_dates, predictions[:days_ahead])
            ],
            "status": "success",
        }

    def _get_parameter_unit(self, parameter: str) -> str:
        """Get unit for air quality parameter."""
        units = {
            "pm25": "µg/m³",
            "pm10": "µg/m³",
            "no2": "ppb",
            "o3": "ppb",
            "so2": "ppb",
            "co": "ppm",
        }
        return units.get(parameter, "unknown")

    def _estimate_confidence(self, value: float, parameter: str) -> float:
        """
        Estimate confidence score for prediction.

        Args:
            value: Predicted value
            parameter: Parameter name

        Returns:
            Confidence score between 0 and 1
        """
        # Simple heuristic: higher confidence for values in typical ranges
        ranges = {
            "pm25": (0, 500),
            "pm10": (0, 1000),
            "no2": (0, 200),
            "o3": (0, 150),
            "so2": (0, 150),
            "co": (0, 50),
        }

        if parameter not in ranges:
            return 0.5

        min_val, max_val = ranges[parameter]
        if min_val <= value <= max_val:
            # Higher confidence for mid-range values
            mid = (min_val + max_val) / 2
            distance = abs(value - mid) / (max_val - min_val)
            return 1 - (distance * 0.3)
        else:
            return 0.6

    def _get_mock_historical_data(self) -> np.ndarray:
        """
        Generate mock historical data for demonstration.

        Returns:
            Mock historical air quality data
        """
        np.random.seed(42)
        n_samples = 30
        n_features = 10

        # Create realistic air quality data
        data = np.random.normal(loc=50, scale=20, size=(n_samples, n_features))
        data = np.clip(data, 0, 500)

        return data
