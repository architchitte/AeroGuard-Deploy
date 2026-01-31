# Spatial Interpolation Service

## Overview

The **Spatial Interpolation Service** provides hyper-local air quality estimation by interpolating AQI values from nearby sensors to arbitrary geographic locations. It implements the industry-standard **Inverse Distance Weighting (IDW)** algorithm with a modular architecture designed to support future interpolation methods like Kriging.

**Key Capabilities:**
- 📍 Estimate AQI at any location using nearby sensor measurements
- 🎯 Inverse Distance Weighting (IDW) with configurable power parameter
- 🌍 Accurate geographic distance calculation using Haversine formula
- 🛡️ Input validation and comprehensive error handling
- 📊 Confidence assessment based on sensor proximity
- 🔌 Modular design for extensible interpolation methods
- ⚡ Batch processing for grid-based estimation
- 🔍 Sensor filtering by distance and count

## Architecture

### System Overview

```
Sensor Network
    │
    ├─ Sensor 1: AQI, Location
    ├─ Sensor 2: AQI, Location
    └─ Sensor N: AQI, Location
         │
         ▼
┌─────────────────────────────────────┐
│   Spatial Interpolation Service     │
│  (High-level orchestration)         │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   IDWInterpolator                   │
│  (Inverse Distance Weighting)       │
│                                      │
│  - Haversine Distance Calculation   │
│  - Weight Computation               │
│  - Confidence Assessment            │
└─────────────────────────────────────┘
         │
         ▼
   Target Location (Lat, Lon)
         │
         ▼
   Estimated AQI + Metadata
```

### Core Classes

#### 1. **GeoPoint**
Represents a geographic location with validation.

```python
@dataclass
class GeoPoint:
    latitude: float      # -90 to 90
    longitude: float     # -180 to 180
```

#### 2. **Sensor**
Extends GeoPoint with AQI measurement data.

```python
@dataclass
class Sensor(GeoPoint):
    aqi_value: float     # Non-negative, typically 0-500
    sensor_id: Optional[str]
    measurement_time: Optional[str]
```

#### 3. **InterpolationResult**
Complete output from interpolation operation.

```python
@dataclass
class InterpolationResult:
    estimated_aqi: float         # Interpolated AQI value
    confidence: float            # 0.0-1.0, based on proximity
    sensors_used: int            # Number of sensors in calculation
    nearest_sensor_distance_km: float
    interpolation_method: str    # Method identifier
```

#### 4. **SpatialInterpolator** (ABC)
Abstract base class for interpolation algorithms.

Allows flexible implementation of different methods (IDW, Kriging, Spline, etc.).

#### 5. **IDWInterpolator**
Concrete implementation of Inverse Distance Weighting.

**Algorithm:**
$$\text{AQI}_{\text{target}} = \frac{\sum_{i=1}^{n} w_i \cdot \text{AQI}_i}{\sum_{i=1}^{n} w_i}$$

where weights are:
$$w_i = \frac{1}{d_i^p}$$

- $d_i$ = distance from target to sensor $i$
- $p$ = power parameter (default: 2.0 for inverse square distance)

#### 6. **SpatialInterpolationService**
High-level service coordinating interpolation operations.

## Usage Patterns

### Pattern 1: Basic Estimation

```python
from app.services.spatial_interpolation import (
    Sensor,
    SpatialInterpolationService
)

# Create service
service = SpatialInterpolationService()

# Define sensors
sensors = [
    Sensor(40.7128, -74.0060, 75.0, sensor_id="sensor_1"),
    Sensor(40.7200, -74.0100, 78.0, sensor_id="sensor_2"),
]

# Estimate AQI at target location
result = service.estimate_aqi(sensors, latitude=40.7150, longitude=-74.0080)

print(f"Estimated AQI: {result.estimated_aqi:.1f}")
print(f"Confidence: {result.confidence:.1%}")
```

### Pattern 2: Dictionary-Based Input (API)

```python
# Sensor data from database
sensors = [
    {"latitude": 40.7128, "longitude": -74.0060, "aqi_value": 75.0},
    {"latitude": 40.7200, "longitude": -74.0100, "aqi_value": 78.0},
]

result = service.estimate_aqi_from_dicts(
    sensors,
    latitude=40.7150,
    longitude=-74.0080
)
```

### Pattern 3: Batch Estimation

