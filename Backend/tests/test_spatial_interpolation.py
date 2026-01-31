"""
Test suite for spatial interpolation service.

Tests cover:
- GeoPoint and Sensor validation
- IDW algorithm correctness
- Distance calculation accuracy
- Edge cases and boundary conditions
- Input validation and error handling
- Batch operations
- Different interpolation parameters
"""

import pytest
from app.services.spatial_interpolation import (
    GeoPoint,
    Sensor,
    InterpolationResult,
    IDWInterpolator,
    SpatialInterpolationService,
    create_spatial_interpolation_service,
)


class TestGeoPoint:
    """Test geographic point validation."""
    
    def test_valid_geopoint(self):
        """Test creating a valid geographic point."""
        point = GeoPoint(latitude=40.7128, longitude=-74.0060)
        assert point.latitude == 40.7128
        assert point.longitude == -74.0060
    
    def test_latitude_bounds(self):
        """Test latitude validation."""
        with pytest.raises(ValueError):
            GeoPoint(latitude=91.0, longitude=0.0)
        
        with pytest.raises(ValueError):
            GeoPoint(latitude=-91.0, longitude=0.0)
    
    def test_longitude_bounds(self):
        """Test longitude validation."""
        with pytest.raises(ValueError):
            GeoPoint(latitude=0.0, longitude=181.0)
        
        with pytest.raises(ValueError):
            GeoPoint(latitude=0.0, longitude=-181.0)
    
    def test_latitude_type_validation(self):
        """Test latitude type checking."""
        with pytest.raises(TypeError):
            GeoPoint(latitude="40.7128", longitude=0.0)
    
    def test_longitude_type_validation(self):
        """Test longitude type checking."""
        with pytest.raises(TypeError):
            GeoPoint(latitude=0.0, longitude="74.0")
    
    def test_edge_coordinates(self):
        """Test valid edge coordinates."""
        # Equator
        GeoPoint(latitude=0.0, longitude=0.0)
        # Prime meridian
        GeoPoint(latitude=0.0, longitude=0.0)
        # Extreme valid coordinates
        GeoPoint(latitude=90.0, longitude=180.0)
        GeoPoint(latitude=-90.0, longitude=-180.0)


class TestSensor:
    """Test sensor data validation."""
    
    def test_valid_sensor(self):
        """Test creating a valid sensor."""
        sensor = Sensor(
            latitude=40.7128,
            longitude=-74.0060,
            aqi_value=75.5,
            sensor_id="sensor_1"
        )
        assert sensor.aqi_value == 75.5
        assert sensor.sensor_id == "sensor_1"
    
    def test_negative_aqi(self):
        """Test that negative AQI is rejected."""
        with pytest.raises(ValueError):
            Sensor(latitude=0.0, longitude=0.0, aqi_value=-1.0)
    
    def test_aqi_type_validation(self):
        """Test AQI type checking."""
        with pytest.raises(TypeError):
            Sensor(latitude=0.0, longitude=0.0, aqi_value="75")
    
    def test_zero_aqi(self):
        """Test zero AQI is valid."""
        sensor = Sensor(latitude=0.0, longitude=0.0, aqi_value=0.0)
        assert sensor.aqi_value == 0.0
    
    def test_high_aqi(self):
        """Test high AQI values (hazardous)."""
        sensor = Sensor(latitude=0.0, longitude=0.0, aqi_value=500.0)
        assert sensor.aqi_value == 500.0
    
    def test_very_high_aqi_warning(self, caplog):
        """Test that extremely high AQI triggers warning."""
        sensor = Sensor(latitude=0.0, longitude=0.0, aqi_value=6000.0, sensor_id="test")
        assert "unusually high AQI" in caplog.text
    
    def test_sensor_inherits_geopoint_validation(self):
        """Test that Sensor validates geographic coordinates."""
        with pytest.raises(ValueError):
            Sensor(latitude=95.0, longitude=0.0, aqi_value=50.0)


