"""
Usage Examples for AQI Explainability Module

Demonstrates 10 real-world scenarios showing how to use the explainability
module to interpret AQI trends and identify contributing factors.
"""

from app.services.explainability import create_explainer, Trend, Duration
import json


def print_assessment(title: str, assessment):
    """Pretty print an assessment."""
    print(f"\n{'='*70}")
    print(f"{title:^70}")
    print(f"{'='*70}")
    print(f"Current AQI: {assessment.current_aqi:.1f}")
    print(f"Trend: {assessment.trend.value.upper()}")
    print(f"Duration: {assessment.duration.value.upper()}")
    print(f"Confidence: {assessment.confidence_overall.value.upper()}")
    print(f"Main Factors: {', '.join(assessment.main_factors)}")
    
    if assessment.duration_assessment:
        print(f"Expected Duration: {assessment.duration_assessment.expected_hours} hours")
        print(f"Reasoning: {assessment.duration_assessment.reasoning}")
    
    print(f"\nJSON Output:")
    print(json.dumps(assessment.to_dict(), indent=2, default=str))


# ===========================================================================
# Example 1: Rapid AQI Increase - Pollution Event
# ===========================================================================

def example_1_pollution_event():
    """
    Example 1: Rapid AQI increase due to pollution event
    
    Scenario: During morning rush hour, traffic builds up with stagnant air
    conditions. AQI rapidly increases from 30 to 85 over 5 hours.
    """
    explainer = create_explainer()
    
    aqi_history = [30.0, 45.0, 60.0, 75.0, 85.0]
    wind_speed = [2.5, 1.8, 1.2, 0.9, 0.8]  # Wind decreasing
    humidity = [60.0, 70.0, 75.0, 80.0, 82.0]  # Humidity increasing
    
    assessment = explainer.explain(
        current_aqi=85.0,
        aqi_history=aqi_history,
        wind_speed_history=wind_speed,
        humidity_history=humidity,
        weather_improving=False
    )
    
    print_assessment("Example 1: Pollution Event - Rush Hour Buildup", assessment)


# ===========================================================================
# Example 2: Air Quality Improvement - Weather System Arrival
# ===========================================================================

def example_2_air_quality_improvement():
    """
    Example 2: Air quality improvement due to weather system arrival
    
    Scenario: A cold front with strong winds arrives, clearing out stagnant
    pollution. AQI drops from 95 to 35 over 6 hours.
    """
    explainer = create_explainer()
    
    aqi_history = [95.0, 85.0, 70.0, 55.0, 40.0, 35.0]
    wind_speed = [0.5, 2.0, 4.5, 6.0, 7.5, 8.0]  # Wind increasing
    humidity = [80.0, 75.0, 65.0, 55.0, 50.0, 45.0]  # Humidity decreasing
    temperature = [18.0, 16.0, 14.0, 12.0, 10.0, 8.0]  # Temperature dropping
    
    assessment = explainer.explain(
        current_aqi=35.0,
        aqi_history=aqi_history,
        wind_speed_history=wind_speed,
        humidity_history=humidity,
        temperature_history=temperature,
        weather_improving=True
    )
    
    print_assessment("Example 2: Air Quality Improvement - Weather Front", assessment)


# ===========================================================================
# Example 3: Stable Stagnant Conditions - Persistent Pollution
# ===========================================================================

def example_3_stagnant_conditions():
    """
    Example 3: Stable stagnant conditions with persistent pollution
    
    Scenario: High pressure system creating stable, stagnant air. AQI remains
    consistently high (70-73) with minimal changes over 5 hours.
    """
    explainer = create_explainer()
    
    aqi_history = [70.0, 70.5, 71.2, 70.8, 70.3, 71.0]
    wind_speed = [0.3, 0.4, 0.5, 0.3, 0.4, 0.3]  # Very low wind (stagnant)
    humidity = [75.0, 76.0, 77.0, 75.5, 76.5, 76.0]  # High, stable humidity
    temperature = [15.0, 15.5, 16.0, 15.5, 16.5, 16.0]  # Warm layer
    
    assessment = explainer.explain(
        current_aqi=71.0,
        aqi_history=aqi_history,
        wind_speed_history=wind_speed,
        humidity_history=humidity,
        temperature_history=temperature,
        weather_improving=False
    )
    
    print_assessment("Example 3: Stagnant Conditions - Persistent Pollution", assessment)


