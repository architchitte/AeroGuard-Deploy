"""
Health Risk Model Wrapper

Integrates the trained aqi_health_risk.pkl model for health risk assessment.
Provides a clean interface for AQI-based health risk classification and advice.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import joblib

logger = logging.getLogger(__name__)


class HealthRiskModel:
    """
    Wrapper for the trained AQI health risk model.
    
    The model provides:
    - AQI category classification
    - Health advice based on risk levels
    - Personalized recommendations
    """
    
    # AQI thresholds (EPA standard)
    AQI_THRESHOLDS = {
        "Good": (0, 50),
        "Moderate": (51, 100),
        "Unhealthy for Sensitive Groups": (101, 150),
        "Unhealthy": (151, 200),
        "Very Unhealthy": (201, 300),
        "Hazardous": (301, 500)
    }
    
    # Color codes for each category
    COLOR_CODES = {
        "Good": "#00E400",
        "Moderate": "#FFFF00",
        "Unhealthy for Sensitive Groups": "#FF7E00",
        "Unhealthy": "#FF0000",
        "Very Unhealthy": "#8F3F97",
        "Hazardous": "#7E0023"
    }
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the health risk model.
        
        Args:
            model_path: Path to the model file (defaults to app/models/aqi_health_risk.pkl)
        """
        if model_path is None:
            model_path = Path(__file__).parent / "aqi_health_risk.pkl"
        
        self.model_path = model_path
        self.model_data: Optional[Dict] = None
        self._is_loaded = False
        
        # Load model on initialization
        self.load()
    
    def load(self) -> bool:
        """
        Load the model from disk.
        
        Returns:
            True if successful
            
        Raises:
            FileNotFoundError: If model file not found
            RuntimeError: If loading fails
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Health risk model not found: {self.model_path}\n"
                "Please ensure aqi_health_risk.pkl is in app/models/"
            )
        
        try:
            logger.info(f"Loading health risk model from {self.model_path}")
            self.model_data = joblib.load(self.model_path)
            
            # Validate model structure
            if not isinstance(self.model_data, dict):
                raise ValueError("Model data must be a dictionary")
            
            required_keys = ['aqi_categories', 'health_advice']
            missing_keys = [k for k in required_keys if k not in self.model_data]
            if missing_keys:
                raise ValueError(f"Model missing required keys: {missing_keys}")
            
            self._is_loaded = True
            logger.info("✓ Health risk model loaded successfully")
            
            # Log available categories
            categories = list(self.model_data['aqi_categories'].keys())
            logger.info(f"Available AQI categories: {categories}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load health risk model: {e}")
            raise RuntimeError(f"Failed to load health risk model: {e}")
    
    def classify_aqi(self, aqi_value: float) -> str:
        """
        Classify AQI value into risk category.
        
        Args:
            aqi_value: Numeric AQI value (0-500+)
            
        Returns:
            Risk category name (e.g., "Good", "Moderate", etc.)
            
        Raises:
            ValueError: If AQI value is invalid
        """
        if aqi_value < 0:
            raise ValueError(f"AQI value must be non-negative: {aqi_value}")
        
        # Find matching category
        for category, (low, high) in self.AQI_THRESHOLDS.items():
            if low <= aqi_value <= high:
                return category
        
        # If above 500, still classify as Hazardous
        return "Hazardous"
    
    def get_health_advice(
        self,
        aqi_value: float,
        persona: Optional[str] = None
    ) -> Dict:
        """
        Get health advice for given AQI value.
        
        Args:
            aqi_value: Numeric AQI value
            persona: User persona (optional, for personalized advice)
            
        Returns:
            Dictionary with health advice and recommendations
        """
        if not self._is_loaded:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        # Classify AQI
        category = self.classify_aqi(aqi_value)
        
        # Get category info from model
        category_info = self.model_data['aqi_categories'].get(category, {})
        
        # Map category to risk level for health advice
        risk_level = self._map_category_to_risk_level(category)
        health_advice = self.model_data['health_advice'].get(risk_level, {})
        
        # Build response
        response = {
            "aqi_value": aqi_value,
            "category": category,
            "color_code": self.COLOR_CODES.get(category, "#000000"),
            "description": category_info.get("description", ""),
            "health_implications": category_info.get("health_implications", []),
            "cautionary_statement": category_info.get("cautionary_statement", ""),
            "general_advice": health_advice.get("general", ""),
            "sensitive_groups": health_advice.get("sensitive_groups", []),
            "precautions": health_advice.get("precautions", []),
            "activity_recommendations": health_advice.get("activity_recommendations", {})
        }
        
        # Add persona-specific advice if requested
        if persona and "personas" in health_advice:
            persona_advice = health_advice["personas"].get(persona, {})
            response["persona_advice"] = persona_advice
        
        return response
    
    def _map_category_to_risk_level(self, category: str) -> str:
        """
        Map AQI category to risk level used in health advice.
        
        Args:
            category: AQI category name
            
        Returns:
            Risk level string
        """
        mapping = {
            "Good": "Low",
            "Moderate": "Moderate",
            "Unhealthy for Sensitive Groups": "Moderate",
            "Unhealthy": "High",
            "Very Unhealthy": "High",
            "Hazardous": "Hazardous"
        }
        return mapping.get(category, "Moderate")
    
    def get_risk_assessment(
        self,
        aqi_value: float,
        pollutant: str = "PM2.5",
        location: Optional[str] = None
    ) -> Dict:
        """
        Get comprehensive risk assessment.
        
        Args:
            aqi_value: Numeric AQI value
            pollutant: Primary pollutant (default: PM2.5)
            location: Location name (optional)
            
        Returns:
            Comprehensive risk assessment dictionary
        """
        category = self.classify_aqi(aqi_value)
        advice = self.get_health_advice(aqi_value)
        
        assessment = {
            "location": location,
            "aqi": aqi_value,
            "primary_pollutant": pollutant,
            "risk_category": category,
            "color_code": self.COLOR_CODES.get(category),
            "risk_level": self._map_category_to_risk_level(category),
            "health_advice": advice,
            "at_risk_groups": self._get_at_risk_groups(category),
            "recommended_actions": self._get_recommended_actions(category)
        }
        
        return assessment
    
    def _get_at_risk_groups(self, category: str) -> List[str]:
        """Get populations at risk for given category."""
        at_risk_map = {
            "Good": [],
            "Moderate": ["Unusually sensitive people"],
            "Unhealthy for Sensitive Groups": [
                "Children",
                "Elderly",
                "People with asthma",
                "People with heart disease"
            ],
            "Unhealthy": [
                "Everyone",
                "Especially sensitive groups"
            ],
            "Very Unhealthy": [
                "Everyone",
                "Serious effects on sensitive groups"
            ],
            "Hazardous": [
                "Everyone",
                "Emergency conditions"
            ]
        }
        return at_risk_map.get(category, [])
    
    def _get_recommended_actions(self, category: str) -> Dict[str, str]:
        """Get recommended actions for given category."""
        actions_map = {
            "Good": {
                "outdoor_activity": "Enjoy normal outdoor activities",
                "indoor_activity": "No restrictions",
                "mask": "Not necessary"
            },
            "Moderate": {
                "outdoor_activity": "Acceptable for most people",
                "indoor_activity": "No restrictions",
                "mask": "Not necessary for most people"
            },
            "Unhealthy for Sensitive Groups": {
                "outdoor_activity": "Sensitive groups should reduce prolonged outdoor exertion",
                "indoor_activity": "Move strenuous activities indoors",
                "mask": "Consider N95 mask for sensitive groups"
            },
            "Unhealthy": {
                "outdoor_activity": "Everyone should reduce outdoor exertion",
                "indoor_activity": "Move activities indoors",
                "mask": "Wear N95 mask outdoors"
            },
            "Very Unhealthy": {
                "outdoor_activity": "Avoid outdoor activities",
                "indoor_activity": "Stay indoors with air purifier",
                "mask": "Wear N95/P100 mask if must go outside"
            },
            "Hazardous": {
                "outdoor_activity": "Avoid all outdoor activities",
                "indoor_activity": "Remain indoors, seal windows",
                "mask": "Wear HEPA respirator if must go outside"
            }
        }
        return actions_map.get(category, {})
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        if not self._is_loaded:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "model_path": str(self.model_path),
            "categories": list(self.model_data['aqi_categories'].keys()),
            "risk_levels": list(self.model_data['health_advice'].keys()),
            "thresholds": self.AQI_THRESHOLDS
        }
    
    @classmethod
    def get_default_instance(cls) -> "HealthRiskModel":
        """
        Get a default instance of the model.
        
        Returns:
            HealthRiskModel instance
        """
        return cls()


# Global instance for easy access
_global_instance: Optional[HealthRiskModel] = None


def get_health_risk_model() -> HealthRiskModel:
    """
    Get global health risk model instance (singleton pattern).
    
    Returns:
        HealthRiskModel instance
    """
    global _global_instance
    if _global_instance is None:
        _global_instance = HealthRiskModel()
    return _global_instance


def classify_aqi(aqi_value: float) -> str:
    """
    Convenience function to classify AQI value.
    
    Args:
        aqi_value: Numeric AQI value
        
    Returns:
        Risk category name
    """
    model = get_health_risk_model()
    return model.classify_aqi(aqi_value)


def get_health_advice(aqi_value: float, persona: Optional[str] = None) -> Dict:
    """
    Convenience function to get health advice.
    
    Args:
        aqi_value: Numeric AQI value
        persona: User persona (optional)
        
    Returns:
        Health advice dictionary
    """
    model = get_health_risk_model()
    return model.get_health_advice(aqi_value, persona)


__all__ = [
    "HealthRiskModel",
    "get_health_risk_model",
    "classify_aqi",
    "get_health_advice"
]

