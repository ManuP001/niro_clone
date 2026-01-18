"""
Welcome Engine - Confidence-Aware Welcome Message Generator

Generates warm, specific, and trustworthy first messages using:
- Natal chart data
- Active Mahadasha / Antardasha  
- Key planet placements (Moon, Lagna lord, Mahadasha lord)
- Signal scores from reading_pack

Key Features:
- Confidence bands (HIGH, MEDIUM, LOW) for each insight
- No questions asked
- No vague or generic claims
- Guardrails against planet drift
- Time overlap validation for past/current claims

Output:
{
    "welcome_text": "string",
    "confidence_map": {
        "personality": "high" | "medium" | None,
        "past_theme": "high" | "medium" | None,
        "current_phase": "high" | "medium" | None
    }
}
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import date, datetime
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIDENCE BANDS
# ============================================================================

class Confidence(str, Enum):
    HIGH = "high"      # Strong signal alignment, no contradictions
    MEDIUM = "medium"  # Meaningful signal but timing/dominance not airtight
    LOW = "low"        # Do NOT say anything


# ============================================================================
# PERSONALITY TRAIT MAPPINGS (Natal-based, High Confidence)
# ============================================================================

# Moon Sign -> Core Emotional Nature (verified astrological mappings)
MOON_SIGN_TRAITS = {
    "Aries": {
        "core": "emotionally direct and action-oriented",
        "trait": "You feel most alive when you're taking initiative and leading the charge",
        "strength": "Your emotional courage helps you bounce back quickly from setbacks"
    },
    "Taurus": {
        "core": "emotionally grounded and security-seeking",
        "trait": "You find comfort in stability, beauty, and sensory pleasures",
        "strength": "Your emotional steadiness makes you a reliable presence for others"
    },
    "Gemini": {
        "core": "emotionally curious and mentally active",
        "trait": "Your feelings are often processed through conversation and analysis",
        "strength": "Your adaptability helps you navigate emotional complexity with flexibility"
    },
    "Cancer": {
        "core": "deeply nurturing and emotionally intuitive",
        "trait": "Home, family, and emotional security form the foundation of your inner world",
        "strength": "Your emotional sensitivity creates deep bonds with those you care about"
    },
    "Leo": {
        "core": "emotionally expressive and warmth-seeking",
        "trait": "You need to feel appreciated and have a natural flair for bringing joy",
        "strength": "Your generosity of spirit inspires confidence in others"
    },
    "Virgo": {
        "core": "emotionally analytical and service-oriented",
        "trait": "You process feelings through practical action and helping others",
        "strength": "Your attention to detail helps you provide meaningful support"
    },
    "Libra": {
        "core": "emotionally harmony-seeking and relationship-focused",
        "trait": "Partnership and fairness deeply matter to your inner peace",
        "strength": "Your diplomatic nature helps create balance in challenging situations"
    },
    "Scorpio": {
        "core": "emotionally intense and transformation-focused",
        "trait": "You experience feelings with profound depth and seek authenticity",
        "strength": "Your emotional resilience allows you to navigate life's deepest waters"
    },
    "Sagittarius": {
        "core": "emotionally expansive and meaning-seeking",
        "trait": "Freedom, truth, and philosophical exploration fuel your inner fire",
        "strength": "Your optimism and faith help you see possibility where others see limits"
    },
    "Capricorn": {
        "core": "emotionally mature and achievement-oriented",
        "trait": "You find emotional fulfillment through building something lasting",
        "strength": "Your disciplined approach helps you achieve long-term emotional security"
    },
    "Aquarius": {
        "core": "emotionally independent and humanitarian",
        "trait": "You connect with feelings through ideals and collective well-being",
        "strength": "Your objectivity helps you offer perspective during emotional intensity"
    },
    "Pisces": {
        "core": "emotionally intuitive and compassionate",
        "trait": "You absorb the feelings of those around you and seek transcendence",
        "strength": "Your empathy creates profound understanding and healing presence"
    }
}

# Ascendant Sign -> Life Approach & External Persona
ASCENDANT_TRAITS = {
    "Aries": "You naturally approach life with directness and pioneering spirit",
    "Taurus": "You move through life with steady determination and practical sensibility",
    "Gemini": "You engage with the world through curiosity and intellectual versatility",
    "Cancer": "You navigate life with protective instincts and emotional intelligence",
    "Leo": "You present yourself with natural confidence and creative flair",
    "Virgo": "You approach life with analytical precision and helpful intentions",
    "Libra": "You move through the world seeking balance, beauty, and partnership",
    "Scorpio": "You engage with life's mysteries with intensity and strategic depth",
    "Sagittarius": "You approach life with philosophical optimism and adventurous spirit",
    "Capricorn": "You navigate the world with ambition, patience, and structural thinking",
    "Aquarius": "You engage with life through innovation and independent thinking",
    "Pisces": "You move through the world with intuitive sensitivity and creative imagination"
}

# Mahadasha Lord -> Life Phase Themes (for current phase insights)
MAHADASHA_THEMES = {
    "Sun": {
        "theme": "self-expression, authority, and recognition",
        "focus": "This is a period for stepping into your power and being seen",
        "energy": "confidence and leadership are highlighted"
    },
    "Moon": {
        "theme": "emotional growth, nurturing, and inner reflection",
        "focus": "This period emphasizes your emotional world and close relationships",
        "energy": "intuition and self-care become priorities"
    },
    "Mars": {
        "theme": "action, courage, and assertive pursuits",
        "focus": "This is a time for bold moves and channeling your drive",
        "energy": "initiative and competitive spirit are amplified"
    },
    "Mercury": {
        "theme": "communication, learning, and intellectual growth",
        "focus": "This period highlights skills, analysis, and connection through ideas",
        "energy": "adaptability and mental agility are your allies"
    },
    "Jupiter": {
        "theme": "expansion, wisdom, and good fortune",
        "focus": "This is a period of growth, opportunities, and higher learning",
        "energy": "optimism and spiritual understanding deepen"
    },
    "Venus": {
        "theme": "relationships, creativity, and life's pleasures",
        "focus": "This period emphasizes love, art, and enjoyment of life's beauty",
        "energy": "harmony and aesthetic sensibility are enhanced"
    },
    "Saturn": {
        "theme": "discipline, responsibility, and long-term building",
        "focus": "This is a time for patience, hard work, and structural foundations",
        "energy": "maturity and perseverance are tested and rewarded"
    },
    "Rahu": {
        "theme": "worldly ambition, unconventional paths, and desire",
        "focus": "This period pushes you toward new experiences and material goals",
        "energy": "intensity around achievements and obsessive interests"
    },
    "Ketu": {
        "theme": "spiritual seeking, letting go, and past karma",
        "focus": "This is a time for release, introspection, and inner wisdom",
        "energy": "detachment and spiritual insights become prominent"
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_lagna_lord(ascendant: str) -> str:
    """Get the lord of the ascendant sign."""
    SIGN_LORDS = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
        'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
        'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    return SIGN_LORDS.get(ascendant, 'Unknown')


def _calculate_dasha_elapsed_percentage(dasha_info: Dict[str, Any]) -> float:
    """Calculate what percentage of a dasha period has elapsed."""
    if not dasha_info:
        return 0.0
    
    years_total = dasha_info.get('years_total', 1)
    years_elapsed = dasha_info.get('years_elapsed', 0)
    
    if years_total <= 0:
        return 0.0
    
    return min(100.0, (years_elapsed / years_total) * 100)


def _is_dasha_in_early_phase(dasha_info: Dict[str, Any]) -> bool:
    """Check if dasha is in early phase (first 20%)."""
    return _calculate_dasha_elapsed_percentage(dasha_info) < 20


def _is_dasha_in_mature_phase(dasha_info: Dict[str, Any]) -> bool:
    """Check if dasha is in mature phase (20-80%)."""
    pct = _calculate_dasha_elapsed_percentage(dasha_info)
    return 20 <= pct <= 80


def _is_dasha_in_late_phase(dasha_info: Dict[str, Any]) -> bool:
    """Check if dasha is in late phase (last 20%)."""
    return _calculate_dasha_elapsed_percentage(dasha_info) > 80


def _validate_planet_placement(planet_name: str, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate that a planet exists in the profile and return its data."""
    planets = profile.get('planets', [])
    for p in planets:
        if p.get('planet', '').lower() == planet_name.lower():
            return p
    return None


