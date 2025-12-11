"""
Astro Interpreter

Builds topic-specific astro_features for NIRO LLM consumption.
Maps chart data to relevant factors based on topic.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
import logging

from .models import AstroProfile, AstroTransits, TransitEvent
from .topics import Topic, get_chart_levers, TOPIC_CHART_LEVERS

logger = logging.getLogger(__name__)

# Sign lords for reference
SIGN_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
    'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}


def build_astro_features(
    profile: AstroProfile,
    transits: AstroTransits,
    mode: str,
    topic: str,
    now: datetime = None,
    timeframe_hint: Dict[str, any] = None
) -> Dict[str, Any]:
    """
    Build topic-specific astro features for NIRO LLM.
    
    This is the main function that creates the astro_features payload
    sent to the LLM. It filters and transforms chart data based on
    the topic to provide relevant astrological context.
    
    Args:
        profile: User's AstroProfile (natal chart + dashas)
        transits: Current transits data
        mode: Conversation mode (NEED_BIRTH_DETAILS, NORMAL_READING)
        topic: Topic being discussed (career, money, etc.)
        now: Current datetime (default: utcnow)
        timeframe_hint: Timeframe classification result (from classify_timeframe)
        
    Returns:
        Dict with structured astro features for LLM
    """
    now = now or datetime.utcnow()
    today = now.date()
    
    # Default timeframe: 12 months if not provided
    if timeframe_hint is None:
        timeframe_hint = {"type": "default", "value": 12, "horizon_months": 12}
    
    logger.info(f"Building astro features: mode={mode}, topic={topic}, timeframe={timeframe_hint.get('horizon_months', 12)} months")
    
    # Get relevant chart levers for this topic
    levers = get_chart_levers(topic)
    relevant_houses = levers.get("houses", [])
    relevant_planets = levers.get("planets", [])
    key_factors_names = levers.get("key_factors", [])
    
    # Build the features dict
    features = {
        # Birth details (always included)
        "birth_details": {
            "dob": profile.birth_details.dob.isoformat(),
            "tob": profile.birth_details.tob,
            "location": profile.birth_details.location
        },
        
        # Core chart data (always included)
        "ascendant": profile.ascendant,
        "ascendant_nakshatra": profile.ascendant_nakshatra,
        "moon_sign": profile.moon_sign,
        "moon_nakshatra": profile.moon_nakshatra,
        "sun_sign": profile.sun_sign,
        
        # Current dasha (always included)
        "mahadasha": _format_dasha(profile.current_mahadasha) if profile.current_mahadasha else None,
        "antardasha": _format_dasha(profile.current_antardasha) if profile.current_antardasha else None,
        
        # Topic-specific factors
        "focus_factors": _extract_focus_factors(profile, relevant_houses, relevant_planets),
        
        # Key rules firing
        "key_rules": _extract_key_rules(profile, transits, topic, key_factors_names),
        
        # Filtered transits relevant to topic
        "transits": _filter_transits_for_topic(transits, relevant_houses, today),
        
        # Planetary strengths (filtered to relevant planets)
        "planetary_strengths": _get_planetary_strengths(profile, relevant_planets),
        
        # Yogas (filtered to topic-relevant)
        "yogas": _filter_yogas_for_topic(profile.yogas, topic),
        
        # Time-based analysis
        "past_events": _analyze_past_events(profile, transits, topic, today) if mode in ["PAST_THEMES", "FOCUS_READING"] else [],
        "timing_windows": _analyze_timing_windows(profile, transits, topic, today),
    }
    
    logger.debug(f"Built features with {len(features['focus_factors'])} focus factors, {len(features['transits'])} transits")
    return features


def _format_dasha(dasha) -> Dict[str, Any]:
    """Format dasha info for LLM"""
    return {
        "planet": dasha.planet,
        "start_date": dasha.start_date.isoformat() if isinstance(dasha.start_date, date) else str(dasha.start_date),
        "end_date": dasha.end_date.isoformat() if isinstance(dasha.end_date, date) else str(dasha.end_date),
        "years_remaining": round(dasha.years_remaining, 1)
    }


def _extract_focus_factors(
    profile: AstroProfile,
    relevant_houses: List[int],
    relevant_planets: List[str]
) -> List[Dict[str, Any]]:
    """
    Extract chart factors relevant to the topic.
    
    For each relevant house and planet, extract:
    - House sign, lord, and occupants
    - Planet position, dignity, and strength
    """
    factors = []
    
    # House-based factors
    for house_num in relevant_houses:
        house = profile.get_house(house_num)
        if house:
            # Get lord's position
            lord = house.sign_lord
            lord_position = profile.get_planet(lord)
            
            factor = {
                "type": "house",
                "house": house_num,
                "sign": house.sign,
                "lord": lord,
                "lord_house": lord_position.house if lord_position else None,
                "lord_sign": lord_position.sign if lord_position else None,
                "lord_strength": lord_position.dignity if lord_position else None,
                "occupants": house.planets,
                "significance": _get_house_significance(house_num)
            }
            factors.append(factor)
    
    # Planet-based factors (resolve special names like "10th Lord")
    for planet_ref in relevant_planets:
        planet_name = _resolve_planet_reference(planet_ref, profile)
        if planet_name:
            planet = profile.get_planet(planet_name)
            if planet:
                factor = {
                    "type": "planet",
                    "planet": planet_name,
                    "reference": planet_ref,  # Original reference (e.g., "10th Lord")
                    "sign": planet.sign,
                    "house": planet.house,
                    "nakshatra": planet.nakshatra,
                    "dignity": planet.dignity,
                    "is_retrograde": planet.is_retrograde,
                    "is_combust": planet.is_combust,
                    "strength_score": planet.strength_score,
                    "significance": _get_planet_significance(planet_name)
                }
                factors.append(factor)
    
    return factors


def _resolve_planet_reference(ref: str, profile: AstroProfile) -> Optional[str]:
    """
    Resolve planet references like '10th Lord' to actual planet names.
    """
    # Direct planet names
    direct_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    if ref in direct_planets:
        return ref
    
    # Lord references (e.g., "10th Lord", "Lagna Lord")
    if 'Lord' in ref:
        if 'Lagna' in ref or '1st' in ref:
            return profile.get_house_lord(1)
        
        # Extract house number
        import re
        match = re.search(r'(\d+)', ref)
        if match:
            house_num = int(match.group(1))
            return profile.get_house_lord(house_num)
    
    # Transit planets (handled separately)
    if 'Transit' in ref:
        return None
    
    return None


def _get_house_significance(house_num: int) -> str:
    """Get the significance of a house"""
    significances = {
        1: "Self, personality, physical body, vitality",
        2: "Wealth, family, speech, values",
        3: "Siblings, courage, short travels, communication",
        4: "Home, mother, emotions, inner peace, property",
        5: "Intelligence, children, creativity, romance, education",
        6: "Enemies, diseases, debts, service, daily work",
        7: "Marriage, partnerships, business, public dealings",
        8: "Longevity, transformation, hidden matters, inheritance",
        9: "Fortune, dharma, higher learning, father, spirituality",
        10: "Career, reputation, status, public image, authority",
        11: "Gains, income, friends, aspirations, elder siblings",
        12: "Losses, expenses, foreign lands, moksha, isolation"
    }
    return significances.get(house_num, "")


def _get_planet_significance(planet: str) -> str:
    """Get the general significance of a planet"""
    significances = {
        "Sun": "Soul, authority, father, vitality, ego, government",
        "Moon": "Mind, emotions, mother, nurturing, public, liquids",
        "Mars": "Energy, courage, siblings, property, aggression, blood",
        "Mercury": "Intelligence, communication, business, skin, nervous system",
        "Jupiter": "Wisdom, expansion, teachers, children, dharma, wealth",
        "Venus": "Love, beauty, luxury, spouse, arts, vehicles, pleasures",
        "Saturn": "Discipline, delays, karma, longevity, service, restrictions",
        "Rahu": "Obsession, foreign, unconventional, sudden gains, illusion",
        "Ketu": "Spirituality, detachment, past karma, moksha, intuition"
    }
    return significances.get(planet, "")


def _extract_key_rules(
    profile: AstroProfile,
    transits: AstroTransits,
    topic: str,
    key_factors: List[str]
) -> List[Dict[str, Any]]:
    """
    Extract key astrological rules that are firing.
    These are specific combinations relevant to the topic.
    """
    rules = []
    
    # Saturn over Moon (emotional challenges)
    saturn = profile.get_planet("Saturn")
    moon = profile.get_planet("Moon")
    if saturn and moon:
        saturn_aspects_moon = _planets_aspect(saturn, moon)
        if saturn_aspects_moon:
            rules.append({
                "id": "SATURN_ASPECT_MOON",
                "meaning": "Saturn's aspect on Moon brings emotional discipline but can cause heaviness",
                "strength": "strong" if saturn.dignity in ['exalted', 'own'] else "medium",
                "planets": ["Saturn", "Moon"],
                "recommendation": "Practice emotional self-care; avoid overthinking"
            })
    
    # Jupiter aspects for blessings
    jupiter = profile.get_planet("Jupiter")
    if jupiter:
        levers = get_chart_levers(topic)
        for house_num in levers.get("houses", [])[:2]:  # Check top 2 relevant houses
            house = profile.get_house(house_num)
            if house and jupiter.house in _get_aspecting_houses(house_num):
                rules.append({
                    "id": f"JUPITER_ASPECT_{house_num}TH",
                    "meaning": f"Jupiter's aspect on {house_num}th house brings expansion and blessings",
                    "strength": "strong" if jupiter.dignity != 'debilitated' else "weak",
                    "planets": ["Jupiter"],
                    "house": house_num,
                    "recommendation": "Favorable period for growth in this area"
                })
    
    # Dasha-related rules
    if profile.current_mahadasha:
        maha_planet = profile.current_mahadasha.planet
        maha_position = profile.get_planet(maha_planet)
        if maha_position:
            rules.append({
                "id": f"MAHADASHA_{maha_planet.upper()}",
                "meaning": f"{maha_planet} Mahadasha emphasizes themes of {_get_planet_significance(maha_planet)}",
                "strength": "strong",
                "planets": [maha_planet],
                "house": maha_position.house,
                "years_remaining": profile.current_mahadasha.years_remaining
            })
    
    # Transit-based rules
    for event in transits.events[:5]:  # Top 5 significant transits
        if event.strength == "strong":
            rules.append({
                "id": f"TRANSIT_{event.planet.upper()}_{event.event_type.upper()}",
                "meaning": f"{event.planet} {event.event_type} affecting {event.to_sign or event.affected_house}",
                "strength": event.strength,
                "nature": event.nature,
                "time_window": f"{event.start_date} to {event.end_date}" if event.end_date else f"From {event.start_date}"
            })
    
    return rules


def _planets_aspect(planet1, planet2) -> bool:
    """Check if planet1 aspects planet2's house"""
    aspecting_houses = _get_aspecting_houses(planet1.house)
    return planet2.house in aspecting_houses


