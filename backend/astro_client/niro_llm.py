"""NIRO LLM Module with OpenAI and Gemini support
Updated with:
- ChatGPT 5.1 model
- Reading pack-based evidence structure
- Structured output with signal references
- Improved prompt with real timing data and dates
- Question-centric focus
- Better logging
- Chat tone policy for conversational quality
"""

import os
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# ============================================================================
# RESPONSE QUALITY VALIDATOR - Ensures high-quality human responses
# ============================================================================

class ResponseQualityValidator:
    """Validates response quality and flags low-quality responses for regeneration"""
    
    ASTRO_JARGON = {
        'jupiter', 'saturn', 'mars', 'venus', 'mercury', 'sun', 'moon',
        'rahu', 'ketu', 'lagna', 'ascendant', 'mahadasha', 'dasha',
        '1st house', '2nd house', '3rd house', '4th house', '5th house',
        '6th house', '7th house', '8th house', '9th house', '10th house',
        '11th house', '12th house', 'retrograde', 'aspect', 'conjunction',
        'opposition', 'trine', 'square', 'navamsa', 'dashamsha', 'hora',
        'vimshamsha', 'karakamsha', 'chara dasha', 'yogini dasha',
        'planet', 'house', 'sign', 'aries', 'taurus', 'gemini', 'cancer',
        'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn',
        'aquarius', 'pisces', 'exaltation', 'debilitation', 'mulatrikona'
    }
    
    def __init__(self):
        self.quality_logger = logging.getLogger(f"{__name__}.quality")
    
    def validate(self, response: Dict[str, Any], user_question: str) -> tuple[bool, str]:
        """
        Validate response quality.
        Returns: (is_high_quality: bool, quality_flag: str)
        
        Flags LOW QUALITY if:
        - Less than 3 sentences
        - Sounds instructional or report-like
        - Uses headings or rigid structure
        - Lacks human opening or closing
        - Contains explicit astro jargon unless user asked
        """
        raw_text = response.get('rawText', '').strip()
        
        # Check 1: Minimum length (3 sentences)
        sentences = [s.strip() for s in re.split(r'[.!?]+', raw_text) if s.strip()]
        if len(sentences) < 3:
            self.quality_logger.debug(f"LOW_QUALITY: Only {len(sentences)} sentences (need 3+)")
            return False, "too_short"
        
        # Check 2: Report-like tone detection
        report_patterns = [
            r'According to',
            r'The analysis shows',
            r'Based on the data',
            r'Here is',
            r'The following',
            r'Key points:'
        ]
        if any(re.search(pattern, raw_text, re.IGNORECASE) for pattern in report_patterns):
            self.quality_logger.debug("LOW_QUALITY: Detected report-like tone")
            return False, "report_like"
        
        # Check 3: Rigid structure (multiple colons/headers)
        header_count = len(re.findall(r'^[A-Z][^:]*:', raw_text, re.MULTILINE))
        if header_count > 1:
            self.quality_logger.debug(f"LOW_QUALITY: Detected {header_count} headers")
            return False, "rigid_structure"
        
        # Check 4: Human opening/closing (more lenient)
        # Opening: Check if starts naturally (not robotic)
        has_good_opening = any([
            raw_text.lower().startswith(phrase) for phrase in
            ['hey', 'hi', 'so', 'i', 'the', 'this', 'looks like', 'that\'s', 'you',
             'yes', 'no', 'great', 'absolutely', 'hmm', 'actually', 'definitely',
             'based on', 'your', 'sounds', 'i\'d', 'my', 'interesting', 'telling', 'you\'re']
        ])
        
        # Closing: Check if ends with engagement (ask a question, offer next step, or reference user perspective)
        # Much more lenient - look for indicators of conversation continuation
        has_engagement = (
            raw_text.endswith(('?', '!')) or  # Ends with question or exclamation
            any(phrase in raw_text.lower() for phrase in [
                'tell me', 'what do you', 'what would', 'how does', 'does that',
                'want me', 'should we', 'interested', 'curious', 'think', 'yours',
                'help', 'explore', 'insights', 'sense', 'distinction', 'matters',
                'what\'s driving', 'what', 'ask', 'driving', 'frustration', 'excitement'
            ])
        )
        
        if not (has_good_opening and has_engagement):
            self.quality_logger.debug(f"LOW_QUALITY: Missing opening ({has_good_opening}) or engagement ({has_engagement})")
            return False, "no_human_touch"
        
        # Check 5: Explicit astro jargon (unless user explicitly asked)
        user_lower = user_question.lower()
        user_asked_astro = any(word in user_lower for word in
            ['planet', 'house', 'dasha', 'saturn', 'jupiter', 'chart', 'kundli', 'transit', 'astro', 'veda'])
        
        if not user_asked_astro:
            # Check for excessive jargon
            jargon_patterns = [
                r'\bmahadasha\b', r'\bdasha\b', r'\bnavamsa\b', r'\bdashamsha\b',
                r'\bchara dasha\b', r'\byogini dasha\b', r'\bkarakamsha\b',
                r'\brahu[-\s]*ketu\b', r'\bretrograde\b'
            ]
            found_jargon = [pattern for pattern in jargon_patterns 
                           if re.search(pattern, raw_text.lower())]
            if found_jargon:
                self.quality_logger.debug(f"LOW_QUALITY: Found astro jargon without user request: {found_jargon[:3]}")
                return False, "unwanted_jargon"
        
        self.quality_logger.debug(f"PASS: {len(sentences)} sentences, has opening & engagement, appropriate tone")
        return True, "pass"
    
    def log_quality_metrics(self, response: Dict[str, Any], quality_flag: str, regeneration_count: int):
        """Log quality metrics for debugging (non-user facing)"""
        raw_text = response.get('rawText', '').strip()
        response_length = len(raw_text)
        sentences = len([s.strip() for s in re.split(r'[.!?]+', raw_text) if s.strip()])
        
        self.quality_logger.info(
            f"QUALITY_METRICS | response_length={response_length} | "
            f"sentences={sentences} | quality_flag={quality_flag} | "
            f"regeneration_count={regeneration_count}"
        )