class TestInterpolationResult:
    """Test interpolation result validation."""
    
    def test_valid_result(self):
        """Test creating a valid result."""
        result = InterpolationResult(
            estimated_aqi=75.0,
            confidence=0.95,
            sensors_used=3,
            nearest_sensor_distance_km=1.5,
            interpolation_method="IDW"
        )
        assert result.estimated_aqi == 75.0
        assert result.confidence == 0.95
    
    def test_confidence_bounds(self):
        """Test confidence must be 0-1."""
        with pytest.raises(ValueError):
            InterpolationResult(
                estimated_aqi=75.0,
                confidence=1.5,
                sensors_used=1,
                nearest_sensor_distance_km=1.0,
                interpolation_method="IDW"
            )
        
        with pytest.raises(ValueError):
            InterpolationResult(
                estimated_aqi=75.0,
                confidence=-0.1,
                sensors_used=1,
                nearest_sensor_distance_km=1.0,
                interpolation_method="IDW"
            )
    
    def test_sensors_used_minimum(self):
        """Test sensors_used must be at least 1."""
        with pytest.raises(ValueError):
            InterpolationResult(
                estimated_aqi=75.0,
                confidence=0.5,
                sensors_used=0,
                nearest_sensor_distance_km=1.0,
                interpolation_method="IDW"
            )
    
    def test_negative_aqi_result(self):
        """Test estimated AQI must be non-negative."""
        with pytest.raises(ValueError):
            InterpolationResult(
                estimated_aqi=-1.0,
                confidence=0.5,
                sensors_used=1,
                nearest_sensor_distance_km=1.0,
                interpolation_method="IDW"
            )


class TestHaversineDistance:
    """Test Haversine distance calculation."""
    
    def test_same_point(self):
        """Test distance between identical points is zero."""
        point = GeoPoint(latitude=40.7128, longitude=-74.0060)
        distance = IDWInterpolator.haversine_distance(point, point)
        assert distance < 0.001  # Less than 1 meter
    
    def test_known_distance_nyc_sf(self):
        """Test known distance: NYC to San Francisco."""
        nyc = GeoPoint(latitude=40.7128, longitude=-74.0060)
        sf = GeoPoint(latitude=37.7749, longitude=-122.4194)
        
        distance = IDWInterpolator.haversine_distance(nyc, sf)
        
        # NYC to SF is approximately 4130 km
        assert 4100 < distance < 4200
    
    def test_equator_distance(self):
        """Test distance along equator."""
        point1 = GeoPoint(latitude=0.0, longitude=0.0)
        point2 = GeoPoint(latitude=0.0, longitude=1.0)
        
        distance = IDWInterpolator.haversine_distance(point1, point2)
        
        # 1 degree at equator is approximately 111.32 km
        assert 110 < distance < 112
    
    def test_pole_convergence(self):
        """Test distance at poles (longitude converges)."""
        north_pole_1 = GeoPoint(latitude=90.0, longitude=0.0)
        north_pole_2 = GeoPoint(latitude=90.0, longitude=180.0)
        
        distance = IDWInterpolator.haversine_distance(north_pole_1, north_pole_2)
        
        # Distance should be very small (all points at pole converge)
        assert distance < 0.01
    
    def test_symmetry(self):
        """Test that distance is symmetric."""
        point1 = GeoPoint(latitude=40.7128, longitude=-74.0060)
        point2 = GeoPoint(latitude=51.5074, longitude=-0.1278)
        
        d1 = IDWInterpolator.haversine_distance(point1, point2)
        d2 = IDWInterpolator.haversine_distance(point2, point1)
        
        assert abs(d1 - d2) < 0.001


