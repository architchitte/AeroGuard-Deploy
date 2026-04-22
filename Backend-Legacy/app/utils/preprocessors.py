"""
Data Preprocessors

Data preprocessing utilities for feature engineering.
"""

import numpy as np
from typing import Optional, Tuple


class DataPreprocessor:
    """Data preprocessing for model inputs."""

    @staticmethod
    def prepare_features(
        historical_data: np.ndarray, forecast_days: int
    ) -> np.ndarray:
        """
        Prepare features for forecasting.

        Args:
            historical_data: Historical air quality data
            forecast_days: Number of days to forecast

        Returns:
            Feature matrix ready for model prediction
        """
        if len(historical_data) == 0:
            raise ValueError("Historical data cannot be empty")

        # Extract features: rolling means, std, trends
        features = []

        # Mean of last 7 days
        if len(historical_data) >= 7:
            features.append(np.mean(historical_data[-7:], axis=0))

        # Mean of all available data
        features.append(np.mean(historical_data, axis=0))

        # Standard deviation
        features.append(np.std(historical_data, axis=0))

        # Trend (last value - mean)
        features.append(historical_data[-1] - np.mean(historical_data, axis=0))

        # Rolling volatility (last 7 days std)
        if len(historical_data) >= 7:
            features.append(np.std(historical_data[-7:], axis=0))

        # Combine and expand for forecast horizon
        feature_matrix = np.vstack(features)

        # Repeat for each forecast day
        forecast_features = np.tile(
            feature_matrix, (min(forecast_days, 7), 1)
        )

        return forecast_features

    @staticmethod
    def normalize_features(
        X: np.ndarray, mean: Optional[np.ndarray] = None, 
        std: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Normalize features using z-score normalization.

        Args:
            X: Feature matrix
            mean: Pre-computed mean (for inference)
            std: Pre-computed std (for inference)

        Returns:
            Tuple of (normalized_X, mean, std)
        """
        if mean is None:
            mean = np.mean(X, axis=0)
        if std is None:
            std = np.std(X, axis=0)

        # Avoid division by zero
        std = np.where(std == 0, 1, std)

        X_normalized = (X - mean) / std

        return X_normalized, mean, std

    @staticmethod
    def remove_outliers(
        X: np.ndarray, threshold: float = 3.0
    ) -> np.ndarray:
        """
        Remove outliers using z-score method.

        Args:
            X: Input data
            threshold: Z-score threshold for outlier detection

        Returns:
            Data with outliers removed
        """
        z_scores = np.abs((X - np.mean(X, axis=0)) / (np.std(X, axis=0) + 1e-8))
        mask = np.all(z_scores < threshold, axis=1)
        return X[mask]

    @staticmethod
    def handle_missing_values(
        X: np.ndarray, method: str = "mean"
    ) -> np.ndarray:
        """
        Handle missing values in data.

        Args:
            X: Input data
            method: Method to handle missing values ('mean', 'forward_fill', 'drop')

        Returns:
            Data with missing values handled
        """
        if method == "mean":
            col_means = np.nanmean(X, axis=0)
            mask = np.isnan(X)
            X[mask] = np.repeat(col_means, mask.sum(axis=0))[
                np.repeat(np.arange(mask.shape[1]), mask.sum(axis=0))
            ]
        elif method == "forward_fill":
            for i in range(X.shape[1]):
                mask = np.isnan(X[:, i])
                idx = np.where(~mask, np.arange(mask.size), 0)
                np.maximum.accumulate(idx, axis=0, out=idx)
                X[mask, i] = X[idx[mask], i]
        elif method == "drop":
            X = X[~np.any(np.isnan(X), axis=1)]

        return X

    @staticmethod
    def scale_to_range(
        X: np.ndarray, feature_range: Tuple[float, float] = (0, 1)
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Scale features to specified range.

        Args:
            X: Input data
            feature_range: Target range (min, max)

        Returns:
            Tuple of (scaled_X, min_vals, max_vals)
        """
        min_vals = np.min(X, axis=0)
        max_vals = np.max(X, axis=0)

        # Avoid division by zero
        range_vals = max_vals - min_vals
        range_vals = np.where(range_vals == 0, 1, range_vals)

        X_scaled = (X - min_vals) / range_vals
        X_scaled = X_scaled * (feature_range[1] - feature_range[0]) + feature_range[0]

        return X_scaled, min_vals, max_vals
