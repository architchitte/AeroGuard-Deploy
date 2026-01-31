"""
AQI Explainability Engine - Comprehensive Documentation

This document provides complete technical reference for the AQI Explainability
Engine, a rule-based system for interpreting AQI trends and identifying
contributing factors without requiring generative AI.

Table of Contents:
1. Architecture & Design
2. Core Concepts
3. API Reference
4. Usage Guide
5. Integration Patterns
6. Advanced Topics
7. Troubleshooting
8. Performance Considerations
"""


# ===========================================================================
# SECTION 1: ARCHITECTURE & DESIGN
# ===========================================================================

ARCHITECTURE = """
ARCHITECTURE & DESIGN
=====================

1.1 System Overview
-------------------

The Explainability Engine consists of three main analysis components that work
together to provide interpretable explanations of AQI behavior:

    ┌─────────────────────────────────────────────────────────────┐
    │                      AQIExplainer                           │
    │                   (Main Orchestrator)                       │
    └─────────────────┬──────────────────────┬────────────────────┘
                      │                      │
        ┌─────────────▼──────┐    ┌──────────▼──────────┐
        │  TrendAnalyzer     │    │  FactorAnalyzer    │
        │  ──────────────    │    │  ──────────────    │
        │ • Rising/Falling   │    │ • Wind Speed       │
        │ • Stable           │    │ • Humidity         │
        │ • Volatility       │    │ • Temperature      │
        │ • Confidence       │    │ • AQI Persistence  │
        └────────────────────┘    └────────────────────┘
                 │                          │
                 └──────────┬───────────────┘
                            │
                 ┌──────────▼──────────┐
                 │ DurationAssessor    │
                 │ ────────────────    │
                 │ • Temporary         │
                 │ • Persistent        │
                 │ • Expected Hours    │
                 │ • Reasoning         │
                 └─────────────────────┘
                            │
                 ┌──────────▼──────────────┐
                 │ ExplainabilityAssessment│
                 │ (Structured Output)     │
                 │ • Trend                 │
                 │ • Main Factors          │
                 │ • Duration              │
                 │ • JSON-serializable     │
                 └─────────────────────────┘


1.2 Design Philosophy
---------------------

The engine uses RULE-BASED LOGIC rather than machine learning or AI:

✓ Explainability: Every conclusion is based on transparent rules
✓ Interpretability: Results include reasoning for every finding
✓ Reliability: Behavior is predictable and auditable
✓ No ML dependency: Works without training data or complex models
✓ Real-time: Instant analysis without preprocessing
✓ Configurable: Easy to adjust thresholds and rules
✓ Compositional: Analysis components work independently or together


1.3 Data Flow
-------------

Input Data:
  • AQI history (required): List of historical AQI values
  • Wind speed history (optional): Wind speeds in m/s
  • Humidity history (optional): Humidity percentages
  • Temperature history (optional): Temperatures in °C
  • Weather outlook (optional): Boolean flag for improving conditions

Processing:
  1. TrendAnalyzer: Detects trend (rising/falling/stable) from AQI history
  2. FactorAnalyzer: Identifies contributing factors (wind, humidity, temp)
  3. DurationAssessor: Classifies pollution duration (temporary/persistent)

Output:
  ExplainabilityAssessment containing:
  • Trend classification with confidence
  • List of main contributing factors
  • Duration classification with expected hours
  • Detailed analysis components (optional)
  • JSON-serializable dictionary representation


# ===========================================================================
# SECTION 2: CORE CONCEPTS
# ===========================================================================

CORE_CONCEPTS = """
CORE CONCEPTS
=============

2.1 Trend Analysis
------------------

Trend classification determines whether AQI is rising, falling, or stable.

TREND TYPES:
• RISING: AQI increasing over time (pollution worsening)
• FALLING: AQI decreasing over time (air quality improving)
• STABLE: AQI change < 2% (conditions unchanged)

METRICS:
• Slope: AQI change per time period
• Change Percentage: Total % change from first to last value
• Volatility: Standard deviation of AQI values
• Confidence: Certainty of trend classification

CALCULATION LOGIC:
1. Calculate AQI change: current - initial
2. Calculate percentage: (change / max(initial, 1)) × 100
3. If |percentage| < 2.0% → STABLE
4. Else if change > 0 → RISING
5. Else → FALLING