class TestIDWInterpolator:
    """Test IDW interpolation algorithm."""
    
    def test_init_valid_parameters(self):
        """Test creating interpolator with valid parameters."""
        interpolator = IDWInterpolator(power=2.0, min_sensors=1, max_sensors=10)
        assert interpolator.power == 2.0
        assert interpolator.min_sensors == 1
        assert interpolator.max_sensors == 10
    
    def test_init_invalid_power(self):
        """Test power parameter validation."""
        with pytest.raises(ValueError):
            IDWInterpolator(power=0.0)
        
        with pytest.raises(ValueError):
            IDWInterpolator(power=-1.0)
    
    def test_init_invalid_min_sensors(self):
        """Test min_sensors validation."""
        with pytest.raises(ValueError):
            IDWInterpolator(min_sensors=0)
    
    def test_init_invalid_max_sensors(self):
        """Test max_sensors vs min_sensors validation."""
        with pytest.raises(ValueError):
            IDWInterpolator(min_sensors=5, max_sensors=3)
    
    def test_init_invalid_max_distance(self):
        """Test max_distance validation."""
        with pytest.raises(ValueError):
            IDWInterpolator(max_distance_km=0.0)
        
        with pytest.raises(ValueError):
            IDWInterpolator(max_distance_km=-1.0)
    
    def test_single_sensor(self):
        """Test interpolation with single sensor."""
        sensor = Sensor(latitude=40.7128, longitude=-74.0060, aqi_value=75.0)
        target = GeoPoint(latitude=40.7128, longitude=-74.0060)
        
        interpolator = IDWInterpolator()
        result = interpolator.interpolate([sensor], target)
        
        assert result.estimated_aqi == 75.0
        assert result.confidence == 1.0
        assert result.sensors_used == 1
    
    def test_exact_sensor_location(self):
        """Test when target is at exact sensor location."""
        sensor = Sensor(latitude=40.7128, longitude=-74.0060, aqi_value=50.0)
        target = GeoPoint(latitude=40.7128, longitude=-74.0060)
        
        interpolator = IDWInterpolator()
        result = interpolator.interpolate([sensor], target)
        
        assert result.estimated_aqi == 50.0
        assert result.confidence == 1.0
    
    def test_two_sensors_equal_distance(self):
        """Test interpolation with two equidistant sensors."""
        sensor1 = Sensor(latitude=0.0, longitude=-0.1, aqi_value=40.0)
        sensor2 = Sensor(latitude=0.0, longitude=0.1, aqi_value=60.0)
        target = GeoPoint(latitude=0.0, longitude=0.0)  # Between both sensors
        
        interpolator = IDWInterpolator(power=2.0)
        result = interpolator.interpolate([sensor1, sensor2], target)
        
        # With equal distances, should average the values
        assert abs(result.estimated_aqi - 50.0) < 0.1
    
    def test_multiple_sensors(self):
        """Test interpolation with multiple sensors."""
        sensors = [
            Sensor(latitude=0.0, longitude=0.0, aqi_value=100.0),
            Sensor(latitude=0.0, longitude=1.0, aqi_value=80.0),
            Sensor(latitude=1.0, longitude=0.0, aqi_value=60.0),
        ]
        target = GeoPoint(latitude=0.5, longitude=0.5)
        
        interpolator = IDWInterpolator()
        result = interpolator.interpolate(sensors, target)
        
        # Result should be between min and max of sensor values
        assert 60.0 < result.estimated_aqi < 100.0
        assert result.sensors_used == 3
    
    def test_power_parameter_effect(self):
        """Test that power parameter affects weighting."""
        sensors = [
            Sensor(latitude=0.0, longitude=0.0, aqi_value=100.0),
            Sensor(latitude=0.0, longitude=1.0, aqi_value=50.0),
        ]
        target = GeoPoint(latitude=0.0, longitude=0.1)
        
        # Higher power should give more weight to close sensor
        result_p1 = IDWInterpolator(power=1.0).interpolate(sensors, target)
        result_p2 = IDWInterpolator(power=2.0).interpolate(sensors, target)
        result_p3 = IDWInterpolator(power=3.0).interpolate(sensors, target)
        
        # Closer sensor has value 100, farther has 50
        # With higher power, should be closer to 100
        assert result_p1.estimated_aqi < result_p2.estimated_aqi < result_p3.estimated_aqi
    
    def test_max_distance_filtering(self):
        """Test max distance parameter filters sensors."""
        sensor_close = Sensor(latitude=0.0, longitude=0.0, aqi_value=100.0)
        sensor_far = Sensor(latitude=0.0, longitude=10.0, aqi_value=50.0)  # Far sensor ~1111 km away
        target = GeoPoint(latitude=0.0, longitude=0.1)  # Close to first sensor
        
        # With max_distance limiting to ~500 km
        # Close sensor at ~11 km is within, far sensor at ~1111 km is outside
        interpolator = IDWInterpolator(max_distance_km=500.0)
        result = interpolator.interpolate([sensor_close, sensor_far], target)
        
        # Should use only close sensor
        assert result.sensors_used == 1
        assert result.estimated_aqi == 100.0
    
    def test_max_sensors_limiting(self):
        """Test max_sensors limits used sensors."""
        sensors = [
            Sensor(latitude=0.0, longitude=0.0, aqi_value=100.0),
            Sensor(latitude=0.0, longitude=0.1, aqi_value=80.0),
            Sensor(latitude=0.0, longitude=0.2, aqi_value=60.0),
        ]
        target = GeoPoint(latitude=0.0, longitude=0.05)
        
        # Limit to using only 1 sensor (closest one)
        interpolator = IDWInterpolator(max_sensors=1)
        result = interpolator.interpolate(sensors, target)
        
        assert result.sensors_used == 1
    
    def test_insufficient_sensors_error(self):
        """Test error when insufficient sensors available."""
        sensor = Sensor(latitude=0.0, longitude=0.0, aqi_value=100.0)
        target = GeoPoint(latitude=0.0, longitude=0.0)
        
        interpolator = IDWInterpolator(min_sensors=2)
        
        with pytest.raises(ValueError, match="Insufficient sensors"):
            interpolator.interpolate([sensor], target)
    
    def test_empty_sensors_error(self):
        """Test error with empty sensor list."""
        target = GeoPoint(latitude=0.0, longitude=0.0)
        interpolator = IDWInterpolator()
        
        with pytest.raises(ValueError, match="At least one sensor"):
            interpolator.interpolate([], target)
    
    def test_all_sensors_filtered_error(self):
        """Test error when all sensors filtered by max_distance."""
        sensor = Sensor(latitude=0.0, longitude=10.0, aqi_value=100.0)
        target = GeoPoint(latitude=0.0, longitude=0.0)
        
        # Max distance too small to include any sensor
        interpolator = IDWInterpolator(max_distance_km=1.0)
        
        with pytest.raises(ValueError, match="Insufficient sensors"):
            interpolator.interpolate([sensor], target)
    
    def test_confidence_calculation(self):
        """Test confidence based on nearest sensor distance."""
        sensor_close = Sensor(latitude=0.0, longitude=0.0, aqi_value=100.0)
        sensor_far = Sensor(latitude=0.0, longitude=10.0, aqi_value=100.0)
        target_close = GeoPoint(latitude=0.0, longitude=0.01)
        target_far = GeoPoint(latitude=0.0, longitude=5.0)
        
        interpolator = IDWInterpolator()
        
        result_close = interpolator.interpolate([sensor_close, sensor_far], target_close)
        result_far = interpolator.interpolate([sensor_close, sensor_far], target_far)
        
        # Confidence should be higher when target is closer to sensors
        assert result_close.confidence > result_far.confidence


