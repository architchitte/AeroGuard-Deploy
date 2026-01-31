"""
Generative AI Explainer - Usage Examples

This module demonstrates various use cases for the GenerativeExplainer class,
showing how to generate human-readable explanations for AQI data with
intelligent LLM integration and template fallback.

Examples cover:
- Different AQI values and trends
- Multiple personas with specific health guidance
- Various explanation styles
- Error handling and fallback behavior
- Integration patterns with the explainability module
"""

from app.services.generative_explainer import (
    GenerativeExplainer,
    LLMConfiguration,
    APIProvider,
    ExplanationStyle,
    create_generative_explainer,
)


# ============================================================================
# Example 1: Basic Usage with Template Fallback (Recommended for offline mode)
# ============================================================================

def example_1_basic_template_usage():
    """
    Demonstrates basic usage with template-based fallback.
    This is the recommended approach when OpenAI API access is unavailable.
    """
    print("\n" + "="*70)
    print("Example 1: Basic Template-Based Explanation")
    print("="*70)
    
    # Create explainer with template provider
    config = LLMConfiguration(provider=APIProvider.TEMPLATE)
    explainer = GenerativeExplainer(config)
    
    # Generate explanation for moderate AQI with rising trend
    result = explainer.generate_explanation(
        aqi_value=80.0,
        trend="rising",
        main_factors=["traffic", "industrial_emissions"],
        duration="temporary",
        persona="general_public"
    )
    
    print(f"\nAQI Value: 80.0 (Moderate)")
    print(f"Trend: Rising")
    print(f"Main Factors: Traffic, Industrial Emissions")
    print(f"Duration: Temporary")
    print(f"Persona: General Public")
    print(f"\n--- Generated Explanation ---")
    print(result.explanation)
    print(f"\n--- Health Advisory ---")
    print(f"Message: {result.health_advisory.message}")
    print(f"Severity: {result.health_advisory.severity}")
    print(f"Affected Groups: {', '.join(result.health_advisory.affected_groups)}")
    print(f"Recommended Actions:")
    for action in result.health_advisory.recommended_actions:
        print(f"  • {action}")
    print(f"\nProvider Used: {result.provider_used.value}")


# ============================================================================
# Example 2: Persona-Specific Guidance (Children)
# ============================================================================

def example_2_children_persona():
    """
    Demonstrates persona-specific guidance for children.
    Shows how advisories change based on vulnerable population.
    """
    print("\n" + "="*70)
    print("Example 2: Children Persona - Vulnerable Population")
    print("="*70)
    
    explainer = GenerativeExplainer(LLMConfiguration(provider=APIProvider.TEMPLATE))
    
    result = explainer.generate_explanation(
        aqi_value=120.0,
        trend="rising",
        main_factors=["vehicle_emissions", "dust"],
        duration="persistent",
        persona="children"
    )
    
    print(f"\nAQI Value: 120.0 (Unhealthy)")
    print(f"Persona: Children (Vulnerable Group)")
    print(f"\n--- Explanation ---")
    print(result.explanation)
    print(f"\n--- Health Advisory for Children ---")
    print(f"Severity: {result.health_advisory.severity}")
    print(f"Message: {result.health_advisory.message}")
    print(f"Recommended Actions:")
    for action in result.health_advisory.recommended_actions:
        print(f"  • {action}")


# ============================================================================
# Example 3: Persona-Specific Guidance (Athletes)
# ============================================================================

def example_3_athletes_persona():
    """
    Demonstrates persona-specific guidance for athletes.
    Shows activity restrictions based on AQI and persona-specific concerns.
    """
    print("\n" + "="*70)
    print("Example 3: Athletes Persona - Activity Restrictions")
    print("="*70)
    
    explainer = GenerativeExplainer(LLMConfiguration(provider=APIProvider.TEMPLATE))
    
    result = explainer.generate_explanation(
        aqi_value=90.0,
        trend="stable",
        main_factors=["wildfire_smoke"],
        duration="temporary",
        persona="athletes"
    )
    
    print(f"\nAQI Value: 90.0 (Unhealthy for Sensitive Groups)")
    print(f"Persona: Athletes")
    print(f"\n--- Explanation ---")
    print(result.explanation)
    print(f"\n--- Health Advisory for Athletes ---")
    print(f"Severity: {result.health_advisory.severity}")
    print(f"Message: {result.health_advisory.message}")
    print(f"Recommended Actions:")
    for action in result.health_advisory.recommended_actions:
        print(f"  • {action}")


# ============================================================================
# Example 4: Different Explanation Styles
# ============================================================================

def example_4_explanation_styles():
    """
    Demonstrates different explanation styles for the same AQI scenario.
    Shows how style affects tone and detail level of explanations.
    """
    print("\n" + "="*70)
    print("Example 4: Different Explanation Styles")
    print("="*70)
    
    styles = [
        ExplanationStyle.TECHNICAL,
        ExplanationStyle.CASUAL,
        ExplanationStyle.URGENT,
        ExplanationStyle.REASSURING,
    ]
    
    explainer = GenerativeExplainer(LLMConfiguration(provider=APIProvider.TEMPLATE))
    
    for style in styles:
        result = explainer.generate_explanation(
            aqi_value=110.0,
            trend="rising",
            main_factors=["industrial_emissions"],
            duration="persistent",
            persona="general_public",
            style=style
        )
        
        print(f"\n--- Style: {style.value.upper()} ---")
        print(result.explanation)