# Constant for OpenAI model - using gpt-5.1
OPENAI_MODEL_NAME = "gpt-5.1"

# ============================================================================
# CHAT TONE POLICY - Centralized messaging quality rules
# ============================================================================
CHAT_TONE_POLICY = """
CORE MESSAGE QUALITY RULES:

1. CONVERSATIONAL TONE
   - Write like a human guide, not a robot
   - Use natural language (avoid "As an AI" or robotic phrasing)
   - Be warm, genuine, and slightly opinionated
   - 3-8 lines maximum unless user asked for detailed reading

2. NO MECHANICAL SECTIONS IN MAIN MESSAGE
   - Never include headers like "SUMMARY:", "REASONS:", "REMEDIES:", "DATA GAPS:"
   - These belong in structured fields only (reasons[], remedies[], etc.)
   - Main message (rawText) should be clean narrative

3. STRUCTURE FOR READABILITY
   - Use line breaks naturally
   - Lead with friendly, context-aware opener (1 line)
   - Give the answer (2-5 lines)
   - End with ONE clear next step or follow-up question

4. DATA GAPS HANDLING
   - If data_gaps is empty → DO NOT mention missing information
   - If data_gaps exists AND truly blocking → ask only for those specific fields
   - Avoid phrases like "lack of specific query" or "limited information available"

5. FOLLOW-UP PROMPTS
   - End with genuine next step ("Want me to look at career, relationships, or finances?")
   - Make choices clear and actionable
   - NO generic "what else would you like to know?"

6. ASTROLOGY READING MODE
   - Reference chart signals lightly and in plain language
   - Avoid jargon dumps (no listing all planets/houses)
   - Explain terms inline if used (e.g., "Jupiter mahadasha (major period)")
   - Ground predictions in timing windows where available

7. AVOID THESE PATTERNS
   - "Based on your chart..." (everyone expects this from astrology)
   - "I see that..." (unnecessary self-reference)
   - "Data gaps" or "missing information" unless truly blocking
   - Lists of all planets/houses/dashas when not asked
   - Forced disclaimers or hedging language
"""