class TestSpatialInterpolationService:
    """Test high-level spatial interpolation service."""
    
    def test_default_interpolator(self):
        """Test service initializes with default IDW interpolator."""
        service = SpatialInterpolationService()
        assert isinstance(service.interpolator, IDWInterpolator)
    
    def test_custom_interpolator(self):
        """Test service with custom interpolator."""
        custom_idw = IDWInterpolator(power=3.0)
        service = SpatialInterpolationService(interpolator=custom_idw)
        assert service.interpolator is custom_idw
    
    def test_estimate_aqi_basic(self):
        """Test basic AQI estimation."""
        service = SpatialInterpolationService()
        
        sensors = [
            Sensor(latitude=0.0, longitude=0.0, aqi_value=100.0),
            Sensor(latitude=0.0, longitude=1.0, aqi_value=50.0),
        ]
        
        result = service.estimate_aqi(sensors, latitude=0.0, longitude=0.5)
        
        assert isinstance(result, InterpolationResult)
        assert 50.0 < result.estimated_aqi < 100.0
    
    def test_estimate_aqi_from_dicts(self):
        """Test estimation with dictionary input."""
        service = SpatialInterpolationService()
        
        sensors = [
            {"latitude": 0.0, "longitude": 0.0, "aqi_value": 100.0, "sensor_id": "s1"},
            {"latitude": 0.0, "longitude": 1.0, "aqi_value": 50.0, "sensor_id": "s2"},
        ]
        
        result = service.estimate_aqi_from_dicts(sensors, latitude=0.0, longitude=0.5)
        
        assert isinstance(result, InterpolationResult)
        assert result.sensors_used == 2
    
    def test_estimate_aqi_from_dicts_missing_field(self):
        """Test error handling for missing required field."""
        service = SpatialInterpolationService()
        
        sensors = [
            {"latitude": 0.0, "longitude": 0.0, "aqi_value": 100.0},
            {"latitude": 0.0, "longitude": 1.0},  # Missing aqi_value
        ]
        
        with pytest.raises(ValueError, match="missing required keys"):
            service.estimate_aqi_from_dicts(sensors, latitude=0.0, longitude=0.5)
    
    def test_batch_estimate(self):
        """Test batch estimation at multiple locations."""
        service = SpatialInterpolationService()
        
        sensors = [
            Sensor(latitude=0.0, longitude=0.0, aqi_value=100.0),
            Sensor(latitude=1.0, longitude=1.0, aqi_value=50.0),
        ]
        
        targets = [
            (0.0, 0.0),
            (0.5, 0.5),
            (1.0, 1.0),
        ]
        
        results = service.batch_estimate(sensors, targets)
        
        assert len(results) == 3
        assert all(isinstance(r, InterpolationResult) for r in results)
        # First result should be exact (100), last should be exact (50)
        assert results[0].estimated_aqi == 100.0
        assert results[2].estimated_aqi == 50.0
    
    def test_set_interpolator(self):
        """Test changing interpolation method."""
        service = SpatialInterpolationService()
        original = service.interpolator
        
        new_interpolator = IDWInterpolator(power=3.0)
        service.set_interpolator(new_interpolator)
        
        assert service.interpolator is new_interpolator
        assert service.interpolator is not original
    
    def test_set_invalid_interpolator(self):
        """Test error when setting invalid interpolator."""
        service = SpatialInterpolationService()
        
        with pytest.raises(TypeError):
            service.set_interpolator("not an interpolator")


