# Database Setup Guide - NeonDB PostgreSQL

## Overview

AeroGuard uses SQLAlchemy ORM with PostgreSQL (via NeonDB) for production and SQLite for development. This guide covers setting up and managing the database.

## Quick Start

### 1. Get NeonDB Credentials

1. Go to [NeonDB Console](https://console.neon.tech)
2. Create a new project
3. Copy the connection string (looks like: `postgresql://user:password@host.neon.tech/database`)
4. Save it for step 2

### 2. Configure Database

Update your `.env` file:

```env
# Development (SQLite - no setup needed)
DATABASE_URL=sqlite:///aeroguard.db

# Production (NeonDB PostgreSQL)
DATABASE_URL=postgresql://username:password@ep-cool-wave-12345.us-east-1.neon.tech/aeroguard_db
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
# Create tables
python init_db.py

# Create tables + seed sample data
python init_db.py --seed

# Drop all tables (careful!)
python init_db.py --drop
```

## Database Schema

### Core Tables

#### `users`
- User accounts and authentication
- Fields: id, email, username, full_name, password_hash, is_active, created_at, updated_at

#### `locations`
- Geographic locations with air quality monitoring
- Fields: id, city, country, latitude, longitude, location_id, is_active, created_at, updated_at
- Indexes: city+country, latitude+longitude

#### `sensors`
- Air quality sensor metadata and locations
- Fields: id, location_id, sensor_id, sensor_name, latitude, longitude, sensor_type, provider, is_active, last_update

#### `aqi_data`
- Hourly air quality measurements (time-series data)
- Fields: id, location_id, timestamp, pm25, pm10, no2, o3, so2, co, aqi, temperature, humidity, wind_speed, wind_direction, is_valid, data_source
- Indexes: location_id+timestamp (for efficient time-series queries)

#### `forecasts`
- Stored forecast predictions for history and model improvement
- Fields: id, location_id, forecast_time, forecast_date, model_type, horizon_hours, aqi_forecast, pm25_forecast, pm10_forecast, confidence, actual_aqi, mae, rmse, is_accurate
- Indexes: location_id+forecast_date

#### `user_locations`
- User's favorite and monitored locations
- Fields: id, user_id, location_id, is_favorite, alert_threshold_aqi, added_at
- Unique constraint: user_id+location_id

#### `user_preferences`
- User preferences for notifications and personalization
- Fields: id, user_id, persona, health_conditions, age_group, enable_alerts, alert_threshold_aqi, notification_method, preferred_forecast_hours, preferred_pollutants, language, temperature_unit, explanation_style

#### `model_metrics`
- Historical model performance tracking
- Fields: id, model_type, location_id, evaluation_date, mae, rmse, mape, r2_score, samples_count, forecast_hours, training_data_days
- Indexes: model_type+evaluation_date

### Relationships

```
User ──┬─→ UserLocation ─→ Location
       └─→ UserPreference

Location ──┬─→ Sensor
           ├─→ AQIData
           ├─→ Forecast
           └─→ ModelMetrics
```

## Key Features

### Time-Series Optimization
- `aqi_data` has compound index on `(location_id, timestamp)` for efficient historical queries
- Perfect for time-series analysis and model training

### Forecast Tracking
- All forecasts stored with actual values for model validation
- Enables continuous model improvement and performance tracking
- Tracks confidence intervals and uncertainty metrics

### User Personalization
- User preferences including health profiles and personas
- Custom alert thresholds per location
- Support for multiple languages and units

### Model Monitoring
- Track model performance metrics over time
- Compare models (SARIMA vs XGBoost vs Ensemble)
- Location-specific model evaluation

## Common Queries

### Get Recent AQI Data for Location

```python
from app.models.database_models import AQIData
from datetime import datetime, timedelta

# Last 24 hours
recent_aqi = AQIData.query.filter(
    AQIData.location_id == location_id,
    AQIData.timestamp >= datetime.utcnow() - timedelta(hours=24)
).order_by(AQIData.timestamp.desc()).all()
```

### Get User's Favorite Locations

```python
from app.models.database_models import UserLocation, Location

user_locations = UserLocation.query.filter(
    UserLocation.user_id == user_id,
    UserLocation.is_favorite == True
).join(Location).all()
```

### Get Recent Forecasts with Accuracy

```python
from app.models.database_models import Forecast

forecasts = Forecast.query.filter(
    Forecast.location_id == location_id,
    Forecast.actual_aqi != None
).order_by(Forecast.forecast_time.desc()).limit(100).all()

# Calculate accuracy
accuracy_rate = sum(1 for f in forecasts if f.is_accurate) / len(forecasts)
```

### Get Model Performance Comparison

```python
from app.models.database_models import ModelMetrics
from datetime import datetime, timedelta

# Last 30 days
recent_metrics = ModelMetrics.query.filter(
    ModelMetrics.evaluation_date >= datetime.utcnow().date() - timedelta(days=30)
).all()

# Group by model
for model in ['sarima', 'xgboost', 'ensemble']:
    model_data = [m for m in recent_metrics if m.model_type == model]
    avg_rmse = sum(m.rmse for m in model_data) / len(model_data)
    print(f"{model}: avg RMSE = {avg_rmse:.2f}")
```

## Migration & Backup

### Export Data

```bash
# PostgreSQL export
pg_dump "postgresql://user:password@host.neon.tech/database" > backup.sql
```

### Restore Data

```bash
# PostgreSQL restore
psql "postgresql://user:password@host.neon.tech/database" < backup.sql
```

## Monitoring & Maintenance

### Connection Pool Settings

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 10,              # Number of connections to maintain
    "pool_recycle": 3600,          # Recycle connections after 1 hour
    "pool_pre_ping": True,         # Test connections before use
    "connect_args": {"connect_timeout": 10},
}
```

### Query Monitoring

```python
# Enable SQL logging in development
SQLALCHEMY_ECHO = True
```

## Troubleshooting

### Connection Error

```
Error: could not translate host name "ep-..." to address
```

**Solution**: Check your DATABASE_URL is correct and you have internet access

### Table Already Exists

```
Error: relation "users" already exists
```

**Solution**: Drop tables first with `python init_db.py --drop` then recreate

### Timeout During Long Queries

**Solution**: Increase `pool_pre_ping` timeout or optimize queries with proper indexes

## Best Practices

1. **Always back up before major changes**
2. **Use indexes for frequently queried columns**
3. **Monitor query performance**
4. **Clean up old forecast data periodically**
5. **Use transactions for multi-table operations**
6. **Test schema changes on development first**

## Next Steps

1. ✅ Initialize database: `python init_db.py --seed`
2. ✅ Start backend: `python run.py`
3. ✅ Verify tables: Check NeonDB dashboard
4. ✅ Test API: Run forecasts and save to database

## Resources

- [NeonDB Documentation](https://neon.tech/docs)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/en/20/orm/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Flask-SQLAlchemy Guide](https://flask-sqlalchemy.palletsprojects.com/)