CONFIDENCE DETERMINATION:
• STABLE with volatility < 5: HIGH confidence
• RISING with slope > 1.0: HIGH confidence  
• FALLING with |slope| > 1.0: HIGH confidence
• Otherwise: MEDIUM confidence


2.2 Factor Analysis
-------------------

Identifies which environmental factors are driving AQI changes.

PRIMARY FACTORS:
• Low wind speed (< 3.0 m/s): Reduces pollution dispersion
• High humidity (> 70%): Increases aerosol formation
• Low humidity (< 40%): May suspend fine particles
• Cold temperature (< 0°C): Traps pollution near surface
• High temperature (> 25°C): Increases secondary pollutants
• High AQI persistence: Recent AQI levels continuing

FACTOR SCORING:
Each factor receives a severity score from 0.0 to 1.0 based on:
• How extreme the condition is
• Historical wind: (actual_wind / threshold) → severity
• Humidity: (deviation_from_ideal) / (max_deviation) → severity
• AQI persistence: Autocorrelation of historical values

CLASSIFICATION:
Factors are classified as:
• Dominant: Severity > 0.6 or clear impact on trend
• Secondary: Severity 0.3-0.6 or minor impact
• Not listed: Severity < 0.3


2.3 Duration Classification
----------------------------

Determines whether pollution is temporary or persistent.

DURATION TYPES:
• TEMPORARY: Pollution expected to clear < 12 hours
• PERSISTENT: Pollution expected to last > 12 hours

DECISION RULES:
1. If AQI persistence > 0.6 → PERSISTENT
2. If AQI volatility > 15.0 → TEMPORARY
3. If trend RISING → PERSISTENT (12-24 hours)
4. If trend FALLING → TEMPORARY (6-12 hours)
5. If trend STABLE → PERSISTENT (18+ hours)

ADJUSTMENTS:
• If weather improving: reduce expected hours by 50%
• If weather deteriorating: increase expected hours by 2×

CONFIDENCE SCORING:
• High: Persistence > 0.75 or volatility < 5
• Medium: Persistence > 0.5 or volatility < 20
• Low: Otherwise


2.4 Structured Output
---------------------

All assessments are returned as structured data, not plain text:

{
  "timestamp": "2026-01-31T12:00:00",
  "current_aqi": 65.0,
  "trend": "rising",
  "main_factors": ["low wind speed", "high humidity"],
  "duration": "persistent",
  "confidence": "high",
  "trend_details": {
    "slope": 2.5,
    "change_percentage": 15.0,
    "volatility": 3.2
  },
  "duration_details": {
    "expected_hours": 18,
    "reasoning": "Rising trend suggests conditions will persist"
  },
  "context": {
    "num_dominant_factors": 2,
    "num_secondary_factors": 1,
    "aqi_persistence_score": 0.72,
    "weather_impact_score": 0.65
  }
}

This structure enables:
• Machine parsing and processing
• Integration with APIs and databases
• Consistent output format
• Rich metadata for debugging
"""


# ===========================================================================
# SECTION 3: API REFERENCE
# ===========================================================================

API_REFERENCE = """
API REFERENCE
=============

3.1 Main Class: AQIExplainer
----------------------------

Purpose: Main entry point for generating explainability assessments

Constructor:
    AQIExplainer(logger_instance: Optional[logging.Logger] = None)

Methods:
    explain(
        current_aqi: float,
        aqi_history: List[float],
        wind_speed_history: Optional[List[float]] = None,
        humidity_history: Optional[List[float]] = None,
        temperature_history: Optional[List[float]] = None,
        weather_improving: Optional[bool] = None
    ) -> ExplainabilityAssessment

Parameters:
• current_aqi: Current AQI value (0-500+)
• aqi_history: Historical AQI values in chronological order
               Minimum 3 values required
• wind_speed_history: Wind speeds in m/s (optional)
                      Should match length of aqi_history
• humidity_history: Humidity % (0-100) (optional)
                    Should match length of aqi_history
• temperature_history: Temperature in °C (optional)
                       Should match length of aqi_history
