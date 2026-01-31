# Model Comparison & Selection Service (Judge Favorite ⭐)

## Overview

The Model Comparison Service provides an automated, extensible framework for comparing multiple forecasting models and selecting the best performer. It's designed to reduce decision paralysis by running all models simultaneously and returning clear metrics on which model performs best.

**Key Feature:** Modular and extensible design allows easy addition of new models without modifying the core comparison logic.

## Components

### 1. ModelComparator (Core Engine)

The main class for comparing models. Handles:
- Model registration
- Training and prediction
- Error metrics calculation (MAE, RMSE)
- Model selection
- Report generation

### 2. ModelSelector (Convenience Wrapper)

Simplified interface for common use cases. Provides:
- Easy initialization
- Clean API
- Direct model selection
- Result retrieval

## Quick Start

### Basic Comparison

```python
from app.services.model_selector import ModelSelector
from app.models.sarima_model import SARIMAModel
from app.models.xgboost_model import XGBoostModel

# Create selector
selector = ModelSelector()
selector.add_model("SARIMA", SARIMAModel())
selector.add_model("XGBoost", XGBoostModel())

# Run comparison
result = selector.select_best(df, target_col="PM2.5", forecast_steps=6)

# Access results
best_model = result['best_model']  # "SARIMA" or "XGBoost"
metrics = result['metrics']         # Error metrics for both
predictions = result['predictions'] # Forecasts from both
```

### Detailed Report

```python
from app.services.model_selector import ModelComparator

comparator = ModelComparator()
comparator.add_model("SARIMA", SARIMAModel())
comparator.add_model("XGBoost", XGBoostModel())

result = comparator.train_and_compare(df)

# Print formatted report
comparator.print_report()
```

## API Reference

### ModelComparator

#### Methods

##### `add_model(model_name: str, model: Any) -> None`
Register a model for comparison.

**Parameters:**
- `model_name`: Unique identifier (string)
- `model`: Model instance with `train()` and `predict()` methods

**Example:**
```python
comparator.add_model("MyModel", my_model_instance)
```

---

##### `train_and_compare(df: pd.DataFrame, target_col: str = "PM2.5", test_size: float = 0.2, forecast_steps: int = 6) -> Dict`
Train all models and compare performance.

**Parameters:**
- `df`: Historical data (DataFrame)
- `target_col`: Target column name
- `test_size`: Fraction for testing (0.0-1.0)
- `forecast_steps`: Steps to forecast

**Returns:**
```python
{
    "best_model": "XGBoost",
    "metrics": {
        "SARIMA": {"MAE": 1.23, "RMSE": 2.45},
        "XGBoost": {"MAE": 0.98, "RMSE": 1.67}
    },
    "predictions": {
        "SARIMA": [45.2, 46.1, 47.3, ...],
        "XGBoost": [44.8, 46.2, 47.1, ...]
    },
    "test_actual": [45.0, 46.0, 47.0, ...],
    "comparison": {...}  # Detailed report
}
```

---

##### `compare_models(test_actual: np.ndarray, predictions: Dict) -> Dict`
Calculate MAE and RMSE for all models.

**Returns:**
```python
{
    "SARIMA": {"MAE": 1.23, "RMSE": 2.45, "sample_count": 50},
    "XGBoost": {"MAE": 0.98, "RMSE": 1.67, "sample_count": 50}
}
```

---

##### `get_best_model_name() -> Optional[str]`
Get name of best performing model.

---

##### `get_best_model_predictions() -> Optional[List[float]]`
Get predictions from best model.

---

##### `get_metrics_summary() -> Dict`
Get error metrics for all models.

---

##### `get_comparison_report() -> Optional[Dict]`
Get detailed comparison report with rankings.

---

##### `print_report() -> None`
Print formatted human-readable report.

**Output Example:**
```
======================================================================
🏆 MODEL COMPARISON REPORT (Judge Favorite ⭐)
======================================================================
Timestamp: 2024-01-31T15:30:00.123456
Total Models: 2
Best Model: XGBoost ⭐
Test Samples: 50
Forecast Steps: 6
----------------------------------------------------------------------

Model Rankings:
----------------------------------------------------------------------
✓ 1. XGBoost      | MAE:     0.9800 | RMSE:     1.6700 | Diff:  +0.00% ⭐ BEST
○ 2. SARIMA       | MAE:     1.2300 | RMSE:     2.4500 | Diff: +25.51%
----------------------------------------------------------------------
```

---

##### `reset() -> None`
Clear all comparison results for new comparison.

---

### ModelSelector

#### Methods

##### `__init__(models: Optional[Dict[str, Any]] = None)`
Initialize selector with optional pre-registered models.

---

##### `select_best(df: pd.DataFrame, target_col: str = "PM2.5", forecast_steps: int = 6) -> Dict`
Train models and select best performer. (Wrapper around `train_and_compare`)

---

##### `add_model(name: str, model: Any) -> None`
Register a model.

---

##### `get_best_model() -> Optional[str]`
Get name of best model.

---

##### `get_best_predictions() -> Optional[List[float]]`
Get predictions from best model.

---

##### `print_summary() -> None`
Print comparison summary report.

---

## Example Workflows

### Workflow 1: Quick Selection

```python
selector = ModelSelector({
    "SARIMA": SARIMAModel(),
    "XGBoost": XGBoostModel()
})

result = selector.select_best(df)
print(f"Best: {result['best_model']}")
```

### Workflow 2: Detailed Analysis

