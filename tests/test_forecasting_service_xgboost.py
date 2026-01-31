"""
Unit tests for ForecastingService with XGBoost integration.

Tests the XGBoost model integration into the ForecastingService class.
"""

import pytest
import numpy as np
import pandas as pd
from app.services.forecasting_service import ForecastingService
from app.models.xgboost_model import XGBoostModel


class TestForecastingServiceXGBoost:
    """Test ForecastingService with XGBoost model type."""

    @pytest.fixture
    def sample_df(self):
        """Create sample preprocessed data with lag and rolling features."""
        np.random.seed(42)
        n_samples = 100
        
        # Create base data
        data = np.random.normal(loc=50, scale=15, size=n_samples)
        data = np.clip(data, 0, 200)
        
        # Column names match XGBoostModel's expected naming convention
        df = pd.DataFrame({
            'PM2.5': data,
            'PM2.5_lag_1h': np.roll(data, 1),
            'PM2.5_lag_3h': np.roll(data, 3),
            'PM2.5_lag_6h': np.roll(data, 6),
            'PM2.5_mean_3h': pd.Series(data).rolling(window=3).mean(),
            'PM2.5_std_3h': pd.Series(data).rolling(window=3).std(),
            'PM2.5_mean_6h': pd.Series(data).rolling(window=6).mean(),
            'PM2.5_std_6h': pd.Series(data).rolling(window=6).std(),
        })
        
        # Drop NaN rows
        df = df.dropna().reset_index(drop=True)
        
        return df

    def test_xgboost_service_initialization(self):
        """Test ForecastingService can be initialized with xgboost model_type."""
        service = ForecastingService(model_type="xgboost")
        
        assert service.model_type == "xgboost"
        assert service.xgboost_model is None
        assert service.sarima_model is None

    def test_train_xgboost(self, sample_df):
        """Test training XGBoost model through ForecastingService."""
        service = ForecastingService(model_type="xgboost")
        
        # Train the model
        metrics = service.train_xgboost(sample_df)
        
        # Check metrics are returned
        assert isinstance(metrics, dict)
        assert "train_mae" in metrics
        assert "train_rmse" in metrics
        assert "test_mae" in metrics
        assert "test_rmse" in metrics
        
        # Check XGBoost model is initialized
        assert service.xgboost_model is not None
        assert isinstance(service.xgboost_model, XGBoostModel)
        
        # Check metrics are reasonable
        assert metrics["test_mae"] > 0
        assert metrics["test_rmse"] > 0

    def test_generate_xgboost_forecast_without_training(self):
        """Test that generating forecast without training raises error."""
        service = ForecastingService(model_type="xgboost")
        
        with pytest.raises(RuntimeError, match="XGBoost model not trained"):
            service.generate_xgboost_forecast("test_location", days_ahead=7)

    def test_generate_xgboost_forecast_invalid_days(self, sample_df):
        """Test that invalid days_ahead raises error."""
        service = ForecastingService(model_type="xgboost")
        service.train_xgboost(sample_df)
        
        with pytest.raises(ValueError, match="days_ahead must be between 1 and 30"):
            service.generate_xgboost_forecast("test_location", days_ahead=31)

    def test_generate_xgboost_forecast(self, sample_df):
        """Test generating forecast with trained XGBoost model."""
        service = ForecastingService(model_type="xgboost")
        service.train_xgboost(sample_df)
        
        # Generate forecast
        forecast = service.generate_xgboost_forecast("test_location", days_ahead=7)
        
        # Check structure
        assert forecast["location_id"] == "test_location"
        assert forecast["days_ahead"] == 7
        assert forecast["model_type"] == "xgboost"
        assert "forecast_date" in forecast
        assert "forecasts" in forecast
        
        # Check forecasts for each parameter
        for param in ["pm25", "pm10", "aqi"]:
            assert param in forecast["forecasts"]
            param_forecast = forecast["forecasts"][param]
            assert param_forecast["status"] == "success"
            assert "predictions" in param_forecast
            assert len(param_forecast["predictions"]) == 7
            
            # Check prediction structure
            for pred in param_forecast["predictions"]:
                assert "date" in pred
                assert "value" in pred
                assert "confidence" in pred
                assert isinstance(pred["value"], float)
                assert 0 <= pred["confidence"] <= 1

    def test_generate_forecast_with_xgboost_mode(self, sample_df):
        """Test that generate_forecast delegates to XGBoost when model_type is xgboost."""
        service = ForecastingService(model_type="xgboost")
        service.train_xgboost(sample_df)
        
        # Use generic generate_forecast
        forecast = service.generate_forecast("test_location", days_ahead=5)
        
        # Check it used XGBoost model
        assert forecast["model_type"] == "xgboost"
        assert "forecasts" in forecast

    def test_xgboost_forecast_days_boundary(self, sample_df):
        """Test forecast generation at boundary days (1 and 30)."""
        service = ForecastingService(model_type="xgboost")
        service.train_xgboost(sample_df)
        
        # Test minimum days
        forecast_1 = service.generate_xgboost_forecast("loc1", days_ahead=1)
        assert forecast_1["days_ahead"] == 1
        assert len(forecast_1["forecasts"]["pm25"]["predictions"]) == 1
        
        # Test maximum days
        forecast_30 = service.generate_xgboost_forecast("loc2", days_ahead=30)
        assert forecast_30["days_ahead"] == 30
        assert len(forecast_30["forecasts"]["pm25"]["predictions"]) == 30

    def test_xgboost_with_custom_target(self, sample_df):
        """Test XGBoost training with custom target column requires matching features."""
        # Custom targets need their own lag/rolling features
        # This test validates the constraint
        sample_df_custom = sample_df.copy()
        sample_df_custom["AQI"] = sample_df_custom["PM2.5"]
        
        service = ForecastingService(model_type="xgboost")
        
        # Training with custom target but PM2.5 features should fail
        with pytest.raises(ValueError, match="Missing feature columns"):
            service.train_xgboost(sample_df_custom, target_col="AQI")

    def test_xgboost_forecast_confidence_scores(self, sample_df):
        """Test that confidence scores are within valid range."""
        service = ForecastingService(model_type="xgboost")
        service.train_xgboost(sample_df)
        
        forecast = service.generate_xgboost_forecast("test_loc", days_ahead=3)
        
        # Check all confidence scores are in valid range
        for param, param_forecast in forecast["forecasts"].items():
            for pred in param_forecast["predictions"]:
                confidence = pred["confidence"]
                assert 0 <= confidence <= 1, f"Invalid confidence {confidence} for {param}"

    def test_xgboost_forecast_prediction_values_reasonable(self, sample_df):
        """Test that predicted values are within reasonable ranges for air quality."""
        service = ForecastingService(model_type="xgboost")
        service.train_xgboost(sample_df)
        
        forecast = service.generate_xgboost_forecast("test_loc", days_ahead=5)
        
        # PM2.5 and PM10 should be non-negative
        for pred in forecast["forecasts"]["pm25"]["predictions"]:
            assert pred["value"] >= 0, "PM2.5 should be non-negative"
        
        for pred in forecast["forecasts"]["pm10"]["predictions"]:
            assert pred["value"] >= 0, "PM10 should be non-negative"

    def test_train_xgboost_with_custom_split(self, sample_df):
        """Test XGBoost training with custom train/test split ratio."""
        service = ForecastingService(model_type="xgboost")
        
        # Train with 70/30 split
        metrics = service.train_xgboost(sample_df, split_ratio=0.7)
        
        assert isinstance(metrics, dict)
        assert "train_mae" in metrics
        assert "test_mae" in metrics

    def test_multiple_forecasts_consistent(self, sample_df):
        """Test that multiple forecasts from same model have consistent structure."""
        service = ForecastingService(model_type="xgboost")
        service.train_xgboost(sample_df)
        
        # Generate multiple forecasts
        forecast1 = service.generate_xgboost_forecast("loc1", days_ahead=7)
        forecast2 = service.generate_xgboost_forecast("loc2", days_ahead=7)
        
        # Both should have same structure
        assert set(forecast1["forecasts"].keys()) == set(forecast2["forecasts"].keys())
        assert len(forecast1["forecasts"]["pm25"]["predictions"]) == \
               len(forecast2["forecasts"]["pm25"]["predictions"])


