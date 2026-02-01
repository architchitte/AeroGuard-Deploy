"""
Real-time AQI Service

Fetches real-time air quality data from WAQI (World Air Quality Index)
API for multiple locations in India.
"""

import logging
import os
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RealtimeAQIService:
    """Service for fetching real-time AQI data from WAQI API."""

    def __init__(self):
        """Initialize the service with API credentials."""
        self.api_key = os.getenv('REALTIME_AQI_API_KEY')
        self.base_url = os.getenv('REALTIME_AQI_BASE_URL', 'https://api.waqi.info')
        self.timeout = 10  # seconds

        if not self.api_key:
            logger.warning("REALTIME_AQI_API_KEY not configured in environment")

    def get_city_aqi(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch real-time AQI data for a specific city.
        Falls back to Mock Data if API fails or is unconfigured.
        """
        if not self.api_key:
            logger.warning("API key not configured, returning MOCK data.")
            return self._get_mock_data(city)

        try:
            url = f"{self.base_url}/feed/{city}/?token={self.api_key}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'ok':
                logger.warning(f"API returned non-ok status for {city}: {data.get('data')}")
                return self._get_mock_data(city)

            return self._parse_aqi_data(data.get('data', {}))

        except Exception as e:
            logger.error(f"Failed to fetch AQI for {city}: {e}")
            return self._get_mock_data(city)

    def get_multiple_cities_aqi(self, cities: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Fetch real-time AQI data for multiple cities.
        """
        results = {}
        for city in cities:
            results[city] = self.get_city_aqi(city)
        return results

    def get_city_by_coordinates(
        self, latitude: float, longitude: float
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch AQI data for a specific location by coordinates.
        """
        if not self.api_key:
             return self._get_mock_data(f"Loc ({latitude:.2f}, {longitude:.2f})")

        try:
            url = f"{self.base_url}/feed/geo:{latitude};{longitude}/?token={self.api_key}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'ok':
                return self._get_mock_data(f"Loc ({latitude:.2f}, {longitude:.2f})")

            return self._parse_aqi_data(data.get('data', {}))

        except Exception as e:
            logger.error(f"Failed to fetch AQI for coords: {e}")
            return self._get_mock_data(f"Loc ({latitude:.2f}, {longitude:.2f})")

    def _get_mock_data(self, city_name: str) -> Dict[str, Any]:
        """Generate realistic mock data when API is unavailable."""
        import random
        
        # Deterministic random based on city name to keep it consistent-ish
        random.seed(city_name)
        
        base_aqi = random.randint(50, 300)
        
        return {
            'city': city_name,
            'aqi': base_aqi,
            'latitude': 28.61 if 'Delhi' in city_name else 19.07, 
            'longitude': 77.20 if 'Delhi' in city_name else 72.87,
            'pollutants': {
                'pm25': round(base_aqi * 0.6, 1),
                'pm10': round(base_aqi * 0.8, 1),
                'no2': random.randint(10, 80),
                'o3': random.randint(10, 60),
                'so2': random.randint(5, 30),
                'co': round(random.uniform(0.5, 2.0), 2),
            },
            'url': 'https://aeroguard.demo',
            'last_updated': datetime.now().isoformat(),
            'source': 'AeroGuard Simulation Engine',
            'is_mock': True
        }

    @staticmethod
    def _parse_aqi_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and structure WAQI API response data.

        Args:
            data: Raw data from WAQI API

        Returns:
            Structured AQI data dictionary
        """
        try:
            # Extract main AQI value
            aqi_value = data.get('aqi')

            # Extract pollutant details
            iaqi = data.get('iaqi', {})
            pollutants = {
                'pm25': iaqi.get('pm25', {}).get('v'),
                'pm10': iaqi.get('pm10', {}).get('v'),
                'no2': iaqi.get('no2', {}).get('v'),
                'o3': iaqi.get('o3', {}).get('v'),
                'so2': iaqi.get('so2', {}).get('v'),
                'co': iaqi.get('co', {}).get('v'),
            }


            # Extract location and time information
            location = data.get('city', {})
            city_name = location.get('name', 'Unknown')
            geo = location.get('geo', [None, None])

            return {
                'city': city_name,
                'aqi': aqi_value,
                'latitude': geo[0],
                'longitude': geo[1],
                'pollutants': pollutants,
                'url': data.get('attribution', [{}])[0].get('url'),
                'last_updated': data.get('time', {}).get('iso', datetime.now().isoformat()),
                'source': data.get('attribution', [{}])[0].get('name', 'Unknown'),
            }

        except Exception as e:
            logger.error(f"Error parsing AQI data: {str(e)}")
            return {}

    def get_aqi_category(self, aqi_value: Optional[float]) -> str:
        """
        Get the AQI category based on AQI value.

        Args:
            aqi_value: Numerical AQI value

        Returns:
            Category string (Good, Moderate, Unhealthy, etc.)
        """
        if aqi_value is None:
            return "Unknown"

        if aqi_value <= 50:
            return "Good"
        elif aqi_value <= 100:
            return "Moderate"
        elif aqi_value <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi_value <= 200:
            return "Unhealthy"
        elif aqi_value <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"


# Popular Indian cities for quick access
POPULAR_INDIAN_CITIES = [
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Pune",
    "Ahmedabad",
    "Jaipur",
    "Lucknow",
    "Chandigarh",
    "Indore",
    "Surat",
    "Visakhapatnam",
    "Nagpur",
]
