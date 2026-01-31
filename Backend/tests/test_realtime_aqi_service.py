"""
Unit tests for Real-time AQI Service with mocked API responses
"""

import pytest
import os
from unittest.mock import Mock, patch
from app.services.realtime_aqi_service import RealtimeAQIService


@pytest.fixture(autouse=True)
def setup_env():
    """Setup environment variables for testing."""
    os.environ['REALTIME_AQI_API_KEY'] = 'test-api-key-12345'
    os.environ['REALTIME_AQI_BASE_URL'] = 'https://api.waqi.info/v2'
    yield
    # Cleanup not needed as module reloads with new env


@pytest.fixture
def service():
    """Create a service instance for testing."""
    # Create a fresh instance with mocked environment
    with patch.dict(os.environ, {
        'REALTIME_AQI_API_KEY': 'test-api-key-12345',
        'REALTIME_AQI_BASE_URL': 'https://api.waqi.info/v2'
    }):
        return RealtimeAQIService()


class TestRealtimeAQIServiceLogic:
    """Test the business logic of RealtimeAQIService."""

    def test_service_initialization(self, service):
        """Test service initializes with correct configuration."""
        assert service.api_key is not None
        assert 'waqi.info' in service.base_url

    def test_aqi_category_good(self, service):
        """Test AQI category mapping for Good range (0-50)."""
        assert service.get_aqi_category(25) == 'Good'
        assert service.get_aqi_category(0) == 'Good'
        assert service.get_aqi_category(50) == 'Good'

    def test_aqi_category_moderate(self, service):
        """Test AQI category mapping for Moderate range (51-100)."""
        assert service.get_aqi_category(51) == 'Moderate'
        assert service.get_aqi_category(75) == 'Moderate'
        assert service.get_aqi_category(100) == 'Moderate'

    def test_aqi_category_unhealthy_sensitive(self, service):
        """Test AQI category mapping for Unhealthy for Sensitive Groups (101-150)."""
        assert service.get_aqi_category(101) == 'Unhealthy for Sensitive Groups'
        assert service.get_aqi_category(125) == 'Unhealthy for Sensitive Groups'
        assert service.get_aqi_category(150) == 'Unhealthy for Sensitive Groups'

    def test_aqi_category_unhealthy(self, service):
        """Test AQI category mapping for Unhealthy (151-200)."""
        assert service.get_aqi_category(151) == 'Unhealthy'
        assert service.get_aqi_category(175) == 'Unhealthy'
        assert service.get_aqi_category(200) == 'Unhealthy'

    def test_aqi_category_very_unhealthy(self, service):
        """Test AQI category mapping for Very Unhealthy (201-300)."""
        assert service.get_aqi_category(201) == 'Very Unhealthy'
        assert service.get_aqi_category(250) == 'Very Unhealthy'
        assert service.get_aqi_category(300) == 'Very Unhealthy'

    def test_aqi_category_hazardous(self, service):
        """Test AQI category mapping for Hazardous (>300)."""
        assert service.get_aqi_category(301) == 'Hazardous'
        assert service.get_aqi_category(500) == 'Hazardous'
        assert service.get_aqi_category(1000) == 'Hazardous'

    @patch('app.services.realtime_aqi_service.requests.get')
    def test_parse_valid_aqi_response(self, mock_get, service):
        """Test parsing valid WAQI API response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'ok',
            'data': {
                'aqi': 85,
                'city': {'name': 'Delhi, India', 'geo': [28.7041, 77.1025]},
                'iaqi': {
                    'pm25': {'v': 65},
                    'pm10': {'v': 120},
                    'no2': {'v': 35},
                    'o3': {'v': 45},
                    'so2': {'v': 25},
                    'co': {'v': 550}
                }
            }
        }
        mock_get.return_value = mock_response

        result = service.get_city_aqi('Delhi')

        assert result is not None
        assert result['aqi'] == 85
        assert result['city'] == 'Delhi'
        assert result['category'] == 'Moderate'
        assert result['latitude'] == 28.7041
        assert result['longitude'] == 77.1025
        assert 'pm25' in result['pollutants']

    @patch('app.services.realtime_aqi_service.requests.get')
    def test_parse_minimal_response(self, mock_get, service):
        """Test parsing minimal WAQI API response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'ok',
            'data': {
                'aqi': 150,
                'city': {'name': 'Mumbai, India', 'geo': [19.0760, 72.8777]},
                'iaqi': {}  # No pollutant details
            }
        }
        mock_get.return_value = mock_response

        result = service.get_city_aqi('Mumbai')

        assert result is not None
        assert result['aqi'] == 150
        assert result['city'] == 'Mumbai'
        assert result['category'] == 'Unhealthy for Sensitive Groups'

    @patch('app.services.realtime_aqi_service.requests.get')
    def test_get_city_aqi_failure(self, mock_get, service):
        """Test handling of API failure."""
        mock_get.side_effect = Exception("Connection error")

        result = service.get_city_aqi('Delhi')

        assert result is None

    @patch('app.services.realtime_aqi_service.requests.get')
    def test_get_multiple_cities(self, mock_get, service):
        """Test fetching multiple cities."""
        def mock_response_side_effect(url, timeout):
            mock = Mock()
            if 'Delhi' in url:
                mock.json.return_value = {
                    'status': 'ok',
                    'data': {
                        'aqi': 85,
                        'city': {'name': 'Delhi', 'geo': [28.7, 77.1]},
                        'iaqi': {'pm25': {'v': 65}}
                    }
                }
            elif 'Mumbai' in url:
                mock.json.return_value = {
                    'status': 'ok',
                    'data': {
                        'aqi': 95,
                        'city': {'name': 'Mumbai', 'geo': [19.0, 72.8]},
                        'iaqi': {'pm25': {'v': 75}}
                    }
                }
            else:
                mock.json.return_value = {'status': 'error'}
            return mock

        mock_get.side_effect = mock_response_side_effect

        result = service.get_multiple_cities_aqi(['Delhi', 'Mumbai', 'Invalid'])

        assert len(result) > 0
        assert 'Delhi' in result
        assert 'Mumbai' in result

    @patch('app.services.realtime_aqi_service.requests.get')
    def test_get_city_by_coordinates(self, mock_get, service):
        """Test fetching AQI by coordinates."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'ok',
            'data': {
                'aqi': 85,
                'city': {'name': 'New Delhi', 'geo': [28.7041, 77.1025]},
                'iaqi': {'pm25': {'v': 65}}
            }
        }
        mock_get.return_value = mock_response

        result = service.get_city_by_coordinates(28.7041, 77.1025)

        assert result is not None
        assert result['aqi'] == 85

    def test_popular_cities_list(self, service):
        """Test that popular cities list is properly defined."""
        assert len(service.POPULAR_CITIES) > 0
        assert 'Delhi' in service.POPULAR_CITIES
        assert 'Mumbai' in service.POPULAR_CITIES
        assert 'Bangalore' in service.POPULAR_CITIES

    def test_popular_cities_contains_major_indian_cities(self, service):
        """Test that popular cities include major Indian metropolitan areas."""
        major_cities = {
            'Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Chennai',
            'Kolkata', 'Pune', 'Ahmedabad'
        }
        for city in major_cities:
            assert city in service.POPULAR_CITIES


class TestRealtimeAQIDataValidation:
    """Test data validation and structure."""

    @patch('app.services.realtime_aqi_service.requests.get')
    def test_response_has_required_fields(self, mock_get):
        """Test that parsed response contains all required fields."""
        service = RealtimeAQIService()
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'ok',
            'data': {
                'aqi': 85,
                'city': {'name': 'Delhi', 'geo': [28.7, 77.1]},
                'iaqi': {'pm25': {'v': 65}}
            }
        }
        mock_get.return_value = mock_response

        result = service.get_city_aqi('Delhi')

        required_fields = ['aqi', 'city', 'category', 'latitude', 'longitude', 
                          'pollutants', 'timestamp']
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    @patch('app.services.realtime_aqi_service.requests.get')
    def test_aqi_value_is_numeric(self, mock_get):
        """Test that AQI value is always numeric."""
        service = RealtimeAQIService()
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'ok',
            'data': {
                'aqi': 85,
                'city': {'name': 'Delhi', 'geo': [28.7, 77.1]},
                'iaqi': {}
            }
        }
        mock_get.return_value = mock_response

        result = service.get_city_aqi('Delhi')

        assert isinstance(result['aqi'], (int, float))
        assert result['aqi'] >= 0

    @patch('app.services.realtime_aqi_service.requests.get')
    def test_coordinates_are_valid_floats(self, mock_get):
        """Test that latitude and longitude are valid floats."""
        service = RealtimeAQIService()
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'ok',
            'data': {
                'aqi': 85,
                'city': {'name': 'Delhi', 'geo': [28.7041, 77.1025]},
                'iaqi': {}
            }
        }
        mock_get.return_value = mock_response

        result = service.get_city_aqi('Delhi')

        assert isinstance(result['latitude'], (int, float))
        assert isinstance(result['longitude'], (int, float))
        assert -90 <= result['latitude'] <= 90
        assert -180 <= result['longitude'] <= 180
