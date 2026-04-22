"""Data ingestion and preprocessing utilities for AeroGuard.

This module provides a small, focused `DataPreprocessor` class that loads
air-quality CSVs, parses datetimes, handles missing values, removes outliers
using the IQR method, creates lag features and rolling statistics, and
returns a cleaned DataFrame ready for modeling.

The implementation is intentionally lightweight and dependency-minimal: it
uses pandas and numpy only.
"""
from __future__ import annotations

from typing import List, Optional, Tuple, Dict
import pandas as pd
import numpy as np
from pathlib import Path


class DataPreprocessor:
    """Preprocess air quality time-series data.

    Responsibilities:
    - Load AQI / PM2.5 data from CSV
    - Parse datetime column (auto-detect or use provided format)
    - Handle missing values (forward fill, rolling mean, or both)
    - Remove outliers using the IQR method
    - Create lag features (configurable hours)
    - Create rolling statistics (mean/std for configurable windows)

    Example:
        pre = DataPreprocessor(datetime_col="time", target_cols=["PM2.5", "AQI"])\
            .preprocess("data.csv", lag_hours=[1,3,6], rolling_windows=[3,6])
    """

    def __init__(
        self,
        datetime_col: str = "datetime",
        target_cols: Optional[List[str]] = None,
    ) -> None:
        """Initialize the preprocessor.

        Args:
            datetime_col: Name of the datetime column in the CSV.
            target_cols: List of target columns to process. If None, common
                columns ("PM2.5", "PM10", "AQI") will be used if present.
        """
        self.datetime_col = datetime_col
        self.target_cols = target_cols
        self._stats: Dict[str, object] = {}

    def load_csv(self, filepath: str) -> pd.DataFrame:
        """Load CSV from disk into a DataFrame.

        Args:
            filepath: Path to the CSV file.

        Returns:
            pd.DataFrame: Raw dataframe read from CSV.
        """
        p = Path(filepath)
        if not p.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        df = pd.read_csv(p)
        return df

    def parse_datetime(self, df: pd.DataFrame, datetime_format: Optional[str] = None) -> pd.DataFrame:
        """Parse and set the datetime column as a sorted index.

        Args:
            df: Input DataFrame.
            datetime_format: Optional strptime format to speed parsing.

        Returns:
            pd.DataFrame with a DateTimeIndex named `datetime`.
        """
        if self.datetime_col not in df.columns:
            raise KeyError(f"Datetime column '{self.datetime_col}' not found in dataframe")
        if datetime_format:
            df[self.datetime_col] = pd.to_datetime(df[self.datetime_col], format=datetime_format)
        else:
            df[self.datetime_col] = pd.to_datetime(df[self.datetime_col], infer_datetime_format=True, utc=False, errors="raise")
        df = df.sort_values(self.datetime_col).set_index(self.datetime_col)
        df.index.name = "datetime"
        return df

    def _infer_target_cols(self, df: pd.DataFrame) -> List[str]:
        if self.target_cols:
            return [c for c in self.target_cols if c in df.columns]
        common = ["PM2.5", "PM10", "AQI", "pm25", "pm10"]
        found = [c for c in common if c in df.columns]
        return found

    def handle_missing_values(
        self,
        df: pd.DataFrame,
        method: str = "forward_fill",
        rolling_window: int = 3,
    ) -> pd.DataFrame:
        """Handle missing values using one of the supported methods.

        Args:
            df: DataFrame with DateTimeIndex.
            method: One of `forward_fill`, `rolling_mean`, or `both`.
            rolling_window: Window size for rolling mean interpolation.

        Returns:
            DataFrame with missing values imputed.
        """
        if method not in {"forward_fill", "rolling_mean", "both"}:
            raise ValueError("method must be 'forward_fill', 'rolling_mean' or 'both'")

        if method == "forward_fill":
            return df.ffill()

        if method == "rolling_mean":
            return df.fillna(df.rolling(window=rolling_window, min_periods=1).mean())

        # both: rolling mean first, then forward fill
        tmp = df.fillna(df.rolling(window=rolling_window, min_periods=1).mean())
        return tmp.ffill()

    def remove_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None, iqr_multiplier: float = 1.5) -> Tuple[pd.DataFrame, Dict[str, Tuple[float, float]]]:
        """Detect and replace outliers using the IQR method.

        Outliers are replaced with the rolling median (window=3) to keep
        local structure.

        Args:
            df: Input DataFrame.
            columns: Columns to examine; if None, infer target columns.
            iqr_multiplier: Multiplier for the IQR fence.

        Returns:
            Tuple of (cleaned_df, stats) where stats maps column -> (lower, upper).
        """
        cols = columns or self._infer_target_cols(df)
        stats: Dict[str, Tuple[float, float]] = {}
        out = df.copy()
        for c in cols:
            if c not in out.columns:
                continue
            series = out[c].astype(float)
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - iqr_multiplier * iqr
            upper = q3 + iqr_multiplier * iqr
            stats[c] = (float(lower), float(upper))
            mask = (series < lower) | (series > upper)
            if mask.any():
                # replace outliers with rolling median
                replacement = series.mask(mask).rolling(window=3, min_periods=1).median()
                out.loc[mask, c] = replacement.loc[mask]
        self._stats.setdefault("outliers", {}).update(stats)
        return out, stats

    def create_lag_features(self, df: pd.DataFrame, lag_hours: Optional[List[int]] = None, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Create lag features for specified columns.

        Args:
            df: DataFrame with DateTimeIndex at hourly frequency (preferred).
            lag_hours: List of integers (hours) for lagging. Defaults to [1,3,6].
            columns: Columns to create lags for; if None, infer target columns.

        Returns:
            DataFrame with new lag columns appended.
        """
        if lag_hours is None:
            lag_hours = [1, 3, 6]
        cols = columns or self._infer_target_cols(df)
        out = df.copy()
        for c in cols:
            if c not in out.columns:
                continue
            for h in lag_hours:
                out[f"{c}_lag_{h}h"] = out[c].shift(h)
        return out

    def create_rolling_statistics(self, df: pd.DataFrame, windows: Optional[List[int]] = None, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Create rolling mean and std dev features for specified windows.

        Args:
            df: DataFrame with DateTimeIndex.
            windows: List of integer window sizes (in hours). Defaults to [3,6].
            columns: Columns to compute rolling stats for; if None, infer target columns.

        Returns:
            DataFrame with rolling mean/std columns appended.
        """
        if windows is None:
            windows = [3, 6]
        cols = columns or self._infer_target_cols(df)
        out = df.copy()
        for c in cols:
            if c not in out.columns:
                continue
            for w in windows:
                out[f"{c}_mean_{w}h"] = out[c].rolling(window=w, min_periods=1).mean()
                out[f"{c}_std_{w}h"] = out[c].rolling(window=w, min_periods=1).std().fillna(0.0)
        return out

    def preprocess(
        self,
        filepath: str,
        datetime_format: Optional[str] = None,
        missing_method: str = "forward_fill",
        missing_rolling_window: int = 3,
        outlier_iqr_multiplier: float = 1.5,
        lag_hours: Optional[List[int]] = None,
        rolling_windows: Optional[List[int]] = None,
        dropna: bool = True,
    ) -> pd.DataFrame:
        """Run the full preprocessing pipeline and return a clean DataFrame.

        Args:
            filepath: Path to the input CSV file.
            datetime_format: Optional datetime format for faster parsing.
            missing_method: Missing value strategy: `forward_fill`, `rolling_mean`, or `both`.
            missing_rolling_window: Window used when `rolling_mean` is selected.
            outlier_iqr_multiplier: IQR multiplier for outlier detection.
            lag_hours: List of lag hours to create (defaults to [1,3,6]).
            rolling_windows: Rolling windows (defaults to [3,6]).
            dropna: If True, drop rows with any NaN after processing.

        Returns:
            Processed pandas DataFrame ready for modeling.
        """
        df = self.load_csv(filepath)
        df = self.parse_datetime(df, datetime_format=datetime_format)

        # determine target columns early
        targets = self._infer_target_cols(df)

        # handle missing values
        df = self.handle_missing_values(df, method=missing_method, rolling_window=missing_rolling_window)

        # remove outliers
        df, outlier_stats = self.remove_outliers(df, columns=targets, iqr_multiplier=outlier_iqr_multiplier)
        self._stats["outlier_stats"] = outlier_stats

        # create lag features
        df = self.create_lag_features(df, lag_hours=lag_hours, columns=targets)

        # create rolling statistics
        df = self.create_rolling_statistics(df, windows=rolling_windows, columns=targets)

        if dropna:
            df = df.dropna(how="any")

        return df

    def get_stats(self) -> Dict[str, object]:
        """Return collected preprocessing statistics (outliers, etc.)."""
        return dict(self._stats)


def load_and_preprocess(filepath: str, **kwargs) -> pd.DataFrame:
    """Convenience function: create a `DataPreprocessor` and run `preprocess`.

    Args:
        filepath: CSV path.
        **kwargs: Forwarded to `DataPreprocessor.preprocess`.

    Returns:
        Cleaned DataFrame.
    """
    pre = DataPreprocessor()
    return pre.preprocess(filepath, **kwargs)