• weather_improving: Boolean flag for weather outlook (optional)
                     True = improving, False = deteriorating

Returns:
    ExplainabilityAssessment containing complete analysis

Raises:
    ValueError: If aqi_history has fewer than 3 values

Example:
    from app.services.explainability import create_explainer
    
    explainer = create_explainer()
    assessment = explainer.explain(
        current_aqi=65.0,
        aqi_history=[50.0, 55.0, 60.0, 65.0],
        wind_speed_history=[2.0, 1.5, 1.0, 0.8],
        humidity_history=[70.0, 75.0, 80.0, 82.0]
    )


3.2 Analyzer Classes
--------------------

TrendAnalyzer.analyze(aqi_history, time_periods=None)
    • Static method for analyzing AQI trends
    • Returns: TrendAnalysis
    • Raises: ValueError if < 3 data points

FactorAnalyzer.analyze(aqi_history, trend, wind_speed_history, ...)
    • Static method for identifying contributing factors
    • Returns: FactorAnalysis
    • Identifies dominant and secondary factors
    
DurationAssessor.assess(aqi_history, trend, aqi_persistence, volatility, ...)
    • Static method for duration classification
    • Returns: DurationAssessment
    • Includes expected hours and reasoning


3.3 Data Classes
----------------

TrendAnalysis:
    • trend: Trend enum (RISING, FALLING, STABLE)
    • slope: Float, AQI change per period
    • change_percentage: Float, total % change
    • volatility: Float, standard deviation
    • confidence: ConfidenceLevel (HIGH, MEDIUM, LOW)

FactorAnalysis:
    • aqi_persistence: Float (0.0-1.0)
    • weather_impact_score: Float (0.0-1.0)
    • dominant_factors: List[Factor]
    • secondary_factors: List[Factor]

Factor:
    • name: String (e.g., "low wind speed")
    • impact: String ("positive", "negative", "neutral")
    • severity: Float (0.0-1.0)
    • description: String (human-readable explanation)

DurationAssessment:
    • duration: Duration enum (TEMPORARY, PERSISTENT)
    • expected_hours: Int, expected duration
    • confidence: ConfidenceLevel
    • reasoning: String, explanation

ExplainabilityAssessment:
    • timestamp: datetime object
    • current_aqi: Float
    • trend: Trend
    • main_factors: List[String]
    • duration: Duration
    • confidence_overall: ConfidenceLevel
    • trend_analysis: TrendAnalysis (optional)
    • factor_analysis: FactorAnalysis (optional)
    • duration_assessment: DurationAssessment (optional)
    • additional_context: Dict[String, Any]

Methods:
    • to_dict(): Converts to JSON-serializable dictionary


3.4 Enumerations
----------------

Trend:
    • RISING = "rising"
    • FALLING = "falling"
    • STABLE = "stable"

Duration:
    • TEMPORARY = "temporary"
    • PERSISTENT = "persistent"

ConfidenceLevel:
    • HIGH = "high"
    • MEDIUM = "medium"
    • LOW = "low"


# ===========================================================================
# SECTION 4: USAGE GUIDE
# ===========================================================================

