"""
AQI Explainability Engine - Quick Reference Guide

Fast lookup for common tasks and classifications.
For detailed information, see EXPLAINABILITY_ENGINE.md
"""


# ===========================================================================
# QUICK START
# ===========================================================================

QUICK_START = """
QUICK START - 5 MINUTE SETUP
=============================

1. Import the explainer:
   from app.services.explainability import create_explainer

2. Create instance:
   explainer = create_explainer()

3. Call explain() with AQI history:
   assessment = explainer.explain(
       current_aqi=65.0,
       aqi_history=[50, 55, 60, 65]
   )

4. Access results:
   print(assessment.trend.value)        # "rising"
   print(assessment.duration.value)     # "persistent"
   print(assessment.main_factors)       # List of factors
   print(assessment.to_dict())          # JSON-ready dict

That's it! You now have explainable AQI analysis.

Optional: Add weather data for richer analysis:
   assessment = explainer.explain(
       current_aqi=65.0,
       aqi_history=[50, 55, 60, 65],
       wind_speed_history=[2.0, 1.5, 1.0, 0.8],
       humidity_history=[70, 75, 80, 82],
       temperature_history=[15, 14, 13, 12]
   )
"""


# ===========================================================================
# TREND CLASSIFICATION
# ===========================================================================

TREND_REFERENCE = """
TREND CLASSIFICATION QUICK REFERENCE
=====================================

┌─────────────┬─────────────────────────┬──────────────────────────────┐
│   TREND     │   CHARACTERISTICS       │   INTERPRETATION             │
├─────────────┼─────────────────────────┼──────────────────────────────┤
│  RISING     │ • AQI increasing        │ Pollution worsening          │
│             │ • Positive slope        │ Peak likely ahead            │
│             │ • Change > 2%           │ May need air quality alert   │
│             │                         │ Vulnerable groups at risk    │
├─────────────┼─────────────────────────┼──────────────────────────────┤
│  FALLING    │ • AQI decreasing        │ Air quality improving        │
│             │ • Negative slope        │ Recovery underway            │
│             │ • Change < -2%          │ Can increase outdoor activity│
│             │                         │ Alert conditions easing      │
├─────────────┼─────────────────────────┼──────────────────────────────┤
│  STABLE     │ • Change between -2%    │ Conditions not changing      │
│             │   and +2%               │ If high AQI: persistent      │
│             │ • Low volatility        │ If low AQI: good condition  │
│             │ • Consistent values     │ May continue or shift soon   │
└─────────────┴─────────────────────────┴──────────────────────────────┘

TREND PREDICTION:
• RISING: Often continues for 3-12 more hours (check duration)
• FALLING: Usually continues improving for 6-24 hours
• STABLE: May persist for hours or suddenly change
"""


# ===========================================================================
# FACTOR INTERPRETATION
# ===========================================================================

FACTOR_REFERENCE = """
FACTOR INTERPRETATION QUICK REFERENCE
======================================

LOW WIND SPEED (< 3.0 m/s)
├─ Impact: Worsens pollution (stagnation)
├─ Severity: Higher = worse dispersion
├─ Typical in: Morning, calm weather patterns
├─ Actions: Monitor for worsening, issue alert if persistent
└─ Resolution: Wait for wind to increase

HIGH HUMIDITY (> 70%)
├─ Impact: May increase aerosol formation
├─ Severity: Higher humidity = more particles suspended
├─ Typical in: Coastal areas, before rain, late evening
├─ Actions: Combined with wind low: major concern
└─ Resolution: Often improves with temperature change

HIGH TEMPERATURE (> 25°C)
├─ Impact: Increases secondary pollutant formation (ozone)
├─ Severity: Peak sun hours most critical
├─ Typical in: Afternoon, clear sunny days
├─ Actions: Peak hours: 2-6 PM typically worst
└─ Resolution: Overnight cooling reduces secondary formation

COLD TEMPERATURE (< 0°C)
├─ Impact: Traps pollution in inversion layer
├─ Severity: Very cold worse than slightly cold
├─ Typical in: Early morning, winter
├─ Actions: Wait for boundary layer to develop
└─ Resolution: Solar heating breaks inversion (9-11 AM typical)

LOW HUMIDITY (< 40%)
├─ Impact: May suspend fine particles longer
├─ Severity: Very dry conditions rare
├─ Typical in: Desert areas, afternoon heating
├─ Actions: Less critical unless combined with other factors
└─ Resolution: Usually not a major concern

AQI PERSISTENCE
├─ Impact: How well recent AQI levels continue
├─ High (> 0.7): Conditions will likely continue
├─ Medium (0.4-0.7): Some change expected
├─ Low (< 0.4): Conditions changing rapidly
├─ Action: High persistence + high AQI = alert needed
└─ Interpretation: Strong persistence = difficult to change
"""


