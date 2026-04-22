"""
Model Loader Utility

Provides centralized model loading functionality with caching and error handling.
Automatically loads trained models from the saved directory.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Literal
from functools import lru_cache

logger = logging.getLogger(__name__)

# Model type definitions
ModelType = Literal["lstm", "sarima", "xgboost"]

# Base path for saved models
MODELS_DIR = Path(__file__).parent.parent / "models" / "saved"


class ModelLoadError(Exception):
    """Raised when model loading fails."""
    pass


class ModelLoader:
    """
    Centralized model loading with caching and error handling.
    
    Features:
    - Automatic model discovery
    - LRU caching for loaded models
    - Graceful error handling
    - Support for multiple cities/locations
    """
    
    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize model loader.
        
        Args:
            models_dir: Custom models directory (defaults to app/models/saved)
        """
        self.models_dir = models_dir or MODELS_DIR
        self._cache: Dict[str, Any] = {}
        
        if not self.models_dir.exists():
            logger.warning(f"Models directory not found: {self.models_dir}")
            self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def load_lstm(self, city: str) -> Any:
        """
        Load LSTM model for specified city.
        
        Args:
            city: City name (e.g., 'mumbai', 'delhi')
            
        Returns:
            Loaded LSTMModel instance
            
        Raises:
            ModelLoadError: If model files not found or loading fails
        """
        cache_key = f"lstm_{city}"
        
        # Check cache
        if cache_key in self._cache:
            logger.debug(f"Returning cached LSTM model for {city}")
            return self._cache[cache_key]
        
        try:
            from app.models.lstm_model import LSTMModel
            
            model_path = self.models_dir / f"lstm_{city}"
            h5_file = model_path.with_suffix('.h5')
            joblib_file = model_path.with_suffix('.joblib')
            
            # Check if files exist
            if not h5_file.exists():
                raise ModelLoadError(
                    f"LSTM model file not found: {h5_file}\n"
                    f"Please upload lstm_{city}.h5 to {self.models_dir}"
                )
            
            if not joblib_file.exists():
                raise ModelLoadError(
                    f"LSTM metadata file not found: {joblib_file}\n"
                    f"Please upload lstm_{city}.joblib to {self.models_dir}"
                )
            
            # Load model
            logger.info(f"Loading LSTM model for {city}...")
            model = LSTMModel.load(str(model_path))
            
            # Cache it
            self._cache[cache_key] = model
            logger.info(f"✓ LSTM model loaded for {city}")
            
            return model
            
        except ImportError as e:
            raise ModelLoadError(
                f"Failed to import LSTMModel: {e}\n"
                "Make sure TensorFlow is installed: pip install tensorflow"
            )
        except Exception as e:
            raise ModelLoadError(f"Failed to load LSTM model for {city}: {e}")
    
    def load_sarima(self, city: str) -> Any:
        """
        Load SARIMA model for specified city.
        
        Args:
            city: City name (e.g., 'mumbai', 'delhi')
            
        Returns:
            Loaded SARIMAModel instance
            
        Raises:
            ModelLoadError: If model file not found or loading fails
        """
        cache_key = f"sarima_{city}"
        
        # Check cache
        if cache_key in self._cache:
            logger.debug(f"Returning cached SARIMA model for {city}")
            return self._cache[cache_key]
        
        try:
            from app.models.sarima_model import SARIMAModel
            
            model_path = self.models_dir / f"sarima_{city}.pkl"
            
            # Check if file exists
            if not model_path.exists():
                raise ModelLoadError(
                    f"SARIMA model file not found: {model_path}\n"
                    f"Please upload sarima_{city}.pkl to {self.models_dir}"
                )
            
            # Load model
            logger.info(f"Loading SARIMA model for {city}...")
            model = SARIMAModel.load(str(model_path))
            
            # Cache it
            self._cache[cache_key] = model
            logger.info(f"✓ SARIMA model loaded for {city}")
            
            return model
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load SARIMA model for {city}: {e}")
    
    def load_xgboost(self, city: str) -> Any:
        """
        Load XGBoost model for specified city.
        
        Args:
            city: City name (e.g., 'mumbai', 'delhi')
            
        Returns:
            Loaded XGBoostModel instance
            
        Raises:
            ModelLoadError: If model file not found or loading fails
        """
        cache_key = f"xgboost_{city}"
        
        # Check cache
        if cache_key in self._cache:
            logger.debug(f"Returning cached XGBoost model for {city}")
            return self._cache[cache_key]
        
        try:
            from app.models.xgboost_model import XGBoostModel
            
            model_path = self.models_dir / f"xgboost_{city}.pkl"
            
            # Check if file exists
            if not model_path.exists():
                raise ModelLoadError(
                    f"XGBoost model file not found: {model_path}\n"
                    f"Please upload xgboost_{city}.pkl to {self.models_dir}"
                )
            
            # Load model
            logger.info(f"Loading XGBoost model for {city}...")
            model = XGBoostModel.load(str(model_path))
            
            # Cache it
            self._cache[cache_key] = model
            logger.info(f"✓ XGBoost model loaded for {city}")
            
            return model
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load XGBoost model for {city}: {e}")
    
    def load_model(self, model_type: ModelType, city: str) -> Any:
        """
        Load model by type and city.
        
        Args:
            model_type: Type of model ('lstm', 'sarima', 'xgboost')
            city: City name
            
        Returns:
            Loaded model instance
            
        Raises:
            ValueError: If model_type is invalid
            ModelLoadError: If loading fails
        """
        if model_type == "lstm":
            return self.load_lstm(city)
        elif model_type == "sarima":
            return self.load_sarima(city)
        elif model_type == "xgboost":
            return self.load_xgboost(city)
        else:
            raise ValueError(
                f"Invalid model_type: {model_type}. "
                "Must be 'lstm', 'sarima', or 'xgboost'"
            )
    
    def is_model_available(self, model_type: ModelType, city: str) -> bool:
        """
        Check if model is available for loading.
        
        Args:
            model_type: Type of model
            city: City name
            
        Returns:
            True if model files exist
        """
        if model_type == "lstm":
            h5_file = self.models_dir / f"lstm_{city}.h5"
            joblib_file = self.models_dir / f"lstm_{city}.joblib"
            return h5_file.exists() and joblib_file.exists()
        elif model_type == "sarima":
            pkl_file = self.models_dir / f"sarima_{city}.pkl"
            return pkl_file.exists()
        elif model_type == "xgboost":
            pkl_file = self.models_dir / f"xgboost_{city}.pkl"
            return pkl_file.exists()
        else:
            return False
    
    def list_available_models(self) -> Dict[str, list]:
        """
        List all available models in the saved directory.
        
        Returns:
            Dict with model types as keys and lists of cities as values
        """
        available = {
            "lstm": [],
            "sarima": [],
            "xgboost": []
        }
        
        if not self.models_dir.exists():
            return available
        
        # Find LSTM models
        for h5_file in self.models_dir.glob("lstm_*.h5"):
            city = h5_file.stem.replace("lstm_", "")
            joblib_file = h5_file.with_suffix('.joblib')
            if joblib_file.exists():
                available["lstm"].append(city)
        
        # Find SARIMA models
        for pkl_file in self.models_dir.glob("sarima_*.pkl"):
            city = pkl_file.stem.replace("sarima_", "")
            available["sarima"].append(city)
        
        # Find XGBoost models
        for pkl_file in self.models_dir.glob("xgboost_*.pkl"):
            city = pkl_file.stem.replace("xgboost_", "")
            available["xgboost"].append(city)
        
        return available
    
    def clear_cache(self) -> None:
        """Clear the model cache."""
        self._cache.clear()
        logger.info("Model cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached models.
        
        Returns:
            Dict with cache statistics
        """
        return {
            "cached_models": list(self._cache.keys()),
            "cache_size": len(self._cache),
            "models_dir": str(self.models_dir)
        }


# Global model loader instance
_global_loader: Optional[ModelLoader] = None


def get_model_loader() -> ModelLoader:
    """
    Get global model loader instance (singleton pattern).
    
    Returns:
        ModelLoader instance
    """
    global _global_loader
    if _global_loader is None:
        _global_loader = ModelLoader()
    return _global_loader


def load_model(model_type: ModelType, city: str) -> Any:
    """
    Convenience function to load a model.
    
    Args:
        model_type: Type of model ('lstm', 'sarima', 'xgboost')
        city: City name
        
    Returns:
        Loaded model instance
        
    Raises:
        ModelLoadError: If loading fails
    """
    loader = get_model_loader()
    return loader.load_model(model_type, city)


def is_model_available(model_type: ModelType, city: str) -> bool:
    """
    Check if model is available.
    
    Args:
        model_type: Type of model
        city: City name
        
    Returns:
        True if model files exist
    """
    loader = get_model_loader()
    return loader.is_model_available(model_type, city)


def list_available_models() -> Dict[str, list]:
    """
    List all available models.
    
    Returns:
        Dict with model types and available cities
    """
    loader = get_model_loader()
    return loader.list_available_models()


__all__ = [
    "ModelLoader",
    "ModelLoadError",
    "get_model_loader",
    "load_model",
    "is_model_available",
    "list_available_models",
]

