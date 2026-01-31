"""Train XGBoost model using Mumbai AQI Dataset."""
import os
import sys
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.xgboost_model import XGBoostModel
from app.utils.timeseries_preprocessor import TimeSeriesPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    dataset_path = Path("India-Air-Quality-Dataset/Mumbai_AQI_Dataset.csv")
    if not dataset_path.exists():
        logger.error(f"Dataset not found at {dataset_path}")
        return

    logger.info("Loading dataset...")
    df = pd.read_csv(dataset_path)
    
    # Preprocess
    preprocessor = TimeSeriesPreprocessor(datetime_column='Date', target_columns=['PM2.5'])
    
    # Convert Date to datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
    df = df.set_index('Date').sort_index()
    
    logger.info("Creating features...")
    df_features = preprocessor.prepare_features(df, target_col='PM2.5')
    df_features = df_features.dropna()
    
    logger.info(f"Training XGBoost on {len(df_features)} samples...")
    model = XGBoostModel(target_col='PM2.5')
    metrics = model.train(df_features)
    
    logger.info(f"Training Complete. Metrics: {metrics}")
    
    # Save model
    save_dir = Path("app/models/saved")
    save_dir.mkdir(parents=True, exist_ok=True)
    model_path = save_dir / "xgboost_mumbai.joblib"
    model.save(str(model_path))
    logger.info(f"Model saved to {model_path}")

if __name__ == "__main__":
    main()
