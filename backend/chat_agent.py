"""
Chat Agent for AstroTrust
Handles conversational astrology with multi-provider support
Uses Gemini (low-cost) first, falls back to OpenAI when needed
"""
import os
import json
import logging
from typing import Tuple, Dict, Any, Optional
from gemini_agent import GeminiAgent
from openai_agent import OpenAIAgent
from provider_router import ProviderRouter, Provider
from chat_models import (
    ExtractedData, SubjectData, PlaceData, ChatContext, 
    APITrigger, ConfidenceMetadata, RequestType
)

logger = logging.getLogger(__name__)

class AstroChatAgent:
    """
    Chat agent for conversational astrology
    Handles NLP extraction, validation, and interpretation
    Uses provider router for intelligent fallback
    """
    
    def __init__(self):
        self.gemini_agent = GeminiAgent()
        self.openai_agent = OpenAIAgent()
        self.router = ProviderRouter(self.gemini_agent, self.openai_agent)
        
    def extract_birth_details(self, user_message: str, conversation_history: list = None) -> ExtractedData:
        """
        Extract birth details from user message using NLP
        
        Args:
            user_message: Raw user input
            conversation_history: Previous messages for context
        
        Returns:
            ExtractedData with extracted fields and confidence
        """
        
        # Build context from conversation history
        context_str = ""
        if conversation_history:
            context_str = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
        
        prompt = f"""Extract birth details from user message. Be VERY lenient and extract even partial information.

**PREVIOUS MESSAGES:**
{context_str if context_str else "None"}

**CURRENT MESSAGE:**
"{user_message}"

**EXTRACT:**
1. Name (first word/name in message)
2. Date of birth (DD-MM-YYYY, DD/MM/YYYY, any date format → YYYY-MM-DD)
3. Time (12h or 24h → HH:MM format, e.g., "10:47am" → "10:47")
4. Place (any city name → extract city name, assume India if not specified)

**IMPORTANT EXTRACTION TIPS:**
- "Manu Pant, 10-10-1985, 10:47am, Dehradun" → name: Manu Pant, dob: 1985-10-10, time: 10:47, city: Dehradun
- If date format is DD-MM-YYYY, convert to YYYY-MM-DD
- If time has "am/pm", convert to 24h (10:47am → 10:47, 2:30pm → 14:30)
- For Indian cities (Delhi, Mumbai, Bangalore, Dehradun, etc.), set country as "India"
- Extract name even if it's just 2 words at the start
- ALWAYS set consent_given to true if any birth details are shared
- Set confidence_score to 0.9 if name, date, time, and place are all present
- Only mark fields as "missing" if they are truly absent from the message

**RETURN JSON ONLY:**
{{
  "extraction_successful": true,
  "confidence_score": 0.9,
  "user": {{
    "name": "extracted name",
    "date_of_birth": "YYYY-MM-DD",
    "time_of_birth": "HH:MM",
    "place_of_birth": {{
      "city": "city name",
      "region": null,
      "country": "India"
    }}
  }},
  "context": {{
    "request_type": "natal",
    "partner": null,
    "consent_given": true
  }},
  "missing_fields": [],
  "ambiguous_fields": [],
  "notes": ""
}}

Return ONLY the JSON, no markdown, no other text."""

        try:
            # Use router to call with automatic fallback
            extracted_json, provider_used = self.router.extract_json(prompt)
            logger.info(f"Extraction used provider: {provider_used.value}")
            
            # Convert to ExtractedData model
            extracted_data = self._json_to_extracted_data(extracted_json)
            
            logger.info(f"Extraction successful: confidence={extracted_data.confidence_score}, provider={provider_used.value}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Extraction failed with all providers: {str(e)}", exc_info=True)
            # Return empty extraction
            return ExtractedData(
                confidence_score=0.0,
                missing_fields=["all"],
                ambiguous_fields=[]
            )
    
    def _json_to_extracted_data(self, data: dict) -> ExtractedData:
        """Convert JSON extraction to ExtractedData model"""
        
        extracted = ExtractedData(
            confidence_score=data.get('confidence_score', 0.0),
            missing_fields=data.get('missing_fields', []),
            ambiguous_fields=data.get('ambiguous_fields', [])
        )
        
        # Extract user data - be more lenient
        if data.get('user'):
            user_data = data['user']
            if user_data.get('name'):
                place_data = user_data.get('place_of_birth', {})
                # Accept place data even if country is missing (we'll infer it)
                if place_data and place_data.get('city'):
                    # If no country specified, assume India for common Indian cities
                    if not place_data.get('country'):
                        indian_cities = ['delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 
                                       'hyderabad', 'pune', 'ahmedabad', 'jaipur', 'dehradun',
                                       'lucknow', 'kanpur', 'nagpur', 'indore', 'bhopal']
                        if place_data['city'].lower() in indian_cities:
                            place_data['country'] = 'India'
                    
                    extracted.user = SubjectData(
                        name=user_data['name'],
                        date_of_birth=user_data.get('date_of_birth', ''),
                        time_of_birth=user_data.get('time_of_birth'),
                        place_of_birth=PlaceData(**place_data)
                    )
        
        # Extract context
        context_data = data.get('context', {})
        extracted.context = ChatContext(
            request_type=RequestType(context_data.get('request_type', 'natal')),
            consent_given=context_data.get('consent_given', False)
        )
        
        return extracted
    
    def generate_followup_question(self, extracted_data: ExtractedData) -> str:
        """Generate a concise follow-up question for missing data"""
        
        missing = extracted_data.missing_fields
        
        if not missing:
            return ""
        
        # Prioritize questions
        if 'name' in missing or 'date_of_birth' in missing:
            return "To generate your astrology chart, I need your **name** and **date of birth** (e.g., 15 August 1990). Could you please provide these?"
        
        if 'time_of_birth' in missing:
            return "Do you know your **time of birth** (e.g., 2:30 PM)? If not, I can still provide insights but they'll be less precise."
        
        if 'place_of_birth' in missing or 'city' in missing:
            return "Which **city** were you born in? This helps determine accurate planetary positions."
        
        # For ambiguous fields
        if extracted_data.ambiguous_fields:
            return f"I need clarification on: {', '.join(extracted_data.ambiguous_fields)}. Could you provide more details?"
        
        return "Could you provide a bit more information to complete your chart?"
    
    def generate_interpretation(
        self, 
        api_response: Dict[str, Any], 
        extracted_data: ExtractedData,
        request_type: str = "natal"
    ) -> Tuple[str, ConfidenceMetadata]:
        """
        Generate probabilistic interpretation from API response
        
        Returns:
            Tuple of (interpretation_text, confidence_metadata)
        """
        
        prompt = f"""Provide a brief astrological interpretation based on birth chart data.

**Birth Info:** {extracted_data.user.name if extracted_data.user else 'User'}, {extracted_data.user.date_of_birth if extracted_data.user else ''}, {extracted_data.user.place_of_birth.city if extracted_data.user and extracted_data.user.place_of_birth else ''}

**Chart Data:**
{json.dumps(api_response, indent=2)[:1000]}

**Task:** Write 2-3 paragraphs covering key insights about career, relationships, and personality based on the planetary positions. Be warm, conversational, and focus on practical guidance.

**Return JSON:**
{{
  "interpretation": "Your brief, friendly interpretation (2-3 paragraphs)...",
  "confidence_metadata": {{
    "overall_confidence": 0.85,
    "assumptions": ["Birth time accurate", "Using Lahiri ayanamsa"],
    "alternate_readings": [],
    "data_quality_notes": ["Data quality good"]
  }}
}}

Keep it concise for fast response. JSON only, no markdown."""

        try:
            # Use router for interpretation with automatic fallback
            result, provider_used = self.router.extract_json(prompt)
            logger.info(f"Interpretation used provider: {provider_used.value}")
            
            interpretation = result.get('interpretation', '')
            metadata_dict = result.get('confidence_metadata', {})
            
            confidence_metadata = ConfidenceMetadata(
                overall_confidence=metadata_dict.get('overall_confidence', 0.7),
                assumptions=metadata_dict.get('assumptions', []),
                alternate_readings=metadata_dict.get('alternate_readings', []),
                data_quality_notes=metadata_dict.get('data_quality_notes', [])
            )
            
            return interpretation, confidence_metadata
            
        except Exception as e:
            logger.error(f"Interpretation failed with all providers: {str(e)}")
            
            # Fallback interpretation
            interpretation = "I've analyzed your birth chart. The planetary positions suggest unique patterns in your life path. For a more detailed analysis, please ensure all birth details are accurate."
            
            confidence_metadata = ConfidenceMetadata(
                overall_confidence=0.5,
                assumptions=["Limited data available"],
                data_quality_notes=["Unable to generate detailed interpretation"]
            )
            
            return interpretation, confidence_metadata
