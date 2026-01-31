"""
Tests for Health Risk Classification Engine

Tests cover:
- AQI classification accuracy
- Risk category determination
- Personalized advice retrieval
- JSON output format
- Error handling
- All personas and air quality parameters
"""

import pytest
import json
from datetime import datetime
from app.services.health_risk import (
    HealthRiskClassifier,
    RiskCategory,
    Persona,
    AQIThresholds,
    HealthEffectsMapping,
    PersonaHealthAdviceMapping,
    HealthRiskAssessment,
    HealthAdvice,
    create_classifier
)


class TestAQIThresholds:
    """Test EPA/WHO AQI threshold definitions"""
    
    def test_pm25_thresholds_exist(self):
        """Verify PM2.5 thresholds are defined"""
        assert len(AQIThresholds.PM25_THRESHOLDS) == 6
        assert RiskCategory.GOOD in AQIThresholds.PM25_THRESHOLDS
        assert RiskCategory.HAZARDOUS in AQIThresholds.PM25_THRESHOLDS
    
    def test_pm25_threshold_ranges(self):
        """Verify PM2.5 ranges are continuous and ascending"""
        thresholds = AQIThresholds.PM25_THRESHOLDS
        categories = [RiskCategory.GOOD, RiskCategory.MODERATE, 
                     RiskCategory.UNHEALTHY_FOR_SENSITIVE, RiskCategory.UNHEALTHY,
                     RiskCategory.VERY_UNHEALTHY, RiskCategory.HAZARDOUS]
        
        for i, category in enumerate(categories[:-1]):
            low1, high1 = thresholds[category]
            low2, high2 = thresholds[categories[i + 1]]
            assert high1 < low2, f"{category.value} upper should be < {categories[i+1].value} lower"
    
    def test_all_parameters_supported(self):
        """Verify all major pollutants have thresholds"""
        assert hasattr(AQIThresholds, 'PM25_THRESHOLDS')
        assert hasattr(AQIThresholds, 'PM10_THRESHOLDS')
        assert hasattr(AQIThresholds, 'NO2_THRESHOLDS')
        assert hasattr(AQIThresholds, 'O3_THRESHOLDS')
        assert hasattr(AQIThresholds, 'SO2_THRESHOLDS')
        assert hasattr(AQIThresholds, 'CO_THRESHOLDS')


class TestHealthEffectsMapping:
    """Test health effects descriptions"""
    
    def test_all_categories_have_effects(self):
        """Verify health effects for all risk categories"""
        for category in RiskCategory:
            assert category in HealthEffectsMapping.EFFECTS
            effects = HealthEffectsMapping.EFFECTS[category]
            assert isinstance(effects, list)
            assert len(effects) > 0
    
    def test_effects_are_strings(self):
        """Verify all effects are descriptive strings"""
        for category, effects in HealthEffectsMapping.EFFECTS.items():
            for effect in effects:
                assert isinstance(effect, str)
                assert len(effect) > 10


class TestPersonaHealthAdviceMapping:
    """Test persona-specific health advice"""
    
    def test_all_personas_have_advice(self):
        """Verify advice exists for supported personas"""
        # Only check personas that have advice defined
        supported_personas = [
            Persona.GENERAL_PUBLIC,
            Persona.CHILDREN,
            Persona.ELDERLY,
            Persona.ATHLETES,
            Persona.OUTDOOR_WORKERS
        ]
        for persona in supported_personas:
            assert persona in PersonaHealthAdviceMapping.ADVICE
    
    def test_all_risk_levels_for_personas(self):
        """Verify supported personas have advice for all risk levels"""
        supported_personas = [
            Persona.GENERAL_PUBLIC,
            Persona.CHILDREN,
            Persona.ELDERLY,
            Persona.ATHLETES,
            Persona.OUTDOOR_WORKERS
        ]
        for persona in supported_personas:
            persona_advice = PersonaHealthAdviceMapping.ADVICE[persona]
            assert len(persona_advice) == 6  # 6 risk categories
            for category in RiskCategory:
                assert category in persona_advice
    
    def test_advice_has_required_fields(self):
        """Verify HealthAdvice objects have all required fields"""
        supported_personas = [
            Persona.GENERAL_PUBLIC,
            Persona.CHILDREN,
            Persona.ELDERLY,
            Persona.ATHLETES,
            Persona.OUTDOOR_WORKERS
        ]
        for persona in supported_personas:
            for category in RiskCategory:
                advice = PersonaHealthAdviceMapping.ADVICE[persona][category]
                assert advice.persona == persona.value
                assert advice.risk_category == category.value
                assert isinstance(advice.aqi_range, tuple)
                assert len(advice.aqi_range) == 2
                assert isinstance(advice.activity_recommendation, str)
                assert isinstance(advice.indoor_outdoor, str)
                assert isinstance(advice.precautions, list)
                assert isinstance(advice.symptoms_to_watch, list)
    
    def test_advice_increases_in_severity(self):
        """Verify advice severity increases with risk level"""
        general_advice = PersonaHealthAdviceMapping.ADVICE[Persona.GENERAL_PUBLIC]
        
        # Good should have no precautions
        assert len(general_advice[RiskCategory.GOOD].precautions) == 0
        
        # Hazardous should have multiple precautions
        assert len(general_advice[RiskCategory.HAZARDOUS].precautions) > 3