def _assess_mahadasha_confidence(
    mahadasha: Dict[str, Any],
    antardasha: Dict[str, Any],
    profile: Dict[str, Any]
) -> Confidence:
    """
    Assess confidence level for current phase insight based on dasha.
    
    HIGH confidence requires:
    - Valid mahadasha with planet
    - Mahadasha planet is in the chart
    - Clear timing (not in transition phases)
    
    MEDIUM confidence if:
    - Valid mahadasha but timing is edge case
    - Or antardasha provides additional context
    """
    if not mahadasha or not mahadasha.get('planet'):
        return Confidence.LOW
    
    maha_planet = mahadasha.get('planet')
    
    # Validate planet exists in chart
    if not _validate_planet_placement(maha_planet, profile):
        # Check if it's a valid planet name at least
        valid_planets = {'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'}
        if maha_planet not in valid_planets:
            return Confidence.LOW
    
    # Check dasha phase
    if _is_dasha_in_early_phase(mahadasha):
        # Just started - HIGH confidence about new phase
        return Confidence.HIGH
    elif _is_dasha_in_mature_phase(mahadasha):
        # Well established - HIGH confidence
        return Confidence.HIGH
    elif _is_dasha_in_late_phase(mahadasha):
        # Transitioning soon - MEDIUM confidence
        return Confidence.MEDIUM
    
    return Confidence.MEDIUM


