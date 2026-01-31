"""
Unit Tests for TimeSeriesPreprocessor

Test suite for air quality time-series preprocessing module.
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
from app.utils.timeseries_preprocessor import (
    TimeSeriesPreprocessor,
    load_and_preprocess_aqi,
    load_and_preprocess_pm25,
)


class TestTimeSeriesPreprocessor(unittest.TestCase):
    """Test cases for TimeSeriesPreprocessor class."""

    @classmethod
    def setUpClass(cls):
        """Create sample test data."""
        # Create test CSV
        cls.test_file = "test_aq_data.csv"
        dates = pd.date_range("2023-01-01", periods=100, freq="H")

        np.random.seed(42)
        data = {
            "datetime": dates,
            "PM2.5": np.random.uniform(30, 80, 100),
            "PM10": np.random.uniform(40, 100, 100),
            "AQI": np.random.uniform(50, 150, 100),
        }

        df = pd.DataFrame(data)
        df.to_csv(cls.test_file, index=False)

    @classmethod
    def tearDownClass(cls):
        """Clean up test files."""
        if Path(cls.test_file).exists():
            Path(cls.test_file).unlink()

    def setUp(self):
        """Create preprocessor instance for each test."""
        self.preprocessor = TimeSeriesPreprocessor(
            datetime_column="datetime",
            target_columns=["PM2.5", "AQI"],
        )

    def test_initialization(self):
        """Test TimeSeriesPreprocessor initialization."""
        self.assertEqual(self.preprocessor.datetime_column, "datetime")
        self.assertEqual(self.preprocessor.target_columns, ["PM2.5", "AQI"])

    def test_load_csv(self):
        """Test CSV loading."""
        df = self.preprocessor.load_csv(self.test_file)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 100)
        self.assertIn("datetime", df.columns)

    def test_load_csv_file_not_found(self):
        """Test error when CSV file not found."""
        with self.assertRaises(FileNotFoundError):
            self.preprocessor.load_csv("nonexistent.csv")

    def test_parse_datetime(self):
        """Test datetime parsing."""
        df = self.preprocessor.load_csv(self.test_file)
        df = self.preprocessor.parse_datetime(df)

        # Check if datetime is index
        self.assertIsInstance(df.index, pd.DatetimeIndex)
        # Check sorting
        self.assertTrue(df.index.is_monotonic_increasing)

    def test_parse_datetime_custom_format(self):
        """Test datetime parsing with custom format."""
        # Create CSV with custom format
        dates = pd.date_range("2023-01-01", periods=20, freq="H")
        data = {
            "date_str": dates.strftime("%d/%m/%Y %H:%M"),
            "PM2.5": np.random.uniform(30, 80, 20),
        }
        df = pd.DataFrame(data)
        df.to_csv("test_custom_format.csv", index=False)

        try:
            preprocessor = TimeSeriesPreprocessor(
                datetime_column="date_str",
                target_columns=["PM2.5"],
            )
            df = preprocessor.load_csv("test_custom_format.csv")
            df = preprocessor.parse_datetime(
                df,
                datetime_column="date_str",
                datetime_format="%d/%m/%Y %H:%M",
            )

            self.assertIsInstance(df.index, pd.DatetimeIndex)
        finally:
            Path("test_custom_format.csv").unlink()

    def test_handle_missing_values_forward_fill(self):
        """Test forward fill missing value handling."""
        df = self.preprocessor.load_csv(self.test_file)
        df = self.preprocessor.parse_datetime(df)

        # Add missing values
        df.loc[df.index[5:10], "PM2.5"] = np.nan

        df_filled = self.preprocessor.handle_missing_values(
            df, method="forward_fill"
        )

        # Check that NaN is reduced
        self.assertLess(df_filled[["PM2.5", "AQI"]].isnull().sum().sum(), 5)

    def test_handle_missing_values_rolling_mean(self):
        """Test rolling mean missing value handling."""
        df = self.preprocessor.load_csv(self.test_file)
        df = self.preprocessor.parse_datetime(df)

        # Add missing values
        df.loc[df.index[5:15], "AQI"] = np.nan

        df_filled = self.preprocessor.handle_missing_values(
            df, method="rolling_mean", rolling_window=3
        )

        # Check that NaN is reduced
        self.assertLess(df_filled[["PM2.5", "AQI"]].isnull().sum().sum(), 5)

    def test_handle_missing_values_both(self):
        """Test hybrid missing value handling."""
        df = self.preprocessor.load_csv(self.test_file)
        df = self.preprocessor.parse_datetime(df)

        # Add missing values
        df.loc[df.index[5:20], "PM2.5"] = np.nan

        df_filled = self.preprocessor.handle_missing_values(
            df, method="both"
        )

        # Check improvement
        self.assertLess(df_filled[["PM2.5", "AQI"]].isnull().sum().sum(), 10)

    def test_remove_outliers_iqr(self):
        """Test IQR-based outlier removal."""
        df = self.preprocessor.load_csv(self.test_file)
        df = self.preprocessor.parse_datetime(df)

        # Add outliers
        df.loc[df.index[5], "PM2.5"] = 500

        df_clean, stats = self.preprocessor.remove_outliers(df, method="iqr")

        # Check that outlier was handled
        self.assertTrue(df_clean["PM2.5"].max() < 500)
        self.assertIn("PM2.5", stats)

    def test_remove_outliers_zscore(self):
        """Test Z-score based outlier removal."""
        df = self.preprocessor.load_csv(self.test_file)
        df = self.preprocessor.parse_datetime(df)

        # Add outlier
        df.loc[df.index[10], "AQI"] = 500

        df_clean, stats = self.preprocessor.remove_outliers(
            df, method="zscore"
        )

        # Check stats structure
        self.assertIn("AQI", stats)
        self.assertIn("count", stats["AQI"])
        self.assertIn("percentage", stats["AQI"])

    def test_create_lag_features(self):
        """Test lag feature creation."""
        df = self.preprocessor.load_csv(self.test_file)
        df = self.preprocessor.parse_datetime(df)

        df_lags = self.preprocessor.create_lag_features(
            df, lag_hours=[1, 3, 6]
        )

        # Check new columns
        expected_cols = [
            "PM2.5_lag_1h",
            "PM2.5_lag_3h",
            "PM2.5_lag_6h",
            "AQI_lag_1h",
            "AQI_lag_3h",
            "AQI_lag_6h",
        ]

        for col in expected_cols:
            self.assertIn(col, df_lags.columns)

    def test_create_rolling_statistics(self):
        """Test rolling statistics creation."""
        df = self.preprocessor.load_csv(self.test_file)
        df = self.preprocessor.parse_datetime(df)

        df_rolling = self.preprocessor.create_rolling_statistics(
            df, windows=[3, 6]
        )

        # Check new columns
        expected_cols = [
            "PM2.5_mean_3h",
            "PM2.5_std_3h",
            "PM2.5_mean_6h",
            "PM2.5_std_6h",
            "AQI_mean_3h",
            "AQI_std_3h",
            "AQI_mean_6h",
            "AQI_std_6h",
        ]

        for col in expected_cols:
            self.assertIn(col, df_rolling.columns)

    def test_complete_preprocessing_pipeline(self):
        """Test complete preprocessing pipeline."""
        df = self.preprocessor.preprocess(
            self.test_file,
            datetime_column="datetime",
            target_columns=["PM2.5", "AQI"],
            lag_hours=[1, 3],
            rolling_windows=[3],
            drop_na=True,
        )

        # Check result properties
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIsInstance(df.index, pd.DatetimeIndex)
        self.assertGreater(len(df), 0)
        self.assertLess(df.isnull().sum().sum(), 5)

    def test_preprocessing_shape_after_feature_creation(self):
        """Test that preprocessing creates expected number of columns."""
        df = self.preprocessor.preprocess(
            self.test_file,
            lag_hours=[1, 3],
            rolling_windows=[3, 6],
            drop_na=False,
        )

        # Count expected columns
        # Original: 3 (PM2.5, AQI, PM10)
        # Lags: 3 * 2 = 6
        # Rolling: 3 * 2 * 2 = 12
        # Total: 3 + 6 + 12 = 21

        expected_feature_cols = 2 * 2 + 2 * 2 * 2  # lags + rolling
        self.assertGreaterEqual(df.shape[1], expected_feature_cols)

    def test_convenience_function_aqi(self):
        """Test convenience function for AQI data."""
        df = load_and_preprocess_aqi(self.test_file)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(df.shape[0], 0)
        # Should have lag and rolling features
        self.assertGreater(df.shape[1], 3)

    def test_convenience_function_pm25(self):
        """Test convenience function for PM2.5 data."""
        df = load_and_preprocess_pm25(self.test_file)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(df.shape[0], 0)
        # Should have lag and rolling features
        self.assertGreater(df.shape[1], 1)

    def test_statistics_tracking(self):
        """Test that statistics are tracked during preprocessing."""
        self.preprocessor.preprocess(self.test_file)

        stats = self.preprocessor.get_statistics()

        self.assertIn("original_shape", stats)
        self.assertIn("missing_values", stats)
        self.assertIsNotNone(stats["original_shape"])

    def test_edge_case_small_dataframe(self):
        """Test preprocessing with small dataset."""
        # Create small test file
        small_file = "test_small.csv"
        dates = pd.date_range("2023-01-01", periods=10, freq="H")
        data = {
            "datetime": dates,
            "PM2.5": np.random.uniform(30, 80, 10),
        }
        df = pd.DataFrame(data)
        df.to_csv(small_file, index=False)

        try:
            preprocessor = TimeSeriesPreprocessor(
                target_columns=["PM2.5"]
            )
            result = preprocessor.preprocess(small_file, drop_na=False)

            self.assertIsInstance(result, pd.DataFrame)
            self.assertGreater(len(result), 0)
        finally:
            Path(small_file).unlink()

    def test_edge_case_all_missing_column(self):
        """Test handling of column with all missing values."""
        df = self.preprocessor.load_csv(self.test_file)
        df = self.preprocessor.parse_datetime(df)

        # Create column with all NaN
        df["all_nan"] = np.nan

        df_filled = self.preprocessor.handle_missing_values(df)

        # Should still have NaN in this column (can't fill all NaN)
        self.assertTrue(df_filled["all_nan"].isnull().any())

    def test_datetime_index_properties(self):
        """Test that datetime index has correct properties."""
        df = self.preprocessor.preprocess(
            self.test_file,
            drop_na=False
        )

        # Check index properties
        self.assertEqual(df.index.name, "datetime")
        self.assertTrue(df.index.is_monotonic_increasing)
        # For hourly data
        self.assertTrue(
            all(df.index.to_series().diff().dt.total_seconds().dropna() >= 3600)
        )


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_invalid_missing_method(self):
        """Test error with invalid missing value method."""
        preprocessor = TimeSeriesPreprocessor()
        dates = pd.date_range("2023-01-01", periods=10, freq="H")
        df = pd.DataFrame(
            {"PM2.5": np.random.rand(10)},
            index=dates
        )

        with self.assertRaises(ValueError):
            preprocessor.handle_missing_values(df, method="invalid")

    def test_invalid_outlier_method(self):
        """Test error with invalid outlier method."""
        preprocessor = TimeSeriesPreprocessor()
        dates = pd.date_range("2023-01-01", periods=10, freq="H")
        df = pd.DataFrame(
            {"PM2.5": np.random.rand(10)},
            index=dates
        )

        with self.assertRaises(ValueError):
            preprocessor.remove_outliers(df, method="invalid")

    def test_missing_datetime_column(self):
        """Test error when datetime column is missing."""
        preprocessor = TimeSeriesPreprocessor(datetime_column="nonexistent")
        df = pd.DataFrame({"PM2.5": [1, 2, 3]})

        with self.assertRaises(ValueError):
            preprocessor.parse_datetime(df)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[""], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
