"""NIRO LLM Module with OpenAI and Gemini support
Updated with:
- ChatGPT 5.1 model
- Reading pack-based evidence structure
- Structured output with signal references
- Improved prompt with real timing data and dates
- Question-centric focus
- Better logging
"""

import os
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Constant for OpenAI model - using gpt-5.1
OPENAI_MODEL_NAME = "gpt-5.1"


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
        return """You are NIRO, an AI Vedic astrologer who provides accurate, compassionate insights.

YOUR PRIMARY ROLE:
1. When answering astrology questions: Use reading packs and structured evidence
2. When answering conversational/casual inputs: Respond naturally without forcing astrology structure

A reading pack is a structured evidence document containing signals (astrological findings) tied to the user's question.

OUTPUT RULES:

FOR ASTROLOGY QUESTIONS (chart-based, timing, predictions, comparisons):
Use the structured format below with SUMMARY, REASONS, REMEDIES, and DATA_GAPS sections.

SUMMARY:
[1-2 sentences] Direct answer to user's question + specific timeframe if future-oriented

REASONS:
[2-4 bullets, each must reference signal(s)]
Format: [Signal ID] → Interpretation → Impact
Example: [S1] Ketu Mahadasha (5 yrs remaining) → Detachment & karmic resolution → Suggests spiritual focus

REMEDIES:
[0-2 items max] Only if challenges exist or user asked for them
- [Actionable remedy with timing window if relevant]

DATA_GAPS:
[Only if reading_pack.data_gaps is non-empty]
- missing_field_1

FOR CONVERSATIONAL INPUTS (greetings, small talk, casual questions):
Respond naturally in plain language. NO structured sections. Be warm and authentic.
Examples of conversational inputs: "hi", "hello", "thanks", "how are you", "tell me about yourself"

CRITICAL RULES:
1. Only use reading_pack.signals for REASONS in astrology responses
2. Only use reading_pack.timing_windows for timing predictions
3. If reading_pack.data_gaps is empty → DO NOT mention any missing data
4. If data_gaps exist → ONLY mention those exact fields in astrology responses
5. Reference signal IDs like [S1], [S2] in REASONS section of astrology responses
6. For compare questions: state which is better + why + when to reassess
7. Keep SUMMARY under 80 words in astrology responses
8. Be conversational yet professional
9. Use arrow notation (→) in REASONS for clear causal logic
10. Never invent planets, houses, dashas, or transits not in signals
11. If time_context is "future", emphasize timing_windows and decision windows
12. If time_context is "compare", focus on distinguishing factors between options

TONE:
- For astrology: Insightful, evidence-based, empowering, never deterministic
- For conversations: Warm, human, genuine, helpful
"""
    
    def _build_user_prompt(self, payload: Dict[str, Any]) -> str:
        """Build the user prompt from payload using reading_pack structure"""
        mode = payload.get('mode', 'NORMAL_READING')
        topic = payload.get('topic', 'general')
        time_context = payload.get('time_context', 'timeless')
        intent = payload.get('intent', 'reflect')
        user_question = payload.get('user_question', '')
        reading_pack = payload.get('reading_pack', {})
        
        # Detect if this is a conversational input (greeting, small talk, etc.)
        is_conversational = self._is_conversational_input(user_question)
        
        if is_conversational:
            # For conversational inputs, keep it simple - no astrology structure
            prompt = f"""USER_MESSAGE: {user_question}

Just respond naturally and warmly. No need for structured sections or astrology analysis."""
            return prompt
        
        # For astrology questions, build structured prompt
        prompt = f"""MODE: {mode}
TOPIC: {topic}
TIME_CONTEXT: {time_context}
INTENT: {intent}
USER_QUESTION: {user_question}

INSTRUCTIONS:
Your primary job is to directly answer the USER_QUESTION using ONLY the signals below.
For timing questions: emphasize TIMING_WINDOWS and specific dates.
For compare questions: state which option is better + why + when to reassess.
Use probability language. Never claim certainty.
Reference signal IDs in REASONS: [S1] → interpretation → impact

"""
        
        # Add signals
        signals = reading_pack.get('signals', [])
        if signals:
            prompt += "SIGNALS (Astrological Evidence):\n"
            for signal in signals:
                signal_id = signal.get('id', '?')
                claim = signal.get('claim', '')
                sig_type = signal.get('type', '')
                polarity = signal.get('polarity', '')
                
                prompt += f"- {signal_id} [{sig_type}] {claim} ({polarity})\n"
            
            prompt += "\n"
        
        # Add timing windows
        timing_windows = reading_pack.get('timing_windows', [])
        if timing_windows:
            prompt += "TIMING_WINDOWS (For Future Questions):\n"
            for window in timing_windows[:3]:  # Max 3
                period = window.get('period', 'Unknown')
                nature = window.get('nature', 'neutral')
                activity = window.get('activity', 'No details')
                
                prompt += f"- {period} ({nature}): {activity}\n"
            
            prompt += "\n"
        
        # Add data gaps warning
        data_gaps = reading_pack.get('data_gaps', [])
        if data_gaps:
            prompt += f"DATA_GAPS: {', '.join(data_gaps)}\n"
            prompt += "⚠️ IMPORTANT: Only mention these gaps if they are truly critical to answering the question.\n\n"
        else:
            prompt += "✓ No data gaps detected. Provide full interpretation without mentioning missing data.\n\n"
        
        return prompt
    
    def _is_conversational_input(self, text: str) -> bool:
        """Detect if input is conversational (greeting, small talk) vs astrology question"""
        if not text:
            return False
        
        msg_lower = text.lower().strip()
        
        # Common conversational patterns
        conversational_patterns = [
            r"^(hi|hello|hey|hey there|howdy)[\s\!\?]*$",
            r"^(thanks|thank you|thx|appreciate|appreciate it)[\s\!\?]*$",
            r"^(how are you|how\'re you|how r u|hru)[\s\!\?]*$",
            r"^(what\'s up|what up|sup|yo)[\s\!\?]*$",
            r"^(good morning|good afternoon|good evening|good night)[\s\!\?]*$",
            r"^(bye|goodbye|see you|catch you)[\s\!\?]*$",
            r"^(nice to meet you|pleased to meet you)[\s\!\?]*$",
            r"^(tell me about yourself|who are you)[\s\!\?]*$",
            r"^(what do you do|what is niro|what\'s niro)[\s\!\?]*$",
            r"^(ok|okay|alright|got it|understood)[\s\!\?]*$",
            r"^(lol|haha|lmao)[\s\!\?]*$",
            r"^(yes|no|maybe|perhaps)[\s\!\?]*$",
        ]
        
        for pattern in conversational_patterns:
            import re
            if re.search(pattern, msg_lower):
                return True
        
        # If message is very short (< 5 words) and doesn't contain astrology keywords
        word_count = len(msg_lower.split())
        if word_count <= 4:
            astro_keywords = [
                'birth', 'chart', 'astro', 'planet', 'dasha', 'transit', 'house',
                'zodiac', 'sign', 'when', 'will', 'should', 'married', 'job',
                'career', 'health', 'timing', 'auspicious', 'question'
            ]
            has_astro_keyword = any(keyword in msg_lower for keyword in astro_keywords)
            if not has_astro_keyword:
                return True
        
        return False
    
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
                    max_completion_tokens=1500
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
        """Parse the LLM response - handles both structured (astrology) and plain text (conversational) formats"""
        lines = content.strip().split('\n')
        
        summary = ''
        reasons = []
        remedies = []
        data_gaps = []
        
        current_section = None
        has_structure = False  # Track if we found structured sections
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('SUMMARY:'):
                has_structure = True
                current_section = 'summary'
                summary_text = line.replace('SUMMARY:', '').strip()
                if summary_text:
                    summary = summary_text
            elif line.startswith('REASONS:'):
                has_structure = True
                current_section = 'reasons'
            elif line.startswith('REMEDIES:'):
                has_structure = True
                current_section = 'remedies'
            elif line.startswith('DATA GAPS:'):
                has_structure = True
                current_section = 'data_gaps'
            elif line.startswith('-') and current_section == 'reasons':
                reasons.append(line[1:].strip())
            elif line.startswith('-') and current_section == 'remedies':
                remedies.append(line[1:].strip())
            elif line.startswith('-') and current_section == 'data_gaps':
                data_gaps.append(line[1:].strip())
            elif current_section == 'summary' and line:
                summary += ' ' + line
        
        # If no structured sections found, treat entire response as plain text
        if not has_structure:
            return {
                'rawText': content,
                'summary': '',  # No summary for conversational responses
                'reasons': [],
                'remedies': []
            }
        
        result = {
            'rawText': content,
            'summary': summary.strip(),
            'reasons': reasons,
            'remedies': remedies
        }
        
        # Add data_gaps to logging if present
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
