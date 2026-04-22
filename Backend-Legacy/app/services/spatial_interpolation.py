"""
Spatial Interpolation Service for Hyper-Local AQI Estimation

This module provides spatial interpolation methods to estimate air quality
at arbitrary locations based on nearby sensor measurements. It implements
inverse distance weighting (IDW) as the primary method with a modular design
that supports future extensions (Kriging, etc.).

Key Features:
- Inverse Distance Weighting (IDW) algorithm
- Support for multiple sensors with weighted averaging
- Input validation and edge-case handling
- Haversine distance calculation for geographic accuracy
- Modular interpolator interface for extensibility
- Confidence assessment based on sensor proximity
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from math import radians, sin, cos, sqrt, atan2
import logging


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class GeoPoint:
    """Geographic point with latitude and longitude."""
    latitude: float
    longitude: float
    
    def __post_init__(self):
        """Validate geographic coordinates."""
        if not isinstance(self.latitude, (int, float)):
            raise TypeError("Latitude must be numeric")
        if not isinstance(self.longitude, (int, float)):
            raise TypeError("Longitude must be numeric")
        
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")


@dataclass
class Sensor(GeoPoint):
    """Sensor location with AQI measurement."""
    aqi_value: float
    sensor_id: Optional[str] = None
    measurement_time: Optional[str] = None
    
    def __post_init__(self):
        """Validate sensor data."""
        super().__post_init__()
        
        if not isinstance(self.aqi_value, (int, float)):
            raise TypeError("AQI value must be numeric")
        
        if self.aqi_value < 0:
            raise ValueError(f"AQI value must be non-negative, got {self.aqi_value}")
        
        # AQI values can exceed 500 for hazardous conditions
        # but cap extremely high values as potential errors
        if self.aqi_value > 5000:
            logger.warning(f"Sensor {self.sensor_id} has unusually high AQI: {self.aqi_value}")


@dataclass
class InterpolationResult:
    """Result of spatial interpolation."""
    estimated_aqi: float
    confidence: float  # 0.0 to 1.0, based on sensor proximity
    sensors_used: int
    nearest_sensor_distance_km: float
    interpolation_method: str
    
    def __post_init__(self):
        """Validate result data."""
        if not 0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        if self.estimated_aqi < 0:
            raise ValueError(f"Estimated AQI must be non-negative, got {self.estimated_aqi}")
        if self.sensors_used < 1:
            raise ValueError(f"Sensors used must be at least 1, got {self.sensors_used}")


class SpatialInterpolator(ABC):
    """
    Abstract base class for spatial interpolation methods.
    
    Defines the interface for different interpolation algorithms,
    allowing for extensibility (e.g., Kriging, Spline, etc.).
    """
    
    @abstractmethod
    def interpolate(
        self,
        sensors: List[Sensor],
        target: GeoPoint
    ) -> InterpolationResult:
        """
        Estimate AQI at target location using sensors.
        
        Args:
            sensors: List of sensor measurements
            target: Target location for estimation
        
        Returns:
            InterpolationResult with estimated AQI and metadata
        
        Raises:
            ValueError: If inputs are invalid
        """
        pass


class IDWInterpolator(SpatialInterpolator):
    """
    Inverse Distance Weighting (IDW) spatial interpolation.
    
    IDW is a simple but effective method that estimates values at a target
    location based on nearby measurements, with weights inversely proportional
    to distance. Closer sensors have more influence.
    
    Mathematical Formula:
        AQI(target) = Σ(w_i * AQI_i) / Σ(w_i)
        where w_i = 1 / (d_i ^ p)
        d_i = distance from target to sensor i
        p = power parameter (exponent)
    """
    
    def __init__(
        self,
        power: float = 2.0,
        min_sensors: int = 1,
        max_sensors: Optional[int] = None,
        max_distance_km: Optional[float] = None
    ):
        """
        Initialize IDW interpolator.
        
        Args:
            power: Exponent for distance weighting. Higher values give more weight
                   to nearby sensors. Default 2.0 (inverse square distance).
                   - 1.0: inverse distance (linear)
                   - 2.0: inverse square distance (common choice)
                   - 3.0+: more localized weighting
            min_sensors: Minimum number of sensors required. Default 1.
            max_sensors: Maximum number of sensors to use. If more sensors are
                        available, use the closest ones. Default None (use all).
            max_distance_km: Maximum distance in km to consider a sensor.
                            Sensors beyond this distance are ignored.
                            Default None (no limit).
        
        Raises:
            ValueError: If parameters are invalid
        """
        if power <= 0:
            raise ValueError(f"Power must be positive, got {power}")
        if min_sensors < 1:
            raise ValueError(f"Minimum sensors must be at least 1, got {min_sensors}")
        if max_sensors is not None and max_sensors < min_sensors:
            raise ValueError(f"Max sensors ({max_sensors}) must be >= min sensors ({min_sensors})")
        if max_distance_km is not None and max_distance_km <= 0:
            raise ValueError(f"Max distance must be positive, got {max_distance_km}")
        
        self.power = power
        self.min_sensors = min_sensors
        self.max_sensors = max_sensors
        self.max_distance_km = max_distance_km
        
        logger.debug(
            f"IDW Interpolator initialized: power={power}, min_sensors={min_sensors}, "
            f"max_sensors={max_sensors}, max_distance_km={max_distance_km}"
        )
    
    @staticmethod
    def haversine_distance(
        point1: GeoPoint,
        point2: GeoPoint
    ) -> float:
        """
        Calculate great-circle distance between two geographic points.
        
        Uses the Haversine formula for accuracy over large distances.
        More accurate than simple Euclidean distance for lat/lon coordinates.
        
        Args:
            point1: First geographic point
            point2: Second geographic point
        
        Returns:
            Distance in kilometers
        """
        # Earth's radius in km
        R = 6371.0
        
        # Convert to radians
        lat1, lon1 = radians(point1.latitude), radians(point1.longitude)
        lat2, lon2 = radians(point2.latitude), radians(point2.longitude)
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def interpolate(
        self,
        sensors: List[Sensor],
        target: GeoPoint
    ) -> InterpolationResult:
        """
        Estimate AQI at target location using IDW.
        
        Args:
            sensors: List of sensor measurements with locations
            target: Target location for AQI estimation
        
        Returns:
            InterpolationResult with estimated AQI, confidence, and metadata
        
        Raises:
            ValueError: If insufficient sensors or invalid inputs
        """
        # Input validation
        if not sensors:
            raise ValueError("At least one sensor is required")
        
        if len(sensors) < self.min_sensors:
            raise ValueError(
                f"Insufficient sensors: {len(sensors)} < minimum {self.min_sensors}"
            )
        
        if not isinstance(target, GeoPoint):
            raise TypeError("Target must be a GeoPoint instance")
        
        logger.debug(f"Interpolating AQI for target ({target.latitude}, {target.longitude})")
        
        # Calculate distances and filter sensors
        sensor_distances = []
        for sensor in sensors:
            distance = self.haversine_distance(sensor, target)
            
            # Filter by max distance if specified
            if self.max_distance_km is not None and distance > self.max_distance_km:
                logger.debug(
                    f"Sensor {sensor.sensor_id} at {distance:.2f}km exceeds "
                    f"max distance {self.max_distance_km}km"
                )
                continue
            
            sensor_distances.append((sensor, distance))
        
        # Verify we have minimum sensors after filtering
        if len(sensor_distances) < self.min_sensors:
            raise ValueError(
                f"Insufficient sensors within max_distance: "
                f"{len(sensor_distances)} < minimum {self.min_sensors}"
            )
        
        # Sort by distance and limit to max_sensors if specified
        sensor_distances.sort(key=lambda x: x[1])
        
        if self.max_sensors is not None:
            sensor_distances = sensor_distances[:self.max_sensors]
        
        # Handle edge case: target is exactly at sensor location
        if sensor_distances[0][1] < 1e-6:  # Less than 1mm
            logger.debug("Target is at exact sensor location, using sensor value")
            return InterpolationResult(
                estimated_aqi=sensor_distances[0][0].aqi_value,
                confidence=1.0,
                sensors_used=1,
                nearest_sensor_distance_km=0.0,
                interpolation_method="IDW (exact location)"
            )
        
        # Calculate IDW weights
        weights = []
        weighted_aqi_sum = 0.0
        weight_sum = 0.0
        
        for sensor, distance in sensor_distances:
            # Weight is inversely proportional to distance^power
            weight = 1.0 / (distance ** self.power)
            weights.append(weight)
            weighted_aqi_sum += weight * sensor.aqi_value
            weight_sum += weight
        
        # Calculate estimated AQI
        estimated_aqi = weighted_aqi_sum / weight_sum
        
        # Calculate confidence based on sensor proximity
        # Confidence is higher when sensors are closer
        nearest_distance = sensor_distances[0][1]
        confidence = self._calculate_confidence(nearest_distance)
        
        logger.debug(
            f"IDW interpolation complete: AQI={estimated_aqi:.1f}, "
            f"confidence={confidence:.2f}, sensors_used={len(sensor_distances)}, "
            f"nearest_distance={nearest_distance:.2f}km"
        )
        
        return InterpolationResult(
            estimated_aqi=estimated_aqi,
            confidence=confidence,
            sensors_used=len(sensor_distances),
            nearest_sensor_distance_km=nearest_distance,
            interpolation_method=f"IDW (power={self.power})"
        )
    
    def _calculate_confidence(self, nearest_distance_km: float) -> float:
        """
        Calculate confidence score based on distance to nearest sensor.
        
        Confidence is high when sensors are nearby, decreases with distance.
        Uses a sigmoid-like function for smooth degradation.
        
        Args:
            nearest_distance_km: Distance to nearest sensor in km
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Tuning parameters for confidence calculation
        # Adjust these based on typical sensor spacing
        optimal_distance = 1.0  # 1 km is considered optimal
        half_confidence_distance = 5.0  # 5 km gives 50% confidence
        
        if nearest_distance_km <= optimal_distance:
            return 1.0
        
        # Smooth decline in confidence with distance
        # Using formula: confidence = 1 / (1 + (d / d_half)^2)
        ratio = nearest_distance_km / half_confidence_distance
        confidence = 1.0 / (1.0 + ratio ** 2)
        
        return max(0.1, min(1.0, confidence))  # Clamp to [0.1, 1.0]