USAGE_GUIDE = """
USAGE GUIDE
===========

4.1 Basic Usage
---------------

Minimal example with only AQI history:

    from app.services.explainability import create_explainer
    
    explainer = create_explainer()
    
    # Provide only AQI data
    aqi_history = [50.0, 55.0, 60.0, 65.0]
    
    assessment = explainer.explain(
        current_aqi=65.0,
        aqi_history=aqi_history
    )
    
    # Access results
    print(f"Trend: {assessment.trend.value}")  # "rising"
    print(f"Duration: {assessment.duration.value}")  # "persistent"
    print(f"Factors: {assessment.main_factors}")  # List of factors


4.2 Complete Usage with Weather Data
-------------------------------------

Full example with all available data:

    from app.services.explainability import create_explainer
    
    explainer = create_explainer()
    
    # Hourly data for 6 hours
    aqi_history = [50.0, 55.0, 60.0, 68.0, 75.0, 78.0]
    wind_speed = [2.5, 2.0, 1.5, 1.0, 0.8, 0.6]
    humidity = [70.0, 72.0, 75.0, 78.0, 80.0, 82.0]
    temperature = [15.0, 14.0, 13.0, 12.0, 11.0, 10.0]
    
    assessment = explainer.explain(
        current_aqi=78.0,
        aqi_history=aqi_history,
        wind_speed_history=wind_speed,
        humidity_history=humidity,
        temperature_history=temperature,
        weather_improving=False
    )
    
    # Export to JSON
    import json
    result_json = json.dumps(assessment.to_dict(), indent=2, default=str)
    print(result_json)


4.3 Interpreting Results
------------------------

TREND:
• RISING: Pollution worsening
  → Check dominant factors
  → May need air quality warnings
  → Recommend reducing outdoor activities
  
• FALLING: Air quality improving
  → Check if factors responsible (wind, rain, etc.)
  → Conditions will continue improving
  → Can gradually increase outdoor activities
  
• STABLE: Conditions unchanged
  → Persistence important
  → If persistent + high AQI: long-term concern
  → If temporary: brief episode expected

DURATION:
• PERSISTENT: Pollution expected to last > 12 hours
  → Vulnerable populations should plan accordingly
  → May affect multiple days
  → Multiple interventions may be needed
  
• TEMPORARY: Pollution expected to clear < 12 hours
  → Short-term impact
  → Avoid peak hours
  → Recovery expected soon

FACTORS:
• Dominant factors: Primary drivers of current situation
  → Address for maximum impact
  → Most important for forecasting
  
• Secondary factors: Contributing but less important
  → May become important if primary factors change
  → Useful for detailed understanding

CONFIDENCE:
• HIGH: Results highly reliable
  → Can base decisions on assessment
  → Unlikely to be wrong
  
• MEDIUM: Results reasonably reliable
  → Useful for planning
  → May need to verify with other sources
  
• LOW: Results less certain
  → Use with caution
  → Verify with other indicators
  → More data may improve confidence


4.4 Integration with APIs
--------------------------

REST Endpoint Example:

    @app.post("/api/aqi/explain")
    def explain_aqi(request: ExplainRequest):
        explainer = create_explainer()
        
        assessment = explainer.explain(
            current_aqi=request.current_aqi,
            aqi_history=request.aqi_history,
            wind_speed_history=request.wind_speed,
            humidity_history=request.humidity,
            temperature_history=request.temperature,
            weather_improving=request.weather_outlook
        )
        
        return assessment.to_dict()


# ===========================================================================
# SECTION 5: INTEGRATION PATTERNS
# ===========================================================================

INTEGRATION_PATTERNS = """
INTEGRATION PATTERNS
====================

5.1 Real-time Monitoring Integration
-------------------------------------

Pattern: Stream AQI data, continuously update explanations

    from collections import deque
    from app.services.explainability import create_explainer
    
    class AQIMonitor:
        def __init__(self, window_size=6):
            self.explainer = create_explainer()
            self.aqi_history = deque(maxlen=window_size)
            self.wind_history = deque(maxlen=window_size)
            self.humidity_history = deque(maxlen=window_size)
        
        def update(self, aqi, wind, humidity):
            self.aqi_history.append(aqi)
            self.wind_history.append(wind)
            self.humidity_history.append(humidity)
            
            if len(self.aqi_history) < 3:
                return None
            
            return self.explainer.explain(
                current_aqi=self.aqi_history[-1],
                aqi_history=list(self.aqi_history),
                wind_speed_history=list(self.wind_history),
                humidity_history=list(self.humidity_history)
            )
    
    monitor = AQIMonitor()
    
    # As new data arrives
    new_assessment = monitor.update(
        aqi=65.0,
        wind=1.5,
        humidity=78.0
    )


5.2 Multi-location Comparison
-----------------------------

Pattern: Explain AQI for multiple locations simultaneously

    locations = {
        'city_center': [50, 55, 60, 65],
        'suburb_east': [45, 48, 50, 52],
        'suburb_west': [55, 65, 75, 85]
    }
    
    explainer = create_explainer()
    assessments = {}
    
    for location, aqi_hist in locations.items():
        assessment = explainer.explain(
            current_aqi=aqi_hist[-1],
            aqi_history=aqi_hist
        )
        assessments[location] = assessment.to_dict()
    
    # Compare across locations
    worst_location = max(
        assessments.items(),
        key=lambda x: x[1]['current_aqi']
    )