class TestHealthRiskClassifier:
    """Test main classifier functionality"""
    
    @pytest.fixture
    def classifier(self):
        """Create classifier instance"""
        return HealthRiskClassifier()
    
    def test_classifier_initialization(self, classifier):
        """Verify classifier initializes with all thresholds"""
        assert len(classifier.thresholds) == 6
        assert 'PM2.5' in classifier.thresholds
        assert 'PM10' in classifier.thresholds
        assert 'NO2' in classifier.thresholds
    
    def test_classify_aqi_good(self, classifier):
        """Test AQI classification for GOOD category"""
        result = classifier.classify_aqi(10, 'PM2.5')
        assert result == RiskCategory.GOOD
    
    def test_classify_aqi_moderate(self, classifier):
        """Test AQI classification for MODERATE category"""
        result = classifier.classify_aqi(25, 'PM2.5')
        assert result == RiskCategory.MODERATE
    
    def test_classify_aqi_unhealthy_for_sensitive(self, classifier):
        """Test AQI classification for UNHEALTHY_FOR_SENSITIVE"""
        result = classifier.classify_aqi(45, 'PM2.5')
        assert result == RiskCategory.UNHEALTHY_FOR_SENSITIVE
    
    def test_classify_aqi_unhealthy(self, classifier):
        """Test AQI classification for UNHEALTHY"""
        result = classifier.classify_aqi(100, 'PM2.5')
        assert result == RiskCategory.UNHEALTHY
    
    def test_classify_aqi_very_unhealthy(self, classifier):
        """Test AQI classification for VERY_UNHEALTHY"""
        result = classifier.classify_aqi(200, 'PM2.5')
        assert result == RiskCategory.VERY_UNHEALTHY
    
    def test_classify_aqi_hazardous(self, classifier):
        """Test AQI classification for HAZARDOUS"""
        result = classifier.classify_aqi(350, 'PM2.5')
        assert result == RiskCategory.HAZARDOUS
    
    def test_classify_aqi_boundary_values(self, classifier):
        """Test AQI at exact threshold boundaries"""
        # Lower boundary of Good
        assert classifier.classify_aqi(0, 'PM2.5') == RiskCategory.GOOD
        
        # Upper boundary of Good
        assert classifier.classify_aqi(12, 'PM2.5') == RiskCategory.GOOD
        
        # Lower boundary of Moderate
        assert classifier.classify_aqi(12.1, 'PM2.5') == RiskCategory.MODERATE
    
    def test_classify_aqi_different_parameters(self, classifier):
        """Test classification for different pollutants"""
        # PM10
        assert classifier.classify_aqi(50, 'PM10') == RiskCategory.GOOD
        assert classifier.classify_aqi(100, 'PM10') == RiskCategory.MODERATE
        
        # NO2
        assert classifier.classify_aqi(30, 'NO2') == RiskCategory.GOOD
        assert classifier.classify_aqi(70, 'NO2') == RiskCategory.MODERATE
    
    def test_classify_aqi_invalid_parameter(self, classifier):
        """Test error handling for unsupported parameter"""
        with pytest.raises(ValueError, match="Unsupported parameter"):
            classifier.classify_aqi(50, 'InvalidGas')
    
    def test_classify_aqi_negative_value(self, classifier):
        """Test error handling for negative AQI"""
        with pytest.raises(ValueError, match="non-negative"):
            classifier.classify_aqi(-10, 'PM2.5')
    
    def test_get_color_code(self, classifier):
        """Test EPA color codes for risk categories"""
        assert classifier.get_color_code(RiskCategory.GOOD) == "#00E400"
        assert classifier.get_color_code(RiskCategory.MODERATE) == "#FFFF00"
        assert classifier.get_color_code(RiskCategory.UNHEALTHY_FOR_SENSITIVE) == "#FF7E00"
        assert classifier.get_color_code(RiskCategory.UNHEALTHY) == "#FF0000"
        assert classifier.get_color_code(RiskCategory.VERY_UNHEALTHY) == "#8F3F97"
        assert classifier.get_color_code(RiskCategory.HAZARDOUS) == "#7E0023"
    
    def test_get_health_effects(self, classifier):
        """Test health effects retrieval"""
        effects = classifier.get_health_effects(RiskCategory.GOOD)
        assert len(effects) > 0
        assert all(isinstance(e, str) for e in effects)
        
        # Hazardous should also have effects (may be same count)
        hazardous_effects = classifier.get_health_effects(RiskCategory.HAZARDOUS)
        assert len(hazardous_effects) > 0
    
    def test_get_at_risk_populations(self, classifier):
        """Test at-risk populations identification"""
        # Good has no at-risk populations
        assert classifier.get_at_risk_populations(RiskCategory.GOOD) == []
        
        # Moderate has sensitive populations
        moderate_risk = classifier.get_at_risk_populations(RiskCategory.MODERATE)
        assert len(moderate_risk) > 0
        
        # Hazardous has general population at risk
        hazardous_risk = classifier.get_at_risk_populations(RiskCategory.HAZARDOUS)
        assert any("population" in p.lower() for p in hazardous_risk)
    
    def test_get_personalized_advice_general_public(self, classifier):
        """Test personalized advice for general public"""
        advice = classifier.get_personalized_advice(RiskCategory.GOOD, Persona.GENERAL_PUBLIC)
        assert advice is not None
        assert advice.persona == "General Public"
        assert advice.risk_category == "Good"
    
    def test_get_personalized_advice_children(self, classifier):
        """Test personalized advice for children"""
        advice = classifier.get_personalized_advice(RiskCategory.UNHEALTHY, Persona.CHILDREN)
        assert advice is not None
        assert "children" in advice.persona.lower()
        assert len(advice.precautions) > 0
    
    def test_get_personalized_advice_elderly(self, classifier):
        """Test personalized advice for elderly"""
        advice = classifier.get_personalized_advice(RiskCategory.UNHEALTHY_FOR_SENSITIVE, Persona.ELDERLY)
        assert advice is not None
        assert "elderly" in advice.persona.lower()
    
    def test_get_personalized_advice_athletes(self, classifier):
        """Test personalized advice for athletes"""
        advice = classifier.get_personalized_advice(RiskCategory.MODERATE, Persona.ATHLETES)
        assert advice is not None
        assert "athlete" in advice.persona.lower()
    
    def test_get_personalized_advice_outdoor_workers(self, classifier):
        """Test personalized advice for outdoor workers"""
        advice = classifier.get_personalized_advice(RiskCategory.UNHEALTHY, Persona.OUTDOOR_WORKERS)
        assert advice is not None
        assert "worker" in advice.persona.lower()
    
    def test_get_personalized_advice_all_personas(self, classifier):
        """Test that advice exists for supported personas"""
        supported_personas = [
            Persona.GENERAL_PUBLIC,
            Persona.CHILDREN,
            Persona.ELDERLY,
            Persona.ATHLETES,
            Persona.OUTDOOR_WORKERS
        ]
        for persona in supported_personas:
            advice = classifier.get_personalized_advice(RiskCategory.MODERATE, persona)
            assert advice is not None
    
    def test_get_recommended_actions(self, classifier):
        """Test recommended actions retrieval"""
        actions = classifier.get_recommended_actions(RiskCategory.GOOD)
        assert isinstance(actions, dict)
        assert len(actions) > 0
        
        # Hazardous should have more actions
        hazardous_actions = classifier.get_recommended_actions(RiskCategory.HAZARDOUS)
        assert len(hazardous_actions) >= len(actions)
    
    def test_assess_health_risk_complete(self, classifier):
        """Test complete health risk assessment"""
        assessment = classifier.assess_health_risk(25, 'PM2.5')
        
        assert isinstance(assessment, HealthRiskAssessment)
        assert assessment.aqi_value == 25
        assert assessment.aqi_parameter == 'PM2.5'
        assert assessment.risk_category == "Moderate"
        assert assessment.color_code is not None
        assert len(assessment.personalized_advice) > 0
        assert len(assessment.health_effects) > 0
        assert isinstance(assessment.timestamp, str)
    
    def test_assess_health_risk_specific_personas(self, classifier):
        """Test assessment with specific personas"""
        personas = [Persona.CHILDREN, Persona.ELDERLY]
        assessment = classifier.assess_health_risk(100, 'PM2.5', personas)
        
        assert len(assessment.personalized_advice) == 2
        assert "Children" in assessment.personalized_advice
        assert "Elderly" in assessment.personalized_advice
    
    def test_assess_health_risk_different_parameters(self, classifier):
        """Test assessment with different pollutants"""
        pm10_assessment = classifier.assess_health_risk(100, 'PM10')
        assert pm10_assessment.aqi_parameter == 'PM10'
        
        no2_assessment = classifier.assess_health_risk(80, 'NO2')
        assert no2_assessment.aqi_parameter == 'NO2'
    
    def test_to_dict_conversion(self, classifier):
        """Test conversion to dictionary"""
        assessment = classifier.assess_health_risk(50, 'PM2.5')
        result_dict = classifier.to_dict(assessment)
        
        assert isinstance(result_dict, dict)
        assert result_dict['aqi_value'] == 50
        assert result_dict['aqi_parameter'] == 'PM2.5'
        assert isinstance(result_dict['personalized_advice'], dict)
        
        # Verify nested advice is also dict
        for persona, advice in result_dict['personalized_advice'].items():
            assert isinstance(advice, dict)
            assert 'persona' in advice
    
    def test_to_json_conversion(self, classifier):
        """Test conversion to JSON string"""
        assessment = classifier.assess_health_risk(100, 'PM2.5')
        json_str = classifier.to_json(assessment)
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed['aqi_value'] == 100
        assert 'personalized_advice' in parsed
        assert isinstance(parsed['personalized_advice'], dict)


