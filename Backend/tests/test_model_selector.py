"""
Unit tests for Model Comparison & Selection Service (Judge Favorite ⭐)

Tests ModelComparator and ModelSelector classes.
"""

import pytest
import numpy as np
import pandas as pd
from app.services.model_selector import ModelComparator, ModelSelector
from app.models.sarima_model import SARIMAModel
from app.models.xgboost_model import XGBoostModel


class TestModelComparator:
    """Test ModelComparator class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample time-series data."""
        np.random.seed(42)
        n_samples = 150
        
        # Time series with trend
        t = np.arange(n_samples)
        base = 50 + 0.1 * t
        noise = np.random.normal(0, 5, n_samples)
        data = base + noise
        data = np.clip(data, 0, 200)
        
        # Create features for XGBoost
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

    def test_comparator_initialization(self):
        """Test ModelComparator initialization."""
        comparator = ModelComparator()
        
        assert comparator.models == {}
        assert comparator.metrics == {}
        assert comparator.best_model is None
        assert comparator.predictions == {}

    def test_add_model(self):
        """Test adding models to comparator."""
        comparator = ModelComparator()
        
        # Create dummy models
        sarima = SARIMAModel()
        xgboost = XGBoostModel()
        
        comparator.add_model("SARIMA", sarima)
        comparator.add_model("XGBoost", xgboost)
        
        assert len(comparator.models) == 2
        assert "SARIMA" in comparator.models
        assert "XGBoost" in comparator.models

    def test_add_model_duplicate_error(self):
        """Test error on duplicate model registration."""
        comparator = ModelComparator()
        sarima = SARIMAModel()
        
        comparator.add_model("SARIMA", sarima)
        
        with pytest.raises(ValueError, match="already registered"):
            comparator.add_model("SARIMA", sarima)

    def test_train_and_compare_no_models(self, sample_data):
        """Test error when no models registered."""
        comparator = ModelComparator()
        
        with pytest.raises(ValueError, match="No models registered"):
            comparator.train_and_compare(sample_data)

    def test_train_and_compare_missing_target(self):
        """Test error when target column missing."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        
        df = pd.DataFrame({'other_col': [1, 2, 3]})
        
        with pytest.raises(ValueError, match="not found"):
            comparator.train_and_compare(df, target_col="PM2.5")

    def test_train_and_compare_insufficient_data(self):
        """Test error with insufficient data."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        
        df = pd.DataFrame({'PM2.5': [1, 2, 3]})
        
        with pytest.raises(ValueError, match="Insufficient data"):
            comparator.train_and_compare(df)

    def test_train_and_compare_success(self, sample_data):
        """Test successful train and compare."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        comparator.add_model("XGBoost", XGBoostModel())
        
        result = comparator.train_and_compare(sample_data, forecast_steps=6)
        
        assert "best_model" in result
        assert "metrics" in result
        assert "predictions" in result
        assert "test_actual" in result
        
        assert result["best_model"] in ["SARIMA", "XGBoost"]
        assert "SARIMA" in result["metrics"]
        assert "XGBoost" in result["metrics"]

    def test_compare_models_metrics(self, sample_data):
        """Test metrics calculation."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        comparator.add_model("XGBoost", XGBoostModel())
        
        comparator.train_and_compare(sample_data, forecast_steps=6)
        
        metrics = comparator.get_metrics_summary()
        
        # Check structure
        assert isinstance(metrics, dict)
        for model_name, metric_dict in metrics.items():
            assert "MAE" in metric_dict
            assert "RMSE" in metric_dict
            assert metric_dict["MAE"] >= 0
            assert metric_dict["RMSE"] >= 0

    def test_compare_models_with_actual(self):
        """Test metric comparison with known values."""
        comparator = ModelComparator()
        
        test_actual = np.array([10, 20, 30, 40, 50])
        predictions = {
            "Model1": [10, 20, 30, 40, 50],  # Perfect prediction
            "Model2": [12, 22, 32, 42, 52],  # 2 unit error
        }
        
        metrics = comparator.compare_models(test_actual, predictions)
        
        # Model1 should be perfect
        assert metrics["Model1"]["MAE"] == 0.0
        assert metrics["Model1"]["RMSE"] == 0.0
        
        # Model2 should have 2.0 error
        assert metrics["Model2"]["MAE"] == 2.0
        assert metrics["Model2"]["RMSE"] == 2.0

    def test_select_best_model(self, sample_data):
        """Test best model selection."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        comparator.add_model("XGBoost", XGBoostModel())
        
        comparator.train_and_compare(sample_data)
        
        best_model = comparator.get_best_model_name()
        assert best_model in ["SARIMA", "XGBoost"]

    def test_get_best_predictions(self, sample_data):
        """Test retrieving best model predictions."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        comparator.add_model("XGBoost", XGBoostModel())
        
        comparator.train_and_compare(sample_data, forecast_steps=6)
        
        preds = comparator.get_best_model_predictions()
        assert preds is not None
        assert len(preds) == 6

    def test_comparison_report_generation(self, sample_data):
        """Test report generation."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        comparator.add_model("XGBoost", XGBoostModel())
        
        comparator.train_and_compare(sample_data, forecast_steps=6)
        
        report = comparator.get_comparison_report()
        
        assert report is not None
        assert "best_model" in report
        assert "models" in report
        assert "timestamp" in report
        assert "total_models" in report
        
        # Check model details
        for model_name, details in report["models"].items():
            assert "rank" in details
            assert "MAE" in details
            assert "RMSE" in details
            assert "is_best" in details

    def test_report_ranking(self, sample_data):
        """Test that report correctly ranks models."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        comparator.add_model("XGBoost", XGBoostModel())
        
        comparator.train_and_compare(sample_data, forecast_steps=6)
        
        report = comparator.get_comparison_report()
        models_info = report["models"]
        
        # Check that best model has rank 1
        for model_name, details in models_info.items():
            if details["is_best"]:
                assert details["rank"] == 1

    def test_reset_functionality(self, sample_data):
        """Test reset clears state."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        comparator.add_model("XGBoost", XGBoostModel())
        
        comparator.train_and_compare(sample_data)
        
        assert comparator.best_model is not None
        assert len(comparator.metrics) > 0
        
        comparator.reset()
        
        assert comparator.best_model is None
        assert len(comparator.metrics) == 0
        assert len(comparator.predictions) == 0

    def test_print_report(self, sample_data, capsys):
        """Test report printing."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        comparator.add_model("XGBoost", XGBoostModel())
        
        comparator.train_and_compare(sample_data, forecast_steps=6)
        comparator.print_report()
        
        captured = capsys.readouterr()
        assert "Judge Favorite" in captured.out
        assert "BEST" in captured.out or "⭐" in captured.out

    def test_print_report_no_comparison(self, capsys):
        """Test print report without comparison."""
        comparator = ModelComparator()
        comparator.print_report()
        
        captured = capsys.readouterr()
        assert "No report generated" in captured.out

    def test_metrics_consistency(self, sample_data):
        """Test that metrics are consistent across calls."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        comparator.add_model("XGBoost", XGBoostModel())
        
        # Run comparison
        result1 = comparator.train_and_compare(sample_data, forecast_steps=6)
        metrics1 = result1["metrics"]
        
        # Metrics should be retrievable
        metrics2 = comparator.get_metrics_summary()
        
        assert metrics1 == metrics2

    def test_percentage_difference_calculation(self):
        """Test percentage difference in report."""
        comparator = ModelComparator()
        
        # Mock metrics for verification
        test_actual = np.array([10, 20, 30, 40, 50])
        predictions = {
            "Model_Good": [10, 20, 30, 40, 50],   # MAE = 0
            "Model_Bad": [11, 21, 31, 41, 51],    # MAE = 1
        }
        
        comparator.metrics = comparator.compare_models(test_actual, predictions)
        comparator.best_model = "Model_Good"
        comparator.comparison_report = comparator._generate_report(
            model_names=["Model_Good", "Model_Bad"],
            test_actual=test_actual,
            forecast_steps=5,
        )
        
        report = comparator.get_comparison_report()
        
        # Bad model should show positive percentage difference (or infinite if best_mae=0)
        bad_pct = report["models"]["Model_Bad"]["mae_pct_diff"]
        # When best_mae is 0 (perfect prediction), pct_diff will be inf but calculated as 0
        # Just verify the structure is correct
        assert "mae_pct_diff" in report["models"]["Model_Bad"]


class TestModelSelector:
    """Test ModelSelector convenience wrapper."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data."""
        np.random.seed(42)
        n_samples = 150
        
        t = np.arange(n_samples)
        base = 50 + 0.1 * t
        noise = np.random.normal(0, 5, n_samples)
        data = base + noise
        data = np.clip(data, 0, 200)
        
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

    def test_selector_initialization(self):
        """Test ModelSelector initialization."""
        selector = ModelSelector()
        assert selector.comparator is not None

    def test_selector_with_initial_models(self):
        """Test ModelSelector with initial models."""
        models = {
            "SARIMA": SARIMAModel(),
            "XGBoost": XGBoostModel(),
        }
        selector = ModelSelector(models=models)
        
        assert len(selector.comparator.models) == 2

    def test_select_best(self, sample_data):
        """Test select_best method."""
        selector = ModelSelector()
        selector.add_model("SARIMA", SARIMAModel())
        selector.add_model("XGBoost", XGBoostModel())
        
        result = selector.select_best(sample_data, forecast_steps=6)
        
        assert "best_model" in result
        assert result["best_model"] is not None

    def test_get_best_model_name(self, sample_data):
        """Test getting best model name."""
        selector = ModelSelector()
        selector.add_model("SARIMA", SARIMAModel())
        selector.add_model("XGBoost", XGBoostModel())
        
        selector.select_best(sample_data)
        
        best = selector.get_best_model()
        assert best in ["SARIMA", "XGBoost"]

    def test_get_best_predictions(self, sample_data):
        """Test getting best model predictions."""
        selector = ModelSelector()
        selector.add_model("SARIMA", SARIMAModel())
        selector.add_model("XGBoost", XGBoostModel())
        
        selector.select_best(sample_data, forecast_steps=6)
        
        preds = selector.get_best_predictions()
        assert preds is not None
        assert len(preds) == 6

    def test_add_model_to_selector(self):
        """Test adding model to selector."""
        selector = ModelSelector()
        
        assert len(selector.comparator.models) == 0
        
        selector.add_model("SARIMA", SARIMAModel())
        
        assert len(selector.comparator.models) == 1

    def test_print_summary(self, sample_data, capsys):
        """Test print_summary method."""
        selector = ModelSelector()
        selector.add_model("SARIMA", SARIMAModel())
        selector.add_model("XGBoost", XGBoostModel())
        
        selector.select_best(sample_data)
        selector.print_summary()
        
        captured = capsys.readouterr()
        assert "Judge Favorite" in captured.out or "BEST" in captured.out

    def test_selector_forecast_steps(self, sample_data):
        """Test with different forecast steps."""
        selector = ModelSelector()
        selector.add_model("SARIMA", SARIMAModel())
        selector.add_model("XGBoost", XGBoostModel())
        
        for steps in [6, 12, 24]:
            result = selector.select_best(sample_data, forecast_steps=steps)
            preds = selector.get_best_predictions()
            assert len(preds) == steps


