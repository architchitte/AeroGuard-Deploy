# Spatial Interpolation - Quick Reference

## 60-Second Quickstart

```python
from app.services.spatial_interpolation import (
    Sensor,
    SpatialInterpolationService
)

# Create service
service = SpatialInterpolationService()

# Add sensors with measurements
sensors = [
    Sensor(40.7128, -74.0060, 75.0, sensor_id="nyc_1"),
    Sensor(40.7200, -74.0100, 78.0, sensor_id="nyc_2"),
]

# Estimate AQI at target location
result = service.estimate_aqi(
    sensors,
    latitude=40.7150,
    longitude=-74.0080
)

print(f"Estimated AQI: {result.estimated_aqi:.1f}")
print(f"Confidence: {result.confidence:.1%}")
```

## Core Components

| Component | Purpose |
|-----------|---------|
| `GeoPoint` | Geographic location (lat/lon) |
| `Sensor` | Location + AQI measurement |
| `IDWInterpolator` | Inverse Distance Weighting algorithm |
| `SpatialInterpolationService` | High-level service |
| `InterpolationResult` | Estimation output |

## Service Methods

### estimate_aqi()
```python
result = service.estimate_aqi(
    sensors=List[Sensor],     # Sensor measurements
    latitude=float,           # Target latitude (-90 to 90)
    longitude=float           # Target longitude (-180 to 180)
) -> InterpolationResult
```

### estimate_aqi_from_dicts()
```python
# Sensor data from database/JSON
sensors = [
    {"latitude": 40.71, "longitude": -74.00, "aqi_value": 75.0},
    {"latitude": 40.72, "longitude": -74.01, "aqi_value": 78.0},
]

result = service.estimate_aqi_from_dicts(
    sensors=List[dict],       # Dict format
    latitude=float,
    longitude=float
) -> InterpolationResult
```

### batch_estimate()
```python
targets = [(40.71, -74.00), (40.72, -74.01)]

results = service.batch_estimate(
    sensors=List[Sensor],     # Fixed sensor network
    targets=List[Tuple]       # Multiple target locations
) -> List[InterpolationResult]
```

### set_interpolator()
```python
new_method = IDWInterpolator(power=3.0)
service.set_interpolator(new_method)
```

## Factory Function

```python
from app.services.spatial_interpolation import create_spatial_interpolation_service

# Quick creation with custom parameters
service = create_spatial_interpolation_service(
    power=2.0,              # Distance weighting
    min_sensors=1,          # Minimum required
    max_sensors=None,       # Maximum to use
    max_distance_km=None    # Distance limit (km)
)
```

## IDW Parameters

| Parameter | Type | Default | Range | Notes |
|-----------|------|---------|-------|-------|
| power | float | 2.0 | > 0 | Higher = more localized. Try 1-3 |
| min_sensors | int | 1 | ≥ 1 | Require minimum sensors available |
| max_sensors | int/None | None | ≥ min | Use only N closest sensors |
| max_distance_km | float/None | None | > 0 | Ignore distant sensors |

### Power Parameter Guidance

| Power | Effect | Use When |
|-------|--------|----------|
| 1.0 | Linear falloff | Smooth, gradual transition |
| 2.0 | Inverse square (default) | Balanced, typical case |
| 3.0 | Steep falloff | Highly localized |
| 4.0+ | Very localized | Near sensor emphasis |

## Output: InterpolationResult

```python
result = service.estimate_aqi(sensors, lat, lon)

# Access fields:
result.estimated_aqi              # float: Interpolated AQI value
result.confidence                 # float: 0.0-1.0 (proximity-based)
result.sensors_used               # int: Number of sensors used
result.nearest_sensor_distance_km # float: Distance to closest sensor
result.interpolation_method       # str: Method identifier
```

## Common Patterns

