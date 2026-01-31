# Air Quality Time-Series Preprocessing Module

Complete guide for using the `TimeSeriesPreprocessor` module for air quality data preprocessing.

## Overview

The `TimeSeriesPreprocessor` class provides a comprehensive pipeline for preparing air quality time-series data for machine learning:

- **Load Data**: Read from CSV files
- **Parse Datetime**: Correctly handle datetime columns
- **Handle Missing Values**: Forward fill, rolling mean, or hybrid approaches
- **Remove Outliers**: IQR or Z-score based detection
- **Feature Engineering**: Lag features and rolling statistics
- **Export**: Clean pandas DataFrame ready for modeling

## Installation

The module is part of the AeroGuard project:

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from app.utils.timeseries_preprocessor import TimeSeriesPreprocessor

# Initialize preprocessor
preprocessor = TimeSeriesPreprocessor(
    datetime_column="datetime",
    target_columns=["PM2.5", "AQI"]
)

# Preprocess data
df = preprocessor.preprocess(
    "air_quality_data.csv",
    datetime_column="datetime",
    lag_hours=[1, 3, 6],
    rolling_windows=[3, 6],
)

print(df.head())
```

### Output

The preprocessed DataFrame has:
- **Datetime index** (sorted chronologically)
- **Original columns** (PM2.5, AQI, etc.)
- **Lag features** (PM2.5_lag_1h, PM2.5_lag_3h, etc.)
- **Rolling statistics** (PM2.5_mean_3h, PM2.5_std_3h, etc.)

## API Reference

### `TimeSeriesPreprocessor`

Main class for time-series preprocessing.

#### Constructor

```python
TimeSeriesPreprocessor(
    datetime_column: str = "datetime",
    target_columns: Optional[List[str]] = None,
)
```

**Parameters:**
- `datetime_column` (str): Name of the datetime column
- `target_columns` (List[str]): Air quality parameters to process
  - Default: `["PM2.5", "AQI"]`

**Example:**
```python
preprocessor = TimeSeriesPreprocessor(
    datetime_column="timestamp",
    target_columns=["PM2.5", "PM10", "NO2", "O3"]
)
```

---

### `load_csv()`

Load air quality data from CSV.

```python
df = preprocessor.load_csv("air_quality.csv")
```

**Parameters:**
- `filepath` (str): Path to CSV file

**Returns:**
- `pd.DataFrame`: Raw data from CSV

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `pd.errors.ParserError`: If CSV is malformed

**Example:**
```python
try:
    df = preprocessor.load_csv("data/aq_2023.csv")
except FileNotFoundError:
    print("File not found!")
```

---

### `parse_datetime()`

Parse and validate datetime column.

```python
df = preprocessor.parse_datetime(
    df,
    datetime_column="datetime",
    datetime_format="%Y-%m-%d %H:%M:%S"
)
```

**Parameters:**
- `df` (DataFrame): Input data
- `datetime_column` (str, optional): Column name (overrides default)
- `datetime_format` (str, optional): strftime format string
  - If `None`, pandas will infer the format

**Returns:**
- `pd.DataFrame`: DataFrame with datetime as index

**Example:**

```python
# Auto-detect format
df = preprocessor.parse_datetime(df, datetime_column="date")

# Specify format
df = preprocessor.parse_datetime(
    df,
    datetime_column="date",
    datetime_format="%d/%m/%Y %H:%M"
)
```

---

### `handle_missing_values()`

Handle missing values using multiple methods.

```python
df = preprocessor.handle_missing_values(
    df,
    method="forward_fill",
    rolling_window=3
)
```

**Parameters:**
- `df` (DataFrame): Input data with datetime index
- `method` (str): Imputation method
  - `"forward_fill"`: Forward fill then backward fill (default)
  - `"rolling_mean"`: Replace with rolling mean
  - `"both"`: Forward fill then rolling mean for remaining
- `rolling_window` (int): Window size in hours for rolling mean

**Returns:**
- `pd.DataFrame`: DataFrame with imputed values

**Methods Comparison:**

| Method | Pros | Cons |
|--------|------|------|
| `forward_fill` | Preserves trends | May propagate errors |
| `rolling_mean` | Smooth interpolation | Reduces accuracy at boundaries |
| `both` | Combines benefits | Slower computation |

**Example:**

```python
# Forward fill (fastest)
df = preprocessor.handle_missing_values(df, method="forward_fill")

