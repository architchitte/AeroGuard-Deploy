"""
Explainability Module for AQI Forecasts

Provides explainable AI logic (non-GenAI) for understanding:
- AQI trends (rising, falling, stable)
- Dominant contributing factors (AQI persistence, weather parameters)
- Pollution duration classification (temporary vs persistent)
- Structured explanation metadata

This module uses rule-based analysis and statistical methods to generate
interpretable explanations for AQI forecast behavior.
"""

import logging
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any
from statistics import mean, stdev
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class Trend(Enum):
    """AQI trend classification."""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"


class Duration(Enum):
    """Pollution duration classification."""
    TEMPORARY = "temporary"
    PERSISTENT = "persistent"


class ConfidenceLevel(Enum):
    """Confidence level for explanations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class TrendAnalysis:
    """Result of trend analysis."""
    trend: Trend
    slope: float  # AQI change per hour or time period
    change_percentage: float  # Percentage change over analysis period
    volatility: float  # Standard deviation of AQI values
    confidence: ConfidenceLevel


@dataclass
class Factor:
    """Represents a contributing factor to AQI trends."""
    name: str
    impact: str  # positive (worsening), negative (improving), neutral
    severity: float  # 0.0 to 1.0
    description: str


@dataclass
class FactorAnalysis:
    """Result of factor analysis."""
    aqi_persistence: float  # 0.0 to 1.0, how persistent is recent AQI
    weather_impact_score: float  # 0.0 to 1.0
    dominant_factors: List[Factor] = field(default_factory=list)
    secondary_factors: List[Factor] = field(default_factory=list)


@dataclass
class DurationAssessment:
    """Result of duration assessment."""
    duration: Duration
    expected_hours: int  # How long the condition is expected to last
    confidence: ConfidenceLevel
    reasoning: str


@dataclass
class ExplainabilityAssessment:
    """Complete explainability assessment for AQI forecast."""
    timestamp: datetime
    current_aqi: float
    trend: Trend
    main_factors: List[str]  # Simplified factor names for JSON output
    duration: Duration
    
    # Detailed analysis components
    trend_analysis: Optional[TrendAnalysis] = None
    factor_analysis: Optional[FactorAnalysis] = None
    duration_assessment: Optional[DurationAssessment] = None
    
    # Metadata
    confidence_overall: ConfidenceLevel = ConfidenceLevel.MEDIUM
    additional_context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "timestamp": self.timestamp.isoformat(),
            "current_aqi": self.current_aqi,
            "trend": self.trend.value,
            "main_factors": self.main_factors,
            "duration": self.duration.value,
            "confidence": self.confidence_overall.value
        }
        
        if self.trend_analysis:
            result["trend_details"] = {
                "slope": round(self.trend_analysis.slope, 3),
                "change_percentage": round(self.trend_analysis.change_percentage, 2),
                "volatility": round(self.trend_analysis.volatility, 2)
            }
        
        if self.duration_assessment:
            result["duration_details"] = {
                "expected_hours": self.duration_assessment.expected_hours,
                "reasoning": self.duration_assessment.reasoning
            }
        
        if self.additional_context:
            result["context"] = self.additional_context
        
        return result


class TrendAnalyzer:
    """Analyzes AQI trends from historical data."""
    
    # Threshold for considering change as significant
    MIN_CHANGE_PERCENTAGE = 2.0  # At least 2% change to be significant
    MIN_DATA_POINTS = 3
    
    @staticmethod
    def analyze(aqi_history: List[float], time_periods: Optional[List[int]] = None) -> TrendAnalysis:
        """
        Analyze AQI trend from historical values.
        
        Args:
            aqi_history: List of AQI values in chronological order
            time_periods: Optional list of time deltas (hours) between readings
        
        Returns:
            TrendAnalysis with trend classification and metrics
        
        Raises:
            ValueError: If insufficient data points
        """
        if len(aqi_history) < TrendAnalyzer.MIN_DATA_POINTS:
            raise ValueError(f"Need at least {TrendAnalyzer.MIN_DATA_POINTS} data points")
        
        # Calculate basic statistics
        current_aqi = aqi_history[-1]
        previous_aqi = aqi_history[0]
        aqi_change = current_aqi - previous_aqi
        change_percentage = (aqi_change / max(previous_aqi, 1)) * 100
        
        # Calculate volatility (standard deviation)
        if len(aqi_history) > 1:
            volatility = stdev(aqi_history)
        else:
            volatility = 0.0
        
        # Calculate slope (AQI change per period)
        slope = aqi_change / (len(aqi_history) - 1)
        
        # Determine trend
        if abs(change_percentage) < TrendAnalyzer.MIN_CHANGE_PERCENTAGE:
            trend = Trend.STABLE
            confidence = ConfidenceLevel.HIGH if volatility < 5 else ConfidenceLevel.MEDIUM
        elif aqi_change > 0:
            trend = Trend.RISING
            confidence = ConfidenceLevel.HIGH if slope > 1.0 else ConfidenceLevel.MEDIUM
        else:
            trend = Trend.FALLING
            confidence = ConfidenceLevel.HIGH if abs(slope) > 1.0 else ConfidenceLevel.MEDIUM
        
        return TrendAnalysis(
            trend=trend,
            slope=slope,
            change_percentage=change_percentage,
            volatility=volatility,
            confidence=confidence
        )


class FactorAnalyzer:
    """Identifies dominant contributing factors to AQI changes."""
    
    # Wind speed thresholds (m/s)
    WIND_SPEED_THRESHOLD = 3.0  # Low wind = < 3 m/s
    
    # Humidity thresholds (%)
    HUMIDITY_THRESHOLD_HIGH = 70  # High humidity
    HUMIDITY_THRESHOLD_LOW = 40   # Low humidity
    
    # AQI persistence thresholds
    PERSISTENCE_THRESHOLD_HIGH = 0.7
    PERSISTENCE_THRESHOLD_MEDIUM = 0.4
    
    @staticmethod
    def analyze(
        aqi_history: List[float],
        trend: Trend,
        wind_speed_history: Optional[List[float]] = None,
        humidity_history: Optional[List[float]] = None,
        temperature_history: Optional[List[float]] = None
    ) -> FactorAnalysis:
        """
        Identify dominant factors contributing to AQI trends.
        
        Args:
            aqi_history: Historical AQI values
            trend: Current trend classification
            wind_speed_history: Optional wind speed values (m/s)
            humidity_history: Optional humidity values (%)
            temperature_history: Optional temperature values (°C)
        
        Returns:
            FactorAnalysis with dominant and secondary factors
        """
        dominant_factors: List[Factor] = []
        secondary_factors: List[Factor] = []
        
        # Calculate AQI persistence
        aqi_persistence = FactorAnalyzer._calculate_persistence(aqi_history)
        
        # Analyze wind impact
        wind_impact_score = 0.0
        if wind_speed_history and len(wind_speed_history) > 0:
            avg_wind = mean(wind_speed_history)
            wind_impact_score = FactorAnalyzer._analyze_wind(
                avg_wind, trend, dominant_factors, secondary_factors
            )
        
        # Analyze humidity impact
        if humidity_history and len(humidity_history) > 0:
            FactorAnalyzer._analyze_humidity(
                humidity_history, trend, dominant_factors, secondary_factors
            )
        
        # Analyze temperature impact
        if temperature_history and len(temperature_history) > 0:
            FactorAnalyzer._analyze_temperature(
                temperature_history, trend, dominant_factors, secondary_factors
            )
        
        # Add AQI persistence as factor
        if aqi_persistence > FactorAnalyzer.PERSISTENCE_THRESHOLD_HIGH:
            persistence_impact = "positive" if trend == Trend.RISING else "negative"
            dominant_factors.append(Factor(
                name="high AQI persistence",
                impact=persistence_impact,
                severity=aqi_persistence,
                description="Recent AQI levels are persisting strongly"
            ))
        elif aqi_persistence > FactorAnalyzer.PERSISTENCE_THRESHOLD_MEDIUM:
            persistence_impact = "positive" if trend == Trend.RISING else "negative"
            secondary_factors.append(Factor(
                name="moderate AQI persistence",
                impact=persistence_impact,
                severity=aqi_persistence,
                description="Recent AQI levels show moderate persistence"
            ))
        
        # Sort by severity
        dominant_factors.sort(key=lambda f: f.severity, reverse=True)
        secondary_factors.sort(key=lambda f: f.severity, reverse=True)
        
        return FactorAnalysis(
            dominant_factors=dominant_factors,
            secondary_factors=secondary_factors,
            aqi_persistence=aqi_persistence,
            weather_impact_score=wind_impact_score
        )
    
    @staticmethod
    def _calculate_persistence(aqi_history: List[float]) -> float:
        """Calculate how much recent AQI values persist (autocorrelation)."""
        if len(aqi_history) < 2:
            return 0.5
        
        # Simple persistence: correlation between consecutive readings
        diffs = [abs(aqi_history[i] - aqi_history[i-1]) for i in range(1, len(aqi_history))]
        
        if not diffs:
            return 0.5
        
        # High variance in differences = low persistence
        # Low variance in differences = high persistence
        avg_diff = mean(diffs)
        max_diff = max(diffs)
        
        if max_diff == 0:
            persistence = 1.0
        else:
            persistence = 1.0 - (avg_diff / max_diff)
        
        return max(0.0, min(1.0, persistence))
    
    @staticmethod
    def _analyze_wind(
        avg_wind: float,
        trend: Trend,
        dominant_factors: List[Factor],
        secondary_factors: List[Factor]
    ) -> float:
        """Analyze wind speed impact on AQI."""
        impact_score = 0.0
        
        if avg_wind < FactorAnalyzer.WIND_SPEED_THRESHOLD:
            # Low wind worsens AQI (stagnant conditions)
            severity = 1.0 - (avg_wind / FactorAnalyzer.WIND_SPEED_THRESHOLD)
            impact_score = severity
            
            factor = Factor(
                name="low wind speed",
                impact="positive" if trend == Trend.RISING else "neutral",
                severity=severity,
                description=f"Wind speed ({avg_wind:.1f} m/s) is low, reducing pollution dispersion"
            )
            
            if severity > 0.6:
                dominant_factors.append(factor)
            else:
                secondary_factors.append(factor)
        else:
            # High wind improves AQI (dispersion)
            severity = (avg_wind - FactorAnalyzer.WIND_SPEED_THRESHOLD) / 5.0
            severity = min(1.0, severity)
            impact_score = -severity  # Negative impact (improvement)
            
            if severity > 0.3:
                factor = Factor(
                    name="good wind dispersion",
                    impact="negative",
                    severity=severity,
                    description=f"Wind speed ({avg_wind:.1f} m/s) aids pollution dispersion"
                )
                secondary_factors.append(factor)
        
        return max(0.0, min(1.0, impact_score))
    
    @staticmethod
    def _analyze_humidity(
        humidity_history: List[float],
        trend: Trend,
        dominant_factors: List[Factor],
        secondary_factors: List[Factor]
    ) -> None:
        """Analyze humidity impact on AQI."""
        avg_humidity = mean(humidity_history)
        
        if avg_humidity > FactorAnalyzer.HUMIDITY_THRESHOLD_HIGH:
            # High humidity can increase aerosol formation
            severity = (avg_humidity - FactorAnalyzer.HUMIDITY_THRESHOLD_HIGH) / 30.0
            severity = min(1.0, severity)
            
            factor = Factor(
                name="high humidity",
                impact="positive" if trend == Trend.RISING else "neutral",
                severity=severity,
                description=f"High humidity ({avg_humidity:.1f}%) may increase aerosol formation"
            )
            
            if severity > 0.5:
                dominant_factors.append(factor)
            else:
                secondary_factors.append(factor)
        
        elif avg_humidity < FactorAnalyzer.HUMIDITY_THRESHOLD_LOW:
            # Very low humidity can suspend fine particles
            severity = (FactorAnalyzer.HUMIDITY_THRESHOLD_LOW - avg_humidity) / 40.0
            severity = min(1.0, severity)
            
            if severity > 0.4:
                factor = Factor(
                    name="low humidity",
                    impact="neutral",
                    severity=severity,
                    description=f"Low humidity ({avg_humidity:.1f}%) may keep particles suspended"
                )
                secondary_factors.append(factor)
    
    @staticmethod
    def _analyze_temperature(
        temperature_history: List[float],
        trend: Trend,
        dominant_factors: List[Factor],
        secondary_factors: List[Factor]
    ) -> None:
        """Analyze temperature impact on AQI."""
        avg_temp = mean(temperature_history)
        
        if avg_temp < 0:
            # Cold temperatures can trap pollution
            severity = min(1.0, abs(avg_temp) / 20.0)
            
            factor = Factor(
                name="cold temperature",
                impact="positive" if trend == Trend.RISING else "neutral",
                severity=severity,
                description=f"Cold temperatures ({avg_temp:.1f}°C) can trap pollution near surface"
            )
            
            if severity > 0.5:
                secondary_factors.append(factor)
        
        elif avg_temp > 25:
            # High temperatures can increase secondary pollutant formation
            severity = min(1.0, (avg_temp - 25) / 20.0)
            
            if severity > 0.4:
                factor = Factor(
                    name="high temperature",
                    impact="positive" if trend == Trend.RISING else "neutral",
                    severity=severity,
                    description=f"High temperatures ({avg_temp:.1f}°C) may increase secondary pollutants"
                )
                secondary_factors.append(factor)


class DurationAssessor:
    """Assesses whether pollution is temporary or persistent."""
    
    # Thresholds for duration classification
    PERSISTENCE_THRESHOLD = 0.6  # > 0.6 = persistent
    VOLATILITY_THRESHOLD = 15.0  # > 15 = more temporary
    
    @staticmethod
    def assess(
        aqi_history: List[float],
        trend: Trend,
        aqi_persistence: float,
        volatility: float,
        weather_conditions_improving: Optional[bool] = None
    ) -> DurationAssessment:
        """
        Assess whether pollution is temporary or persistent.
        
        Args:
            aqi_history: Historical AQI values
            trend: Current trend classification
            aqi_persistence: Persistence score (0-1)
            volatility: AQI volatility (standard deviation)
            weather_conditions_improving: Optional indicator if weather will improve
        
        Returns:
            DurationAssessment with duration classification and expected hours
        """
        # Primary indicator: persistence
        if aqi_persistence > DurationAssessor.PERSISTENCE_THRESHOLD:
            duration = Duration.PERSISTENT
            expected_hours = 24  # Persistent conditions typically last > 24 hours
            reasoning = "High AQI persistence indicates conditions will continue"
        elif volatility > DurationAssessor.VOLATILITY_THRESHOLD:
            duration = Duration.TEMPORARY
            expected_hours = 6  # Volatile conditions typically clear faster
            reasoning = "High AQI volatility suggests temporary conditions"
        else:
            # Fallback: use trend
            if trend == Trend.RISING:
                duration = Duration.PERSISTENT
                expected_hours = 18
                reasoning = "Rising trend suggests worsening conditions will persist"
            elif trend == Trend.FALLING:
                duration = Duration.TEMPORARY
                expected_hours = 12
                reasoning = "Falling trend suggests improving conditions"
            else:
                duration = Duration.PERSISTENT
                expected_hours = 18
                reasoning = "Stable conditions likely to continue"
        
        # Adjust based on weather outlook if provided
        if weather_conditions_improving is not None:
            if weather_conditions_improving and duration == Duration.PERSISTENT:
                expected_hours = max(6, expected_hours // 2)
                reasoning += "; however, improving weather may clear conditions faster"
            elif not weather_conditions_improving and duration == Duration.TEMPORARY:
                expected_hours = expected_hours * 2
                reasoning += "; but deteriorating weather may prolong conditions"
        
        # Determine confidence
        if aqi_persistence > 0.75 or volatility < 5:
            confidence = ConfidenceLevel.HIGH
        elif aqi_persistence > 0.5 or volatility < 20:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW
        
        return DurationAssessment(
            duration=duration,
            expected_hours=expected_hours,
            confidence=confidence,
            reasoning=reasoning
        )


class AQIExplainer:
    """Main class for generating explainability assessments for AQI forecasts."""
    
    def __init__(self, logger_instance: Optional[logging.Logger] = None):
        """
        Initialize the explainer.
        
        Args:
            logger_instance: Optional logger for debug output
        """
        self.logger = logger_instance or logger
    
    def explain(
        self,
        current_aqi: float,
        aqi_history: List[float],
        wind_speed_history: Optional[List[float]] = None,
        humidity_history: Optional[List[float]] = None,
        temperature_history: Optional[List[float]] = None,
        weather_improving: Optional[bool] = None
    ) -> ExplainabilityAssessment:
        """
        Generate a complete explainability assessment for AQI forecast.
        
        Args:
            current_aqi: Current AQI value
            aqi_history: List of AQI values (chronological order, latest last)
            wind_speed_history: Optional wind speed history (m/s)
            humidity_history: Optional humidity history (%)
            temperature_history: Optional temperature history (°C)
            weather_improving: Optional flag indicating weather outlook
        
        Returns:
            ExplainabilityAssessment with trend, factors, and duration
        
        Raises:
            ValueError: If insufficient data for analysis
        """
        if len(aqi_history) < 3:
            raise ValueError("Need at least 3 historical AQI values for analysis")
        
        self.logger.debug(f"Starting explainability analysis for AQI={current_aqi}")
        
        # 1. Analyze trend
        trend_analysis = TrendAnalyzer.analyze(aqi_history)
        self.logger.debug(f"Trend: {trend_analysis.trend.value}, slope: {trend_analysis.slope:.3f}")
        
        # 2. Analyze factors
        factor_analysis = FactorAnalyzer.analyze(
            aqi_history=aqi_history,
            trend=trend_analysis.trend,
            wind_speed_history=wind_speed_history,
            humidity_history=humidity_history,
            temperature_history=temperature_history
        )
        self.logger.debug(f"Found {len(factor_analysis.dominant_factors)} dominant factors")
        
        # 3. Assess duration
        duration_assessment = DurationAssessor.assess(
            aqi_history=aqi_history,
            trend=trend_analysis.trend,
            aqi_persistence=factor_analysis.aqi_persistence,
            volatility=trend_analysis.volatility,
            weather_conditions_improving=weather_improving
        )
        self.logger.debug(f"Duration: {duration_assessment.duration.value}")
        
        # 4. Extract simplified factor names for output
        main_factors = [f.name for f in factor_analysis.dominant_factors]
        if not main_factors and factor_analysis.secondary_factors:
            main_factors = [f.name for f in factor_analysis.secondary_factors[:2]]
        
        # Default factors if none identified
        if not main_factors:
            if trend_analysis.trend == Trend.RISING:
                main_factors = ["AQI persistence"]
            elif trend_analysis.trend == Trend.FALLING:
                main_factors = ["improving conditions"]
            else:
                main_factors = ["stable conditions"]
        
        # 5. Determine overall confidence
        confidence_scores = [
            trend_analysis.confidence,
            duration_assessment.confidence
        ]
        avg_confidence = sum(c.value == "high" for c in confidence_scores) / len(confidence_scores)
        if avg_confidence > 0.6:
            overall_confidence = ConfidenceLevel.HIGH
        elif avg_confidence > 0.3:
            overall_confidence = ConfidenceLevel.MEDIUM
        else:
            overall_confidence = ConfidenceLevel.LOW
        
        # 6. Build assessment
        assessment = ExplainabilityAssessment(
            timestamp=datetime.now(),
            current_aqi=current_aqi,
            trend=trend_analysis.trend,
            main_factors=main_factors,
            duration=duration_assessment.duration,
            trend_analysis=trend_analysis,
            factor_analysis=factor_analysis,
            duration_assessment=duration_assessment,
            confidence_overall=overall_confidence,
            additional_context={
                "num_dominant_factors": len(factor_analysis.dominant_factors),
                "num_secondary_factors": len(factor_analysis.secondary_factors),
                "aqi_persistence_score": round(factor_analysis.aqi_persistence, 3),
                "weather_impact_score": round(factor_analysis.weather_impact_score, 3)
            }
        )
        
        self.logger.debug(f"Explainability assessment complete: {assessment.trend.value}")
        return assessment


def create_explainer(logger_instance: Optional[logging.Logger] = None) -> AQIExplainer:
    """
    Factory function to create an AQIExplainer instance.
    
    Args:
        logger_instance: Optional logger instance
    
    Returns:
        Configured AQIExplainer instance
    """
    return AQIExplainer(logger_instance=logger_instance or logger)