def _get_aspecting_houses(from_house: int) -> List[int]:
    """Get houses aspected from a given house (standard aspects)"""
    # All planets aspect 7th from their position
    aspects = [(from_house + 6) % 12 + 1]  # 7th aspect
    return aspects


def _filter_transits_for_topic(
    transits: AstroTransits,
    relevant_houses: List[int],
    today: date
) -> List[Dict[str, Any]]:
    """
    Filter transits to those relevant to the topic.
    """
    filtered = []
    
    # Time windows
    past_cutoff = today - timedelta(days=180)  # Past 6 months
    future_cutoff = today + timedelta(days=365)  # Next 12 months
    
    for event in transits.events:
        # Check if within relevant time window
        if event.start_date < past_cutoff:
            continue
        if event.start_date > future_cutoff:
            continue
        
        # Check if affects relevant houses
        if event.affected_house and event.affected_house in relevant_houses:
            filtered.append({
                "planet": event.planet,
                "event_type": event.event_type,
                "sign": event.to_sign,
                "affected_house": event.affected_house,
                "start_date": event.start_date.isoformat(),
                "end_date": event.end_date.isoformat() if event.end_date else None,
                "nature": event.nature,
                "strength": event.strength
            })
    
    return filtered[:10]  # Limit to top 10 most relevant


