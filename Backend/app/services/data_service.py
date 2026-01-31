"""
Data Service

Service for data retrieval and management.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class DataService:
    """
    Service for managing air quality data operations.

    Handles data retrieval, storage, and preprocessing at service level.
    """

    def __init__(self):
        """Initialize the data service."""
        self.cache = {}

    def fetch_historical_data(
        self, location_id: str, days: int = 30
    ) -> Optional[np.ndarray]:
        """
        Fetch historical air quality data for a location.

        Args:
            location_id: Location identifier
            days: Number of historical days to fetch

        Returns:
            Historical data as numpy array or None
        """
        # Check cache first
        cache_key = f"hist_{location_id}_{days}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # In production, this would query a database or external API
        data = self._generate_mock_data(days)
        self.cache[cache_key] = data

        return data

    def fetch_current_conditions(self, location_id: str) -> Dict:
        """
        Fetch current air quality conditions.

        Args:
            location_id: Location identifier

        Returns:
            Dictionary with current conditions
        """
        return {
            "location_id": location_id,
            "timestamp": datetime.now().isoformat(),
            "pm25": np.random.uniform(10, 100),
            "pm10": np.random.uniform(20, 150),
            "no2": np.random.uniform(5, 50),
            "o3": np.random.uniform(10, 80),
            "so2": np.random.uniform(0, 30),
            "co": np.random.uniform(0.1, 5),
        }

    def validate_location(self, location_id: str) -> Tuple[bool, str]:
        """
        Validate if location is valid.

        Args:
            location_id: Location identifier

        Returns:
            Tuple of (is_valid, message)
        """
        if not location_id or len(location_id) == 0:
            return False, "Location ID cannot be empty"

        if len(location_id) > 100:
            return False, "Location ID too long"

        if not location_id.replace("_", "").replace("-", "").isalnum():
            return False, "Location ID contains invalid characters"

        return True, "Valid location"

    def get_location_metadata(self, location_id: str) -> Dict:
        """
        Get metadata for a location.

        Args:
            location_id: Location identifier

        Returns:
            Dictionary with location metadata
        """
        return {
            "location_id": location_id,
            "name": f"Location {location_id}",
            "latitude": 19.0760 + np.random.uniform(-0.1, 0.1),
            "longitude": 72.8777 + np.random.uniform(-0.1, 0.1),
            "country": "India",
            "timezone": "UTC+5:30",
            "last_update": datetime.now().isoformat(),
        }

    def _generate_mock_data(self, days: int) -> np.ndarray:
        """
        Generate mock historical data.

        Args:
            days: Number of days of data

        Returns:
            Mock data as numpy array
        """
        np.random.seed(42)
        n_features = 10
        data = np.random.normal(loc=50, scale=20, size=(days, n_features))
        data = np.clip(data, 0, 500)
        return data

    def clear_cache(self, location_id: Optional[str] = None) -> bool:
        """
        Clear cached data.

        Args:
            location_id: Specific location to clear, or None for all

        Returns:
            True if successful
        """
        if location_id:
            keys_to_delete = [k for k in self.cache.keys() if location_id in k]
            for key in keys_to_delete:
                del self.cache[key]
        else:
            self.cache.clear()

        return True
