"""
Personalized Welcome Message Generator for Niro.AI

Generates warm, conversational, emotionally intelligent welcome messages based on Kundli data.

CORE PRINCIPLE:
"Someone who understands me has already looked at my chart."

NO mechanical formatting. NO report-style sections.
NO bullet points in the final message. NO astrology jargon.
Pure, natural conversation between an astrologer and someone whose chart was already reviewed.
"""

# Vedic zodiac signs (Rashis) to key personality signals
# These are used to derive conversational qualities
SIGN_TRAITS = {
    "Aries": ["courageous", "direct", "initiating energy"],
    "Taurus": ["grounded", "patient", "steady presence"],
    "Gemini": ["curious", "adaptable", "communicative"],
    "Cancer": ["emotionally intuitive", "protective", "deeply caring"],
    "Leo": ["warm-hearted", "confident", "naturally magnetic"],
    "Virgo": ["thoughtful", "discerning", "service-minded"],
    "Libra": ["balanced", "gracious", "naturally diplomatic"],
    "Scorpio": ["penetrating", "resilient", "deeply transformative"],
    "Sagittarius": ["expansive", "honest", "philosophically inclined"],
    "Capricorn": ["disciplined", "responsible", "long-term focused"],
    "Aquarius": ["independent", "original", "systems-thinking"],
    "Pisces": ["imaginative", "empathetic", "spiritually open"],
}

# Moon (emotional nature) traits
MOON_TRAITS = {
    "Aries": ["passionate", "spontaneous", "brave", "action-oriented"],
    "Taurus": ["stable emotions", "appreciative", "pleasure-loving", "calm"],
    "Gemini": ["curious mind", "communicative", "social", "adaptable"],
    "Cancer": ["emotionally perceptive", "nurturing", "intuitive", "caring"],
    "Leo": ["warm-hearted", "generous", "confident", "proud"],
    "Virgo": ["analytical mind", "service-oriented", "careful", "discerning"],
    "Libra": ["balanced emotions", "appreciates beauty", "diplomatic", "social"],
    "Scorpio": ["deep emotions", "perceptive", "transformative", "magnetic"],
    "Sagittarius": ["optimistic", "philosophical", "honest", "expansive"],
    "Capricorn": ["disciplined", "responsible", "ambitious", "serious"],
    "Aquarius": ["detached", "humanitarian", "logical", "innovative"],
    "Pisces": ["sensitive", "imaginative", "dreamy", "empathetic"],
}

# Sun (core essence) traits
SUN_TRAITS = {
    "Aries": ["bold", "initiator", "courageous", "direct"],
    "Taurus": ["stable", "strong-willed", "devoted", "methodical"],
    "Gemini": ["communicative", "adaptable", "intelligent", "curious"],
    "Cancer": ["protective", "family-oriented", "sensitive", "loyal"],
    "Leo": ["leader", "creative", "generous", "dignified"],
    "Virgo": ["humble", "analytical", "helpful", "perfectionist"],
    "Libra": ["balanced", "diplomatic", "artistic", "justice-seeking"],
    "Scorpio": ["intense", "determined", "secretive", "powerful"],
    "Sagittarius": ["adventurer", "optimistic", "freedom-loving", "idealistic"],
    "Capricorn": ["structured", "ambitious", "responsible", "authoritative"],
    "Aquarius": ["visionary", "humanitarian", "unique", "progressive"],
    "Pisces": ["spiritual", "intuitive", "compassionate", "artistic"],
}


def get_dominant_elements(ascendant: str = None, moon_sign: str = None, sun_sign: str = None) -> list:
    """
    Map zodiac signs to their elements (Fire, Earth, Air, Water).
    Returns the dominant elements from ascendant/moon/sun.
    
    Used for tone selection.
    """
    element_map = {
        # Fire
        "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
        # Earth
        "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
        # Air
        "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
        # Water
        "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
    }
    
    elements = []
    for sign in [ascendant, moon_sign, sun_sign]:
        if sign and sign in element_map:
            elem = element_map[sign]
            if elem not in elements:
                elements.append(elem)
    
    return elements


def select_tone(elements: list) -> str:
    """
    Determine conversation tone based on dominant elements.
    
    MANDATORY TONE SELECTION LOGIC (from the prompt):
    
    Tone A — Calm & Grounded
        Use when dominant elements include Earth or Water
        
    Tone B — Warm & Encouraging
        Use when Water + Fire are both present
        
    Tone C — Confident & Forward-looking
        Use when dominant elements include Fire or Air
    
    Returns: "A", "B", or "C"
    """
    has_fire = "Fire" in elements
    has_water = "Water" in elements
    has_earth = "Earth" in elements
    has_air = "Air" in elements
    
    # Tone B takes precedence (most balanced, emotionally warm)
    if has_water and has_fire:
        return "B"
    
    # Tone A (grounded, calm)
    if has_earth or (has_water and not has_fire and not has_air):
        return "A"
    
    # Tone C (forward-looking, confident)
    if has_fire or has_air:
        return "C"
    
    # Default to Tone A (safest, warmest)
    return "A"


