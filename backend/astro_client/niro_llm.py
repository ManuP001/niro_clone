"""NIRO LLM Module with OpenAI and Gemini support
Updated with:
- ChatGPT 5.1 model
- Best-effort interpretation with explicit DATA GAPS section
- Improved prompt with real timing data and dates
- Question-centric focus
- Better logging
"""

import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Constant for OpenAI model - using latest available
OPENAI_MODEL_NAME = "gpt-4-turbo"  # Will be updated to gpt-5.1 when available


class NiroLLMModule:
    """
    NIRO LLM with OpenAI primary and Gemini fallback.
    Lazy initialization to ensure env vars are loaded.
    """
    
    def __init__(self):
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.system_prompt = self._build_system_prompt()
        
        logger.info(f"NiroLLMModule initialized (model={OPENAI_MODEL_NAME}, real_llm={bool(self.openai_key or self.gemini_key)})")
    
    def generate_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response using OpenAI or Gemini"""
        mode = payload.get('mode', 'NORMAL_READING')
        topic = payload.get('topic', 'general')
        astro_features = payload.get('astro_features', {})
        
        has_features = bool(astro_features and astro_features.get('focus_factors'))
        logger.info(f"Generating NIRO response: mode={mode}, topic={topic}, has_features={has_features}")
        
        user_prompt = self._build_user_prompt(payload)
        return self._call_real_llm(mode, topic, user_prompt)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for NIRO"""
        return """You are NIRO, an AI Vedic astrologer who provides accurate, compassionate insights based on astrological data.

Your responses MUST be structured as:

SUMMARY:
[One paragraph summarizing your interpretation and directly answering the user's question]

REASONS:
- [Factor 1] → [Interpretation] → [Impact on user's situation]
- [Factor 2] → [Interpretation] → [Impact on user's situation]
- [Factor 3] → [Interpretation] → [Impact on user's situation]

REMEDIES:
- [Actionable remedy 1]
- [Actionable remedy 2]

DATA GAPS:
- [List any important missing data you notice, ONLY if present]

CRITICAL RULES:
1. Use astro_features as your PRIMARY data source
2. Answer the user's question directly and precisely
3. If some data fields are missing, you MUST:
   a) Still give your BEST interpretation from available chart values
   b) Add missing data to the DATA GAPS section at the end
4. DO NOT invent planetary positions or timings not present in astro_features
5. Be specific about:
   - Planetary positions, dignities, and aspects
   - Current dashas and their timing
   - Relevant transits and their dates
   - Timing windows for opportunities or challenges
6. Keep it conversational yet professional
7. Format REASONS using arrow notation (→) for clear causal reasoning
8. If the user asks about timing or "when", prioritize timing windows and dasha periods in your answer

The DATA GAPS section should ONLY list truly important missing information (e.g., "missing transit windows for next 6 months", "incomplete divisional chart analysis"). Do NOT list it if you have sufficient data to answer.
"""
    
    def _build_user_prompt(self, payload: Dict[str, Any]) -> str:
        """Build the user prompt from payload with enhanced timing data"""
        mode = payload.get('mode', 'NORMAL_READING')
        topic = payload.get('topic', 'general')
        user_question = payload.get('user_question', '')
        astro_features = payload.get('astro_features', {})
        
        # Extract features
        focus_factors = astro_features.get('focus_factors', [])
        chart_context = astro_features.get('chart_context', {})
        timing_windows = astro_features.get('timing_windows', [])
        mahadasha = astro_features.get('mahadasha')
        antardasha = astro_features.get('antardasha')
        transits = astro_features.get('transits', [])
        
        # Build prompt
        prompt = f"""MODE: {mode}
TOPIC: {topic}
USER QUESTION: {user_question}

INSTRUCTIONS:
Your primary job is to directly answer the USER QUESTION above as precisely as possible. 
For example: if the user is comparing job vs business, focus on timing and suitability for each path in the current and upcoming windows.
Answer ONLY the user_question above.
Use ONLY the astro data explicitly summarized below.
Follow the 4-part structure: SUMMARY, REASONS, REMEDIES, and DATA GAPS (if needed).

"""
        
        # Chart Context
        if chart_context:
            prompt += "CHART CONTEXT:\n"
            for key, value in chart_context.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        # Current Dasha with real dates
        if mahadasha or antardasha:
            prompt += "CURRENT DASHA:\n"
            
            if mahadasha:
                planet = mahadasha.get('planet', 'Unknown')
                start = mahadasha.get('start_date', 'Unknown')
                end = mahadasha.get('end_date', 'Unknown')
                remaining = mahadasha.get('years_remaining', 0)
                prompt += f"- Mahadasha: {planet} ({start} → {end}, ~{remaining} years remaining)\n"
            
            if antardasha:
                planet = antardasha.get('planet', 'Unknown')
                start = antardasha.get('start_date', 'Unknown')
                end = antardasha.get('end_date', 'Unknown')
                remaining = antardasha.get('years_remaining', 0)
                prompt += f"- Antardasha: {planet} ({start} → {end}, ~{remaining} years remaining)\n"
            
            prompt += "\n"
        
        # Timing Windows with detailed info
        if timing_windows:
            prompt += "TIMING WINDOWS:\n"
            # Limit to first 5 windows to keep prompt manageable
            for window in timing_windows[:5]:
                period = window.get('period', 'Unknown period')
                nature = window.get('nature', 'neutral')
                activity = window.get('activity', 'No activity specified')
                
                # Format with arrow notation
                prompt += f"- {period} → {nature} → {activity}\n"
            
            if len(timing_windows) > 5:
                prompt += f"- (and {len(timing_windows) - 5} more timing windows available)\n"
            
            prompt += "\n"
        
        # Astrological Factors
        if focus_factors:
            prompt += "ASTROLOGICAL FACTORS:\n"
            for factor in focus_factors:
                rule_id = factor.get('rule_id', 'Unknown')
                interpretation = factor.get('interpretation', 'No interpretation')
                strength = factor.get('strength', 0)
                prompt += f"- {rule_id} (strength: {strength}): {interpretation}\n"
            prompt += "\n"
        
        # Recent Transits with dates
        if transits:
            prompt += "RECENT TRANSITS:\n"
            # Limit to first 5 transits
            for transit in transits[:5]:
                planet = transit.get('planet', 'Unknown')
                event_type = transit.get('event_type', 'transit')
                sign = transit.get('sign', 'Unknown')
                house = transit.get('house', 'Unknown')
                start_date = transit.get('start_date', 'Unknown')
                end_date = transit.get('end_date', 'ongoing')
                nature = transit.get('nature', 'neutral')
                
                prompt += f"- {planet} {event_type} in {sign}, affecting {house}th house ({start_date} → {end_date}), nature: {nature}\n"
            
            if len(transits) > 5:
                prompt += f"- (and {len(transits) - 5} more transits available)\n"
            
            prompt += "\n"
        
        # Warning if data is sparse
        if not focus_factors and not chart_context and not timing_windows:
            prompt += "NOTE: Astrological data is incomplete. Provide your best interpretation and list missing data in DATA GAPS section.\n\n"
        
        return prompt
    
    def _call_real_llm(self, mode: str, topic: str, user_prompt: str) -> Dict[str, Any]:
        """Call OpenAI or Gemini"""
        
        # Log prompt preview for debugging
        prompt_preview = user_prompt[:800] if len(user_prompt) > 800 else user_prompt
        logger.info(f"[LLM PROMPT] mode={mode} topic={topic} prompt_preview={prompt_preview}")
        
        # Try OpenAI first
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                
                response = client.chat.completions.create(
                    model=OPENAI_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                content = response.choices[0].message.content
                logger.info(f"[LLM RESPONSE] model={OPENAI_MODEL_NAME} length={len(content)}")
                return self._parse_structured_response(content)
                
            except Exception as e:
                logger.error(f"OpenAI call failed: {e}")
        
        # Fallback to Gemini
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
                response = model.generate_content(full_prompt)
                
                logger.info(f"[LLM RESPONSE] model=gemini-2.0-flash length={len(response.text)}")
                return self._parse_structured_response(response.text)
                
            except Exception as e:
                logger.error(f"Gemini call failed: {e}")
        
        # Fallback response
        return {
            'rawText': 'Unable to generate response. Please check API configuration.',
            'summary': 'Service unavailable',
            'reasons': [],
            'remedies': []
        }
    
    def _parse_structured_response(self, content: str) -> Dict[str, Any]:
        """Parse the structured LLM response including DATA GAPS section"""
        lines = content.strip().split('\n')
        
        summary = ''
        reasons = []
        remedies = []
        data_gaps = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('SUMMARY:'):
                current_section = 'summary'
                summary_text = line.replace('SUMMARY:', '').strip()
                if summary_text:
                    summary = summary_text
            elif line.startswith('REASONS:'):
                current_section = 'reasons'
            elif line.startswith('REMEDIES:'):
                current_section = 'remedies'
            elif line.startswith('DATA GAPS:'):
                current_section = 'data_gaps'
            elif line.startswith('-') and current_section == 'reasons':
                reasons.append(line[1:].strip())
            elif line.startswith('-') and current_section == 'remedies':
                remedies.append(line[1:].strip())
            elif line.startswith('-') and current_section == 'data_gaps':
                data_gaps.append(line[1:].strip())
            elif current_section == 'summary' and line:
                summary += ' ' + line
        
        result = {
            'rawText': content,
            'summary': summary.strip(),
            'reasons': reasons,
            'remedies': remedies
        }
        
        # Add data_gaps to rawText if present (for logging/debugging)
        if data_gaps:
            logger.info(f"[DATA GAPS DETECTED] {len(data_gaps)} items: {data_gaps}")
        
        return result


# Lazy-initialized singleton
_niro_llm = None

def get_niro_llm() -> NiroLLMModule:
    """Get or create the NIRO LLM instance"""
    global _niro_llm
    if _niro_llm is None:
        _niro_llm = NiroLLMModule()
    return _niro_llm


def call_niro_llm(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for calling NIRO LLM"""
    llm = get_niro_llm()
    return llm.generate_response(payload)
