"""Train LSTM model using Mumbai AQI Dataset."""
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.lstm_model import LSTMModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    dataset_path = Path("India-Air-Quality-Dataset/Mumbai_AQI_Dataset.csv")
    if not dataset_path.exists():
        logger.error(f"Dataset not found at {dataset_path}")
        return

    logger.info("Loading dataset...")
    df = pd.read_csv(dataset_path)
    
    # Convert Date to datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
    df = df.set_index('Date').sort_index()
    
    # LSTM needs a target column
    logger.info(f"Training LSTM on {len(df)} samples...")
    model = LSTMModel(target_col='PM2.5', lookback=14) # 2 weeks lookback for daily data
    
    try:
        metrics = model.train(df, epochs=30, batch_size=16, verbose=1)
        logger.info(f"LSTM Training Complete. Metrics: {metrics}")
        
        # Save model
        save_dir = Path("app/models/saved")
        save_dir.mkdir(parents=True, exist_ok=True)
        model_path = save_dir / "lstm_mumbai"
        model.save(str(model_path))
        logger.info(f"Model saved to {model_path}.joblib and .h5")
    except Exception as e:
        logger.error(f"LSTM training failed: {e}")

if __name__ == "__main__":
    main()
