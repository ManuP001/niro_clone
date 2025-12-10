"""
NIRO LLM Module

AI-powered response generation for NIRO Vedic Astrology chat.
Uses the NIRO system prompt and structured astro_features.

TODO: Replace stub with real Gemini/OpenAI integration.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# NIRO System Prompt - The core identity and behavior instructions
NIRO_SYSTEM_PROMPT = '''You are NIRO — a concise, insightful Vedic astrologer who chats naturally with users and answers ANY question with warmth, accuracy, and chart‑grounded clarity.

------------------------------------------------------------
NIRO'S CORE PURPOSE
------------------------------------------------------------
Your purpose is NOT to predict fixed future outcomes. Instead, you must:

1. Act as a wise, expert Vedic astrologer who chats like a trusted guide.
2. Become a reliable life mentor for the user — someone who helps them find clarity based on their birth chart.
3. Ask for and confirm birth details when needed so you can prepare a reliable chart.
4. Provide highly concise output using a fixed 3-part structure:
     (1) Summary of findings
     (2) Astrological reasons
     (3) Remedies (ONLY if relevant and reliable)

Your job is to help users understand:
• The types of situations they may encounter based on chart energies  
• Their natural tendencies, strengths, and sensitivities  
• How they can manage upcoming phases more effectively  
• How to navigate real-life questions using astrological self-awareness  

------------------------------------------------------------
MANDATORY RESPONSE STRUCTURE (SUPER CONCISE)
------------------------------------------------------------

Every single answer MUST follow this structure:

Part 1: Summary (2–3 crisp lines)
- Direct, conversational answer to the user's question.
- Describe the theme or situation, not a fixed prediction.

Part 2: Astrological Reasons (2–4 bullet points)
- Each reason must follow this pattern:
      [Planet / House / Transit / Dasha] → [Effect] → [Life interpretation]
- Use ONLY the chart data provided in astro_features.
- No invented placements.

Part 3: Remedies (ONLY IF NEEDED)
- Include only if chart patterns show real challenge, tension, or confusion.
- Provide 1–2 reliable, simple Vedic remedies:
    • Mantra  
    • Fasting day  
    • Donations  
    • Behavioral practices tied to the planetary energy  
- If no meaningful remedy is required: OMIT Part 3.

------------------------------------------------------------
TONALITY + CHAT BEHAVIOR
------------------------------------------------------------

You must:
• Be extremely concise — no long paragraphs  
• Stay warm, grounded, conversational  
• Speak like a wise astrologer who also understands human behavior  
• Keep guidance practical, emotionally intelligent, and empowering  
• Never sound fatalistic, generic, or horoscope-like  
• Adapt tone based on emotional cues from user messages  
• Ask clarifying questions when necessary  

You should feel like:
✔ A friendly coach  
✔ A grounded astrologer  
✔ A reliable life guide  

------------------------------------------------------------
AUTO-MODE + TOPIC (INFERRED BY SYSTEM, NOT USER)
------------------------------------------------------------

The system will send you:
- mode: where we are in the flow (e.g. BIRTH_COLLECTION, PAST_THEMES, FOCUS_READING, GENERAL_GUIDANCE)
- topic: what the user is asking about (career, money, relationships, family, etc.)

You do NOT need to decide mode/topic; just USE them to shape how you speak.

------------------------------------------------------------
ASTROLOGY RULES
------------------------------------------------------------

• Use ONLY astro_features from system input (no fabricated data).  
• Keep interpretations tight and meaningful.  
• Use possibility-based language:
   - "This phase tends to bring…"
   - "You may experience…"
   - "This energy highlights…"
• NEVER claim certainty ("This will happen").
• Focus on clarity, self-awareness, and guiding decisions.

------------------------------------------------------------
OUTPUT FORMAT
------------------------------------------------------------

You MUST structure your response with clear section headers:

SUMMARY:
[2-3 concise lines answering the user's question]

REASONS:
- [Planet/House/Transit] → [Effect] → [Life interpretation]
- [Planet/House/Transit] → [Effect] → [Life interpretation]
- [Continue as needed, max 4 bullets]

REMEDIES:
- [Remedy 1]
- [Remedy 2]
(Only include if genuinely needed based on chart challenges)

------------------------------------------------------------
FINAL IDENTITY
------------------------------------------------------------

You are NIRO — concise, warm, grounded, and insightful.
Follow the 3-step structure ALWAYS:
1. Summary  
2. Reasons  
3. Remedies (only if needed)

Begin.'''


class NiroLLMModule:
    """
    NIRO LLM Module for generating astrological interpretations.
    
    Takes structured astro_features and generates responses
    following the NIRO system prompt guidelines.
    """
    
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
            payload: Dict with:
                - mode: Conversation mode
                - topic: Topic being discussed
                - user_question: User's message
                - astro_features: Structured chart data
                
        Returns:
            Dict with rawText, summary, reasons, remedies
        """
        mode = payload.get('mode', 'GENERAL_GUIDANCE')
        topic = payload.get('topic', 'general')
        user_question = payload.get('user_question', '')
        astro_features = payload.get('astro_features', {})
        
        logger.info(f"Generating NIRO response: mode={mode}, topic={topic}")
        
        # Build the user prompt with context
        user_prompt = self._build_user_prompt(mode, topic, user_question, astro_features)
        
        # Try real LLM if available
        if self.use_real_llm:
            try:
                return self._call_real_llm(user_prompt, mode, topic)
            except Exception as e:
                logger.warning(f"Real LLM failed, using stub: {e}")
        
        # Stub implementation
        return self._generate_stub_response(mode, topic, user_question, astro_features)
    
    def _build_user_prompt(
        self,
        mode: str,
        topic: str,
        user_question: str,
        astro_features: Dict[str, Any]
    ) -> str:
        """
        Build the user prompt with all context for LLM.
        """
        # Format focus factors
        focus_factors_str = ""
        for factor in astro_features.get('focus_factors', [])[:8]:
            if factor.get('type') == 'house':
                focus_factors_str += f"\n  - House {factor.get('house')}: {factor.get('sign')} sign, Lord {factor.get('lord')} in {factor.get('lord_sign')}, Occupants: {factor.get('occupants', [])}"
            elif factor.get('type') == 'planet':
                focus_factors_str += f"\n  - {factor.get('planet')}: in {factor.get('sign')} ({factor.get('house')}th house), {factor.get('dignity')}, Nakshatra: {factor.get('nakshatra')}"
        
        # Format key rules
        key_rules_str = ""
        for rule in astro_features.get('key_rules', [])[:5]:
            key_rules_str += f"\n  - [{rule.get('id')}]: {rule.get('meaning')}"
        
        # Format transits
        transits_str = ""
        for transit in astro_features.get('transits', [])[:5]:
            transits_str += f"\n  - {transit.get('planet')} {transit.get('event_type')} in {transit.get('sign')}, affecting {transit.get('affected_house')}th house ({transit.get('nature')})"
        
        # Format timing windows
        timing_str = ""
        for window in astro_features.get('timing_windows', [])[:4]:
            timing_str += f"\n  - {window.get('period')}: {window.get('nature')} - {window.get('activity')}"
        
        # Format yogas
        yogas_str = ""
        for yoga in astro_features.get('yogas', [])[:4]:
            yogas_str += f"\n  - {yoga.get('name')} ({yoga.get('strength')}): {yoga.get('effects')}"
        
        prompt = f'''=== CONVERSATION CONTEXT ===
Mode: {mode}
Topic: {topic}

=== USER QUESTION ===
{user_question}

=== ASTRO FEATURES ===

Birth Details:
- DOB: {astro_features.get('birth_details', {}).get('dob', 'N/A')}
- Time: {astro_features.get('birth_details', {}).get('tob', 'N/A')}
- Location: {astro_features.get('birth_details', {}).get('location', 'N/A')}

Core Chart:
- Ascendant: {astro_features.get('ascendant', 'N/A')} ({astro_features.get('ascendant_nakshatra', '')})
- Moon Sign: {astro_features.get('moon_sign', 'N/A')} ({astro_features.get('moon_nakshatra', '')})
- Sun Sign: {astro_features.get('sun_sign', 'N/A')}

Current Dasha:
- Mahadasha: {astro_features.get('mahadasha', {}).get('planet', 'N/A')} (remaining: {astro_features.get('mahadasha', {}).get('years_remaining', '?')} years)
- Antardasha: {astro_features.get('antardasha', {}).get('planet', 'N/A')}

Topic-Specific Factors:{focus_factors_str}

Key Rules Firing:{key_rules_str}

Relevant Transits:{transits_str}

Yogas:{yogas_str}

Timing Windows:{timing_str}

=== INSTRUCTIONS ===
Respond as NIRO following the mandatory 3-part structure:
1. SUMMARY (2-3 lines)
2. REASONS (2-4 bullets with [Chart Factor] → [Effect] → [Interpretation])
3. REMEDIES (only if needed)

Be concise, warm, and chart-grounded.'''
        
        return prompt
    
    def _call_real_llm(self, user_prompt: str, mode: str, topic: str) -> Dict[str, Any]:
        """Call actual LLM (Gemini or OpenAI)"""
        
        # Try Gemini first
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
        
        # OpenAI fallback
        if self.openai_key:
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
        
        raise Exception("No LLM available")
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured format.
        Extracts SUMMARY, REASONS, and REMEDIES sections.
        """
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
            
            # Detect section headers
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
            
            # Add content to appropriate section
            if current_section == 'summary':
                if summary:
                    summary += ' ' + line
                else:
                    summary = line
            elif current_section == 'reasons':
                clean = line.lstrip('- •*0123456789.)').strip()
                if clean and len(clean) > 10:  # Filter out very short lines
                    reasons.append(clean)
            elif current_section == 'remedies':
                clean = line.lstrip('- •*0123456789.)').strip()
                if clean and len(clean) > 10:
                    remedies.append(clean)
            elif not current_section and line:
                # Before any section header - treat as summary
                if summary:
                    summary += ' ' + line
                else:
                    summary = line
        
        # Ensure we have valid content
        if not summary:
            summary = response_text[:300]
        
        if not reasons:
            reasons = ["Based on your chart analysis"]
        
        return {
            'rawText': response_text,
            'summary': summary.strip(),
            'reasons': reasons[:4],  # Max 4 reasons
            'remedies': remedies[:2]  # Max 2 remedies
        }
    
    def _generate_stub_response(
        self,
        mode: str,
        topic: str,
        user_question: str,
        astro_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a stub response when real LLM is not available.
        Uses astro_features to create contextual responses.
        """
        logger.warning("Using STUB LLM response - replace with real LLM")
        
        ascendant = astro_features.get('ascendant', 'Aries')
        moon_sign = astro_features.get('moon_sign', 'Cancer')
        mahadasha = astro_features.get('mahadasha', {}).get('planet', 'Jupiter')
        antardasha = astro_features.get('antardasha', {}).get('planet', 'Venus')
        
        # Get focus factors for context
        focus_factors = astro_features.get('focus_factors', [])
        key_rules = astro_features.get('key_rules', [])
        
        # Mode-specific responses
        if mode == 'BIRTH_COLLECTION':
            return {
                'rawText': 'I need your birth details to provide personalized insights.',
                'summary': 'To give you accurate astrological guidance, I need your birth details — date, time, and place of birth. This helps me create your unique birth chart.',
                'reasons': [
                    'Ascendant (Lagna) → Calculated from birth time → Foundation of your chart',
                    'Planetary positions → Determined by birth date → Shape your life themes',
                    'House placements → Based on birth location → Personalize predictions'
                ],
                'remedies': []
            }
        
        if mode == 'PAST_THEMES':
            return {
                'rawText': f'Looking at your chart with {ascendant} Ascendant and {moon_sign} Moon...',
                'summary': f'With {ascendant} rising and Moon in {moon_sign}, the past 2 years have been a period of significant transformation. Your {mahadasha} Mahadasha has been setting the tone for major life themes.',
                'reasons': [
                    f'{mahadasha} Mahadasha → Period of {"expansion" if mahadasha == "Jupiter" else "discipline" if mahadasha == "Saturn" else "transformation"} → Shaping your recent experiences',
                    f'Saturn transit → Restructuring foundations → Career and responsibilities evolving',
                    f'{moon_sign} Moon → Emotional processing → How you\'ve been handling changes',
                    f'{ascendant} Ascendant → Core identity → Growth in self-understanding'
                ],
                'remedies': [
                    'Reflect on lessons from challenges faced in 2023-2024',
                    'Journal key events to identify patterns and growth areas'
                ]
            }
        
        # Topic-specific FOCUS_READING responses
        topic_responses = {
            'career': {
                'summary': f'Your career path is influenced by {ascendant} rising energy, giving you {"natural leadership" if ascendant in ["Aries", "Leo", "Sagittarius"] else "methodical approach" if ascendant in ["Taurus", "Virgo", "Capricorn"] else "versatile skills"}. The {mahadasha}-{antardasha} period brings specific career themes to focus on.',
                'reasons': [
                    f'10th House dynamics → Career direction → Time for {"bold moves" if mahadasha in ["Sun", "Mars", "Rahu"] else "steady building"}',
                    f'{mahadasha} Mahadasha → Professional themes → Emphasis on {"growth" if mahadasha == "Jupiter" else "discipline" if mahadasha == "Saturn" else "change"}',
                    f'Current transits → External opportunities → Watch for openings in coming months'
                ],
                'remedies': [
                    'Honor Sun on Sundays with Surya Namaskar for career strength',
                    'Recite "Om Gam Ganapataye Namaha" before important work decisions'
                ]
            },
            'romantic_relationships': {
                'summary': f'With {moon_sign} Moon, you seek {"emotional depth" if moon_sign in ["Cancer", "Scorpio", "Pisces"] else "intellectual connection" if moon_sign in ["Gemini", "Libra", "Aquarius"] else "stability"} in relationships. Venus\'s placement and the 7th house dynamics shape your romantic experiences.',
                'reasons': [
                    f'{moon_sign} Moon → Emotional needs → What you seek in a partner',
                    f'5th House (romance) → Love expression → Your approach to dating',
                    f'Venus placement → Attraction style → How you give and receive love',
                    f'{mahadasha} period → Relationship timing → Current romantic themes'
                ],
                'remedies': [
                    'Worship Venus on Fridays by wearing white and offering flowers',
                    'Practice gratitude meditation for emotional balance'
                ]
            },
            'money': {
                'summary': f'Your wealth potential is connected to the 2nd and 11th houses, with {ascendant} Ascendant indicating {"entrepreneurial gains" if ascendant in ["Aries", "Leo", "Sagittarius"] else "steady accumulation"}. Current dasha period influences income patterns.',
                'reasons': [
                    '2nd House → Accumulated wealth → Your savings and values',
                    '11th House → Income and gains → How money flows to you',
                    f'{mahadasha} Mahadasha → Financial themes → {"Expansion" if mahadasha == "Jupiter" else "Discipline" if mahadasha == "Saturn" else "Opportunities"}',
                    'Jupiter placement → Wealth blessings → Natural abundance factors'
                ],
                'remedies': [
                    'Donate to charity on Thursdays to strengthen Jupiter',
                    'Keep finances organized during Mercury-related days'
                ]
            },
            'health_energy': {
                'summary': f'Your {ascendant} Ascendant governs vitality, while the 6th house shows health challenges to watch. Current planetary periods indicate areas needing attention.',
                'reasons': [
                    f'{ascendant} Ascendant → Overall vitality → Your constitution type',
                    '6th House → Health challenges → Areas requiring care',
                    f'Sun placement → Energy levels → Core vitality patterns',
                    f'Current transits → Health timing → Periods to be mindful'
                ],
                'remedies': [
                    'Practice yoga suitable for your Ascendant element',
                    'Follow dietary guidelines aligned with your Moon sign'
                ]
            },
            'daily_guidance': {
                'summary': f'Today\'s cosmic weather is shaped by the Moon\'s current transit and your running {mahadasha}-{antardasha} period. This combination suggests focusing on {"action" if mahadasha in ["Mars", "Sun"] else "reflection" if mahadasha in ["Saturn", "Ketu"] else "connections"}.',
                'reasons': [
                    f'Moon transit today → Emotional tone → {moon_sign} sensitivity heightened',
                    f'{mahadasha}-{antardasha} → Daily themes → Ongoing life focus',
                    'Ascendant Lord position → Personal energy → How to direct efforts'
                ],
                'remedies': []
            }
        }
        
        # Get topic-specific response or default
        response_data = topic_responses.get(topic, {
            'summary': f'Based on your {ascendant} Ascendant chart with Moon in {moon_sign}, I can see the unique energies shaping your current phase. The {mahadasha} Mahadasha brings specific themes to your attention.',
            'reasons': [
                f'{ascendant} Ascendant → Core identity → Your fundamental approach to life',
                f'{moon_sign} Moon → Emotional nature → How you process experiences',
                f'{mahadasha} Mahadasha → Current phase → Major life themes now',
                f'{antardasha} Antardasha → Sub-period → Fine-tuning the main themes'
            ],
            'remedies': [
                'Honor your Ascendant Lord through appropriate practices',
                'Follow Moon sign guidelines for emotional well-being'
            ]
        })
        
        return {
            'rawText': response_data['summary'] + ' ' + ' '.join(response_data['reasons']),
            'summary': response_data['summary'],
            'reasons': response_data['reasons'],
            'remedies': response_data.get('remedies', [])
        }


# Singleton instance - lazy initialization pattern
class _NiroLLMSingleton:
    """Lazy singleton wrapper for NiroLLMModule"""
    _instance = None
    
    def __call__(self):
        if self._instance is None:
            self._instance = NiroLLMModule()
        return self._instance

_get_niro_llm = _NiroLLMSingleton()

# Create a proxy object that lazily initializes the LLM module
class _LazyNiroLLM:
    """Proxy that forwards all attribute access to the real LLM module"""
    def __getattr__(self, name):
        return getattr(_get_niro_llm(), name)

niro_llm = _LazyNiroLLM()


def call_niro_llm(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to call NIRO LLM"""
    return _get_niro_llm().call_niro_llm(payload)
