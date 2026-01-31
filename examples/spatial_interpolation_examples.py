"""
Spatial Interpolation Service - Usage Examples

This module demonstrates various use cases for hyper-local AQI estimation
using inverse distance weighting (IDW) spatial interpolation.

Examples cover:
- Basic single-target estimation
- Multiple target locations (batch processing)
- Different interpolation parameters
- Confidence assessment
- Integration with real sensor networks
- Edge case handling
"""

from app.services.spatial_interpolation import (
    Sensor,
    GeoPoint,
    IDWInterpolator,
    SpatialInterpolationService,
    create_spatial_interpolation_service,
)


# ============================================================================
# Example 1: Basic Hyper-Local AQI Estimation
# ============================================================================

def example_1_basic_estimation():
    """
    Demonstrates basic spatial interpolation with multiple nearby sensors.
    
    Scenario: Urban area with 3 air quality sensors, estimate AQI at
    a location without a sensor.
    """
    print("\n" + "="*70)
    print("Example 1: Basic Hyper-Local AQI Estimation")
    print("="*70)
    
    # Create sensor network in urban area (NYC coordinates)
    sensors = [
        Sensor(
            latitude=40.7128,
            longitude=-74.0060,
            aqi_value=75.0,
            sensor_id="manhattan_1"
        ),
        Sensor(
            latitude=40.7200,
            longitude=-74.0100,
            aqi_value=78.0,
            sensor_id="manhattan_2"
        ),
        Sensor(
            latitude=40.7050,
            longitude=-74.0150,
            aqi_value=72.0,
            sensor_id="brooklyn_1"
        ),
    ]
    
    # Create service with default IDW interpolator
    service = SpatialInterpolationService()
    
    # Estimate AQI at unknown location (between sensors)
    target_lat = 40.7120
    target_lon = -74.0100
    
    result = service.estimate_aqi(sensors, target_lat, target_lon)
    
    print(f"\nSensor Network:")
    for sensor in sensors:
        print(f"  {sensor.sensor_id}: AQI {sensor.aqi_value} "
              f"at ({sensor.latitude}, {sensor.longitude})")
    
    print(f"\nTarget Location: ({target_lat}, {target_lon})")
    print(f"\n--- Estimation Result ---")
    print(f"Estimated AQI: {result.estimated_aqi:.1f}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Sensors Used: {result.sensors_used}")
    print(f"Nearest Sensor Distance: {result.nearest_sensor_distance_km:.2f} km")
    print(f"Interpolation Method: {result.interpolation_method}")


# ============================================================================
# Example 2: City-Wide Grid Estimation
# ============================================================================

def example_2_grid_estimation():
    """
    Demonstrates batch estimation across a grid of locations.
    
    Scenario: Create a heatmap by estimating AQI at grid points
    across a city.
    """
    print("\n" + "="*70)
    print("Example 2: City-Wide Grid Estimation")
    print("="*70)
    
    # Sparse sensor network
    sensors = [
        Sensor(0.0, 0.0, 100.0, "north_west"),
        Sensor(0.0, 1.0, 60.0, "north_east"),
        Sensor(1.0, 0.0, 80.0, "south_west"),
        Sensor(1.0, 1.0, 40.0, "south_east"),
    ]
    
    service = SpatialInterpolationService()
    
    # Create grid of estimation points
    grid_points = []
    for lat in [0.0, 0.25, 0.5, 0.75, 1.0]:
        for lon in [0.0, 0.25, 0.5, 0.75, 1.0]:
            grid_points.append((lat, lon))
    
    print(f"\nEstimating AQI across {len(grid_points)} grid points...")
    
    # Batch estimate
    results = service.batch_estimate(sensors, grid_points)
    
    # Display results in grid format
    print(f"\nInterpolated AQI Values (Grid):")
    header = f"{'Lat':<8} {'Lon':<8} 0.00{'':<4} 0.25{'':<4} 0.50{'':<4} 0.75{'':<4} 1.00"
    print(f"{'Lat':<8} {'0.00':<8} {'0.25':<8} {'0.50':<8} {'0.75':<8} {'1.00':<8}")
    print("-" * 50)
    
    for lat_idx, lat in enumerate([0.0, 0.25, 0.5, 0.75, 1.0]):
        row = f"{lat:<8.2f}"
        for lon_idx, lon in enumerate([0.0, 0.25, 0.5, 0.75, 1.0]):
            result_idx = lat_idx * 5 + lon_idx
            aqi = results[result_idx].estimated_aqi
            row += f"{aqi:<8.1f}"
        print(row)
    
    # Statistics
    aqi_values = [r.estimated_aqi for r in results]
    print(f"\nGrid Statistics:")
    print(f"  Min AQI: {min(aqi_values):.1f}")
    print(f"  Max AQI: {max(aqi_values):.1f}")
    print(f"  Mean AQI: {sum(aqi_values)/len(aqi_values):.1f}")


