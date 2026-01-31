"""
Health Risk Classification Engine - Usage Examples

Demonstrates:
1. Basic AQI classification
2. Personalized health advice retrieval
3. Risk assessment for different personas
4. Real-world pollution scenarios
5. JSON output generation
"""

import json
from app.services.health_risk import (
    HealthRiskClassifier,
    Persona,
    RiskCategory,
    create_classifier
)


def example_1_basic_classification():
    """Example 1: Basic AQI classification"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic AQI Classification")
    print("="*80)
    
    classifier = create_classifier()
    
    # Test different AQI values
    aqi_values = [10, 50, 100, 150, 250, 350]
    
    print("\nAQI Value -> Risk Category:\n")
    for aqi in aqi_values:
        risk_category = classifier.classify_aqi(aqi)
        color = classifier.get_color_code(risk_category)
        print(f"  AQI {aqi:3d} -> {risk_category.value:30s} (Color: {color})")


def example_2_health_effects():
    """Example 2: Health effects for different risk levels"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Health Effects by Risk Level")
    print("="*80)
    
    classifier = create_classifier()
    
    for category in RiskCategory:
        print(f"\n{category.value}:")
        effects = classifier.get_health_effects(category)
        for i, effect in enumerate(effects, 1):
            print(f"  {i}. {effect}")


def example_3_personalized_advice():
    """Example 3: Personalized advice for specific personas"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Personalized Health Advice")
    print("="*80)
    
    classifier = create_classifier()
    
    # Unhealthy air quality scenario
    aqi_value = 150
    print(f"\nScenario: AQI = {aqi_value} (Unhealthy for Sensitive Groups)")
    print("-" * 80)
    
    # Get advice for different personas
    personas = [
        Persona.GENERAL_PUBLIC,
        Persona.CHILDREN,
        Persona.ELDERLY,
        Persona.ATHLETES,
        Persona.OUTDOOR_WORKERS
    ]
    
    risk_category = classifier.classify_aqi(aqi_value)
    
    for persona in personas:
        advice = classifier.get_personalized_advice(risk_category, persona)
        if advice:
            print(f"\n{persona.value}:")
            print(f"  Activity: {advice.activity_recommendation}")
            print(f"  Setting: {advice.indoor_outdoor}")
            if advice.health_warning:
                print(f"  ⚠️  Warning: {advice.health_warning}")
            print(f"  Precautions ({len(advice.precautions)}):")
            for precaution in advice.precautions[:2]:  # Show first 2
                print(f"    • {precaution}")
            if len(advice.precautions) > 2:
                print(f"    ... and {len(advice.precautions) - 2} more")


def example_4_complete_assessment():
    """Example 4: Complete health risk assessment"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Complete Health Risk Assessment")
    print("="*80)
    
    classifier = create_classifier()
    
    # Assess air quality with pollution event
    aqi_value = 200
    print(f"\nPerforming health risk assessment for AQI = {aqi_value}...")
    
    assessment = classifier.assess_health_risk(aqi_value, 'PM2.5')
    
    print(f"\n📊 Assessment Results:")
    print(f"  Risk Category: {assessment.risk_category}")
    print(f"  Color Code: {assessment.color_code}")
    print(f"  General Advice: {assessment.general_advice}")
    
    print(f"\n👥 At-Risk Populations:")
    for population in assessment.at_risk_populations:
        print(f"  • {population}")
    
    print(f"\n⚕️  Health Effects:")
    for effect in assessment.health_effects[:3]:
        print(f"  • {effect}")
    if len(assessment.health_effects) > 3:
        print(f"  ... and {len(assessment.health_effects) - 3} more")
    
    print(f"\n📋 Recommended Actions:")
    for action_type, action in assessment.recommended_actions.items():
        print(f"  {action_type}: {action}")


def example_5_multi_persona_assessment():
    """Example 5: Assessment with multiple specific personas"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Multi-Persona Risk Assessment")
    print("="*80)
    
    classifier = create_classifier()
    
    # Focus on vulnerable groups
    personas = [Persona.CHILDREN, Persona.ELDERLY, Persona.OUTDOOR_WORKERS]
    aqi_value = 175
    
    print(f"\nAssessing risk for vulnerable groups (AQI = {aqi_value})...")
    
    assessment = classifier.assess_health_risk(
        aqi_value,
        'PM2.5',
        personas=personas
    )
    
    print(f"\nRisk Category: {assessment.risk_category}\n")
    
    for persona_name, advice in assessment.personalized_advice.items():
        print(f"{persona_name}:")
        print(f"  Activity: {advice.activity_recommendation}")
        print(f"  Symptoms to Watch:")
        for symptom in advice.symptoms_to_watch[:3]:
            print(f"    • {symptom}")
        print()


def example_6_pollution_escalation():
    """Example 6: Real-world pollution escalation scenario"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Pollution Event Escalation")
    print("="*80)
    
    classifier = create_classifier()
    
    # Simulate a pollution event throughout the day
    hourly_aqi = [
        ("06:00", 35),   # Morning - Moderate
        ("09:00", 85),   # Mid-morning - Upper moderate
        ("12:00", 145),  # Noon - Unhealthy for sensitive
        ("15:00", 180),  # Afternoon - Unhealthy
        ("18:00", 240),  # Evening - Very Unhealthy
        ("21:00", 200),  # Night - Very Unhealthy declining
    ]
    
    print("\n📈 Air Quality Throughout the Day:\n")
    print(f"{'Time':<10} {'AQI':<6} {'Category':<30} {'Status':<20}")
    print("-" * 66)
    
    for time, aqi in hourly_aqi:
        risk = classifier.classify_aqi(aqi)
        status = "🟢" if risk == RiskCategory.GOOD else \
                 "🟡" if risk == RiskCategory.MODERATE else \
                 "🟠" if risk == RiskCategory.UNHEALTHY_FOR_SENSITIVE else \
                 "🔴" if risk == RiskCategory.UNHEALTHY else \
                 "🟣" if risk == RiskCategory.VERY_UNHEALTHY else "⬛"
        
        print(f"{time:<10} {aqi:<6} {risk.value:<30} {status}")
    
    # Get detailed recommendation for peak pollution
    peak_aqi = 240
    print(f"\n⚠️  Peak Pollution Scenario (AQI = {peak_aqi}):")
    
    assessment = classifier.assess_health_risk(peak_aqi)
    print(f"\nRecommended Actions:")
    for action_type, action in assessment.recommended_actions.items():
        print(f"  • {action_type}: {action}")