5.3 Forecast Enhancement
------------------------

Pattern: Enhance numerical forecasts with explainability

    def enhance_forecast(forecast_data):
        # Your existing forecast model
        forecast_aqi = model.predict(forecast_data)
        
        # Get historical data
        recent_aqi = get_recent_aqi(hours=6)
        
        # Add explanation
        explainer = create_explainer()
        explanation = explainer.explain(
            current_aqi=recent_aqi[-1],
            aqi_history=recent_aqi,
            wind_speed_history=forecast_data['wind'],
            humidity_history=forecast_data['humidity']
        )
        
        # Combine with forecast
        return {
            'forecast': forecast_aqi,
            'explanation': explanation.to_dict(),
            'confidence': explanation.confidence_overall.value
        }


5.4 Alert System Integration
-----------------------------

Pattern: Trigger alerts based on explainability assessment

    def check_alert_conditions(assessment):
        alerts = []
        
        # Persistent high AQI
        if (assessment.current_aqi > 150 and 
            assessment.duration == Duration.PERSISTENT):
            alerts.append({
                'type': 'HAZARDOUS_PERSISTENT',
                'severity': 'CRITICAL',
                'message': 'Hazardous air expected to persist > 12 hours'
            })
        
        # Rapidly worsening
        if (assessment.trend == Trend.RISING and 
            assessment.confidence_overall == ConfidenceLevel.HIGH):
            alerts.append({
                'type': 'RAPID_DETERIORATION',
                'severity': 'WARNING',
                'reason': ' '.join(assessment.main_factors)
            })
        
        # Low wind stagnation
        if 'low wind speed' in assessment.main_factors:
            alerts.append({
                'type': 'STAGNANT_CONDITIONS',
                'severity': 'INFO',
                'message': 'Poor wind dispersion expected'
            })
        
        return alerts


# ===========================================================================
# SECTION 6: ADVANCED TOPICS
# ===========================================================================

ADVANCED_TOPICS = """
ADVANCED TOPICS
===============

6.1 Customizing Analysis Thresholds
-----------------------------------

Default thresholds can be modified for specific use cases:

    # Example: Adjust wind speed threshold for coastal areas
    class CoastalFactorAnalyzer(FactorAnalyzer):
        WIND_SPEED_THRESHOLD = 2.0  # Lower threshold for coast
        HUMIDITY_THRESHOLD_HIGH = 80  # Higher humidity normal

    # Use custom analyzer
    analysis = CoastalFactorAnalyzer.analyze(
        aqi_history=aqi_hist,
        trend=trend
    )


6.2 Confidence Weighting
------------------------

Use confidence levels to weight decisions:

    assessment = explainer.explain(...)
    
    if assessment.confidence_overall == ConfidenceLevel.HIGH:
        # High confidence: can act decisively
        issue_alert(assessment)
    elif assessment.confidence_overall == ConfidenceLevel.MEDIUM:
        # Medium confidence: verify with other sources
        verify_with_satellite_data(assessment)
    else:
        # Low confidence: wait for more data
        collect_more_data()


6.3 Combining Multiple Assessments
----------------------------------

Aggregate results from multiple analysis runs:

    # Historical trend analysis
    hist_assessment = explainer.explain(aqi_history)
    
    # Recent trend analysis (last 3 hours)
    recent_assessment = explainer.explain(aqi_history[-3:])
    
    # Compare to identify change points
    if hist_assessment.trend != recent_assessment.trend:
        print("Trend shift detected!")


6.4 Performance Optimization
----------------------------

For high-frequency updates with large history:

    # Cache analysis results
    from functools import lru_cache
    
    @lru_cache(maxsize=128)
    def cached_explain(current_aqi, aqi_tuple):
        return explainer.explain(
            current_aqi=current_aqi,
            aqi_history=list(aqi_tuple)
        )
    
    # Only run on significant changes
    if abs(new_aqi - last_aqi) > 2.0:
        assessment = cached_explain(
            new_aqi, 
            tuple(aqi_history)
        )


# ===========================================================================
# SECTION 7: TROUBLESHOOTING
# ===========================================================================

TROUBLESHOOTING = """
TROUBLESHOOTING
===============

