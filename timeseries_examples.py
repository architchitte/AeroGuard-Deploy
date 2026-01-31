"""
Time-Series Preprocessing Examples and Tests

This script demonstrates how to use the TimeSeriesPreprocessor
for air quality data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from app.utils.timeseries_preprocessor import (
    TimeSeriesPreprocessor,
    load_and_preprocess_aqi,
    load_and_preprocess_pm25,
)


def create_sample_aq_data(filename: str = "sample_aq_data.csv", n_rows: int = 500):
    """
    Create sample air quality data for testing.

    Args:
        filename: Output CSV filename
        n_rows: Number of rows to generate
    """
    # Create datetime index (hourly)
    dates = pd.date_range("2023-01-01", periods=n_rows, freq="H")

    # Create realistic air quality data with patterns
    np.random.seed(42)
    base_pm25 = 50 + 20 * np.sin(np.arange(n_rows) * 2 * np.pi / 168)  # Weekly cycle
    pm25 = base_pm25 + np.random.normal(0, 5, n_rows)

    base_pm10 = 80 + 30 * np.sin(np.arange(n_rows) * 2 * np.pi / 168)
    pm10 = base_pm10 + np.random.normal(0, 8, n_rows)

    # AQI (simplified)
    aqi = (pm25 + pm10) / 2 + np.random.normal(0, 3, n_rows)

    # Add some missing values
    missing_indices = np.random.choice(n_rows, size=int(0.05 * n_rows), replace=False)
    pm25[missing_indices] = np.nan
    pm10[missing_indices[:len(missing_indices)//2]] = np.nan

    # Add some outliers
    outlier_indices = np.random.choice(n_rows, size=5, replace=False)
    pm25[outlier_indices] = pm25[outlier_indices] * 3

    # Create DataFrame
    df = pd.DataFrame({
        "datetime": dates,
        "PM2.5": pm25,
        "PM10": pm10,
        "AQI": aqi,
    })

    # Ensure non-negative values
    df[["PM2.5", "PM10", "AQI"]] = df[["PM2.5", "PM10", "AQI"]].clip(lower=0)

    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"✓ Created sample data: {filename} ({n_rows} rows)")
    return df


def example_basic_preprocessing():
    """Example 1: Basic preprocessing with default settings."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Preprocessing")
    print("="*70)

    # Create sample data
    create_sample_aq_data("sample_basic.csv", n_rows=500)

    # Preprocess
    preprocessor = TimeSeriesPreprocessor(
        datetime_column="datetime",
        target_columns=["PM2.5", "AQI"],
    )

    df = preprocessor.preprocess(
        "sample_basic.csv",
        datetime_column="datetime",
    )

    print("\nData sample:")
    print(df.head(10))
    print("\nData info:")
    print(df.info())
    print("\nStatistics:")
    print(df.describe())

    return df


def example_custom_lag_windows():
    """Example 2: Custom lag hours and rolling windows."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Custom Lag Hours and Rolling Windows")
    print("="*70)

    create_sample_aq_data("sample_custom.csv", n_rows=500)

    preprocessor = TimeSeriesPreprocessor(
        datetime_column="datetime",
        target_columns=["PM2.5", "PM10"],
    )

    df = preprocessor.preprocess(
        "sample_custom.csv",
        datetime_column="datetime",
        target_columns=["PM2.5", "PM10"],
        lag_hours=[1, 2, 4, 8, 12],  # More lag features
        rolling_windows=[2, 4, 12],  # Different window sizes
    )

    print("\nFeature columns created:")
    feature_cols = [col for col in df.columns if any(
        x in col for x in ["lag", "mean", "std"]
    )]
    print(f"Total: {len(feature_cols)} features")
    print("Sample:", feature_cols[:5])

    return df


def example_outlier_methods():
    """Example 3: Compare outlier detection methods."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Outlier Detection Methods")
    print("="*70)

    create_sample_aq_data("sample_outliers.csv", n_rows=500)

    # IQR method
    print("\n--- IQR Method ---")
    preprocessor_iqr = TimeSeriesPreprocessor(
        datetime_column="datetime",
        target_columns=["PM2.5"],
    )
    df_iqr = preprocessor_iqr.preprocess(
        "sample_outliers.csv",
        target_columns=["PM2.5"],
        outlier_method="iqr",
        lag_hours=[1, 3],
        rolling_windows=[3],
    )

    # Z-score method
    print("\n--- Z-Score Method ---")
    preprocessor_zscore = TimeSeriesPreprocessor(
        datetime_column="datetime",
        target_columns=["PM2.5"],
    )
    df_zscore = preprocessor_zscore.preprocess(
        "sample_outliers.csv",
        target_columns=["PM2.5"],
        outlier_method="zscore",
        lag_hours=[1, 3],
        rolling_windows=[3],
    )

    print("\nComparison:")
    print(f"IQR result shape: {df_iqr.shape}")
    print(f"Z-score result shape: {df_zscore.shape}")

    return df_iqr, df_zscore


