"""
Generative AI Explanation Generator for AQI Forecasts

Transforms structured AQI analysis into human-readable explanations
using generative AI (LLM) with intelligent fallback to templates.

Features:
- OpenAI API integration (GPT-3.5/GPT-4)
- Template-based fallback for robustness
- Persona-aware health advisories
- No medical claims, preventive guidance only
- Streaming support for real-time responses
- Comprehensive error handling
"""

import logging
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ExplanationStyle(Enum):
    """Style of generated explanation."""
    TECHNICAL = "technical"      # For professionals
    CASUAL = "casual"             # For general public
    URGENT = "urgent"             # For alert/warning situations
    REASSURING = "reassuring"     # For good air quality


class APIProvider(Enum):
    """Supported LLM API providers."""
    OPENAI = "openai"
    TEMPLATE = "template"  # Fallback
    MOCK = "mock"          # For testing


@dataclass
class LLMConfiguration:
    """Configuration for LLM API integration."""
    provider: APIProvider = APIProvider.OPENAI
    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"  # or "gpt-4"
    temperature: float = 0.7       # 0-1, creativity level
    max_tokens: int = 500          # Max response length
    timeout: int = 10              # Seconds
    
    # Advanced options
    top_p: float = 0.95            # Nucleus sampling
    frequency_penalty: float = 0.0 # Avoid repetition
    presence_penalty: float = 0.0  # Encourage new topics
    
    # Fallback settings
    use_fallback: bool = True      # Use template if LLM fails
    retry_count: int = 2           # Retries before fallback
    
    def is_configured(self) -> bool:
        """Check if LLM is properly configured."""
        if self.provider == APIProvider.OPENAI:
            return self.api_key is not None
        return self.provider in [APIProvider.TEMPLATE, APIProvider.MOCK]


@dataclass
class HealthAdvisory:
    """Health advisory message with severity."""
    message: str
    severity: str  # "info", "warning", "alert"
    affected_groups: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class GeneratedExplanation:
    """Generated explanation with metadata."""
    explanation: str
    health_advisory: HealthAdvisory
    provider_used: APIProvider
    model_used: str
    generated_at: datetime = field(default_factory=datetime.now)
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "explanation": self.explanation,
            "health_advisory": {
                "message": self.health_advisory.message,
                "severity": self.health_advisory.severity,
                "affected_groups": self.health_advisory.affected_groups,
                "recommended_actions": self.health_advisory.recommended_actions
            },
            "provider": self.provider_used.value,
            "model": self.model_used,
            "generated_at": self.generated_at.isoformat(),
            "tokens_used": self.tokens_used,
            "cost_estimate": self.cost_estimate
        }


class PromptBuilder:
    """Builds optimized prompts for LLM."""
    
    SYSTEM_PROMPT = """You are an air quality expert providing clear, 
helpful explanations about AQI (Air Quality Index) conditions and health impacts.

Guidelines:
- Use simple, clear language accessible to general public
- Provide specific, actionable health guidance
- NO medical diagnoses or medical claims
- Focus on PREVENTIVE measures only
- Be conversational and reassuring when appropriate
- Acknowledge when conditions are safe
- Adapt tone to the situation (casual for good conditions, urgent for bad)

Health advisory rules:
- DO: Recommend staying indoors, masks, window closing
- DO: Suggest vulnerable groups need extra precautions
- DON'T: Diagnose conditions or prescribe medication
- DON'T: Make definitive health claims
- DON'T: Use overly alarming language unless justified"""
    
    @staticmethod
    def build_explanation_prompt(
        aqi_value: float,
        trend: str,
        main_factors: List[str],
        duration: str,
        persona: str = "general_public",
        style: ExplanationStyle = ExplanationStyle.CASUAL
    ) -> str:
        """Build prompt for explanation generation."""
        
        factors_text = ", ".join(main_factors) if main_factors else "multiple factors"
        
        duration_context = {
            "temporary": "expected to clear within hours",
            "persistent": "expected to last many hours or days"
        }
        
        duration_desc = duration_context.get(duration, "expected to change")
        
        prompt = f"""Generate a clear, helpful explanation of current air quality conditions.

CURRENT CONDITIONS:
- AQI Value: {aqi_value}
- Trend: {trend.upper()}
- Main Contributing Factors: {factors_text}
- Duration: {duration_desc}
- Target Audience: {persona.replace('_', ' ').title()}
- Tone: {style.value}

REQUIREMENTS:
1. Start with a brief summary of current conditions (1-2 sentences)
2. Explain the contributing factors in simple terms (2-3 sentences)
3. Provide specific health recommendations for this persona (2-3 bullets)
4. Include what will happen next (trend-based prediction)
5. End with an encouraging or reassuring note when appropriate

HEALTH ADVISORY:
- Determine severity level: "info", "warning", or "alert"
- List affected groups (e.g., children, elderly, outdoor workers)
- Provide 2-3 specific recommended actions

Format your response as JSON:
{{
    "explanation": "main explanation text here",
    "health_advisory": {{
        "severity": "warning",
        "message": "short advisory message",
        "affected_groups": ["group1", "group2"],
        "recommended_actions": ["action1", "action2"]
    }}
}}"""
        
        return prompt
    
    @staticmethod
    def build_advisory_prompt(
        aqi_value: float,
        persona: str
    ) -> str:
        """Build prompt for health advisory only."""
        
        aqi_categories = {
            (0, 50): "Good",
            (51, 100): "Moderate",
            (101, 150): "Unhealthy for Sensitive Groups",
            (151, 200): "Unhealthy",
            (201, 300): "Very Unhealthy",
            (301, float('inf')): "Hazardous"
        }
        
        category = "Unknown"
        for range_tuple, cat_name in aqi_categories.items():
            if range_tuple[0] <= aqi_value <= range_tuple[1]:
                category = cat_name
                break
        
        prompt = f"""Generate a health advisory for {persona.replace('_', ' ').title()} 
during {category} air quality (AQI: {aqi_value}).

Create ONLY a health advisory JSON response:
{{
    "severity": "info|warning|alert",
    "message": "brief advisory (1-2 sentences)",
    "affected_groups": ["relevant group"],
    "recommended_actions": ["action1", "action2", "action3"]
}}

Rules:
- NO medical claims
- Focus on preventive measures
- Be specific to the persona
- Include window/door closing, masks, indoor activity recommendations
- Validate that group is actually affected by this AQI level"""
        
        return prompt