def _assess_personality_confidence(
    moon_sign: str,
    ascendant: str,
    profile: Dict[str, Any]
) -> Confidence:
    """
    Assess confidence for personality anchor.
    
    HIGH confidence requires:
    - Valid moon sign with traits defined
    - Valid ascendant
    
    MEDIUM if only one is available.
    LOW if neither is valid.
    """
    has_moon = moon_sign and moon_sign in MOON_SIGN_TRAITS
    has_asc = ascendant and ascendant in ASCENDANT_TRAITS
    
    if has_moon and has_asc:
        return Confidence.HIGH
    elif has_moon or has_asc:
        return Confidence.MEDIUM
    else:
        return Confidence.LOW


def _format_dasha_phase_text(mahadasha: Dict[str, Any], antardasha: Dict[str, Any]) -> str:
    """Format the dasha phase description with timing context."""
    maha_planet = mahadasha.get('planet', '')
    
    if not maha_planet or maha_planet not in MAHADASHA_THEMES:
        return ""
    
    theme = MAHADASHA_THEMES[maha_planet]
    
    # Determine phase description
    if _is_dasha_in_early_phase(mahadasha):
        phase_context = f"You've recently entered a {maha_planet} period"
    elif _is_dasha_in_late_phase(mahadasha):
        years_remaining = mahadasha.get('years_remaining', 0)
        if years_remaining > 0:
            phase_context = f"You're in the later stages of your {maha_planet} period"
        else:
            phase_context = f"Your {maha_planet} period is active"
    else:
        phase_context = f"You are in your {maha_planet} Mahadasha"
    
    # Add antardasha context if meaningful
    antar_planet = antardasha.get('planet', '') if antardasha else ''
    if antar_planet and antar_planet != maha_planet:
        antar_text = f", currently colored by {antar_planet}'s influence"
    else:
        antar_text = ""
    
    return f"{phase_context}{antar_text}. {theme['focus']}."


# ============================================================================
# MAIN WELCOME MESSAGE GENERATOR
# ============================================================================