# Rolling mean (smoother)
df = preprocessor.handle_missing_values(
    df,
    method="rolling_mean",
    rolling_window=6
)

# Hybrid approach
df = preprocessor.handle_missing_values(df, method="both")
```

---

### `remove_outliers()`

Detect and handle outliers.

```python
df, stats = preprocessor.remove_outliers(
    df,
    method="iqr",
    iqr_multiplier=1.5
)
```

**Parameters:**
- `df` (DataFrame): Input data
- `method` (str): Detection method
  - `"iqr"`: Interquartile range (default)
  - `"zscore"`: Z-score method
- `iqr_multiplier` (float): IQR multiplier (default: 1.5)
- `std_multiplier` (float): Std dev multiplier for Z-score (default: 3.0)

**Returns:**
- `Tuple[DataFrame, Dict]`: Cleaned data and outlier statistics

**Methods:**

**IQR Method:**
```
Lower bound = Q1 - 1.5 * IQR
Upper bound = Q3 + 1.5 * IQR
```

**Z-Score Method:**
```
Z = |value - mean| / std
Outlier if Z > 3
```

**Example:**

```python
# IQR method (robust)
df, stats = preprocessor.remove_outliers(df, method="iqr")

# Z-score method (more sensitive)
df, stats = preprocessor.remove_outliers(
    df,
    method="zscore",
    std_multiplier=2.5
)

print(stats)
# Output: {'PM2.5': {'count': 5, 'percentage': 1.25}, ...}
```

---

### `create_lag_features()`

Create lagged features for time-series modeling.

```python
df = preprocessor.create_lag_features(
    df,
    lag_hours=[1, 3, 6]
)
```

**Parameters:**
- `df` (DataFrame): Input data with hourly datetime index
- `lag_hours` (List[int]): Lag hours to create
  - Default: `[1, 3, 6]`

**Returns:**
- `pd.DataFrame`: DataFrame with lag columns added

**Example:**

```python
# Standard lags
df = preprocessor.create_lag_features(df, lag_hours=[1, 3, 6])

# Custom lags
df = preprocessor.create_lag_features(
    df,
    lag_hours=[1, 2, 4, 8, 12, 24]
)
```

**Created Columns:**
For each target column and lag hour:
```
{column}_lag_{hour}h
```

Example:
```
PM2.5_lag_1h
PM2.5_lag_3h
PM2.5_lag_6h
AQI_lag_1h
AQI_lag_3h
AQI_lag_6h
```

---

### `create_rolling_statistics()`

Create rolling mean and standard deviation features.

```python
df = preprocessor.create_rolling_statistics(
    df,
    windows=[3, 6]
)
```

**Parameters:**
- `df` (DataFrame): Input data with hourly datetime index
- `windows` (List[int]): Window sizes in hours
  - Default: `[3, 6]`

**Returns:**
- `pd.DataFrame`: DataFrame with rolling statistic columns

**Example:**

```python
# Standard windows
df = preprocessor.create_rolling_statistics(df, windows=[3, 6])

