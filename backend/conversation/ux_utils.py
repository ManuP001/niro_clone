"""
UX Utilities for NIRO Chat
Handles conversation state, short-reply detection, chip generation, and trust widget building.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Short reply patterns
SHORT_REPLY_TOKENS = {"yes", "ok", "okay", "continue", "sure", "go", "go on", "next", "more", 
                       "tell me", "yes please", "yep", "yeah", "alright", "right", "got it",
                       "understood", "i see", "hmm", "interesting", "cool", "great", "thanks",
                       "thank you", "no", "nope", "not really", "maybe"}

# Single-word topic keywords
TOPIC_KEYWORDS = {
    "career": ["career", "job", "work", "profession", "business", "employment"],
    "relationship": ["relationship", "love", "marriage", "partner", "spouse", "dating"],
    "health": ["health", "wellness", "fitness", "medical", "disease", "body"],
    "finance": ["finance", "money", "wealth", "income", "investment", "savings"],
    "spirituality": ["spirituality", "spiritual", "meditation", "karma", "dharma", "soul"],
    "education": ["education", "study", "learning", "exam", "college", "university"],
    "family": ["family", "parents", "children", "siblings", "home"],
    "travel": ["travel", "foreign", "abroad", "relocation", "moving"]
}


def is_short_reply(message: str, max_tokens: int = 5) -> bool:
    """
    Detect if a message is a short reply that needs context resolution.
    
    Args:
        message: User message
        max_tokens: Maximum token count to consider as short
        
    Returns:
        True if message is a short reply
    """
    clean_msg = message.strip().lower()
    
    # Check if it's a known short reply pattern
    if clean_msg in SHORT_REPLY_TOKENS:
        return True
    
    # Check token count
    tokens = clean_msg.split()
    if len(tokens) <= max_tokens:
        # Check if it's a single-word topic
        for topic, keywords in TOPIC_KEYWORDS.items():
            if clean_msg in keywords:
                return True
        
        # Check if it looks like a continuation
        if len(tokens) <= 2:
            return True
    
    return False


def resolve_short_reply(
    message: str,
    last_ai_question: Optional[str],
    current_topic: Optional[str],
    last_user_intent: Optional[str]
) -> Tuple[str, float, Optional[str]]:
    """
    Resolve a short reply against conversation context.
    
    Args:
        message: Short user message
        last_ai_question: Last question asked by AI
        current_topic: Current conversation topic
        last_user_intent: Last detected user intent
        
    Returns:
        Tuple of (resolved_message, confidence, clarifying_question)
        - resolved_message: Expanded message with context
        - confidence: 0.0-1.0 confidence in resolution
        - clarifying_question: Question to ask if confidence is low (or None)
    """
    clean_msg = message.strip().lower()
    confidence = 0.5
    clarifying_question = None
    resolved_message = message
    
    # Affirmative replies
    if clean_msg in {"yes", "ok", "okay", "sure", "yep", "yeah", "alright", "go", "go on", "continue", "next", "more", "tell me", "yes please"}:
        if last_ai_question:
            resolved_message = f"Yes, please continue with: {last_ai_question}"
            confidence = 0.8
        elif current_topic:
            resolved_message = f"Tell me more about {current_topic}"
            confidence = 0.7
        else:
            clarifying_question = "What would you like to know more about?"
            confidence = 0.3
            
    # Negative replies
    elif clean_msg in {"no", "nope", "not really"}:
        if last_ai_question:
            resolved_message = f"No, I don't want to continue with {last_ai_question}. What else can you tell me?"
            confidence = 0.6
        else:
            clarifying_question = "What would you prefer to explore instead?"
            confidence = 0.3
            
    # Single-word topic detection
    else:
        detected_topic = None
        for topic, keywords in TOPIC_KEYWORDS.items():
            if clean_msg in keywords:
                detected_topic = topic
                break
        
        if detected_topic:
            resolved_message = f"Tell me about my {detected_topic} prospects based on my chart"
            confidence = 0.85
        elif len(clean_msg.split()) <= 2:
            # Very short but not recognized - ask for clarification
            clarifying_question = f"I'd love to help! Could you tell me a bit more about what aspect of '{message}' you'd like to explore?"
            confidence = 0.3
    
    return resolved_message, confidence, clarifying_question


def generate_clarifying_options(
    current_topic: Optional[str],
    last_ai_question: Optional[str]
) -> List[Dict[str, str]]:
    """
    Generate 2-3 clarifying options for ambiguous replies.
    
    Returns:
        List of options with id and label
    """
    options = []
    
    if current_topic:
        topic_options = {
            "career": [
                {"id": "career_timing", "label": "When is the best time for career moves?"},
                {"id": "career_change", "label": "Should I change my job?"},
                {"id": "career_growth", "label": "How can I grow in my current role?"}
            ],
            "relationship": [
                {"id": "rel_timing", "label": "When will I find love?"},
                {"id": "rel_compatibility", "label": "Am I compatible with my partner?"},
                {"id": "rel_advice", "label": "How can I improve my relationships?"}
            ],
            "health": [
                {"id": "health_concerns", "label": "Any health concerns I should watch?"},
                {"id": "health_timing", "label": "When is a good time for medical procedures?"},
                {"id": "health_wellness", "label": "How can I improve my wellbeing?"}
            ],
            "finance": [
                {"id": "fin_investment", "label": "Is this a good time to invest?"},
                {"id": "fin_income", "label": "When will my income improve?"},
                {"id": "fin_savings", "label": "How can I manage my finances better?"}
            ]
        }
        options = topic_options.get(current_topic, [])[:3]
    
    if not options:
        options = [
            {"id": "explore_career", "label": "Explore my career"},
            {"id": "explore_relationships", "label": "Explore relationships"},
            {"id": "explore_general", "label": "General life guidance"}
        ]
    
    return options


# Topic-specific impact descriptions - comprehensive for ALL planets
TOPIC_IMPACTS = {
    'career': {
        'Jupiter': 'brings growth opportunities, mentorship & expansion in your profession',
        'Venus': 'enhances workplace harmony, creativity & professional relationships',
        'Saturn': 'demands discipline but rewards persistence with lasting career gains',
        'Mars': 'drives ambition and competitive edge in professional pursuits',
        'Mercury': 'sharpens communication skills & business acumen',
        'Sun': 'boosts leadership potential & recognition at work',
        'Moon': 'influences work-life balance & emotional fulfillment in career',
        'Rahu': 'creates unconventional career opportunities & sudden breakthroughs',
        'Ketu': 'encourages detachment from material success, spiritual career paths'
    },
    'relationship': {
        'Jupiter': 'expands relationship possibilities & brings wisdom to partnerships',
        'Venus': 'heightens romance, attraction & harmony in relationships',
        'Saturn': 'brings commitment, loyalty & long-term relationship stability',
        'Mars': 'adds passion but may create conflicts if unchecked',
        'Mercury': 'improves communication & understanding with partners',
        'Sun': 'affects ego dynamics & mutual respect in relationships',
        'Moon': 'deepens emotional bonding & nurturing in partnerships',
        'Rahu': 'may bring intense, unconventional relationship experiences',
        'Ketu': 'encourages spiritual connection over material attachment'
    },
    'health': {
        'Jupiter': 'supports overall vitality & recovery from illness',
        'Venus': 'influences reproductive health & overall wellness',
        'Saturn': 'demands attention to chronic conditions & bone health',
        'Mars': 'affects energy levels, blood & inflammatory conditions',
        'Mercury': 'influences nervous system & mental well-being',
        'Sun': 'core vitality, heart health & immune strength',
        'Moon': 'emotional health, fluid balance & digestive wellness',
        'Rahu': 'may create mysterious ailments, needs careful diagnosis',
        'Ketu': 'spiritual healing, but watch for unexplained symptoms'
    },
    'finance': {
        'Jupiter': 'opens doors for wealth growth & wise investments',
        'Venus': 'attracts luxury, comforts & gains through partnerships',
        'Saturn': 'slow but steady wealth building through hard work',
        'Mars': 'aggressive financial moves, real estate opportunities',
        'Mercury': 'gains through business, trading & intellectual work',
        'Sun': 'income from government, authority positions',
        'Moon': 'fluctuating finances, gains through public & liquids',
        'Rahu': 'sudden gains or losses, speculative opportunities',
        'Ketu': 'detachment from wealth, spiritual over material gains'
    },
    'family': {
        'Jupiter': 'brings blessings, harmony & growth to family matters',
        'Venus': 'enhances domestic happiness, comfort & family bonds',
        'Saturn': 'teaches responsibility & creates lasting family structures',
        'Mars': 'energizes home projects but watch for family tensions',
        'Mercury': 'improves family communication & sibling relationships',
        'Sun': 'affects father figures & authority dynamics at home',
        'Moon': 'deepens emotional connection, especially with mother',
        'Rahu': 'may bring unexpected changes or unconventional family situations',
        'Ketu': 'encourages letting go of family attachments, ancestral healing'
    },
    'spiritual': {
        'Jupiter': 'expands spiritual wisdom, brings teachers & higher learning',
        'Venus': 'opens doors to devotion, artistic spirituality & inner beauty',
        'Saturn': 'deepens spiritual discipline & karmic understanding',
        'Mars': 'energizes spiritual practices & drives transformation',
        'Mercury': 'facilitates spiritual study & metaphysical understanding',
        'Sun': 'illuminates soul purpose & authentic self-expression',
        'Moon': 'deepens intuition, meditation & emotional spirituality',
        'Rahu': 'creates intense spiritual seeking & mystical experiences',
        'Ketu': 'accelerates liberation, past-life wisdom & enlightenment'
    },
    'travel': {
        'Jupiter': 'opens opportunities for meaningful journeys & foreign connections',
        'Venus': 'attracts pleasant travel experiences & beautiful destinations',
        'Saturn': 'may delay travel but brings structured, purposeful journeys',
        'Mars': 'energizes adventurous travel & quick movements',
        'Mercury': 'facilitates business travel & communication during journeys',
        'Sun': 'brings travel for recognition, government or leadership purposes',
        'Moon': 'influences emotional journeys & travel to water destinations',
        'Rahu': 'creates sudden travel opportunities & foreign adventures',
        'Ketu': 'encourages pilgrimages & spiritually significant journeys'
    },
    'education': {
        'Jupiter': 'expands learning opportunities & brings wise teachers',
        'Venus': 'enhances artistic learning & creative studies',
        'Saturn': 'demands discipline but rewards with deep, lasting knowledge',
        'Mars': 'drives competitive academic pursuits & technical learning',
        'Mercury': 'sharpens intellect, memory & communication skills',
        'Sun': 'boosts confidence in studies & leadership in academia',
        'Moon': 'affects emotional engagement with learning & intuitive knowledge',
        'Rahu': 'creates interest in unconventional subjects & foreign education',
        'Ketu': 'encourages spiritual knowledge & letting go of academic ego'
    },
    'general': {
        'Jupiter': 'brings expansion, wisdom & opportunities for growth in this area',
        'Venus': 'enhances harmony, pleasure & positive connections',
        'Saturn': 'brings lessons, structure & long-term development',
        'Mars': 'energizes action, courage & drives forward momentum',
        'Mercury': 'sharpens thinking, communication & decision-making',
        'Sun': 'illuminates your path & boosts confidence',
        'Moon': 'influences emotions, intuition & inner responses',
        'Rahu': 'creates intensity, ambition & unconventional opportunities',
        'Ketu': 'encourages release, spiritual insight & transcendence'
    }
}

HOUSE_MEANINGS = {
    1: "self & personality", 2: "wealth & speech", 3: "courage & siblings",
    4: "home & mother", 5: "creativity & children", 6: "health & enemies",
    7: "partnerships & marriage", 8: "transformation", 9: "luck & wisdom",
    10: "career & status", 11: "gains & aspirations", 12: "spirituality & losses"
}

TOPIC_DISPLAY = {
    'career': 'career', 'relationship': 'relationships', 
    'health': 'health', 'finance': 'finances',
    'family': 'family matters', 'spiritual': 'spiritual journey',
    'travel': 'travel plans', 'education': 'learning',
    'general': 'life path'
}


def _build_trust_widget_from_drivers(
    drivers: List[Dict[str, Any]],
    topic_normalized: str,
    timing_windows: List[Dict[str, Any]],
    time_context: str
) -> Dict[str, Any]:
    """
    Build Trust Widget from pre-selected drivers (from reading_pack).
    
    ROLE ENFORCEMENT: Only shows signals with roles:
    - TOPIC_DRIVER (primary)
    - TIME_DRIVER (timing context)
    - BASELINE_CONTEXT (optional, max 1)
    
    NEW: Includes topic_tag per driver for multi-topic questions.
    
    Excludes:
    - planet="Unknown" or "Mixed"
    - role="NOISE"
    """
    widget_drivers = []
    seen_planets = set()
    baseline_count = 0
    
    current_impacts = TOPIC_IMPACTS.get(topic_normalized, TOPIC_IMPACTS['general'])
    topic_display = TOPIC_DISPLAY.get(topic_normalized, 'life path')
    
    # Topic tag display labels
    topic_tag_labels = {
        'career': 'Career',
        'health_energy': 'Health',
        'health': 'Health',
        'romantic_relationships': 'Relationships',
        'relationship': 'Relationships',
        'marriage_partnership': 'Marriage',
        'money': 'Finance',
        'finance': 'Finance',
        'family_home': 'Family',
        'family': 'Family',
        'learning_education': 'Education',
        'education': 'Education',
        'travel_relocation': 'Travel',
        'travel': 'Travel',
        'spirituality': 'Spiritual',
        'self_psychology': 'Self',
        'general': 'General',
    }
    
    # Valid roles for Trust Widget
    valid_roles = {'TOPIC_DRIVER', 'TIME_DRIVER', 'BASELINE_CONTEXT'}
    
    for signal in drivers[:4]:  # Check up to 4, show max 3
        if len(widget_drivers) >= 3:
            break
            
        planet = signal.get('planet', signal.get('_planet', ''))
        sig_type = signal.get('type', '')
        house = signal.get('house')
        claim = signal.get('claim', '')
        polarity = signal.get('polarity', 'mixed')
        evidence = signal.get('evidence', {})
        role = signal.get('role', 'NOISE')
        topic_tag = signal.get('topic_tag', topic_normalized)  # NEW: Get topic tag
        
        # ROLE FILTER: Skip NOISE and invalid roles
        if role not in valid_roles:
            continue
        
        # PLANET FILTER: Skip Unknown/Mixed planets
        if planet in ('Unknown', 'Mixed', ''):
            continue
        
        # Limit BASELINE_CONTEXT to 1
        if role == 'BASELINE_CONTEXT':
            if baseline_count >= 1:
                continue
            baseline_count += 1
        
        # Skip duplicate planets
        if planet in seen_planets:
            continue
        
        # Get display label for topic tag
        topic_label = topic_tag_labels.get(topic_tag, topic_tag.replace('_', ' ').title())
        
        # Build driver label based on signal type
        if sig_type == 'dasha':
            period_type = 'Mahadasha' if 'Mahadasha' in claim else 'Antardasha'
            impact = current_impacts.get(planet, f'influences your {topic_display} direction')
            widget_drivers.append({
                "label": f"{planet} {period_type} active — {impact}",
                "type": "dasha",
                "role": role,
                "topic_tag": topic_label  # NEW: Include topic tag
            })
            seen_planets.add(planet)
                
        elif sig_type == 'transit':
            house_desc = f"transiting your {house}th house" if house else "in transit"
            impact = current_impacts.get(planet, f'affecting your {topic_display}')
            widget_drivers.append({
                "label": f"{planet} {house_desc} — {impact}",
                "type": "transit",
                "role": role,
                "topic_tag": topic_label  # NEW: Include topic tag
            })
            seen_planets.add(planet)
                
        elif sig_type == 'planet_position':
            house_num = evidence.get('house') if isinstance(evidence, dict) else house
            # Fallback to signal's house attribute
            if not house_num:
                house_num = house
            is_retrograde = evidence.get('retrograde', False) if isinstance(evidence, dict) else False
            
            if house_num:
                house_meaning = HOUSE_MEANINGS.get(int(house_num), f"{house_num}th house")
                impact = current_impacts.get(planet, f'influences your {topic_display}')
                retro_note = " (retrograde)" if is_retrograde else ""
                widget_drivers.append({
                    "label": f"{planet} in {house_meaning}{retro_note} — {impact}",
                    "type": "planet_position",
                    "role": role,
                    "topic_tag": topic_label  # NEW: Include topic tag
                })
                seen_planets.add(planet)
            else:
                # No house info but still valid planet position
                impact = current_impacts.get(planet, f'influences your {topic_display}')
                widget_drivers.append({
                    "label": f"{planet} in your chart — {impact}",
                    "type": "planet_position",
                    "role": role,
                    "topic_tag": topic_label  # NEW: Include topic tag
                })
                seen_planets.add(planet)
                    
        elif sig_type == 'yoga':
            yoga_name = claim or "Beneficial yoga"
            topic_label = topic_tag_labels.get(topic_tag, topic_tag.replace('_', ' ').title())
            widget_drivers.append({
                "label": f"{yoga_name} — enhances your chart's positive potential",
                "type": "yoga",
                "role": role,
                "topic_tag": topic_label  # NEW: Include topic tag
            })
            
        elif sig_type in ('planet_strength', 'rule'):
            topic_label = topic_tag_labels.get(topic_tag, topic_tag.replace('_', ' ').title())
            if house:
                house_meaning = HOUSE_MEANINGS.get(int(house), f"{house}th house matters")
                polarity_word = "strengthens" if polarity == 'supportive' else "challenges"
                widget_drivers.append({
                    "label": f"{house}th house ({house_meaning}) — {polarity_word} this area",
                    "type": "house",
                    "role": role,
                    "topic_tag": topic_label  # NEW: Include topic tag
                })
    
    # Extract time window (skip for past context)
    time_window = None
    if time_context != "past" and timing_windows:
        first_window = timing_windows[0]
        period = first_window.get('period', '')
        nature = first_window.get('nature', '')
        if period and 'ongoing' not in period.lower():
            time_window = f"{period}" + (f" ({nature})" if nature else "")
    
    return {
        "drivers": widget_drivers[:3],  # Max 3 drivers
        "time_window": time_window
    }


def generate_next_step_chips(
    current_topic: Optional[str],
    last_ai_question: Optional[str],
    mode: str,
    reply_text: str
) -> List[Dict[str, str]]:
    """
    Generate 3-5 context-aware next-step chips.
    
    Args:
        current_topic: Current conversation topic
        last_ai_question: Last question from AI
        mode: Current conversation mode
        reply_text: AI's reply text
        
    Returns:
        List of chip objects with id and label
    """
    chips = []
    
    # Topic-specific chips
    topic_chips = {
        "career": [
            {"id": "career_timing", "label": "🕐 Timing"},
            {"id": "career_action", "label": "📋 What should I do?"},
            {"id": "career_vs_business", "label": "🤔 Job vs Business"},
            {"id": "switch_topic", "label": "🔄 Ask about something else"}
        ],
        "relationship": [
            {"id": "rel_timing", "label": "🕐 Timing"},
            {"id": "rel_compatibility", "label": "💕 Compatibility"},
            {"id": "rel_action", "label": "📋 What should I do?"},
            {"id": "switch_topic", "label": "🔄 Ask about something else"}
        ],
        "health": [
            {"id": "health_timing", "label": "🕐 Timing"},
            {"id": "health_precautions", "label": "⚠️ Precautions"},
            {"id": "health_wellness", "label": "🧘 Wellness tips"},
            {"id": "switch_topic", "label": "🔄 Ask about something else"}
        ],
        "finance": [
            {"id": "fin_timing", "label": "🕐 Best time to invest"},
            {"id": "fin_action", "label": "📋 What should I do?"},
            {"id": "fin_sources", "label": "💰 Income sources"},
            {"id": "switch_topic", "label": "🔄 Ask about something else"}
        ],
        "spirituality": [
            {"id": "spirit_practices", "label": "🧘 Practices for me"},
            {"id": "spirit_guidance", "label": "✨ Spiritual guidance"},
            {"id": "spirit_karma", "label": "☯️ Karmic insights"},
            {"id": "switch_topic", "label": "🔄 Ask about something else"}
        ]
    }
    
    if current_topic and current_topic in topic_chips:
        chips = topic_chips[current_topic][:4]
    else:
        # Default chips for general conversation
        chips = [
            {"id": "explore_career", "label": "💼 Career"},
            {"id": "explore_relationship", "label": "💕 Relationships"},
            {"id": "explore_finance", "label": "💰 Finance"},
            {"id": "explore_health", "label": "🏥 Health"},
            {"id": "explore_timing", "label": "🕐 Timing"}
        ]
    
    # Add "Tell me more" if the response seems to have more to offer
    if "?" in reply_text and len(chips) < 5:
        chips.append({"id": "continue", "label": "📖 Tell me more"})
    
    return chips[:5]


def build_trust_widget(
    reasons: List[str],
    timing_windows: List[Dict[str, Any]],
    signal_scores: List[float],
    time_context: str = "timeless",
    selected_signals: List[Dict[str, Any]] = None,
    topic: str = None,
    drivers_from_pack: List[Dict[str, Any]] = None,
    is_astro_intent: bool = True
) -> Dict[str, Any]:
    """
    Build Trust Widget data - uses EXACTLY the drivers from reading_pack.
    
    IMPORTANT: For non-astro intents, returns empty/hidden widget.
    For astro intents, uses the pre-selected drivers from the signal pipeline.
    
    Args:
        reasons: Raw reasons list from LLM response (fallback only)
        timing_windows: Timing window data
        signal_scores: Signal scores (kept for compatibility)
        time_context: Time context ("past", "present", "future", "timeless")
        selected_signals: List of selected signals (deprecated, use drivers_from_pack)
        topic: Current topic (career, relationship, health, etc.)
        drivers_from_pack: Pre-selected drivers from reading_pack (NEW - preferred)
        is_astro_intent: Whether this is an astrology question (NEW)
        
    Returns:
        Trust Widget dict with detailed drivers and time_window
        For non-astro intents: returns {"drivers": [], "time_window": None}
    """
    # NON-ASTRO INTENT: Return empty trust widget
    if not is_astro_intent:
        return {
            "drivers": [],
            "time_window": None,
            "hidden": True
        }
    
    # Normalize topic names
    topic_normalized = topic.lower() if topic else ''
    
    if 'relationship' in topic_normalized or 'romantic' in topic_normalized or 'love' in topic_normalized or 'marriage' in topic_normalized:
        topic_normalized = 'relationship'
    elif 'career' in topic_normalized or 'job' in topic_normalized or 'work' in topic_normalized or 'business' in topic_normalized:
        topic_normalized = 'career'
    elif 'health' in topic_normalized or 'wellness' in topic_normalized or 'energy' in topic_normalized:
        topic_normalized = 'health'
    elif 'finance' in topic_normalized or 'money' in topic_normalized or 'wealth' in topic_normalized:
        topic_normalized = 'finance'
    elif 'family' in topic_normalized or 'home' in topic_normalized:
        topic_normalized = 'family'
    elif 'spirit' in topic_normalized or 'soul' in topic_normalized:
        topic_normalized = 'spiritual'
    elif 'travel' in topic_normalized or 'relocation' in topic_normalized:
        topic_normalized = 'travel'
    elif 'education' in topic_normalized or 'learning' in topic_normalized:
        topic_normalized = 'education'
    else:
        topic_normalized = 'general'
    
    # USE DRIVERS FROM READING PACK (preferred path)
    if drivers_from_pack and len(drivers_from_pack) > 0:
        return _build_trust_widget_from_drivers(drivers_from_pack, topic_normalized, timing_windows, time_context)
    
    # Fallback to selected_signals if drivers_from_pack not provided
    if selected_signals:
        return _build_trust_widget_from_drivers(selected_signals[:3], topic_normalized, timing_windows, time_context)
    
    # Ultimate fallback - build from LLM reasons
    drivers = []
    if reasons:
        for reason in reasons[:3]:
            clean_reason = re.sub(r'\[S\d+\]\s*', '', reason).strip()
            if clean_reason and len(clean_reason) > 10:
                drivers.append({
                    "label": humanize_astrological_term(clean_reason),
                    "type": "reason"
                })
    
    # Extract time window
    time_window = None
    if time_context != "past" and timing_windows:
        first_window = timing_windows[0]
        period = first_window.get('period', '')
        if period and 'ongoing' not in period.lower():
            nature = first_window.get('nature', '')
            time_window = f"{period}" + (f" ({nature})" if nature else "")
    
    return {
        "drivers": drivers[:3],
        "time_window": time_window
    }


def humanize_astrological_term(term: str) -> str:
    """
    Convert astrological jargon to human-readable terms.
    """
    replacements = {
        "Mahadasha": "Major planetary period",
        "Antardasha": "Sub-period",
        "mahadasha": "major period",
        "antardasha": "sub-period",
        "dasha": "planetary period",
        "Rahu": "North Node (Rahu)",
        "Ketu": "South Node (Ketu)",
        "Saturn": "Saturn's influence",
        "Jupiter": "Jupiter's blessing",
        "Mars": "Mars energy",
        "Venus": "Venus influence",
        "Mercury": "Mercury's effect",
        "Sun": "Solar influence",
        "Moon": "Lunar influence",
        "house": "life area",
        "1st house": "self & identity",
        "2nd house": "wealth & family",
        "3rd house": "communication & siblings",
        "4th house": "home & mother",
        "5th house": "creativity & children",
        "6th house": "health & daily work",
        "7th house": "partnerships & marriage",
        "8th house": "transformation & hidden matters",
        "9th house": "luck & higher learning",
        "10th house": "career & public image",
        "11th house": "gains & aspirations",
        "12th house": "spirituality & endings"
    }
    
    result = term
    
    # First, clean up technical rule references like "Rule3 strength 0"
    import re
    
    # Remove "Rule#" patterns - these are internal references
    result = re.sub(r'Rule\d+\s*', '', result)
    
    # Remove "strength #" patterns - convert to more human terms
    strength_match = re.search(r'strength\s*(\d+)', result.lower())
    if strength_match:
        strength = int(strength_match.group(1))
        if strength >= 70:
            strength_label = "strongly positioned"
        elif strength >= 50:
            strength_label = "moderately positioned"
        elif strength >= 30:
            strength_label = "weakly positioned"
        else:
            strength_label = "challenged"
        result = re.sub(r'strength\s*\d+', strength_label, result, flags=re.IGNORECASE)
    
    # Remove "S#" signal ID references if they somehow got through
    result = re.sub(r'\[?S\d+\]?\s*', '', result)
    
    # Clean up any leftover technical patterns
    result = re.sub(r'\(\s*strength:\s*\d+\s*\)', '', result)
    
    # Apply word replacements
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    # Clean up extra whitespace
    result = ' '.join(result.split())
    
    return result


def should_show_feedback(
    reply_text: str,
    is_welcome: bool = False,
    has_emotional_insight: bool = False
) -> bool:
    """
    Determine if we should show micro-feedback buttons.
    
    Shows feedback for:
    - Welcome messages
    - Emotional insights
    - Strong personality-based statements
    """
    if is_welcome:
        return True
    
    if has_emotional_insight:
        return True
    
    # Check for emotional/personality language
    emotional_keywords = [
        "you are", "you're", "your nature", "your personality",
        "you tend to", "you feel", "emotionally", "your strengths",
        "your weaknesses", "naturally", "innately"
    ]
    
    lower_text = reply_text.lower()
    for keyword in emotional_keywords:
        if keyword in lower_text:
            return True
    
    return False


def extract_ai_question(reply_text: str) -> Optional[str]:
    """
    Extract the question from AI's reply (usually at the end).
    """
    # Find the last question in the reply
    sentences = re.split(r'[.!]\s+', reply_text)
    for sentence in reversed(sentences):
        if '?' in sentence:
            return sentence.strip()
    return None
