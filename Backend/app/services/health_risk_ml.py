"""
ML-Enhanced Health Risk Service

Integrates the trained aqi_health_risk.pkl model with the existing health risk service.
Provides ML-based health risk assessment alongside rule-based classification.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from app.models.health_risk_model import HealthRiskModel, get_health_risk_model

logger = logging.getLogger(__name__)


class MLHealthRiskService:
    """
    ML-enhanced health risk assessment service.
    
    Combines trained ML model with rule-based health advice for
    comprehensive risk assessment.
    """
    
    def __init__(self, use_ml_model: bool = True):
        """
        Initialize the service.
        
        Args:
            use_ml_model: Whether to use ML model (True) or fallback to rules (False)
        """
        self.use_ml_model = use_ml_model
        self.ml_model: Optional[HealthRiskModel] = None
        
        if use_ml_model:
            try:
                self.ml_model = get_health_risk_model()
                logger.info("✓ ML Health Risk Model loaded")
            except Exception as e:
                logger.warning(f"Failed to load ML model, using fallback: {e}")
                self.use_ml_model = False
    
    def assess_health_risk(
        self,
        aqi_value: float,
        pollutant: str = "PM2.5",
        location: Optional[str] = None,
        persona: Optional[str] = None
    ) -> Dict:
        """
        Comprehensive health risk assessment.
        
        Args:
            aqi_value: Numeric AQI value
            pollutant: Primary pollutant (PM2.5, PM10, etc.)
            location: Location name (optional)
            persona: User persona for personalized advice (optional)
            
        Returns:
            Comprehensive risk assessment dictionary
        """
        if self.use_ml_model and self.ml_model:
            return self._ml_assessment(aqi_value, pollutant, location, persona)
        else:
            return self._fallback_assessment(aqi_value, pollutant, location)
    
    def _ml_assessment(
        self,
        aqi_value: float,
        pollutant: str,
        location: Optional[str],
        persona: Optional[str]
    ) -> Dict:
        """ML-based assessment using trained model."""
        try:
            # Get ML model assessment
            assessment = self.ml_model.get_risk_assessment(
                aqi_value=aqi_value,
                pollutant=pollutant,
                location=location
            )
            
            # Get health advice (with persona if provided)
            health_advice = self.ml_model.get_health_advice(aqi_value, persona)
            
            # Combine into comprehensive response
            response = {
                "timestamp": datetime.now().isoformat(),
                "location": location,
                "aqi": {
                    "value": aqi_value,
                    "primary_pollutant": pollutant,
                    "category": assessment["risk_category"],
                    "color_code": assessment["color_code"],
                    "risk_level": assessment["risk_level"]
                },
                "health_assessment": {
                    "description": health_advice.get("description", ""),
                    "health_implications": health_advice.get("health_implications", []),
                    "cautionary_statement": health_advice.get("cautionary_statement", ""),
                    "at_risk_groups": assessment["at_risk_groups"]
                },
                "recommendations": {
                    "general_advice": health_advice.get("general_advice", ""),
                    "sensitive_groups": health_advice.get("sensitive_groups", []),
                    "precautions": health_advice.get("precautions", []),
                    "activity_recommendations": health_advice.get("activity_recommendations", {}),
                    "recommended_actions": assessment["recommended_actions"]
                },
                "model_source": "ml_trained",
                "model_confidence": "high"
            }
            
            # Add persona-specific advice if available
            if persona and "persona_advice" in health_advice:
                response["persona_advice"] = health_advice["persona_advice"]
            
            return response
            
        except Exception as e:
            logger.error(f"ML assessment failed: {e}")
            return self._fallback_assessment(aqi_value, pollutant, location)
    
    def _fallback_assessment(
        self,
        aqi_value: float,
        pollutant: str,
        location: Optional[str]
    ) -> Dict:
        """Fallback rule-based assessment."""
        # Simple rule-based classification
        category = self._classify_aqi_simple(aqi_value)
        
        response = {
            "timestamp": datetime.now().isoformat(),
            "location": location,
            "aqi": {
                "value": aqi_value,
                "primary_pollutant": pollutant,
                "category": category,
                "color_code": self._get_color_code(category),
                "risk_level": self._get_risk_level(category)
            },
            "health_assessment": {
                "description": self._get_description(category),
                "health_implications": self._get_health_implications(category),
                "cautionary_statement": self._get_cautionary_statement(category),
                "at_risk_groups": self._get_at_risk_groups(category)
            },
            "recommendations": {
                "general_advice": self._get_general_advice(category),
                "precautions": self._get_precautions(category),
                "activity_recommendations": self._get_activity_recommendations(category)
            },
            "model_source": "rule_based",
            "model_confidence": "medium"
        }
        
        return response
    
    def _classify_aqi_simple(self, aqi_value: float) -> str:
        """Simple AQI classification."""
        if aqi_value <= 50:
            return "Good"
        elif aqi_value <= 100:
            return "Moderate"
        elif aqi_value <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi_value <= 200:
            return "Unhealthy"
        elif aqi_value <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    def _get_color_code(self, category: str) -> str:
        """Get color code for category."""
        colors = {
            "Good": "#00E400",
            "Moderate": "#FFFF00",
            "Unhealthy for Sensitive Groups": "#FF7E00",
            "Unhealthy": "#FF0000",
            "Very Unhealthy": "#8F3F97",
            "Hazardous": "#7E0023"
        }
        return colors.get(category, "#000000")
    
    def _get_risk_level(self, category: str) -> str:
        """Get risk level for category."""
        mapping = {
            "Good": "Low",
            "Moderate": "Moderate",
            "Unhealthy for Sensitive Groups": "Moderate",
            "Unhealthy": "High",
            "Very Unhealthy": "High",
            "Hazardous": "Hazardous"
        }
        return mapping.get(category, "Moderate")
    
    def _get_description(self, category: str) -> str:
        """Get description for category."""
        descriptions = {
            "Good": "Air quality is satisfactory, and air pollution poses little or no risk.",
            "Moderate": "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.",
            "Unhealthy for Sensitive Groups": "Members of sensitive groups may experience health effects. The general public is less likely to be affected.",
            "Unhealthy": "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.",
            "Very Unhealthy": "Health alert: The risk of health effects is increased for everyone.",
            "Hazardous": "Health warning of emergency conditions: everyone is more likely to be affected."
        }
        return descriptions.get(category, "")
    
    def _get_health_implications(self, category: str) -> List[str]:
        """Get health implications for category."""
        implications = {
            "Good": ["No health concerns", "Air quality satisfactory"],
            "Moderate": ["Acceptable for most people", "Sensitive individuals should be cautious"],
            "Unhealthy for Sensitive Groups": ["Sensitive groups may experience health effects", "Respiratory symptoms possible"],
            "Unhealthy": ["Increased likelihood of health effects", "Respiratory and cardiovascular symptoms"],
            "Very Unhealthy": ["Serious health effects for all", "Significant respiratory distress possible"],
            "Hazardous": ["Emergency health conditions", "Severe health effects expected"]
        }
        return implications.get(category, [])
    
    def _get_cautionary_statement(self, category: str) -> str:
        """Get cautionary statement for category."""
        statements = {
            "Good": "Enjoy outdoor activities.",
            "Moderate": "Unusually sensitive people should consider limiting prolonged outdoor exertion.",
            "Unhealthy for Sensitive Groups": "Sensitive groups should reduce prolonged or heavy outdoor exertion.",
            "Unhealthy": "Everyone should reduce prolonged or heavy outdoor exertion.",
            "Very Unhealthy": "Everyone should avoid prolonged or heavy outdoor exertion.",
            "Hazardous": "Everyone should avoid all outdoor exertion."
        }
        return statements.get(category, "")
    
    def _get_at_risk_groups(self, category: str) -> List[str]:
        """Get at-risk groups for category."""
        groups = {
            "Good": [],
            "Moderate": ["Unusually sensitive people"],
            "Unhealthy for Sensitive Groups": ["Children", "Elderly", "People with asthma", "People with heart disease"],
            "Unhealthy": ["Everyone", "Especially sensitive groups"],
            "Very Unhealthy": ["Everyone", "Serious effects on sensitive groups"],
            "Hazardous": ["Everyone", "Emergency conditions"]
        }
        return groups.get(category, [])
    
    def _get_general_advice(self, category: str) -> str:
        """Get general advice for category."""
        advice = {
            "Good": "It's a great day to be active outside.",
            "Moderate": "Enjoy outdoor activities, but sensitive individuals should watch for symptoms.",
            "Unhealthy for Sensitive Groups": "Sensitive groups should limit outdoor activities.",
            "Unhealthy": "Everyone should limit outdoor activities.",
            "Very Unhealthy": "Avoid outdoor activities. Stay indoors with air purification.",
            "Hazardous": "Remain indoors and keep activity levels low. Follow emergency guidelines."
        }
        return advice.get(category, "")
    
    def _get_precautions(self, category: str) -> List[str]:
        """Get precautions for category."""
        precautions = {
            "Good": [],
            "Moderate": ["Monitor air quality", "Watch for symptoms"],
            "Unhealthy for Sensitive Groups": ["Limit outdoor time", "Wear N95 mask if going outside", "Keep medications accessible"],
            "Unhealthy": ["Stay indoors when possible", "Wear N95 mask outdoors", "Use air purifier"],
            "Very Unhealthy": ["Avoid all outdoor activity", "Keep windows closed", "Run air purifier continuously"],
            "Hazardous": ["Seal windows and doors", "Use HEPA air purifier", "Follow emergency protocols"]
        }
        return precautions.get(category, [])
    
    def _get_activity_recommendations(self, category: str) -> Dict[str, str]:
        """Get activity recommendations for category."""
        recommendations = {
            "Good": {
                "outdoor": "All activities appropriate",
                "indoor": "No restrictions",
                "exercise": "Normal exercise routine"
            },
            "Moderate": {
                "outdoor": "Acceptable for most people",
                "indoor": "No restrictions",
                "exercise": "Normal for most, sensitive groups monitor"
            },
            "Unhealthy for Sensitive Groups": {
                "outdoor": "Limit prolonged exertion",
                "indoor": "Move strenuous activities indoors",
                "exercise": "Reduce intensity for sensitive groups"
            },
            "Unhealthy": {
                "outdoor": "Reduce outdoor exertion",
                "indoor": "Move activities indoors",
                "exercise": "Reduce intensity for everyone"
            },
            "Very Unhealthy": {
                "outdoor": "Avoid outdoor activities",
                "indoor": "Stay indoors with air purification",
                "exercise": "Light indoor activity only"
            },
            "Hazardous": {
                "outdoor": "Avoid all outdoor exposure",
                "indoor": "Remain indoors in sealed environment",
                "exercise": "Minimal activity"
            }
        }
        return recommendations.get(category, {})
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model metadata
        """
        if self.use_ml_model and self.ml_model:
            return {
                "model_type": "ml_trained",
                "model_loaded": True,
                "model_info": self.ml_model.get_model_info()
            }
        else:
            return {
                "model_type": "rule_based",
                "model_loaded": False,
                "fallback_active": True
            }


# Global service instance
_global_service: Optional[MLHealthRiskService] = None


def get_health_risk_service() -> MLHealthRiskService:
    """
    Get global health risk service instance (singleton pattern).
    
    Returns:
        MLHealthRiskService instance
    """
    global _global_service
    if _global_service is None:
        _global_service = MLHealthRiskService()
    return _global_service


def assess_health_risk(
    aqi_value: float,
    pollutant: str = "PM2.5",
    location: Optional[str] = None,
    persona: Optional[str] = None
) -> Dict:
    """
    Convenience function for health risk assessment.
    
    Args:
        aqi_value: Numeric AQI value
        pollutant: Primary pollutant
        location: Location name (optional)
        persona: User persona (optional)
        
    Returns:
        Health risk assessment dictionary
    """
    service = get_health_risk_service()
    return service.assess_health_risk(aqi_value, pollutant, location, persona)


__all__ = [
    "MLHealthRiskService",
    "get_health_risk_service",
    "assess_health_risk"
]