# ============================================================================
# Example 3: Power Parameter Sensitivity
# ============================================================================

def example_3_power_parameter():
    """
    Demonstrates how power parameter affects interpolation behavior.
    
    Higher power = more weight on closer sensors (localized)
    Lower power = more uniform weight distribution (smooth)
    """
    print("\n" + "="*70)
    print("Example 3: Power Parameter Sensitivity Analysis")
    print("="*70)
    
    # Two sensors with different values
    sensors = [
        Sensor(latitude=0.0, longitude=0.0, aqi_value=100.0, sensor_id="clean"),
        Sensor(latitude=0.0, longitude=1.0, aqi_value=50.0, sensor_id="polluted"),
    ]
    
    # Target location closer to clean sensor
    target_lat = 0.0
    target_lon = 0.1
    
    print(f"\nSensor Network:")
    print(f"  Clean zone: AQI 100 at (0.0, 0.0)")
    print(f"  Polluted zone: AQI 50 at (0.0, 1.0)")
    print(f"\nTarget Location: ({target_lat}, {target_lon})")
    print(f"  [Closer to clean zone]")
    
    print(f"\n--- Power Parameter Effect ---")
    
    powers = [1.0, 2.0, 3.0, 4.0]
    
    for power in powers:
        interpolator = IDWInterpolator(power=power)
        result = interpolator.interpolate(sensors, GeoPoint(target_lat, target_lon))
        
        print(f"\nPower = {power}:")
        print(f"  Estimated AQI: {result.estimated_aqi:.1f}")
        print(f"  Distance to nearest sensor: {result.nearest_sensor_distance_km:.2f} km")


# ============================================================================
# Example 4: Sensor Distance Filtering
# ============================================================================

def example_4_distance_filtering():
    """
    Demonstrates max_distance_km parameter to exclude distant sensors.
    
    Useful for preventing distant sensors from influencing local estimates,
    which improves accuracy in heterogeneous environments.
    """
    print("\n" + "="*70)
    print("Example 4: Sensor Distance Filtering")
    print("="*70)
    
    # Sparse sensor network across large area
    sensors = [
        Sensor(latitude=40.0, longitude=-74.0, aqi_value=80.0, sensor_id="local_1"),
        Sensor(latitude=40.01, longitude=-74.01, aqi_value=85.0, sensor_id="local_2"),
        Sensor(latitude=45.0, longitude=-75.0, aqi_value=50.0, sensor_id="remote"),
    ]
    
    target_lat = 40.005
    target_lon = -74.005
    
    print(f"\nSensor Network:")
    for s in sensors:
        print(f"  {s.sensor_id}: AQI {s.aqi_value} at ({s.latitude}, {s.longitude})")
    
    print(f"\nTarget Location: ({target_lat}, {target_lon})")
    
    # Without distance filtering
    service_no_filter = SpatialInterpolationService(
        IDWInterpolator(max_distance_km=None)
    )
    result_no_filter = service_no_filter.estimate_aqi(sensors, target_lat, target_lon)
    
    # With distance filtering (exclude remote sensor)
    service_with_filter = SpatialInterpolationService(
        IDWInterpolator(max_distance_km=200.0)
    )
    result_with_filter = service_with_filter.estimate_aqi(sensors, target_lat, target_lon)
    
    print(f"\n--- Without Distance Filter ---")
    print(f"Estimated AQI: {result_no_filter.estimated_aqi:.1f}")
    print(f"Sensors Used: {result_no_filter.sensors_used}")
    print(f"Confidence: {result_no_filter.confidence:.2%}")
    
    print(f"\n--- With Max Distance 200 km ---")
    print(f"Estimated AQI: {result_with_filter.estimated_aqi:.1f}")
    print(f"Sensors Used: {result_with_filter.sensors_used}")
    print(f"Confidence: {result_with_filter.confidence:.2%}")
    
    print(f"\nDifference: {abs(result_with_filter.estimated_aqi - result_no_filter.estimated_aqi):.1f} AQI points")