# Longer windows for longer-term trends
df = preprocessor.create_rolling_statistics(
    df,
    windows=[6, 12, 24]
)
```

**Created Columns:**
For each target column and window:
```
{column}_mean_{window}h
{column}_std_{window}h
```

Example:
```
PM2.5_mean_3h      # 3-hour moving average
PM2.5_std_3h       # 3-hour moving std dev
PM2.5_mean_6h      # 6-hour moving average
PM2.5_std_6h       # 6-hour moving std dev
```

---

### `preprocess()` - Complete Pipeline

Full preprocessing pipeline in one call.

```python
df = preprocessor.preprocess(
    filepath="air_quality.csv",
    datetime_column="datetime",
    datetime_format="%Y-%m-%d %H:%M:%S",
    target_columns=["PM2.5", "PM10", "AQI"],
    missing_method="forward_fill",
    outlier_method="iqr",
    lag_hours=[1, 3, 6],
    rolling_windows=[3, 6],
    drop_na=True
)
```

**Parameters:**
- `filepath` (str): Path to CSV file
- `datetime_column` (str): Datetime column name
- `datetime_format` (str, optional): Datetime format string
- `target_columns` (List[str], optional): Air quality parameters
- `missing_method` (str): Missing value handling method
- `outlier_method` (str): Outlier detection method
- `lag_hours` (List[int]): Lag hours for features
- `rolling_windows` (List[int]): Rolling window sizes
- `drop_na` (bool): Drop rows with NaN after feature creation

**Returns:**
- `pd.DataFrame`: Clean preprocessed data

**Processing Steps:**
1. Load CSV
2. Parse datetime
3. Handle missing values
4. Remove outliers
5. Create lag features
6. Create rolling statistics
7. Drop remaining NaN rows

**Example:**

```python
# Full preprocessing pipeline
df = preprocessor.preprocess(
    "hourly_aq_data.csv",
    datetime_column="timestamp",
    target_columns=["PM2.5", "PM10"],
    missing_method="both",
    outlier_method="iqr",
    lag_hours=[1, 3, 6, 12],
    rolling_windows=[3, 6, 12],
    drop_na=True
)

print(f"Preprocessed shape: {df.shape}")
print(f"Features: {df.shape[1]} columns")
```

---

## Convenience Functions

Quick functions for common preprocessing tasks.

### `load_and_preprocess_aqi()`

Quick preprocessing for AQI data.

```python
from app.utils.timeseries_preprocessor import load_and_preprocess_aqi

df = load_and_preprocess_aqi(
    "air_quality.csv",
    datetime_column="datetime",
    drop_na=True
)
```

**Parameters:**
- `filepath` (str): CSV file path
- `datetime_column` (str): Datetime column name
- `drop_na` (bool): Drop rows with NaN

**Preprocessing:**
- Targets: `["AQI", "PM2.5", "PM10"]`
- Lags: `[1, 3, 6]` hours
- Rolling windows: `[3, 6]` hours

---

### `load_and_preprocess_pm25()`

Quick preprocessing for PM2.5 data.

```python
from app.utils.timeseries_preprocessor import load_and_preprocess_pm25

df = load_and_preprocess_pm25(
    "pm25_data.csv",
    datetime_column="date",
    drop_na=True
)
```

**Parameters:**
- `filepath` (str): CSV file path
- `datetime_column` (str): Datetime column name
- `drop_na` (bool): Drop rows with NaN

**Preprocessing:**
- Targets: `["PM2.5"]`
- Lags: `[1, 3, 6]` hours
- Rolling windows: `[3, 6]` hours

---

## Usage Examples

### Example 1: Basic Preprocessing

```python
from app.utils.timeseries_preprocessor import TimeSeriesPreprocessor

preprocessor = TimeSeriesPreprocessor(
    target_columns=["PM2.5", "AQI"]
)

df = preprocessor.preprocess("aq_data.csv")

# Ready for modeling
X = df.drop("PM2.5", axis=1)
y = df["PM2.5"]
```

### Example 2: Custom Configuration

```python
df = preprocessor.preprocess(
    "data.csv",
    datetime_column="time",
    datetime_format="%d/%m/%Y %H:%M",
    target_columns=["PM2.5", "PM10", "NO2"],
    missing_method="both",
    outlier_method="zscore",
    lag_hours=[1, 2, 3, 6, 12],
    rolling_windows=[2, 4, 8],
    drop_na=True
)
```

### Example 3: Save Preprocessed Data

```python
df = preprocessor.preprocess("raw_data.csv")

# Save to CSV
df.to_csv("preprocessed_data.csv")

# Save to Parquet (faster)
df.to_parquet("preprocessed_data.parquet")

# Save to pickle
df.to_pickle("preprocessed_data.pkl")
```

### Example 4: Split into Train/Test

```python
from sklearn.model_selection import train_test_split

df = preprocessor.preprocess("aq_data.csv")

# Split by time (recommended for time-series)
split_idx = int(0.8 * len(df))
train_df = df.iloc[:split_idx]
test_df = df.iloc[split_idx:]

print(f"Train: {len(train_df)}, Test: {len(test_df)}")
```

### Example 5: Feature Selection

```python
df = preprocessor.preprocess("aq_data.csv")