def collect_personality_traits(ascendant: str = None, moon_sign: str = None, sun_sign: str = None) -> list:
    """
    Gather personality traits from all three signs.
    Returns a list of 3 distinct, conversational traits.
    
    No mechanical language. No jargon.
    These will be woven into natural prose.
    """
    traits = []
    traits_set = set()
    
    # Primary: Ascendant (overall personality)
    if ascendant and ascendant in SIGN_TRAITS:
        for trait in SIGN_TRAITS[ascendant][:2]:
            if trait not in traits_set:
                traits.append(trait)
                traits_set.add(trait)
    
    # Secondary: Moon sign (emotional/inner nature)
    if moon_sign and moon_sign in MOON_TRAITS:
        for trait in MOON_TRAITS[moon_sign][:2]:
            if trait not in traits_set:
                traits.append(trait)
                traits_set.add(trait)
                if len(traits) >= 3:
                    break
    
    # Tertiary: Sun sign (core essence)
    if sun_sign and sun_sign in SUN_TRAITS and len(traits) < 3:
        for trait in SUN_TRAITS[sun_sign][:2]:
            if trait not in traits_set:
                traits.append(trait)
                traits_set.add(trait)
                if len(traits) >= 3:
                    break
    
    # Defaults if we don't have enough
    if len(traits) < 3:
        defaults = ["emotionally intelligent", "purposeful", "grounded"]
        for default in defaults:
            if default not in traits_set and len(traits) < 3:
                traits.append(default)
                traits_set.add(default)
    
    return traits[:3]


def generate_welcome_message(
    name: str,
    ascendant: str = None,
    moon_sign: str = None,
    sun_sign: str = None
) -> str:
    """
    Generate a warm, conversational, personalized welcome message.
    
    STRUCTURE (soft, not mechanical):
    1. Personal greeting using the user's name
    2. Acknowledgement that their chart has been looked at
    3. Three positive personality qualities, phrased conversationally
       (derived from ascendant + moon + dominant elements)
    4. Gentle invitation to continue the conversation
    
    TONE & STYLE RULES:
    ✓ Conversational, not mystical
    ✓ Calm confidence, not hype
    ✓ No bullet points
    ✓ No headings like "Summary" or "Analysis"
    ✓ No astrology jargon unless it sounds natural
    ✓ No advice yet — this is welcome, not a reading
    ✓ No emojis
    
    OUTPUT: Plain text only, 70-120 words
    
    SUCCESS CRITERIA:
    When a real user reads this message, they should feel:
    - Seen
    - Calm
    - Curious to continue
    
    If it sounds like it could appear in a PDF report, it is WRONG.
    """
    
    if not name:
        name = "there"
    
    # Step 1: Determine tone based on elements
    elements = get_dominant_elements(ascendant, moon_sign, sun_sign)
    tone = select_tone(elements)
    
    # Step 2: Collect personality traits
    traits = collect_personality_traits(ascendant, moon_sign, sun_sign)
    
    # Step 3: Build the message based on tone
    # The key is to weave traits naturally into prose, not list them
    
    if tone == "A":
        # TONE A — Calm & Grounded
        # Use when dominant elements include Earth or Water
        # Natural flow: greeting → acknowledgement → observation with traits woven in → invitation
        greeting = f"Hey {name}."
        acknowledgement = "I've looked at your chart."
        observation = f"I see someone who's {traits[0]}, {traits[1]}, and {traits[2]}—there's a grounded calm in that."
        invitation = "What would you like to explore?"
        
    elif tone == "B":
        # TONE B — Warm & Encouraging
        # Use when Water + Fire are both present
        # This combo creates someone emotionally aware AND expressive
        greeting = f"Hey {name}."
        acknowledgement = "I've looked at your chart."
        observation = f"There's something warm and genuine here—you're {traits[0]}, {traits[1]}, and {traits[2]}."
        invitation = "What's on your mind?"
        
    else:  # tone == "C"
        # TONE C — Confident & Forward-looking
        # Use when dominant elements include Fire or Air
        # Natural, bold, clear energy
        greeting = f"Hey {name}."
        acknowledgement = "I've looked at your chart."
        observation = f"You come across as {traits[0]}, {traits[1]}, and {traits[2]}. There's real clarity there."
        invitation = "What would you like to understand?"
    
    # Step 4: Combine into one warm, conversational paragraph
    # NO FORMATTING. NO LABELS. Plain text flow.
    message = f"{greeting} {acknowledgement} {observation}\n\n{invitation}"
    
    return message


def create_welcome_message(
    name: str,
    ascendant: str = None,
    moon_sign: str = None,
    sun_sign: str = None
) -> dict:
    """
    Legacy wrapper for backward compatibility.
    Returns both the new warm message format and legacy fields.
    """
    warm_message = generate_welcome_message(name, ascendant, moon_sign, sun_sign)
    
    # Generate legacy fields for backward compatibility
    traits = collect_personality_traits(ascendant, moon_sign, sun_sign)
    
    return {
        "message": warm_message,  # New: single warm, conversational message
        "title": f"Welcome, {name}!",  # Legacy
        "subtitle": "Your chart is ready.",  # Legacy
        "bullets": [f"• {t.capitalize()}" for t in traits],  # Legacy
    }


# Legacy function for backward compatibility
def generate_strengths(ascendant: str = None, moon_sign: str = None, sun_sign: str = None) -> list:
    """
    Legacy function. Returns 3 personality traits.
    Kept for backward compatibility with existing code.
    """
    return collect_personality_traits(ascendant, moon_sign, sun_sign)
