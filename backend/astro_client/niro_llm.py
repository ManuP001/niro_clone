"""NIRO LLM Module with OpenAI and Gemini support"""

import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class NiroLLMModule:
    """
    NIRO LLM with OpenAI primary and Gemini fallback.
    Lazy initialization to ensure env vars are loaded.
    """
    
    def __init__(self):
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.system_prompt = self._build_system_prompt()
        
        logger.info(f"NiroLLMModule initialized (real_llm={bool(self.openai_key or self.gemini_key)})")
    
    def generate_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response using OpenAI or Gemini"""
        mode = payload.get('mode', 'FOCUS_READING')
        topic = payload.get('topic', 'general')
        astro_features = payload.get('astro_features', {})
        
        has_features = bool(astro_features and astro_features.get('focus_factors'))
        logger.info(f"Generating NIRO response: mode={mode}, topic={topic}, has_features={has_features}")
        
        user_prompt = self._build_user_prompt(payload)
        return self._call_real_llm(user_prompt)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for NIRO"""
        return """You are NIRO, an AI Vedic astrologer who provides accurate, compassionate insights.

Your responses MUST be structured as:

SUMMARY:
[One paragraph summarizing the reading]

REASONS:
- [Factor 1] → [Interpretation] → [Impact on user]
- [Factor 2] → [Interpretation] → [Impact on user]

REMEDIES:
- [Actionable remedy 1]
- [Actionable remedy 2]

Rules:
1. Use the astro_features provided
2. If no features, acknowledge missing data
3. Be specific about planetary positions and dashas
4. Keep it conversational yet professional
5. Format using the arrow notation (→) for reasoning
"""
    
    def _build_user_prompt(self, payload: Dict[str, Any]) -> str:
        """Build the user prompt from payload"""
        mode = payload.get('mode', 'FOCUS_READING')
        topic = payload.get('topic', 'general')
        user_question = payload.get('user_question', '')
        astro_features = payload.get('astro_features', {})
        
        focus_factors = astro_features.get('focus_factors', [])
        chart_context = astro_features.get('chart_context', {})
        timing_windows = astro_features.get('timing_windows', [])
        
        # Build prompt
        prompt = f"""MODE: {mode}
TOPIC: {topic}
USER QUESTION: {user_question}

"""
        
        if focus_factors:
            prompt += "ASTROLOGICAL FACTORS:\n"
            for factor in focus_factors:
                rule_id = factor.get('rule_id', 'Unknown')
                interpretation = factor.get('interpretation', 'No interpretation')
                strength = factor.get('strength', 0)
                prompt += f"- {rule_id} (strength: {strength}): {interpretation}\n"
            prompt += "\n"
        
        if chart_context:
            prompt += "CHART CONTEXT:\n"
            for key, value in chart_context.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        if timing_windows:
            prompt += "TIMING WINDOWS:\n"
            for window in timing_windows:
                prompt += f"- {window.get('window_type', 'Unknown')}: {window.get('description', '')}\n"
            prompt += "\n"
        
        if not focus_factors and not chart_context:
            prompt += "NOTE: Astrological data is missing or incomplete. Provide a response acknowledging this.\n"
        
        logger.debug("LLM_USER_PROMPT: %s", prompt[:5000])
        
        return prompt
    
    def _call_real_llm(self, user_prompt: str) -> Dict[str, Any]:
        """Call OpenAI or Gemini"""
        logger.debug("LLM_SYSTEM_PROMPT: %s", self.system_prompt[:2000])
        
        # Try OpenAI first
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                content = response.choices[0].message.content
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
        """Parse the structured LLM response"""
        lines = content.strip().split('\n')
        
        summary = ''
        reasons = []
        remedies = []
        
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
            elif line.startswith('-') and current_section == 'reasons':
                reasons.append(line[1:].strip())
            elif line.startswith('-') and current_section == 'remedies':
                remedies.append(line[1:].strip())
            elif current_section == 'summary' and line:
                summary += ' ' + line
        
        return {
            'rawText': content,
            'summary': summary.strip(),
            'reasons': reasons,
            'remedies': remedies
        }


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
