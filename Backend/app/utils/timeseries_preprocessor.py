"""
Time-Series Preprocessing for Air Quality Data

This module provides utilities for preprocessing air quality time-series data,
including loading, cleaning, feature engineering, and outlier detection.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path


class TimeSeriesPreprocessor:
    """
    Comprehensive time-series preprocessing for air quality data.
    
    Handles CSV loading, datetime parsing, missing value imputation,
    outlier detection, and feature engineering (lag features and
    rolling statistics).
    """

    def __init__(
        self,
        datetime_column: str = "datetime",
        target_columns: Optional[List[str]] = None,
    ):
        """
        Initialize the time-series preprocessor.

        Args:
            datetime_column: Name of the datetime column
            target_columns: Air quality parameter columns to process
                           (e.g., ["PM2.5", "AQI", "NO2"])
        """
        self.datetime_column = datetime_column
        self.target_columns = target_columns or ["PM2.5", "AQI"]
        self.original_shape = None
        self.missing_value_stats = {}

    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        Load air quality data from CSV file.

        Args:
            filepath: Path to CSV file

        Returns:
            Pandas DataFrame with raw data

        Raises:
            FileNotFoundError: If file doesn't exist
            pd.errors.ParserError: If CSV is malformed
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        try:
            df = pd.read_csv(filepath)
            print(f"✓ Loaded {len(df)} rows from {filepath.name}")
            return df
        except pd.errors.ParserError as e:
            raise pd.errors.ParserError(f"Failed to parse CSV: {str(e)}")

    def parse_datetime(
        self,
        df: pd.DataFrame,
        datetime_column: Optional[str] = None,
        datetime_format: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Parse and validate datetime column.

        Args:
            df: Input DataFrame
            datetime_column: Column name (overrides default)
            datetime_format: strftime format string (e.g., "%Y-%m-%d %H:%M:%S")
                            If None, pandas will infer format

        Returns:
            DataFrame with parsed datetime as index

        Raises:
            ValueError: If datetime column not found or parsing fails
        """
        col = datetime_column or self.datetime_column

        if col not in df.columns:
            raise ValueError(f"Datetime column '{col}' not found in data")

        try:
            if datetime_format:
                df[col] = pd.to_datetime(df[col], format=datetime_format)
            else:
                df[col] = pd.to_datetime(df[col])

            # Set as index and sort
            df = df.set_index(col).sort_index()
            df.index.name = col

            print(f"✓ Parsed datetime: {df.index.min()} to {df.index.max()}")
            return df

        except Exception as e:
            raise ValueError(f"Failed to parse datetime: {str(e)}")

    def handle_missing_values(
        self,
        df: pd.DataFrame,
        method: str = "forward_fill",
        rolling_window: int = 3,
    ) -> pd.DataFrame:
        """
        Handle missing values in air quality data.

        Args:
            df: Input DataFrame with datetime index
            method: Imputation method
                   - "forward_fill": Forward fill missing values
                   - "rolling_mean": Replace with rolling mean
                   - "both": Forward fill then rolling mean for remaining
            rolling_window: Window size for rolling mean (in hours)

        Returns:
            DataFrame with missing values imputed
        """
        initial_missing = df[self.target_columns].isnull().sum()
        self.missing_value_stats["before"] = initial_missing.to_dict()

        if method == "forward_fill":
            df_filled = df.fillna(method="ffill", limit=24)
            df_filled = df_filled.fillna(method="bfill", limit=24)

        elif method == "rolling_mean":
            df_filled = df.copy()
            for col in self.target_columns:
                mask = df_filled[col].isnull()
                df_filled[col] = df_filled[col].fillna(
                    df_filled[col].rolling(
                        window=rolling_window,
                        center=True,
                        min_periods=1,
                    ).mean()
                )

        elif method == "both":
            # First forward fill
            df_filled = df.fillna(method="ffill", limit=12)
            # Then rolling mean for remaining
            for col in self.target_columns:
                mask = df_filled[col].isnull()
                df_filled[col] = df_filled[col].fillna(
                    df_filled[col].rolling(
                        window=rolling_window,
                        center=True,
                        min_periods=1,
                    ).mean()
                )

        else:
            raise ValueError(
                f"Unknown method: {method}. "
                f"Use 'forward_fill', 'rolling_mean', or 'both'"
            )

        final_missing = df_filled[self.target_columns].isnull().sum()
        self.missing_value_stats["after"] = final_missing.to_dict()
        self.missing_value_stats["method"] = method

        print(f"✓ Handled missing values using '{method}' method")
        print(f"  Before: {initial_missing.sum()} missing values")
        print(f"  After: {final_missing.sum()} missing values")

        return df_filled

    def remove_outliers(
        self,
        df: pd.DataFrame,
        method: str = "iqr",
        iqr_multiplier: float = 1.5,
        std_multiplier: float = 3.0,
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Remove outliers from air quality data.

        Args:
            df: Input DataFrame
            method: Outlier detection method
                   - "iqr": Interquartile range method
                   - "zscore": Z-score method
            iqr_multiplier: IQR multiplier for bounds (default 1.5)
            std_multiplier: Standard deviation multiplier (default 3.0)

        Returns:
            Tuple of (cleaned DataFrame, outlier statistics)
        """
        outlier_stats = {}

        for col in self.target_columns:
            if col not in df.columns:
                continue

            initial_count = len(df)

            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1

                lower_bound = Q1 - iqr_multiplier * IQR
                upper_bound = Q3 + iqr_multiplier * IQR

                # Mark outliers
                is_outlier = (df[col] < lower_bound) | (df[col] > upper_bound)

            elif method == "zscore":
                mean = df[col].mean()
                std = df[col].std()
                z_scores = np.abs((df[col] - mean) / std)
                is_outlier = z_scores > std_multiplier

            else:
                raise ValueError(
                    f"Unknown method: {method}. Use 'iqr' or 'zscore'"
                )

            n_outliers = is_outlier.sum()
            outlier_stats[col] = {
                "count": int(n_outliers),
                "percentage": float((n_outliers / initial_count) * 100),
            }

            # Replace outliers with rolling median
            df.loc[is_outlier, col] = df.loc[is_outlier, col].rolling(
                window=5, center=True, min_periods=1
            ).median()

        total_outliers = sum(s["count"] for s in outlier_stats.values())
        print(f"✓ Removed/fixed {total_outliers} outliers using '{method}'")

        return df, outlier_stats

    def create_lag_features(
        self,
        df: pd.DataFrame,
        lag_hours: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """
        Create lagged features for time-series modeling.

        Args:
            df: Input DataFrame with datetime index (hourly frequency)
            lag_hours: List of lag hours to create
                      (default: [1, 3, 6])

        Returns:
            DataFrame with additional lag feature columns
        """
        if lag_hours is None:
            lag_hours = [1, 3, 6]

        for col in self.target_columns:
            if col not in df.columns:
                continue

            for lag in lag_hours:
                lag_col_name = f"{col}_lag_{lag}h"
                df[lag_col_name] = df[col].shift(lag)

        n_lag_cols = len(self.target_columns) * len(lag_hours)
        print(f"✓ Created {n_lag_cols} lag features: {lag_hours}h")

        return df

    def create_rolling_statistics(
        self,
        df: pd.DataFrame,
        windows: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """
        Create rolling statistics (mean, std) for features.

        Args:
            df: Input DataFrame with datetime index (hourly frequency)
            windows: List of rolling window sizes in hours
                    (default: [3, 6])

        Returns:
            DataFrame with additional rolling statistic columns
        """
        if windows is None:
            windows = [3, 6]

        for col in self.target_columns:
            if col not in df.columns:
                continue

            for window in windows:
                # Rolling mean
                mean_col = f"{col}_mean_{window}h"
                df[mean_col] = df[col].rolling(
                    window=window, center=True, min_periods=1
                ).mean()

                # Rolling standard deviation
                std_col = f"{col}_std_{window}h"
                df[std_col] = df[col].rolling(
                    window=window, center=True, min_periods=1
                ).std()

        n_rolling_cols = len(self.target_columns) * len(windows) * 2
        print(f"✓ Created {n_rolling_cols} rolling statistics: {windows}h windows")

        return df

    def preprocess(
        self,
        filepath: str,
        datetime_column: str = "datetime",
        datetime_format: Optional[str] = None,
        target_columns: Optional[List[str]] = None,
        missing_method: str = "forward_fill",
        outlier_method: str = "iqr",
        lag_hours: Optional[List[int]] = None,
        rolling_windows: Optional[List[int]] = None,
        drop_na: bool = True,
    ) -> pd.DataFrame:
        """
        Complete preprocessing pipeline for air quality time-series data.

        Args:
            filepath: Path to CSV file
            datetime_column: Name of datetime column
            datetime_format: Datetime format string
            target_columns: Air quality parameter columns
            missing_method: Method for handling missing values
            outlier_method: Method for outlier detection
            lag_hours: Lag hours for feature creation
            rolling_windows: Rolling window sizes
            drop_na: Drop rows with NaN values after feature creation

        Returns:
            Clean pandas DataFrame ready for modeling

        Example:
            >>> preprocessor = TimeSeriesPreprocessor()
            >>> df = preprocessor.preprocess(
            ...     "aq_data.csv",
            ...     target_columns=["PM2.5", "AQI"],
            ...     lag_hours=[1, 3, 6],
            ...     rolling_windows=[3, 6]
            ... )
        """
        # Update configuration
        self.datetime_column = datetime_column
        if target_columns:
            self.target_columns = target_columns

        print("\n" + "=" * 60)
        print("Air Quality Time-Series Preprocessing Pipeline")
        print("=" * 60 + "\n")

        # Step 1: Load data
        df = self.load_csv(filepath)
        self.original_shape = df.shape

        # Step 2: Parse datetime
        df = self.parse_datetime(df, datetime_column, datetime_format)

        # Step 3: Handle missing values
        df = self.handle_missing_values(df, method=missing_method)

        # Step 4: Remove outliers
        df, outlier_stats = self.remove_outliers(df, method=outlier_method)

        # Step 5: Create lag features
        df = self.create_lag_features(df, lag_hours)

        # Step 6: Create rolling statistics
        df = self.create_rolling_statistics(df, rolling_windows)

        # Step 7: Handle NaN from feature creation
        if drop_na:
            initial_rows = len(df)
            df = df.dropna()
            final_rows = len(df)
            dropped = initial_rows - final_rows
            print(f"✓ Dropped {dropped} rows with NaN (after feature creation)")

        # Summary statistics
        print("\n" + "=" * 60)
        print("Preprocessing Summary")
        print("=" * 60)
        print(f"Original shape: {self.original_shape}")
        print(f"Final shape: {df.shape}")
        print(f"Features created: {df.shape[1]} columns")
        print(f"Time range: {df.index.min()} to {df.index.max()}")
        print("=" * 60 + "\n")

        return df

    def get_statistics(self) -> Dict:
        """
        Get preprocessing statistics.

        Returns:
            Dictionary with preprocessing information
        """
        return {
            "original_shape": self.original_shape,
            "missing_values": self.missing_value_stats,
        }


# Convenience functions for common use cases

def load_and_preprocess_aqi(
    filepath: str,
    datetime_column: str = "datetime",
    drop_na: bool = True,
) -> pd.DataFrame:
    """
    Quick preprocessing for standard AQI data.

    Args:
        filepath: Path to CSV file
        datetime_column: Name of datetime column
        drop_na: Drop rows with NaN

    Returns:
        Preprocessed DataFrame
    """
    preprocessor = TimeSeriesPreprocessor(
        datetime_column=datetime_column,
        target_columns=["AQI", "PM2.5", "PM10"],
    )

    return preprocessor.preprocess(
        filepath,
        datetime_column=datetime_column,
        target_columns=["AQI", "PM2.5", "PM10"],
        lag_hours=[1, 3, 6],
        rolling_windows=[3, 6],
        drop_na=drop_na,
    )


def load_and_preprocess_pm25(
    filepath: str,
    datetime_column: str = "datetime",
    drop_na: bool = True,
) -> pd.DataFrame:
    """
    Quick preprocessing for PM2.5 focused data.

    Args:
        filepath: Path to CSV file
        datetime_column: Name of datetime column
        drop_na: Drop rows with NaN

    Returns:
        Preprocessed DataFrame
    """
    preprocessor = TimeSeriesPreprocessor(
        datetime_column=datetime_column,
        target_columns=["PM2.5"],
    )

    return preprocessor.preprocess(
        filepath,
        datetime_column=datetime_column,
        target_columns=["PM2.5"],
        lag_hours=[1, 3, 6],
        rolling_windows=[3, 6],
        drop_na=drop_na,
    )
