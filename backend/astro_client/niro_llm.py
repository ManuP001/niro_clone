"""
NIRO LLM Module

AI-powered response generation for NIRO Vedic Astrology chat.
Uses structured astro_features and answers user questions directly.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

NIRO_SYSTEM_PROMPT = '''You are NIRO — a concise, insightful Vedic astrologer.

Your purpose:
1. Answer ONLY the user's question directly and concisely
2. Use ONLY the astro_features provided as your astrological data source
3. If data is missing or inconclusive, state uncertainty instead of guessing
4. Never generate full reports unless explicitly asked
5. Use the topic/focus to scope your answer appropriately

MANDATORY RESPONSE STRUCTURE:

SUMMARY:
[2-3 concise lines directly answering the user's question]

REASONS:
- [Chart Factor] → [Effect] → [Interpretation]
- [Chart Factor] → [Effect] → [Interpretation]
(2-4 bullets maximum, using ONLY provided astro_features)

REMEDIES:
(Only include if chart shows clear challenge)
- [Simple remedy 1]
- [Simple remedy 2]

RULES:
- Use possibility language: "This phase tends to...", "You may experience..."
- Never claim certainty: avoid "This will happen"
- Stay warm, grounded, conversational
- Be extremely concise
- Focus on clarity and self-awareness'''


class NiroLLMModule:
    """NIRO LLM Module for generating astrological interpretations."""
    
    def __init__(self):
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.use_real_llm = bool(self.gemini_key or self.openai_key)
        self.system_prompt = NIRO_SYSTEM_PROMPT
        
        logger.info(f"NiroLLMModule initialized (real_llm={self.use_real_llm})")
    
    def call_niro_llm(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate NIRO response from the payload.
        
        Args:
            payload: Dict with mode, topic, user_question, astro_features
                
        Returns:
            Dict with rawText, summary, reasons, remedies
        """
        mode = payload.get('mode', 'GENERAL_GUIDANCE')
        topic = payload.get('topic', 'general')
        user_question = payload.get('user_question', '')
        astro_features = payload.get('astro_features', {})
        
        logger.info(f"Generating NIRO response: mode={mode}, topic={topic}, has_features={bool(astro_features)}")
        
        # Build user prompt
        user_prompt = self._build_user_prompt(mode, topic, user_question, astro_features)
        
        # Try real LLM
        if self.use_real_llm:
            try:
                return self._call_real_llm(user_prompt)
            except Exception as e:
                logger.warning(f"Real LLM failed: {e}")
        
        # Fallback stub
        return self._generate_stub_response(mode, topic, user_question, astro_features)
    
    def _build_user_prompt(self, mode: str, topic: str, user_question: str, astro_features: Dict[str, Any]) -> str:
        """Build the user prompt with all context for LLM."""
        
        # Format focus factors
        factors_str = ""
        for factor in astro_features.get('focus_factors', [])[:8]:
            if factor.get('type') == 'house':
                factors_str += f"\n  - House {factor.get('house')}: {factor.get('sign')} sign, Lord {factor.get('lord')}"
            elif factor.get('type') == 'planet':
                factors_str += f"\n  - {factor.get('planet')}: {factor.get('sign')} ({factor.get('house')}th house), {factor.get('dignity')}"
        
        # Format key rules
        rules_str = ""
        for rule in astro_features.get('key_rules', [])[:5]:
            rules_str += f"\n  - {rule.get('meaning')}"
        
        # Format transits
        transits_str = ""
        for transit in astro_features.get('transits', [])[:5]:
            transits_str += f"\n  - {transit.get('planet')} {transit.get('event_type')} affecting {transit.get('affected_house')}th house"
        
        prompt = f'''CONTEXT:
Mode: {mode}
Topic: {topic}

USER QUESTION:
{user_question}

ASTRO DATA:

Core Chart:
- Ascendant: {astro_features.get('ascendant', 'N/A')}
- Moon Sign: {astro_features.get('moon_sign', 'N/A')}
- Sun Sign: {astro_features.get('sun_sign', 'N/A')}

Current Dasha:
- Mahadasha: {astro_features.get('mahadasha', {}).get('planet', 'N/A')}
- Antardasha: {astro_features.get('antardasha', {}).get('planet', 'N/A')}

Topic-Specific Factors:{factors_str}

Key Rules:{rules_str}

Recent Transits:{transits_str}

INSTRUCTIONS:
- Answer ONLY the user_question above
- Use ONLY the astro data provided
- Follow the 3-part structure: SUMMARY, REASONS, REMEDIES
- Be concise and direct'''
        
        return prompt
    
    def _call_real_llm(self, user_prompt: str) -> Dict[str, Any]:
        """OpenAI primary, Gemini fallback."""
        
        # OpenAI first
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                return self._parse_llm_response(response.choices[0].message.content)
            except Exception as e:
                logger.warning(f"OpenAI failed: {e}")

        # Gemini fallback
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash')
                full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
                response = model.generate_content(full_prompt)
                return self._parse_llm_response(response.text)
            except Exception as e:
                logger.warning(f"Gemini failed: {e}")

        raise Exception("No LLM available")
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        summary = ""
        reasons = []
        remedies = []
        
        current_section = None
        lines = response_text.strip().split('\n')
        
        for line in lines:
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
                summary = summary + ' ' + line if summary else line
            elif current_section == 'reasons':
                clean = line.lstrip('- •*0123456789.)').strip()
                if clean and len(clean) > 10:
                    reasons.append(clean)
            elif current_section == 'remedies':
                clean = line.lstrip('- •*0123456789.)').strip()
                if clean and len(clean) > 10:
                    remedies.append(clean)
            elif not current_section and line:
                summary = summary + ' ' + line if summary else line
        
        if not summary:
            summary = response_text[:300]
        
        if not reasons:
            reasons = ["Based on your chart analysis"]
        
        return {
            'rawText': response_text,
            'summary': summary.strip(),
            'reasons': reasons[:4],
            'remedies': remedies[:2]
        }
    
    def _generate_stub_response(self, mode: str, topic: str, user_question: str, astro_features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate stub response when real LLM not available."""
        logger.warning("Using STUB LLM response")
        
        ascendant = astro_features.get('ascendant', 'Aries')
        moon_sign = astro_features.get('moon_sign', 'Cancer')
        mahadasha = astro_features.get('mahadasha', {}).get('planet', 'Jupiter')
        
        if mode == 'BIRTH_COLLECTION':
            return {
                'rawText': 'I need your birth details to provide personalized insights.',
                'summary': 'To give you accurate astrological guidance, I need your birth details — date, time, and place of birth.',
                'reasons': [
                    'Ascendant calculated from birth time → Foundation of your chart',
                    'Planetary positions from birth date → Shape your life themes'
                ],
                'remedies': []
            }
        
        summary = f"With {ascendant} Ascendant and {moon_sign} Moon, your {topic} area is influenced by {mahadasha} Mahadasha."
        
        return {
            'rawText': f"SUMMARY:\n{summary}\n\nREASONS:\n- {ascendant} Ascendant shapes your approach to {topic}\n- {moon_sign} Moon influences emotional patterns\n- Current {mahadasha} period brings specific themes",
            'summary': summary,
            'reasons': [
                f"{ascendant} Ascendant → Your natural approach → Shapes how you handle {topic}",
                f"{moon_sign} Moon → Emotional foundation → Influences your {topic} decisions",
                f"{mahadasha} Mahadasha → Current life phase → Brings focus to certain areas"
            ],
            'remedies': []
        }


# Singleton instance - lazy initialization
class _NiroLLMSingleton:
    _instance = None
    
    def __call__(self):
        if self._instance is None:
            self._instance = NiroLLMModule()
        return self._instance

_get_niro_llm = _NiroLLMSingleton()


def call_niro_llm(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to call NIRO LLM"""
    return _get_niro_llm().call_niro_llm(payload)
