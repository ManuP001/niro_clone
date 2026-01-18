"""NIRO Ultra-Thin LLM Module with Narrative Guardrails

Token-Optimized Architecture with Planet Drift Prevention:
- Single LLM call per user message
- LLM acts as WRITER only, not reasoner
- STRICT: Only allowed_planets can be mentioned in narrative
- All logic (topic detection, scoring, driver selection) done in backend
- Minimal prompt: user_question + 3 drivers + time_context + allowed_entities
- Trust widget rendered from backend data only
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# ============================================================================
# NARRATIVE GUARDRAIL SYSTEM PROMPT - NATURAL CONVERSATIONAL FORMAT
# ============================================================================

GUARDRAIL_SYSTEM_PROMPT = """You are NIRO, a direct and grounded astrology guide. You have a natural conversation with users.

═══════════════════════════════════════════════════════════════════════════════
QUESTION TYPE HANDLING (CRITICAL)
═══════════════════════════════════════════════════════════════════════════════

Different questions need different response styles:

**YES/NO QUESTIONS** (Should I...? Is it...? Will I...?)
→ Start with a clear stance: "Yes, this looks favorable" / "No, timing isn't ideal" / "It depends..."

**EXPLORATORY QUESTIONS** (What should I...? Which...? Where...? How...?)
→ DO NOT start with "Yes" - these need substantive answers
→ Start with the actual insight: "Looking at your chart, businesses involving communication or technology align well with..."
→ Or: "For your children's education, schools emphasizing creativity and practical skills would serve them best..."

**VAGUE/UNCLEAR QUESTIONS** (context missing, topic unclear)
→ Ask for clarity FIRST before attempting an answer
→ Example: "I'd love to help with that. Could you share a bit more about what aspect you're curious about?"
→ DO NOT force an answer by assuming topic from previous conversation

═══════════════════════════════════════════════════════════════════════════════
RESPONSE STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

1. LEAD WITH INSIGHT (1-3 lines)
   - For yes/no: Give the answer directly
   - For exploratory: Give the substantive insight immediately
   - For unclear: Ask for clarification

2. WHY THIS MAKES SENSE (1-2 short paragraphs)
   - Anchor to PRIMARY_DRIVERS — what in the chart supports this
   - Paragraph 2 (only if SECONDARY_TOPIC exists): Address the impact/tradeoff
   - Use natural language, not astro-jargon
   - Name placements only from ALLOWED_ENTITIES

3. PRACTICAL NEXT STEPS (3 bullets - NOT as a bulleted intro line)
   - Write "Here's what I'd suggest:" as a regular sentence, then start bullets
   - Concrete, actionable steps specific to their situation
   - Example: "Test the idea with a small pilot before full commitment"
   - NOT generic: "Trust your intuition" or "Follow your heart"

