"""Intent Router for NIRO Chat

Classifies user messages into one of four intent categories:
- ASTRO_READING: Questions requiring astrological analysis
- PRODUCT_HELP: Questions about app features, bugs, payments
- GENERAL_ADVICE: Life advice not requiring astrology
- SMALL_TALK: Greetings, thanks, acknowledgments

Uses keyword heuristics (no LLM call) for fast, deterministic classification.
"""

from enum import Enum
from typing import Dict, Any, Set
import re
import logging

logger = logging.getLogger(__name__)


class UserIntent(str, Enum):
    """User intent categories for routing"""
    ASTRO_READING = "astro_reading"
    PRODUCT_HELP = "product_help"  
    GENERAL_ADVICE = "general_advice"
    SMALL_TALK = "small_talk"


# Astrological keywords that indicate ASTRO_READING intent
ASTRO_KEYWORDS: Set[str] = {
    # Core astrology terms
    "kundli", "kundali", "horoscope", "chart", "birth chart", "natal chart",
    "vedic", "jyotish", "astrology", "astrological",
    
    # Dasha terms
    "dasha", "mahadasha", "antardasha", "bhukti", "pratyantar",
    
    # Zodiac/houses
    "lagna", "ascendant", "moon sign", "sun sign", "rashi", "nakshatra",
    "house", "bhava", "1st house", "2nd house", "3rd house", "4th house",
    "5th house", "6th house", "7th house", "8th house", "9th house",
    "10th house", "11th house", "12th house",
    
    # Planets
    "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn",
    "rahu", "ketu", "mangal", "budh", "guru", "shukra", "shani",
    
    # Transits & movements
    "transit", "gochar", "sade sati", "retrograde",
    
    # Yogas & combinations
    "yoga", "raj yoga", "dhana yoga", "gaja kesari", "hamsa",
    
    # Matching/compatibility
    "manglik", "mangal dosha", "gun milan", "kundli matching",
    
    # Chart references
    "in my chart", "my chart", "as per astrology", "according to my chart",
    "my horoscope", "stars say", "planets indicate", "astrologically",
    
    # Time periods
    "planetary period", "current period", "dasha period",
}

# Product/app-related keywords that indicate PRODUCT_HELP intent
PRODUCT_KEYWORDS: Set[str] = {
    # App features
    "app", "application", "feature", "how to use", "how do i",
    "match tab", "report", "checklist", "dashboard", "profile",
    "settings", "account", "notification",
    
    # Technical issues  
    "bug", "error", "crash", "not working", "doesn't work", "broken",
    "fix", "issue", "problem", "glitch", "slow", "loading",
    
    # Account/auth
    "login", "logout", "sign in", "sign up", "register", "password",
    "otp", "verification", "email", "phone number",
    
    # Onboarding
    "onboarding", "setup", "getting started", "first time",
    
    # Payments
    "payment", "subscription", "plan", "upgrade", "premium",
    "refund", "billing", "price", "cost", "free", "paid",
    
    # Support
    "support", "help me with app", "contact", "feedback",
}

# Small talk patterns - greetings, acknowledgments, short responses
SMALL_TALK_PATTERNS: Set[str] = {
    # Greetings
    "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
    "howdy", "hola", "namaste", "namaskar",
    
    # Thanks
    "thanks", "thank you", "thx", "tysm", "appreciated", "grateful",
    
    # Acknowledgments
    "ok", "okay", "sure", "alright", "got it", "understood",
    "i see", "makes sense", "cool", "great", "nice", "good",
    
    # Farewells
    "bye", "goodbye", "see you", "take care", "later",
    
    # Affirmatives/negatives
    "yes", "yeah", "yep", "no", "nope", "not really",
    
    # Fillers
    "hmm", "uh", "um", "well",
}

# General life advice patterns (not specifically astrology)
GENERAL_ADVICE_INDICATORS: Set[str] = {
    "advice", "suggest", "recommendation", "opinion", "think",
    "what do you think", "your thoughts", "your opinion",
    "generally speaking", "in general", "life advice",
}


