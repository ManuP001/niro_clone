"""Reading Evidence Pack Builder - GLOBAL SCORE-BASED DRIVER SELECTION

Implements GLOBAL SCORE-BASED signal selection pipeline (v3):
1. Collect → Gather all candidate signals
2. Resolve Topic Lords → Convert "4th Lord", "10th Lord" to actual planets for user's chart
3. Time Layer Classification → Mark signals as static_natal or time_layer
4. Role Assignment → Assign TOPIC_DRIVER / TIME_DRIVER / BASELINE_CONTEXT / NOISE
5. Global Scoring → Score ALL signals with TIME RELEVANCE BOOST for time-specific queries
6. Driver Selection → Select top 3 by score_final (NOT by role quotas)
   - Soft diversity: max 2 drivers per planet
   - Exclude BASELINE_CONTEXT from drivers (unless topic = general/life_overview)
   - Mahadasha only if planet ∈ resolved_topic_planets OR rules topic house AND ranks in global top 3
   - REQUIRE at least 1 time-layer driver for past/future queries when data exists
7. Render → Human-readable output for Trust Widget

Key Changes from v2:
- Time-layer signals get scoring boost when query specifies year/range
- Debug includes: is_static_natal, is_time_layer, time_period, query_year
- Past vs future queries now yield different drivers when time data exists
- time_data_missing flag when no time-layer signals available

SINGLE SOURCE OF TRUTH: All topic→house/planet mappings come from topics.py
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from enum import Enum
import logging
import re
from datetime import datetime, date

# Import topic mappings from SINGLE SOURCE OF TRUTH
from .topics import get_topic_houses_and_planets, resolve_topic_planets, Topic, REAL_PLANETS

logger = logging.getLogger(__name__)


# ============================================================================
# SIGNAL ROLE ENUM
# ============================================================================

class SignalRole(str, Enum):
    """Signal roles for quota enforcement"""
    TOPIC_DRIVER = "TOPIC_DRIVER"       # Directly tied to topic houses/planets
    TIME_DRIVER = "TIME_DRIVER"         # Dasha/transit for timing context
    BASELINE_CONTEXT = "BASELINE_CONTEXT"  # Lagna lord, Moon, baseline traits
    CONTRAST_SIGNAL = "CONTRAST_SIGNAL"    # Opposing indicator (optional)
    NOISE = "NOISE"                      # Everything else, excluded


# Global storage for candidate signals debug (keyed by run_id)
_candidate_signals_cache: Dict[str, Dict[str, Any]] = {}


def store_candidate_signals_debug(run_id: str, data: Dict[str, Any]) -> None:
    """Store candidate signals debug data in cache."""
    _candidate_signals_cache[run_id] = data
    # Keep only last 100 entries to prevent memory bloat
    if len(_candidate_signals_cache) > 100:
        oldest_keys = sorted(_candidate_signals_cache.keys(), 
                            key=lambda k: _candidate_signals_cache[k].get('timestamp', ''))[:50]
        for k in oldest_keys:
            del _candidate_signals_cache[k]


def get_candidate_signals_debug(run_id: str) -> Optional[Dict[str, Any]]:
    """Get candidate signals debug data for a specific run."""
    return _candidate_signals_cache.get(run_id)


def get_latest_candidate_signals_debug(user_id: str = None) -> Optional[Dict[str, Any]]:
    """Get the most recent candidate signals debug data."""
    if not _candidate_signals_cache:
        return None
    
    latest = None
    latest_ts = None
    for run_id, data in _candidate_signals_cache.items():
        if user_id and data.get('user_id') != user_id:
            continue
        ts = data.get('timestamp')
        if ts and (latest_ts is None or ts > latest_ts):
            latest = data
            latest_ts = ts
    return latest


# Baseline planets that provide emotional/contextual tone (NOT topic-specific)
BASELINE_PLANETS = {"Moon", "Lagna Lord", "Ascendant"}

# Sign lords for house lord calculation
SIGN_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
    'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}


# ============================================================================
# SIGNAL EXTRACTION HELPERS
# ============================================================================

def _extract_planet_from_signal(signal: Dict[str, Any]) -> str:
    """Extract planet name from signal evidence or claim."""
    planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    
    evidence = signal.get('evidence', {})
    
    # Try evidence.planet first
    if isinstance(evidence, dict):
        planet = evidence.get('planet', '')
        if planet:
            for p in planets:
                if p.lower() == planet.lower():
                    return p
            return planet.title()
    
    claim = signal.get('claim', '')
    
    # Try to extract planet from claim
    for p in planets:
        if p.lower() in claim.lower():
            return p
    
    # Check applies_to for planet hints
    applies_to = signal.get('applies_to', '')
    for p in planets:
        if p.lower() in applies_to.lower():
            return p
    
    return 'Unknown'


def _extract_house_from_signal(signal: Dict[str, Any]) -> Optional[int]:
    """Extract house number from signal evidence."""
    evidence = signal.get('evidence', {})
    if isinstance(evidence, dict):
        house = evidence.get('house')
        if house:
            try:
                return int(house)
            except (ValueError, TypeError):
                pass
    return None


def _humanize_signal_text(signal: Dict[str, Any]) -> str:
    """Generate human-readable text for a signal."""
    sig_type = signal.get('type', 'rule')
    claim = signal.get('claim', '')
    polarity = signal.get('polarity', 'mixed')
    
    planet = _extract_planet_from_signal(signal)
    house = _extract_house_from_signal(signal)
    
    if sig_type == 'dasha':
        return f"{planet} Dasha period - {polarity} influence"
    elif sig_type == 'transit':
        if house:
            return f"{planet} transiting {house}th house - {polarity} effects"
        return f"{planet} transit - {polarity} influence"
    elif sig_type == 'yoga':
        return f"Yoga formed by {planet} - {claim}"
    elif sig_type == 'planet_position':
        if house:
            return f"{planet} placed in {house}th house of your chart"
        return f"{planet} natal position - {polarity}"
    elif sig_type == 'planet_strength':
        if house:
            return f"{planet} in {house}th house - strength indicator"
        return f"{planet} strength/dignity - {polarity}"
    else:
        return claim or f"{planet} {sig_type} - {polarity}"


def _planet_rules_topic_house(planet: str, topic_houses: List[int], astro_features: Dict[str, Any]) -> bool:
    """
    Check if a planet rules any of the topic houses based on the chart.
    
    Args:
        planet: Planet name (e.g., 'Jupiter')
        topic_houses: List of house numbers relevant to the topic
        astro_features: Astro features containing house data
        
    Returns:
        True if planet rules any topic house
    """
    if not planet or not topic_houses:
        return False
    
    houses_data = astro_features.get('houses', [])
    
    for house_info in houses_data:
        house_num = house_info.get('number') or house_info.get('house')
        if house_num and int(house_num) in topic_houses:
            # Check if this planet is the lord of this house
            house_lord = house_info.get('lord', '')
            house_sign = house_info.get('sign', '')
            
            # Direct lord match
            if house_lord and planet.lower() == house_lord.lower():
                return True
            
            # Sign-based lord lookup
            if house_sign:
                sign_lord = SIGN_LORDS.get(house_sign, '')
                if sign_lord and planet.lower() == sign_lord.lower():
                    return True
    
    return False


# ============================================================================
# TIME LAYER CLASSIFICATION AND PERIOD EXTRACTION
# ============================================================================

# Static natal signal types (unchanging, based on birth chart)
STATIC_NATAL_TYPES = {'planet_position', 'planet_strength', 'yoga', 'rule'}

# Time layer signal types (change over time - dasha, transits)
TIME_LAYER_TYPES = {'dasha', 'transit'}


def extract_query_year(user_question: str) -> Optional[int]:
    """
    Extract a specific year from the user's question.
    
    Patterns matched:
    - "in 2022", "in 2026"
    - "2022", "2026" standalone
    - "during 2023"
    - "for 2024"
    - "year 2025"
    
    Returns:
        Year as int, or None if no year found
    """
    if not user_question:
        return None
    
    # Common year patterns
    patterns = [
        r'\b(?:in|during|for|year)\s*(\d{4})\b',  # "in 2022", "during 2023"
        r'\b(\d{4})\b',  # standalone year like "2022"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, user_question, re.IGNORECASE)
        for match in matches:
            try:
                year = int(match)
                # Valid year range: 1900-2100
                if 1900 <= year <= 2100:
                    return year
            except ValueError:
                continue
    
    return None


def extract_time_range(user_question: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Extract year range from user question (e.g., "2022-2024", "between 2020 and 2023").
    
    Returns:
        (start_year, end_year) or (None, None)
    """
    if not user_question:
        return None, None
    
    # Range patterns
    patterns = [
        r'(\d{4})\s*[-–to]\s*(\d{4})',  # "2022-2024" or "2022 to 2024"
        r'between\s*(\d{4})\s*(?:and|&)\s*(\d{4})',  # "between 2020 and 2023"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_question, re.IGNORECASE)
        if match:
            try:
                start = int(match.group(1))
                end = int(match.group(2))
                if 1900 <= start <= 2100 and 1900 <= end <= 2100:
                    return start, end
            except ValueError:
                continue
    
    # If single year found, use it as both start and end
    single_year = extract_query_year(user_question)
    if single_year:
        return single_year, single_year
    
    return None, None


def classify_signal_time_layer(signal: Dict[str, Any]) -> Tuple[bool, bool, Optional[str]]:
    """
    Classify a signal as static_natal or time_layer.
    
    Args:
        signal: Signal dict with 'type', 'evidence', etc.
        
    Returns:
        (is_static_natal: bool, is_time_layer: bool, time_period: Optional[str])
        
        time_period format: "YYYY" or "YYYY-YYYY" or None
    """
    sig_type = signal.get('type', '')
    evidence = signal.get('evidence', {})
    
    is_static_natal = sig_type in STATIC_NATAL_TYPES
    is_time_layer = sig_type in TIME_LAYER_TYPES
    
    # Extract time period from evidence
    time_period = None
    
    if is_time_layer and isinstance(evidence, dict):
        start_date = evidence.get('start_date')
        end_date = evidence.get('end_date')
        
        start_year = None
        end_year = None
        
        # Parse start date
        if start_date:
            if isinstance(start_date, (date, datetime)):
                start_year = start_date.year
            elif isinstance(start_date, str):
                try:
                    start_year = int(start_date[:4])
                except (ValueError, IndexError):
                    pass
        
        # Parse end date
        if end_date:
            if isinstance(end_date, (date, datetime)):
                end_year = end_date.year
            elif isinstance(end_date, str):
                try:
                    end_year = int(end_date[:4])
                except (ValueError, IndexError):
                    pass
        
        if start_year and end_year:
            if start_year == end_year:
                time_period = str(start_year)
            else:
                time_period = f"{start_year}-{end_year}"
        elif start_year:
            time_period = f"{start_year}-ongoing"
    
    return is_static_natal, is_time_layer, time_period


def check_dasha_overlaps_query_year(dasha_data: Dict[str, Any], query_year: Optional[int]) -> Tuple[bool, Optional[str]]:
    """
    Check if a dasha period overlaps with the query year.
    
    Args:
        dasha_data: Dict with start_date, end_date keys
        query_year: Year extracted from user question (e.g., 2022)
        
    Returns:
        (overlaps: bool, overlap_window: Optional[str])
        overlap_window format: "2020-2036" or None
    """
    if not query_year or not dasha_data:
        return False, None
    
    start_date = dasha_data.get('start_date')
    end_date = dasha_data.get('end_date')
    
    start_year = None
    end_year = None
    
    # Parse start date
    if start_date:
        if isinstance(start_date, (date, datetime)):
            start_year = start_date.year
        elif isinstance(start_date, str):
            try:
                start_year = int(start_date[:4])
            except (ValueError, IndexError):
                pass
    
    # Parse end date
    if end_date:
        if isinstance(end_date, (date, datetime)):
            end_year = end_date.year
        elif isinstance(end_date, str):
            try:
                end_year = int(end_date[:4])
            except (ValueError, IndexError):
                pass
    
    if start_year and end_year:
        overlaps = start_year <= query_year <= end_year
        overlap_window = f"{start_year}-{end_year}"
        return overlaps, overlap_window
    elif start_year:
        # Ongoing dasha - check if query year is after start
        overlaps = query_year >= start_year
        overlap_window = f"{start_year}-ongoing"
        return overlaps, overlap_window
    
    return False, None


def signal_matches_query_time(signal: Dict[str, Any], query_year: Optional[int], time_context: str) -> Tuple[bool, float]:
    """
    Check if a time-layer signal matches the query's time period.
    
    Returns:
        (matches: bool, relevance_score: float 0.0-1.0)
        
        relevance_score:
        - 1.0: Signal's time period includes/matches query year exactly
        - 0.7: Signal overlaps with query time context (past/future direction matches)
        - 0.3: Signal is time-layer but doesn't match specific year
        - 0.0: Not a time-layer signal
    """
    sig_type = signal.get('type', '')
    evidence = signal.get('evidence', {})
    
    # Not a time-layer signal
    if sig_type not in TIME_LAYER_TYPES:
        return False, 0.0
    
    if not isinstance(evidence, dict):
        return True, 0.3  # Time-layer but no date info
    
    start_date = evidence.get('start_date')
    end_date = evidence.get('end_date')
    
    # Parse years
    start_year = None
    end_year = None
    
    if start_date:
        if isinstance(start_date, (date, datetime)):
            start_year = start_date.year
        elif isinstance(start_date, str):
            try:
                start_year = int(start_date[:4])
            except (ValueError, IndexError):
                pass
    
    if end_date:
        if isinstance(end_date, (date, datetime)):
            end_year = end_date.year
        elif isinstance(end_date, str):
            try:
                end_year = int(end_date[:4])
            except (ValueError, IndexError):
                pass
    
    current_year = datetime.now().year
    
    # If query has specific year
    if query_year:
        if start_year and end_year:
            # Signal covers query year
            if start_year <= query_year <= end_year:
                return True, 1.0
            # Close but not exact
            elif abs(query_year - start_year) <= 2 or abs(query_year - end_year) <= 2:
                return True, 0.6
        elif start_year:
            # Ongoing signal - check if query year is after start
            if query_year >= start_year:
                return True, 0.8
            elif abs(query_year - start_year) <= 2:
                return True, 0.5
        
        return True, 0.3  # Time-layer but doesn't match year
    
    # If no specific year, check time_context direction
    if time_context == 'past':
        # Past signals: end before current year or started before current year
        if end_year and end_year < current_year:
            return True, 0.8
        elif start_year and start_year < current_year:
            return True, 0.7
    elif time_context == 'future':
        # Future signals: start after current year or ongoing into future
        if start_year and start_year >= current_year:
            return True, 0.9
        elif end_year and end_year > current_year:
            return True, 0.7
    elif time_context in ('present', 'timeless'):
        # Present/timeless: current signals
        if start_year and end_year:
            if start_year <= current_year <= end_year:
                return True, 0.9
        elif start_year and start_year <= current_year:
            return True, 0.8
    
    return True, 0.5  # Default time-layer relevance


# ============================================================================
# ROLE ASSIGNMENT FUNCTION (with resolved topic planets)
# ============================================================================

def assign_signal_role(
    signal: Dict[str, Any],
    topic: str,
    time_context: str,
    topic_houses: List[int],
    resolved_topic_planets: List[str],
    is_general_topic: bool = False
) -> tuple:
    """
    Assign a role to a signal based on query context.
    
    UPDATED: Uses resolved_topic_planets (actual planet names like "Sun", "Mars")
    instead of abstract references like "4th Lord".
    
    Role Assignment Rules:
    A. TOPIC_DRIVER: Signal's planet ∈ resolved_topic_planets OR house ∈ topic_houses
    B. TIME_DRIVER: Dasha/transit for relevant time direction
    C. BASELINE_CONTEXT: Lagna lord/Moon baseline traits (not directly topic-linked)
    D. NOISE: Everything else
    
    Args:
        signal: The signal to classify
        topic: Query topic (career, relationship, etc.)
        time_context: Time direction (past, present, future, timeless)
        topic_houses: List of relevant houses for topic
        resolved_topic_planets: List of RESOLVED actual planet names for topic
        is_general_topic: True if topic is general/life_overview
        
    Returns:
        (role: SignalRole, role_reason: str)
    """
    sig_type = signal.get('type', '')
    planet = signal.get('planet', _extract_planet_from_signal(signal))
    house = signal.get('house', _extract_house_from_signal(signal))
    claim = signal.get('claim', '').lower()
    
    # Check topic relevance with RESOLVED planets
    is_topic_house = house and house in topic_houses
    is_topic_planet = planet in resolved_topic_planets  # Now uses resolved actual planets
    is_baseline_planet = planet in {'Moon', 'Lagna Lord', 'Ascendant'}
    is_unknown_planet = planet in ('Unknown', 'Mixed', '')
    
    # Check time relevance
    is_dasha = sig_type == 'dasha'
    is_transit = sig_type == 'transit'
    is_current_ongoing = 'current' in claim or 'ongoing' in claim or 'active' in claim
    
    # NEW: Check for past time overlap (Mahadasha included via time overlap for past queries)
    has_time_overlap = signal.get('time_overlap', False)
    
    # Rule A: TOPIC_DRIVER
    # Signal's planet matches resolved topic planets OR house matches topic houses
    if is_topic_house or is_topic_planet:
        if is_topic_house and is_topic_planet:
            reason = f"planet={planet} in topic house {house}, matches resolved topic planet"
        elif is_topic_house:
            reason = f"signal in topic house {house}"
        else:
            reason = f"planet={planet} is resolved karaka for {topic}"
        return SignalRole.TOPIC_DRIVER, reason
    
    # Rule A2 (NEW): TIME_DRIVER for dasha with time_overlap on past queries
    # This ensures Mahadasha included via past_time_overlap gets TIME_DRIVER role
    if is_dasha and has_time_overlap and time_context == 'past':
        overlap_window = signal.get('overlap_window', 'unknown')
        return SignalRole.TIME_DRIVER, f"dasha with time_overlap for past query (planet={planet}, window={overlap_window})"
    
    # Rule B: TIME_DRIVER
    # Dasha/transit for relevant time direction
    if is_dasha:
        if time_context == 'past':
            # For past: allow dasha only if NOT current/ongoing
            if not is_current_ongoing:
                return SignalRole.TIME_DRIVER, f"dasha signal for past context (planet={planet})"
            # Current ongoing dasha should not be TIME_DRIVER for past questions
        elif time_context in ('present', 'timeless'):
            return SignalRole.TIME_DRIVER, f"dasha signal for present/timeless (planet={planet})"
        elif time_context == 'future':
            return SignalRole.TIME_DRIVER, f"dasha signal for future timing (planet={planet})"
    
    if is_transit:
        if time_context == 'past':
            # Skip transit for past unless explicitly supported
            pass  # Will fall through to NOISE or BASELINE
        elif time_context in ('present', 'future', 'timeless'):
            return SignalRole.TIME_DRIVER, f"transit signal for {time_context} (planet={planet})"
    
    # Rule C: BASELINE_CONTEXT
    # Lagna lord / Moon / baseline traits but not directly topic-linked
    if is_baseline_planet and not is_unknown_planet:
        return SignalRole.BASELINE_CONTEXT, f"baseline planet={planet} for emotional context"
    
    # Mahadasha lord as baseline (if not topic-relevant AND no time_overlap)
    if 'mahadasha' in claim and not is_topic_planet and not has_time_overlap:
        return SignalRole.BASELINE_CONTEXT, "mahadasha lord as baseline context (not topic planet)"
    
    # Natal position can be baseline if not topic-relevant
    if sig_type == 'planet_position' and not is_topic_house and not is_topic_planet:
        if not is_unknown_planet:
            return SignalRole.BASELINE_CONTEXT, f"natal {planet} as background context"
    
    # Rule D: NOISE - everything else
    if is_unknown_planet:
        return SignalRole.NOISE, "unknown planet, classified as noise"
    
    return SignalRole.NOISE, f"no role match for {sig_type} {planet}"


# ============================================================================
# GLOBAL SCORING (with TIME RELEVANCE BOOST) - v3
# ============================================================================

def _score_signal_globally(
    signal: Dict[str, Any],
    role: SignalRole,
    topic: str,
    time_context: str,
    recent_planets: Set[str],
    topic_houses: List[int],
    resolved_topic_planets: List[str],
    query_year: Optional[int] = None
) -> tuple:
    """
    Score a signal GLOBALLY based on topic relevance, signal quality, and TIME RELEVANCE.
    
    UPDATED v3: Includes TIME RELEVANCE BOOST for time-specific queries.
    Time-layer signals (dasha/transit) get significant boost when query specifies year/range.
    
    Base scoring factors:
    - Topic house match: +0.30 (primary house) / +0.20 (secondary)
    - Topic planet match: +0.25 (resolved karaka)
    - Signal type bonus: dasha +0.15, transit +0.10, planet_position +0.08
    - Time alignment: +0.15 if time_context matches signal nature
    
    TIME RELEVANCE BOOST (NEW):
    - +0.35 if time-layer signal matches query year exactly
    - +0.25 if time-layer signal overlaps with query time direction
    - +0.15 if time-layer signal for past/future but no specific year match
    
    Penalties:
    - Static natal penalty: -0.10 for past/future queries when time-layer exists
    - Repetition: -0.10 if planet was recently used
    - Past context mismatch: -0.15 if asking about past but signal is "current"
    - Unknown planet: -0.30
    
    Returns (score, scoring_breakdown).
    """
    breakdown = {}
    score = 0.20  # Base score for any valid signal
    breakdown["base"] = 0.20
    breakdown["role"] = role.value
    
    sig_type = signal.get('type', '')
    planet = signal.get('planet', _extract_planet_from_signal(signal))
    house = signal.get('house', _extract_house_from_signal(signal))
    claim = signal.get('claim', '').lower()
    
    # Classify signal time layer
    is_static_natal, is_time_layer, time_period = classify_signal_time_layer(signal)
    breakdown["is_static_natal"] = is_static_natal
    breakdown["is_time_layer"] = is_time_layer
    breakdown["time_period"] = time_period
    
    # ========================================================================
    # TOPIC RELEVANCE BONUSES (most important for driver selection)
    # ========================================================================
    
    # Topic house match
    if house and house in topic_houses:
        if topic_houses and house == topic_houses[0]:
            score += 0.30  # Primary topic house
            breakdown["primary_house_bonus"] = 0.30
        else:
            score += 0.20  # Secondary topic house
            breakdown["secondary_house_bonus"] = 0.20
    
    # Topic planet match (using RESOLVED planets)
    if planet in resolved_topic_planets:
        if resolved_topic_planets and planet == resolved_topic_planets[0]:
            score += 0.25  # Primary karaka
            breakdown["primary_karaka_bonus"] = 0.25
        else:
            score += 0.15  # Secondary karaka
            breakdown["secondary_karaka_bonus"] = 0.15
    
    # ========================================================================
    # SIGNAL TYPE BONUSES
    # ========================================================================
    
    if sig_type == 'dasha':
        score += 0.15
        breakdown["dasha_type_bonus"] = 0.15
        
        # Extra bonus if dasha planet is topic-relevant
        if planet in resolved_topic_planets:
            score += 0.10
            breakdown["dasha_topic_planet_bonus"] = 0.10
            
    elif sig_type == 'transit':
        score += 0.10
        breakdown["transit_type_bonus"] = 0.10
        
    elif sig_type == 'planet_position':
        score += 0.08
        breakdown["position_type_bonus"] = 0.08
        
    elif sig_type == 'yoga':
        score += 0.12
        breakdown["yoga_type_bonus"] = 0.12
    
    # ========================================================================
    # TIME RELEVANCE BOOST (NEW - critical for past vs future differentiation)
    # ========================================================================
    
    if is_time_layer:
        matches_time, time_relevance = signal_matches_query_time(signal, query_year, time_context)
        breakdown["time_matches_query"] = matches_time
        breakdown["time_relevance_score"] = round(time_relevance, 2)
        
        # Significant boost for time-layer signals matching query time
        if time_relevance >= 0.9:
            score += 0.35  # Exact match or very close
            breakdown["time_exact_match_boost"] = 0.35
        elif time_relevance >= 0.7:
            score += 0.25  # Good overlap with query direction
            breakdown["time_direction_match_boost"] = 0.25
        elif time_relevance >= 0.5:
            score += 0.15  # Time-layer but not perfect match
            breakdown["time_layer_base_boost"] = 0.15
        else:
            score += 0.08  # Minimal time-layer bonus
            breakdown["time_layer_minimal_boost"] = 0.08
    
    # Penalize static natal signals for time-specific queries
    if is_static_natal and time_context in ('past', 'future') and query_year:
        score -= 0.12  # Static natal less relevant for time-specific queries
        breakdown["static_natal_time_penalty"] = -0.12
    
    # ========================================================================
    # PAST QUERY TIME OVERLAP BOOST (for Mahadasha covering query year)
    # ========================================================================
    
    # Check if signal has explicit time_overlap flag (from Mahadasha/Antardasha gating)
    has_time_overlap = signal.get('time_overlap', False)
    overlap_window = signal.get('overlap_window')
    
    if has_time_overlap and time_context == 'past' and query_year:
        # Significant boost for dasha signals that cover the past query year
        score += 0.30  # Strong boost for time overlap
        breakdown["past_time_overlap_boost"] = 0.30
        breakdown["overlap_window"] = overlap_window
        logger.debug(f"[SCORING] {planet} gets past_time_overlap_boost: window={overlap_window} covers {query_year}")
    
    breakdown["time_overlap"] = has_time_overlap
    
    # ========================================================================
    # TIME ALIGNMENT BONUSES
    # ========================================================================
    
    if time_context in ('present', 'timeless') and sig_type == 'dasha':
        score += 0.10
        breakdown["time_dasha_alignment"] = 0.10
        
    elif time_context == 'future' and sig_type == 'transit':
        score += 0.12
        breakdown["time_transit_alignment"] = 0.12
    
    # ========================================================================
    # PENALTIES
    # ========================================================================
    
    # Repetition penalty if same planet used recently
    if planet in recent_planets:
        score -= 0.10
        breakdown["repetition_penalty"] = -0.10
    
    # Past context mismatch
    if time_context == 'past' and ('current' in claim or 'ongoing' in claim):
        score -= 0.15
        breakdown["past_current_penalty"] = -0.15
    
    # Unknown/invalid planet penalty
    if planet in ('Unknown', 'Mixed', ''):
        score -= 0.30
        breakdown["unknown_planet_penalty"] = -0.30
    
    # ========================================================================
    # ROLE-SPECIFIC ADJUSTMENTS (minor - roles still inform relevance)
    # ========================================================================
    
    # TOPIC_DRIVER gets slight boost (already high from house/planet matches)
    if role == SignalRole.TOPIC_DRIVER:
        score += 0.05
        breakdown["topic_driver_role_bonus"] = 0.05
        
    # TIME_DRIVER reasonable for timing questions
    elif role == SignalRole.TIME_DRIVER:
        if time_context in ('future', 'present'):
            score += 0.05
            breakdown["time_driver_role_bonus"] = 0.05
    
    # BASELINE_CONTEXT gets NO bonus (should not dominate drivers for specific topics)
    # NOISE stays low
    
    # Clamp to [0, 1]
    score = max(0.0, min(1.0, score))
    breakdown["final"] = round(score, 3)
    
    return score, breakdown


# ============================================================================
# GLOBAL SCORE-BASED DRIVER SELECTION (with TIME-LAYER REQUIREMENT)
# ============================================================================

MAX_SIGNALS_PER_PLANET = 2  # Soft diversity: max 2 drivers from same planet
MAX_DRIVERS = 3  # Max drivers to show in Trust Widget


def select_drivers_by_global_score(
    all_signals: List[Dict[str, Any]],
    is_general_topic: bool,
    resolved_topic_planets: List[str],
    topic_houses: List[int],
    astro_features: Dict[str, Any],
    time_context: str = 'timeless',
    query_year: Optional[int] = None
) -> tuple:
    """
    Select top 3 drivers by global score with TIME-LAYER REQUIREMENT for past/future.
    
    RULES (v3 - updated):
    1. Select top 3 by score_final across ALL signals
    2. Exclude BASELINE_CONTEXT from drivers unless topic = general/life_overview
    3. Enforce soft diversity: max 2 drivers per planet
    4. Mahadasha enters drivers only if:
       - planet ∈ resolved_topic_planets, OR
       - planet rules a topic house AND ranks in global top 3
    5. NO fallback that fills drivers with baseline just to reach 3
    6. NEW: For past/future queries, REQUIRE at least 1 time-layer driver when available
    
    Args:
        all_signals: All scored signals sorted by score_final descending
        is_general_topic: True if topic is general/life_overview/daily_guidance/self_psychology
        resolved_topic_planets: List of resolved actual planet names for topic
        topic_houses: List of relevant houses for topic
        astro_features: For checking if planet rules a topic house
        time_context: Time context (past, present, future, timeless)
        query_year: Specific year from query (e.g., 2022, 2026)
        
    Returns:
        (drivers: List[Dict], selection_log: List[str], time_layer_stats: Dict)
    """
    drivers = []
    selection_log = []
    planet_counts: Dict[str, int] = {}
    
    # Sort all signals by score_final descending
    sorted_signals = sorted(all_signals, key=lambda s: s.get('score_final', 0), reverse=True)
    
    # ========================================================================
    # TIME-LAYER ANALYSIS
    # ========================================================================
    time_layer_signals = [s for s in sorted_signals if s.get('_scoring_breakdown', {}).get('is_time_layer', False)]
    static_natal_signals = [s for s in sorted_signals if s.get('_scoring_breakdown', {}).get('is_static_natal', False)]
    
    has_time_layer_data = len(time_layer_signals) > 0
    time_data_missing = not has_time_layer_data and time_context in ('past', 'future')
    
    # For past/future queries, we REQUIRE at least 1 time-layer driver if data exists
    require_time_layer = time_context in ('past', 'future') and has_time_layer_data
    time_layer_driver_count = 0
    
    selection_log.append(f"TIME_LAYER_ANALYSIS: time_context={time_context}, query_year={query_year}, "
                        f"time_layer_count={len(time_layer_signals)}, static_natal_count={len(static_natal_signals)}, "
                        f"require_time_layer={require_time_layer}, time_data_missing={time_data_missing}")
    
    # Log top 5 candidates for debugging
    top_5_preview = []
    for s in sorted_signals[:5]:
        breakdown = s.get('_scoring_breakdown', {})
        layer = 'T' if breakdown.get('is_time_layer') else 'N'
        top_5_preview.append(f"{s.get('planet', '?')}[{layer}]({s.get('role', '?')[:4]})={s.get('score_final', 0):.2f}")
    selection_log.append(f"Top 5 candidates: {', '.join(top_5_preview)}")
    
    # ========================================================================
    # FIRST PASS: Select drivers prioritizing time-layer for past/future
    # ========================================================================
    
    for signal in sorted_signals:
        if len(drivers) >= MAX_DRIVERS:
            break
        
        planet = signal.get('planet', 'Unknown')
        role = signal.get('role', 'NOISE')
        sig_type = signal.get('type', '')
        score = signal.get('score_final', 0)
        claim = signal.get('claim', '').lower()
        breakdown = signal.get('_scoring_breakdown', {})
        is_time_layer = breakdown.get('is_time_layer', False)
        
        # RULE 1: Skip unknown/invalid planets
        if planet in ('Unknown', 'Mixed', ''):
            selection_log.append(f"SKIP {planet}: invalid planet")
            continue
        
        # RULE 2: Skip NOISE role
        if role == SignalRole.NOISE.value:
            selection_log.append(f"SKIP {planet}: NOISE role")
            continue
        
        # RULE 3: Exclude BASELINE_CONTEXT unless general/life_overview topic
        if role == SignalRole.BASELINE_CONTEXT.value and not is_general_topic:
            selection_log.append(f"SKIP {planet}: BASELINE_CONTEXT excluded for specific topic")
            continue
        
        # RULE 4: Mahadasha special gating
        if sig_type == 'dasha' and 'mahadasha' in claim:
            # Check if this Mahadasha was included via time_overlap override
            has_time_overlap = signal.get('time_overlap', False)
            
            # If time_overlap=True (included for past query), SKIP topic-relevance gating
            if has_time_overlap:
                selection_log.append(
                    f"ALLOW Mahadasha {planet}: time_overlap override (window={signal.get('overlap_window')})"
                )
            else:
                # Mahadasha only enters drivers if:
                # a) planet ∈ resolved_topic_planets, OR
                # b) planet rules a topic house AND currently ranks in global top 3
                
                planet_is_topic_relevant = planet in resolved_topic_planets
                planet_rules_topic_house = _planet_rules_topic_house(planet, topic_houses, astro_features)
                
                # Check if this would be in top 3 by score (already sorted, so position matters)
                current_position = len(drivers) + 1
                is_top_3_by_score = current_position <= 3
                
                if not planet_is_topic_relevant and not (planet_rules_topic_house and is_top_3_by_score):
                    selection_log.append(
                        f"SKIP Mahadasha {planet}: not topic-relevant "
                        f"(topic_planet={planet_is_topic_relevant}, rules_house={planet_rules_topic_house}, top3={is_top_3_by_score})"
                    )
                    continue
                else:
                    selection_log.append(
                        f"ALLOW Mahadasha {planet}: topic_planet={planet_is_topic_relevant}, "
                        f"rules_house={planet_rules_topic_house}"
                    )
        
        # RULE 5: Soft diversity - max 2 drivers per planet
        current_count = planet_counts.get(planet, 0)
        if current_count >= MAX_SIGNALS_PER_PLANET:
            selection_log.append(f"SKIP {planet}: diversity limit ({current_count} already)")
            continue
        
        # RULE 6: For past/future, check time-layer requirement
        # If we need time-layer and haven't got one yet, defer static natal signals
        if require_time_layer and not is_time_layer and time_layer_driver_count == 0 and len(drivers) >= 2:
            # We're about to fill the 3rd slot without any time-layer driver
            # Check if there's a time-layer signal we can use instead
            available_time_layer = None
            for tl_signal in time_layer_signals:
                tl_planet = tl_signal.get('planet', 'Unknown')
                tl_role = tl_signal.get('role', 'NOISE')
                if tl_planet not in ('Unknown', 'Mixed', '') and tl_role != SignalRole.NOISE.value:
                    if planet_counts.get(tl_planet, 0) < MAX_SIGNALS_PER_PLANET:
                        if tl_signal not in drivers:
                            available_time_layer = tl_signal
                            break
            
            if available_time_layer:
                selection_log.append(f"DEFER static {planet}: reserving slot for time-layer signal")
                continue
        
        # All checks passed - add as driver
        drivers.append(signal)
        planet_counts[planet] = current_count + 1
        if is_time_layer:
            time_layer_driver_count += 1
        
        layer_tag = 'TIME_LAYER' if is_time_layer else 'STATIC_NATAL'
        selection_log.append(
            f"SELECT {planet} [{layer_tag}][{role[:4]}] score={score:.2f} "
            f"(driver #{len(drivers)}, planet_count={planet_counts[planet]})"
        )
    
    # ========================================================================
    # SECOND PASS: If we still need time-layer and have room, try to add one
    # ========================================================================
    
    if require_time_layer and time_layer_driver_count == 0 and len(drivers) < MAX_DRIVERS:
        selection_log.append("SECOND_PASS: Attempting to add time-layer driver")
        for tl_signal in time_layer_signals:
            if len(drivers) >= MAX_DRIVERS:
                break
            if tl_signal in drivers:
                continue
            
            tl_planet = tl_signal.get('planet', 'Unknown')
            tl_role = tl_signal.get('role', 'NOISE')
            
            if tl_planet in ('Unknown', 'Mixed', ''):
                continue
            if tl_role == SignalRole.NOISE.value:
                continue
            if tl_role == SignalRole.BASELINE_CONTEXT.value and not is_general_topic:
                continue
            
            current_count = planet_counts.get(tl_planet, 0)
            if current_count >= MAX_SIGNALS_PER_PLANET:
                continue
            
            drivers.append(tl_signal)
            planet_counts[tl_planet] = current_count + 1
            time_layer_driver_count += 1
            
            selection_log.append(
                f"SELECT_SECOND_PASS {tl_planet} [TIME_LAYER][{tl_role[:4]}] "
                f"score={tl_signal.get('score_final', 0):.2f} (driver #{len(drivers)})"
            )
            break
    
    # Final summary
    driver_planets = [d.get('planet', '?') for d in drivers]
    driver_layers = ['T' if d.get('_scoring_breakdown', {}).get('is_time_layer') else 'N' for d in drivers]
    selection_log.append(f"FINAL DRIVERS: {list(zip(driver_planets, driver_layers))} ({len(drivers)} total, "
                        f"time_layer_count={time_layer_driver_count})")
    
    # NOTE: We do NOT fill to 3 with baseline - that's intentional per requirements
    if len(drivers) < MAX_DRIVERS:
        selection_log.append(f"INFO: Only {len(drivers)} drivers (no baseline fallback applied)")
    
    # Time layer stats for debug output
    time_layer_stats = {
        'time_context': time_context,
        'query_year': query_year,
        'time_layer_signals_available': len(time_layer_signals),
        'static_natal_signals_available': len(static_natal_signals),
        'time_layer_drivers_selected': time_layer_driver_count,
        'time_data_missing': time_data_missing,
        'require_time_layer_met': not require_time_layer or time_layer_driver_count > 0
    }
    
    return drivers, selection_log, time_layer_stats


# ============================================================================
# MAIN BUILD FUNCTION
# ============================================================================

def build_reading_pack(
    user_question: str,
    topic: Optional[str],
    time_context: str,
    astro_features: Dict[str, Any],
    missing_keys: List[str] = None,
    intent: str = 'reflect',
    recent_planets: List[str] = None,
    memory_context: Dict[str, Any] = None  # NEW: Memory context for repetition penalty
) -> Dict[str, Any]:
    """
    Build a reading pack with role-based signal selection and TIME LAYER analysis.
    
    Pipeline v3 + Memory Integration:
    1. Collect all candidate signals from astro_features
    2. Resolve topic lords ("4th Lord" → actual planet)
    3. Extract query year from user question
    4. Classify signals as static_natal or time_layer
    5. Assign role to each signal (TOPIC_DRIVER/TIME_DRIVER/BASELINE_CONTEXT/NOISE)
    6. Score signals with TIME RELEVANCE BOOST for time-specific queries
    7. Apply REPETITION PENALTY for signals matching avoid_repeating (from memory)
    8. Select drivers by global score with TIME LAYER REQUIREMENT
    9. Return pack with kept signals as drivers for Trust Widget
    
    Args:
        user_question: Original user question
        topic: Topic label (career, relationship, etc.)
        time_context: Time context (past, present, future, timeless)
        astro_features: Full astro features dict
        missing_keys: Optional missing data keys
        intent: User intent
        recent_planets: Planets used in recent answers (for diversity)
        memory_context: Memory context with avoid_repeating, confirmed_facts, etc.
        
    Returns:
        Dict with signals, drivers, timing_windows, and debug metadata
    """
    if missing_keys is None:
        missing_keys = []
    if recent_planets is None:
        recent_planets = []
    if memory_context is None:
        memory_context = {}
    
    recent_planets_set = set(recent_planets)
    
    # Extract memory-based penalties
    avoid_repeating = memory_context.get('avoid_repeating', [])
    confirmed_facts = memory_context.get('confirmed_facts', [])
    has_prior_context = memory_context.get('has_prior_context', False)
    
    # Get topic-specific houses and planets from SINGLE SOURCE OF TRUTH (topics.py)
    topic_houses, topic_planets = get_topic_houses_and_planets(topic)
    
    # Determine if this is a general/life overview topic (for Mahadasha inclusion)
    is_general_topic = topic in (None, '', 'general', Topic.GENERAL.value, Topic.DAILY_GUIDANCE.value, Topic.SELF_PSYCHOLOGY.value)
    
    # ========================================================================
    # EXTRACT QUERY YEAR FROM USER QUESTION (NEW - for time-layer scoring)
    # ========================================================================
    query_year = extract_query_year(user_question)
    query_start_year, query_end_year = extract_time_range(user_question)
    
    logger.info(f"[READING_PACK] TIME EXTRACTION: query_year={query_year}, "
               f"time_context={time_context}, question='{user_question[:50]}...', "
               f"has_memory={has_prior_context}, avoid_items={len(avoid_repeating)}")
    
    # Initialize pack
    pack = {
        'question': user_question,
        'topic': topic or 'general',
        'time_context': time_context,
        'query_year': query_year,  # NEW: Store extracted year
        'decision_frame': None,
        'signals': [],
        'drivers': [],  # Top drivers for Trust Widget (role-enforced)
        'timing_windows': [],
        'data_gaps': [],
    }
    
    # Compute data gaps
    important_missing = []
    if missing_keys:
        critical_fields = {'ascendant', 'moon_sign', 'mahadasha', 'antardasha', 'planets', 'houses'}
        important_missing = [k for k in missing_keys if k in critical_fields]
    pack['data_gaps'] = important_missing
    
    # ========================================================================
    # STEP 1: COLLECT ALL CANDIDATE SIGNALS
    # ========================================================================
    
    raw_signals = []
    signal_id_counter = 0
    
    # ========================================================================
    # GET HOUSES DATA FOR RESOLVING TOPIC LORDS
    # ========================================================================
    houses_data = astro_features.get('houses', [])
    
    # Pre-resolve topic planets for Mahadasha gating
    # This ensures Mahadasha is only included if relevant to ACTUAL planets
    resolved_topic_planets_for_gating = resolve_topic_planets(topic_planets, houses_data, topic_houses)
    
    # ========================================================================
    # MAHADASHA GATING: Include if topic-relevant OR overlaps past query year
    # ========================================================================
    if astro_features.get('mahadasha'):
        maha = astro_features['mahadasha']
        maha_planet = maha.get('planet', '')
        
        # Check if Mahadasha planet is topic-relevant using RESOLVED planets
        maha_is_topic_relevant = (
            is_general_topic or
            maha_planet in resolved_topic_planets_for_gating or
            _planet_rules_topic_house(maha_planet, topic_houses, astro_features)
        )
        
        # NEW: Check time overlap for past queries (override topic gating)
        maha_time_overlap, maha_overlap_window = check_dasha_overlaps_query_year(maha, query_year)
        maha_past_override = (
            time_context == 'past' and 
            query_year is not None and 
            maha_time_overlap
        )
        
        # Include if topic-relevant OR past query overlaps Mahadasha period
        if maha_is_topic_relevant or maha_past_override:
            signal_id_counter += 1
            
            # Determine inclusion reason for debugging
            if maha_past_override and not maha_is_topic_relevant:
                inclusion_reason = f"past_time_overlap ({maha_overlap_window} covers {query_year})"
                claim_suffix = f" - active during {query_year}"
            else:
                inclusion_reason = "topic_relevant"
                claim_suffix = " (current)"
            
            raw_signals.append({
                'id': f'C{signal_id_counter}',
                'type': 'dasha',
                'claim': f"Mahadasha of {maha_planet}{claim_suffix}",
                'evidence': {
                    'planet': maha_planet,
                    'start_date': maha.get('start_date'),
                    'end_date': maha.get('end_date'),
                },
                'polarity': _dasha_polarity(maha_planet),
                'applies_to': topic or 'general',
                # DEBUG FIELDS
                'time_overlap': maha_time_overlap,
                'overlap_window': maha_overlap_window,
                '_inclusion_reason': inclusion_reason,
            })
            logger.info(f"[MAHADASHA] Included {maha_planet} - reason={inclusion_reason}, time_overlap={maha_time_overlap}, window={maha_overlap_window}")
        else:
            logger.debug(f"[MAHADASHA] Excluded {maha_planet} - not topic-relevant and no past time overlap")
    
    # Antardasha - same gating logic with time overlap override
    if astro_features.get('antardasha'):
        anta = astro_features['antardasha']
        anta_planet = anta.get('planet', '')
        
        anta_is_topic_relevant = (
            is_general_topic or
            anta_planet in resolved_topic_planets_for_gating or
            _planet_rules_topic_house(anta_planet, topic_houses, astro_features)
        )
        
        # NEW: Check time overlap for past queries
        anta_time_overlap, anta_overlap_window = check_dasha_overlaps_query_year(anta, query_year)
        anta_past_override = (
            time_context == 'past' and 
            query_year is not None and 
            anta_time_overlap
        )
        
        if anta_is_topic_relevant or anta_past_override:
            signal_id_counter += 1
            
            if anta_past_override and not anta_is_topic_relevant:
                inclusion_reason = f"past_time_overlap ({anta_overlap_window} covers {query_year})"
                claim_suffix = f" - active during {query_year}"
            else:
                inclusion_reason = "topic_relevant"
                claim_suffix = " (ongoing)"
            
            raw_signals.append({
                'id': f'C{signal_id_counter}',
                'type': 'dasha',
                'claim': f"Antardasha of {anta_planet}{claim_suffix}",
                'evidence': {
                    'planet': anta_planet,
                    'start_date': anta.get('start_date'),
                    'end_date': anta.get('end_date'),
                },
                'polarity': _dasha_polarity(anta_planet),
                'applies_to': topic or 'general',
                # DEBUG FIELDS
                'time_overlap': anta_time_overlap,
                'overlap_window': anta_overlap_window,
                '_inclusion_reason': inclusion_reason,
            })
            logger.info(f"[ANTARDASHA] Included {anta_planet} - reason={inclusion_reason}, time_overlap={anta_time_overlap}")
    
    # Planet position signals (from planets array)
    planets_data = astro_features.get('planets', [])
    for planet_info in planets_data:
        planet_name = planet_info.get('name', '')
        planet_house = planet_info.get('house')
        planet_sign = planet_info.get('sign', '')
        is_retrograde = planet_info.get('retrograde', False)
        
        if not planet_name or planet_name in ('Ascendant', 'Asc'):
            continue
        
        signal_id_counter += 1
        house_int = int(planet_house) if planet_house else 0
        
        # Determine polarity
        benefics = ['Jupiter', 'Venus', 'Moon', 'Mercury']
        malefics = ['Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun']
        if planet_name in benefics:
            polarity = 'supportive'
        elif planet_name in malefics:
            polarity = 'challenging' if is_retrograde else 'mixed'
        else:
            polarity = 'mixed'
        
        retro_str = " (retrograde)" if is_retrograde else ""
        claim = f"{planet_name} in {planet_sign}, {house_int}th house{retro_str}"
        
        raw_signals.append({
            'id': f'C{signal_id_counter}',
            'type': 'planet_position',
            'claim': claim,
            'evidence': {
                'planet': planet_name,
                'sign': planet_sign,
                'house': house_int,
                'retrograde': is_retrograde,
                'degree': planet_info.get('degree')
            },
            'polarity': polarity,
            'applies_to': topic if house_int in topic_houses else 'general',
        })
    
    # Focus factors (house/planet strengths)
    focus_factors = astro_features.get('focus_factors', [])
    for factor in focus_factors[:8]:
        signal_id_counter += 1
        strength = factor.get('strength', 0)
        
        if strength >= 0.7:
            polarity = 'supportive'
        elif strength <= 0.3:
            polarity = 'challenging'
        else:
            polarity = 'mixed'
        
        raw_signals.append({
            'id': f'C{signal_id_counter}',
            'type': 'planet_strength',
            'claim': f"House/Planet strength: {factor.get('interpretation', '')}",
            'evidence': factor,
            'polarity': polarity,
            'applies_to': topic or 'general',
        })
    
    # Yogas
    yogas = astro_features.get('yogas', [])
    for yoga in yogas[:4]:
        signal_id_counter += 1
        raw_signals.append({
            'id': f'C{signal_id_counter}',
            'type': 'yoga',
            'claim': yoga.get('name', 'Yoga'),
            'evidence': yoga.get('interpretation', ''),
            'polarity': 'supportive',
            'applies_to': topic or 'general',
        })
    
    # Key rules
    key_rules = astro_features.get('key_rules', [])
    for rule in key_rules[:6]:
        signal_id_counter += 1
        raw_signals.append({
            'id': f'C{signal_id_counter}',
            'type': 'rule',
            'claim': rule.get('name', 'Rule'),
            'evidence': rule.get('interpretation', ''),
            'polarity': rule.get('polarity', 'mixed'),
            'applies_to': topic or 'general',
        })
    
    # Transits
    transits = astro_features.get('transits', [])
    for transit in transits[:8]:
        signal_id_counter += 1
        raw_signals.append({
            'id': f'C{signal_id_counter}',
            'type': 'transit',
            'claim': f"{transit.get('planet', 'Planet')} transiting {transit.get('sign', '')} (house {transit.get('house', '')})",
            'evidence': transit,
            'polarity': transit.get('nature', 'mixed'),
            'applies_to': topic or 'general',
        })
    
    # ========================================================================
    # STEP 2: RESOLVE TOPIC PLANETS (convert "4th Lord" to actual planets)
    # ========================================================================
    
    # Get houses data for resolving lords
    houses_data = astro_features.get('houses', [])
    
    # Resolve abstract planet references to actual planets for this chart
    resolved_topic_planets = resolve_topic_planets(topic_planets, houses_data, topic_houses)
    
    logger.info(
        f"[READING_PACK] Topic planet resolution: {topic_planets} → {resolved_topic_planets} "
        f"(topic={topic}, houses={topic_houses})"
    )
    
    # ========================================================================
    # STEP 3: ASSIGN ROLES TO ALL SIGNALS (using RESOLVED planets)
    # ========================================================================
    
    for signal in raw_signals:
        # Extract and store planet/house for easy access
        signal['planet'] = _extract_planet_from_signal(signal)
        signal['house'] = _extract_house_from_signal(signal)
        
        # Assign role with RESOLVED topic planets
        role, role_reason = assign_signal_role(
            signal=signal,
            topic=topic,
            time_context=time_context,
            topic_houses=topic_houses,
            resolved_topic_planets=resolved_topic_planets,
            is_general_topic=is_general_topic
        )
        signal['role'] = role.value
        signal['role_reason'] = role_reason
    
    # ========================================================================
    # STEP 4: GLOBAL SCORING (not role-bucket based)
    # ========================================================================
    
    # Group signals by role (for debug metrics only)
    signals_by_role: Dict[SignalRole, List[Dict[str, Any]]] = {
        SignalRole.TOPIC_DRIVER: [],
        SignalRole.TIME_DRIVER: [],
        SignalRole.BASELINE_CONTEXT: [],
        SignalRole.CONTRAST_SIGNAL: [],
        SignalRole.NOISE: [],
    }
    
    for signal in raw_signals:
        role = SignalRole(signal['role'])
        
        # GLOBAL scoring (not role-bucket based)
        score, breakdown = _score_signal_globally(
            signal=signal,
            role=role,
            topic=topic,
            time_context=time_context,
            recent_planets=recent_planets_set,
            topic_houses=topic_houses,
            resolved_topic_planets=resolved_topic_planets,
            query_year=query_year  # NEW: Pass query year for time relevance boost
        )
        signal['score_raw'] = round(score, 3)
        signal['score_final'] = round(score, 3)
        signal['_scoring_breakdown'] = breakdown
        
        # ================================================================
        # MEMORY-BASED REPETITION PENALTY (NEW)
        # ================================================================
        if avoid_repeating and has_prior_context:
            claim = signal.get('claim', '') or signal.get('text_human', '')
            claim_lower = claim.lower() if claim else ''
            
            repetition_penalty = 0.0
            for avoided in avoid_repeating:
                avoided_lower = avoided.lower()
                # Check for significant overlap
                avoided_words = set(avoided_lower.split())
                claim_words = set(claim_lower.split())
                overlap = avoided_words.intersection(claim_words)
                
                # If more than 3 meaningful words overlap, apply penalty
                meaningful_overlap = [w for w in overlap if len(w) > 3]
                if len(meaningful_overlap) >= 3:
                    repetition_penalty = 0.15  # 15% penalty for repetition
                    signal['_repetition_match'] = avoided[:50]
                    break
            
            if repetition_penalty > 0:
                signal['score_final'] = max(0.1, signal['score_final'] - repetition_penalty)
                signal['_repetition_penalty'] = repetition_penalty
                logger.debug(f"[READING_PACK] Applied repetition penalty to {signal.get('planet', '?')}: -{repetition_penalty}")
        
        signals_by_role[role].append(signal)
    
    # ========================================================================
    # STEP 5: SELECT DRIVERS BY GLOBAL SCORE (with TIME-LAYER REQUIREMENT)
    # ========================================================================
    
    drivers, driver_selection_log, time_layer_stats = select_drivers_by_global_score(
        all_signals=raw_signals,
        is_general_topic=is_general_topic,
        resolved_topic_planets=resolved_topic_planets,
        topic_houses=topic_houses,
        astro_features=astro_features,
        time_context=time_context,
        query_year=query_year  # NEW: Pass query year
    )
    
    # Determine kept signals (all signals used, drivers are subset)
    # For backward compatibility, kept_signals = drivers + top non-driver signals
    kept_signals = drivers.copy()
    for signal in sorted(raw_signals, key=lambda s: s.get('score_final', 0), reverse=True):
        if signal not in kept_signals and len(kept_signals) < 6:
            kept_signals.append(signal)
    
    # Reindex signal IDs for kept signals
    for idx, signal in enumerate(kept_signals, 1):
        signal['final_id'] = f'S{idx}'
    
    pack['drivers'] = drivers
    pack['signals'] = kept_signals
    
    # Store memory context info for debug
    pack['_memory_applied'] = {
        'has_prior_context': has_prior_context,
        'avoid_repeating_count': len(avoid_repeating),
        'confirmed_facts_count': len(confirmed_facts),
    }
    
    # ========================================================================
    # STEP 6: BUILD DEBUG DATA WITH RESOLVED TOPIC PLANETS
    # ========================================================================
    
    candidate_signals_list = []
    for idx, signal in enumerate(raw_signals):
        is_kept = signal in kept_signals
        is_driver = signal in pack['drivers']
        
        candidate_signals_list.append({
            'signal_id': signal.get('id', f'C{idx+1}'),
            'final_id': signal.get('final_id') if is_kept else None,
            'signal_type': signal.get('type', 'unknown'),
            'planet': signal.get('planet', 'Unknown'),
            'house': signal.get('house'),
            'role': signal.get('role', 'NOISE'),
            'role_reason': signal.get('role_reason', ''),
            'time_context': time_context,
            'score_raw': signal.get('score_raw', 0),
            'score_final': signal.get('score_final', 0),
            'scoring_breakdown': signal.get('_scoring_breakdown', {}),
            'kept': is_kept,
            'is_driver': is_driver,
            'claim': signal.get('claim', ''),
            'polarity': signal.get('polarity', 'mixed'),
            'text_human': _humanize_signal_text(signal),
            # NEW: Time layer fields
            'is_static_natal': signal.get('_scoring_breakdown', {}).get('is_static_natal', False),
            'is_time_layer': signal.get('_scoring_breakdown', {}).get('is_time_layer', False),
            'time_period': signal.get('_scoring_breakdown', {}).get('time_period'),
        })
    
    # Build role counts
    role_counts = {role.value: len(signals) for role, signals in signals_by_role.items()}
    
    # Build summary
    planet_counts = {}
    for cs in candidate_signals_list:
        planet = cs['planet']
        planet_counts[planet] = planet_counts.get(planet, 0) + 1
    
    # NEW: Build time layer counts
    time_layer_count = sum(1 for cs in candidate_signals_list if cs.get('is_time_layer'))
    static_natal_count = sum(1 for cs in candidate_signals_list if cs.get('is_static_natal'))
    
    top_10_by_score = sorted(candidate_signals_list, key=lambda x: x['score_final'], reverse=True)[:10]
    
    # NEW: Group top 10 by time layer flag
    top_10_time_layer = [s for s in top_10_by_score if s.get('is_time_layer')]
    top_10_static_natal = [s for s in top_10_by_score if s.get('is_static_natal')]
    
    debug_summary = {
        'total_candidates': len(candidate_signals_list),
        'kept_count': len(kept_signals),
        'driver_count': len(pack['drivers']),
        'role_counts': role_counts,
        'counts_by_planet': planet_counts,
        # NEW: Time layer summary
        'time_layer_stats': time_layer_stats,
        'counts_by_time_layer': {
            'time_layer': time_layer_count,
            'static_natal': static_natal_count
        },
        'driver_selection_log': driver_selection_log,  # Detailed driver selection reasoning
        'top_10_by_score': [
            {
                'signal_id': s['signal_id'], 
                'planet': s['planet'], 
                'role': s['role'],
                'score': s['score_final'], 
                'kept': s['kept'], 
                'is_driver': s['is_driver'],
                # NEW: Time layer info
                'is_time_layer': s.get('is_time_layer', False),
                'is_static_natal': s.get('is_static_natal', False),
                'time_period': s.get('time_period')
            }
            for s in top_10_by_score
        ],
        # NEW: Grouped top 10
        'top_10_time_layer': [
            {'signal_id': s['signal_id'], 'planet': s['planet'], 'score': s['score_final'], 'time_period': s.get('time_period')}
            for s in top_10_time_layer
        ],
        'top_10_static_natal': [
            {'signal_id': s['signal_id'], 'planet': s['planet'], 'score': s['score_final']}
            for s in top_10_static_natal
        ],
    }
    
    pack['_candidate_signals_debug'] = {
        'candidates': candidate_signals_list,
        'summary': debug_summary,
        'topic': topic,
        'topic_houses': topic_houses,
        'topic_planets_raw': topic_planets,  # Original unresolved references
        'resolved_topic_planets': resolved_topic_planets,  # Resolved actual planets
        'time_context': time_context,
        'query_year': query_year,  # NEW: Extracted year from query
        'intent': intent,
        'recent_planets': list(recent_planets_set),
        'is_general_topic': is_general_topic,
        'max_signals_per_planet': MAX_SIGNALS_PER_PLANET,
        'timestamp': datetime.utcnow().isoformat(),
    }
    
    # Extract timing windows
    timing_windows = astro_features.get('timing_windows', [])
    pack['timing_windows'] = timing_windows[:3]
    
    logger.info(
        f"[READING_PACK] topic={topic} time={time_context} query_year={query_year} "
        f"candidates={len(raw_signals)} drivers={len(pack['drivers'])} "
        f"time_layer={time_layer_count} static_natal={static_natal_count} "
        f"resolved_planets={resolved_topic_planets}"
    )
    
    return pack


def _dasha_polarity(planet: str) -> str:
    """Determine dasha polarity based on planet"""
    supportive = {'jupiter', 'venus', 'sun', 'mercury'}
    challenging = {'saturn', 'rahu', 'ketu', 'mars'}
    
    planet_lower = planet.lower() if planet else ''
    
    if planet_lower in supportive:
        return 'supportive'
    elif planet_lower in challenging:
        return 'challenging'
    return 'mixed'



# ============================================================================
# MULTI-TOPIC READING PACK BUILDER
# ============================================================================

def build_multi_topic_reading_pack(
    user_question: str,
    primary_topic: str,
    secondary_topics: List[str],
    time_context: str,
    astro_features: Dict[str, Any],
    missing_keys: List[str] = None,
    intent: str = 'reflect',
    recent_planets: List[str] = None
) -> Dict[str, Any]:
    """
    Build a reading pack for multi-topic questions.
    
    Handles questions like "If I start a business, will it affect my health?"
    
    Pipeline:
    1. Fetch levers for primary + secondary topics
    2. Union houses/karakas/lords with topic tags per signal
    3. Score with topic_match_bonus (higher for primary)
    4. Select drivers with constraint:
       - At least 2 drivers from primary topic
       - At least 1 driver from secondary topic (if exists and has good signals)
    5. If not enough good signals for secondary, drop it (don't force)
    
    Args:
        user_question: Original user question
        primary_topic: Main topic (career, health, etc.)
        secondary_topics: Secondary topics (0-2)
        time_context: Time context (past, present, future, timeless)
        astro_features: Full astro features dict
        missing_keys: Optional missing data keys
        intent: User intent
        recent_planets: Planets used in recent answers
        
    Returns:
        Dict with primary_drivers, secondary_drivers, allowed_entities, debug info
    """
    if missing_keys is None:
        missing_keys = []
    if recent_planets is None:
        recent_planets = []
    if secondary_topics is None:
        secondary_topics = []
    
    logger.info(f"[MULTI_TOPIC] Building pack: primary={primary_topic}, secondary={secondary_topics}")
    
    # Get houses data for resolving lords
    houses_data = astro_features.get('houses', [])
    
    # ========================================================================
    # GET TOPIC LEVERS FOR PRIMARY AND SECONDARY TOPICS
    # ========================================================================
    
    primary_houses, primary_planets_raw = get_topic_houses_and_planets(primary_topic)
    primary_planets = resolve_topic_planets(primary_planets_raw, houses_data, primary_houses)
    
    secondary_houses_union = []
    secondary_planets_union = []
    secondary_topic_map = {}  # planet -> topic for tagging
    
    for sec_topic in secondary_topics:
        sec_houses, sec_planets_raw = get_topic_houses_and_planets(sec_topic)
        sec_planets = resolve_topic_planets(sec_planets_raw, houses_data, sec_houses)
        
        secondary_houses_union.extend(sec_houses)
        secondary_planets_union.extend(sec_planets)
        
        # Map planets to their topic for tagging
        for p in sec_planets:
            if p not in secondary_topic_map:
                secondary_topic_map[p] = sec_topic
    
    # Deduplicate
    secondary_houses_union = list(set(secondary_houses_union))
    secondary_planets_union = list(set(secondary_planets_union))
    
    # Union all houses and planets
    all_topic_houses = list(set(primary_houses + secondary_houses_union))
    all_topic_planets = list(set(primary_planets + secondary_planets_union))
    
    logger.info(f"[MULTI_TOPIC] Primary: houses={primary_houses}, planets={primary_planets}")
    logger.info(f"[MULTI_TOPIC] Secondary union: houses={secondary_houses_union}, planets={secondary_planets_union}")
    
    # ========================================================================
    # BUILD BASE READING PACK (uses primary topic for baseline scoring)
    # ========================================================================
    
    base_pack = build_reading_pack(
        user_question=user_question,
        topic=primary_topic,
        time_context=time_context,
        astro_features=astro_features,
        missing_keys=missing_keys,
        intent=intent,
        recent_planets=recent_planets
    )
    
    # ========================================================================
    # RE-SCORE SIGNALS WITH MULTI-TOPIC BONUSES
    # ========================================================================
    
    all_signals = base_pack.get('_candidate_signals_debug', {}).get('candidates', [])
    
    # Apply topic-specific bonuses
    for signal in all_signals:
        planet = signal.get('planet', '')
        house = signal.get('house')
        
        # Calculate topic relevance
        is_primary_planet = planet in primary_planets
        is_primary_house = house in primary_houses if house else False
        is_secondary_planet = planet in secondary_planets_union
        is_secondary_house = house in secondary_houses_union if house else False
        
        # Determine topic tag
        if is_primary_planet or is_primary_house:
            signal['topic_tag'] = primary_topic
        elif is_secondary_planet or is_secondary_house:
            signal['topic_tag'] = secondary_topic_map.get(planet, secondary_topics[0] if secondary_topics else 'general')
        else:
            signal['topic_tag'] = 'general'
        
        # Apply topic match bonuses to score
        base_score = signal.get('score_final', 0)
        bonus = 0
        
        if is_primary_planet or is_primary_house:
            bonus += 0.15  # Primary topic bonus
            signal['_primary_match'] = True
        elif is_secondary_planet or is_secondary_house:
            bonus += 0.08  # Smaller secondary topic bonus
            signal['_secondary_match'] = True
        
        signal['score_final'] = min(1.0, base_score + bonus)
        signal['_topic_bonus'] = bonus
    
    # Sort by adjusted score
    all_signals_sorted = sorted(all_signals, key=lambda s: s.get('score_final', 0), reverse=True)
    
    # ========================================================================
    # SELECT DRIVERS WITH MULTI-TOPIC CONSTRAINTS
    # ========================================================================
    
    primary_drivers = []
    secondary_drivers = []
    planet_counts = {}
    
    # First pass: Collect primary drivers (at least 2)
    for signal in all_signals_sorted:
        if len(primary_drivers) >= 3:
            break
        
        planet = signal.get('planet', '')
        if planet in ('Unknown', 'Mixed', ''):
            continue
        
        role = signal.get('role', 'NOISE')
        if role == 'NOISE':
            continue
        
        # Check if primary topic relevant
        is_primary = signal.get('_primary_match', False)
        if not is_primary:
            # Also check if planet/house matches primary directly
            is_primary = (planet in primary_planets or 
                         signal.get('house') in primary_houses if signal.get('house') else False)
        
        if is_primary:
            if planet_counts.get(planet, 0) < 2:
                signal['topic_tag'] = primary_topic
                primary_drivers.append(signal)
                planet_counts[planet] = planet_counts.get(planet, 0) + 1
    
    # Second pass: Collect secondary drivers (at least 1 if good signals exist)
    if secondary_topics:
        for signal in all_signals_sorted:
            if len(secondary_drivers) >= 2:
                break
            
            planet = signal.get('planet', '')
            if planet in ('Unknown', 'Mixed', ''):
                continue
            
            role = signal.get('role', 'NOISE')
            if role == 'NOISE':
                continue
            
            # Skip if already a primary driver
            if signal in primary_drivers:
                continue
            
            # Check if secondary topic relevant
            is_secondary = signal.get('_secondary_match', False)
            if not is_secondary:
                is_secondary = (planet in secondary_planets_union or 
                               signal.get('house') in secondary_houses_union if signal.get('house') else False)
            
            # Only include if score is decent (above 0.4)
            if is_secondary and signal.get('score_final', 0) >= 0.4:
                if planet_counts.get(planet, 0) < 2:
                    signal['topic_tag'] = secondary_topic_map.get(planet, secondary_topics[0])
                    secondary_drivers.append(signal)
                    planet_counts[planet] = planet_counts.get(planet, 0) + 1
    
    # If not enough secondary signals, don't force - just use primary
    secondary_dropped = len(secondary_drivers) == 0 and len(secondary_topics) > 0
    if secondary_dropped:
        logger.info(f"[MULTI_TOPIC] Dropped secondary topics {secondary_topics} - no good signals")
    
    # ========================================================================
    # BUILD ALLOWED ENTITIES FROM SELECTED DRIVERS
    # ========================================================================
    
    all_drivers = primary_drivers + secondary_drivers
    allowed_planets = set()
    allowed_houses = set()
    
    for driver in all_drivers:
        planet = driver.get('planet', '')
        if planet and planet not in ('Unknown', 'Mixed'):
            allowed_planets.add(planet.lower())
        
        house = driver.get('house')
        if house:
            allowed_houses.add(house)
    
    # Also add dasha if present
    mahadasha = astro_features.get('mahadasha', {})
    if mahadasha.get('planet'):
        allowed_planets.add(mahadasha['planet'].lower())
    
    # ========================================================================
    # BUILD OUTPUT
    # ========================================================================
    
    result = {
        'question': user_question,
        'primary_topic': primary_topic,
        'secondary_topics': secondary_topics if not secondary_dropped else [],
        'secondary_dropped': secondary_dropped,
        'time_context': time_context,
        
        # Drivers with topic tags
        'primary_drivers': primary_drivers,
        'secondary_drivers': secondary_drivers,
        'drivers': all_drivers,  # Combined for backward compatibility
        
        # Allowed entities for LLM guardrails
        'allowed_entities': {
            'planets': list(allowed_planets),
            'houses': list(allowed_houses),
        },
        
        # Full signal list
        'signals': base_pack.get('signals', []),
        
        # Timing windows
        'timing_windows': base_pack.get('timing_windows', []),
        
        # Debug info
        '_multi_topic_debug': {
            'primary_houses': primary_houses,
            'primary_planets': primary_planets,
            'secondary_houses_union': secondary_houses_union,
            'secondary_planets_union': secondary_planets_union,
            'primary_driver_count': len(primary_drivers),
            'secondary_driver_count': len(secondary_drivers),
            'secondary_dropped': secondary_dropped,
            'all_signals_count': len(all_signals),
        },
        '_candidate_signals_debug': base_pack.get('_candidate_signals_debug', {}),
    }
    
    logger.info(
        f"[MULTI_TOPIC] Result: primary_drivers={len(primary_drivers)}, "
        f"secondary_drivers={len(secondary_drivers)}, secondary_dropped={secondary_dropped}, "
        f"allowed_planets={allowed_planets}"
    )
    
    return result