def _get_planetary_strengths(
    profile: AstroProfile,
    relevant_planets: List[str]
) -> List[Dict[str, Any]]:
    """
    Get strength information for relevant planets.
    """
    strengths = []
    
    for planet_ref in relevant_planets:
        planet_name = _resolve_planet_reference(planet_ref, profile)
        if planet_name:
            planet = profile.get_planet(planet_name)
            if planet:
                strengths.append({
                    "planet": planet_name,
                    "sign": planet.sign,
                    "dignity": planet.dignity,
                    "strength_score": planet.strength_score,
                    "is_retrograde": planet.is_retrograde,
                    "nakshatra": planet.nakshatra
                })
    
    return strengths


def _filter_yogas_for_topic(
    yogas: List,
    topic: str
) -> List[Dict[str, Any]]:
    """
    Filter yogas relevant to the topic.
    """
    # Yoga category to topic mapping
    topic_yoga_categories = {
        Topic.CAREER.value: ["raja", "pancha_mahapurusha"],
        Topic.MONEY.value: ["dhana"],
        Topic.ROMANTIC_RELATIONSHIPS.value: ["relationship"],
        Topic.MARRIAGE_PARTNERSHIP.value: ["relationship", "raja"],
        Topic.HEALTH_ENERGY.value: ["arishta"],
        Topic.SPIRITUALITY.value: ["sannyasa", "moksha"],
    }
    
    relevant_categories = topic_yoga_categories.get(topic, [])
    
    filtered = []
    for yoga in yogas:
        # Include if category matches or it's a general positive yoga
        if yoga.category in relevant_categories or yoga.category in ["raja", "dhana"]:
            filtered.append({
                "name": yoga.name,
                "category": yoga.category,
                "strength": yoga.strength,
                "effects": yoga.effects,
                "planets_involved": yoga.planets_involved
            })
    
    return filtered