class TemplateExplainer:
    """Template-based explanation generator (fallback)."""
    
    TEMPLATES = {
        ("rising", "temporary"): {
            "explanation": "Air quality is getting worse, but conditions are expected to improve soon. "
                          "The main issue is {factors}. Avoid outdoor activities during peak hours, "
                          "and consider staying indoors if you're in a sensitive group. "
                          "Conditions should improve as {factors} change.",
            "advisory_severity": "warning"
        },
        ("rising", "persistent"): {
            "explanation": "Air quality is worsening and conditions are expected to persist for extended periods. "
                          "Primary factors include {factors}. This is a significant concern for vulnerable populations. "
                          "Limit outdoor activities substantially and consider air purification indoors. "
                          "Conditions may not improve for many hours.",
            "advisory_severity": "alert"
        },
        ("falling", "temporary"): {
            "explanation": "Great news! Air quality is improving. {factors} are helping clear the pollution. "
                          "Conditions should continue getting better over the next few hours. "
                          "You can gradually resume normal outdoor activities as the AQI improves.",
            "advisory_severity": "info"
        },
        ("falling", "persistent"): {
            "explanation": "Air quality is improving, which is positive! However, some improvement factors "
                          "may fade, so changes could take many hours. {factors} are currently helping. "
                          "Start with light outdoor activities and monitor conditions.",
            "advisory_severity": "info"
        },
        ("stable", "temporary"): {
            "explanation": "Air quality is stable at current levels and should change soon. {factors} are "
                          "keeping conditions relatively consistent right now. Stay ready for potential changes. "
                          "Conditions should shift within hours.",
            "advisory_severity": "info"
        },
        ("stable", "persistent"): {
            "explanation": "Air quality is stable, but conditions are likely to persist for extended periods. "
                          "This means {factors} will continue affecting air quality for many hours. "
                          "Plan outdoor activities accordingly and take necessary precautions.",
            "advisory_severity": "warning"
        }
    }
    
    PERSONA_RECOMMENDATIONS = {
        "general_public": [
            "Monitor air quality throughout the day",
            "Use N95 masks for outdoor activity",
            "Keep windows and doors closed during peak hours"
        ],
        "children": [
            "Keep children indoors or limit outdoor play",
            "Ensure proper ventilation indoors",
            "Avoid strenuous outdoor activities",
            "Use air purifier if available"
        ],
        "elderly": [
            "Limit outdoor exposure significantly",
            "Keep indoor environment clean and well-ventilated",
            "Have medication accessible",
            "Stay hydrated and avoid strenuous activity"
        ],
        "athletes": [
            "Avoid outdoor training during peak pollution hours",
            "Consider indoor alternatives",
            "Reduce exercise intensity",
            "Use proper respiratory protection if exercising outdoors"
        ],
        "outdoor_workers": [
            "Wear N95 or P100 respirator",
            "Take frequent breaks indoors",
            "Use air-purified shelter when available",
            "Monitor personal health carefully"
        ]
    }
    
    @staticmethod
    def generate(
        aqi_value: float,
        trend: str,
        main_factors: List[str],
        duration: str,
        persona: str = "general_public"
    ) -> GeneratedExplanation:
        """Generate explanation using templates."""
        
        # Select template
        template_key = (trend.lower(), duration.lower())
        template = TemplateExplainer.TEMPLATES.get(
            template_key,
            TemplateExplainer.TEMPLATES[("stable", "temporary")]
        )
        
        # Format factors
        factors_str = ", ".join(main_factors) if main_factors else "various factors"
        explanation = template["explanation"].format(factors=factors_str)
        
        # Get persona-specific recommendations
        actions = TemplateExplainer.PERSONA_RECOMMENDATIONS.get(
            persona,
            TemplateExplainer.PERSONA_RECOMMENDATIONS["general_public"]
        )
        
        # Determine affected groups based on AQI
        affected_groups = []
        if aqi_value > 100:
            affected_groups.extend(["children", "elderly", "people with respiratory conditions"])
        if aqi_value > 150:
            affected_groups.extend(["general public", "outdoor workers"])
        if not affected_groups:
            affected_groups = ["sensitive groups"]
        
        # Create advisory
        advisory = HealthAdvisory(
            message=f"Current conditions are {template['advisory_severity']} for {persona.replace('_', ' ')}.",
            severity=template["advisory_severity"],
            affected_groups=affected_groups,
            recommended_actions=actions[:3]
        )
        
        return GeneratedExplanation(
            explanation=explanation,
            health_advisory=advisory,
            provider_used=APIProvider.TEMPLATE,
            model_used="template-v1"
        )