# ============================================================================
# Example 5: Confidence Assessment
# ============================================================================

def example_5_confidence_assessment():
    """
    Demonstrates how confidence varies with sensor proximity.
    
    Confidence is highest when sensors are nearby, decreases with distance.
    Use confidence to weight estimates or determine reliability.
    """
    print("\n" + "="*70)
    print("Example 5: Confidence Assessment Based on Proximity")
    print("="*70)
    
    # One reference sensor
    sensors = [
        Sensor(latitude=0.0, longitude=0.0, aqi_value=75.0, sensor_id="reference"),
    ]
    
    service = SpatialInterpolationService()
    
    # Estimate at various distances from sensor
    distances = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]
    
    print(f"\nConfidence at Various Distances from Sensor:")
    print(f"{'Distance':<12} {'Lon Offset':<12} {'Est. AQI':<12} {'Confidence':<12}")
    print("-" * 50)
    
    for offset in distances:
        result = service.estimate_aqi(sensors, 0.0, offset)
        lon_distance = result.nearest_sensor_distance_km
        
        print(f"{lon_distance:<12.2f} km {offset:<12.2f} "
              f"{result.estimated_aqi:<12.1f} {result.confidence:<12.1%}")


# ============================================================================
# Example 6: Dictionary-Based Input (API Integration)
# ============================================================================

def example_6_dictionary_input():
    """
    Demonstrates API-friendly interface using dictionaries.
    
    Useful for integrating with databases, JSON APIs, or external
    sensor data sources.
    """
    print("\n" + "="*70)
    print("Example 6: Dictionary-Based Input (API Integration)")
    print("="*70)
    
    # Sensor data from database query or API response
    sensor_dicts = [
        {
            "sensor_id": "indoor_1",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "aqi_value": 45.0,
            "measurement_time": "2024-01-31T12:00:00Z"
        },
        {
            "sensor_id": "outdoor_1",
            "latitude": 40.7200,
            "longitude": -74.0100,
            "aqi_value": 65.0,
            "measurement_time": "2024-01-31T12:00:00Z"
        },
        {
            "sensor_id": "rooftop_1",
            "latitude": 40.7050,
            "longitude": -74.0150,
            "aqi_value": 55.0,
            "measurement_time": "2024-01-31T12:00:00Z"
        },
    ]
    
    service = SpatialInterpolationService()
    
    print(f"\nSensor Data (from database):")
    for sensor in sensor_dicts:
        print(f"  {sensor['sensor_id']}: AQI {sensor['aqi_value']}")
    
    # Estimate using dictionary input
    result = service.estimate_aqi_from_dicts(
        sensor_dicts,
        latitude=40.7120,
        longitude=-74.0100
    )
    
    print(f"\nEstimation Result:")
    print(f"  Estimated AQI: {result.estimated_aqi:.1f}")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"  Sensors Used: {result.sensors_used}")


# ============================================================================
# Example 7: Multiple Target Estimation
# ============================================================================