def example_missing_value_methods():
    """Example 4: Compare missing value handling methods."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Missing Value Handling Methods")
    print("="*70)

    create_sample_aq_data("sample_missing.csv", n_rows=500)

    methods = ["forward_fill", "rolling_mean", "both"]
    results = {}

    for method in methods:
        print(f"\n--- {method.upper()} Method ---")
        preprocessor = TimeSeriesPreprocessor(
            datetime_column="datetime",
            target_columns=["PM2.5", "PM10"],
        )

        df = preprocessor.preprocess(
            "sample_missing.csv",
            target_columns=["PM2.5", "PM10"],
            missing_method=method,
            lag_hours=[1, 3],
            rolling_windows=[3],
        )

        results[method] = {
            "shape": df.shape,
            "missing": df[["PM2.5", "PM10"]].isnull().sum().sum(),
        }

    print("\nSummary:")
    for method, stats in results.items():
        print(f"{method}: shape={stats['shape']}, missing={stats['missing']}")

    return results


def example_convenience_functions():
    """Example 5: Using convenience functions."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Convenience Functions")
    print("="*70)

    create_sample_aq_data("sample_convenience.csv", n_rows=500)

    # Quick AQI preprocessing
    print("\n--- Quick AQI Preprocessing ---")
    df_aqi = load_and_preprocess_aqi("sample_convenience.csv")
    print(f"Shape: {df_aqi.shape}")
    print(f"Columns: {list(df_aqi.columns)}")

    # Quick PM2.5 preprocessing
    print("\n--- Quick PM2.5 Preprocessing ---")
    df_pm25 = load_and_preprocess_pm25("sample_convenience.csv")
    print(f"Shape: {df_pm25.shape}")
    print(f"Columns: {list(df_pm25.columns)}")

    return df_aqi, df_pm25


def example_custom_datetime_format():
    """Example 6: Custom datetime format."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Custom Datetime Format")
    print("="*70)

    # Create data with different datetime format
    dates = pd.date_range("2023-01-01", periods=200, freq="H")
    df = pd.DataFrame({
        "date_str": dates.strftime("%d/%m/%Y %H:%M"),  # DD/MM/YYYY HH:MM format
        "PM2.5": np.random.uniform(30, 80, 200),
        "AQI": np.random.uniform(50, 150, 200),
    })
    df.to_csv("sample_custom_format.csv", index=False)

    preprocessor = TimeSeriesPreprocessor(
        datetime_column="date_str",
        target_columns=["PM2.5"],
    )

    result = preprocessor.preprocess(
        "sample_custom_format.csv",
        datetime_column="date_str",
        datetime_format="%d/%m/%Y %H:%M",  # Specify format
        lag_hours=[1, 3],
        rolling_windows=[3],
    )

    print(f"\nSuccessfully handled custom datetime format")
    print(f"Result shape: {result.shape}")
    print(f"Index range: {result.index.min()} to {result.index.max()}")

    return result


def example_save_preprocessed_data():
    """Example 7: Save preprocessed data for modeling."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Save Preprocessed Data")
    print("="*70)

    create_sample_aq_data("sample_save.csv", n_rows=500)

    preprocessor = TimeSeriesPreprocessor(
        datetime_column="datetime",
        target_columns=["PM2.5", "PM10"],
    )

    df = preprocessor.preprocess(
        "sample_save.csv",
        target_columns=["PM2.5", "PM10"],
        lag_hours=[1, 3, 6],
        rolling_windows=[3, 6],
    )

    # Save to CSV
    output_file = "preprocessed_aq_data.csv"
    df.to_csv(output_file)
    print(f"✓ Saved to {output_file}")

    # Save as pickle for fast loading
    pickle_file = "preprocessed_aq_data.pkl"
    df.to_pickle(pickle_file)
    print(f"✓ Saved to {pickle_file}")

    # Display file sizes
    import os
    csv_size = os.path.getsize(output_file) / 1024
    pkl_size = os.path.getsize(pickle_file) / 1024
    print(f"\nFile sizes:")
    print(f"  CSV: {csv_size:.1f} KB")
    print(f"  Pickle: {pkl_size:.1f} KB")

    return df


def main():
    """Run all examples."""
    print("\n" + "🎯" * 35)
    print("TIME-SERIES PREPROCESSING EXAMPLES")
    print("🎯" * 35)

    try:
        # Run examples
        example_basic_preprocessing()
        example_custom_lag_windows()
        example_outlier_methods()
        example_missing_value_methods()
        example_convenience_functions()
        example_custom_datetime_format()
        example_save_preprocessed_data()

        print("\n" + "="*70)
        print("✅ All examples completed successfully!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
