"""
Database Models for AeroGuard

Defines SQLAlchemy ORM models for:
- Users and authentication
- Locations and sensor networks
- Air quality measurements
- Historical forecasts
- User preferences
"""

from datetime import datetime
from app.database import db
from sqlalchemy import func, Index
import enum


class User(db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120))
    password_hash = db.Column(db.String(255))  # Store hashed passwords
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    locations = db.relationship('UserLocation', backref='user', lazy=True, cascade='all, delete-orphan')
    preferences = db.relationship('UserPreference', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Location(db.Model):
    """Geographic location with air quality monitoring"""
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_id = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Custom identifier
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sensors = db.relationship('Sensor', backref='location', lazy=True, cascade='all, delete-orphan')
    aqi_data = db.relationship('AQIData', backref='location', lazy=True, cascade='all, delete-orphan')
    forecasts = db.relationship('Forecast', backref='location', lazy=True, cascade='all, delete-orphan')
    user_locations = db.relationship('UserLocation', backref='location', lazy=True, cascade='all, delete-orphan')
    
    # Index for common queries
    __table_args__ = (
        Index('ix_location_city_country', 'city', 'country'),
        Index('ix_location_coords', 'latitude', 'longitude'),
    )
    
    def __repr__(self):
        return f'<Location {self.city}, {self.country}>'


class Sensor(db.Model):
    """Air quality sensor location and metadata"""
    __tablename__ = 'sensors'
    
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    sensor_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    sensor_name = db.Column(db.String(120))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    sensor_type = db.Column(db.String(50))  # e.g., "PM2.5", "PM10", "Multi"
    provider = db.Column(db.String(120))  # e.g., "WAQI", "IQAir", "AirVisual"
    is_active = db.Column(db.Boolean, default=True)
    last_update = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Sensor {self.sensor_id}>'


class AQIData(db.Model):
    """Hourly air quality measurements"""
    __tablename__ = 'aqi_data'
    
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    
    # Pollutants
    pm25 = db.Column(db.Float)  # Fine particulate matter (µg/m³)
    pm10 = db.Column(db.Float)  # Coarse particulate matter (µg/m³)
    no2 = db.Column(db.Float)   # Nitrogen dioxide (ppb)
    o3 = db.Column(db.Float)    # Ozone (ppb)
    so2 = db.Column(db.Float)   # Sulfur dioxide (ppb)
    co = db.Column(db.Float)    # Carbon monoxide (ppm)
    aqi = db.Column(db.Float)   # Air Quality Index
    
    # Environmental conditions
    temperature = db.Column(db.Float)  # Celsius
    humidity = db.Column(db.Float)     # Percentage
    wind_speed = db.Column(db.Float)   # m/s
    wind_direction = db.Column(db.Integer)  # Degrees
    
    # Data quality
    is_valid = db.Column(db.Boolean, default=True)
    data_source = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Index for time-series queries
    __table_args__ = (
        Index('ix_aqi_location_timestamp', 'location_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<AQIData {self.location_id} @ {self.timestamp}>'


class Forecast(db.Model):
    """Stored forecasts for historical reference and model improvement"""
    __tablename__ = 'forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    forecast_time = db.Column(db.DateTime, nullable=False)  # When forecast was generated
    forecast_date = db.Column(db.Date, nullable=False, index=True)
    
    # Forecast parameters
    model_type = db.Column(db.String(50), nullable=False)  # "sarima", "xgboost", "ensemble"
    horizon_hours = db.Column(db.Integer)  # How many hours ahead
    
    # Predictions
    aqi_forecast = db.Column(db.Float)
    pm25_forecast = db.Column(db.Float)
    pm10_forecast = db.Column(db.Float)
    
    # Confidence and uncertainty
    confidence = db.Column(db.Float)  # 0-1
    prediction_interval_lower = db.Column(db.Float)
    prediction_interval_upper = db.Column(db.Float)
    
    # Actual values (for evaluation)
    actual_aqi = db.Column(db.Float)
    actual_pm25 = db.Column(db.Float)
    actual_pm10 = db.Column(db.Float)
    actual_recorded_at = db.Column(db.DateTime)
    
    # Forecast accuracy
    mae = db.Column(db.Float)  # Mean Absolute Error
    rmse = db.Column(db.Float)  # Root Mean Squared Error
    is_accurate = db.Column(db.Boolean)  # Manual validation flag
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_forecast_location_date', 'location_id', 'forecast_date'),
    )
    
    def __repr__(self):
        return f'<Forecast {self.model_type} @ {self.forecast_time}>'


class UserLocation(db.Model):
    """User's favorite or monitored locations"""
    __tablename__ = 'user_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)
    alert_threshold_aqi = db.Column(db.Float)  # Alert when AQI exceeds this
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_user_location_unique', 'user_id', 'location_id', unique=True),
    )
    
    def __repr__(self):
        return f'<UserLocation user={self.user_id} location={self.location_id}>'


class PersonaEnum(enum.Enum):
    """User personas for personalized recommendations"""
    GENERAL_PUBLIC = "General Public"
    CHILDREN = "Children"
    ELDERLY = "Elderly"
    ATHLETES = "Athletes"
    OUTDOOR_WORKERS = "Outdoor Workers"
    SENSITIVE_GROUPS = "Sensitive Groups"


class UserPreference(db.Model):
    """User preferences for notifications and recommendations"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Health profile
    persona = db.Column(db.Enum(PersonaEnum), default=PersonaEnum.GENERAL_PUBLIC)
    health_conditions = db.Column(db.String(500))  # Comma-separated list
    age_group = db.Column(db.String(20))  # e.g., "0-5", "6-12", "13-18", "19-65", "65+"
    
    # Notification preferences
    enable_alerts = db.Column(db.Boolean, default=True)
    alert_threshold_aqi = db.Column(db.Float, default=100)  # Default unhealthy level
    notification_method = db.Column(db.String(50))  # "email", "push", "sms"
    
    # Forecast preferences
    preferred_forecast_hours = db.Column(db.Integer, default=6)  # Hours ahead
    preferred_pollutants = db.Column(db.String(200))  # Comma-separated: "pm25,pm10,aqi"
    
    # Language and units
    language = db.Column(db.String(10), default="en")
    temperature_unit = db.Column(db.String(1), default="C")  # C or F
    
    # Explanation style
    explanation_style = db.Column(db.String(50), default="casual")  # casual, technical, urgent
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPreference user={self.user_id} persona={self.persona}>'


class ModelMetrics(db.Model):
    """Track model performance metrics over time"""
    __tablename__ = 'model_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    model_type = db.Column(db.String(50), nullable=False)  # "sarima", "xgboost", "ensemble"
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    evaluation_date = db.Column(db.Date, nullable=False, index=True)
    
    # Performance metrics
    mae = db.Column(db.Float)   # Mean Absolute Error
    rmse = db.Column(db.Float)  # Root Mean Squared Error
    mape = db.Column(db.Float)  # Mean Absolute Percentage Error
    r2_score = db.Column(db.Float)  # R² score
    
    # Data points used
    samples_count = db.Column(db.Integer)
    forecast_hours = db.Column(db.Integer)  # Horizon evaluated
    
    # Metadata
    training_data_days = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_metrics_model_date', 'model_type', 'evaluation_date'),
    )
    
    def __repr__(self):
        return f'<ModelMetrics {self.model_type} @ {self.evaluation_date}>'


# Create indexes for common queries
def create_indexes():
    """Create additional indexes for performance"""
    pass  # Indexes are defined in __table_args__ above
