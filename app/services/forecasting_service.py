"""
Forecasting Service

High-level service for generating air quality forecasts.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from app.models.forecast_model import ForecastModel
from app.utils.preprocessors import DataPreprocessor
from datetime import datetime, timedelta


class ForecastingService:
    """
    Service for air quality forecasting operations.

    Manages model interactions, data preprocessing, and forecast generation.
    """

    def __init__(self, model: ForecastModel):
        """
        Initialize the forecasting service.

        Args:
            model: ForecastModel instance
        """
        self.model = model
        self.preprocessor = DataPreprocessor()

    def generate_forecast(
        self,
        location_id: str,
        days_ahead: int = 7,
        historical_data: Optional[np.ndarray] = None,
    ) -> Dict:
        """
        Generate air quality forecast for specified location and duration.

        Args:
            location_id: Identifier for the location
            days_ahead: Number of days to forecast (1-30)
            historical_data: Historical air quality data for context

        Returns:
            Dictionary with forecast results including predictions and confidence
        """
        if not 1 <= days_ahead <= 30:
            raise ValueError("days_ahead must be between 1 and 30")

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
                forecasts[parameter] = {
                    "status": "error",
                    "message": str(e),
                    "predictions": [],
                }

        return {
            "location_id": location_id,
            "forecast_date": datetime.now().isoformat(),
            "days_ahead": days_ahead,
            "forecasts": forecasts,
        }

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
