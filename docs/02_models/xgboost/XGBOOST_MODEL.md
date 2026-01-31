# XGBoost Time-Series Forecasting Model

## Overview

The XGBoost model in AeroGuard provides short-term (6-hour default) air quality forecasting using gradient boosting regression. It's particularly effective for capturing non-linear patterns in air quality data with lag-based and rolling window features.

**Model Type:** `xgboost`  
**Default Forecast Horizon:** 6 hours  
**Minimum Training Data:** 10 samples  
**Data Frequency:** Hourly

## Features

### Feature Engineering

XGBoost uses automatically engineered features from the preprocessed time-series data:

#### Lag Features
- **Lag Hours:** [1h, 3h, 6h]  
- **Purpose:** Captures recent history and hourly patterns
- **Column Naming:** `{target}_lag_{hours}h` (e.g., `PM2.5_lag_1h`)

#### Rolling Statistics
- **Windows:** [3h, 6h]
- **Metrics:** Mean and standard deviation
- **Purpose:** Captures local trends and volatility
- **Column Naming:** `{target}_mean_{window}h`, `{target}_std_{window}h`

### Hyperparameters

```python
n_estimators = 100       # Number of boosting rounds
max_depth = 6            # Maximum tree depth
learning_rate = 0.1      # Step size shrinkage
random_state = 42        # Reproducibility
```

## Usage

### Training

```python
from app.services.forecasting_service import ForecastingService
from app.utils.timeseries_preprocessor import TimeSeriesPreprocessor
import pandas as pd

# Load and preprocess data
preprocessor = TimeSeriesPreprocessor()
df = preprocessor.load_and_preprocess_pm25('data/air_quality.csv')

# Initialize service with XGBoost model
service = ForecastingService(model_type="xgboost")

# Train model
metrics = service.train_xgboost(
    df,
    target_col="PM2.5",
    split_ratio=0.8  # 80% train, 20% test
)

print(f"Test MAE: {metrics['test_mae']:.2f}")
print(f"Test RMSE: {metrics['test_rmse']:.2f}")
```

### Prediction

```python
# Generate forecast for specified location
forecast = service.generate_xgboost_forecast(
    location_id="Beijing_Chaoyang",
    days_ahead=7  # Forecast 7 days (168 hours)
)

# Access predictions
pm25_forecast = forecast['forecasts']['pm25']
for pred in pm25_forecast['predictions']:
    print(f"{pred['date']}: {pred['value']} µg/m³ (confidence: {pred['confidence']:.2f})")
```

## Model Architecture

### Training Process

```python
def train(df: pd.DataFrame, split_ratio: float = 0.8) -> Dict[str, float]:
    """
    1. Extract feature columns (lag + rolling stats)
    2. Remove rows with missing values
    3. Split into train/test sets (default 80/20)
    4. Initialize XGBoost regressor with hyperparameters
    5. Fit model on training data
    6. Evaluate on test set
    7. Return MAE, RMSE for train and test sets
    """
```

### Prediction Process

```python
def predict(X: pd.DataFrame, steps: int = 6, iterative: bool = True) -> List[float]:
    """
    1. Start with initial feature vector X
    2. For each step (up to 'steps'):
        a. Predict next value using current features
        b. Update lag features with new prediction
        c. Recalculate rolling statistics
        d. Store prediction
    3. Return list of multi-step predictions
    """
```

## Comparison with Other Models

| Aspect | XGBoost | SARIMA | Ensemble |
|--------|---------|--------|----------|
| **Seasonality** | Manual features | Automatic | Not explicit |
| **Non-linearity** | Strong | Weak | Strong |
| **Cold start** | OK (10+ samples) | OK (50+ samples) | Moderate |
| **Interpretability** | Medium | High | Low |
| **Training speed** | Fast | Slow | Fast |
| **Multi-step** | Iterative | Direct | Direct |
| **Hyperparameter tuning** | Easy | Hard | Medium |

## Performance Characteristics

### Strengths
- Captures non-linear relationships in air quality
- Fast training and inference
- Works well with engineered features (lags, rolling stats)
- Provides feature importance insights
- Handles missing values gracefully with NaN removal

### Limitations
- Requires extensive feature engineering
- May overfit without proper regularization
- Iterative forecasting can accumulate errors over long horizons
- Assumes stationary patterns (may drift with seasonal changes)

## Configuration

### Default Configuration