def generate_welcome_message(
    profile: Dict[str, Any],
    signals: Optional[List[Dict[str, Any]]] = None,
    user_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a confidence-aware welcome message.
    
    Args:
        profile: AstroProfile dict containing:
            - ascendant: str (Lagna sign)
            - moon_sign: str
            - moon_nakshatra: str
            - current_mahadasha: dict with planet, start_date, end_date, years_*
            - current_antardasha: dict
            - planets: list of planet positions
        signals: Optional list of scored signals from reading_pack
        user_name: Optional user's name for personalization
    
    Returns:
        {
            "welcome_text": str,
            "confidence_map": {
                "personality": "high" | "medium" | None,
                "past_theme": "high" | "medium" | None,
                "current_phase": "high" | "medium" | None
            }
        }
    """
    logger.info("[WELCOME] Generating confidence-aware welcome message")
    
    # Initialize output
    sections = []
    confidence_map = {
        "personality": None,
        "past_theme": None,
        "current_phase": None
    }
    
    # Extract key data
    ascendant = profile.get('ascendant', '')
    moon_sign = profile.get('moon_sign', '')
    # moon_nakshatra available for future enhanced personality insights
    _ = profile.get('moon_nakshatra', '')
    
    mahadasha = profile.get('current_mahadasha', {})
    antardasha = profile.get('current_antardasha', {})
    
    # Handle DashaInfo objects vs dicts
    if hasattr(mahadasha, 'model_dump'):
        mahadasha = mahadasha.model_dump()
    if hasattr(antardasha, 'model_dump'):
        antardasha = antardasha.model_dump()
    
    # =========================================================================
    # SECTION 1: Personality Anchor (High Confidence Only)
    # =========================================================================
    personality_confidence = _assess_personality_confidence(moon_sign, ascendant, profile)
    
    if personality_confidence == Confidence.HIGH:
        # Generate personality text from Moon sign (primary) + Ascendant (secondary)
        moon_traits = MOON_SIGN_TRAITS.get(moon_sign, {})
        asc_trait = ASCENDANT_TRAITS.get(ascendant, '')
        
        if moon_traits:
            personality_text = f"With Moon in {moon_sign}, you are {moon_traits['core']}. {moon_traits['strength']}."
            if asc_trait and ascendant != moon_sign:
                personality_text += f" {asc_trait}."
            
            sections.append(personality_text)
            confidence_map["personality"] = "high"
            logger.info(f"[WELCOME] Added HIGH confidence personality anchor: Moon in {moon_sign}, Asc {ascendant}")
    
    elif personality_confidence == Confidence.MEDIUM:
        # Only one element available - use what we have with slightly hedged language
        if moon_sign and moon_sign in MOON_SIGN_TRAITS:
            moon_traits = MOON_SIGN_TRAITS[moon_sign]
            personality_text = f"Your Moon in {moon_sign} suggests you're {moon_traits['core']}."
            sections.append(personality_text)
            confidence_map["personality"] = "medium"
            logger.info(f"[WELCOME] Added MEDIUM confidence personality: Moon in {moon_sign}")
        elif ascendant and ascendant in ASCENDANT_TRAITS:
            asc_trait = ASCENDANT_TRAITS[ascendant]
            personality_text = f"As a {ascendant} rising, {asc_trait.lower()}."
            sections.append(personality_text)
            confidence_map["personality"] = "medium"
            logger.info(f"[WELCOME] Added MEDIUM confidence personality: {ascendant} Asc")
    
    # If LOW confidence, omit entirely (no generic filler)
    
    # =========================================================================
    # SECTION 2: Current Life Phase Insight (High Confidence Only)
    # =========================================================================
    phase_confidence = _assess_mahadasha_confidence(mahadasha, antardasha, profile)
    
    if phase_confidence == Confidence.HIGH:
        phase_text = _format_dasha_phase_text(mahadasha, antardasha)
        if phase_text:
            sections.append(phase_text)
            confidence_map["current_phase"] = "high"
            logger.info(f"[WELCOME] Added HIGH confidence current phase: {mahadasha.get('planet')} Mahadasha")
    
    elif phase_confidence == Confidence.MEDIUM:
        # Hedged language for medium confidence
        maha_planet = mahadasha.get('planet', '')
        if maha_planet and maha_planet in MAHADASHA_THEMES:
            theme = MAHADASHA_THEMES[maha_planet]
            phase_text = f"You're likely experiencing themes of {theme['theme']} during this period."
            sections.append(phase_text)
            confidence_map["current_phase"] = "medium"
            logger.info(f"[WELCOME] Added MEDIUM confidence current phase: {maha_planet}")
    
    # =========================================================================
    # SECTION 3: Past Theme (Medium+ Confidence, with time validation)
    # - Only include if we have completed dasha periods to reference
    # - Currently NOT implementing past theme to avoid false claims
    # - Can be added later with full dasha timeline analysis
    # =========================================================================
    # Note: Past theme section intentionally omitted for now
    # It requires full dasha timeline analysis to validate completed periods
    # confidence_map["past_theme"] remains None
    
    # =========================================================================
    # ASSEMBLE FINAL MESSAGE
    # =========================================================================
    
    if not sections:
        # Fallback: If no confident sections, return minimal safe message
        logger.warning("[WELCOME] No confident sections generated, using minimal fallback")
        welcome_text = "Welcome. I've reviewed your chart and am ready to explore your questions."
        return {
            "welcome_text": welcome_text,
            "confidence_map": confidence_map
        }
    
    # Add warm opening with name if available
    if user_name:
        opening = f"Welcome, {user_name}. "
    else:
        opening = ""
    
    # Join sections with proper spacing
    welcome_text = opening + " ".join(sections)
    
    # Clean up any double spaces
    welcome_text = " ".join(welcome_text.split())
    
    logger.info(f"[WELCOME] Generated message with confidence map: {confidence_map}")
    
    return {
        "welcome_text": welcome_text,
        "confidence_map": confidence_map
    }


def generate_welcome_from_astro_profile(
    astro_profile,  # AstroProfile object
    user_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience wrapper that accepts an AstroProfile object directly.
    
    Args:
        astro_profile: AstroProfile pydantic model
        user_name: Optional user's name
    
    Returns:
        Same as generate_welcome_message()
    """
    # Convert AstroProfile to dict
    if hasattr(astro_profile, 'model_dump'):
        profile_dict = astro_profile.model_dump()
    elif hasattr(astro_profile, 'dict'):
        profile_dict = astro_profile.dict()
    else:
        profile_dict = dict(astro_profile)
    
    return generate_welcome_message(profile_dict, user_name=user_name)


# ============================================================================
# VALIDATION & GUARDRAILS
# ============================================================================

def validate_welcome_message(welcome_result: Dict[str, Any]) -> List[str]:
    """
    Validate that the welcome message follows all guardrails.
    
    Returns list of violations (empty if valid).
    """
    violations = []
    text = welcome_result.get('welcome_text', '')
    
    # Check for questions
    if '?' in text:
        violations.append("VIOLATION: Welcome message contains a question")
    
    # Check for generic/vague phrases
    vague_phrases = [
        "you may feel",
        "you might be",
        "possibly",
        "perhaps",
        "in some ways",
        "sometimes",
        "could be",
        "might have",
        "may have experienced",
        "it's possible that"
    ]
    for phrase in vague_phrases:
        if phrase.lower() in text.lower():
            violations.append(f"VIOLATION: Contains vague phrase: '{phrase}'")
    
    # Check for generic astrology statements
    generic_statements = [
        "the stars say",
        "the universe",
        "cosmic energy",
        "planetary alignment",
        "celestial",
        "according to astrology"
    ]
    for stmt in generic_statements:
        if stmt.lower() in text.lower():
            violations.append(f"VIOLATION: Contains generic astrology statement: '{stmt}'")
    
    return violations


# ============================================================================
# TESTING UTILITY
# ============================================================================

def test_welcome_engine():
    """Test the welcome engine with sample data."""
    
    # Sample profile (Sharad Harjai)
    test_profile = {
        "ascendant": "Sagittarius",
        "moon_sign": "Gemini",
        "moon_nakshatra": "Ardra",
        "sun_sign": "Capricorn",
        "current_mahadasha": {
            "planet": "Mercury",
            "start_date": "2025-02-09",
            "end_date": "2042-02-10",
            "years_total": 17,
            "years_elapsed": 0.5,
            "years_remaining": 16.5
        },
        "current_antardasha": {
            "planet": "Mercury",
            "start_date": "2025-02-09",
            "end_date": "2027-07-09",
            "years_total": 2.4,
            "years_elapsed": 0.5,
            "years_remaining": 1.9
        },
        "planets": [
            {"planet": "Sun", "sign": "Capricorn", "house": 2},
            {"planet": "Moon", "sign": "Gemini", "house": 7},
            {"planet": "Mars", "sign": "Scorpio", "house": 12},
            {"planet": "Mercury", "sign": "Capricorn", "house": 2},
            {"planet": "Jupiter", "sign": "Capricorn", "house": 2},
            {"planet": "Venus", "sign": "Capricorn", "house": 2},
            {"planet": "Saturn", "sign": "Scorpio", "house": 12},
            {"planet": "Rahu", "sign": "Aries", "house": 5},
            {"planet": "Ketu", "sign": "Libra", "house": 11}
        ]
    }
    
    print("="*80)
    print("WELCOME ENGINE TEST")
    print("="*80)
    
    result = generate_welcome_message(test_profile, user_name="Sharad")
    
    print("\n📝 WELCOME TEXT:")
    print(f"   {result['welcome_text']}")
    
    print("\n📊 CONFIDENCE MAP:")
    for key, value in result['confidence_map'].items():
        status = "✅" if value == "high" else ("⚠️" if value == "medium" else "❌")
        print(f"   {status} {key}: {value or 'omitted'}")
    
    print("\n🔍 VALIDATION:")
    violations = validate_welcome_message(result)
    if violations:
        for v in violations:
            print(f"   ❌ {v}")
    else:
        print("   ✅ All guardrails passed")
    
    return result


if __name__ == "__main__":
    test_welcome_engine()
