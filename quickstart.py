"""
Quick Start Script for AeroGuard

This script demonstrates how to:
1. Train a forecasting model
2. Save the trained model
3. Generate forecasts
4. Get model status
"""

import numpy as np
import json
from app import create_app
from app.models.forecast_model import ForecastModel
from app.services.forecasting_service import ForecastingService
from app.services.data_service import DataService


def generate_sample_data(n_samples=100, n_features=10):
    """
    Generate sample training data.
    
    Args:
        n_samples: Number of samples
        n_features: Number of features
        
    Returns:
        Tuple of (X, y_dict)
    """
    np.random.seed(42)
    
    # Feature matrix
    X = np.random.normal(loc=50, scale=20, size=(n_samples, n_features))
    X = np.clip(X, 0, 500)
    
    # Target variables
    y_dict = {
        "pm25": np.random.uniform(10, 100, n_samples),
        "pm10": np.random.uniform(20, 150, n_samples),
        "no2": np.random.uniform(5, 50, n_samples),
        "o3": np.random.uniform(10, 80, n_samples),
        "so2": np.random.uniform(0, 30, n_samples),
        "co": np.random.uniform(0.1, 5, n_samples),
    }
    
    return X, y_dict


def main():
    """Run quick start demonstration."""
    
    print("=" * 60)
    print("AeroGuard - Quick Start Demo")
    print("=" * 60)
    
    # 1. Create Flask app
    print("\n1. Creating Flask application...")
    app = create_app()
    
    # 2. Initialize model and services
    print("2. Initializing models and services...")
    model = ForecastModel(model_type="ensemble")
    forecast_service = ForecastingService(model)
    data_service = DataService()
    
    # 3. Generate and train on sample data
    print("3. Generating sample training data...")
    X, y_dict = generate_sample_data(n_samples=100, n_features=10)
    print(f"   - Features shape: {X.shape}")
    print(f"   - Parameters: {list(y_dict.keys())}")
    
    print("4. Training ensemble model...")
    metrics = model.train(X, y_dict)
    print("   Training complete!")
    print("   Metrics (R² scores):")
    for param, score in metrics.items():
        print(f"     - {param}: {score:.4f}")
    
    # 5. Make predictions
    print("\n5. Making predictions...")
    test_X = X[:10]  # Use first 10 samples
    predictions = model.predict(test_X, parameter="pm25")
    print(f"   - PM2.5 predictions: {predictions[:3]}")
    
    # 6. Generate forecast
    print("\n6. Generating air quality forecast...")
    forecast = forecast_service.generate_forecast(
        location_id="demo_location",
        days_ahead=7,
        historical_data=X
    )
    print(f"   - Location: {forecast['location_id']}")
    print(f"   - Days ahead: {forecast['days_ahead']}")
    print(f"   - Parameters forecasted: {list(forecast['forecasts'].keys())}")
    
    # Display sample forecast
    pm25_forecast = forecast['forecasts']['pm25']
    if pm25_forecast['status'] == 'success':
        print("\n   PM2.5 Forecast Sample:")
        for pred in pm25_forecast['predictions'][:2]:
            print(f"     - {pred['date']}: {pred['value']} µg/m³ (confidence: {pred['confidence']:.2f})")
    
    # 7. Get feature importance
    print("\n7. Feature Importance Analysis...")
    importance = model.get_feature_importance("pm25")
    if importance:
        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3]
        print("   Top 3 Important Features (PM2.5):")
        for feat, score in top_features:
            print(f"     - {feat}: {score:.4f}")
    
    # 8. Model status
    print("\n8. Model Status:")
    print(f"   - Is trained: {model.is_trained}")
    print(f"   - Model type: {model.model_type}")
    print(f"   - Parameters trained for: {list(model.models.keys())}")
    
    # 9. Get location metadata
    print("\n9. Location Metadata:")
    metadata = data_service.get_location_metadata("demo_location")
    print(f"   - Location ID: {metadata['location_id']}")
    print(f"   - Name: {metadata['name']}")
    print(f"   - Country: {metadata['country']}")
    
    # 10. Save model
    print("\n10. Saving trained model...")
    try:
        model.save("models/demo_model_v1")
        print("    Model saved successfully!")
    except Exception as e:
        print(f"    Error saving model: {e}")
    
    print("\n" + "=" * 60)
    print("✓ Quick start demo completed successfully!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  1. Run the Flask app: python run.py")
    print("  2. Try the forecast API: http://localhost:5000/api/v1/forecast")
    print("  3. Check model status: http://localhost:5000/api/v1/model/status")
    print("  4. Read full documentation: README.md")


if __name__ == "__main__":
    main()