```python
XGBoostModel(
    target_col="PM2.5",
    lag_hours=[1, 3, 6],
    rolling_windows=[3, 6],
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1
)
```

### Custom Configuration

```python
from app.models.xgboost_model import XGBoostModel

# Create with custom hyperparameters
model = XGBoostModel(
    target_col="PM10",
    lag_hours=[1, 2, 6, 12, 24],  # Include daily pattern
    rolling_windows=[3, 6, 24],     # Longer windows
    n_estimators=200,               # More trees
    max_depth=8,                    # Deeper trees
    learning_rate=0.05              # Slower learning
)
```

## Example: Complete Workflow

```python
from app.services.forecasting_service import ForecastingService
from app.utils.timeseries_preprocessor import TimeSeriesPreprocessor

# Step 1: Load and preprocess data
preprocessor = TimeSeriesPreprocessor()
df = preprocessor.load_and_preprocess_pm25('data/pm25_hourly.csv')

# Step 2: Create service
service = ForecastingService(model_type="xgboost")

# Step 3: Train model
metrics = service.train_xgboost(df, split_ratio=0.8)
print(f"Model trained. Test MAE: {metrics['test_mae']:.2f} µg/m³")

# Step 4: Generate forecast
forecast = service.generate_xgboost_forecast(
    location_id="Site_A",
    days_ahead=3
)

# Step 5: Access results
for param, param_forecast in forecast['forecasts'].items():
    print(f"\n{param.upper()} Forecast:")
    if param_forecast['status'] == 'success':
        for pred in param_forecast['predictions']:
            print(f"  {pred['date']}: {pred['value']} ({pred['confidence']:.2%} confidence)")
    else:
        print(f"  Error: {param_forecast['message']}")

# Step 6: Save model for later use
service.xgboost_model.save('models/xgboost_pm25.pkl')

# Step 7: Load and retrain with new data
loaded_model = XGBoostModel.load('models/xgboost_pm25.pkl')
new_metrics = loaded_model.retrain(new_df, keep_weights=True)
print(f"Model retrained. New test MAE: {new_metrics['test_mae']:.2f}")
```

## API Integration

### Training Endpoint
```
POST /api/v1/forecast/xgboost/train
Content-Type: application/json

{
    "data": [preprocessed DataFrame as dict],
    "target_col": "PM2.5",
    "split_ratio": 0.8
}

Response: {
    "status": "success",
    "metrics": {
        "train_mae": 1.23,
        "train_rmse": 2.45,
        "test_mae": 1.45,
        "test_rmse": 2.78
    }
}
```

### Prediction Endpoint
```
POST /api/v1/forecast/xgboost/predict
Content-Type: application/json

{
    "location_id": "Beijing_Chaoyang",
    "days_ahead": 7
}

Response: {
    "location_id": "Beijing_Chaoyang",
    "forecast_date": "2024-01-15T10:30:00Z",
    "model_type": "xgboost",
    "days_ahead": 7,
    "forecasts": {
        "pm25": {
            "status": "success",
            "parameter": "pm25",
            "predictions": [
                {
                    "date": "2024-01-16",
                    "value": 45.67,
                    "confidence": 0.85
                },
                ...
            ]
        },
        ...
    }
}
```

## Troubleshooting

### Error: "Missing feature columns"
**Cause:** Input DataFrame doesn't have required lag/rolling features  
**Solution:** Use `TimeSeriesPreprocessor` to create features:
```python
preprocessor = TimeSeriesPreprocessor()
df = preprocessor.preprocess(df)
```

### Error: "Not enough valid samples"
**Cause:** After removing NaN, fewer than 10 samples remain  
**Solution:** Increase input data size or reduce lag_hours/rolling_windows

### Error: "X must be a pandas DataFrame"
**Cause:** Predict method received None instead of DataFrame  
**Solution:** Ensure data is properly formatted:
```python
X = pd.DataFrame(features)  # Convert to DataFrame
preds = model.predict(X, steps=6)
```

### Poor Forecast Performance
**Cause:** Model may be underfitting or overfitting  
**Solutions:**
- Increase/decrease `max_depth` (control complexity)
- Adjust `learning_rate` (control training speed)
- Add more/fewer lag features
- Collect more training data

## References

- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Gradient Boosting for Time Series](https://arxiv.org/abs/2302.12784)
- [AeroGuard TimeSeriesPreprocessor](./TIMESERIES_PREPROCESSING.md)