class NiroLLMModule:
    """
    NIRO LLM with OpenAI primary and Gemini fallback.
    Lazy initialization to ensure env vars are loaded.
    Includes quality validation and auto-regeneration for low-quality responses.
    """
    
    MAX_REGENERATION_ATTEMPTS = 2  # Max times to retry a low-quality response
    
    def __init__(self):
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.system_prompt = self._build_system_prompt()
        self.quality_validator = ResponseQualityValidator()
        
        logger.info(f"NiroLLMModule initialized (model={OPENAI_MODEL_NAME}, real_llm={bool(self.openai_key or self.gemini_key)})")
    
    def generate_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response using OpenAI or Gemini with quality validation and auto-regeneration"""
        mode = payload.get('mode', 'NORMAL_READING')
        topic = payload.get('topic', 'general')
        user_question = payload.get('user_question', '')
        astro_features = payload.get('astro_features', {})
        
        has_features = bool(astro_features and astro_features.get('focus_factors'))
        logger.info(f"Generating NIRO response: mode={mode}, topic={topic}, has_features={has_features}")
        
        # Generate with quality validation and regeneration
        response = self._generate_with_quality_check(payload, user_question)
        return response
    
    def _generate_with_quality_check(self, payload: Dict[str, Any], user_question: str, attempt: int = 0) -> Dict[str, Any]:
        """Generate response and validate quality, regenerate if needed"""
        user_prompt = self._build_user_prompt(payload)
        mode = payload.get('mode', 'NORMAL_READING')
        topic = payload.get('topic', 'general')
        
        # Call LLM
        response = self._call_real_llm(mode, topic, user_prompt)
        
        # Validate quality (with error handling to ensure quality checks don't break response generation)
        try:
            is_high_quality, quality_flag = self.quality_validator.validate(response, user_question)
        except Exception as e:
            logger.error(f"Quality validation error: {e}. Proceeding without quality check.")
            is_high_quality = True  # Assume high quality if validation fails
            quality_flag = "validation_error"
        
        # Log quality metrics (with error handling)
        try:
            self.quality_validator.log_quality_metrics(response, quality_flag, attempt)
        except Exception as e:
            logger.error(f"Quality logging error: {e}")
        
        # If low quality and we have regeneration attempts left, try again
        if not is_high_quality and attempt < self.MAX_REGENERATION_ATTEMPTS:
            logger.warning(
                f"LOW QUALITY RESPONSE (flag={quality_flag}, attempt={attempt}). "
                f"Regenerating with stronger instruction..."
            )
            
            # Create regeneration prompt with stronger instruction
            regen_payload = payload.copy()
            regen_payload['_regeneration_instruction'] = (
                "\n\n[REGENERATION REQUIRED]\n"
                "The previous response was too mechanical or lacked warmth. "
                "Rewrite with MORE human touch: warmer tone, deeper insights, better opening/closing, "
                "and conversational flow. Expand into 4-6 sentences of warm, human guidance."
            )
            
            return self._generate_with_quality_check(regen_payload, user_question, attempt + 1)
        
        # Final quality log
        final_flag = "regenerated" if attempt > 0 else quality_flag
        try:
            self.quality_validator.log_quality_metrics(response, final_flag, attempt)
        except Exception as e:
            logger.error(f"Quality logging error on final log: {e}")
        
        return response
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for NIRO"""
        return f"""You are NIRO, an AI Vedic astrologer who provides accurate, compassionate, and conversational insights.

YOUR PRIMARY ROLE:
1. For astrology questions: Use reading packs and provide conversational analysis (NOT mechanical lists)
2. For conversational inputs: Respond warmly and naturally, guide them to ask a question

A reading pack is a structured evidence document containing signals (astrological findings) tied to the user's question.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHAT QUALITY RULES (CRITICAL - APPLY TO ALL RESPONSES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{CHAT_TONE_POLICY}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your response has TWO parts:

PART 1: rawText (Main Message - Conversational)
========
- Clean narrative text only
- NO section headers (SUMMARY:, REASONS:, REMEDIES:, DATA_GAPS:)
- 3-8 lines unless detailed reading requested
- End with one clear follow-up or question
- For astrology: reference signals lightly, explain jargon inline
- For conversational: be warm and natural

PART 2: Structured Fields (For UI "Why this answer" section)
========
You MUST populate these fields so the UI can display them separately:
- reasons: List of 2-4 short bullets explaining your answer (use this to cite signals)
- remedies: List of 0-2 actionable items (only if applicable)
- data_gaps: List of missing fields (only if non-empty AND blocking)

FORMAT THE OUTPUT AS:
```
rawText: [Your conversational message here - NO section headers]

reasons:
- [S1] Signal interpretation → Impact
- [S2] Another signal → Impact

remedies:
- [Remedy if applicable]

data_gaps:
- [Only list if truly blocking - otherwise omit section]
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERNAL QUALITY SELF-CHECK (BEFORE FINALIZING)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before you send your response, internally verify:

✓ Does this sound like a human guide, not a report or list?
✓ Would this feel comforting or insightful to a real person?
✓ Is the message engaging enough to invite a follow-up?
✓ Are there 3+ sentences with clear opening and closing?
✓ Does it avoid mechanical jargon and feel conversational?

If ANY answer is "no" → Rewrite the rawText section to be warmer, more engaging, and more human.
This is non-negotiable: HIGH QUALITY HUMAN RESPONSES are the default.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPONSE ROUTING (Choose one)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IF CONVERSATIONAL INPUT (greeting, small talk, "thanks", "hi", "how are you"):
→ Use natural language response
→ Warm and genuine tone
→ Guide them to ask an astrology question
→ NO structured sections needed

EXAMPLE - User says "hi":
```
rawText: Hey! Great to have you here. I'm NIRO, your personal astrology guide. What's on your mind? Career, relationships, finances—or just curious about what's coming up?

reasons:
- Friendly greeting, prompt for question

remedies:
(empty)

data_gaps:
(empty)
```

IF ASTROLOGY QUESTION (career, timing, comparisons, life advice based on chart):
→ Start with friendly opener (1 line)
→ Give clear answer (2-5 lines) referencing chart signals lightly
→ End with follow-up question or next step (1 line)
→ Populate reasons[] with signal references
→ Only mention data_gaps if truly blocking

EXAMPLE - User asks "Should I switch jobs?":
```
rawText: Based on your chart, this looks like a good transition window. Venus in your 10th suggests career growth potential, and the timing aligns well for a shift. I'd lean toward yes—but before you jump, tell me: are you more worried about leaving a comfortable role or about making the jump itself?

reasons:
- [S1] Venus in 10th house → Career growth & opportunities
- [S4] Favorable timing window (next 6 months) → Good for major decisions

remedies:
- Have conversations with your network before resigning

data_gaps:
(empty - only include if missing critical fields)
```

IF DATA GAPS EXIST AND BLOCK ANSWER:
→ Ask ONLY for the missing fields
→ Be brief and non-technical
→ Make it easy to respond

EXAMPLE - Missing critical data:
```
rawText: I can definitely look at this for you. To give you a solid answer about timing, I need your birth time and place. Once I have those, I'll have everything I need.

reasons:
(empty)

remedies:
(empty)

data_gaps:
- Birth time (hour and minute)
- Birth location (city/place)
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL CONTENT RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SIGNAL USAGE
   - Only cite signals from reading_pack.signals
   - Format: [S#] Signal claim → Interpretation → Impact
   - Never invent planets/houses/dashas not in signals
   - Limit to 2-4 signals max per response (don't dump all)

2. TIMING
   - Use reading_pack.timing_windows for predictions
   - Be specific: "next 6 months", "January-March 2025", not vague
   - Avoid "soon", "eventually", "in the future"

3. DATA GAPS
   - If reading_pack.data_gaps is EMPTY → Never mention missing data
   - If reading_pack.data_gaps has items AND they block the answer → Ask for them
   - If gaps exist but don't block → Don't mention, just answer what you can

4. TONE GUARDRAILS
   - NO "As an AI" or "I'm an algorithm"
   - NO forced hedging ("It's possible that...", "Maybe you should...")
   - NO long disclaimers
   - NO astrojargon dumps
   - BE slightly opinionated but evidence-based

5. COMPARE QUESTIONS
   - State which is better + why (concisely)
   - When to reassess (timing)
   - ONE follow-up question
   - NO lengthy pro/con lists

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SMALL TALK EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Hi" / "Hello" / "Hey":
→ Warm greeting + ask what they want to know

"Thanks" / "Thank you":
→ You're welcome + ask next question or confirm they're done

"OK" / "Got it":
→ Brief acknowledgment + ask if they want to explore something else

"How are you?" / "Tell me about yourself":
→ Humanize response, redirect to astrology question

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def _build_user_prompt(self, payload: Dict[str, Any]) -> str:
        """Build the user prompt from payload using reading_pack structure"""
        mode = payload.get('mode', 'NORMAL_READING')
        topic = payload.get('topic', 'general')
        time_context = payload.get('time_context', 'timeless')
        intent = payload.get('intent', 'reflect')
        user_question = payload.get('user_question', '')
        reading_pack = payload.get('reading_pack', {})
        regen_instruction = payload.get('_regeneration_instruction', '')
        
        # Detect if this is a conversational input (greeting, small talk, etc.)
        is_conversational = self._is_conversational_input(user_question)
        
        if is_conversational:
            # For conversational inputs, keep it simple - no astrology structure
            prompt = f"""USER_MESSAGE: {user_question}