# ===========================================================================
# Example 4: Morning Inversion - Temperature Trap
# ===========================================================================

def example_4_morning_inversion():
    """
    Example 4: Morning temperature inversion trapping pollution
    
    Scenario: Early morning with temperature inversion (cold near surface,
    warm aloft). Pollution is trapped. AQI high and rising. Wind is calm.
    """
    explainer = create_explainer()
    
    aqi_history = [55.0, 60.0, 65.0, 72.0, 78.0]
    wind_speed = [0.2, 0.2, 0.3, 0.2, 0.3]  # Nearly calm
    humidity = [85.0, 87.0, 88.0, 86.0, 85.0]  # Very high (foggy)
    temperature = [2.0, 2.5, 3.0, 3.5, 4.0]  # Cold (frost layer)
    
    assessment = explainer.explain(
        current_aqi=78.0,
        aqi_history=aqi_history,
        wind_speed_history=wind_speed,
        humidity_history=humidity,
        temperature_history=temperature,
        weather_improving=False
    )
    
    print_assessment("Example 4: Morning Inversion - Temperature Trap", assessment)


# ===========================================================================
# Example 5: Afternoon Boundary Layer Breakup
# ===========================================================================

def example_5_afternoon_breakup():
    """
    Example 5: Afternoon boundary layer breakup improving air quality
    
    Scenario: As surface warms in afternoon, convective boundary layer
    deepens and breaks down the inversion, dispersing pollutants. AQI
    improves from 72 to 45.
    """
    explainer = create_explainer()
    
    aqi_history = [72.0, 68.0, 60.0, 50.0, 45.0]
    wind_speed = [0.4, 1.2, 2.5, 3.8, 4.5]  # Wind increasing as layer mixes
    humidity = [85.0, 78.0, 70.0, 60.0, 52.0]  # Humidity decreasing
    temperature = [4.0, 8.0, 12.0, 16.0, 18.0]  # Warming (convection)
    
    assessment = explainer.explain(
        current_aqi=45.0,
        aqi_history=aqi_history,
        wind_speed_history=wind_speed,
        humidity_history=humidity,
        temperature_history=temperature,
        weather_improving=True
    )
    
    print_assessment("Example 5: Afternoon Breakup - Boundary Layer Mix", assessment)


# ===========================================================================
# Example 6: Rain Event - Precipitation Cleanup
# ===========================================================================

def example_6_rain_cleanup():
    """
    Example 6: Rain event cleaning out pollution
    
    Scenario: Frontal rainfall occurring. Rain washes out particles and
    humidity is very high. AQI drops from 68 to 30. Trend is strongly
    falling.
    """
    explainer = create_explainer()
    
    aqi_history = [68.0, 58.0, 48.0, 38.0, 30.0, 25.0]
    wind_speed = [1.5, 2.0, 3.0, 4.0, 5.5, 6.0]  # Frontal wind increase
    humidity = [95.0, 98.0, 100.0, 98.0, 96.0, 94.0]  # Saturated (rain)
    temperature = [8.0, 7.5, 7.0, 8.0, 10.0, 12.0]  # Warming behind front
    
    assessment = explainer.explain(
        current_aqi=25.0,
        aqi_history=aqi_history,
        wind_speed_history=wind_speed,
        humidity_history=humidity,
        temperature_history=temperature,
        weather_improving=True
    )
    
    print_assessment("Example 6: Rain Event - Precipitation Cleanup", assessment)


# ===========================================================================
# Example 7: Volatile Conditions - Rapid Fluctuations
# ===========================================================================

def example_7_volatile_conditions():
    """
    Example 7: Volatile AQI with rapid fluctuations
    
    Scenario: Gusty winds causing variable mixing and pollution transport.
    AQI fluctuates rapidly between 45 and 75 with no clear trend.
    """
    explainer = create_explainer()
    
    aqi_history = [50.0, 70.0, 45.0, 75.0, 48.0, 68.0, 52.0]
    wind_speed = [2.0, 4.5, 1.5, 5.0, 2.5, 4.0, 2.2]  # Highly variable wind
    humidity = [65.0, 55.0, 75.0, 50.0, 72.0, 58.0, 68.0]  # Variable humidity
    temperature = [12.0, 14.0, 10.0, 15.0, 11.0, 13.0, 12.0]
    
    assessment = explainer.explain(
        current_aqi=52.0,
        aqi_history=aqi_history,
        wind_speed_history=wind_speed,
        humidity_history=humidity,
        temperature_history=temperature,
        weather_improving=False
    )
    
    print_assessment("Example 7: Volatile Conditions - Rapid Fluctuations", assessment)