class SpatialInterpolationService:
    """
    High-level service for spatial AQI interpolation.
    
    Provides a convenient interface for estimating AQI at arbitrary
    locations based on sensor measurements. Supports multiple interpolation
    methods through pluggable interpolators.
    """
    
    def __init__(self, interpolator: Optional[SpatialInterpolator] = None):
        """
        Initialize the spatial interpolation service.
        
        Args:
            interpolator: Interpolation method instance. Defaults to IDWInterpolator
                         with default parameters if not provided.
        """
        self.interpolator = interpolator or IDWInterpolator()
        logger.info(f"Spatial interpolation service initialized with {type(self.interpolator).__name__}")
    
    def estimate_aqi(
        self,
        sensors: List[Sensor],
        latitude: float,
        longitude: float
    ) -> InterpolationResult:
        """
        Estimate AQI at a target location.
        
        Args:
            sensors: List of sensor measurements
            latitude: Target latitude
            longitude: Target longitude
        
        Returns:
            InterpolationResult with estimated AQI and metadata
        
        Raises:
            ValueError: If inputs are invalid
            TypeError: If inputs have wrong type
        """
        try:
            target = GeoPoint(latitude=latitude, longitude=longitude)
            return self.interpolator.interpolate(sensors, target)
        except (TypeError, ValueError) as e:
            logger.error(f"Estimation error: {e}")
            raise
    
    def estimate_aqi_from_dicts(
        self,
        sensors: List[dict],
        latitude: float,
        longitude: float
    ) -> InterpolationResult:
        """
        Estimate AQI using dictionary-based sensor data.
        
        Convenient method for API integration where sensors may be
        represented as dictionaries from database queries or JSON.
        
        Args:
            sensors: List of dicts with keys: latitude, longitude, aqi_value,
                    and optional keys: sensor_id, measurement_time
            latitude: Target latitude
            longitude: Target longitude
        
        Returns:
            InterpolationResult with estimated AQI and metadata
        
        Raises:
            ValueError: If sensor dicts are missing required fields
            TypeError: If fields have wrong types
        """
        sensor_objects = []
        
        for i, sensor_dict in enumerate(sensors):
            try:
                required_keys = {'latitude', 'longitude', 'aqi_value'}
                if not required_keys.issubset(sensor_dict.keys()):
                    missing = required_keys - sensor_dict.keys()
                    raise ValueError(f"Sensor {i} missing required keys: {missing}")
                
                sensor = Sensor(
                    latitude=sensor_dict['latitude'],
                    longitude=sensor_dict['longitude'],
                    aqi_value=sensor_dict['aqi_value'],
                    sensor_id=sensor_dict.get('sensor_id'),
                    measurement_time=sensor_dict.get('measurement_time')
                )
                sensor_objects.append(sensor)
            except (TypeError, ValueError, KeyError) as e:
                logger.error(f"Invalid sensor data at index {i}: {e}")
                raise ValueError(f"Invalid sensor data at index {i}: {e}")
        
        return self.estimate_aqi(sensor_objects, latitude, longitude)
    
    def batch_estimate(
        self,
        sensors: List[Sensor],
        targets: List[Tuple[float, float]]
    ) -> List[InterpolationResult]:
        """
        Estimate AQI at multiple target locations.
        
        Efficient batch processing for multiple locations.
        
        Args:
            sensors: List of sensor measurements
            targets: List of (latitude, longitude) tuples
        
        Returns:
            List of InterpolationResult objects
        
        Raises:
            ValueError: If inputs are invalid
        """
        results = []
        
        for latitude, longitude in targets:
            try:
                result = self.estimate_aqi(sensors, latitude, longitude)
                results.append(result)
            except (TypeError, ValueError) as e:
                logger.error(f"Failed to estimate AQI at ({latitude}, {longitude}): {e}")
                raise
        
        return results
    
    def set_interpolator(self, interpolator: SpatialInterpolator):
        """
        Change the interpolation method.
        
        Allows switching between different interpolation algorithms
        at runtime.
        
        Args:
            interpolator: New interpolation method instance
        """
        if not isinstance(interpolator, SpatialInterpolator):
            raise TypeError("Interpolator must be a SpatialInterpolator instance")
        
        self.interpolator = interpolator
        logger.info(f"Interpolation method changed to {type(interpolator).__name__}")


# Convenience factory function
def create_spatial_interpolation_service(
    power: float = 2.0,
    min_sensors: int = 1,
    max_sensors: Optional[int] = None,
    max_distance_km: Optional[float] = None
) -> SpatialInterpolationService:
    """
    Create a spatial interpolation service with IDW method.
    
    Convenience function for common use case of creating service with
    IDW interpolator and custom parameters.
    
    Args:
        power: IDW power parameter
        min_sensors: Minimum sensors required
        max_sensors: Maximum sensors to use
        max_distance_km: Maximum distance to consider a sensor
    
    Returns:
        Configured SpatialInterpolationService instance
    """
    interpolator = IDWInterpolator(
        power=power,
        min_sensors=min_sensors,
        max_sensors=max_sensors,
        max_distance_km=max_distance_km
    )
    return SpatialInterpolationService(interpolator=interpolator)