# Select specific features
feature_cols = [col for col in df.columns 
                if "lag" in col or "mean" in col]

X = df[feature_cols]
y = df["PM2.5"]

print(f"Features: {len(feature_cols)}")
print(f"X shape: {X.shape}, y shape: {y.shape}")
```

## Data Format Requirements

### Input CSV

Your CSV file should have:
- **Datetime column** with recognizable date/time format
- **Target columns** with numeric air quality values
- Optional: other feature columns

**Example:**
```
datetime,PM2.5,PM10,AQI,Temperature,Humidity
2023-01-01 00:00,45.2,62.1,85,15.3,65
2023-01-01 01:00,48.5,65.3,92,14.8,68
2023-01-01 02:00,52.1,68.9,98,14.1,72
```

### Output DataFrame

- **Index**: Datetime (hourly frequency)
- **Columns**: Original + lag features + rolling statistics
- **All values**: Numeric (no NaN if drop_na=True)

## Tips & Best Practices

### 1. Choose Appropriate Lag Hours

```python
# Short-term forecasting (1-6 hours)
lag_hours = [1, 2, 3]

# Medium-term forecasting (1-24 hours)
lag_hours = [1, 3, 6, 12, 24]

# Long-term forecasting
lag_hours = [6, 12, 24, 48]
```

### 2. Rolling Window Sizes

```python
# Same as lag hours for consistency
windows = [3, 6, 12]

# Or use multiples of your forecast horizon
# If forecasting 24 hours ahead:
windows = [24, 48, 72]
```

### 3. Handle Missing Values Strategy

```python
# Few missing values
method = "forward_fill"

# Many missing values
method = "rolling_mean"

# Mixed approach (recommended)
method = "both"
```

### 4. Outlier Detection

```python
# Less aggressive (preserves more data)
method = "iqr"
iqr_multiplier = 2.0

# More aggressive (removes more outliers)
method = "zscore"
std_multiplier = 2.5
```

### 5. Memory Optimization

```python
# Use float32 instead of float64 to save memory
df = df.astype('float32')

# Use Parquet for efficient storage
df.to_parquet("data.parquet")
df = pd.read_parquet("data.parquet")
```

## Troubleshooting

### Issue: "Datetime column not found"

**Solution:**
```python
# Check available columns
print(df.columns)

# Use correct column name
df = preprocessor.parse_datetime(df, datetime_column="correct_name")
```

### Issue: "Unable to parse datetime"

**Solution:**
```python
# Specify datetime format explicitly
df = preprocessor.parse_datetime(
    df,
    datetime_column="date",
    datetime_format="%Y-%m-%d %H:%M:%S"
)

# Or check raw data
print(df["date"].head())
```

### Issue: Too many NaN values after feature creation

**Solution:**
```python
# Reduce lag hours or rolling windows
df = preprocessor.preprocess(
    "data.csv",
    lag_hours=[1, 3],  # Shorter lags
    rolling_windows=[3],  # Smaller windows
    drop_na=False  # Keep rows with NaN
)

# Manual NaN handling
df = df.fillna(method='ffill').fillna(method='bfill')
```

### Issue: Memory error with large files

**Solution:**
```python
# Process in chunks
chunk_size = 10000
reader = pd.read_csv("large_file.csv", chunksize=chunk_size)

processed_chunks = []
for chunk in reader:
    processed = preprocessor.preprocess_chunk(chunk)
    processed_chunks.append(processed)

df = pd.concat(processed_chunks, ignore_index=True)
```

## Performance Considerations

| Parameter | Impact | Recommendation |
|-----------|--------|-----------------|
| Lag hours | More features, slower | [1, 3, 6] or [1, 6, 12] |
| Rolling windows | More features, slower | [3, 6] |
| Missing method | Processing time | "forward_fill" fastest |
| Outlier method | Processing time | "iqr" faster |
| drop_na | Result size | True for cleaner data |

## References

- [Pandas Documentation](https://pandas.pydata.org/)
- [Time Series Analysis](https://en.wikipedia.org/wiki/Time_series)
- [Feature Engineering](https://en.wikipedia.org/wiki/Feature_engineering)
- [Outlier Detection](https://en.wikipedia.org/wiki/Outlier)

---

**Created for AeroGuard - Air Quality Forecasting System**