def example_7_hotspot_detection():
    """
    Demonstrates identifying pollution hotspots across a city.
    
    Uses batch estimation to find areas with high AQI values.
    """
    print("\n" + "="*70)
    print("Example 7: Pollution Hotspot Detection")
    print("="*70)
    
    # Sensor network with pollution gradient
    sensors = [
        Sensor(0.0, 0.0, 50.0, "clean_area"),
        Sensor(0.0, 1.0, 150.0, "industrial_area"),
        Sensor(1.0, 0.0, 60.0, "residential_area"),
        Sensor(1.0, 1.0, 140.0, "traffic_area"),
    ]
    
    # Create monitoring grid
    targets = [
        (0.0, 0.0),    # Clean
        (0.0, 0.5),    # Mixed
        (0.0, 1.0),    # Industrial
        (0.5, 0.5),    # Center
        (1.0, 0.5),    # Mixed
        (1.0, 1.0),    # Traffic
    ]
    
    service = SpatialInterpolationService()
    results = service.batch_estimate(sensors, targets)
    
    print(f"\nLocation Analysis:")
    print(f"{'Location':<15} {'Est. AQI':<12} {'Risk Level':<15}")
    print("-" * 40)
    
    locations = [
        "Clean Zone",
        "Industrial Fringe",
        "Industrial Zone",
        "City Center",
        "Mixed Zone",
        "Traffic Zone"
    ]
    
    for loc, result in zip(locations, results):
        if result.estimated_aqi < 50:
            risk = "Good"
        elif result.estimated_aqi < 100:
            risk = "Moderate"
        elif result.estimated_aqi < 150:
            risk = "Unhealthy (SG)"
        else:
            risk = "Unhealthy"
        
        print(f"{loc:<15} {result.estimated_aqi:<12.1f} {risk:<15}")


# ============================================================================
# Example 8: Modular Design - Future Kriging Support
# ============================================================================

def example_8_custom_interpolator():
    """
    Demonstrates the modular design that supports future interpolators.
    
    Currently uses IDW, but shows how service can be extended with
    other methods (Kriging, Spline, etc.) without changing service code.
    """
    print("\n" + "="*70)
    print("Example 8: Modular Interpolator Design")
    print("="*70)
    
    sensors = [
        Sensor(0.0, 0.0, 100.0),
        Sensor(0.0, 1.0, 50.0),
        Sensor(1.0, 0.0, 75.0),
    ]
    
    target = GeoPoint(0.5, 0.5)
    
    # Create service with default IDW
    service = SpatialInterpolationService()
    
    print(f"\nCurrent Interpolator: {type(service.interpolator).__name__}")
    
    result_idw = service.interpolator.interpolate(sensors, target)
    print(f"IDW Estimated AQI: {result_idw.estimated_aqi:.1f}")
    
    # Can easily swap with different parameters
    service.set_interpolator(IDWInterpolator(power=3.0))
    print(f"\nSwapped to: {type(service.interpolator).__name__} with power=3.0")
    
    result_p3 = service.interpolator.interpolate(sensors, target)
    print(f"IDW (power=3) Estimated AQI: {result_p3.estimated_aqi:.1f}")
    
    print(f"\nNote: Future versions could add:")
    print(f"  - KrigingInterpolator (for variance estimation)")
    print(f"  - SplineInterpolator (for smooth surfaces)")
    print(f"  - IDWInterpolator variations (exponential weighting)")
    print(f"\nService design allows plugin-and-play interpolation methods!")


# ============================================================================
# Example 9: Edge Cases and Robustness
# ============================================================================