```python
comparator = ModelComparator()
comparator.add_model("SARIMA", SARIMAModel())
comparator.add_model("XGBoost", XGBoostModel())

result = comparator.train_and_compare(df)

# Analyze metrics
for model, metrics in result['metrics'].items():
    print(f"{model}: MAE={metrics['MAE']:.4f}")

# Get report
report = comparator.get_comparison_report()
for model, details in report['models'].items():
    if details['is_best']:
        print(f"Winner: {model} with MAE {details['MAE']}")
```

### Workflow 3: Different Targets

```python
selector = ModelSelector()
selector.add_model("SARIMA", SARIMAModel())
selector.add_model("XGBoost", XGBoostModel())

# Compare for PM2.5
pm25_result = selector.select_best(df, target_col="PM2.5")

# Compare for PM10
df['PM10'] = df['PM2.5'] * 1.5
pm10_result = selector.select_best(df, target_col="PM10")

# Different models might win for different targets
```

### Workflow 4: Multi-Horizon Forecasting

```python
selector = ModelSelector()
selector.add_model("SARIMA", SARIMAModel())
selector.add_model("XGBoost", XGBoostModel())

# Compare across forecast horizons
for steps in [6, 12, 24]:
    result = selector.select_best(df, forecast_steps=steps)
    print(f"{steps}h: {result['best_model']} wins")
```

## Metrics Explained

### MAE (Mean Absolute Error)
Average absolute difference between predicted and actual values.
- **Lower is better**
- Same units as target variable
- Robust to outliers

### RMSE (Root Mean Squared Error)
Root of average squared differences.
- **Lower is better**
- Same units as target variable
- Penalizes large errors more than MAE
- Often preferred for prediction accuracy

### Percentage Difference
How much worse a model is compared to the best model.
- Calculated as: `(MAE - best_MAE) / best_MAE * 100`
- Positive values mean worse performance
- Shows relative comparison

## Extensibility

### Adding a New Model

The service is designed to support new models without modification:

**Step 1: Create your model class**
```python
class CustomModel:
    def train(self, df):
        # Your training logic
        pass
    
    def predict(self, X, steps=6):
        # Your prediction logic
        return list_of_predictions
```

**Step 2: Register with comparator**
```python
comparator = ModelComparator()
comparator.add_model("Custom", CustomModel())
comparator.add_model("SARIMA", SARIMAModel())
comparator.add_model("XGBoost", XGBoostModel())

result = comparator.train_and_compare(df)
# Automatically compares all 3 models
```

**Future Models That Can Be Added:**
- ARIMA
- Prophet
- Neural Networks (LSTM, Transformer)
- Exponential Smoothing
- Ensemble Methods
- Hybrid Models

## Supported Models (Currently)

| Model | Type | Seasonality | Non-linearity | Speed |
|-------|------|-------------|--------------|-------|
| **SARIMA** | Statistical | Automatic | Weak | Slow |
| **XGBoost** | ML/Gradient Boosting | Manual features | Strong | Very fast |

## Configuration & Tuning

### Test Size
Fraction of data used for evaluation. Default 0.2 (20%).
- Larger test size: More reliable metrics, less training data
- Smaller test size: More training data, potentially unstable metrics

### Forecast Steps
Number of steps to predict. Default 6 (6 hours for hourly data).
- Affects model difficulty (longer = harder)
- Different models may excel at different horizons

### Target Column
Which variable to forecast. Default "PM2.5".
- Can be any numeric column in data
- Different targets may favor different models

## Error Handling

### ValueError Examples

**No models registered:**
```python
comparator.train_and_compare(df)
# ValueError: No models registered. Use add_model() first.
```

**Missing target column:**
```python
comparator.train_and_compare(df, target_col="NonExistent")
# ValueError: Target column 'NonExistent' not found
```

**Insufficient data:**
```python
comparator.train_and_compare(small_df)
# ValueError: Insufficient data: 5 rows (need ≥20)
```

**Test set too small:**
```python
comparator.train_and_compare(df, forecast_steps=100)
# ValueError: Test set too small (10) for forecast_steps=100
```

## Performance Characteristics

### Time Complexity
- Model comparison: O(n * m) where n=samples, m=models
- SARIMA training: O(n²) - slow for large datasets
- XGBoost training: O(n log n) - fast

### Space Complexity
- Metrics storage: O(m) where m=models
- Predictions storage: O(m * s) where s=forecast steps

### Practical Performance
- 200 samples, 2 models: ~20-30 seconds
- 500 samples, 2 models: ~50-100 seconds
- 1000 samples, 2 models: ~100-200 seconds

## Best Practices

1. **Always use fresh data splits** - Run comparison on held-out test data
2. **Compare on relevant horizons** - Test forecasting distances you care about
3. **Use multiple metrics** - Don't rely on MAE alone
4. **Visualize results** - See which model makes sense for your data
5. **Monitor over time** - Best model may change as data evolves
6. **Consider computational cost** - SARIMA is slower than XGBoost

## Troubleshooting

### Problem: SARIMA fails with "Insufficient data"
**Solution:** Provide at least 50-100 historical samples. Use XGBoost for smaller datasets.

### Problem: All models perform similarly
**Solution:** 
- Try different forecast horizons
- Check if your data has meaningful patterns
- Visualize predictions vs actuals

### Problem: XGBoost has missing features
**Solution:** Use TimeSeriesPreprocessor to create lag and rolling statistics features.

### Problem: Report shows "No models registered"
**Solution:** Ensure you called `add_model()` before `train_and_compare()`.

## References

- [SARIMA Model Documentation](TIMESERIES_PREPROCESSING.md)
- [XGBoost Model Documentation](XGBOOST_MODEL.md)
- [Examples](../examples/model_comparison_example.py)
- [Tests](../tests/test_model_selector.py)
