"""
Tests for Real-time AQI API endpoints
"""

import pytest
import json
from app import create_app
from app.config import TestingConfig


@pytest.fixture
def app():
    """Create test application."""
    app = create_app(TestingConfig)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestRealtimeAQIEndpoints:
    """Test real-time AQI API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/v1/realtime-aqi/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert 'service' in data
        assert data['service'] == 'Real-time AQI'

    def test_single_city_delhi(self, client):
        """Test fetching AQI for Delhi."""
        response = client.get('/api/v1/realtime-aqi/city/Delhi')
        
        assert response.status_code in [200, 404]
        data = response.get_json()
        assert 'status' in data

        if response.status_code == 200:
            assert data['status'] == 'success'
            assert 'data' in data
            aqi_data = data['data']
            
            # Verify response structure
            assert 'aqi' in aqi_data
            assert 'city' in aqi_data
            assert 'category' in aqi_data
            assert 'pollutants' in aqi_data
            assert 'timestamp' in aqi_data
            
            # Verify pollutants
            pollutants = aqi_data['pollutants']
            assert isinstance(pollutants, dict)
            assert any(p is not None for p in pollutants.values())

    def test_single_city_mumbai(self, client):
        """Test fetching AQI for Mumbai."""
        response = client.get('/api/v1/realtime-aqi/city/Mumbai')
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert data['status'] == 'success'
            assert data['data']['city'] == 'Mumbai'

    def test_single_city_bangalore(self, client):
        """Test fetching AQI for Bangalore."""
        response = client.get('/api/v1/realtime-aqi/city/Bangalore')
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert data['status'] == 'success'

    def test_empty_city_name(self, client):
        """Test with empty city name."""
        response = client.get('/api/v1/realtime-aqi/city/')
        
        # Should return 404 since path is empty
        assert response.status_code in [404, 405]

    def test_coordinates_valid(self, client):
        """Test fetching AQI by valid coordinates (Delhi)."""
        # Delhi coordinates
        response = client.get('/api/v1/realtime-aqi/coordinates?latitude=28.7041&longitude=77.1025')
        
        assert response.status_code in [200, 404]
        data = response.get_json()
        
        if response.status_code == 200:
            assert data['status'] == 'success'
            assert 'data' in data
            aqi_data = data['data']
            assert 'aqi' in aqi_data
            assert 'latitude' in aqi_data
            assert 'longitude' in aqi_data

    def test_coordinates_missing_latitude(self, client):
        """Test coordinates endpoint without latitude."""
        response = client.get('/api/v1/realtime-aqi/coordinates?longitude=77.1025')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_coordinates_missing_longitude(self, client):
        """Test coordinates endpoint without longitude."""
        response = client.get('/api/v1/realtime-aqi/coordinates?latitude=28.7041')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_coordinates_invalid_values(self, client):
        """Test coordinates with invalid values."""
        response = client.get('/api/v1/realtime-aqi/coordinates?latitude=invalid&longitude=invalid')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_multiple_cities_valid(self, client):
        """Test fetching AQI for multiple cities."""
        payload = {
            'cities': ['Delhi', 'Mumbai', 'Bangalore']
        }
        
        response = client.post(
            '/api/v1/realtime-aqi/multiple-cities',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'timestamp' in data
        
        # Verify response contains requested cities
        cities_data = data['data']
        assert 'Delhi' in cities_data or len(cities_data) > 0

    def test_multiple_cities_empty_list(self, client):
        """Test with empty cities list."""
        payload = {'cities': []}
        
        response = client.post(
            '/api/v1/realtime-aqi/multiple-cities',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_multiple_cities_missing_cities_field(self, client):
        """Test with missing cities field."""
        payload = {}
        
        response = client.post(
            '/api/v1/realtime-aqi/multiple-cities',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_multiple_cities_exceeds_limit(self, client):
        """Test exceeding maximum cities limit (50)."""
        payload = {
            'cities': [f'City{i}' for i in range(51)]
        }
        
        response = client.post(
            '/api/v1/realtime-aqi/multiple-cities',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_popular_cities(self, client):
        """Test fetching AQI for popular cities."""
        response = client.get('/api/v1/realtime-aqi/popular-cities')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'timestamp' in data
        
        # Should have data for popular cities
        cities_data = data['data']
        assert isinstance(cities_data, dict)
        
        # At least some cities should be in the response
        assert len(cities_data) > 0

    def test_response_structure(self, client):
        """Test that response has consistent structure."""
        response = client.get('/api/v1/realtime-aqi/popular-cities')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check top-level structure
        assert 'status' in data
        assert 'data' in data
        assert 'timestamp' in data
        
        # Check data structure
        for city_name, aqi_data in data['data'].items():
            if aqi_data:  # Skip null entries
                assert 'aqi' in aqi_data
                assert 'city' in aqi_data
                assert 'category' in aqi_data
                assert 'pollutants' in aqi_data

    def test_aqi_categories(self, client):
        """Test that AQI categories are correctly assigned."""
        response = client.get('/api/v1/realtime-aqi/popular-cities')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Valid categories
        valid_categories = [
            'Good',
            'Moderate',
            'Unhealthy for Sensitive Groups',
            'Unhealthy',
            'Very Unhealthy',
            'Hazardous'
        ]
        
        for city_name, aqi_data in data['data'].items():
            if aqi_data and aqi_data.get('aqi') is not None:
                category = aqi_data.get('category')
                assert category in valid_categories, f"Invalid category: {category}"


class TestRealtimeAQIIntegration:
    """Integration tests for real-time AQI service."""

    def test_full_workflow(self, client):
        """Test complete workflow: health, single city, coordinates, multiple cities, popular."""
        
        # Step 1: Health check
        health_response = client.get('/api/v1/realtime-aqi/health')
        assert health_response.status_code == 200
        
        # Step 2: Single city
        city_response = client.get('/api/v1/realtime-aqi/city/Delhi')
        assert city_response.status_code in [200, 404, 500]
        
        # Step 3: Coordinates
        coords_response = client.get('/api/v1/realtime-aqi/coordinates?latitude=28.7041&longitude=77.1025')
        assert coords_response.status_code in [200, 404, 500]
        
        # Step 4: Multiple cities
        multi_response = client.post(
            '/api/v1/realtime-aqi/multiple-cities',
            data=json.dumps({'cities': ['Delhi', 'Mumbai']}),
            content_type='application/json'
        )
        assert multi_response.status_code == 200
        
        # Step 5: Popular cities
        popular_response = client.get('/api/v1/realtime-aqi/popular-cities')
        assert popular_response.status_code == 200

    def test_response_consistency(self, client):
        """Test that different endpoints return consistent data structure."""
        
        # Get data from multiple sources
        delhi_response = client.get('/api/v1/realtime-aqi/city/Delhi')
        popular_response = client.get('/api/v1/realtime-aqi/popular-cities')
        
        if delhi_response.status_code == 200 and popular_response.status_code == 200:
            delhi_data = delhi_response.get_json()['data']
            popular_data = popular_response.get_json()['data'].get('Delhi')
            
            if delhi_data and popular_data:
                # Both should have same structure
                assert 'aqi' in delhi_data
                assert 'aqi' in popular_data
                assert 'category' in delhi_data
                assert 'category' in popular_data


class TestRealtimeAQIErrors:
    """Test error handling."""

    def test_invalid_city_name(self, client):
        """Test with invalid city name."""
        response = client.get('/api/v1/realtime-aqi/city/NonexistentCity12345')
        
        assert response.status_code in [404, 500]
        data = response.get_json()
        assert 'status' in data

    def test_malformed_json(self, client):
        """Test with malformed JSON in POST request."""
        response = client.post(
            '/api/v1/realtime-aqi/multiple-cities',
            data='{invalid json}',
            content_type='application/json'
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 500]
