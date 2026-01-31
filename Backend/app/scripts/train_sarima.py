"""Train SARIMA model using Mumbai AQI Dataset."""
import os
import sys
import pandas as pd
from pathlib import Path
import logging

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.sarima_model import SARIMAModel

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
    
    # SARIMA training (using daily frequency)
    series = df['PM2.5'].dropna()
    
    logger.info(f"Training SARIMA on {len(series)} samples...")
    model = SARIMAModel(order=(1, 1, 1), seasonal_order=(1, 1, 1, 7)) # s=7 for weekly seasonality in daily data
    model.train(series)
    
    logger.info("SARIMA Training Complete.")
    
    # Save model
    save_dir = Path("app/models/saved")
    save_dir.mkdir(parents=True, exist_ok=True)
    model_path = save_dir / "sarima_mumbai.joblib"
    model.save(str(model_path))
    logger.info(f"Model saved to {model_path}")

if __name__ == "__main__":
    main()
