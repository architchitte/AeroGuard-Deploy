import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from app.models.sarima_model import SARIMAModel


def make_series(n: int = 120, seed: int = 42) -> pd.Series:
    rng = pd.date_range(start="2023-01-01", periods=n, freq="H")
    rng_np = np.arange(n)
    np.random.seed(seed)
    values = 10.0 + np.sin(rng_np / 24.0 * 2 * np.pi) + np.random.normal(0, 0.5, size=n)
    return pd.Series(values, index=rng)


def test_train_predict_save_load(tmp_path):
    series = make_series(120)
    model = SARIMAModel()

    # Train
    model.train(series)
    assert model._results is not None

    # Predict
    preds = model.predict(6)
    assert isinstance(preds, list)
    assert len(preds) == 6
    assert all(isinstance(x, float) for x in preds)

    # Evaluate (use preds as actuals to get zero error)
    metrics = model.evaluate_forecast(preds, preds)
    assert pytest.approx(metrics["mae"], rel=1e-12) == 0.0
    assert pytest.approx(metrics["rmse"], rel=1e-12) == 0.0

    # Save & load
    p = tmp_path / "sarima_test.joblib"
    model.save(str(p))
    loaded = SARIMAModel.load(str(p))
    assert loaded._results is not None

    # Loaded model can predict
    loaded_preds = loaded.predict(6)
    assert len(loaded_preds) == 6
    assert all(isinstance(x, float) for x in loaded_preds)


def test_train_too_short():
    series = make_series(10)
    model = SARIMAModel()
    with pytest.raises(ValueError):
        model.train(series)


def test_predict_before_train():
    model = SARIMAModel()
    with pytest.raises(RuntimeError):
        model.predict(3)


def test_evaluate_length_mismatch():
    model = SARIMAModel()
    with pytest.raises(ValueError):
        model.evaluate_forecast([1.0, 2.0], [1.0])