# ===========================================================================
# Example 8: Sea Breeze Effect - Coastal Pollution Transport
# ===========================================================================

def example_8_sea_breeze_effect():
    """
    Example 8: Sea breeze effect transporting pollution inland
    
    Scenario: Coastal city with daytime sea breeze pushing ocean-modified
    air inland in afternoon. Wind shifts and strengthens, bringing cleaner
    air. AQI decreases.
    """
    explainer = create_explainer()
    
    aqi_history = [58.0, 52.0, 48.0, 42.0, 35.0]
    wind_speed = [3.5, 4.5, 5.5, 6.5, 7.5]  # Sea breeze strengthening
    humidity = [75.0, 78.0, 80.0, 82.0, 80.0]  # Maritime influence
    temperature = [16.0, 18.0, 20.0, 22.0, 20.0]  # Warming then stabilizing
    
    assessment = explainer.explain(
        current_aqi=35.0,
        aqi_history=aqi_history,
        wind_speed_history=wind_speed,
        humidity_history=humidity,
        temperature_history=temperature,
        weather_improving=True
    )
    
    print_assessment("Example 8: Sea Breeze Effect - Coastal Transport", assessment)


# ===========================================================================
# Example 9: Minimal Data - Only AQI History Available
# ===========================================================================

def example_9_minimal_data():
    """
    Example 9: Analysis with minimal data (AQI only)
    
    Scenario: Limited data availability. Only AQI measurements available,
    no weather data. System should still provide useful explanation based
    on AQI trend and persistence.
    """
    explainer = create_explainer()
    
    # Only AQI history, no weather data
    aqi_history = [55.0, 58.0, 60.0, 62.0]
    
    assessment = explainer.explain(
        current_aqi=62.0,
        aqi_history=aqi_history
    )
    
    print_assessment("Example 9: Minimal Data - AQI Only", assessment)


# ===========================================================================
# Example 10: Excellent Air Quality - Low Pollution
# ===========================================================================

def example_10_excellent_air():
    """
    Example 10: Excellent air quality with very low AQI
    
    Scenario: Clean air conditions after extended wind period. AQI very
    low (5-15) with strong winds and low humidity. Conditions improving.
    """
    explainer = create_explainer()
    
    aqi_history = [15.0, 12.0, 10.0, 8.0, 6.0, 5.0]
    wind_speed = [6.5, 7.0, 7.5, 8.0, 8.5, 9.0]  # Strong winds
    humidity = [35.0, 32.0, 30.0, 28.0, 28.0, 30.0]  # Low humidity
    temperature = [18.0, 19.0, 20.0, 21.0, 20.0, 19.0]  # Clear conditions
    
    assessment = explainer.explain(
        current_aqi=5.0,
        aqi_history=aqi_history,
        wind_speed_history=wind_speed,
        humidity_history=humidity,
        temperature_history=temperature,
        weather_improving=True
    )
    
    print_assessment("Example 10: Excellent Air Quality - Clean Conditions", assessment)


# ===========================================================================
# Main Execution
# ===========================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AQI EXPLAINABILITY MODULE - USAGE EXAMPLES".center(70))
    print("="*70)
    print("\nThese examples demonstrate how to use the explainability module")
    print("to interpret AQI trends and identify contributing factors.\n")
    
    # Run all examples
    example_1_pollution_event()
    example_2_air_quality_improvement()
    example_3_stagnant_conditions()
    example_4_morning_inversion()
    example_5_afternoon_breakup()
    example_6_rain_cleanup()
    example_7_volatile_conditions()
    example_8_sea_breeze_effect()
    example_9_minimal_data()
    example_10_excellent_air()
    
    print("\n" + "="*70)
    print("All examples completed successfully!".center(70))
    print("="*70 + "\n")
