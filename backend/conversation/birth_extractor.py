"""Hybrid Birth Details Extractor
Credit-optimized: Regex first, LLM fallback only if needed
"""

import os
import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from .models import BirthDetails as ConvBirthDetails

logger = logging.getLogger(__name__)

# Model constant - using gpt-4-turbo for structured extraction (temperature=0)
EXTRACTION_MODEL_NAME = "gpt-4-turbo"


class HybridBirthDetailsExtractor:
    """
    Credit-optimized birth details extraction.
    Tries regex first, calls LLM only if necessary.
    """
    
    def __init__(self):
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        logger.info(f"HybridBirthDetailsExtractor initialized (llm_available={bool(self.openai_key)})")
    
    def extract(self, text: str) -> Optional[ConvBirthDetails]:
        """
        Extract birth details from text.
        Tries regex first, LLM fallback only if needed.
        """
        # Step 1: Try regex
        regex_result = self._extract_rule_based(text)
        logger.debug("BIRTH_EXTRACTION_REGEX_RESULT: %s", regex_result or "None")
        
        # If regex finds ALL 3 fields (DOB, TOB, location), return immediately without LLM
        if regex_result:
            dob = regex_result.get('dob')
            tob = regex_result.get('tob')
            location = regex_result.get('location')
            
            if dob and tob and location:
                confidence = regex_result.get('confidence', 0.0)
                logger.info(f"✅ Regex extracted all fields (confidence={confidence:.2f}) - skipping LLM")
                return ConvBirthDetails(
                    dob=dob,
                    tob=tob,
                    location=location,
                    timezone=regex_result.get('timezone', 5.5)
                )
        
        # Step 2: LLM fallback (only if OpenAI key exists and any field is missing)
        if self.openai_key:
            logger.info("⚠️ Regex incomplete - attempting LLM extraction fallback")
            llm_result = self._extract_with_llm(text)
            logger.debug("BIRTH_EXTRACTION_LLM_RESULT: %s", llm_result or "None")
            if llm_result:
                return llm_result
        
        logger.info("❌ Birth details extraction failed")
        return None
    
    def _extract_rule_based(self, text: str) -> Optional[Dict[str, Any]]:
        """Regex-based extraction."""
        dob = None
        tob = None
        location = None
        confidence = 0.0
        
        # Date patterns
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',       # DD.MM.YYYY
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})',  # DD MMM YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    if groups[1] in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                        # Month name format
                        month_map = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                                   'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
                        day = groups[0].zfill(2)
                        month = month_map.get(groups[1][:3], '01')
                        year = groups[2]
                        dob = f"{year}-{month}-{day}"
                    else:
                        # Numeric format
                        day = groups[0].zfill(2)
                        month = groups[1].zfill(2)
                        year = groups[2]
                        dob = f"{year}-{month}-{day}"
                    confidence += 0.4
                    break
        
        # Time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'(\d{1,2})\s*(am|pm)',
            r'(\d{1,2})\.(\d{2})',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                hour = int(groups[0])
                minute = int(groups[1]) if len(groups) > 1 and groups[1] and groups[1].isdigit() else 0
                meridiem = groups[-1].lower() if len(groups) > 0 and groups[-1] and groups[-1].lower() in ['am', 'pm'] else None
                
                if meridiem == 'pm' and hour != 12:
                    hour += 12
                elif meridiem == 'am' and hour == 12:
                    hour = 0
                
                tob = f"{hour:02d}:{minute:02d}"
                confidence += 0.3
                break
        
        # Location patterns
        location_patterns = [
            r'(?:in|at|from)\s+([A-Z][a-zA-Z\s,]+?)(?:\s|$|\.)',
            r'(?:born\s+in)\s+([A-Z][a-zA-Z\s,]+?)(?:\s|$|\.)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip().rstrip(',.')
                if len(location) > 2:
                    confidence += 0.3
                    break
        
        if dob or tob or location:
            return {
                'dob': dob,
                'tob': tob,
                'location': location,
                'timezone': 5.5,
                'confidence': confidence
            }
        
        return None
    
    def _extract_with_llm(self, text: str) -> Optional[ConvBirthDetails]:
        """LLM-based extraction fallback."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            response = client.chat.completions.create(
                model=EXTRACTION_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "Extract birth details ONLY. Return STRICT JSON."},
                    {"role": "user", "content": text}
                ],
                temperature=0,
                max_tokens=120
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            import json
            data = json.loads(content)
            
            dob = data.get('dob')
            tob = data.get('tob')
            location = data.get('location')
            
            if dob and tob and location:
                logger.info("LLM extraction successful")
                return ConvBirthDetails(
                    dob=dob,
                    tob=tob,
                    location=location,
                    timezone=data.get('timezone', 5.5)
                )
            
        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}")
        
        return None
