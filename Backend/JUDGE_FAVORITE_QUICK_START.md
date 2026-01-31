# Judge Favorite ⭐ - Quick Start Guide

## What Is This?

**Judge Favorite** is an intelligent model comparison service that automatically trains SARIMA and XGBoost forecasting models, compares their performance, and tells you which one is better for your specific forecasting task.

Think of it as having a judge who:
1. Trains all your models
2. Tests them fairly on held-out data
3. Compares their error metrics
4. Declares the winner ⭐
5. Gives you clear metrics and predictions

## Why Use It?

✅ **No Decision Paralysis** - Don't waste time choosing between models  
✅ **Fair Comparison** - Both models tested on same validation data  
✅ **Clear Metrics** - See exactly how each model performed  
✅ **Easy to Use** - Just 3 lines of code  
✅ **Extensible** - Add new models anytime  

## Get Started in 30 Seconds

### 1. Create a selector
```python
from app.services.model_selector import ModelSelector
from app.models.sarima_model import SARIMAModel
from app.models.xgboost_model import XGBoostModel

selector = ModelSelector({
    "SARIMA": SARIMAModel(),
    "XGBoost": XGBoostModel()
})
```

### 2. Run comparison
```python
result = selector.select_best(df, target_col="PM2.5", forecast_steps=6)
```

### 3. Get the winner
```python
print(f"🏆 Best Model: {result['best_model']}")
print(f"📊 Metrics: {result['metrics']}")
print(f"🔮 Forecast: {result['predictions']}")
```

## What You Get

```
Best Model: XGBoost ⭐

Metrics:
  XGBoost: MAE=0.98, RMSE=1.67 (BEST)
  SARIMA:  MAE=1.23, RMSE=2.45 (25.5% worse)

Forecast:
  [44.8, 46.2, 47.1, 48.5, 49.2, 50.1]
```

## Real-World Example

```python
import pandas as pd
from app.services.model_selector import ModelSelector
from app.models.sarima_model import SARIMAModel
from app.models.xgboost_model import XGBoostModel

# Load your air quality data
df = pd.read_csv("aqi_data.csv", parse_dates=["date"], index_col="date")

# Create selector
selector = ModelSelector({
    "SARIMA": SARIMAModel(),      # Statistical model
    "XGBoost": XGBoostModel()     # Machine learning model
})

# Compare models
result = selector.select_best(
    df, 
    target_col="PM2.5",      # What to forecast
    forecast_steps=6          # 6-hour ahead forecast
)

# Print results
print(f"Winner: {result['best_model']} ⭐")
print(f"MAE: {result['metrics'][result['best_model']]['MAE']:.4f}")
print(f"Forecast: {result['predictions'][result['best_model']]}")
```

## Compare Different Scenarios

### Different Air Quality Parameter
```python
# Compare for PM10 instead of PM2.5
result_pm10 = selector.select_best(df, target_col="PM10")
print(f"PM10 winner: {result_pm10['best_model']}")

# Different parameters might favor different models!
```

### Different Forecast Horizon
```python
# Compare short-term forecasts
result_6h = selector.select_best(df, forecast_steps=6)     # 6 hours
result_12h = selector.select_best(df, forecast_steps=12)   # 12 hours
result_24h = selector.select_best(df, forecast_steps=24)   # 24 hours

# XGBoost might be better for short-term
# SARIMA might be better for long-term
```

### More Detailed Report
```python
from app.services.model_selector import ModelComparator

comparator = ModelComparator()
comparator.add_model("SARIMA", SARIMAModel())
comparator.add_model("XGBoost", XGBoostModel())

comparator.train_and_compare(df, target_col="PM2.5")

# Print nice formatted report
comparator.print_report()

# Access detailed comparison
report = comparator.get_comparison_report()
```

## Add Your Own Model

Don't have SARIMA or XGBoost? Add your own!

```python
class MyCustomModel:
    def train(self, df):
        # Your training code
        pass
    
    def predict(self, X, steps=6):
        # Your prediction code
        return predictions

selector = ModelSelector({
    "SARIMA": SARIMAModel(),
    "XGBoost": XGBoostModel(),
    "MyModel": MyCustomModel()      # Your custom model!
})

# Now all 3 will be compared
result = selector.select_best(df)
```

## Metrics Explained

| Metric | What It Means | Lower = Better |
|--------|---------------|----------------|
| **MAE** | Average forecast error | ✅ Yes |
| **RMSE** | Error with extra penalty for big mistakes | ✅ Yes |
| **% Diff** | How much worse vs best model | ✅ Yes (0% = best) |

## Common Questions

**Q: Which model will win?**  
A: It depends on your data! XGBoost is usually faster, SARIMA is more statistical. Let Judge Favorite decide.

**Q: Can I use different models?**  
A: Yes! Any model with `train()` and `predict()` methods works.

**Q: How long does it take?**  
A: For 500 samples, typically 50-100 seconds. SARIMA is slower, XGBoost is fast.

**Q: What if my data is small?**  
A: You need at least 20 samples, preferably 100+. SARIMA needs more historical data.

**Q: Can I add Prophet or ARIMA?**  
A: Yes! Implement them with the same interface and add them to the selector.

## Files You Need

| File | Purpose |
|------|---------|
| [MODEL_SELECTOR.md](docs/MODEL_SELECTOR.md) | Full documentation |
| [examples/model_comparison_example.py](examples/model_comparison_example.py) | Working examples |
| [tests/test_model_selector.py](tests/test_model_selector.py) | Test cases |

## Key Features

✅ Automatic model training  
✅ Fair performance comparison  
✅ Intelligent best model selection  
✅ Detailed metrics and reporting  
✅ Extensible for new models  
✅ Production-ready code  
✅ Comprehensive testing (29 tests)  
✅ Full documentation  

## Status

🎯 **COMPLETE** - All 29 tests passing  
📚 **DOCUMENTED** - Full API reference and examples  
🚀 **PRODUCTION READY** - Ready to use immediately  

---

**Ready to judge your models? Start with the 30-second example above!**

For more: See [MODEL_SELECTOR.md](docs/MODEL_SELECTOR.md)