```python
# Estimate at multiple locations (grid points)
targets = [
    (40.71, -74.00),
    (40.72, -74.01),
    (40.73, -74.02),
]

results = service.batch_estimate(sensors, targets)

for result in results:
    print(f"AQI: {result.estimated_aqi:.1f}")
```

### Pattern 4: Custom Interpolation Parameters

```python
from app.services.spatial_interpolation import create_spatial_interpolation_service

# Create service with custom parameters
service = create_spatial_interpolation_service(
    power=3.0,              # Higher = more weight to nearest sensors
    min_sensors=2,          # Require at least 2 sensors
    max_sensors=5,          # Use at most 5 closest sensors
    max_distance_km=10.0    # Ignore sensors > 10 km away
)

result = service.estimate_aqi(sensors, lat, lon)
```

### Pattern 5: Switching Interpolation Methods

```python
# Start with IDW
service = SpatialInterpolationService()

# Later, switch to different method (e.g., future Kriging)
new_interpolator = IDWInterpolator(power=3.0)
service.set_interpolator(new_interpolator)

# Estimate using new method
result = service.estimate_aqi(sensors, lat, lon)
```

## Inverse Distance Weighting (IDW) Algorithm

### How IDW Works

IDW estimates values at unmeasured locations by:

1. **Distance Calculation**: Compute distances from target to all sensors using Haversine formula
2. **Weight Calculation**: Assign weights inversely proportional to distance
3. **Weighted Average**: Calculate weighted average of sensor AQI values
4. **Confidence**: Assess confidence based on nearest sensor distance

### Power Parameter Effect

The power parameter $p$ controls how much closer sensors influence the estimate:

| Power | Behavior | Use Case |
|-------|----------|----------|
| 1.0 | Linear falloff | Smooth interpolation |
| 2.0 | Inverse square (default) | Balanced localization |
| 3.0+ | Steep falloff | Highly localized |

**Example:**
- Power=1: Weight at 1 km = 1.0, at 2 km = 0.5
- Power=2: Weight at 1 km = 1.0, at 2 km = 0.25 (default)
- Power=3: Weight at 1 km = 1.0, at 2 km = 0.125

### Advantages
- ✅ Simple and fast
- ✅ No assumptions about data distribution
- ✅ Guaranteed values between min/max of sensors
- ✅ Intuitive parameter tuning

### Limitations
- ⚠️ No uncertainty quantification
- ⚠️ Can create "bulls-eye" effects around sensor points
- ⚠️ Doesn't account for spatial correlation

### When to Use IDW
- Rapid estimation needed
- Sensor network is dense
- Simplicity is priority
- No prior knowledge of AQI field

### When to Consider Alternatives
- Uncertainty quantification needed → Kriging
- Smooth surface required → Spline
- Sparse sensors → Kriging
- High complexity acceptable → Machine learning models

## Distance Calculation

### Haversine Formula

The service uses the Haversine formula for accurate geographic distances:

$$a = \sin^2\left(\frac{\Delta\text{lat}}{2}\right) + \cos(\text{lat}_1) \cos(\text{lat}_2) \sin^2\left(\frac{\Delta\text{lon}}{2}\right)$$

$$c = 2 \arctan2\left(\sqrt{a}, \sqrt{1-a}\right)$$

$$d = R \cdot c$$

Where:
- $R$ = Earth's radius (6371 km)
- More accurate than Euclidean distance
- Accounts for Earth's curvature
- Accurate over large distances

### Distance Units
All distances in the service are in **kilometers**.

## Configuration Guide

### IDWInterpolator Parameters

```python
interpolator = IDWInterpolator(
    power=2.0,              # Distance weighting exponent
    min_sensors=1,          # Minimum sensors required
    max_sensors=None,       # Maximum sensors to use (None = all)
    max_distance_km=None    # Max distance to consider (None = unlimited)
)
```

#### power (float, default=2.0)
- **Range:** > 0
- **Default:** 2.0 (inverse square distance)
- **Effect:** Higher values = more localized weighting
- **Recommendation:** 
  - 1.0-1.5 for smooth interpolation
  - 2.0-3.0 for typical use
  - 3.0+ for highly localized effects

#### min_sensors (int, default=1)
- **Range:** >= 1
- **Default:** 1
- **Effect:** Requires minimum number of sensors within range
- **Recommendation:**
  - 1 for single sensor (degenerate case)
  - 2+ for robust estimation
  - Adjust based on sensor density

