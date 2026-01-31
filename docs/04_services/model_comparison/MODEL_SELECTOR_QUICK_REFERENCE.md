# Model Comparison Quick Reference

## Import
```python
from app.services.model_selector import ModelComparator, ModelSelector
from app.models.sarima_model import SARIMAModel
from app.models.xgboost_model import XGBoostModel
```

## Quick Comparison (Fastest)
```python
selector = ModelSelector({
    "SARIMA": SARIMAModel(),
    "XGBoost": XGBoostModel()
})

result = selector.select_best(df)
print(f"Winner: {result['best_model']}")
```

## Detailed Analysis
```python
comparator = ModelComparator()
comparator.add_model("SARIMA", SARIMAModel())
comparator.add_model("XGBoost", XGBoostModel())

comparator.train_and_compare(df, target_col="PM2.5", forecast_steps=6)
comparator.print_report()
```

## Access Results
```python
# Get best model name
best = comparator.get_best_model_name()  # "XGBoost"

# Get predictions from best model
forecasts = comparator.get_best_model_predictions()  # [45.2, 46.1, 47.3, ...]

# Get all metrics
metrics = comparator.get_metrics_summary()
# {
#     "SARIMA": {"MAE": 1.23, "RMSE": 2.45, "sample_count": 50},
#     "XGBoost": {"MAE": 0.98, "RMSE": 1.67, "sample_count": 50}
# }

# Get detailed report
report = comparator.get_comparison_report()
```

## Compare Different Targets
```python
selector = ModelSelector()
selector.add_model("SARIMA", SARIMAModel())
selector.add_model("XGBoost", XGBoostModel())

for target in ["PM2.5", "PM10", "NO2"]:
    result = selector.select_best(df, target_col=target)
    print(f"{target}: {result['best_model']} wins")
```

## Compare Across Horizons
```python
for steps in [6, 12, 24]:
    result = selector.select_best(df, forecast_steps=steps)
    print(f"{steps}h forecast: {result['best_model']}")
```

## Compare More Models
```python
from app.models.custom_model import CustomModel

comparator = ModelComparator()
comparator.add_model("SARIMA", SARIMAModel())
comparator.add_model("XGBoost", XGBoostModel())
comparator.add_model("Custom", CustomModel())

result = comparator.train_and_compare(df)
# Automatically compares all 3 models
```

## Metrics Explained
- **MAE**: Average absolute error (lower = better)
- **RMSE**: Root mean squared error (lower = better)
- **Percentage Difference**: How much worse vs best model

## Error Handling
```python
try:
    result = comparator.train_and_compare(df)
except ValueError as e:
    print(f"Error: {e}")
    # No models registered
    # Target column not found
    # Insufficient data
    # Test set too small
```

## Configuration
```python
# Custom train/test split
result = comparator.train_and_compare(df, test_size=0.3)  # 70/30 split

# Different forecast horizon
result = comparator.train_and_compare(df, forecast_steps=12)

# Custom target column
result = comparator.train_and_compare(df, target_col="PM10")

# All together
result = comparator.train_and_compare(
    df,
    target_col="PM2.5",
    test_size=0.2,
    forecast_steps=6
)
```

## Reset for New Comparison
```python
comparator.reset()  # Clear all results
```

## Full Example
```python
import pandas as pd
from app.services.model_selector import ModelComparator
from app.models.sarima_model import SARIMAModel
from app.models.xgboost_model import XGBoostModel

# Load data
df = pd.read_csv("data/aqi_data.csv", parse_dates=["date"], index_col="date")

# Create comparator
comparator = ModelComparator()
comparator.add_model("SARIMA", SARIMAModel())
comparator.add_model("XGBoost", XGBoostModel())

# Run comparison
result = comparator.train_and_compare(df, target_col="PM2.5", forecast_steps=6)

# Print results
comparator.print_report()

# Access programmatically
print(f"Best Model: {comparator.get_best_model_name()}")
metrics = comparator.get_metrics_summary()
for model, m in metrics.items():
    print(f"{model}: MAE={m['MAE']:.4f}, RMSE={m['RMSE']:.4f}")

# Get forecasts
best_predictions = comparator.get_best_model_predictions()
print(f"Forecast from {comparator.get_best_model_name()}: {best_predictions}")
```

## See Also
- [Model Comparison Documentation](MODEL_SELECTOR.md)
- [Usage Examples](../examples/model_comparison_example.py)
- [Full API Reference](../tests/test_model_selector.py)