def classify_intent(user_message: str) -> Dict[str, Any]:
    """
    Classify the intent of a user message using keyword heuristics.
    
    Args:
        user_message: The user's raw message text
        
    Returns:
        Dict with:
        - intent: UserIntent enum value
        - confidence: float 0.0-1.0
        - matched_keywords: list of keywords that matched
        - reason: explanation for classification
    """
    if not user_message:
        return {
            "intent": UserIntent.SMALL_TALK,
            "confidence": 0.5,
            "matched_keywords": [],
            "reason": "Empty message"
        }
    
    msg_lower = user_message.lower().strip()
    msg_words = set(re.findall(r'\b\w+\b', msg_lower))
    
    # Count matches for each category
    astro_matches = []
    product_matches = []
    small_talk_matches = []
    general_matches = []
    
    # Check astro keywords (single words and phrases)
    for keyword in ASTRO_KEYWORDS:
        if ' ' in keyword:
            # Multi-word phrase
            if keyword in msg_lower:
                astro_matches.append(keyword)
        else:
            # Single word
            if keyword in msg_words:
                astro_matches.append(keyword)
    
    # Check product keywords
    for keyword in PRODUCT_KEYWORDS:
        if ' ' in keyword:
            if keyword in msg_lower:
                product_matches.append(keyword)
        else:
            if keyword in msg_words:
                product_matches.append(keyword)
    
    # Check small talk patterns (only for short messages)
    word_count = len(msg_words)
    if word_count <= 5:
        for pattern in SMALL_TALK_PATTERNS:
            if pattern in msg_lower or msg_lower.strip('?!.') == pattern:
                small_talk_matches.append(pattern)
    
    # Check general advice indicators
    for indicator in GENERAL_ADVICE_INDICATORS:
        if ' ' in indicator:
            if indicator in msg_lower:
                general_matches.append(indicator)
        else:
            if indicator in msg_words:
                general_matches.append(indicator)
    
    # Decision logic with priority
    # Priority 1: ASTRO_READING (any astrology mention)
    if astro_matches:
        confidence = min(0.95, 0.6 + 0.1 * len(astro_matches))
        return {
            "intent": UserIntent.ASTRO_READING,
            "confidence": confidence,
            "matched_keywords": astro_matches[:5],  # Top 5
            "reason": f"Astrology keywords detected: {', '.join(astro_matches[:3])}"
        }
    
    # Priority 2: PRODUCT_HELP (app/technical issues)
    if product_matches:
        confidence = min(0.90, 0.6 + 0.1 * len(product_matches))
        return {
            "intent": UserIntent.PRODUCT_HELP,
            "confidence": confidence,
            "matched_keywords": product_matches[:5],
            "reason": f"Product/app keywords detected: {', '.join(product_matches[:3])}"
        }
    
    # Priority 3: SMALL_TALK (short, generic messages)
    if small_talk_matches and word_count <= 5 and not general_matches:
        confidence = min(0.85, 0.5 + 0.15 * len(small_talk_matches))
        return {
            "intent": UserIntent.SMALL_TALK,
            "confidence": confidence,
            "matched_keywords": small_talk_matches[:3],
            "reason": f"Short message with small talk pattern: '{msg_lower[:30]}'"
        }
    
    # Priority 4: GENERAL_ADVICE (non-astro life questions)
    # This is the fallback for most questions that don't mention astrology
    if general_matches:
        confidence = min(0.75, 0.5 + 0.1 * len(general_matches))
        return {
            "intent": UserIntent.GENERAL_ADVICE,
            "confidence": confidence,
            "matched_keywords": general_matches[:3],
            "reason": f"General advice indicators: {', '.join(general_matches[:3])}"
        }
    
    # Default: If message is a question/substantive, treat as ASTRO_READING
    # Since NIRO is an astrology app, assume astro intent for substantive queries
    question_words = {'what', 'when', 'why', 'how', 'will', 'should', 'can', 'is', 'are', 'do', 'does'}
    topic_words = {'career', 'job', 'work', 'money', 'love', 'relationship', 'marriage', 'health', 
                   'family', 'travel', 'education', 'future', 'life', 'success'}
    
    has_question = any(w in msg_words for w in question_words)
    has_topic = any(w in msg_words for w in topic_words)
    
    if has_question or has_topic or word_count > 5:
        # Substantive question - likely wants astro reading
        return {
            "intent": UserIntent.ASTRO_READING,
            "confidence": 0.65,  # Medium confidence since no explicit astro keywords
            "matched_keywords": list(msg_words & topic_words)[:3],
            "reason": "Substantive question/topic detected, defaulting to astro reading"
        }
    
    # Ultimate fallback: SMALL_TALK for very short, non-specific messages
    return {
        "intent": UserIntent.SMALL_TALK if word_count <= 3 else UserIntent.GENERAL_ADVICE,
        "confidence": 0.5,
        "matched_keywords": [],
        "reason": "No specific keywords matched, using default based on message length"
    }


def should_use_astro_signals(intent: UserIntent) -> bool:
    """
    Determine if astrology signals should be used for this intent.
    
    Args:
        intent: Classified user intent
        
    Returns:
        True if astro signals should be used, False otherwise
    """
    return intent == UserIntent.ASTRO_READING


def get_response_mode_for_intent(intent: UserIntent) -> str:
    """
    Get the response mode based on intent.
    
    Args:
        intent: Classified user intent
        
    Returns:
        Response mode string for the LLM
    """
    mode_map = {
        UserIntent.ASTRO_READING: "astro_reading",
        UserIntent.PRODUCT_HELP: "product_help",
        UserIntent.GENERAL_ADVICE: "general_advice", 
        UserIntent.SMALL_TALK: "small_talk",
    }
    return mode_map.get(intent, "astro_reading")