4. FOLLOW-UP INVITATION (1 line at the end)
   - Suggest what THEY can ask YOU next (not what you're asking them)
   - Frame as an offer of deeper exploration
   - GOOD: "Would you like to explore which timing windows look best for this?"
   - GOOD: "I can also look at which specific approaches suit your chart best - interested?"
   - BAD: "What type of business are you considering?" (this asks them, not offers)
   - BAD: "Tell me more about your goals" (this is interrogating, not offering)

═══════════════════════════════════════════════════════════════════════════════
HARD CONSTRAINTS
═══════════════════════════════════════════════════════════════════════════════

ENTITY RULES:
- You may ONLY mention planets, houses, dashas from ALLOWED_ENTITIES
- If tempted to mention something NOT in the list: rephrase without it
- Never substitute with another planet — describe the insight differently

TIME RULES:
- If TIME_CONTEXT = past: NO words like "ongoing", "current", "right now"
- If TIME_CONTEXT = future: Use "will likely", "may", "could" — not certainties
- If TIME_CONTEXT = present: Ground in "right now", "currently"

FORMATTING RULES:
- "Here's what I'd suggest:" is a SENTENCE, not a bullet point
- Bullets (•) come AFTER that sentence
- NO bullet on the "Here's what I'd suggest:" line itself

TONE RULES:
- Direct, not mystical
- Warm but not fluffy
- No "energies", "universe", "vibrations", "destiny"
- No filler phrases: "allows you to", "gives you the ability"

═══════════════════════════════════════════════════════════════════════════════
MULTI-TOPIC HANDLING
═══════════════════════════════════════════════════════════════════════════════

When SECONDARY_TOPIC is present:
1. Answer the primary question first
2. Explicitly address the secondary concern in paragraph 2
3. Include at least one action item related to the secondary topic

═══════════════════════════════════════════════════════════════════════════════
MEMORY & CONTEXT RULES (CRITICAL - avoid repetition)
═══════════════════════════════════════════════════════════════════════════════

If ESTABLISHED_FACTS or AVOID_REPEATING are provided:
- DO NOT restate facts/conclusions already listed in AVOID_REPEATING
- Only reference memory/prior context if directly relevant to current question
- Build on established facts, don't re-explain them
- If user asks same thing again, acknowledge briefly then add NEW insight

Example:
- AVOID_REPEATING: "Career looks favorable, Mercury supports communication"
- BAD: "Your career looks favorable because Mercury supports communication..."
- GOOD: "Building on what we discussed, the timing for action is also favorable..."

If unsure about something:
- Say so briefly ("The signals here aren't definitive...")
- Don't fill silence with vague astrology or generic traits
- Give safe, practical next steps anyway

═══════════════════════════════════════════════════════════════════════════════
UNCLEAR QUESTION HANDLING
═══════════════════════════════════════════════════════════════════════════════

If QUESTION_CLARITY = unclear:
- DO NOT force an answer using assumed topic
- Ask a gentle clarifying question instead
- Example: "I'd be happy to look into that. Are you asking about [topic A] or [topic B]?"
- Keep it brief and friendly, not interrogating

═══════════════════════════════════════════════════════════════════════════════
FORMAT (FOLLOW EXACTLY)
═══════════════════════════════════════════════════════════════════════════════

Write in flowing paragraphs with this EXACT structure:

[Lead insight - 1-3 sentences]

[Why paragraph 1 - explains the reasoning]

[Why paragraph 2 - only if secondary topic]

Here's what I'd suggest:
• First actionable step
• Second actionable step  
• Third actionable step

[Follow-up invitation - one sentence]

CRITICAL FORMATTING:
- "Here's what I'd suggest:" MUST be plain text, NOT a bullet point
- It goes on its OWN line, followed by bullets starting on the NEXT line
- WRONG: "• Here's what I'd suggest:"
- CORRECT: "Here's what I'd suggest:" (then bullets below)
- • Bullet 3
- [blank line]
- Follow-up invitation (one sentence)

Total length: 150-220 words (tight, complete, no padding)"""


# Non-astro response prompt (for questions that don't need chart reading)
NON_ASTRO_PROMPT = """You are NIRO, a helpful assistant. The user asked a non-astrology question.

Respond helpfully WITHOUT astrology framing:
- No chart references, no planets, no "your chart shows"
- Just answer like a knowledgeable, friendly person
- Keep it brief (2-3 sentences)
- Be warm but direct"""


# Planet name variations for validation
PLANET_NAMES = {
    'sun': ['sun', 'surya', 'solar'],
    'moon': ['moon', 'chandra', 'lunar'],
    'mars': ['mars', 'mangal', 'kuja', 'martian'],
    'mercury': ['mercury', 'budh', 'budha', 'mercurial'],
    'jupiter': ['jupiter', 'guru', 'brihaspati', 'jovian'],
    'venus': ['venus', 'shukra', 'venusian'],
    'saturn': ['saturn', 'shani', 'saturnian', 'saturnine'],
    'rahu': ['rahu', 'north node', 'dragon head'],
    'ketu': ['ketu', 'south node', 'dragon tail'],
}

# House references to detect
HOUSE_PATTERNS = [
    r'\b(1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th|11th|12th)\s+(house|bhava)\b',
    r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)\s+house\b',
    r'\bhouse\s+(1|2|3|4|5|6|7|8|9|10|11|12)\b',
    r'\b(ascendant|lagna|descendant|midheaven|ic)\b',
]

# Dasha patterns
DASHA_PATTERNS = [
    r'\b(mahadasha|antardasha|dasha|bhukti)\b',
    r'\b(\w+)\s+dasha\b',  # "Jupiter dasha", "Saturn dasha"
]


class NarrativeValidator:
    """Validates LLM output against allowed entities."""
    
    @classmethod
    def extract_mentioned_planets(cls, text: str) -> Set[str]:
        """Extract all planets mentioned in text."""
        text_lower = text.lower()
        mentioned = set()
        
        for canonical, variants in PLANET_NAMES.items():
            for variant in variants:
                # Use word boundaries to avoid false positives
                if re.search(rf'\b{re.escape(variant)}\b', text_lower):
                    mentioned.add(canonical)
                    break
        
        return mentioned
    
    @classmethod
    def extract_mentioned_houses(cls, text: str) -> Set[int]:
        """Extract all house numbers mentioned in text."""
        text_lower = text.lower()
        houses = set()
        
        # Numeric houses
        for match in re.finditer(r'\b(\d{1,2})(?:st|nd|rd|th)?\s*house', text_lower):
            num = int(match.group(1))
            if 1 <= num <= 12:
                houses.add(num)
        
        # Word houses
        word_to_num = {
            'first': 1, 'second': 2, 'third': 3, 'fourth': 4,
            'fifth': 5, 'sixth': 6, 'seventh': 7, 'eighth': 8,
            'ninth': 9, 'tenth': 10, 'eleventh': 11, 'twelfth': 12
        }
        for word, num in word_to_num.items():
            if re.search(rf'\b{word}\s+house\b', text_lower):
                houses.add(num)
        
        return houses
    
    @classmethod
    def validate_narrative(
        cls,
        text: str,
        allowed_planets: Set[str],
        allowed_houses: Set[int]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that narrative only mentions allowed entities.
        
        Returns:
            (is_valid, list_of_violations)
        """
        violations = []
        
        # Check planets
        mentioned_planets = cls.extract_mentioned_planets(text)
        disallowed_planets = mentioned_planets - allowed_planets
        
        if disallowed_planets:
            violations.append(f"Mentioned planets not in drivers: {disallowed_planets}")
        
        # Check houses (only if we have explicit house constraints)
        if allowed_houses:
            mentioned_houses = cls.extract_mentioned_houses(text)
            disallowed_houses = mentioned_houses - allowed_houses
            if disallowed_houses:
                violations.append(f"Mentioned houses not in drivers: {disallowed_houses}")
        
        return len(violations) == 0, violations
    
    @classmethod
    def soft_clean_response(cls, text: str, allowed_planets: Set[str]) -> str:
        """
        Attempt soft cleanup of obvious planet drift.
        Only removes clear violations, preserves sentence structure.
        """
        # This is a lightweight pass - not full regeneration
        # Just removes obvious "Planet X" references that slipped through
        
        mentioned = cls.extract_mentioned_planets(text)
        violations = mentioned - allowed_planets
        
        if not violations:
            return text
        
        cleaned = text
        for planet in violations:
            variants = PLANET_NAMES.get(planet, [planet])
            for variant in variants:
                # Remove "Planet influence" or "Planet's effect" type phrases
                # But preserve sentence structure
                patterns = [
                    rf'\b{variant}\'?s?\s+(influence|effect|energy|aspect|placement)\b',
                    rf'\b(the\s+)?{variant}\s+(is|brings|creates|shows)\b',
                ]
                for pattern in patterns:
                    cleaned = re.sub(pattern, 'this planetary energy', cleaned, flags=re.IGNORECASE)
        
        return cleaned


class NiroLLMModule:
    """Ultra-thin LLM module with narrative guardrails."""
    
    def __init__(self):
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        
        logger.info(f"NiroLLMModule initialized (guardrailed, single-call)")
    
    def generate_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response with narrative guardrails."""
        user_question = payload.get('user_question', '')
        
        # Check if conversational input
        if self._is_conversational_input(user_question):
            return self._handle_conversational(user_question)
        
        # Extract allowed entities from payload
        allowed_planets, allowed_houses = self._extract_allowed_entities(payload)
        
        # Build guardrailed prompt
        guardrail_prompt = self._build_guardrailed_prompt(payload, allowed_planets, allowed_houses)
        
        # Single LLM call
        raw_response = self._call_llm(guardrail_prompt)
        
        # Validate and soft-clean if needed
        is_valid, violations = NarrativeValidator.validate_narrative(
            raw_response, allowed_planets, allowed_houses
        )
        
        if not is_valid:
            logger.warning(f"[NARRATIVE_DRIFT] Violations detected: {violations}")
            # Soft clean - don't regenerate, just patch obvious issues
            raw_response = NarrativeValidator.soft_clean_response(raw_response, allowed_planets)
        
        # Fix formatting issues regardless of validation
        raw_response = self._fix_formatting(raw_response)
        
        return {
            'rawText': raw_response,
            'summary': '',
            'reasons': [],  # Backend fills from reading_pack.drivers
            'remedies': [],
            '_narrative_validation': {
                'is_valid': is_valid,
                'violations': violations,
                'allowed_planets': list(allowed_planets),
            }
        }
    
    def _fix_formatting(self, text: str) -> str:
        """Fix common formatting issues in LLM output."""
        import re
        
        # Fix bulleted "Here's what I'd suggest:" - remove bullet before it
        text = re.sub(r'[•\-\*]\s*(Here\'s what I\'d suggest:?)', r'\n\1', text, flags=re.IGNORECASE)
        text = re.sub(r'[•\-\*]\s*(What I\'d suggest:?)', r'\nHere\'s what I\'d suggest:', text, flags=re.IGNORECASE)
        
        # Ensure "Here's what I'd suggest:" is on its own line
        text = re.sub(r'([.!?])\s*(Here\'s what I\'d suggest:?)', r'\1\n\n\2', text, flags=re.IGNORECASE)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _extract_allowed_entities(self, payload: Dict[str, Any]) -> Tuple[Set[str], Set[int]]:
        """Extract allowed planets and houses from reading_pack."""
        reading_pack = payload.get('reading_pack', {})
        drivers = reading_pack.get('drivers', [])
        signals = reading_pack.get('signals', [])[:6]  # Include secondary context
        
        allowed_planets = set()
        allowed_houses = set()
        
        # From drivers (PRIMARY)
        for d in drivers:
            planet = d.get('planet', '')
            if planet:
                allowed_planets.add(planet.lower())
            
            house = d.get('house')
            if house and isinstance(house, int):
                allowed_houses.add(house)
            
            # Extract from evidence/claim
            claim = d.get('claim', '').lower()
            for canonical in PLANET_NAMES.keys():
                if canonical in claim:
                    allowed_planets.add(canonical)
        
        # From secondary signals
        for s in signals:
            planet = s.get('planet', '')
            if planet:
                allowed_planets.add(planet.lower())
            
            house = s.get('house')
            if house and isinstance(house, int):
                allowed_houses.add(house)
        
        # Always allow Ascendant/Lagna references (structural, not a planet)
        # Don't add planets not in drivers/signals
        
        logger.debug(f"[ALLOWED_ENTITIES] planets={allowed_planets}, houses={allowed_houses}")
        return allowed_planets, allowed_houses
    
    def _build_guardrailed_prompt(
        self, 
        payload: Dict[str, Any],
        allowed_planets: Set[str],
        allowed_houses: Set[int]
    ) -> str:
        """Build prompt with answer-first format, multi-topic support, and memory context."""
        user_question = payload.get('user_question', '')
        reading_pack = payload.get('reading_pack', {})
        time_context = payload.get('time_context', 'present')
        topic = payload.get('topic', 'general')
        question_type = payload.get('question_type', 'general')
        memory_context = payload.get('memory_context', {})  # NEW: Memory context
        
        # Check for multi-topic setup
        primary_topic = reading_pack.get('primary_topic', topic)
        secondary_topics = reading_pack.get('secondary_topics', [])
        secondary_dropped = reading_pack.get('secondary_dropped', False)
        
        # Extract primary drivers - max 3, human readable with topic tags
        primary_drivers_list = reading_pack.get('primary_drivers', reading_pack.get('drivers', []))[:3]
        primary_drivers = []
        for d in primary_drivers_list:
            text = d.get('text_human') or d.get('claim', '')
            planet = d.get('planet', '')
            topic_tag = d.get('topic_tag', primary_topic)
            if text:
                primary_drivers.append(f"• [{topic_tag.upper()}] {text}")
            elif planet:
                primary_drivers.append(f"• [{topic_tag.upper()}] {planet} influence is significant")
        
        # Extract secondary drivers (for multi-topic questions)
        secondary_drivers_list = reading_pack.get('secondary_drivers', [])[:2]
        secondary_drivers = []
        for d in secondary_drivers_list:
            text = d.get('text_human') or d.get('claim', '')
            planet = d.get('planet', '')
            topic_tag = d.get('topic_tag', secondary_topics[0] if secondary_topics else 'secondary')
            if text:
                secondary_drivers.append(f"• [{topic_tag.upper()}] {text}")
            elif planet:
                secondary_drivers.append(f"• [{topic_tag.upper()}] {planet} influence")
        
        # Build the ALLOWED_ENTITIES list explicitly
        entities_list = sorted(allowed_planets) if allowed_planets else ['general planetary energies']
        entities_str = ', '.join(entities_list)
        
        # Time context label
        time_label = {
            'past': 'PAST (no "current/ongoing" language)',
            'future': 'FUTURE (use "likely/may/could")',
            'present': 'PRESENT (ground in "now/currently")',
            'timeless': 'GENERAL GUIDANCE'
        }.get(time_context, 'PRESENT')
        
        # Question type guidance and response style
        question_type_info = self._classify_question_style(user_question)
        response_style = question_type_info['style']
        is_exploratory = question_type_info['is_exploratory']
        is_unclear = question_type_info['is_unclear']
        
        # Construct prompt
        prompt_parts = [
            f"ALLOWED_ENTITIES (ONLY these): {entities_str}",
            f"TIME_CONTEXT: {time_label}",
        ]
        
        # ================================================================
        # MEMORY CONTEXT (NEW - avoid repetition)
        # ================================================================
        avoid_repeating = memory_context.get('avoid_repeating', [])
        confirmed_facts = memory_context.get('confirmed_facts', [])
        last_answer_summary = memory_context.get('last_ai_answer_summary', [])
        has_prior_context = memory_context.get('has_prior_context', False)
        
        if has_prior_context and (avoid_repeating or last_answer_summary):
            prompt_parts.append("\n══════════════════════════════════════════")
            prompt_parts.append("CONVERSATION MEMORY (do NOT repeat these):")
            
            if last_answer_summary:
                prompt_parts.append("\nLAST ANSWER COVERED:")
                for item in last_answer_summary[:3]:
                    prompt_parts.append(f"• {item[:100]}")
            
            if avoid_repeating:
                prompt_parts.append("\nAVOID_REPEATING (already established):")
                for item in avoid_repeating[:5]:
                    prompt_parts.append(f"• {item[:80]}")
            
            prompt_parts.append("\n⚠️ Build on this context, don't repeat it.")
            prompt_parts.append("══════════════════════════════════════════")
        
        # Add question classification
        if is_unclear:
            prompt_parts.append("QUESTION_CLARITY: unclear (ask for clarification, don't force an answer)")
        elif is_exploratory:
            prompt_parts.append(f"QUESTION_STYLE: exploratory (DO NOT start with Yes/No - give substantive insight)")
            prompt_parts.append(f"RESPONSE_APPROACH: {response_style}")
        else:
            prompt_parts.append(f"QUESTION_STYLE: yes/no or direct (start with clear answer)")
            prompt_parts.append(f"RESPONSE_APPROACH: {response_style}")
        
        prompt_parts.extend([
            f"\n══════════════════════════════════════════",
            f"USER QUESTION: {user_question}",
            f"══════════════════════════════════════════",
        ])
        
        # Primary drivers section
        if primary_drivers:
            prompt_parts.append(f"\nPRIMARY_DRIVERS (anchor your reasoning to these):")
            prompt_parts.extend(primary_drivers)
        
        # Secondary topic section (for multi-topic questions)
        if secondary_topics and not secondary_dropped and secondary_drivers:
            prompt_parts.append(f"\nSECONDARY_TOPIC: {', '.join(secondary_topics)}")
            prompt_parts.append("SECONDARY_DRIVERS (address in paragraph 2):")
            prompt_parts.extend(secondary_drivers)
            prompt_parts.append("\n⚠️ You MUST address the secondary topic explicitly in your response.")
        elif secondary_topics and secondary_dropped:
            prompt_parts.append(f"\n[Note: Secondary topic '{secondary_topics[0]}' was requested but insufficient signals found. Focus on primary topic only.]")
        
        prompt_parts.append("\n══════════════════════════════════════════")
        prompt_parts.append("RESPONSE FORMAT REMINDERS:")
        
        if is_unclear:
            prompt_parts.append("→ Ask a brief, friendly clarifying question")
            prompt_parts.append("→ DO NOT force an answer with assumed topic")
        elif is_exploratory:
            prompt_parts.append("→ Start with the INSIGHT (not Yes/No)")
            prompt_parts.append("→ 'Here's what I'd suggest:' is a SENTENCE, not a bullet")
            prompt_parts.append("→ End with a follow-up offer (what they can ask you next)")
        else:
            prompt_parts.append("→ Lead with your answer (Yes/No/It depends)")
            prompt_parts.append("→ 'Here's what I'd suggest:' is a SENTENCE, not a bullet")
            prompt_parts.append("→ End with a follow-up offer (what they can ask you next)")
        
        prompt_parts.append("══════════════════════════════════════════")
        
        return "\n".join(prompt_parts)
    
    def _classify_question_style(self, question: str) -> dict:
        """
        Classify question to determine response style.
        
        Returns:
            {
                'style': str,  # Response approach guidance
                'is_exploratory': bool,  # True for What/Which/Where/How questions
                'is_unclear': bool,  # True if question lacks context
            }
        """
        q = question.lower().strip()
        
        # Check for unclear/vague questions
        unclear_patterns = [
            r'^(what|how|why)\s*\?*$',  # Single word questions
            r'^(tell me|explain|help)\s*$',
            r'^(it|this|that)\s*$',
        ]
        
        is_unclear = False
        for pattern in unclear_patterns:
            if re.match(pattern, q):
                is_unclear = True
                break
        
        # Also unclear if very short and lacks topic indicators
        if len(q.split()) <= 2 and not any(word in q for word in ['career', 'job', 'money', 'health', 'love', 'marriage', 'family', 'business']):
            is_unclear = True
        
        # Exploratory questions (What/Which/Where/How/Who)
        exploratory_patterns = [
            r'^what\s+(should|can|would|could|type|kind|business|career|job)',
            r'^which\s+',
            r'^where\s+(should|can|would)',
            r'^how\s+(should|can|do|would)',
            r'^who\s+',
            r'(what|which)\s+(type|kind|sort|area|field|business|career)',
            r'(ideas?|options?|suggestions?|recommendations?)',
        ]
        
        is_exploratory = False
        for pattern in exploratory_patterns:
            if re.search(pattern, q):
                is_exploratory = True
                break
        
        # Determine response style
        if is_unclear:
            style = "Ask for clarification before answering"
        elif is_exploratory:
            style = "Lead with specific insights/options from the chart"
        elif re.search(r'^(should|will|can|is|are|do|does|would|could)\s+', q):
            style = "Give clear yes/no/conditional answer first"
        else:
            style = "Provide balanced insight"
        
        return {
            'style': style,
            'is_exploratory': is_exploratory,
            'is_unclear': is_unclear
        }
    
    def _get_tone_guideline(self, topic: str, time_context: str) -> str:
        """Get one-sentence tone guideline."""
        tone_map = {
            'career': 'Be practical and encouraging about professional matters.',
            'money': 'Be grounded and realistic about financial matters.',
            'romantic_relationships': 'Be warm and empathetic about relationship matters.',
            'health_energy': 'Be caring and supportive about wellbeing.',
            'family': 'Be warm and understanding about family dynamics.',
            'education': 'Be encouraging about learning and growth.',
            'travel': 'Be enthusiastic about new experiences.',
            'spirituality': 'Be thoughtful and reflective.',
            'legal_disputes': 'Be measured and practical.',
            'general': 'Be warm and insightful.',
        }
        
        base_tone = tone_map.get(topic, 'Be warm and insightful.')
        
        if time_context == 'past':
            return f"{base_tone} Reflect gently on past experiences."
        elif time_context == 'future':
            return f"{base_tone} Be optimistic but grounded about possibilities."
        
        return base_tone
    
    def _is_conversational_input(self, text: str) -> bool:
        """Detect greetings and small talk."""
        if not text:
            return False
        
        msg = text.lower().strip()
        
        conversational = [
            'hi', 'hello', 'hey', 'howdy', 'yo',
            'thanks', 'thank you', 'thx',
            'ok', 'okay', 'got it', 'understood',
            'bye', 'goodbye', 'see you',
            'good morning', 'good afternoon', 'good evening',
            'how are you', "what's up", 'sup'
        ]
        
        for pattern in conversational:
            if msg == pattern or msg.startswith(pattern + ' ') or msg.startswith(pattern + '!') or msg.startswith(pattern + '?'):
                return True
        
        if len(msg.split()) <= 3:
            astro_words = ['birth', 'chart', 'planet', 'career', 'job', 'marriage', 'health', 'money', 'when', 'will', 'should']
            if not any(w in msg for w in astro_words):
                return True
        
        return False
    
    def _handle_conversational(self, text: str) -> Dict[str, Any]:
        """Handle greetings/small talk with minimal LLM call."""
        msg = text.lower().strip()
        
        if msg in ('hi', 'hello', 'hey'):
            return {
                'rawText': "Hey! Great to have you here. What's on your mind today - career, relationships, timing for something important?",
                'summary': '',
                'reasons': [],
                'remedies': []
            }
        
        if msg.startswith('thank'):
            return {
                'rawText': "You're welcome! Anything else you'd like to explore?",
                'summary': '',
                'reasons': [],
                'remedies': []
            }
        
        if msg in ('ok', 'okay', 'got it'):
            return {
                'rawText': "Great! What would you like to know more about?",
                'summary': '',
                'reasons': [],
                'remedies': []
            }
        
        if msg in ('bye', 'goodbye'):
            return {
                'rawText': "Take care! Come back anytime you need guidance.",
                'summary': '',
                'reasons': [],
                'remedies': []
            }
        
        prompt = f"User says: {text}\nRespond warmly and guide them to ask an astrology question. Keep it brief (1-2 sentences)."
        response = self._call_llm(prompt)
        
        return {
            'rawText': response,
            'summary': '',
            'reasons': [],
            'remedies': []
        }
    
    def _call_llm(self, user_prompt: str) -> str:
        """Single LLM call with guardrailed system prompt."""
        
        prompt_size = len(GUARDRAIL_SYSTEM_PROMPT) + len(user_prompt)
        logger.info(f"[LLM CALL] prompt_size={prompt_size} chars")
        
        # Try OpenAI first (default/primary)
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": GUARDRAIL_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                
                content = response.choices[0].message.content
                logger.info(f"[LLM RESPONSE] model=gpt-4o-mini (OpenAI direct) length={len(content)}")
                return self._clean_response(content)
                
            except Exception as e:
                logger.error(f"OpenAI failed: {e}")
        
        # Fallback to Emergent LLM key
        if self.emergent_key:
            try:
                import asyncio
                import nest_asyncio
                from emergentintegrations.llm.chat import LlmChat, UserMessage
                
                nest_asyncio.apply()
                
                chat = LlmChat(
                    api_key=self.emergent_key,
                    session_id="niro-guardrailed",
                    system_message=GUARDRAIL_SYSTEM_PROMPT
                )
                
                chat.with_model("openai", "gpt-4o-mini")
                
                user_message = UserMessage(text=user_prompt)
                
                try:
                    loop = asyncio.get_running_loop()
                    response_text = loop.run_until_complete(chat.send_message(user_message))
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        response_text = loop.run_until_complete(chat.send_message(user_message))
                    finally:
                        loop.close()
                
                logger.info(f"[LLM RESPONSE] model=gpt-4o-mini (Emergent) length={len(response_text)}")
                return self._clean_response(response_text)
                
            except Exception as e:
                logger.error(f"Emergent LLM failed: {e}")
        
        # Fallback to Gemini
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                full_prompt = f"{GUARDRAIL_SYSTEM_PROMPT}\n\n{user_prompt}"
                response = model.generate_content(full_prompt)
                
                logger.info(f"[LLM RESPONSE] model=gemini-flash length={len(response.text)}")
                return self._clean_response(response.text)
                
            except Exception as e:
                logger.error(f"Gemini failed: {e}")
        
        return "I'd love to help you with that. Could you tell me a bit more about what's on your mind?"
    
    def _clean_response(self, text: str) -> str:
        """Clean up LLM response."""
        # Remove markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Remove rawText: prefix
        text = re.sub(r'^rawText:\s*', '', text, flags=re.IGNORECASE)
        
        # Remove signal IDs
        text = re.sub(r'\[S\d+\]', '', text)
        
        # Remove section headers
        text = re.sub(r'^(reasons|remedies|data_gaps|summary):\s*.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Clean multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()


# ============================================================================
# MODULE INTERFACE
# ============================================================================

_niro_llm: Optional[NiroLLMModule] = None

def get_niro_llm() -> NiroLLMModule:
    """Get or create the NIRO LLM instance."""
    global _niro_llm
    if _niro_llm is None:
        _niro_llm = NiroLLMModule()
    return _niro_llm


def call_niro_llm(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for calling NIRO LLM."""
    llm = get_niro_llm()
    return llm.generate_response(payload)