### Pattern 1: Basic Estimation
```python
sensors = [
    Sensor(0.0, 0.0, 100.0),
    Sensor(0.0, 1.0, 50.0),
]

result = service.estimate_aqi(sensors, 0.0, 0.5)
```

### Pattern 2: API Integration
```python
# From database
sensor_dicts = fetch_sensors_from_db(region_id)

result = service.estimate_aqi_from_dicts(
    sensor_dicts,
    latitude, longitude
)

return result.to_dict()  # JSON-ready
```

### Pattern 3: Create Heatmap
```python
points = []
for lat in range(-90, 91, 5):
    for lon in range(-180, 181, 5):
        points.append((lat, lon))

results = service.batch_estimate(sensors, points)

# results[i].estimated_aqi for each point
```

### Pattern 4: Configure for Accuracy
```python
service = create_spatial_interpolation_service(
    power=2.5,              # Slight localization boost
    min_sensors=2,          # Need at least 2
    max_sensors=5,          # Use 5 closest
    max_distance_km=20.0    # Within 20 km
)
```

### Pattern 5: Error Handling
```python
try:
    result = service.estimate_aqi(sensors, lat, lon)
except ValueError as e:
    logger.error(f"Estimation failed: {e}")
    # Fallback: use nearest sensor value
    return nearest_sensor.aqi_value
```

## Input Validation

| Field | Valid Range | Example |
|-------|-------------|---------|
| latitude | -90.0 to 90.0 | 40.7128 |
| longitude | -180.0 to 180.0 | -74.0060 |
| aqi_value | ≥ 0 | 75.0 |
| sensor_id | Any string | "sensor_nyc_1" |

## Confidence Interpretation

| Confidence | Meaning | Action |
|------------|---------|--------|
| > 0.8 | High reliability | Use directly |
| 0.5-0.8 | Good estimate | Use with caution |
| 0.2-0.5 | Moderate | Consider uncertainty |
| < 0.2 | Low coverage | Use as rough estimate |

## Haversine Distance

Distance in kilometers between two points:

```python
from app.services.spatial_interpolation import IDWInterpolator

dist_km = IDWInterpolator.haversine_distance(
    GeoPoint(40.7128, -74.0060),  # NYC
    GeoPoint(34.0522, -118.2437)  # LA
)
# Result: ~3944 km
```

## Performance Notes

| Operation | Time | Space |
|-----------|------|-------|
| Single estimate (N sensors) | O(N log N) | O(N) |
| Batch (N sensors, M targets) | O(N log N + MN) | O(N) |
| Typical: 10 sensors, 1 target | ~1-5 ms | ~1 KB |
| Typical: 100 sensors, 1000 targets | ~100-500 ms | ~100 KB |

## Constants

```python
EARTH_RADIUS_KM = 6371.0          # Used in haversine distance
DEFAULT_POWER = 2.0                # Default IDW exponent
DEFAULT_MIN_SENSORS = 1            # Default minimum
MIN_DISTANCE_FOR_EXACT = 1e-6      # ~1 mm, exact location threshold
```

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Latitude must be between -90 and 90" | Invalid latitude | Check coordinate |
| "Longitude must be between -180 and 180" | Invalid longitude | Check coordinate |
| "AQI value must be non-negative" | Negative AQI | Verify sensor data |
| "At least one sensor is required" | Empty sensor list | Add sensors |
| "Insufficient sensors: X < minimum Y" | Too few sensors | Add sensors or lower min_sensors |
| "Insufficient sensors within max_distance" | All sensors too far | Increase max_distance_km |

## Data Classes

### GeoPoint
```python
from app.services.spatial_interpolation import GeoPoint

point = GeoPoint(latitude=40.7128, longitude=-74.0060)
```

### Sensor
```python
from app.services.spatial_interpolation import Sensor

sensor = Sensor(
    latitude=40.7128,
    longitude=-74.0060,
    aqi_value=75.0,
    sensor_id="sensor_1",
    measurement_time="2024-01-31T12:00:00Z"
)
```