class TestModelComparatorIntegration:
    """Integration tests for model comparison."""

    @pytest.fixture
    def real_timeseries(self):
        """Create realistic time-series data."""
        np.random.seed(42)
        n_samples = 200
        
        # Simulate air quality with seasonality
        t = np.arange(n_samples)
        seasonal = 10 * np.sin(2 * np.pi * t / 24)  # Daily pattern
        trend = 0.05 * t
        noise = np.random.normal(0, 3, n_samples)
        data = 50 + seasonal + trend + noise
        data = np.clip(data, 0, 200)
        
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

    def test_full_comparison_workflow(self, real_timeseries):
        """Test complete comparison workflow."""
        selector = ModelSelector()
        selector.add_model("SARIMA", SARIMAModel())
        selector.add_model("XGBoost", XGBoostModel())
        
        # Run comparison
        result = selector.select_best(real_timeseries, forecast_steps=12)
        
        # Verify results
        assert result["best_model"] is not None
        best_preds = result["predictions"][result["best_model"]]
        assert len(best_preds) == 12
        
        # All predictions should be numeric
        for pred_dict in result["predictions"].values():
            assert all(isinstance(p, (int, float)) for p in pred_dict)

    def test_comparison_with_different_targets(self, real_timeseries):
        """Test comparison with different target columns."""
        # Create additional target
        real_timeseries['PM10'] = real_timeseries['PM2.5'] * 1.5
        
        selector = ModelSelector()
        selector.add_model("SARIMA", SARIMAModel())
        selector.add_model("XGBoost", XGBoostModel())
        
        result = selector.select_best(
            real_timeseries, 
            target_col="PM10",
            forecast_steps=6
        )
        
        assert result["best_model"] is not None

    def test_model_error_comparison(self, real_timeseries):
        """Test error metrics comparison."""
        comparator = ModelComparator()
        comparator.add_model("SARIMA", SARIMAModel())
        comparator.add_model("XGBoost", XGBoostModel())
        
        result = comparator.train_and_compare(real_timeseries)
        metrics = result["metrics"]
        
        # Check that both models have valid metrics
        assert len(metrics) == 2
        for model_name, metric_dict in metrics.items():
            assert 0 <= metric_dict["MAE"] <= 1000
            assert 0 <= metric_dict["RMSE"] <= 1000
            assert metric_dict["RMSE"] >= metric_dict["MAE"]