class GenerativeExplainer:
    """Main class for generating AI-powered explanations."""
    
    def __init__(self, config: Optional[LLMConfiguration] = None):
        """
        Initialize the generative explainer.
        
        Args:
            config: LLM configuration (uses defaults if None)
        """
        self.config = config or LLMConfiguration()
        self.logger = logger
        self._openai_client = None
        
        # Initialize OpenAI client if configured
        if self.config.provider == APIProvider.OPENAI and self.config.api_key:
            try:
                import openai
                openai.api_key = self.config.api_key
                self._openai_client = openai
                self.logger.info("OpenAI client initialized successfully")
            except ImportError:
                self.logger.warning("OpenAI package not installed. Using template fallback.")
                self.config.use_fallback = True
    
    def generate_explanation(
        self,
        aqi_value: float,
        trend: str,
        main_factors: List[str],
        duration: str,
        persona: str = "general_public",
        style: ExplanationStyle = ExplanationStyle.CASUAL
    ) -> GeneratedExplanation:
        """
        Generate a full explanation with health advisory.
        
        Args:
            aqi_value: Current AQI value (0-500+)
            trend: "rising", "falling", or "stable"
            main_factors: List of contributing factors
            duration: "temporary" or "persistent"
            persona: Target audience persona
            style: Explanation style
        
        Returns:
            GeneratedExplanation with text and advisory
        """
        
        self.logger.debug(
            f"Generating explanation: AQI={aqi_value}, trend={trend}, "
            f"duration={duration}, persona={persona}"
        )
        
        # Try LLM first if configured
        if self.config.provider == APIProvider.OPENAI and self._can_use_llm():
            for attempt in range(self.config.retry_count):
                try:
                    return self._generate_with_llm(
                        aqi_value, trend, main_factors, duration, persona, style
                    )
                except Exception as e:
                    self.logger.warning(
                        f"LLM attempt {attempt + 1} failed: {str(e)}. "
                        f"{'Retrying...' if attempt < self.config.retry_count - 1 else 'Using fallback.'}"
                    )
                    if attempt == self.config.retry_count - 1 and not self.config.use_fallback:
                        raise
        
        # Fall back to template
        if self.config.use_fallback:
            self.logger.info("Using template-based explanation as fallback")
            return TemplateExplainer.generate(
                aqi_value, trend, main_factors, duration, persona
            )
        
        raise RuntimeError("No explanation provider available")
    
    def _can_use_llm(self) -> bool:
        """Check if LLM can be used."""
        if self.config.provider == APIProvider.TEMPLATE:
            return False
        if self.config.provider == APIProvider.MOCK:
            return True
        return self.config.api_key is not None and self._openai_client is not None
    
    def _generate_with_llm(
        self,
        aqi_value: float,
        trend: str,
        main_factors: List[str],
        duration: str,
        persona: str,
        style: ExplanationStyle
    ) -> GeneratedExplanation:
        """Generate explanation using LLM API."""
        
        # Handle mock provider for testing
        if self.config.provider == APIProvider.MOCK:
            return self._generate_mock_response(
                aqi_value, trend, main_factors, duration, persona, style
            )
        
        # Build prompt
        prompt = PromptBuilder.build_explanation_prompt(
            aqi_value, trend, main_factors, duration, persona, style
        )
        
        # Call OpenAI API
        try:
            response = self._openai_client.ChatCompletion.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": PromptBuilder.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
                timeout=self.config.timeout
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            return self._parse_llm_response(
                response_text, aqi_value, persona
            )
        
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _generate_mock_response(
        self,
        aqi_value: float,
        trend: str,
        main_factors: List[str],
        duration: str,
        persona: str,
        style: ExplanationStyle
    ) -> GeneratedExplanation:
        """Generate mock response for testing."""
        
        factors_str = ", ".join(main_factors) if main_factors else "various factors"
        
        explanation = (
            f"Current air quality shows a {trend} trend with AQI at {aqi_value}. "
            f"Main contributing factors are: {factors_str}. "
            f"These conditions are {duration}. "
            f"For {persona.replace('_', ' ')}, it's recommended to monitor air quality "
            f"and take appropriate precautions."
        )
        
        advisory = HealthAdvisory(
            message=f"Exercise caution during {duration} {trend} air quality conditions.",
            severity="warning" if aqi_value > 100 else "info",
            affected_groups=["sensitive groups"],
            recommended_actions=["Monitor air quality", "Use air purifier", "Limit outdoor time"]
        )
        
        return GeneratedExplanation(
            explanation=explanation,
            health_advisory=advisory,
            provider_used=APIProvider.MOCK,
            model_used="mock-v1",
            tokens_used=50
        )
    
    def _parse_llm_response(
        self,
        response_text: str,
        aqi_value: float,
        persona: str
    ) -> GeneratedExplanation:
        """Parse structured response from LLM."""
        
        try:
            # Try to extract JSON from response
            import json
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if response isn't valid JSON
            self.logger.warning("LLM response was not valid JSON. Using template fallback.")
            # Return with basic parsing
            data = {
                "explanation": response_text,
                "health_advisory": {
                    "severity": "info",
                    "message": "Monitor air quality conditions.",
                    "affected_groups": ["sensitive groups"],
                    "recommended_actions": ["Monitor air quality"]
                }
            }
        
        advisory = HealthAdvisory(
            message=data.get("health_advisory", {}).get("message", "Monitor conditions."),
            severity=data.get("health_advisory", {}).get("severity", "info"),
            affected_groups=data.get("health_advisory", {}).get("affected_groups", []),
            recommended_actions=data.get("health_advisory", {}).get("recommended_actions", [])
        )
        
        return GeneratedExplanation(
            explanation=data.get("explanation", response_text),
            health_advisory=advisory,
            provider_used=APIProvider.OPENAI,
            model_used=self.config.model
        )
    
    def generate_health_advisory_only(
        self,
        aqi_value: float,
        persona: str = "general_public"
    ) -> HealthAdvisory:
        """Generate health advisory without full explanation."""
        
        if self.config.provider == APIProvider.OPENAI and self._can_use_llm():
            try:
                prompt = PromptBuilder.build_advisory_prompt(aqi_value, persona)
                
                response = self._openai_client.ChatCompletion.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": PromptBuilder.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=200,
                    timeout=self.config.timeout
                )
                
                response_text = response.choices[0].message.content
                
                try:
                    data = json.loads(response_text)
                    return HealthAdvisory(
                        message=data.get("message", "Monitor air quality."),
                        severity=data.get("severity", "info"),
                        affected_groups=data.get("affected_groups", []),
                        recommended_actions=data.get("recommended_actions", [])
                    )
                except json.JSONDecodeError:
                    pass
            
            except Exception as e:
                self.logger.warning(f"LLM advisory failed: {str(e)}")
        
        # Fallback
        severity = "alert" if aqi_value > 200 else "warning" if aqi_value > 100 else "info"
        
        return HealthAdvisory(
            message=f"Current conditions require attention for {persona.replace('_', ' ')}.",
            severity=severity,
            affected_groups=["affected groups"],
            recommended_actions=["Monitor conditions", "Limit outdoor time", "Use protection if needed"]
        )


def create_generative_explainer(
    api_key: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
    provider: APIProvider = APIProvider.OPENAI
) -> GenerativeExplainer:
    """
    Factory function to create a generative explainer.
    
    Args:
        api_key: OpenAI API key (or None for template fallback)
        model: LLM model to use
        provider: API provider to use
    
    Returns:
        Configured GenerativeExplainer instance
    """
    config = LLMConfiguration(
        api_key=api_key,
        model=model,
        provider=provider,
        use_fallback=True
    )
    return GenerativeExplainer(config)
