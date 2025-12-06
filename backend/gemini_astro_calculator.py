"""
Gemini-based Astrological Calculator
WARNING: LLMs are not designed for precise astronomical calculations.
This should be used for experimentation only, not production.
"""
import os
import logging
from typing import Dict, Any, Tuple
from gemini_agent import GeminiAgent

logger = logging.getLogger(__name__)

class GeminiAstroCalculator:
    """
    Uses Gemini LLM for astrological calculations
    WARNING: This is experimental and may not provide accurate results
    """
    
    def __init__(self):
        self.gemini_agent = GeminiAgent()
        logger.warning("GeminiAstroCalculator initialized. Note: LLMs are not suitable for precise astronomical calculations.")
    
    def calculate_houses_and_planets(
        self, 
        dob: str, 
        tob: str, 
        lat: float, 
        lon: float, 
        location: str,
        timezone: float = 5.5
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Calculate astrological houses and planetary positions using Gemini LLM
        
        Args:
            dob: Date of birth (DD-MM-YYYY)
            tob: Time of birth (HH:MM in 24h format)
            lat: Latitude
            lon: Longitude
            location: Location name
            timezone: Timezone offset
        
        Returns:
            Tuple of (success, data_dict, error_message)
        """
        
        # Convert DD-MM-YYYY to YYYY-MM-DD for better LLM understanding
        try:
            day, month, year = dob.split('-')
            iso_date = f"{year}-{month}-{day}"
        except:
            iso_date = dob
        
        prompt = f"""You are an expert Vedic astrologer with deep knowledge of astronomical calculations and house systems.

**TASK:** Calculate the complete Vedic astrological chart for the following birth details.

**BIRTH DETAILS:**
- Date of Birth: {iso_date} (YYYY-MM-DD format)
- Time of Birth: {tob} (24-hour format, local time)
- Place of Birth: {location}
- Latitude: {lat}°
- Longitude: {lon}°
- Timezone Offset: UTC+{timezone} hours

**REQUIREMENTS:**

1. **Calculate the 12 Houses (Bhavas):**
   - Use the Placidus or Whole Sign house system
   - Provide the starting degree (cusp) for each house in zodiac format (sign + degree)
   - Include both tropical and sidereal calculations (use Lahiri ayanamsa for sidereal)

2. **Calculate Planetary Positions:**
   - Determine positions for: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu (North Node), Ketu (South Node)
   - For each planet, provide:
     * Zodiac sign
     * Degree within sign (0-30°)
     * House placement (which house it occupies)
     * Whether it's retrograde (for applicable planets)
   - Use sidereal zodiac with Lahiri ayanamsa (~24° currently)

3. **Calculate Ascendant (Lagna):**
   - Rising sign at the time of birth
   - Exact degree of ascendant

4. **Additional Calculations:**
   - Nakshatra (lunar mansion) for the Moon
   - Tithi (lunar day)
   - Current dasha period (Vimshottari system)

**OUTPUT FORMAT:**
Provide your response as a valid JSON object with the following structure:

```json
{{
  "calculation_method": "Vedic Astrology with Lahiri Ayanamsa",
  "birth_info": {{
    "date": "{iso_date}",
    "time": "{tob}",
    "location": "{location}",
    "latitude": {lat},
    "longitude": {lon},
    "timezone": {timezone}
  }},
  "ascendant": {{
    "sign": "sign name",
    "degree": degree_value,
    "nakshatra": "nakshatra name"
  }},
  "houses": {{
    "house_1": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_2": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_3": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_4": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_5": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_6": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_7": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_8": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_9": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_10": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_11": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}},
    "house_12": {{"sign": "sign", "degree": degree, "cusp": "sign degree"}}
  }},
  "planets": {{
    "Sun": {{
      "sign": "sign name",
      "degree": degree_value,
      "house": house_number,
      "retrograde": false
    }},
    "Moon": {{
      "sign": "sign name",
      "degree": degree_value,
      "house": house_number,
      "retrograde": false,
      "nakshatra": "nakshatra name",
      "nakshatra_pada": pada_number
    }},
    "Mercury": {{"sign": "...", "degree": ..., "house": ..., "retrograde": true/false}},
    "Venus": {{"sign": "...", "degree": ..., "house": ..., "retrograde": true/false}},
    "Mars": {{"sign": "...", "degree": ..., "house": ..., "retrograde": true/false}},
    "Jupiter": {{"sign": "...", "degree": ..., "house": ..., "retrograde": true/false}},
    "Saturn": {{"sign": "...", "degree": ..., "house": ..., "retrograde": true/false}},
    "Rahu": {{"sign": "...", "degree": ..., "house": ...}},
    "Ketu": {{"sign": "...", "degree": ..., "house": ...}}
  }},
  "additional": {{
    "moon_tithi": "tithi name",
    "moon_tithi_number": tithi_number,
    "current_dasha": {{
      "mahadasha": "planet name",
      "antardasha": "planet name",
      "pratyantardasha": "planet name"
    }}
  }},
  "notes": "Any important observations or calculation notes"
}}
```

**IMPORTANT:**
- Return ONLY valid JSON, no markdown formatting, no code blocks
- Use precise degree values (e.g., 15.23, not just 15)
- For sidereal positions, subtract approximately 24° from tropical
- Show your astronomical reasoning if uncertain
- If you cannot calculate with astronomical precision, state this clearly in the notes

Begin calculation:"""

        try:
            logger.info("Requesting astrological calculations from Gemini LLM...")
            
            # Use Gemini Pro for calculations
            response = self.gemini_agent._call_model(
                self.gemini_agent.pro_model,
                prompt,
                temperature=0.1  # Low temperature for more consistent results
            )
            
            # Clean response
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            # Try to parse as JSON
            import json
            try:
                data = json.loads(response)
                logger.info("Successfully parsed Gemini LLM astrological calculations")
                
                # Add metadata
                data['calculation_source'] = 'Gemini LLM'
                data['warning'] = 'These calculations are generated by LLM and may not be astronomically accurate'
                
                return True, data, ""
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Response preview: {response[:500]}")
                
                # Return raw response as fallback
                return False, {
                    "raw_response": response,
                    "error": "LLM did not return valid JSON"
                }, "Failed to parse LLM response as JSON"
                
        except Exception as e:
            logger.error(f"Gemini astrological calculation failed: {str(e)}")
            return False, {}, str(e)
    
    def format_for_interpretation(self, gemini_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format Gemini calculation output to match VedicAstroAPI structure
        This ensures the interpretation prompts work with both sources
        """
        
        if not gemini_data or 'planets' not in gemini_data:
            return gemini_data
        
        # Create a structure similar to VedicAstroAPI response
        formatted = {
            "source": "Gemini LLM",
            "warning": gemini_data.get('warning', ''),
            "birth_details": gemini_data.get('birth_info', {}),
            "ascendant": gemini_data.get('ascendant', {}),
            "houses": gemini_data.get('houses', {}),
            "planets": gemini_data.get('planets', {}),
            "additional_info": gemini_data.get('additional', {}),
            "calculation_notes": gemini_data.get('notes', ''),
            "raw_data": gemini_data  # Keep original for reference
        }
        
        return formatted