class TestForecastingServiceModelSwitching:
    """Test switching between different model types."""

    @pytest.fixture
    def sample_df(self):
        """Create sample data for all model types."""
        np.random.seed(42)
        n_samples = 100
        
        data = np.random.normal(loc=50, scale=15, size=n_samples)
        data = np.clip(data, 0, 200)
        
        # Column names match XGBoostModel's expected naming convention
        df = pd.DataFrame({
            'PM2.5': data,
            'PM2.5_lag_1h': np.roll(data, 1),
            'PM2.5_lag_3h': np.roll(data, 3),
            'PM2.5_lag_6h': np.roll(data, 6),
            'PM2.5_mean_3h': pd.Series(data).rolling(window=3).mean(),
            'PM2.5_std_3h': pd.Series(data).rolling(window=3).std(),
            'PM2.5_mean_6h': pd.Series(data).rolling(window=6).mean(),
            'PM2.5_std_6h': pd.Series(data).rolling(window=6).std(),
        })
        
        df = df.dropna().reset_index(drop=True)
        return df

    def test_service_model_type_parameter(self, sample_df):
        """Test ForecastingService accepts xgboost model_type."""
        service_xgb = ForecastingService(model_type="xgboost")
        
        assert service_xgb.model_type == "xgboost"
        
        # Train and verify
        metrics = service_xgb.train_xgboost(sample_df)
        assert service_xgb.xgboost_model is not None

    def test_generate_forecast_respects_model_type(self, sample_df):
        """Test that generate_forecast respects the model_type setting."""
        service_xgb = ForecastingService(model_type="xgboost")
        service_xgb.train_xgboost(sample_df)
        
        # Call generic generate_forecast - should use XGBoost
        forecast = service_xgb.generate_forecast("test", days_ahead=3)
        assert forecast["model_type"] == "xgboost"