INSTRUCTION: Respond naturally and warmly. Be genuine and helpful. If appropriate, guide them toward asking an astrology question. No need for structured sections—just write like you're chatting with a friend.

Remember the chat tone policy: warm, human, no "As an AI" language, no mechanical sections."""
            if regen_instruction:
                prompt += regen_instruction
            return prompt
        
        # For astrology questions, build structured prompt
        prompt = f"""MODE: {mode}
TOPIC: {topic}
TIME_CONTEXT: {time_context}
INTENT: {intent}
USER_QUESTION: {user_question}

INSTRUCTIONS:
Your primary job is to directly answer the USER_QUESTION using ONLY the signals below.
Use the new format with clear rawText section (conversational, no headers) and structured reasons/remedies/data_gaps.
For timing questions: emphasize TIMING_WINDOWS and specific dates.
For compare questions: state which option is better + why + when to reassess.
Use probability language. Never claim certainty.
Reference signal IDs in REASONS: [S1] → interpretation → impact
Keep the main message (rawText) warm and natural - NO mechanical sections like "SUMMARY:" or "REASONS:" in the message itself.

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
        
        # Add regeneration instruction if this is a retry
        if regen_instruction:
            prompt += regen_instruction
        
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
        """Parse the LLM response - handles both structured (astrology) and plain text (conversational) formats
        
        Expects format:
        rawText: [conversational message]
        
        reasons:
        - [reason 1]
        - [reason 2]
        
        remedies:
        - [remedy]
        
        data_gaps:
        - [gap] (optional - only if non-empty)
        """
        
        result = {
            'rawText': content,
            'summary': '',
            'reasons': [],
            'remedies': [],
            'data_gaps': []
        }
        
        lines = content.strip().split('\n')
        
        current_section = None
        rawtext_lines = []
        parsing_sections = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check for section headers
            if line_stripped.lower().startswith('rawtext:'):
                parsing_sections = True
                rawtext_content = line_stripped.replace('rawtext:', '', 1).strip()
                if rawtext_content:
                    rawtext_lines.append(rawtext_content)
                current_section = 'rawtext'
                
            elif line_stripped.lower().startswith('reasons:'):
                parsing_sections = True
                current_section = 'reasons'
                
            elif line_stripped.lower().startswith('remedies:'):
                parsing_sections = True
                current_section = 'remedies'
                
            elif line_stripped.lower().startswith('data_gaps:') or line_stripped.lower().startswith('data gaps:'):
                parsing_sections = True
                current_section = 'data_gaps'
                
            elif line_stripped.lower().startswith('summary:'):
                # Handle legacy format
                parsing_sections = True
                current_section = 'summary'
                summary_content = line_stripped.replace('summary:', '', 1).replace('SUMMARY:', '', 1).strip()
                if summary_content:
                    result['summary'] = summary_content
                    
            elif line_stripped.startswith('-') and current_section in ['reasons', 'remedies', 'data_gaps']:
                # Handle bullet points
                item = line_stripped[1:].strip()
                if item:
                    result[current_section].append(item)
                    
            elif current_section == 'rawtext' and line_stripped and not line_stripped.startswith('-'):
                # Accumulate rawtext lines until we hit a section header
                if not any(line_stripped.lower().startswith(s) for s in ['reasons:', 'remedies:', 'data_gaps:', 'data gaps:', 'summary:']):
                    rawtext_lines.append(line_stripped)
                    
            elif current_section == 'summary' and line_stripped and not line_stripped.startswith('-'):
                # Handle multi-line summary (legacy format)
                if not any(line_stripped.lower().startswith(s) for s in ['reasons:', 'remedies:', 'data_gaps:', 'data gaps:']):
                    result['summary'] += ' ' + line_stripped if result['summary'] else line_stripped
        
        # Set rawText from accumulated lines
        if rawtext_lines:
            result['rawText'] = '\n'.join(rawtext_lines)
        elif not parsing_sections:
            # If no sections found, treat entire response as rawText (conversational)
            result['rawText'] = content
            result['reasons'] = []
            result['remedies'] = []
            result['data_gaps'] = []
        
        # Clean up data_gaps - only include if non-empty
        if not result.get('data_gaps'):
            result.pop('data_gaps', None)
        
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
