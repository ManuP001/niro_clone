"""
WelcomeMessageBuilder - Dedicated Welcome Message Generator

Creates high-trust, chart-anchored, confidence-aware personalized welcome messages.
This is a SINGLE-MESSAGE experience shown immediately after onboarding.

Key Design Principles:
- Does NOT reuse the normal chat generation flow
- Uses LLM as WRITER only (not reasoner)
- Pre-computes all insights with confidence levels
- Skips sections when confidence is LOW
- Silence is better than generic astrology

Strict Content Structure:
A. Introduction (fixed)
B. Personality Insight (Moon sign + Ascendant + Lagna lord)
C. Past Pattern (only if confidence ≥ threshold)
D. Current Life Phase (Mahadasha/Antardasha)
E. Closing Prompt (fixed)

Output: ≤180 words, zero questions to user
"""

import os
import re
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIDENCE LEVELS
# ============================================================================

class ConfidenceLevel(str, Enum):
    HIGH = "high"       # Include with full detail
    MEDIUM = "medium"   # Include with hedged language
    LOW = "low"         # SKIP entirely


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class WelcomeInput:
    """Minimal input contract to LLM."""
    first_name: str
    personality_summary: Optional[str] = None  # Pre-computed, 2-3 signals max
    past_theme: Optional[str] = None           # Already confidence-filtered
    current_phase_insight: Optional[str] = None  # Already confidence-filtered
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "first_name": self.first_name,
            "personality_summary": self.personality_summary,
            "past_theme": self.past_theme,
            "current_phase_insight": self.current_phase_insight
        }


@dataclass  
class WelcomeOutput:
    """Output from welcome message generation."""
    welcome_message: str
    confidence_map: Dict[str, Optional[str]]
    word_count: int
    sections_included: List[str]


# ============================================================================
# ASTROLOGICAL MAPPINGS (for pre-computation)
# Designed for natural, conversational, trust-building welcome messages
# ============================================================================

# Moon Sign -> Natural language insight + "the hook" (something uncomfortably accurate)
MOON_SIGN_DATA = {
    "Aries": {
        "insight": "you process life through action—when something feels off, your instinct is to move, not wait",
        "hook": "sitting with uncertainty drives you a little crazy"
    },
    "Taurus": {
        "insight": "you need time to settle into changes before you can truly accept them",
        "hook": "you've probably held onto things longer than you should, just because letting go felt like losing"
    },
    "Gemini": {
        "insight": "you think out loud—you don't fully know what you believe until you've said it or written it down",
        "hook": "your mind is restless, always pulling threads, connecting things others wouldn't"
    },
    "Cancer": {
        "insight": "you feel things before you understand them—emotions arrive first, logic follows",
        "hook": "you remember how things felt long after others have forgotten they happened"
    },
    "Leo": {
        "insight": "you understand yourself through what you create and how others respond to your presence",
        "hook": "not being seen—really seen—quietly bothers you more than you'd admit"
    },
    "Virgo": {
        "insight": "you make sense of life by breaking things down, looking for patterns and practical fixes",
        "hook": "you're harder on yourself than anyone else would ever be"
    },
    "Libra": {
        "insight": "you understand yourself through your relationships—others mirror back what you need to see",
        "hook": "making decisions alone feels harder than it probably should"
    },
    "Scorpio": {
        "insight": "you process life at depth—you need to transform experiences before you can release them",
        "hook": "you've never quite trusted surface-level explanations for anything"
    },
    "Sagittarius": {
        "insight": "you make sense of life by finding meaning—every experience needs a 'why' to feel complete",
        "hook": "routine without purpose slowly suffocates you"
    },
    "Capricorn": {
        "insight": "you process life through structure and progress—achievement helps you feel grounded",
        "hook": "you've carried responsibility since before it was fair to ask you to"
    },
    "Aquarius": {
        "insight": "you see your own life from a distance, as part of something larger",
        "hook": "you've felt like an outsider in rooms where you technically belonged"
    },
    "Pisces": {
        "insight": "you absorb experiences deeply, often needing time alone to sort what's yours from what isn't",
        "hook": "you've felt other people's emotions and mistaken them for your own"
    }
}