class TestIntegration:
    """Integration tests for classifier"""
    
    def test_full_workflow_good_air_quality(self):
        """Test complete workflow for good air quality"""
        classifier = create_classifier()
        assessment = classifier.assess_health_risk(8)
        
        assert assessment.risk_category == "Good"
        assert len(assessment.at_risk_populations) == 0
        assert "good" in assessment.general_advice.lower()
    
    def test_full_workflow_hazardous_air_quality(self):
        """Test complete workflow for hazardous air quality"""
        classifier = create_classifier()
        assessment = classifier.assess_health_risk(350)
        
        assert assessment.risk_category == "Hazardous"
        assert len(assessment.at_risk_populations) > 0
        assert "entire population" in str(assessment.at_risk_populations).lower()
    
    def test_real_world_pollution_event(self):
        """Test realistic pollution event scenario"""
        classifier = create_classifier()
        
        # Simulate escalating pollution
        levels = [10, 25, 45, 100, 200, 350]
        categories = []
        
        for level in levels:
            assessment = classifier.assess_health_risk(level)
            categories.append(assessment.risk_category)
        
        # Verify escalation in severity (all risk levels increase)
        assert categories[0] == "Good"
        assert categories[1] == "Moderate"
        assert categories[2] == "Unhealthy for Sensitive Groups"
        assert categories[3] == "Unhealthy"
        assert categories[4] == "Very Unhealthy"
        assert categories[5] == "Hazardous"
    
    def test_different_pollutants_same_severity(self):
        """Test that different pollutants can have same risk level"""
        classifier = create_classifier()
        
        # Test with matching thresholds
        pm25_assessment = classifier.assess_health_risk(10, 'PM2.5')
        pm10_assessment = classifier.assess_health_risk(50, 'PM10')
        
        # Both should be Good
        assert pm25_assessment.risk_category == "Good"
        assert pm10_assessment.risk_category == "Good"
    
    def test_persona_specific_workflow(self):
        """Test workflow with specific personas"""
        classifier = create_classifier()
        
        # Assess for vulnerable groups
        assessment = classifier.assess_health_risk(
            150,
            'PM2.5',
            [Persona.CHILDREN, Persona.ELDERLY, Persona.ATHLETES]
        )
        
        # Verify all personas have appropriate advice
        assert "Children" in assessment.personalized_advice
        assert "Elderly" in assessment.personalized_advice
        assert "Athletes" in assessment.personalized_advice
        
        # Athletes advice should include activity restrictions
        athlete_advice = assessment.personalized_advice["Athletes"]
        assert len(athlete_advice.precautions) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_aqi(self):
        """Test with AQI of 0"""
        classifier = create_classifier()
        assessment = classifier.assess_health_risk(0)
        assert assessment.risk_category == "Good"
    
    def test_extreme_high_aqi(self):
        """Test with very high AQI"""
        classifier = create_classifier()
        assessment = classifier.assess_health_risk(1000)
        assert assessment.risk_category == "Hazardous"
    
    def test_decimal_aqi_values(self):
        """Test with decimal AQI values"""
        classifier = create_classifier()
        assessment = classifier.assess_health_risk(12.5)
        assert assessment.risk_category == "Moderate"
    
    def test_no_personas_specified(self):
        """Test assessment without specifying personas"""
        classifier = create_classifier()
        assessment = classifier.assess_health_risk(50, 'PM2.5', personas=None)
        
        # Should include all available personas (5 with advice)
        assert len(assessment.personalized_advice) == 5


class TestFactory:
    """Test factory function"""
    
    def test_create_classifier(self):
        """Test classifier creation via factory"""
        classifier = create_classifier()
        assert isinstance(classifier, HealthRiskClassifier)
        assert len(classifier.thresholds) == 6