#### max_sensors (int or None, default=None)
- **Range:** None or >= min_sensors
- **Default:** None (use all sensors)
- **Effect:** Limit to N closest sensors
- **Recommendation:**
  - None for sparse networks
  - 3-10 for dense networks
  - Reduces computation cost

#### max_distance_km (float or None, default=None)
- **Range:** None or > 0
- **Default:** None (no distance limit)
- **Effect:** Ignore sensors beyond distance threshold
- **Recommendation:**
  - None for sparse networks
  - 5-20 km for dense urban areas
  - Improves local accuracy

## Confidence Assessment

The service computes confidence scores based on sensor proximity:

$$\text{confidence} = \frac{1}{1 + (d/d_{\text{half}})^2}$$

Where:
- $d$ = distance to nearest sensor (km)
- $d_{\text{half}}$ = reference distance (default: 5 km, gives 50% confidence)
- Range: [0.1, 1.0]

**Interpretation:**
- Confidence ≈ 1.0: Sensor very close, high reliability
- Confidence ≈ 0.5: Typical interpolation distance
- Confidence < 0.2: Limited sensor coverage, use with caution

## Error Handling

### Input Validation

The service validates all inputs:

```python
# Invalid latitude (outside -90 to 90)
Sensor(latitude=95.0, longitude=0.0, aqi_value=50.0)
# Raises: ValueError

# Invalid AQI (negative)
Sensor(latitude=0.0, longitude=0.0, aqi_value=-5.0)
# Raises: ValueError

# Insufficient sensors
IDWInterpolator(min_sensors=3).interpolate(
    [sensor1],
    target
)
# Raises: ValueError
```

### Error Recovery

```python
try:
    result = service.estimate_aqi(sensors, lat, lon)
except ValueError as e:
    # Handle validation error
    logger.error(f"Estimation failed: {e}")
    # Use fallback strategy
except TypeError as e:
    # Handle type error
    logger.error(f"Invalid input type: {e}")
```

## Performance

### Time Complexity
- **N sensors, M targets:**
  - Single estimate: O(N log N) sorting + O(N) interpolation
  - Batch estimate: O(N log N + M×N)
  - Typical: 1-10 ms per target

### Space Complexity
- O(N) for sensor storage
- O(N) for distance calculations

### Optimization Tips

1. **Limit max_sensors** for large networks
   ```python
   IDWInterpolator(max_sensors=10)  # Use 10 closest only
   ```

2. **Use max_distance_km** to exclude far sensors
   ```python
   IDWInterpolator(max_distance_km=10.0)  # 10 km radius
   ```

3. **Batch processing** for multiple locations
   ```python
   results = service.batch_estimate(sensors, targets)  # More efficient than loop
   ```

4. **Sensor caching** for repeated estimates
   - Consider caching sensor data locally
   - Update periodically from source

## Integration Patterns

### Pattern 1: REST API Integration

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
service = SpatialInterpolationService()

@app.route('/api/interpolate', methods=['POST'])
def interpolate():
    data = request.json
    
    sensors = [Sensor(**s) for s in data['sensors']]
    result = service.estimate_aqi(
        sensors,
        data['latitude'],
        data['longitude']
    )
    
    return jsonify(result.to_dict())
```

### Pattern 2: Database Integration

```python
from sqlalchemy import select
from app.models import SensorModel

def estimate_from_db(lat, lon, region_id):
    # Fetch sensors from database
    stmt = select(SensorModel).where(
        SensorModel.region_id == region_id
    )
    db_sensors = session.execute(stmt).scalars()
    
    # Convert to Sensor objects
    sensors = [
        Sensor(s.latitude, s.longitude, s.aqi_value)
        for s in db_sensors
    ]
    
    # Estimate
    return service.estimate_aqi(sensors, lat, lon)
```

### Pattern 3: Batch Map Generation

```python
def generate_aqi_heatmap(sensors, bounds, resolution=0.01):
    """Generate AQI heatmap for region."""
    points = []
    for lat in arange(bounds.south, bounds.north, resolution):
        for lon in arange(bounds.west, bounds.east, resolution):
            points.append((lat, lon))
    
    results = service.batch_estimate(sensors, points)
    
    # Convert to GeoJSON or raster format
    return format_results(results, bounds)