# ============================================================================
# Example 5: Outdoor Workers - High Exposure Persona
# ============================================================================

def example_5_outdoor_workers():
    """
    Demonstrates guidance for outdoor workers who face extended exposure.
    Shows occupational health considerations and protective measures.
    """
    print("\n" + "="*70)
    print("Example 5: Outdoor Workers - Occupational Exposure")
    print("="*70)
    
    explainer = GenerativeExplainer(LLMConfiguration(provider=APIProvider.TEMPLATE))
    
    result = explainer.generate_explanation(
        aqi_value=130.0,
        trend="rising",
        main_factors=["construction_dust", "vehicle_emissions"],
        duration="persistent",
        persona="outdoor_workers"
    )
    
    print(f"\nAQI Value: 130.0 (Unhealthy)")
    print(f"Persona: Outdoor Workers (Extended Exposure)")
    print(f"\n--- Explanation ---")
    print(result.explanation)
    print(f"\n--- Health Advisory for Outdoor Workers ---")
    print(f"Severity: {result.health_advisory.severity}")
    print(f"Message: {result.health_advisory.message}")
    print(f"Recommended Actions:")
    for action in result.health_advisory.recommended_actions:
        print(f"  • {action}")


# ============================================================================
# Example 6: Elderly Population with Special Considerations
# ============================================================================

def example_6_elderly_persona():
    """
    Demonstrates guidance for elderly population.
    Shows how recommendations account for reduced respiratory function.
    """
    print("\n" + "="*70)
    print("Example 6: Elderly Persona - Age-Specific Guidance")
    print("="*70)
    
    explainer = GenerativeExplainer(LLMConfiguration(provider=APIProvider.TEMPLATE))
    
    result = explainer.generate_explanation(
        aqi_value=75.0,
        trend="rising",
        main_factors=["traffic", "low_wind"],
        duration="temporary",
        persona="elderly"
    )
    
    print(f"\nAQI Value: 75.0 (Moderate)")
    print(f"Persona: Elderly (Age-Related Vulnerabilities)")
    print(f"\n--- Explanation ---")
    print(result.explanation)
    print(f"\n--- Health Advisory for Elderly ---")
    print(f"Severity: {result.health_advisory.severity}")
    print(f"Message: {result.health_advisory.message}")
    print(f"Recommended Actions:")
    for action in result.health_advisory.recommended_actions:
        print(f"  • {action}")


# ============================================================================
# Example 7: Critical AQI with Urgent Guidance
# ============================================================================

def example_7_hazardous_aqi():
    """
    Demonstrates guidance for hazardous AQI levels.
    Shows escalated recommendations and urgent messaging.
    """
    print("\n" + "="*70)
    print("Example 7: Hazardous AQI Level - Critical Guidance")
    print("="*70)
    
    explainer = GenerativeExplainer(LLMConfiguration(provider=APIProvider.TEMPLATE))
    
    result = explainer.generate_explanation(
        aqi_value=200.0,
        trend="rising",
        main_factors=["wildfire_smoke", "dust"],
        duration="persistent",
        persona="general_public",
        style=ExplanationStyle.URGENT
    )
    
    print(f"\nAQI Value: 200.0 (Hazardous)")
    print(f"Trend: Rising")
    print(f"Style: URGENT")
    print(f"\n--- Explanation ---")
    print(result.explanation)
    print(f"\n--- Critical Health Advisory ---")
    print(f"Severity: {result.health_advisory.severity}")
    print(f"Message: {result.health_advisory.message}")
    print(f"Recommended Actions:")
    for action in result.health_advisory.recommended_actions:
        print(f"  • {action}")


# ============================================================================
# Example 8: Good Air Quality with Reassuring Message
# ============================================================================

def example_8_good_air_quality():
    """
    Demonstrates guidance for good air quality conditions.
    Shows reassuring messaging when pollution is low.
    """
    print("\n" + "="*70)
    print("Example 8: Good Air Quality - Reassuring Message")
    print("="*70)
    
    explainer = GenerativeExplainer(LLMConfiguration(provider=APIProvider.TEMPLATE))
    
    result = explainer.generate_explanation(
        aqi_value=35.0,
        trend="falling",
        main_factors=["strong_wind", "precipitation"],
        duration="temporary",
        persona="general_public",
        style=ExplanationStyle.REASSURING
    )
    
    print(f"\nAQI Value: 35.0 (Good)")
    print(f"Trend: Falling")
    print(f"Style: REASSURING")
    print(f"\n--- Explanation ---")
    print(result.explanation)
    print(f"\n--- Health Advisory ---")
    print(f"Severity: {result.health_advisory.severity}")
    print(f"Message: {result.health_advisory.message}")
    print(f"Recommended Actions:")
    for action in result.health_advisory.recommended_actions:
        print(f"  • {action}")


