"""
Chat Agent for AstroTrust
Handles conversational astrology using Gemini LLM
"""
import os
import json
import logging
from typing import Tuple, Dict, Any, Optional
from gemini_agent import GeminiAgent
from chat_models import (
    ExtractedData, SubjectData, PlaceData, ChatContext, 
    APITrigger, ConfidenceMetadata, RequestType
)

logger = logging.getLogger(__name__)

class AstroChatAgent:
    """
    Chat agent for conversational astrology
    Handles NLP extraction, validation, and interpretation
    """
    
    def __init__(self):
        self.gemini_agent = GeminiAgent()
        
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
        
        prompt = f"""You are an NLP extraction system for an astrology application. Extract birth details from user messages.

**CONVERSATION HISTORY:**
{context_str if context_str else "No previous context"}

**CURRENT USER MESSAGE:**
"{user_message}"

**YOUR TASK:**
Extract the following information if present:
1. Person's name
2. Date of birth (convert to YYYY-MM-DD format)
3. Time of birth (convert to HH:MM 24h format, or mark as "unknown")
4. Place of birth (city, region/state, country)
5. Request type (natal chart, marriage compatibility, relationship advice, panchang, synastry)
6. Partner details (if mentioned - same fields as above)
7. Whether user has given consent to process their data

**OUTPUT FORMAT:**
Return ONLY valid JSON with this structure:

{{
  "extraction_successful": true/false,
  "confidence_score": 0.0-1.0,
  "user": {{
    "name": "extracted name or null",
    "date_of_birth": "YYYY-MM-DD or null",
    "time_of_birth": "HH:MM or 'unknown' or null",
    "place_of_birth": {{
      "city": "city name or null",
      "region": "state/region or null",
      "country": "country or null"
    }}
  }},
  "context": {{
    "request_type": "natal|marriage|relationship|panchang|synastry",
    "partner": {{...}} (only if mentioned, otherwise null),
    "consent_given": true/false
  }},
  "missing_fields": ["list", "of", "missing", "required", "fields"],
  "ambiguous_fields": ["list", "of", "ambiguous", "fields"],
  "notes": "Any important notes about the extraction"
}}

**EXTRACTION RULES:**
- If date is in Indian format (DD-MM-YYYY or DD/MM/YYYY), convert to YYYY-MM-DD
- If time is in 12h format, convert to 24h
- If place is mentioned as "Delhi", "Mumbai" etc, fill city and country as "India"
- Mark time as "unknown" if user says "don't know", "not sure", "morning/evening" etc
- Confidence 1.0 = all required fields present and clear
- Confidence 0.7-0.9 = most fields present, some ambiguity
- Confidence <0.7 = significant missing data

Return ONLY the JSON, no other text."""

        try:
            response = self.gemini_agent._call_model(
                self.gemini_agent.flash_model,  # Use Flash for faster extraction
                prompt,
                temperature=0.1  # Low temperature for consistent extraction
            )
            
            # Clean response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            extracted_json = json.loads(response)
            
            # Convert to ExtractedData model
            extracted_data = self._json_to_extracted_data(extracted_json)
            
            logger.info(f"Extraction successful: confidence={extracted_data.confidence_score}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
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
        
        # Extract user data
        if data.get('user') and data['user'].get('name'):
            place_data = data['user'].get('place_of_birth', {})
            if place_data and place_data.get('city') and place_data.get('country'):
                extracted.user = SubjectData(
                    name=data['user']['name'],
                    date_of_birth=data['user'].get('date_of_birth', ''),
                    time_of_birth=data['user'].get('time_of_birth'),
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
        
        prompt = f"""You are an expert Vedic astrologer providing probabilistic interpretations.

**USER REQUEST:** {request_type} chart analysis

**EXTRACTED BIRTH DATA:**
{json.dumps(extracted_data.model_dump() if hasattr(extracted_data, 'model_dump') else {}, indent=2)}

**ASTROLOGICAL DATA FROM API:**
```json
{json.dumps(api_response, indent=2)}
```

**YOUR TASK:**
Provide a conversational, human-friendly interpretation that includes:

1. **Main Interpretation** (2-3 paragraphs)
   - Explain key findings in simple language
   - Focus on most significant astrological factors
   - Be warm and empathetic

2. **Confidence Assessment**
   - Overall confidence score (0-1)
   - List assumptions made (e.g., "Assuming birth time is accurate...")
   - Data quality notes (e.g., "Without exact birth time, ascendant is approximate")

3. **Alternate Readings** (if applicable)
   - If birth time is unknown or approximate, provide 2-3 alternate scenarios
   - Rank by likelihood

**OUTPUT FORMAT:**
```json
{{
  "interpretation": "Your warm, conversational interpretation here...",
  "confidence_metadata": {{
    "overall_confidence": 0.85,
    "assumptions": [
      "Birth time is accurate",
      "Using Lahiri ayanamsa"
    ],
    "alternate_readings": [
      {{
        "scenario": "If born 1 hour earlier",
        "likelihood": 0.15,
        "key_difference": "Ascendant would be..."
      }}
    ],
    "data_quality_notes": [
      "Exact birth time available - high precision possible"
    ]
  }}
}}
```

**TONE:**
- Conversational and warm
- Avoid jargon, explain concepts simply
- Be probabilistic, not absolute ("likely", "suggests", "indicates")
- Empowering, not fear-inducing

Return ONLY the JSON."""

        try:
            response = self.gemini_agent._call_model(
                self.gemini_agent.pro_model,  # Use Pro for quality interpretation
                prompt,
                temperature=0.7
            )
            
            # Clean and parse
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            
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
            logger.error(f"Interpretation failed: {str(e)}")
            
            # Fallback interpretation
            interpretation = "I've analyzed your birth chart. The planetary positions suggest unique patterns in your life path. For a more detailed analysis, please ensure all birth details are accurate."
            
            confidence_metadata = ConfidenceMetadata(
                overall_confidence=0.5,
                assumptions=["Limited data available"],
                data_quality_notes=["Unable to generate detailed interpretation"]
            )
            
            return interpretation, confidence_metadata