# Ascendant -> How they meet the world (natural phrasing for weaving in)
ASCENDANT_DATA = {
    "Aries": {
        "style": "directness—you meet life head-on",
        "gives": "an openness that people trust, though it also means you sometimes start things before thinking them through"
    },
    "Taurus": {
        "style": "patience and steadiness",
        "gives": "a grounded presence others find calming, though change doesn't come easy"
    },
    "Gemini": {
        "style": "curiosity and mental quickness",
        "gives": "an adaptability that serves you well, though it can scatter your focus"
    },
    "Cancer": {
        "style": "emotional intelligence and protective instincts",
        "gives": "a warmth people feel safe around, though you guard your own vulnerabilities carefully"
    },
    "Leo": {
        "style": "natural warmth and quiet confidence",
        "gives": "a presence that draws people in, though you feel the weight of their expectations"
    },
    "Virgo": {
        "style": "careful attention and practical helpfulness",
        "gives": "a reliability people depend on, though you notice flaws others would miss"
    },
    "Libra": {
        "style": "grace and a natural sense of balance",
        "gives": "a diplomatic ease in social situations, though you can lose yourself trying to keep everyone happy"
    },
    "Scorpio": {
        "style": "intensity and strategic awareness",
        "gives": "a perceptiveness that sees through surface, though you don't reveal yourself easily"
    },
    "Sagittarius": {
        "style": "openness and philosophical optimism",
        "gives": "an enthusiasm that's contagious, though you sometimes scatter your attention across too many directions"
    },
    "Capricorn": {
        "style": "patience and long-term thinking",
        "gives": "an ambition that builds lasting things, though you can be too hard on yourself along the way"
    },
    "Aquarius": {
        "style": "independence and original thinking",
        "gives": "a perspective that's genuinely different, though you can feel disconnected from the crowd"
    },
    "Pisces": {
        "style": "intuitive sensitivity and imagination",
        "gives": "a creative depth others admire, though boundaries don't come naturally"
    }
}

# Mahadasha -> Current phase (actionable, direct language)
MAHADASHA_DATA = {
    "Sun": {
        "entered": "a Sun period",
        "sharp": "Your sense of self is clearer now—this is a time to lead, not follow",
        "trap": "The only trap? Ego battles. Let your work speak."
    },
    "Moon": {
        "entered": "a Moon period",
        "sharp": "Your emotional world is front and center—trust what you feel, even when it doesn't make logical sense",
        "trap": "The trap here is reactivity. Not every feeling needs immediate action."
    },
    "Mars": {
        "entered": "a Mars period",
        "sharp": "Your drive is up—this is a time for bold moves, competition, physical energy",
        "trap": "The trap? Impulsiveness. Count to ten before major decisions."
    },
    "Mercury": {
        "entered": "a Mercury period",
        "sharp": "Your mind is sharper than usual—writing, learning, speaking all flow more easily",
        "trap": "The only trap? Overthinking. Sometimes done is better than perfect."
    },
    "Jupiter": {
        "entered": "a Jupiter period",
        "sharp": "Opportunities tend to find you now—growth, expansion, taking calculated risks",
        "trap": "The trap is overcommitment. Say yes to the right things, not everything."
    },
    "Venus": {
        "entered": "a Venus period",
        "sharp": "Relationships and creative work flow naturally—collaboration over competition",
        "trap": "The trap? Comfort becoming complacency. Don't let ease make you passive."
    },
    "Saturn": {
        "entered": "a Saturn period",
        "sharp": "This is a slow-build phase—consistent effort, responsibility, foundations that last",
        "trap": "The trap is frustration with the pace. This isn't a quick-wins period."
    },
    "Rahu": {
        "entered": "a Rahu period",
        "sharp": "Something is pushing you toward new experiences, unconventional paths, worldly ambitions",
        "trap": "The trap is obsession. Stay aware of what you're really chasing."
    },
    "Ketu": {
        "entered": "a Ketu period",
        "sharp": "This phase pulls you inward—letting go, simplifying, spiritual depth",
        "trap": "The trap is too much detachment. Some withdrawal is healthy; isolation isn't."
    }
}

# Sign to Lord mapping
SIGN_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
    'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

# Sign to Lord mapping
SIGN_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
    'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}


# ============================================================================
# WELCOME MESSAGE BUILDER
# ============================================================================