# ============================================================================
# Example 9: Factory Function with Convenient Defaults
# ============================================================================

def example_9_factory_function():
    """
    Demonstrates the factory function for quick explainer creation.
    Shows default configuration and customization options.
    """
    print("\n" + "="*70)
    print("Example 9: Factory Function - Quick Setup")
    print("="*70)
    
    # Create explainer with defaults (Template provider, no API key needed)
    explainer = create_generative_explainer()
    
    print(f"\nCreated explainer with factory function (template provider)")
    
    result = explainer.generate_explanation(
        aqi_value=60.0,
        trend="stable",
        main_factors=["vehicular_traffic"],
        duration="temporary",
        persona="general_public"
    )
    
    print(f"\nAQI Value: 60.0 (Moderate)")
    print(f"\n--- Generated Explanation ---")
    print(result.explanation)
    print(f"\nProvider Used: {result.provider_used.value}")


# ============================================================================
# Example 10: Integration with Explainability Module Output
# ============================================================================

def example_10_integration_with_explainability():
    """
    Demonstrates how GenerativeExplainer integrates with the
    Explainability module output.
    
    This example shows a typical workflow:
    1. Explainability module analyzes AQI data
    2. GenerativeExplainer creates human-readable explanation
    3. Combined output sent to user
    """
    print("\n" + "="*70)
    print("Example 10: Integration with Explainability Module")
    print("="*70)
    
    # Simulated output from explainability module
    analysis_data = {
        "aqi_value": 95.0,
        "trend": "rising",
        "main_factors": ["traffic", "industrial"],
        "duration": "persistent",
        "explanation_type": "moderate_with_concern",
    }
    
    # User persona (from health classification or user profile)
    user_persona = "general_public"
    
    # Generate explanation using the analysis data
    explainer = GenerativeExplainer(LLMConfiguration(provider=APIProvider.TEMPLATE))
    
    result = explainer.generate_explanation(
        aqi_value=analysis_data["aqi_value"],
        trend=analysis_data["trend"],
        main_factors=analysis_data["main_factors"],
        duration=analysis_data["duration"],
        persona=user_persona
    )
    
    print(f"\n--- Analysis Data from Explainability Module ---")
    print(f"AQI Value: {analysis_data['aqi_value']}")
    print(f"Trend: {analysis_data['trend']}")
    print(f"Main Factors: {', '.join(analysis_data['main_factors'])}")
    print(f"Duration: {analysis_data['duration']}")
    
    print(f"\n--- User Profile ---")
    print(f"Persona: {user_persona}")
    
    print(f"\n--- Generated Explanation ---")
    print(result.explanation)
    
    print(f"\n--- Health Advisory ---")
    print(f"Message: {result.health_advisory.message}")
    print(f"Severity: {result.health_advisory.severity}")
    print(f"Recommended Actions:")
    for action in result.health_advisory.recommended_actions:
        print(f"  • {action}")
    
    print(f"\\n--- Metadata ---")
    print(f"Provider: {result.provider_used.value}")


# ============================================================================
# Example 11: Health Advisory Only Generation
# ============================================================================

def example_11_health_advisory_only():
    """
    Demonstrates generating only health advisory without explanation.
    Useful when explanation is provided separately.
    """
    print("\n" + "="*70)
    print("Example 11: Health Advisory Only Generation")
    print("="*70)
    
    explainer = GenerativeExplainer(LLMConfiguration(provider=APIProvider.TEMPLATE))
    
    result = explainer.generate_health_advisory_only(
        aqi_value=105.0,
        persona="children"
    )
    
    print(f"\nAQI Value: 105.0 (Unhealthy)")
    print(f"Persona: Children")
    print(f"\n--- Health Advisory Only ---")
    print(f"Severity: {result.severity}")
    print(f"Message: {result.message}")
    print(f"Affected Groups: {', '.join(result.affected_groups)}")
    print(f"Recommended Actions:")
    for action in result.recommended_actions:
        print(f"  • {action}")


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    """
    Run all examples to demonstrate GenerativeExplainer capabilities.
    """
    print("\n" + "="*70)
    print("GENERATIVE AI EXPLAINER - COMPREHENSIVE EXAMPLES")
    print("="*70)
    print("\nDemonstrating LLM-based explanation generation with template fallback")
    print("for AeroGuard AQI analysis and health guidance.")
    
    # Run all examples
    example_1_basic_template_usage()
    example_2_children_persona()
    example_3_athletes_persona()
    example_4_explanation_styles()
    example_5_outdoor_workers()
    example_6_elderly_persona()
    example_7_hazardous_aqi()
    example_8_good_air_quality()
    example_9_factory_function()
    example_10_integration_with_explainability()
    example_11_health_advisory_only()
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nKey Takeaways:")
    print("• Template provider works offline without API keys")
    print("• Different personas receive tailored health guidance")
    print("• Explanation styles adapt tone to urgency level")
    print("• Seamless integration with explainability module")
    print("• Health advisories account for vulnerable populations")
    print("\nFor OpenAI integration, set API key in LLMConfiguration:")
    print("  config = LLMConfiguration(api_key='your-key', provider=APIProvider.OPENAI)")