def _analyze_past_events(
    profile: AstroProfile,
    transits: AstroTransits,
    topic: str,
    today: date
) -> List[Dict[str, Any]]:
    """
    Analyze past 18-24 months for topic-relevant events.
    """
    events = []
    past_start = today - timedelta(days=730)  # 2 years back
    
    # Get relevant houses for the topic
    levers = get_chart_levers(topic)
    relevant_houses = levers.get("houses", [])
    
    # Find past transits that affected relevant houses
    for transit in transits.events:
        if transit.start_date >= past_start and transit.start_date < today:
            if transit.affected_house in relevant_houses:
                events.append({
                    "period": transit.start_date.strftime("%B %Y"),
                    "planet": transit.planet,
                    "event_type": transit.event_type,
                    "house_affected": transit.affected_house,
                    "theme": _get_theme_for_house_transit(transit.planet, transit.affected_house),
                    "nature": transit.nature
                })
    
    # Add dasha-related past events
    if profile.current_mahadasha:
        events.append({
            "period": "Current Period",
            "planet": profile.current_mahadasha.planet,
            "event_type": "mahadasha",
            "theme": f"{profile.current_mahadasha.planet} period themes",
            "nature": "ongoing"
        })
    
    return events[:5]  # Top 5 events


def _get_theme_for_house_transit(planet: str, house: int) -> str:
    """Generate theme description for a transit"""
    themes = {
        ("Saturn", 10): "Career restructuring, professional challenges",
        ("Saturn", 7): "Relationship testing, commitment decisions",
        ("Jupiter", 10): "Career expansion, recognition opportunities",
        ("Jupiter", 2): "Financial growth, value reassessment",
        ("Rahu", 10): "Unconventional career moves, ambition surge",
        ("Mars", 10): "Career drive, potential conflicts at work",
    }
    return themes.get((planet, house), f"{planet} influence on {_get_house_significance(house).split(',')[0]}")


def _analyze_timing_windows(
    profile: AstroProfile,
    transits: AstroTransits,
    topic: str,
    today: date
) -> List[Dict[str, Any]]:
    """
    Identify favorable and challenging timing windows.
    """
    windows = []
    future_end = today + timedelta(days=545)  # ~18 months
    
    # Get relevant houses
    levers = get_chart_levers(topic)
    relevant_houses = levers.get("houses", [])
    
    # Analyze upcoming transits
    for transit in transits.events:
        if transit.start_date >= today and transit.start_date <= future_end:
            if transit.affected_house in relevant_houses and transit.strength == "strong":
                nature = "favorable" if transit.nature == "beneficial" else "challenging" if transit.nature == "malefic" else "mixed"
                windows.append({
                    "period": f"{transit.start_date.strftime('%B %Y')} - {transit.end_date.strftime('%B %Y') if transit.end_date else 'ongoing'}",
                    "nature": nature,
                    "trigger": f"{transit.planet} {transit.event_type}",
                    "house": transit.affected_house,
                    "activity": _suggest_activity_for_window(transit.planet, transit.affected_house, nature)
                })
    
    # Add dasha timing
    if profile.current_antardasha:
        windows.append({
            "period": f"Current Antardasha ({profile.current_antardasha.planet})",
            "nature": "ongoing",
            "trigger": f"{profile.current_mahadasha.planet}-{profile.current_antardasha.planet} period",
            "activity": "Themes of both planets are active"
        })
    
    return windows[:6]  # Top 6 windows


def _suggest_activity_for_window(planet: str, house: int, nature: str) -> str:
    """Suggest activity based on timing window"""
    if nature == "favorable":
        return "Good time for new initiatives and decisions"
    elif nature == "challenging":
        return "Focus on consolidation and careful planning"
    else:
        return "Mixed results - proceed with awareness"