```

## Testing

The module includes 52 comprehensive tests covering:

- **Data Validation:** GeoPoint, Sensor, InterpolationResult
- **Distance Calculation:** Haversine accuracy
- **IDW Algorithm:** Various sensor configurations
- **Edge Cases:** Single sensor, exact location, insufficient sensors
- **Parameters:** Power, max_sensors, max_distance_km
- **Batch Processing:** Multiple targets
- **Integration:** Real-world scenarios

Run tests:
```bash
python -m pytest tests/test_spatial_interpolation.py -v
```

Expected output:
```
52 passed in 1.22s
```

## Future Enhancements

### Planned Extensions

1. **Kriging Interpolator**
   - Spatial correlation modeling
   - Variance/uncertainty quantification
   - Better predictions with sparse data
   - Trade-off: More computational cost

2. **Spline Interpolation**
   - Smooth surface generation
   - Better for continuous phenomena
   - Memory efficient for large grids

3. **Machine Learning Models**
   - Neural networks for complex patterns
   - Incorporate additional features (wind, time, etc.)
   - Learning-based weight optimization

4. **Performance Optimizations**
   - Spatial indexing (KD-tree, R-tree)
   - Caching and memoization
   - GPU acceleration for large batches
   - Incremental updates for streaming data

5. **Advanced Confidence**
   - Uncertainty bounds (confidence intervals)
   - Leave-one-out cross-validation error
   - Sensor reliability weighting

### Extensibility Design

The modular architecture supports future extensions:

```python
# Current: IDW
class IDWInterpolator(SpatialInterpolator):
    def interpolate(self, sensors, target):
        # IDW implementation
        pass

# Future: Kriging
class KrigingInterpolator(SpatialInterpolator):
    def interpolate(self, sensors, target):
        # Kriging implementation
        pass

# Seamless switching
service.set_interpolator(KrigingInterpolator())
```

## API Reference

### SpatialInterpolationService

```python
def estimate_aqi(
    sensors: List[Sensor],
    latitude: float,
    longitude: float
) -> InterpolationResult:
    """Estimate AQI at target location."""

def estimate_aqi_from_dicts(
    sensors: List[dict],
    latitude: float,
    longitude: float
) -> InterpolationResult:
    """Estimate AQI using dictionary input."""

def batch_estimate(
    sensors: List[Sensor],
    targets: List[Tuple[float, float]]
) -> List[InterpolationResult]:
    """Estimate AQI at multiple locations."""

def set_interpolator(
    interpolator: SpatialInterpolator
):
    """Change interpolation method."""
```

### IDWInterpolator

```python
def interpolate(
    sensors: List[Sensor],
    target: GeoPoint
) -> InterpolationResult:
    """Perform IDW interpolation."""

@staticmethod
def haversine_distance(
    point1: GeoPoint,
    point2: GeoPoint
) -> float:
    """Calculate geographic distance in km."""
```

## Troubleshooting

### Issue: "Insufficient sensors" error
**Solution:** 
- Check min_sensors parameter
- Verify sensor locations are within max_distance_km
- Ensure sensors have valid coordinates

### Issue: Low confidence scores
**Solution:**
- Insufficient sensor coverage in area
- Consider increasing max_distance_km
- Add more sensors to network

### Issue: Unexpected interpolated values
**Solution:**
- Check sensor AQI values (outliers?)
- Adjust power parameter (try 1.0-3.0)
- Verify distance calculations (use haversine_distance)

### Issue: Performance degradation
**Solution:**
- Use max_sensors to limit computations
- Implement caching for repeated locations
- Use batch_estimate instead of loop

## Best Practices

1. **Always validate input sensors**
   - Check coordinates are valid
   - Verify AQI values are realistic
   - Ensure sensor_id is unique

2. **Set appropriate parameters**
   - min_sensors ≥ 2 for robustness
   - Adjust power based on sensor density
   - Use max_distance_km for local accuracy

3. **Monitor confidence scores**
   - Warn users if confidence < 0.3
   - Consider uncertainty in decisions
   - Inform stakeholders of estimate reliability

4. **Test with real sensor networks**
   - Validate against actual measurements
   - Cross-check interpolation accuracy
   - Adjust parameters based on results

5. **Consider sensor quality**
   - Weight by sensor calibration quality
   - Handle outliers appropriately
   - Update old measurements carefully

## See Also

- [Usage Examples](../../examples/spatial_interpolation_examples.py)
- [Test Suite](../../tests/test_spatial_interpolation.py)
- [Quick Reference](SPATIAL_INTERPOLATION_QUICK_REF.md)
- [Explainability Module](EXPLAINABILITY.md)
- [Generative Explainer](GENERATIVE_EXPLAINER.md)