# ===========================================================================
# DURATION INTERPRETATION
# ===========================================================================

DURATION_REFERENCE = """
DURATION CLASSIFICATION QUICK REFERENCE
========================================

┌────────────┬──────────────┬────────────────────────────────────┐
│ DURATION   │ EXPECTED     │ WHAT IT MEANS                      │
├────────────┼──────────────┼────────────────────────────────────┤
│ TEMPORARY  │ < 12 hours   │ Episode expected to clear soon     │
│            │              │ Can avoid peak hours               │
│            │              │ Short-term precautions sufficient  │
│            │              │ Recovery expected by tomorrow      │
├────────────┼──────────────┼────────────────────────────────────┤
│ PERSISTENT │ > 12 hours   │ Long-term concern                  │
│            │              │ Vulnerable groups need protection  │
│            │              │ May last multiple days             │
│            │              │ May need multiple interventions    │
└────────────┴──────────────┴────────────────────────────────────┘

EXPECTED HOURS BREAKDOWN:
• 0-3 hours: Rapid clearing (strong improving winds)
• 3-6 hours: Short-term temporary episode
• 6-12 hours: Extended temporary period
• 12-18 hours: Persistent condition
• 18-24 hours: Very persistent (overnight + next day)
• 24+ hours: Multi-day pollution event

FACTORS AFFECTING DURATION:
• Trend: Rising → longer, Falling → shorter
• Wind speed: Higher wind → shorter duration
• Persistence: High → longer, Low → shorter
• Weather outlook: Improving → shorter, Deteriorating → longer
• Time of day: Morning inversions break by afternoon
"""


# ===========================================================================
# CONFIDENCE LEVELS
# ===========================================================================

CONFIDENCE_REFERENCE = """
CONFIDENCE LEVEL INTERPRETATION
================================

HIGH CONFIDENCE
├─ Meaning: Results are very reliable
├─ When: Clear patterns, stable conditions, good data
├─ Action: Can confidently base decisions on results
├─ Triggers: 
│  • Volatility < 5
│  • Persistence > 0.75
│  • Steep trend (slope > 1.5)
└─ Typical: Well-defined trends, clear factors

MEDIUM CONFIDENCE
├─ Meaning: Results reasonably reliable
├─ When: Mixed patterns, moderate change, adequate data
├─ Action: Useful for planning, verify important decisions
├─ Triggers:
│  • Volatility 5-20
│  • Persistence 0.5-0.75
│  • Moderate trend (slope 0.5-1.5)
└─ Typical: Changing conditions, complex interactions

LOW CONFIDENCE
├─ Meaning: Results less certain
├─ When: Chaotic patterns, unclear data, insufficient history
├─ Action: Use with caution, verify with other sources
├─ Triggers:
│  • Volatility > 20
│  • Persistence < 0.5
│  • Weak trend (|slope| < 0.5)
└─ Typical: Rapidly changing, ambiguous patterns

RECOMMENDATION:
• HIGH: Trust the analysis
• MEDIUM: Supportive of other indicators
• LOW: Supplementary only, need more data
"""


# ===========================================================================
# COMMON USE CASES
# ===========================================================================

USE_CASES = """
COMMON USE CASES - WHAT TO DO WITH RESULTS
============================================

1. RISING TREND + HIGH AQI + PERSISTENT
   → Issue/escalate air quality alert
   → Recommend vulnerable groups stay indoors
   → Predict duration from expected_hours
   → Alert will likely last > 12 hours

2. FALLING TREND + PERSISTENT + WEATHER IMPROVING
   → Clear improvement underway
   → Public can resume normal activities soon
   → Recovery expected in assessment.duration_assessment.expected_hours

3. STABLE TREND + HIGH AQI + LOW WIND SPEED
   → Stagnant conditions
   → Pollution will remain high without wind
   → Watch for any trend shift
   → May persist indefinitely without weather change

4. RISING TREND + "LOW WIND SPEED" FACTOR
   → Primary issue is stagnation
   → Will improve when wind picks up
   → Watch wind forecast for improvement
   → Most important factor to track

5. HIGH VOLATILITY + TEMPORARY DURATION
   → Rapidly changing conditions
   → Peak hours likely unpredictable
   → Avoid outdoor activity during peak windows
   → Recovery expected within hours

6. STABLE + LOW AQI
   → Air quality is good
   → Expected to remain good
   → Safe for outdoor activities
   → No immediate action needed

7. MULTIPLE DOMINANT FACTORS
   → Multiple issues contributing
   → No single fix available
   → May take time to improve
   → Each factor should be monitored

8. "HIGH HUMIDITY" + "HIGH TEMPERATURE" FACTORS
   → Classic afternoon ozone production pattern
   → Will peak 2-6 PM (secondary pollutants)
   → Evening will improve as temperature drops
   → Tomorrow may be similar or worse
"""


