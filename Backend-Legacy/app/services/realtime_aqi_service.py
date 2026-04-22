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
        """Initialize the service with API credentials and cache."""
        self.api_key = os.getenv('REALTIME_WAQI_API_KEY') or os.getenv('REALTIME_AQI_API_KEY')
        self.base_url = os.getenv('REALTIME_WAQI_BASE_URL') or os.getenv('REALTIME_AQI_BASE_URL', 'https://api.waqi.info')
        self.timeout = 10  # seconds
        
        # Simple In-Memory Cache: {key: (timestamp, data)}
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes in seconds

        if not self.api_key:
            logger.warning("REALTIME_AQI_API_KEY not configured in environment")

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Retrieve a valid item from cache if exists."""
        import time
        if key in self._cache:
            timestamp, data = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return data
        return None

    def _set_to_cache(self, key: str, data: Any):
        """Store item in cache with current timestamp."""
        import time
        if data:
            self._cache[key] = (time.time(), data)

    def get_city_aqi(self, city: str) -> Optional[Dict[str, Any]]:
        """Fetch AQI for a city with caching."""
        cache_key = f"city:{city}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        if not self.api_key:
            return self._get_mock_data(city)

        try:
            url = f"{self.base_url}/feed/{city}/"
            params = {"token": self.api_key}
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'ok':
                return self._get_mock_data(city)

            result = self._parse_aqi_data(data.get('data', {}))
            self._set_to_cache(cache_key, result)
            return result

        except requests.RequestException as e:
            # Don't log the full URL which might contain API key
            logger.error(f"Failed to fetch AQI for {city}: {type(e).__name__}")
            return self._get_mock_data(city)
        except Exception as e:
            logger.error(f"Unexpected error fetching AQI for {city}: {type(e).__name__}")
            return self._get_mock_data(city)

    def get_multiple_cities_aqi(self, cities: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Fetch real-time AQI data for multiple cities.
        """
        results = {}
        for city in cities:
            results[city] = self.get_city_aqi(city)
        return results

    def get_map_bounds_data(
        self, lat_min: float, lon_min: float, lat_max: float, lon_max: float
    ) -> List[Dict[str, Any]]:
        """Fetch AQI data for stations in bounds with caching."""
        cache_key = f"bounds:{lat_min},{lon_min},{lat_max},{lon_max}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        if not self.api_key:
            return []

        # If box is very large (e.g. whole of India), WAQI API returns very few stations.
        # We use a grid fetch to increase density.
        lat_span = lat_max - lat_min
        lon_span = lon_max - lon_min
        is_large_box = lat_span > 15 or lon_span > 15

        try:
            if is_large_box:
                logger.info(f"Large bounding box detected ({lat_span:.1f}x{lon_span:.1f}). Using 10x10 grid fetch.")
                
                lat_steps = 10
                lon_steps = 10
                lat_inc = lat_span / lat_steps
                lon_inc = lon_span / lon_steps
                
                all_stations = []
                for i in range(lat_steps):
                    for j in range(lon_steps):
                        q_lat_min = lat_min + i * lat_inc
                        q_lat_max = q_lat_min + lat_inc
                        q_lon_min = lon_min + j * lon_inc
                        q_lon_max = q_lon_min + lon_inc
                        
                        q_data = self._fetch_bounds_once(q_lat_min, q_lon_min, q_lat_max, q_lon_max)
                        all_stations.extend(q_data)
                
                # De-duplicate by UID
                seen_uids = set()
                result = []
                for s in all_stations:
                    uid = s.get("uid")
                    if uid and uid not in seen_uids:
                        seen_uids.add(uid)
                        result.append(s)
                
                logger.info(f"Grid fetch completed. Found {len(result)} unique stations.")
            else:
                result = self._fetch_bounds_once(lat_min, lon_min, lat_max, lon_max)

            self._set_to_cache(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"Failed to fetch map bounds data: {str(e)}")
            return []

    def _fetch_bounds_once(self, lat_min: float, lon_min: float, lat_max: float, lon_max: float) -> List[Dict[str, Any]]:
        """Single API call for bounding box."""
        try:
            url = f"{self.base_url}/map/bounds/"
            params = {
                "token": self.api_key,
                "latlng": f"{lat_min},{lon_min},{lat_max},{lon_max}"
            }
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'ok':
                return []

            stations = data.get('data', [])
            result = []
            for s in stations:
                aqi_val = s.get("aqi")
                if aqi_val == "-" or aqi_val is None:
                    continue
                try:
                    result.append({
                        "lat": float(s.get("lat")),
                        "lon": float(s.get("lon")),
                        "aqi": int(aqi_val),
                        "station": s.get("station", {}).get("name", "Unknown Station"),
                        "uid": s.get("uid")
                    })
                except (ValueError, TypeError):
                    continue
            return result
        except Exception as e:
            logger.error(f"Error in _fetch_bounds_once: {str(e)}")
            return []

    def get_supplemented_nationwide_data(self) -> List[Dict[str, Any]]:
        """
        Fetch nationwide data and supplement with major city data.
        """
        # India Bounding Box (approximate)
        lat_min, lon_min, lat_max, lon_max = 6.5, 68.7, 37.1, 97.25
        grid_stations = self.get_map_bounds_data(lat_min, lon_min, lat_max, lon_max)
        
        seen_uids = set(s.get("uid") for s in grid_stations if s.get("uid"))
        result = list(grid_stations)
        
        logger.info(f"Supplementing {len(grid_stations)} stations with popular cities...")
        
        for city in POPULAR_INDIAN_CITIES:
            try:
                data = self.get_city_aqi(city)
                if data and data.get('aqi') is not None:
                    uid = data.get('uid') or f"city-{city.lower()}"
                    if uid not in seen_uids:
                        seen_uids.add(uid)
                        result.append({
                            "lat": data.get("latitude"),
                            "lon": data.get("longitude"),
                            "aqi": data.get("aqi"),
                            "station": data.get("city", city),
                            "uid": uid
                        })
            except Exception as e:
                logger.warning(f"Supplementation failed for {city}: {e}")
                
        logger.info(f"Final supplemented count: {len(result)} stations.")
        return result

    def get_city_by_coordinates(
        self, latitude: float, longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Fetch AQI for coordinates with caching."""
        cache_key = f"geo:{latitude},{longitude}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        if not self.api_key:
             return self._get_mock_data(f"Loc ({latitude:.2f}, {longitude:.2f})")

        try:
            url = f"{self.base_url}/feed/geo:{latitude};{longitude}/"
            params = {"token": self.api_key}
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'ok':
                return self._get_mock_data(f"Loc ({latitude:.2f}, {longitude:.2f})")

            result = self._parse_aqi_data(data.get('data', {}))
            self._set_to_cache(cache_key, result)
            return result

        except requests.RequestException as e:
            logger.error(f"Failed to fetch AQI for coordinates: {type(e).__name__}")
            return self._get_mock_data(f"Loc ({latitude:.2f}, {longitude:.2f})")
        except Exception as e:
            logger.error(f"Unexpected error for coordinates: {type(e).__name__}")
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
                'dominant': data.get('dominentpol', 'PM2.5'),
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



# Popular Indian cities for comprehensive nationwide coverage
POPULAR_INDIAN_CITIES = [
    "Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", 
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow", 
    "Chandigarh", "Indore", "Surat", "Visakhapatnam", "Nagpur",
    "Patna", "Bhopal", "Ludhiana", "Agra", "Nashik",
    "Vadodara", "Faridabad", "Thane", "Meerut", "Rajkot",
    "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar",
    "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior",
    "Vijayawada", "Madurai", "Guwahati", "Shimla", "Dehradun",
    "Panaji", "Shillong", "Raipur", "Bhubaneswar", "Kanpur"
]