### InterpolationResult
```python
# Returned by estimate_aqi()
result: InterpolationResult

# Fields:
aqi = result.estimated_aqi
conf = result.confidence
count = result.sensors_used
dist = result.nearest_sensor_distance_km
method = result.interpolation_method

# JSON conversion:
json_dict = result.to_dict()
```

## Testing

Run tests:
```bash
python -m pytest tests/test_spatial_interpolation.py -v
```

Test coverage includes:
- Distance calculations
- IDW algorithm
- Parameter validation
- Edge cases
- Batch operations
- Integration scenarios

## Example: Quick Start

```python
from app.services.spatial_interpolation import (
    create_spatial_interpolation_service,
    Sensor
)

# 1. Create service
service = create_spatial_interpolation_service()

# 2. Add sensor data
sensors = [
    Sensor(40.0, -74.0, 75.0, "s1"),
    Sensor(40.1, -74.1, 80.0, "s2"),
]

# 3. Estimate
result = service.estimate_aqi(sensors, 40.05, -74.05)

# 4. Use result
print(f"AQI: {result.estimated_aqi:.1f}, "
      f"Confidence: {result.confidence:.0%}")
# Output: AQI: 77.5, Confidence: 100%
```

## Example: API Handler

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
service = create_spatial_interpolation_service()

@app.route('/api/aqi/interpolate', methods=['POST'])
def interpolate():
    try:
        data = request.json
        
        # Convert dicts to Sensors
        sensors = [Sensor(**s) for s in data['sensors']]
        
        # Estimate
        result = service.estimate_aqi(
            sensors,
            data['latitude'],
            data['longitude']
        )
        
        return jsonify(result.to_dict())
        
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), 400
```

## Example: Grid Generation

```python
from app.services.spatial_interpolation import create_spatial_interpolation_service

service = create_spatial_interpolation_service(
    max_distance_km=50.0
)

# Generate 5x5 grid
grid = []
for lat in range(40, 41, 1):
    row = []
    for lon in range(-74, -73, 1):
        result = service.estimate_aqi(sensors, lat, lon)
        row.append(result.estimated_aqi)
    grid.append(row)

# grid[i][j] = AQI at location (40+i, -74+j)
```

## Troubleshooting

| Issue | Debug | Fix |
|-------|-------|-----|
| Low confidence | Check nearest_sensor_distance_km | Add sensors nearby |
| Unexpected AQI | Validate sensor values | Check for outliers |
| "Insufficient sensors" | Check min_sensors, max_distance_km | Adjust parameters |
| Slow performance | Check N×M for batch | Use max_sensors limit |

## Advanced Tips

1. **Optimize for Accuracy**
   ```python
   # Use 2-3 power for localization
   service = create_spatial_interpolation_service(power=2.5)
   ```

2. **Optimize for Speed**
   ```python
   # Limit sensors
   service = create_spatial_interpolation_service(max_sensors=5)
   ```

3. **Optimize for Coverage**
   ```python
   # Allow distant sensors
   service = create_spatial_interpolation_service(min_sensors=1)
   ```

4. **Validate Before Estimate**
   ```python
   if result.confidence < 0.3:
       logger.warning("Low confidence estimate")
   ```

## Integration Checklist

- [ ] Import required classes
- [ ] Create service instance
- [ ] Prepare sensor data (validate coordinates)
- [ ] Call estimate_aqi() or batch_estimate()
- [ ] Check result.confidence
- [ ] Handle ValueError exceptions
- [ ] Log estimates for auditing
- [ ] Consider caching for repeated locations

## See Also

- [Full Documentation](SPATIAL_INTERPOLATION.md)
- [Usage Examples](../../examples/spatial_interpolation_examples.py)
- [Test Suite](../../tests/test_spatial_interpolation.py)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)
- [IDW Interpolation](https://en.wikipedia.org/wiki/Inverse_distance_weighting)
