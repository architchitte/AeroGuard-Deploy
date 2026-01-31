"""Unit tests for XGBoostModel."""
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.models.xgboost_model import XGBoostModel


def make_preprocessed_df(n: int = 100, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic preprocessed data with lag/rolling features."""
    np.random.seed(seed)
    
    # Base time-series with trend and seasonality
    t = np.arange(n)
    base = 50 + 10 * np.sin(t / 24 * 2 * np.pi) + 0.1 * t + np.random.normal(0, 2, n)
    
    df = pd.DataFrame({
        "PM2.5": np.clip(base, 0, 500),
    })
    
    # Add lag features
    for h in [1, 3, 6]:
        df[f"PM2.5_lag_{h}h"] = df["PM2.5"].shift(h)
    
    # Add rolling statistics
    for w in [3, 6]:
        df[f"PM2.5_mean_{w}h"] = df["PM2.5"].rolling(w, min_periods=1).mean()
        df[f"PM2.5_std_{w}h"] = df["PM2.5"].rolling(w, min_periods=1).std().fillna(0)
    
    return df.dropna()


def test_xgboost_train_predict():
    """Test basic training and prediction."""
    df = make_preprocessed_df(100)
    model = XGBoostModel(target_col="PM2.5")
    
    # Train
    metrics = model.train(df)
    assert "train_mae" in metrics
    assert "train_rmse" in metrics
    assert "test_mae" in metrics
    assert "test_rmse" in metrics
    assert metrics["train_mae"] >= 0
    assert metrics["train_rmse"] >= 0
    
    # Predict
    X_test = df.iloc[-1:].copy()
    preds = model.predict(X_test, steps=6)
    assert len(preds) == 6
    assert all(isinstance(p, float) for p in preds)
    assert all(0 < p < 500 for p in preds)  # Reasonable AQI range


def test_xgboost_evaluate():
    """Test evaluation metrics."""
    model = XGBoostModel()
    
    preds = [50.0, 55.0, 52.0]
    actuals = [48.0, 57.0, 51.0]
    
    metrics = model.evaluate(preds, actuals)
    assert "mae" in metrics
    assert "rmse" in metrics
    # MAE = (|50-48| + |55-57| + |52-51|) / 3 = (2 + 2 + 1) / 3 = 1.667
    assert metrics["mae"] == pytest.approx(1.667, rel=0.05)
    assert metrics["rmse"] > metrics["mae"]


def test_xgboost_save_load(tmp_path):
    """Test save and load functionality."""
    df = make_preprocessed_df(100)
    model = model = XGBoostModel(target_col="PM2.5")
    model.train(df)
    
    # Save
    save_path = tmp_path / "xgb_model.joblib"
    model.save(str(save_path))
    assert save_path.exists()
    
    # Load
    loaded = XGBoostModel.load(str(save_path))
    assert loaded.target_col == "PM2.5"
    assert loaded._model is not None
    
    # Loaded model can predict
    X_test = df.iloc[-1:].copy()
    preds_orig = model.predict(X_test, steps=3)
    preds_loaded = loaded.predict(X_test, steps=3)
    
    assert len(preds_loaded) == 3
    # Predictions should be identical
    for p1, p2 in zip(preds_orig, preds_loaded):
        assert p1 == pytest.approx(p2, rel=1e-5)


def test_xgboost_missing_columns():
    """Test error handling for missing columns."""
    model = XGBoostModel(target_col="PM2.5")
    
    # DataFrame without lag features
    bad_df = pd.DataFrame({"PM2.5": [50, 51, 52]})
    
    with pytest.raises(ValueError):
        model.train(bad_df)


def test_xgboost_predict_before_train():
    """Test error when predicting before training."""
    model = XGBoostModel()
    df = make_preprocessed_df(10)
    
    with pytest.raises(RuntimeError):
        model.predict(df.iloc[-1:], steps=3)


def test_xgboost_evaluate_length_mismatch():
    """Test error on length mismatch in evaluation."""
    model = XGBoostModel()
    
    with pytest.raises(ValueError):
        model.evaluate([1.0, 2.0], [1.0])


def test_xgboost_custom_target_column():
    """Test with custom target column."""
    np.random.seed(42)
    df = pd.DataFrame({
        "AQI": np.random.uniform(0, 200, 100),
    })
    
    # Add required features
    for h in [1, 3, 6]:
        df[f"AQI_lag_{h}h"] = df["AQI"].shift(h)
    
    for w in [3, 6]:
        df[f"AQI_mean_{w}h"] = df["AQI"].rolling(w, min_periods=1).mean()
        df[f"AQI_std_{w}h"] = df["AQI"].rolling(w, min_periods=1).std().fillna(0)
    
    df = df.dropna()
    
    model = XGBoostModel(target_col="AQI")
    metrics = model.train(df)
    
    assert metrics["train_mae"] >= 0
    assert metrics["train_rmse"] >= 0


def test_xgboost_iterative_vs_static():
    """Test iterative forecasting vs static."""
    df = make_preprocessed_df(100)
    model = XGBoostModel()
    model.train(df)
    
    X_test = df.iloc[-1:].copy()
    
    # Iterative (default)
    preds_iter = model.predict(X_test, steps=6, iterative=True)
    
    # Static (no lag update)
    preds_static = model.predict(X_test, steps=6, iterative=False)
    
    assert len(preds_iter) == 6
    assert len(preds_static) == 6
    # Static predictions should be more stable
    assert np.std(preds_static) <= np.std(preds_iter) + 5


def test_xgboost_retrain(tmp_path):
    """Test model retraining."""
    df1 = make_preprocessed_df(80, seed=1)
    df2 = make_preprocessed_df(20, seed=2)
    
    model = XGBoostModel()
    metrics1 = model.train(df1)
    
    # Retrain without keeping weights
    metrics2 = model.retrain(df2, keep_weights=False)
    # Full retrain returns train/test splits
    assert "train_mae" in metrics2 or "mae" in metrics2
    assert "train_rmse" in metrics2 or "rmse" in metrics2
    
    # Model should still be able to predict
    X_test = df2.iloc[-1:].copy()
    preds = model.predict(X_test, steps=3)
    assert len(preds) == 3


def test_xgboost_feature_importance():
    """Test feature importance extraction."""
    df = make_preprocessed_df(100)
    model = XGBoostModel()
    model.train(df)
    
    importances = model.get_feature_importance()
    assert isinstance(importances, dict)
    assert len(importances) > 0
    assert all(isinstance(v, (float, np.floating)) for v in importances.values())
    assert sum(importances.values()) == pytest.approx(1.0, rel=0.01)
