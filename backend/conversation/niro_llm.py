"""
NIRO LLM Module
Stubbed implementation for the NIRO AI response generation.
Replace with actual LLM integration later.
"""

from typing import Dict, Any, List, Optional
import logging
import os

from .models import NiroReply, NiroLLMPayload

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
                logger.warning(f"Real LLM failed, using stub: {e}")
        
        # Stub implementation
        return self._generate_stub_response(mode, focus, user_question, astro_features)
    
    def _call_real_llm(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call actual LLM (Gemini or OpenAI)"""
        mode = payload.get('mode', 'GENERAL_GUIDANCE')
        focus = payload.get('focus')
        user_question = payload.get('user_question', '')
        astro_features = payload.get('astro_features', {})
        
        system_prompt = self._build_system_prompt(mode, focus)
        user_prompt = self._build_user_prompt(user_question, astro_features, mode, focus)
        
        # Try Gemini first
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
        
        # OpenAI fallback
        if self.openai_key:
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
    
    def _generate_stub_response(
        self,
        mode: str,
        focus: Optional[str],
        user_question: str,
        astro_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a stub response based on mode and focus.
        Used when real LLM is not available.
        """
        logger.warning("Using STUB LLM response - replace with real LLM")
        
        ascendant = astro_features.get('ascendant', 'Aries')
        moon_sign = astro_features.get('moon_sign', 'Cancer')
        mahadasha = astro_features.get('mahadasha', {}).get('lord', 'Jupiter')
        
        # Mode-specific responses
        if mode == 'BIRTH_COLLECTION':
            return {
                'rawText': 'I need your birth details to provide personalized insights.',
                'summary': 'To give you accurate astrological guidance, I need your birth details - date, time, and place of birth.',
                'reasons': [
                    'Birth time determines your Ascendant (Lagna), the foundation of your chart',
                    'Birth location is needed for precise planetary positions',
                    'Date of birth establishes your planetary placements'
                ],
                'remedies': []
            }
        
        if mode == 'PAST_THEMES':
            return {
                'rawText': f'Looking at your chart with {ascendant} Ascendant and {moon_sign} Moon...',
                'summary': f'With {ascendant} Ascendant and Moon in {moon_sign}, the past 2 years have been a period of significant transformation guided by your {mahadasha} Mahadasha.',
                'reasons': [
                    f'Saturn\'s transit through key houses has restructured your foundations',
                    f'Jupiter\'s blessings have brought growth opportunities in unexpected areas',
                    f'Your {mahadasha} Mahadasha has emphasized themes of {"expansion" if mahadasha == "Jupiter" else "discipline" if mahadasha == "Saturn" else "transformation"}'
                ],
                'remedies': [
                    'Acknowledge the growth you\'ve achieved during challenging periods',
                    'Journal about key events from 2023-2024 to identify patterns'
                ]
            }
        
        if mode == 'FOCUS_READING' and focus:
            focus_responses = {
                'career': {
                    'summary': f'Your {ascendant} Ascendant gives you natural leadership qualities. The 10th house lord\'s placement suggests a period of career consolidation and new opportunities.',
                    'reasons': [
                        'The 10th house of career shows favorable planetary influences',
                        f'{mahadasha} Mahadasha supports professional growth',
                        'Current transits indicate potential for advancement'
                    ],
                    'remedies': [
                        'Worship Sun on Sundays to strengthen career prospects',
                        'Wear Ruby or Manik after consultation for career boost',
                        'Network actively during Mercury hora for best results'
                    ]
                },
                'relationship': {
                    'summary': f'With {moon_sign} Moon, you seek emotional depth in relationships. The 7th house configuration suggests meaningful connections ahead.',
                    'reasons': [
                        'Venus placement indicates capacity for deep love',
                        '7th house lord is well-positioned for partnerships',
                        f'Current {mahadasha} period favors relationship growth'
                    ],
                    'remedies': [
                        'Worship Venus on Fridays for relationship harmony',
                        'Wear white or light colors on Fridays',
                        'Practice gratitude meditation for emotional balance'
                    ]
                },
                'health': {
                    'summary': f'Your {ascendant} Ascendant rules certain body parts. The 6th house analysis shows areas to focus on for optimal health.',
                    'reasons': [
                        'Ascendant lord position indicates overall vitality',
                        '6th house planets suggest specific health focus areas',
                        'Current transits require attention to routine'
                    ],
                    'remedies': [
                        'Practice yoga asanas suited to your constitution',
                        'Follow dietary recommendations for your Moon sign',
                        'Observe fasting on days ruled by malefic planets'
                    ]
                }
            }
            
            response = focus_responses.get(focus, focus_responses['career'])
            return {
                'rawText': response['summary'] + ' ' + ' '.join(response['reasons']),
                'summary': response['summary'],
                'reasons': response['reasons'],
                'remedies': response['remedies']
            }
        
        # Default GENERAL_GUIDANCE response
        return {
            'rawText': f'Based on your {ascendant} Ascendant chart...',
            'summary': f'With {ascendant} rising and Moon in {moon_sign}, you possess a unique combination of {"dynamic energy" if ascendant in ["Aries", "Leo", "Sagittarius"] else "grounded wisdom" if ascendant in ["Taurus", "Virgo", "Capricorn"] else "intellectual curiosity" if ascendant in ["Gemini", "Libra", "Aquarius"] else "emotional depth"}.',
            'reasons': [
                f'Your Ascendant lord\'s placement shapes your life path',
                f'{moon_sign} Moon provides emotional intelligence',
                f'{mahadasha} Mahadasha period guides current themes'
            ],
            'remedies': [
                'Honor your Ascendant lord through appropriate worship',
                'Follow Moon sign dietary and lifestyle guidelines',
                'Meditate during brahma muhurta for spiritual growth'
            ]
        }