def example_9_edge_cases():
    """
    Demonstrates handling of edge cases and boundary conditions.
    """
    print("\n" + "="*70)
    print("Example 9: Edge Cases and Error Handling")
    print("="*70)
    
    # Case 1: Single sensor (degenerate case)
    print(f"\n--- Case 1: Single Sensor ---")
    sensors_single = [Sensor(0.0, 0.0, 80.0, "only_sensor")]
    service = SpatialInterpolationService()
    result = service.estimate_aqi(sensors_single, 0.1, 0.1)
    print(f"Single sensor AQI: {result.estimated_aqi:.1f}")
    print(f"(Should use the only sensor's value)")
    
    # Case 2: Exact location match
    print(f"\n--- Case 2: Target at Exact Sensor Location ---")
    sensors = [Sensor(40.0, -74.0, 75.0, "times_square")]
    result = service.estimate_aqi(sensors, 40.0, -74.0)
    print(f"Estimated AQI at sensor location: {result.estimated_aqi:.1f}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"(Should match sensor value exactly)")
    
    # Case 3: Invalid input handling
    print(f"\n--- Case 3: Invalid Input Handling ---")
    try:
        service.estimate_aqi(sensors, latitude=95.0, longitude=0.0)
    except ValueError as e:
        print(f"Caught error: {e}")
    
    # Case 4: Insufficient sensors
    print(f"\n--- Case 4: Insufficient Sensors ---")
    try:
        strict_service = SpatialInterpolationService(
            IDWInterpolator(min_sensors=3)
        )
        strict_service.estimate_aqi(sensors, 40.0, -74.0)
    except ValueError as e:
        print(f"Caught error: {e}")


# ============================================================================
# Example 10: Real-World Scenario - Urban Monitoring
# ============================================================================

def example_10_urban_monitoring():
    """
    Realistic scenario: Monitoring air quality across a metropolitan area.
    """
    print("\n" + "="*70)
    print("Example 10: Real-World Urban Monitoring Scenario")
    print("="*70)
    
    # Simulated NYC air quality sensor network
    sensors = [
        Sensor(40.7128, -74.0060, 68.0, "manhattan_central"),
        Sensor(40.7614, -73.9776, 72.0, "upper_east"),
        Sensor(40.6892, -74.0445, 85.0, "brooklyn_heights"),
        Sensor(40.7505, -73.9972, 70.0, "midtown"),
        Sensor(40.8448, -73.8648, 62.0, "bronx_south"),
    ]
    
    print(f"\nSensor Network Deployment:")
    for sensor in sensors:
        print(f"  {sensor.sensor_id:<20} AQI: {sensor.aqi_value:5.1f} "
              f"at ({sensor.latitude:7.4f}, {sensor.longitude:8.4f})")
    
    # Create monitoring points (popular areas)
    monitoring_points = {
        "Central Park": (40.7829, -73.9654),
        "Times Square": (40.7580, -73.9855),
        "Brooklyn Bridge": (40.7061, -73.9969),
        "Statue of Liberty": (40.6892, -74.0445),
        "Grand Central": (40.7527, -73.9772),
    }
    
    service = create_spatial_interpolation_service(
        power=2.0,
        min_sensors=2,
        max_distance_km=50.0
    )
    
    print(f"\n--- Air Quality Estimate at Monitoring Points ---")
    print(f"{'Location':<20} {'AQI':<8} {'Confidence':<12} {'Risk Level':<15}")
    print("-" * 55)
    
    for location, (lat, lon) in monitoring_points.items():
        result = service.estimate_aqi(sensors, lat, lon)
        
        aqi = result.estimated_aqi
        if aqi < 50:
            risk = "Good"
        elif aqi < 100:
            risk = "Moderate"
        elif aqi < 150:
            risk = "Unhealthy (SG)"
        else:
            risk = "Unhealthy"
        
        print(f"{location:<20} {aqi:<8.1f} {result.confidence:<12.0%} {risk:<15}")
    
    print(f"\nMonitoring Complete! Use these estimates for:")
    print(f"  • Public health alerts")
    print(f"  • Tourism guidance")
    print(f"  • Urban planning")
    print(f"  • Air quality forecasting")


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    """
    Run all spatial interpolation examples.
    """
    print("\n" + "="*70)
    print("SPATIAL INTERPOLATION - COMPREHENSIVE EXAMPLES")
    print("="*70)
    print("\nHyper-local AQI estimation using inverse distance weighting (IDW)")
    print("and modular design supporting future interpolation methods.")
    
    example_1_basic_estimation()
    example_2_grid_estimation()
    example_3_power_parameter()
    example_4_distance_filtering()
    example_5_confidence_assessment()
    example_6_dictionary_input()
    example_7_hotspot_detection()
    example_8_custom_interpolator()
    example_9_edge_cases()
    example_10_urban_monitoring()
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nKey Features Demonstrated:")
    print("  * Inverse Distance Weighting (IDW) algorithm")
    print("  * Haversine distance calculation (geographic accuracy)")
    print("  * Confidence assessment based on sensor proximity")
    print("  * Flexible parameter tuning (power, max_distance, max_sensors)")
    print("  * Batch processing for grid-based estimation")
    print("  * API-friendly dictionary input")
    print("  * Modular design for future interpolation methods")
    print("  * Robust error handling and validation")
    print("\nNext Steps:")
    print("  1. Integrate with your sensor database")
    print("  2. Create monitoring dashboard with estimated AQI values")
    print("  3. Consider adding Kriging for uncertainty quantification")
    print("  4. Implement caching for frequently estimated locations")