# ===========================================================================
# DATA FORMATS
# ===========================================================================

DATA_FORMATS = """
INPUT/OUTPUT DATA FORMATS
==========================

MINIMAL INPUT:
aqi_history = [50.0, 55.0, 60.0, 65.0]  # Required, min 3 values
current_aqi = 65.0                       # Latest value

OPTIONAL INPUT:
wind_speed_history = [2.0, 1.5, 1.0, 0.8]      # m/s
humidity_history = [70.0, 75.0, 80.0, 82.0]    # %
temperature_history = [15.0, 14.0, 13.0, 12.0] # °C
weather_improving = True                        # Bool or None

OUTPUT STRUCTURE:
{
    "timestamp": "2026-01-31T12:00:00",
    "current_aqi": 65.0,
    "trend": "rising",              # rising | falling | stable
    "main_factors": [               # List of factor names
        "low wind speed",
        "high humidity"
    ],
    "duration": "persistent",       # persistent | temporary
    "confidence": "high",           # high | medium | low
    "trend_details": {              # Optional
        "slope": 2.5,
        "change_percentage": 15.0,
        "volatility": 3.2
    },
    "duration_details": {           # Optional
        "expected_hours": 18,
        "reasoning": "Rising trend suggests..."
    },
    "context": {                    # Optional metadata
        "num_dominant_factors": 2,
        "aqi_persistence_score": 0.72,
        "weather_impact_score": 0.65
    }
}

FACTOR NAMES (POSSIBLE VALUES):
• "low wind speed"
• "good wind dispersion"
• "high humidity"
• "low humidity"
• "cold temperature"
• "high temperature"
• "high AQI persistence"
• "moderate AQI persistence"
• "improving conditions"
• "stable conditions"
"""


# ===========================================================================
# THRESHOLD VALUES
# ===========================================================================

THRESHOLDS = """
DEFAULT THRESHOLD VALUES
========================

WIND SPEED:
• Low wind threshold: < 3.0 m/s
• Good dispersion: > 3.0 m/s
• Strong dispersion: > 5.0 m/s
• Calm conditions: < 0.5 m/s

HUMIDITY:
• High humidity: > 70%
• Moderate humidity: 40-70%
• Low humidity: < 40%
• Very high (saturated): > 95%

TEMPERATURE:
• Cold (trapping): < 0°C
• Cool: 0-10°C
• Moderate: 10-20°C
• Warm: 20-25°C
• Hot (ozone): > 25°C
• Very hot: > 30°C

AQI PERSISTENCE:
• High: > 0.7
• Moderate: 0.4-0.7
• Low: < 0.4

VOLATILITY:
• High: > 15.0
• Moderate: 5-15
• Low: < 5

TREND CHANGE:
• Significant: > 2% change
• Minimal: < 2% change
• Slope thresholds for confidence calculation

CONFIDENCE CRITERIA:
• HIGH: Volatility < 5 OR persistence > 0.75
• MEDIUM: Volatility < 20 OR persistence > 0.5
• LOW: Otherwise

Custom thresholds can be set by modifying
the Analyzer class constants.
"""


# ===========================================================================
# PYTHON API CHEAT SHEET
# ===========================================================================