class WelcomeMessageBuilder:
    """
    Builds high-trust, confidence-aware welcome messages.
    
    Does NOT reuse normal chat flow - dedicated single-purpose generator.
    """
    
    def __init__(self):
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        
        # Confidence thresholds
        self.PERSONALITY_THRESHOLD = ConfidenceLevel.MEDIUM  # Need at least medium
        self.PAST_THRESHOLD = ConfidenceLevel.HIGH           # Only include if high
        self.PHASE_THRESHOLD = ConfidenceLevel.MEDIUM        # Need at least medium
        
        logger.info("[WELCOME_BUILDER] Initialized")
    
    def build(
        self,
        first_name: str,
        astro_profile: Dict[str, Any],
        signals: Optional[List[Dict[str, Any]]] = None
    ) -> WelcomeOutput:
        """
        Build a personalized welcome message.
        
        Objectives:
        1. RECOGNITION: Make them feel "this system knows me"
        2. WELCOME: Invite them into conversation, not hand them a report
        3. TRUST: Name real chart placements confidently
        4. INTRIGUE: Drop one insight that makes them want more
        """
        logger.info(f"[WELCOME_BUILDER] Building welcome for {first_name}")
        
        # Step 1: Extract and assess confidence for each section
        personality_data = self._assess_personality(astro_profile)
        past_data = self._assess_past_pattern(signals)
        phase_data = self._assess_current_phase(astro_profile)
        
        # Step 2: Build structured input for LLM
        llm_input = {
            "first_name": first_name,
            "personality": personality_data.get('chart_data') if personality_data['confidence'] != ConfidenceLevel.LOW else None,
            "current_phase": phase_data.get('phase_data') if phase_data['confidence'] != ConfidenceLevel.LOW else None,
        }
        
        # Step 3: Generate message via LLM
        message = self._generate_with_llm(llm_input)
        
        # Step 4: Validate output
        message = self._validate_and_clean(message)
        
        # Build confidence map
        confidence_map = {
            "personality": personality_data['confidence'].value if personality_data['confidence'] != ConfidenceLevel.LOW else None,
            "past_theme": past_data['confidence'].value if past_data['confidence'] == ConfidenceLevel.HIGH else None,
            "current_phase": phase_data['confidence'].value if phase_data['confidence'] != ConfidenceLevel.LOW else None
        }
        
        # Track which sections were included
        sections_included = ["introduction", "closing"]
        if llm_input["personality"]:
            sections_included.append("personality")
        if llm_input["current_phase"]:
            sections_included.append("current_phase")
        
        word_count = len(message.split())
        
        logger.info(f"[WELCOME_BUILDER] Generated {word_count} words, sections: {sections_included}")
        
        return WelcomeOutput(
            welcome_message=message,
            confidence_map=confidence_map,
            word_count=word_count,
            sections_included=sections_included
        )
    
    def _assess_personality(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess personality insight confidence and build chart-anchored data.
        
        Returns structured data for LLM including:
        - Moon sign insight + hook
        - Ascendant style + shadow
        - Confidence level
        """
        moon_sign = profile.get('moon_sign', '')
        ascendant = profile.get('ascendant', '')
        
        # Normalize sign names
        moon_sign = self._normalize_sign(moon_sign)
        ascendant = self._normalize_sign(ascendant)
        
        has_moon = moon_sign and moon_sign in MOON_SIGN_DATA
        has_asc = ascendant and ascendant in ASCENDANT_DATA
        
        # Determine confidence
        if has_moon and has_asc:
            confidence = ConfidenceLevel.HIGH
        elif has_moon or has_asc:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW
            return {"confidence": confidence, "chart_data": None}
        
        # Build chart data for LLM (structured, not pre-written prose)
        chart_data = {
            "moon_sign": moon_sign if has_moon else None,
            "moon_insight": MOON_SIGN_DATA[moon_sign]["insight"] if has_moon else None,
            "moon_hook": MOON_SIGN_DATA[moon_sign]["hook"] if has_moon else None,
            "ascendant": ascendant if has_asc else None,
            "asc_style": ASCENDANT_DATA[ascendant]["style"] if has_asc else None,
            "asc_gives": ASCENDANT_DATA[ascendant]["gives"] if has_asc else None,
        }
        
        logger.info(f"[WELCOME_BUILDER] Personality: {confidence.value}, moon={moon_sign}, asc={ascendant}")
        
        return {
            "confidence": confidence,
            "chart_data": chart_data,
            "moon_sign": moon_sign,
            "ascendant": ascendant
        }
    
    def _assess_past_pattern(self, signals: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Assess past pattern confidence.
        
        For now, we skip past patterns entirely because:
        1. We need full dasha timeline to validate completed periods
        2. Making claims about the past without validation risks trust
        
        This can be enhanced later with proper timeline analysis.
        """
        # For MVP: Always return LOW confidence to skip this section
        # Future enhancement: Analyze completed dasha periods
        
        return {
            "confidence": ConfidenceLevel.LOW,
            "theme": None
        }
    
    def _assess_current_phase(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess current life phase insight based on Mahadasha.
        
        Returns structured data for LLM with actionable, direct language.
        """
        mahadasha = profile.get('current_mahadasha', {})
        
        # Handle DashaInfo objects
        if hasattr(mahadasha, 'model_dump'):
            mahadasha = mahadasha.model_dump()
        
        maha_planet = mahadasha.get('planet', '') if mahadasha else ''
        
        if not maha_planet or maha_planet not in MAHADASHA_DATA:
            return {"confidence": ConfidenceLevel.LOW, "phase_data": None}
        
        # Check dasha timing
        years_elapsed = mahadasha.get('years_elapsed', 0)
        years_total = mahadasha.get('years_total', 1)
        
        if years_total <= 0:
            return {"confidence": ConfidenceLevel.LOW, "phase_data": None}
        
        elapsed_pct = (years_elapsed / years_total) * 100
        
        # Determine confidence and timing language
        if elapsed_pct < 10:
            confidence = ConfidenceLevel.HIGH
            timing = "just entered"
        elif elapsed_pct > 85:
            confidence = ConfidenceLevel.MEDIUM
            timing = "in the final stretch of"
        else:
            confidence = ConfidenceLevel.HIGH
            timing = "in"
        
        phase_info = MAHADASHA_DATA[maha_planet]
        
        phase_data = {
            "planet": maha_planet,
            "timing": timing,
            "period_name": phase_info["entered"],
            "sharp": phase_info["sharp"],
            "trap": phase_info["trap"],
            "elapsed_pct": elapsed_pct
        }
        
        logger.info(f"[WELCOME_BUILDER] Current phase: {confidence.value}, planet={maha_planet}, elapsed={elapsed_pct:.1f}%")
        
        return {
            "confidence": confidence,
            "phase_data": phase_data,
            "planet": maha_planet
        }
    
    def _generate_with_llm(self, llm_input: Dict[str, Any]) -> str:
        """
        Generate the welcome message using LLM.
        
        The LLM receives structured chart data and writes a flowing, natural message.
        """
        # Build the prompt
        prompt = self._build_llm_prompt(llm_input)
        
        # Call LLM
        response = self._call_llm(prompt)
        
        return response
    
    def _build_llm_prompt(self, llm_input: Dict[str, Any]) -> str:
        """
        Build the LLM prompt designed for natural, trust-building welcome messages.
        
        Objectives:
        1. RECOGNITION: Make them feel "this system knows me"
        2. WELCOME: Invite into conversation, not hand a report
        3. TRUST: Name chart placements confidently
        4. INTRIGUE: One insight that makes them want more
        """
        
        system_prompt = """You are Niro, a trained AI astrologer writing a welcome message to someone whose chart you've just studied.

OBJECTIVES (what this message must achieve):
1. RECOGNITION: Make them feel "this system actually knows me" — be specific, not generic
2. WELCOME: Make them feel invited into a conversation, not handed a report
3. TRUST: Establish credibility by naming real chart placements confidently
4. INTRIGUE: Drop one insight that makes them think "wait, how did it know that?" — leave them wanting more

VOICE & TONE:
- You're a thoughtful friend who happens to know astrology deeply
- Speak naturally, like you're sitting across from them
- Be specific, not flattering. Say what you actually see.
- Confident but not mystical. No "energies", no "universe", no fluff.
- Slightly warm, but not overly enthusiastic

STRUCTURE (flow naturally, but with mobile-friendly breaks):
1. Open: "Welcome, {name}. I'm Niro, a trained AI astrologer." [LINE BREAK AFTER THIS]
2. Bridge into chart: "I've looked at your chart..." or "A few things stood out..."
3. Personality insight: Name placements naturally ("That Gemini Moon...", "With Sagittarius rising..."). Describe HOW they experience life — something they'd recognize in themselves.
4. The hook: One specific insight or tension that feels personal — something that makes them pause and think "yes, that's me" [LINE BREAK AFTER PERSONALITY SECTION]
5. Current phase: If provided, weave in naturally. Be actionable, not abstract.
6. Invitation: "What would you like to explore today?" — feels like an open door, not a form field

RULES:
- Write as ONE flowing piece BUT with paragraph breaks for mobile readability
- Structure: Intro (1 line) → Personality (1 short para) → Phase (1 short para) → Closing
- Each paragraph should be 2-4 sentences max
- NAME the Moon sign and Ascendant naturally — this builds trust
- Use everyday language: "you think out loud" not "you process by articulating"
- Include ONE line that feels uncomfortably accurate (the hook)
- Cut ALL filler: "sense of growth", "broader perspective", "embrace experiences", "allows you to"
- Be direct about current phase: "Your mind is sharp" not "highlights learning"
- Total: 90-140 words (tight, warm, specific)

WHAT NOT TO DO:
- Don't write boxed sections that feel like a template
- Don't use connector phrases: "combined with", "this allows you to", "which means"
- Don't repeat yourself or pad with synonyms
- Don't sound like a horoscope column or self-help book
- Don't over-explain — let the insight land
- Don't be vague — vague kills trust"""

        # Build the user prompt with chart data
        user_parts = [f"FIRST_NAME: {llm_input['first_name']}"]
        
        personality = llm_input.get('personality')
        if personality:
            user_parts.append(f"""
CHART_DATA:
- Moon Sign: {personality.get('moon_sign', 'Unknown')}
- Ascendant: {personality.get('ascendant', 'Unknown')}

PERSONALITY_INSIGHT (weave naturally, name the placements):
- Core: {personality.get('moon_insight', '')}
- The Hook (use this — it should land): {personality.get('moon_hook', '')}
- Ascendant gives: {personality.get('asc_gives', '')}""")
        else:
            user_parts.append("\nPERSONALITY: [Skip - no confident data]")
        
        phase = llm_input.get('current_phase')
        if phase:
            user_parts.append(f"""
CURRENT_PHASE:
- Period: {phase.get('period_name', '')} ({phase.get('timing', 'in')} this phase)
- What's sharp: {phase.get('sharp', '')}
- The trap: {phase.get('trap', '')}""")
        else:
            user_parts.append("\nCURRENT_PHASE: [Skip - no confident data]")
        
        user_parts.append("\nNow write the welcome message. Flow naturally. Make it feel personal.")
        
        return system_prompt + "\n\n---\n\n" + "\n".join(user_parts)
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with the welcome prompt."""
        
        logger.info(f"[WELCOME_BUILDER] Calling LLM, prompt size: {len(prompt)} chars")
        
        # Try OpenAI first
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=400
                )
                
                content = response.choices[0].message.content
                logger.info(f"[WELCOME_BUILDER] OpenAI response: {len(content)} chars")
                return content.strip()
                
            except Exception as e:
                logger.error(f"[WELCOME_BUILDER] OpenAI failed: {e}")
        
        # Try Emergent LLM
        if self.emergent_key:
            try:
                import asyncio
                import nest_asyncio
                from emergentintegrations.llm.chat import LlmChat, UserMessage
                
                nest_asyncio.apply()
                
                chat = LlmChat(
                    api_key=self.emergent_key,
                    session_id="welcome-builder"
                )
                chat.with_model("openai", "gpt-4o-mini")
                
                user_message = UserMessage(text=prompt)
                
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
                
                logger.info(f"[WELCOME_BUILDER] Emergent response: {len(response_text)} chars")
                return response_text.strip()
                
            except Exception as e:
                logger.error(f"[WELCOME_BUILDER] Emergent LLM failed: {e}")
        
        # Try Gemini
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                response = model.generate_content(prompt)
                logger.info(f"[WELCOME_BUILDER] Gemini response: {len(response.text)} chars")
                return response.text.strip()
                
            except Exception as e:
                logger.error(f"[WELCOME_BUILDER] Gemini failed: {e}")
        
        # Fallback: Build a minimal message without LLM
        logger.warning("[WELCOME_BUILDER] No LLM available, using fallback")
        return self._build_fallback_message(llm_input.get('first_name', 'there') if isinstance(llm_input, dict) else "there")
    
    def _build_fallback_message(self, first_name: str) -> str:
        """Build a minimal safe message when LLM is unavailable."""
        return f"""Welcome, {first_name}. I'm Niro, a trained AI astrologer.

I've looked at your chart, and a few things stood out. I'm ready to explore what matters to you.

What would you like to explore today?"""
    
    def _validate_and_clean(self, message: str) -> str:
        """
        Validate and clean the generated message.
        
        Ensures:
        1. No markdown artifacts
        2. No forbidden filler words
        3. Proper closing question
        4. Clean formatting
        """
        # Remove any markdown formatting
        message = re.sub(r'^#+\s+', '', message, flags=re.MULTILINE)
        message = re.sub(r'\*\*(.*?)\*\*', r'\1', message)
        message = re.sub(r'\*(.*?)\*', r'\1', message)
        
        # Remove bullet points if any snuck through
        message = re.sub(r'^\s*[-•]\s+', '', message, flags=re.MULTILINE)
        
        # Clean multiple newlines
        message = re.sub(r'\n{3,}', '\n\n', message)
        
        # Check for forbidden spiritual/filler words
        forbidden = ['energy', 'vibes', 'destiny', 'universe', 'cosmic', 'celestial', 'stars say']
        for word in forbidden:
            if word.lower() in message.lower():
                logger.warning(f"[WELCOME_BUILDER] Forbidden word found: {word}")
        
        # Check for filler phrases that indicate robotic writing
        filler_phrases = [
            'allows you to', 'combined with', 'which means', 'this enables',
            'sense of growth', 'broader perspective', 'embrace experiences',
            'in this current phase', 'during this period'
        ]
        for phrase in filler_phrases:
            if phrase.lower() in message.lower():
                logger.warning(f"[WELCOME_BUILDER] Filler phrase detected: {phrase}")
        
        # Ensure proper closing
        if "What would you like to explore today?" not in message:
            if not message.endswith(('?', '.')):
                message += "."
            message += "\n\nWhat would you like to explore today?"
        
        # Clean up whitespace
        message = message.strip()
        message = re.sub(r' +', ' ', message)
        
        return message
    
    def _normalize_sign(self, sign: str) -> str:
        """Normalize zodiac sign name."""
        if not sign:
            return ""
        
        # Handle common variations
        sign_map = {
            'aries': 'Aries', 'taurus': 'Taurus', 'gemini': 'Gemini',
            'cancer': 'Cancer', 'leo': 'Leo', 'virgo': 'Virgo',
            'libra': 'Libra', 'scorpio': 'Scorpio', 'sagittarius': 'Sagittarius',
            'capricorn': 'Capricorn', 'aquarius': 'Aquarius', 'pisces': 'Pisces'
        }
        
        return sign_map.get(sign.lower().strip(), sign)


# ============================================================================
# MODULE INTERFACE
# ============================================================================

_builder: Optional[WelcomeMessageBuilder] = None


def get_welcome_builder() -> WelcomeMessageBuilder:
    """Get or create the WelcomeMessageBuilder instance."""
    global _builder
    if _builder is None:
        _builder = WelcomeMessageBuilder()
    return _builder


async def generate_welcome_message(
    first_name: str,
    astro_profile: Dict[str, Any],
    signals: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Main entry point for generating welcome messages.
    
    Args:
        first_name: User's first name
        astro_profile: Dict with chart data
        signals: Optional scored signals
    
    Returns:
        {
            "welcome_message": str,
            "confidence_map": {...},
            "word_count": int,
            "sections_included": [...]
        }
    """
    builder = get_welcome_builder()
    result = builder.build(first_name, astro_profile, signals)
    
    return {
        "welcome_message": result.welcome_message,
        "confidence_map": result.confidence_map,
        "word_count": result.word_count,
        "sections_included": result.sections_included
    }
