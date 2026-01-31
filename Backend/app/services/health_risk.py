"""
Health Risk Classification Engine for Air Quality Data

This module provides health risk assessment based on AQI values,
supporting multiple user personas with personalized health advice
based on EPA/WHO air quality standards.

Features:
- EPA/WHO AQI threshold-based classification
- Multi-persona support (Children/Elderly, Athletes, General Public)
- Personalized health recommendations
- Structured JSON-friendly output
- Health effect descriptions
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """EPA/WHO air quality risk categories"""
    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_FOR_SENSITIVE = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"


class Persona(Enum):
    """User personas for personalized health guidance"""
    GENERAL_PUBLIC = "General Public"
    CHILDREN = "Children"
    ELDERLY = "Elderly"
    OUTDOOR_WORKERS = "Outdoor Workers"
    ATHLETES = "Athletes"
    SENSITIVE_GROUPS = "Sensitive Groups"


@dataclass
class HealthAdvice:
    """Structured health advice for a specific persona and risk level"""
    persona: str
    risk_category: str
    aqi_range: Tuple[int, int]
    activity_recommendation: str
    indoor_outdoor: str
    health_warning: Optional[str]
    precautions: List[str]
    symptoms_to_watch: List[str]


@dataclass
class HealthRiskAssessment:
    """Complete health risk assessment output"""
    aqi_value: float
    aqi_parameter: str
    risk_category: str
    color_code: str
    general_advice: str
    personalized_advice: Dict[str, HealthAdvice]
    health_effects: List[str]
    at_risk_populations: List[str]
    recommended_actions: Dict[str, str]
    timestamp: str


class AQIThresholds:
    """EPA/WHO AQI thresholds for different pollutants"""
    
    # PM2.5 thresholds (µg/m³)
    PM25_THRESHOLDS = {
        RiskCategory.GOOD: (0, 12),
        RiskCategory.MODERATE: (12.1, 35.4),
        RiskCategory.UNHEALTHY_FOR_SENSITIVE: (35.5, 55.4),
        RiskCategory.UNHEALTHY: (55.5, 150.4),
        RiskCategory.VERY_UNHEALTHY: (150.5, 250.4),
        RiskCategory.HAZARDOUS: (250.5, float('inf'))
    }
    
    # PM10 thresholds (µg/m³)
    PM10_THRESHOLDS = {
        RiskCategory.GOOD: (0, 54),
        RiskCategory.MODERATE: (55, 154),
        RiskCategory.UNHEALTHY_FOR_SENSITIVE: (155, 254),
        RiskCategory.UNHEALTHY: (255, 354),
        RiskCategory.VERY_UNHEALTHY: (355, 424),
        RiskCategory.HAZARDOUS: (425, float('inf'))
    }
    
    # NO₂ thresholds (ppb)
    NO2_THRESHOLDS = {
        RiskCategory.GOOD: (0, 53),
        RiskCategory.MODERATE: (54, 100),
        RiskCategory.UNHEALTHY_FOR_SENSITIVE: (101, 360),
        RiskCategory.UNHEALTHY: (361, 649),
        RiskCategory.VERY_UNHEALTHY: (650, 1249),
        RiskCategory.HAZARDOUS: (1250, float('inf'))
    }
    
    # O₃ thresholds (ppb)
    O3_THRESHOLDS = {
        RiskCategory.GOOD: (0, 54),
        RiskCategory.MODERATE: (55, 70),
        RiskCategory.UNHEALTHY_FOR_SENSITIVE: (71, 85),
        RiskCategory.UNHEALTHY: (86, 105),
        RiskCategory.VERY_UNHEALTHY: (106, 200),
        RiskCategory.HAZARDOUS: (201, float('inf'))
    }
    
    # SO₂ thresholds (ppb)
    SO2_THRESHOLDS = {
        RiskCategory.GOOD: (0, 35),
        RiskCategory.MODERATE: (36, 75),
        RiskCategory.UNHEALTHY_FOR_SENSITIVE: (76, 185),
        RiskCategory.UNHEALTHY: (186, 304),
        RiskCategory.VERY_UNHEALTHY: (305, 604),
        RiskCategory.HAZARDOUS: (605, float('inf'))
    }
    
    # CO thresholds (ppm)
    CO_THRESHOLDS = {
        RiskCategory.GOOD: (0, 4.4),
        RiskCategory.MODERATE: (4.5, 9.4),
        RiskCategory.UNHEALTHY_FOR_SENSITIVE: (9.5, 12.4),
        RiskCategory.UNHEALTHY: (12.5, 15.4),
        RiskCategory.VERY_UNHEALTHY: (15.5, 30.4),
        RiskCategory.HAZARDOUS: (30.5, float('inf'))
    }


class HealthEffectsMapping:
    """Health effects for each AQI level"""
    
    EFFECTS = {
        RiskCategory.GOOD: [
            "No health concerns",
            "Air quality satisfactory",
            "Air pollution poses little to no risk"
        ],
        RiskCategory.MODERATE: [
            "Air quality acceptable",
            "Unusually sensitive people should consider outdoor activity limitations",
            "General public unaffected"
        ],
        RiskCategory.UNHEALTHY_FOR_SENSITIVE: [
            "Members of sensitive groups may experience health effects",
            "General public not likely to be affected",
            "Respiratory symptoms possible in sensitive individuals"
        ],
        RiskCategory.UNHEALTHY: [
            "Some members of the general public may experience health effects",
            "Members of sensitive groups more likely to experience health effects",
            "Increased likelihood of respiratory symptoms"
        ],
        RiskCategory.VERY_UNHEALTHY: [
            "Health alert: all members of the general public may begin to experience effects",
            "Members of sensitive groups may experience more serious health effects",
            "Significant health risk to all people"
        ],
        RiskCategory.HAZARDOUS: [
            "Health warning of emergency conditions: entire population more likely to be affected",
            "Serious health effects possible for all people",
            "Everyone should reduce prolonged outdoor exertion"
        ]
    }


class PersonaHealthAdviceMapping:
    """Personalized health advice for different personas"""
    
    ADVICE = {
        Persona.GENERAL_PUBLIC: {
            RiskCategory.GOOD: HealthAdvice(
                persona="General Public",
                risk_category="Good",
                aqi_range=(0, 50),
                activity_recommendation="All outdoor activities are appropriate",
                indoor_outdoor="Normal outdoor activity",
                health_warning=None,
                precautions=[],
                symptoms_to_watch=[]
            ),
            RiskCategory.MODERATE: HealthAdvice(
                persona="General Public",
                risk_category="Moderate",
                aqi_range=(51, 100),
                activity_recommendation="Moderate outdoor activity is acceptable",
                indoor_outdoor="Enjoy outdoor activities normally",
                health_warning="Unusually sensitive people should limit outdoor exposure",
                precautions=["Reduce prolonged outdoor exertion if unusually sensitive"],
                symptoms_to_watch=[]
            ),
            RiskCategory.UNHEALTHY_FOR_SENSITIVE: HealthAdvice(
                persona="General Public",
                risk_category="Unhealthy for Sensitive Groups",
                aqi_range=(101, 150),
                activity_recommendation="Continue outdoor activities for most people",
                indoor_outdoor="Sensitive groups should limit outdoor activity",
                health_warning="Sensitive groups may experience health effects",
                precautions=["Limit outdoor activity if sensitive", "Wear N95 mask if going outside"],
                symptoms_to_watch=["Coughing", "Shortness of breath", "Chest tightness"]
            ),
            RiskCategory.UNHEALTHY: HealthAdvice(
                persona="General Public",
                risk_category="Unhealthy",
                aqi_range=(151, 200),
                activity_recommendation="Reduce outdoor activity",
                indoor_outdoor="Limit outdoor activity, stay indoors when possible",
                health_warning="General public may experience health effects",
                precautions=["Limit outdoor activity", "Wear N95/P100 mask outdoors", "Use air purifier indoors"],
                symptoms_to_watch=["Persistent coughing", "Wheezing", "Shortness of breath"]
            ),
            RiskCategory.VERY_UNHEALTHY: HealthAdvice(
                persona="General Public",
                risk_category="Very Unhealthy",
                aqi_range=(201, 300),
                activity_recommendation="Avoid all outdoor activity",
                indoor_outdoor="Remain indoors, keep indoor air clean",
                health_warning="Everyone should reduce outdoor exertion",
                precautions=["Avoid all outdoor activity", "Keep windows closed", "Run air purifier", "Seek medical care if symptoms worsen"],
                symptoms_to_watch=["Severe coughing", "Difficulty breathing", "Chest pain", "Confusion"]
            ),
            RiskCategory.HAZARDOUS: HealthAdvice(
                persona="General Public",
                risk_category="Hazardous",
                aqi_range=(301, 500),
                activity_recommendation="Avoid all outdoor activity, stay in well-sealed home",
                indoor_outdoor="Remain indoors, keep air quality safe",
                health_warning="Health emergency - severe health effects expected",
                precautions=["Avoid all outdoor activity", "Seal windows and doors", "Use HEPA air purifier", "Keep emergency supplies ready", "Follow local health warnings"],
                symptoms_to_watch=["Emergency symptoms requiring immediate medical attention", "Severe breathing difficulty", "Loss of consciousness"]
            )
        },
        Persona.CHILDREN: {
            RiskCategory.GOOD: HealthAdvice(
                persona="Children",
                risk_category="Good",
                aqi_range=(0, 50),
                activity_recommendation="All outdoor activities are appropriate",
                indoor_outdoor="Normal outdoor play and activities",
                health_warning=None,
                precautions=[],
                symptoms_to_watch=[]
            ),
            RiskCategory.MODERATE: HealthAdvice(
                persona="Children",
                risk_category="Moderate",
                aqi_range=(51, 100),
                activity_recommendation="Outdoor play is acceptable",
                indoor_outdoor="Encourage outdoor activities with breaks",
                health_warning="Some children may be sensitive to air quality",
                precautions=["Monitor children for respiratory symptoms", "Take frequent breaks from play"],
                symptoms_to_watch=["Coughing during play", "Difficulty keeping up with peers"]
            ),
            RiskCategory.UNHEALTHY_FOR_SENSITIVE: HealthAdvice(
                persona="Children",
                risk_category="Unhealthy for Sensitive Groups",
                aqi_range=(101, 150),
                activity_recommendation="Limit outdoor activity, especially vigorous play",
                indoor_outdoor="Move vigorous activities indoors",
                health_warning="Children should reduce outdoor exposure",
                precautions=["Keep children indoors as much as possible", "Avoid vigorous outdoor play", "Have rescue inhaler accessible"],
                symptoms_to_watch=["Persistent coughing", "Wheezing", "Chest tightness", "Difficulty keeping up with peers"]
            ),
            RiskCategory.UNHEALTHY: HealthAdvice(
                persona="Children",
                risk_category="Unhealthy",
                aqi_range=(151, 200),
                activity_recommendation="Avoid outdoor activity",
                indoor_outdoor="Keep children indoors, use air purifier",
                health_warning="Children should avoid outdoor exposure",
                precautions=["Keep children indoors", "Avoid outdoor activities", "Keep medications accessible", "Monitor closely for symptoms"],
                symptoms_to_watch=["Severe coughing", "Wheezing", "Difficulty breathing", "Fatigue", "Asthma attacks"]
            ),
            RiskCategory.VERY_UNHEALTHY: HealthAdvice(
                persona="Children",
                risk_category="Very Unhealthy",
                aqi_range=(201, 300),
                activity_recommendation="Strictly avoid all outdoor activity",
                indoor_outdoor="Keep indoors in air-filtered environment",
                health_warning="Children at high risk - strict protection needed",
                precautions=["Keep children indoors in sealed rooms", "Use HEPA air purifier continuously", "Have emergency action plan ready", "Monitor vital signs", "Seek medical attention for any respiratory symptoms"],
                symptoms_to_watch=["Severe respiratory distress", "Inability to engage in normal activities", "Altered mental status"]
            ),
            RiskCategory.HAZARDOUS: HealthAdvice(
                persona="Children",
                risk_category="Hazardous",
                aqi_range=(301, 500),
                activity_recommendation="Complete avoidance of outdoor exposure",
                indoor_outdoor="Remain in protected indoor environment",
                health_warning="Health emergency - children at critical risk",
                precautions=["Keep in sealed environment", "Use HEPA filtration system", "Have emergency medical plan", "Follow local emergency guidance", "Be prepared to relocate if necessary"],
                symptoms_to_watch=["Severe respiratory failure symptoms", "Unconsciousness", "Emergency medical intervention required"]
            )
        },
        Persona.ELDERLY: {
            RiskCategory.GOOD: HealthAdvice(
                persona="Elderly",
                risk_category="Good",
                aqi_range=(0, 50),
                activity_recommendation="All outdoor activities appropriate",
                indoor_outdoor="Normal outdoor activity",
                health_warning=None,
                precautions=[],
                symptoms_to_watch=[]
            ),
            RiskCategory.MODERATE: HealthAdvice(
                persona="Elderly",
                risk_category="Moderate",
                aqi_range=(51, 100),
                activity_recommendation="Outdoor activity acceptable with awareness",
                indoor_outdoor="Enjoy outdoor activities with monitoring",
                health_warning="Elderly with respiratory conditions should be cautious",
                precautions=["Check air quality before outdoor activities", "Have medications accessible"],
                symptoms_to_watch=["Fatigue", "Shortness of breath", "Chest discomfort"]
            ),
            RiskCategory.UNHEALTHY_FOR_SENSITIVE: HealthAdvice(
                persona="Elderly",
                risk_category="Unhealthy for Sensitive Groups",
                aqi_range=(101, 150),
                activity_recommendation="Limit outdoor exertion",
                indoor_outdoor="Reduce outdoor time, especially strenuous activities",
                health_warning="Elderly should limit outdoor exposure",
                precautions=["Reduce outdoor activity", "Avoid strenuous exercise", "Keep emergency contacts handy", "Take frequent breaks"],
                symptoms_to_watch=["Chest pain", "Shortness of breath", "Dizziness", "Irregular heartbeat"]
            ),
            RiskCategory.UNHEALTHY: HealthAdvice(
                persona="Elderly",
                risk_category="Unhealthy",
                aqi_range=(151, 200),
                activity_recommendation="Avoid outdoor activity",
                indoor_outdoor="Stay indoors with good air filtration",
                health_warning="Elderly at increased health risk",
                precautions=["Stay indoors", "Use air purifier", "Avoid all strenuous activity", "Check on others", "Have medications ready"],
                symptoms_to_watch=["Severe chest pain", "Difficulty breathing", "Dizziness", "Confusion", "Cardiac symptoms"]
            ),
            RiskCategory.VERY_UNHEALTHY: HealthAdvice(
                persona="Elderly",
                risk_category="Very Unhealthy",
                aqi_range=(201, 300),
                activity_recommendation="Strictly limit outdoor exposure",
                indoor_outdoor="Remain indoors in safe environment",
                health_warning="Elderly at very high risk",
                precautions=["Remain indoors continuously", "Use HEPA air purifier", "Have medical support available", "Monitor health closely", "Limit physical activity to minimum"],
                symptoms_to_watch=["Cardiac distress", "Severe breathing difficulty", "Confusion or disorientation", "Fainting"]
            ),
            RiskCategory.HAZARDOUS: HealthAdvice(
                persona="Elderly",
                risk_category="Hazardous",
                aqi_range=(301, 500),
                activity_recommendation="Complete avoidance of outdoor air",
                indoor_outdoor="Remain in protected environment",
                health_warning="Health emergency - critical risk",
                precautions=["Stay in sealed, filtered environment", "Continuous medical monitoring recommended", "Have emergency medical plan", "Consider evacuation if necessary"],
                symptoms_to_watch=["Critical cardiac or respiratory emergency", "Loss of consciousness", "Immediate emergency medical care needed"]
            )
        },
        Persona.ATHLETES: {
            RiskCategory.GOOD: HealthAdvice(
                persona="Athletes",
                risk_category="Good",
                aqi_range=(0, 50),
                activity_recommendation="All outdoor training appropriate",
                indoor_outdoor="Ideal conditions for outdoor training",
                health_warning=None,
                precautions=[],
                symptoms_to_watch=[]
            ),
            RiskCategory.MODERATE: HealthAdvice(
                persona="Athletes",
                risk_category="Moderate",
                aqi_range=(51, 100),
                activity_recommendation="Outdoor training acceptable",
                indoor_outdoor="Training can continue outdoors",
                health_warning="Consider air quality in training plans",
                precautions=["Monitor performance", "Adjust intensity if needed", "Stay hydrated"],
                symptoms_to_watch=["Difficulty maintaining performance", "Abnormal fatigue"]
            ),
            RiskCategory.UNHEALTHY_FOR_SENSITIVE: HealthAdvice(
                persona="Athletes",
                risk_category="Unhealthy for Sensitive Groups",
                aqi_range=(101, 150),
                activity_recommendation="Reduce outdoor training intensity",
                indoor_outdoor="Move vigorous training indoors",
                health_warning="Athletes should reduce outdoor exertion",
                precautions=["Move intense training indoors", "Reduce workout duration", "Lower exercise intensity", "Use air purifier"],
                symptoms_to_watch=["Throat irritation", "Chest tightness during exercise", "Coughing", "Reduced endurance"]
            ),
            RiskCategory.UNHEALTHY: HealthAdvice(
                persona="Athletes",
                risk_category="Unhealthy",
                aqi_range=(151, 200),
                activity_recommendation="Move training indoors",
                indoor_outdoor="All training should be indoors",
                health_warning="Avoid outdoor exertion",
                precautions=["Train indoors only", "Use treadmills/indoor facilities", "Reduce overall training volume", "Avoid hard efforts"],
                symptoms_to_watch=["Severe throat irritation", "Bronchial symptoms", "Chest pain during exercise", "Shortness of breath at rest"]
            ),
            RiskCategory.VERY_UNHEALTHY: HealthAdvice(
                persona="Athletes",
                risk_category="Very Unhealthy",
                aqi_range=(201, 300),
                activity_recommendation="Avoid strenuous training",
                indoor_outdoor="Rest day or light indoor activity only",
                health_warning="Intense exercise not recommended",
                precautions=["Take rest days", "No strenuous training", "Light indoor walking only", "Use air purifier", "Stay well hydrated"],
                symptoms_to_watch=["Serious respiratory symptoms", "Inability to train", "Persistent coughing"]
            ),
            RiskCategory.HAZARDOUS: HealthAdvice(
                persona="Athletes",
                risk_category="Hazardous",
                aqi_range=(301, 500),
                activity_recommendation="No physical training",
                indoor_outdoor="Complete rest, minimal activity",
                health_warning="No exercise recommended",
                precautions=["Complete training suspension", "Minimal physical activity", "Stay indoors with air filtration", "Seek medical advice"],
                symptoms_to_watch=["Emergency respiratory symptoms", "Cardiac symptoms", "Medical emergency signs"]
            )
        },
        Persona.OUTDOOR_WORKERS: {
            RiskCategory.GOOD: HealthAdvice(
                persona="Outdoor Workers",
                risk_category="Good",
                aqi_range=(0, 50),
                activity_recommendation="No work restrictions",
                indoor_outdoor="Normal outdoor work",
                health_warning=None,
                precautions=[],
                symptoms_to_watch=[]
            ),
            RiskCategory.MODERATE: HealthAdvice(
                persona="Outdoor Workers",
                risk_category="Moderate",
                aqi_range=(51, 100),
                activity_recommendation="Normal outdoor work with breaks",
                indoor_outdoor="Outdoor work acceptable",
                health_warning="Sensitive workers should monitor symptoms",
                precautions=["Take frequent breaks indoors", "Stay hydrated", "Monitor symptoms"],
                symptoms_to_watch=["Throat irritation", "Fatigue"]
            ),
            RiskCategory.UNHEALTHY_FOR_SENSITIVE: HealthAdvice(
                persona="Outdoor Workers",
                risk_category="Unhealthy for Sensitive Groups",
                aqi_range=(101, 150),
                activity_recommendation="Reduce outdoor work time",
                indoor_outdoor="Limit outdoor exposure, take breaks indoors",
                health_warning="Sensitive workers should consider reduced outdoor time",
                precautions=["Increase indoor break time", "Move non-essential tasks indoors", "Wear N95 mask", "Monitor symptoms closely"],
                symptoms_to_watch=["Persistent throat irritation", "Chest discomfort", "Respiratory symptoms"]
            ),
            RiskCategory.UNHEALTHY: HealthAdvice(
                persona="Outdoor Workers",
                risk_category="Unhealthy",
                aqi_range=(151, 200),
                activity_recommendation="Significantly reduce outdoor work",
                indoor_outdoor="Move work indoors when possible",
                health_warning="Limit outdoor work to essential tasks",
                precautions=["Move to indoor work if possible", "Use respiratory protection (N95/P100)", "Limit outdoor time to essential tasks only", "Take frequent breaks"],
                symptoms_to_watch=["Severe throat irritation", "Chest pain", "Difficulty breathing"]
            ),
            RiskCategory.VERY_UNHEALTHY: HealthAdvice(
                persona="Outdoor Workers",
                risk_category="Very Unhealthy",
                aqi_range=(201, 300),
                activity_recommendation="Minimal outdoor work",
                indoor_outdoor="Work indoors, avoid outdoor exposure",
                health_warning="Outdoor work not recommended",
                precautions=["Move all work indoors", "Only venture outside for emergencies", "Use HEPA respirator if must go outside", "Monitor health continuously"],
                symptoms_to_watch=["Severe respiratory distress", "Unable to work", "Medical symptoms developing"]
            ),
            RiskCategory.HAZARDOUS: HealthAdvice(
                persona="Outdoor Workers",
                risk_category="Hazardous",
                aqi_range=(301, 500),
                activity_recommendation="No outdoor work",
                indoor_outdoor="Work indoors only",
                health_warning="Do not work outdoors",
                precautions=["No outdoor work", "Remain indoors with air filtration", "Consider evacuation if necessary", "Follow emergency guidelines"],
                symptoms_to_watch=["Emergency medical symptoms", "Respiratory failure signs"]
            )
        }
    }


class HealthRiskClassifier:
    """
    Main classifier for health risk assessment based on AQI values.
    
    Provides:
    - Risk classification based on EPA/WHO thresholds
    - Personalized health advice for different personas
    - Health effects and recommendations
    - JSON-friendly output
    """
    
    def __init__(self):
        """Initialize the classifier with thresholds and mappings"""
        self.thresholds = {
            'PM2.5': AQIThresholds.PM25_THRESHOLDS,
            'PM10': AQIThresholds.PM10_THRESHOLDS,
            'NO2': AQIThresholds.NO2_THRESHOLDS,
            'O3': AQIThresholds.O3_THRESHOLDS,
            'SO2': AQIThresholds.SO2_THRESHOLDS,
            'CO': AQIThresholds.CO_THRESHOLDS
        }
        self.effects = HealthEffectsMapping.EFFECTS
        self.persona_advice = PersonaHealthAdviceMapping.ADVICE
        logger.info("HealthRiskClassifier initialized")
    
    def classify_aqi(self, aqi_value: float, parameter: str = 'PM2.5') -> RiskCategory:
        """
        Classify AQI value into risk category based on EPA thresholds.
        
        Args:
            aqi_value: Numeric AQI value
            parameter: Air quality parameter (PM2.5, PM10, etc.)
        
        Returns:
            RiskCategory enum value
        
        Raises:
            ValueError: If parameter not supported or value invalid
        """
        if parameter not in self.thresholds:
            raise ValueError(f"Unsupported parameter: {parameter}")
        
        if aqi_value < 0:
            raise ValueError(f"AQI value must be non-negative: {aqi_value}")
        
        thresholds = self.thresholds[parameter]
        
        for category, (low, high) in thresholds.items():
            if low <= aqi_value <= high:
                logger.debug(f"AQI {aqi_value} ({parameter}) classified as {category.value}")
                return category
        
        # Should not reach here with valid value
        return RiskCategory.HAZARDOUS
    
    def get_color_code(self, risk_category: RiskCategory) -> str:
        """
        Get EPA AQI color code for risk category.
        
        Args:
            risk_category: RiskCategory enum value
        
        Returns:
            Hex color code string
        """
        color_map = {
            RiskCategory.GOOD: "#00E400",  # Green
            RiskCategory.MODERATE: "#FFFF00",  # Yellow
            RiskCategory.UNHEALTHY_FOR_SENSITIVE: "#FF7E00",  # Orange
            RiskCategory.UNHEALTHY: "#FF0000",  # Red
            RiskCategory.VERY_UNHEALTHY: "#8F3F97",  # Purple
            RiskCategory.HAZARDOUS: "#7E0023"  # Maroon
        }
        return color_map.get(risk_category, "#000000")
    
    def get_health_effects(self, risk_category: RiskCategory) -> List[str]:
        """
        Get health effects for risk category.
        
        Args:
            risk_category: RiskCategory enum value
        
        Returns:
            List of health effect descriptions
        """
        return self.effects.get(risk_category, [])
    
    def get_at_risk_populations(self, risk_category: RiskCategory) -> List[str]:
        """
        Get populations at risk for given AQI level.
        
        Args:
            risk_category: RiskCategory enum value
        
        Returns:
            List of at-risk population groups
        """
        at_risk_map = {
            RiskCategory.GOOD: [],
            RiskCategory.MODERATE: ["Unusually sensitive people"],
            RiskCategory.UNHEALTHY_FOR_SENSITIVE: [
                "People with asthma",
                "Children and elderly",
                "People with respiratory conditions"
            ],
            RiskCategory.UNHEALTHY: [
                "General population",
                "Children and elderly",
                "People with asthma and respiratory conditions",
                "People with heart disease"
            ],
            RiskCategory.VERY_UNHEALTHY: [
                "Entire population",
                "Severe effects on sensitive groups",
                "Health emergency for vulnerable groups"
            ],
            RiskCategory.HAZARDOUS: [
                "Entire population at risk",
                "Emergency health conditions",
                "All groups affected"
            ]
        }
        return at_risk_map.get(risk_category, [])
    
    def get_personalized_advice(
        self,
        risk_category: RiskCategory,
        persona: Persona
    ) -> Optional[HealthAdvice]:
        """
        Get personalized health advice for specific persona and risk level.
        
        Args:
            risk_category: RiskCategory enum value
            persona: Persona enum value
        
        Returns:
            HealthAdvice dataclass or None if not available
        """
        if persona not in self.persona_advice:
            logger.warning(f"No advice available for persona: {persona.value}")
            return None
        
        persona_advice_map = self.persona_advice[persona]
        advice = persona_advice_map.get(risk_category)
        
        if advice:
            logger.debug(f"Retrieved advice for {persona.value} at {risk_category.value}")
        
        return advice
    
    def get_recommended_actions(self, risk_category: RiskCategory) -> Dict[str, str]:
        """
        Get recommended actions for risk category.
        
        Args:
            risk_category: RiskCategory enum value
        
        Returns:
            Dictionary of actions by type
        """
        actions = {
            RiskCategory.GOOD: {
                "General": "Enjoy outdoor activities",
                "Exercise": "All activities are appropriate",
                "Outdoor": "Normal outdoor activity encouraged"
            },
            RiskCategory.MODERATE: {
                "General": "Air quality is satisfactory",
                "Exercise": "Moderate activity acceptable",
                "Outdoor": "Outdoor activities can continue"
            },
            RiskCategory.UNHEALTHY_FOR_SENSITIVE: {
                "General": "Sensitive groups should limit outdoor exposure",
                "Exercise": "Sensitive groups should reduce exertion",
                "Outdoor": "Limit outdoor time for sensitive groups",
                "Protection": "Use air purifiers indoors"
            },
            RiskCategory.UNHEALTHY: {
                "General": "Reduce outdoor activity",
                "Exercise": "Limit strenuous outdoor exercise",
                "Outdoor": "Limit time outdoors",
                "Protection": "Use N95 mask outdoors, air purifier indoors"
            },
            RiskCategory.VERY_UNHEALTHY: {
                "General": "Avoid outdoor activity",
                "Exercise": "Avoid strenuous activity",
                "Outdoor": "Stay indoors as much as possible",
                "Protection": "Use HEPA air purifier, keep windows closed"
            },
            RiskCategory.HAZARDOUS: {
                "General": "Stay indoors, avoid all outdoor activity",
                "Exercise": "No outdoor exercise",
                "Outdoor": "Minimize outdoor exposure",
                "Protection": "Use HEPA air purifier, seal windows and doors"
            }
        }
        return actions.get(risk_category, {})
    
    def assess_health_risk(
        self,
        aqi_value: float,
        parameter: str = 'PM2.5',
        personas: Optional[List[Persona]] = None
    ) -> HealthRiskAssessment:
        """
        Perform comprehensive health risk assessment.
        
        Args:
            aqi_value: Numeric AQI value
            parameter: Air quality parameter (default: PM2.5)
            personas: List of personas to assess for (default: all)
        
        Returns:
            HealthRiskAssessment dataclass with complete assessment
        """
        # Classify risk
        risk_category = self.classify_aqi(aqi_value, parameter)
        
        # Get general information
        color_code = self.get_color_code(risk_category)
        health_effects = self.get_health_effects(risk_category)
        at_risk_populations = self.get_at_risk_populations(risk_category)
        recommended_actions = self.get_recommended_actions(risk_category)
        
        # Get personalized advice
        if personas is None:
            personas = list(Persona)
        
        personalized_advice = {}
        for persona in personas:
            advice = self.get_personalized_advice(risk_category, persona)
            if advice:
                personalized_advice[persona.value] = advice
        
        # Create assessment
        assessment = HealthRiskAssessment(
            aqi_value=aqi_value,
            aqi_parameter=parameter,
            risk_category=risk_category.value,
            color_code=color_code,
            general_advice=f"Air quality is {risk_category.value.lower()}",
            personalized_advice=personalized_advice,
            health_effects=health_effects,
            at_risk_populations=at_risk_populations,
            recommended_actions=recommended_actions,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Health risk assessment complete: {risk_category.value} for AQI={aqi_value}")
        return assessment
    
    def to_dict(self, assessment: HealthRiskAssessment) -> Dict:
        """
        Convert assessment to JSON-friendly dictionary.
        
        Args:
            assessment: HealthRiskAssessment dataclass
        
        Returns:
            Dictionary representation
        """
        # Convert main assessment
        result = asdict(assessment)
        
        # Convert personalized advice to dicts
        result['personalized_advice'] = {
            persona: asdict(advice)
            for persona, advice in assessment.personalized_advice.items()
        }
        
        return result
    
    def to_json(self, assessment: HealthRiskAssessment) -> str:
        """
        Convert assessment to JSON string.
        
        Args:
            assessment: HealthRiskAssessment dataclass
        
        Returns:
            JSON string representation
        """
        import json
        return json.dumps(self.to_dict(assessment), indent=2, default=str)


def create_classifier() -> HealthRiskClassifier:
    """
    Factory function to create and initialize classifier.
    
    Returns:
        Initialized HealthRiskClassifier instance
    """
    return HealthRiskClassifier()