def example_7_different_pollutants():
    """Example 7: Compare assessment across different pollutants"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Different Pollutants Assessment")
    print("="*80)
    
    classifier = create_classifier()
    
    # Same risk level across different pollutants
    scenarios = [
        ("PM2.5", 50),
        ("PM10", 100),
        ("NO2", 70),
        ("O3", 65),
    ]
    
    print(f"\n{'Parameter':<10} {'Value':<8} {'Category':<30}")
    print("-" * 48)
    
    for parameter, value in scenarios:
        risk = classifier.classify_aqi(value, parameter)
        print(f"{parameter:<10} {value:<8} {risk.value:<30}")
    
    # Get detailed assessment for PM2.5
    print("\nDetailed Assessment for PM2.5:")
    assessment = classifier.assess_health_risk(50, 'PM2.5')
    print(f"  Risk Level: {assessment.risk_category}")
    print(f"  Effects: {assessment.health_effects[0]}")


def example_8_json_output():
    """Example 8: JSON output generation"""
    print("\n" + "="*80)
    print("EXAMPLE 8: JSON Output Generation")
    print("="*80)
    
    classifier = create_classifier()
    
    # Create assessment
    assessment = classifier.assess_health_risk(
        150,
        'PM2.5',
        [Persona.CHILDREN, Persona.ELDERLY]
    )
    
    # Convert to JSON
    json_output = classifier.to_json(assessment)
    
    print("\nJSON Assessment Output:\n")
    # Pretty print
    data = json.loads(json_output)
    print(json.dumps({
        "aqi_value": data["aqi_value"],
        "aqi_parameter": data["aqi_parameter"],
        "risk_category": data["risk_category"],
        "color_code": data["color_code"],
        "general_advice": data["general_advice"],
        "health_effects_count": len(data["health_effects"]),
        "at_risk_populations_count": len(data["at_risk_populations"]),
        "personas_assessed": list(data["personalized_advice"].keys()),
        "timestamp": data["timestamp"]
    }, indent=2))
    
    print("\n✓ Full JSON output is JSON-serializable and API-ready")


def example_9_risk_threshold_boundaries():
    """Example 9: AQI threshold boundary testing"""
    print("\n" + "="*80)
    print("EXAMPLE 9: AQI Threshold Boundaries (PM2.5)")
    print("="*80)
    
    classifier = create_classifier()
    
    # Test boundary values
    boundaries = [
        (0, "Good - Minimum"),
        (12, "Good - Maximum"),
        (12.1, "Moderate - Minimum"),
        (35.4, "Moderate - Maximum"),
        (35.5, "Unhealthy for Sensitive - Minimum"),
        (150.4, "Unhealthy - Maximum"),
        (250.5, "Hazardous - Minimum"),
    ]
    
    print(f"\n{'AQI Value':<12} {'Category':<30} {'Description':<30}")
    print("-" * 72)
    
    for aqi, description in boundaries:
        risk = classifier.classify_aqi(aqi)
        print(f"{aqi:<12} {risk.value:<30} {description:<30}")


def example_10_advice_structure():
    """Example 10: Understanding advice structure"""
    print("\n" + "="*80)
    print("EXAMPLE 10: Health Advice Data Structure")
    print("="*80)
    
    classifier = create_classifier()
    
    # Get advice for a specific scenario
    advice = classifier.get_personalized_advice(
        RiskCategory.UNHEALTHY,
        Persona.CHILDREN
    )
    
    print(f"\nAdvice Structure for {advice.persona} during {advice.risk_category}:\n")
    print(f"  Persona: {advice.persona}")
    print(f"  Risk Category: {advice.risk_category}")
    print(f"  AQI Range: {advice.aqi_range[0]}-{advice.aqi_range[1]}")
    print(f"  Activity Recommendation: {advice.activity_recommendation}")
    print(f"  Indoor/Outdoor: {advice.indoor_outdoor}")
    print(f"  Health Warning: {advice.health_warning}")
    print(f"\n  Precautions ({len(advice.precautions)}):")
    for i, precaution in enumerate(advice.precautions, 1):
        print(f"    {i}. {precaution}")
    print(f"\n  Symptoms to Watch ({len(advice.symptoms_to_watch)}):")
    for i, symptom in enumerate(advice.symptoms_to_watch, 1):
        print(f"    {i}. {symptom}")


def main():
    """Run all examples"""
    examples = [
        example_1_basic_classification,
        example_2_health_effects,
        example_3_personalized_advice,
        example_4_complete_assessment,
        example_5_multi_persona_assessment,
        example_6_pollution_escalation,
        example_7_different_pollutants,
        example_8_json_output,
        example_9_risk_threshold_boundaries,
        example_10_advice_structure,
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {e}")
    
    print("\n" + "="*80)
    print("✓ All examples completed!")
    print("="*80)


if __name__ == "__main__":
    main()