class TestFactoryFunction:
    """Test factory function for service creation."""
    
    def test_factory_default(self):
        """Test factory function with defaults."""
        service = create_spatial_interpolation_service()
        assert isinstance(service, SpatialInterpolationService)
        assert isinstance(service.interpolator, IDWInterpolator)
    
    def test_factory_custom_parameters(self):
        """Test factory function with custom parameters."""
        service = create_spatial_interpolation_service(
            power=3.0,
            min_sensors=2,
            max_sensors=5,
            max_distance_km=10.0
        )
        
        interpolator = service.interpolator
        assert interpolator.power == 3.0
        assert interpolator.min_sensors == 2
        assert interpolator.max_sensors == 5
        assert interpolator.max_distance_km == 10.0


class TestIntegrationScenarios:
    """Integration tests with realistic scenarios."""
    
    def test_urban_grid_interpolation(self):
        """Test interpolation in urban grid pattern."""
        # 3x3 grid of sensors
        sensors = []
        for lat in range(3):
            for lon in range(3):
                aqi = 50 + (lat + lon) * 10  # Gradient from 50 to 90
                sensors.append(
                    Sensor(
                        latitude=float(lat),
                        longitude=float(lon),
                        aqi_value=float(aqi),
                        sensor_id=f"sensor_{lat}_{lon}"
                    )
                )
        
        service = SpatialInterpolationService()
        
        # Test at center
        result = service.estimate_aqi(sensors, 1.0, 1.0)
        assert 60.0 < result.estimated_aqi < 80.0
        assert result.sensors_used > 0
    
    def test_sparse_sensor_network(self):
        """Test with sparse sensor coverage."""
        sensors = [
            Sensor(latitude=0.0, longitude=0.0, aqi_value=100.0, sensor_id="north"),
            Sensor(latitude=0.0, longitude=3.0, aqi_value=80.0, sensor_id="south"),
        ]
        
        service = create_spatial_interpolation_service(min_sensors=1, max_distance_km=None)
        
        # Request at midpoint
        result = service.estimate_aqi(sensors, 0.0, 1.5)
        
        assert 80.0 < result.estimated_aqi < 100.0
        assert result.confidence < 1.0  # Should have lower confidence
    
    def test_high_variance_scenario(self):
        """Test interpolation with high variance in sensor values."""
        sensors = [
            Sensor(latitude=0.0, longitude=0.0, aqi_value=20.0),
            Sensor(latitude=0.0, longitude=1.0, aqi_value=200.0),
        ]
        
        interpolator = IDWInterpolator()
        
        # Close to low sensor
        result_low = interpolator.interpolate(sensors, GeoPoint(0.0, 0.1))
        # Close to high sensor
        result_high = interpolator.interpolate(sensors, GeoPoint(0.0, 0.9))
        
        # Should show significant difference
        assert result_high.estimated_aqi > result_low.estimated_aqi
    
    def test_coastal_area_interpolation(self):
        """Test realistic coastal area scenario."""
        sensors = [
            Sensor(latitude=40.7128, longitude=-74.0060, aqi_value=75.0, sensor_id="nyc_1"),
            Sensor(latitude=40.7200, longitude=-74.0100, aqi_value=78.0, sensor_id="nyc_2"),
            Sensor(latitude=40.7050, longitude=-74.0150, aqi_value=72.0, sensor_id="nyc_3"),
        ]
        
        service = SpatialInterpolationService()
        
        # Estimate between the sensors
        result = service.estimate_aqi(sensors, 40.7120, -74.0100)
        
        assert 70.0 < result.estimated_aqi < 80.0
        assert result.sensors_used == 3