API_CHEAT_SHEET = """
PYTHON API CHEAT SHEET
======================

CREATE EXPLAINER:
    from app.services.explainability import create_explainer
    explainer = create_explainer()

BASIC EXPLAIN:
    assessment = explainer.explain(
        current_aqi=65.0,
        aqi_history=[50, 55, 60, 65]
    )

EXPLAIN WITH WEATHER:
    assessment = explainer.explain(
        current_aqi=65.0,
        aqi_history=[50, 55, 60, 65],
        wind_speed_history=[2, 1.5, 1, 0.8],
        humidity_history=[70, 75, 80, 82],
        temperature_history=[15, 14, 13, 12],
        weather_improving=False
    )

ACCESS RESULTS:
    assessment.current_aqi              # Float
    assessment.trend                    # Trend enum
    assessment.trend.value              # "rising", "falling", "stable"
    assessment.main_factors             # List[str]
    assessment.duration                 # Duration enum
    assessment.duration.value           # "temporary", "persistent"
    assessment.confidence_overall       # ConfidenceLevel enum
    assessment.confidence_overall.value # "high", "medium", "low"

DETAILED ANALYSIS:
    assessment.trend_analysis           # TrendAnalysis object
    assessment.trend_analysis.slope
    assessment.trend_analysis.volatility
    assessment.trend_analysis.confidence
    
    assessment.factor_analysis          # FactorAnalysis object
    assessment.factor_analysis.aqi_persistence
    assessment.factor_analysis.weather_impact_score
    assessment.factor_analysis.dominant_factors  # List[Factor]
    assessment.factor_analysis.secondary_factors # List[Factor]
    
    assessment.duration_assessment      # DurationAssessment object
    assessment.duration_assessment.expected_hours
    assessment.duration_assessment.reasoning

EXPORT TO JSON:
    import json
    json_str = json.dumps(
        assessment.to_dict(),
        indent=2,
        default=str
    )

CHECK FACTORS:
    if "low wind speed" in assessment.main_factors:
        print("Stagnant conditions detected")
    
    for factor in assessment.factor_analysis.dominant_factors:
        print(f"{factor.name}: {factor.severity}")

COMPARE ASSESSMENTS:
    assessment1 = explainer.explain(current_aqi, history1)
    assessment2 = explainer.explain(current_aqi, history2)
    
    if assessment1.trend != assessment2.trend:
        print("Trend changed!")
"""


# ===========================================================================
# TROUBLESHOOTING
# ===========================================================================

TROUBLESHOOTING = """
QUICK TROUBLESHOOTING
=====================

PROBLEM: ValueError about data points
FIX: Provide at least 3 AQI values in aqi_history

PROBLEM: Unexpected trend classification
FIX: 
1. Verify aqi_history is in chronological order
2. Check for data quality issues
3. Review confidence level (low = uncertain)

PROBLEM: Results seem inconsistent
FIX:
1. Ensure weather data matches history length
2. Verify weather_improving parameter is correct
3. Check if conditions are genuinely volatile

PROBLEM: Confidence always LOW
FIX:
1. Provide more history (6+ hours better)
2. Ensure data quality
3. May indicate genuinely unclear conditions

PROBLEM: Factors seem wrong
FIX:
1. Verify weather data values are realistic
2. Check severity thresholds
3. May need custom threshold adjustment

PROBLEM: Duration seems incorrect
FIX:
1. Check weather_improving parameter
2. Verify persistence score in context
3. Consider actual meteorological forecast
4. May need more history data
"""


# ===========================================================================
# FILE LOCATIONS
# ===========================================================================

LOCATIONS = """
WHERE TO FIND THINGS
====================

Source Code:
  app/services/explainability.py     Main module

Tests:
  tests/test_explainability.py       42 comprehensive tests

Examples:
  examples/explainability_examples.py 10 real-world scenarios

Documentation:
  EXPLAINABILITY_ENGINE.md           Complete reference (this file)
  EXPLAINABILITY_QUICK_REF.md        Quick reference

Testing the module:
  python -m pytest tests/test_explainability.py -v

Running examples:
  python examples/explainability_examples.py

All tests should pass (42/42)
"""


# ===========================================================================
# PRINT ALL SECTIONS
# ===========================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AQI EXPLAINABILITY ENGINE - QUICK REFERENCE GUIDE")
    print("="*70 + "\n")
    
    sections = [
        QUICK_START,
        TREND_REFERENCE,
        FACTOR_REFERENCE,
        DURATION_REFERENCE,
        CONFIDENCE_REFERENCE,
        USE_CASES,
        DATA_FORMATS,
        THRESHOLDS,
        API_CHEAT_SHEET,
        TROUBLESHOOTING,
        LOCATIONS
    ]
    
    for section in sections:
        print(section)
        print("\n")