7.1 Common Issues
-----------------

Issue: ValueError: "Need at least 3 data points"
Solution: Provide aqi_history with minimum 3 values
Example: aqi_history = [50.0, 55.0, 60.0]

Issue: Results seem inconsistent
Solution: 
• Verify data is in chronological order (oldest first)
• Check for data quality issues
• Review confidence levels
• May need more data for better results

Issue: Confidence level always "LOW"
Solution:
• Provide more historical data points
• Check data consistency
• Ensure weather data matches AQI history length
• May indicate unclear conditions

Issue: Expected hours seem too high/low
Solution:
• Check weather_improving parameter
• Review persistence score in context
• Compare with other indicators
• Adjust DurationAssessor thresholds if needed


7.2 Validation Checklist
------------------------

Before using assessment results:

☐ Verify minimum 3 AQI values in history
☐ Check that aqi_history is chronological order
☐ If weather data provided, verify length matches
☐ Confirm weather_improving parameter is correct
☐ Review confidence level (HIGH is best)
☐ Cross-check with other indicators
☐ For critical decisions, use HIGH confidence results


7.3 Data Quality Guidelines
----------------------------

For best results, provide:

AQI Data:
• Regular time intervals (hourly recommended)
• Quality assured values
• No gaps in series
• At least 3-6 hours of history

Weather Data:
• Same time intervals as AQI
• Realistic values (wind 0-20 m/s typical)
• Same length as AQI history
• Quality assured measurements


# ===========================================================================
# SECTION 8: PERFORMANCE CONSIDERATIONS
# ===========================================================================

PERFORMANCE = """
PERFORMANCE CONSIDERATIONS
===========================

8.1 Computational Complexity
----------------------------

All analysis is O(n) where n = number of data points:

• TrendAnalyzer: O(n) - single pass for statistics
• FactorAnalyzer: O(n) - evaluates each data point
• DurationAssessor: O(1) - constant time decision
• Total: O(n) dominated by factor analysis

Typical performance:
• 10 data points: < 1 ms
• 100 data points: < 5 ms
• 1000 data points: < 50 ms

Memory usage: O(n) for storing history


8.2 Scalability
---------------

For real-time monitoring:

• Single location, hourly data: Negligible overhead
• 100 locations, hourly: < 100 ms total
• 1000 locations, real-time: May need batching

Recommended batching for large deployments:
• Batch locations into groups of 100
• Process groups in parallel
• Cache results (valid 5-15 minutes)


8.3 Optimization Strategies
---------------------------

For performance-critical applications:

1. Limit history window:
   • Keep only last 24-48 hours
   • Reduces O(n) overhead
   • Still provides good analysis

2. Cache results:
   • Results valid for 5-15 minutes
   • Reduces redundant computation
   • Use LRU cache for memory efficiency

3. Batch process:
   • Group similar analyses
   • Run in parallel if possible
   • Reduces API call overhead

4. Asynchronous execution:
   • For API endpoints, use async
   • Non-blocking for user requests
   • Better concurrency


# ===========================================================================
# END OF DOCUMENTATION
# ===========================================================================

For additional help, see:
• EXPLAINABILITY_QUICK_REF.md - Quick reference guide
• examples/explainability_examples.py - Usage examples
• tests/test_explainability.py - Test cases
"""


# ===========================================================================
# Print All Sections
# ===========================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AQI EXPLAINABILITY ENGINE - COMPREHENSIVE DOCUMENTATION")
    print("="*70 + "\n")
    
    sections = [
        ("ARCHITECTURE", ARCHITECTURE),
        ("CORE CONCEPTS", CORE_CONCEPTS),
        ("API REFERENCE", API_REFERENCE),
        ("USAGE GUIDE", USAGE_GUIDE),
        ("INTEGRATION PATTERNS", INTEGRATION_PATTERNS),
        ("ADVANCED TOPICS", ADVANCED_TOPICS),
        ("TROUBLESHOOTING", TROUBLESHOOTING),
        ("PERFORMANCE", PERFORMANCE)
    ]
    
    for title, content in sections:
        print(content)
        print("\n")
