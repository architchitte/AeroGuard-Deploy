"""
Database initialization and schema management

Script to initialize the database, create tables, and populate with initial data.

Usage:
    python init_db.py              # Initialize database
    python init_db.py --drop       # Drop all tables (be careful!)
    python init_db.py --seed       # Seed with example data
"""

import os
import sys
from pathlib import Path

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.database import db, init_db
from app.models.database_models import (
    User, Location, Sensor, AQIData, Forecast, 
    UserLocation, UserPreference, ModelMetrics, PersonaEnum
)
from datetime import datetime, timedelta
import click


def initialize_database(app):
    """Initialize database schema"""
    with app.app_context():
        print("\n" + "="*70)
        print("DATABASE INITIALIZATION")
        print("="*70)
        # Initialize database only if SQLAlchemy is not already registered
        # (create_app typically calls init_db). This avoids double-init
        # and the RuntimeError about multiple SQLAlchemy instances.
        if 'sqlalchemy' not in getattr(app, 'extensions', {}):
            init_db(app)
            print("✓ Database initialized via init_db")
        else:
            # Ensure tables exist
            from app.database import db
            db.create_all()
            print("✓ Database initialized (existing SQLAlchemy instance)")


def drop_all_tables(app):
    """Drop all tables (USE WITH CAUTION!)"""
    with app.app_context():
        print("\n" + "="*70)
        print("⚠️  DROPPING ALL TABLES")
        print("="*70)
        
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response.lower() == 'yes':
            db.drop_all()
            print("✓ All tables dropped")
        else:
            print("✗ Cancelled")


def seed_sample_data(app):
    """Populate database with sample data for testing"""
    with app.app_context():
        print("\n" + "="*70)
        print("SEEDING SAMPLE DATA")
        print("="*70)
        
        try:
            # Create sample users
            print("\nCreating sample users...")
            user1 = User(
                email="alice@example.com",
                username="alice",
                full_name="Alice Johnson"
            )
            user2 = User(
                email="bob@example.com",
                username="bob",
                full_name="Bob Smith"
            )
            db.session.add_all([user1, user2])
            db.session.commit()
            print(f"✓ Created {2} users")
            
            # Create sample locations
            print("\nCreating sample locations...")
            locations_data = [
                {
                    "city": "Delhi",
                    "country": "India",
                    "latitude": 28.7041,
                    "longitude": 77.1025,
                    "location_id": "delhi_central"
                },
                {
                    "city": "New York",
                    "country": "USA",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "location_id": "nyc_manhattan"
                },
                {
                    "city": "London",
                    "country": "UK",
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "location_id": "london_center"
                },
            ]
            
            locations = []
            for loc_data in locations_data:
                loc = Location(**loc_data)
                locations.append(loc)
                db.session.add(loc)
            db.session.commit()
            print(f"✓ Created {len(locations)} locations")
            
            # Create sample sensors
            print("\nCreating sample sensors...")
            for location in locations:
                sensor = Sensor(
                    location_id=location.id,
                    sensor_id=f"{location.location_id}_sensor_1",
                    sensor_name=f"AQI Monitor - {location.city}",
                    latitude=location.latitude,
                    longitude=location.longitude,
                    sensor_type="Multi",
                    provider="WAQI"
                )
                db.session.add(sensor)
            db.session.commit()
            print(f"✓ Created sensors for all locations")
            
            # Create sample AQI data (last 30 days)
            print("\nCreating sample AQI data...")
            aqi_count = 0
            for location in locations:
                for days_back in range(30):
                    for hour in range(0, 24, 6):  # 4 measurements per day
                        timestamp = datetime.utcnow() - timedelta(days=days_back, hours=hour)
                        aqi_data = AQIData(
                            location_id=location.id,
                            timestamp=timestamp,
                            pm25=40 + (days_back % 10) * 5,
                            pm10=60 + (days_back % 10) * 7,
                            aqi=50 + (days_back % 10) * 8,
                            temperature=20 + (hour // 6) * 5,
                            humidity=60 + (hour % 6) * 5,
                            wind_speed=2 + (hour % 4),
                            data_source="sample"
                        )
                        db.session.add(aqi_data)
                        aqi_count += 1
            db.session.commit()
            print(f"✓ Created {aqi_count} AQI data points")
            
            # Create sample forecasts
            print("\nCreating sample forecasts...")
            forecast_count = 0
            for location in locations:
                for model in ["sarima", "xgboost", "ensemble"]:
                    forecast = Forecast(
                        location_id=location.id,
                        forecast_time=datetime.utcnow(),
                        forecast_date=datetime.utcnow().date(),
                        model_type=model,
                        horizon_hours=6,
                        aqi_forecast=75.5,
                        pm25_forecast=42.3,
                        pm10_forecast=68.9,
                        confidence=0.85,
                        prediction_interval_lower=65.0,
                        prediction_interval_upper=86.0
                    )
                    db.session.add(forecast)
                    forecast_count += 1
            db.session.commit()
            print(f"✓ Created {forecast_count} forecasts")
            
            # Create user preferences
            print("\nCreating sample user preferences...")
            for user in [user1, user2]:
                pref = UserPreference(
                    user_id=user.id,
                    persona=PersonaEnum.GENERAL_PUBLIC,
                    alert_threshold_aqi=100,
                    preferred_forecast_hours=6,
                    preferred_pollutants="pm25,pm10,aqi"
                )
                db.session.add(pref)
            db.session.commit()
            print(f"✓ Created user preferences")
            
            # Create user locations
            print("\nCreating sample user locations...")
            for user in [user1, user2]:
                for location in locations[:2]:  # Favorite first 2 locations
                    user_loc = UserLocation(
                        user_id=user.id,
                        location_id=location.id,
                        is_favorite=True,
                        alert_threshold_aqi=100
                    )
                    db.session.add(user_loc)
            db.session.commit()
            print(f"✓ Created user location mappings")
            
            # Create model metrics
            print("\nCreating sample model metrics...")
            for location in locations:
                for model in ["sarima", "xgboost", "ensemble"]:
                    metrics = ModelMetrics(
                        model_type=model,
                        location_id=location.id,
                        evaluation_date=datetime.utcnow().date(),
                        mae=8.5,
                        rmse=10.2,
                        mape=0.12,
                        r2_score=0.88,
                        samples_count=720,
                        forecast_hours=6,
                        training_data_days=90
                    )
                    db.session.add(metrics)
            db.session.commit()
            print(f"✓ Created model metrics")
            
            print("\n" + "="*70)
            print("✓ Sample data seeded successfully!")
            print("="*70 + "\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error seeding data: {e}\n")
            raise


@click.command()
@click.option('--drop', is_flag=True, help='Drop all tables')
@click.option('--seed', is_flag=True, help='Seed with sample data')
def main(drop, seed):
    """Database initialization utility"""
    
    # Determine environment
    env = os.getenv("FLASK_ENV", "development")
    
    if env == "development":
        from app.config import DevelopmentConfig
        app = create_app(DevelopmentConfig)
    elif env == "testing":
        from app.config import TestingConfig
        app = create_app(TestingConfig)
    else:
        from app.config import ProductionConfig
        app = create_app(ProductionConfig)
    
    # Drop tables if requested
    if drop:
        drop_all_tables(app)
    
    # Initialize database
    initialize_database(app)
    
    # Seed sample data if requested
    if seed:
        seed_sample_data(app)
    
    if not seed:
        print("\n💡 Tip: Run with --seed flag to populate sample data")
        print("   Example: python init_db.py --seed\n")


if __name__ == "__main__":
    main()
