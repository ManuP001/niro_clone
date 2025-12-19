"""
NIRO LLM Module
Stubbed implementation for the NIRO AI response generation.
Replace with actual LLM integration later.
"""

from typing import Dict, Any, List, Optional
import logging
import os

from .models import NiroReply

logger = logging.getLogger(__name__)


class NiroLLM:
    """
    NIRO LLM Module for generating astrological interpretations.
    
    This is a STUB implementation that generates deterministic responses.
    Replace with actual Gemini/OpenAI integration.
    """
    
    def __init__(self):
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.use_real_llm = bool(self.gemini_key or self.openai_key)
        
        logger.info(f"NiroLLM initialized (real_llm={self.use_real_llm})")
    
    def call_niro_llm(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate NIRO response from the payload.
        
        STUB IMPLEMENTATION - Returns templated responses.
        Replace with actual LLM call.
        
        Args:
            payload: NiroLLMPayload dict with mode, focus, user_question, astro_features
            
        Returns:
            Dict with rawText, summary, reasons, remedies
        """
        mode = payload.get('mode', 'GENERAL_GUIDANCE')
        focus = payload.get('focus')
        user_question = payload.get('user_question', '')
        astro_features = payload.get('astro_features', {})
        
        logger.info(f"Generating NIRO response: mode={mode}, focus={focus}")
        
        # Try real LLM if available
        if self.use_real_llm:
            try:
                return self._call_real_llm(payload)
            except Exception as e:
                logger.error(f"Real LLM failed, no stub fallback available: {e}")
                raise RuntimeError(f"LLM unavailable and no stub fallback: {e}")
        
        # No real LLM available - raise error instead of using stub
        logger.error("No real LLM configured and stub fallback disabled")
        raise RuntimeError("No LLM available (neither OpenAI nor Gemini configured, stubs disabled)")
    
    def _call_real_llm(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call actual LLM (OpenAI primary, Gemini fallback)"""
        mode = payload.get('mode', 'GENERAL_GUIDANCE')
        focus = payload.get('focus')
        user_question = payload.get('user_question', '')
        astro_features = payload.get('astro_features', {})
        
        system_prompt = self._build_system_prompt(mode, focus)
        user_prompt = self._build_user_prompt(user_question, astro_features, mode, focus)
        
        # Try OpenAI first (primary)
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                return self._parse_llm_response(response.choices[0].message.content, mode, focus)
            except Exception as e:
                logger.warning(f"OpenAI failed: {e}")
        
        # Gemini fallback
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = model.generate_content(full_prompt)
                return self._parse_llm_response(response.text, mode, focus)
            except Exception as e:
                logger.warning(f"Gemini failed: {e}")
        
        raise Exception("No LLM available")
    
    def _build_system_prompt(self, mode: str, focus: Optional[str]) -> str:
        """Build system prompt for LLM"""
        return """You are NIRO, a wise and compassionate Vedic astrology guide.
You provide insights using traditional Jyotish wisdom in a warm, accessible way.

IMPORTANT: Structure your response in exactly this format:

SUMMARY:
[Write a 2-3 sentence overview of the main insight]

REASONS:
- [First astrological reason or influence]
- [Second astrological reason or influence]
- [Third astrological reason or influence]

REMEDIES:
- [First practical remedy or suggestion]
- [Second practical remedy or suggestion]

Keep your language warm and encouraging. Reference planets, houses, and nakshatras."""
    
    def _build_user_prompt(
        self,
        user_question: str,
        astro_features: Dict[str, Any],
        mode: str,
        focus: Optional[str]
    ) -> str:
        """Build user prompt with astro context"""
        prompt = f"""Mode: {mode}
Focus: {focus or 'general'}
User Question: {user_question}

Astrological Context:
- Ascendant: {astro_features.get('ascendant', 'N/A')}
- Moon Sign: {astro_features.get('moon_sign', 'N/A')}
- Current Mahadasha: {astro_features.get('mahadasha', {}).get('lord', 'N/A')}
- Current Antardasha: {astro_features.get('antardasha', {}).get('lord', 'N/A')}

Provide a structured Vedic astrology response."""
        return prompt
    
    def _parse_llm_response(
        self,
        response_text: str,
        mode: str,
        focus: Optional[str]
    ) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        summary = ""
        reasons = []
        remedies = []
        
        current_section = None
        
        for line in response_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            lower_line = line.lower()
            
            if 'summary' in lower_line and ':' in line:
                current_section = 'summary'
                after = line.split(':', 1)[1].strip()
                if after:
                    summary = after
                continue
            elif 'reason' in lower_line and ':' in line:
                current_section = 'reasons'
                continue
            elif 'remed' in lower_line and ':' in line:
                current_section = 'remedies'
                continue
            
            if current_section == 'summary':
                summary += ' ' + line if summary else line
            elif current_section == 'reasons':
                clean = line.lstrip('- •*0123456789.)').strip()
                if clean:
                    reasons.append(clean)
            elif current_section == 'remedies':
                clean = line.lstrip('- •*0123456789.)').strip()
                if clean:
                    remedies.append(clean)
            elif not current_section:
                summary += ' ' + line if summary else line
        
        if not summary:
            summary = response_text[:300]
        
        return {
            'rawText': response_text,
            'summary': summary.strip(),
            'reasons': reasons if reasons else ['Based on your planetary positions'],
            'remedies': remedies
        }
    