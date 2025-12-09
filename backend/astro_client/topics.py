"""
Topic Classification and Mapping

Defines:
- Topic taxonomy (internal topic identifiers)
- Action ID to topic mapping
- Keyword-based topic classification
- Topic to chart lever mapping (houses, planets)
"""

from enum import Enum
from typing import Optional, Set, Dict, List
import re
import logging

logger = logging.getLogger(__name__)


class Topic(str, Enum):
    """Topic taxonomy for NIRO conversations"""
    
    # Self & Psychology
    SELF_PSYCHOLOGY = "self_psychology"
    
    # Career & Work
    CAREER = "career"
    
    # Money & Finances
    MONEY = "money"
    
    # Relationships
    ROMANTIC_RELATIONSHIPS = "romantic_relationships"
    MARRIAGE_PARTNERSHIP = "marriage_partnership"
    
    # Family & Home
    FAMILY_HOME = "family_home"
    
    # Social
    FRIENDS_SOCIAL = "friends_social"
    
    # Education
    LEARNING_EDUCATION = "learning_education"
    
    # Health
    HEALTH_ENERGY = "health_energy"
    
    # Spirituality
    SPIRITUALITY = "spirituality"
    
    # Travel & Relocation
    TRAVEL_RELOCATION = "travel_relocation"
    
    # Legal
    LEGAL_CONTRACTS = "legal_contracts"
    
    # Time-based
    DAILY_GUIDANCE = "daily_guidance"
    
    # Default
    GENERAL = "general"


# Action ID to Topic mapping
ACTION_TO_TOPIC: Dict[str, str] = {
    # Focus actions
    "focus_career": Topic.CAREER.value,
    "focus_relationship": Topic.ROMANTIC_RELATIONSHIPS.value,
    "focus_marriage": Topic.MARRIAGE_PARTNERSHIP.value,
    "focus_money": Topic.MONEY.value,
    "focus_finance": Topic.MONEY.value,
    "focus_health": Topic.HEALTH_ENERGY.value,
    "focus_family": Topic.FAMILY_HOME.value,
    "focus_education": Topic.LEARNING_EDUCATION.value,
    "focus_spirituality": Topic.SPIRITUALITY.value,
    "focus_travel": Topic.TRAVEL_RELOCATION.value,
    
    # Ask actions
    "ask_career": Topic.CAREER.value,
    "ask_relationship": Topic.ROMANTIC_RELATIONSHIPS.value,
    "ask_money": Topic.MONEY.value,
    "ask_health": Topic.HEALTH_ENERGY.value,
    
    # Time-based actions
    "daily_guidance": Topic.DAILY_GUIDANCE.value,
    "ask_timing": Topic.GENERAL.value,
    "weekly_outlook": Topic.DAILY_GUIDANCE.value,
    
    # Deep dive (preserves current topic)
    "deep_dive": None,
    "go_deeper": None,
    
    # Compatibility
    "compatibility": Topic.ROMANTIC_RELATIONSHIPS.value,
}


# Keyword sets for topic classification
TOPIC_KEYWORDS: Dict[str, Set[str]] = {
    Topic.CAREER.value: {
        "job", "career", "work", "office", "boss", "promotion", "startup",
        "company", "profession", "employment", "colleague", "interview",
        "resign", "fired", "hired", "workplace", "business", "venture",
        "entrepreneur", "corporate", "salary hike", "appraisal", "project"
    },
    
    Topic.ROMANTIC_RELATIONSHIPS.value: {
        "love", "crush", "dating", "boyfriend", "girlfriend", "romantic",
        "attraction", "relationship", "romance", "flirt", "breakup",
        "ex", "feelings", "chemistry", "soulmate", "twin flame"
    },
    
    Topic.MARRIAGE_PARTNERSHIP.value: {
        "marriage", "husband", "wife", "spouse", "wedding", "married",
        "divorce", "engagement", "partner", "matrimony", "manglik",
        "compatibility", "kundli matching", "vivah", "shaadi"
    },
    
    Topic.MONEY.value: {
        "money", "income", "salary", "finance", "investment", "debt",
        "loan", "wealth", "rich", "poor", "savings", "stock", "trading",
        "real estate", "property", "inheritance", "financial", "profit",
        "loss", "expense", "budget", "crypto", "mutual fund"
    },
    
    Topic.FAMILY_HOME.value: {
        "family", "mother", "father", "parents", "home", "house",
        "children", "kids", "son", "daughter", "sibling", "brother",
        "sister", "relatives", "in-laws", "ancestral", "property",
        "domestic", "household"
    },
    
    Topic.FRIENDS_SOCIAL.value: {
        "friend", "friends", "social", "party", "networking", "group",
        "community", "circle", "connections", "acquaintance", "peers"
    },
    
    Topic.LEARNING_EDUCATION.value: {
        "study", "exam", "college", "university", "course", "degree",
        "learning", "skill", "education", "school", "student", "teacher",
        "training", "certification", "academic", "research", "phd",
        "masters", "bachelors", "competitive exam", "upsc", "cat", "gmat"
    },
    
    Topic.HEALTH_ENERGY.value: {
        "health", "tired", "energy", "fitness", "diet", "stress",
        "sleep", "illness", "disease", "doctor", "hospital", "medicine",
        "surgery", "mental", "anxiety", "depression", "wellness",
        "fatigue", "chronic", "recovery"
    },
    
    Topic.SPIRITUALITY.value: {
        "spiritual", "meditation", "karma", "purpose", "soul", "inner",
        "enlightenment", "guru", "temple", "prayer", "mantra", "moksha",
        "dharma", "divine", "consciousness", "awakening", "past life",
        "astral", "intuition"
    },
    
    Topic.TRAVEL_RELOCATION.value: {
        "travel", "trip", "abroad", "relocate", "move", "foreign",
        "immigration", "visa", "overseas", "settle", "migration",
        "country", "city", "shifting", "transfer"
    },
    
    Topic.LEGAL_CONTRACTS.value: {
        "court", "legal", "contract", "case", "lawsuit", "lawyer",
        "litigation", "dispute", "agreement", "settlement", "judge",
        "police", "crime"
    },
    
    Topic.SELF_PSYCHOLOGY.value: {
        "personality", "character", "nature", "myself", "identity",
        "confidence", "self-esteem", "who am i", "purpose", "life path",
        "destiny", "potential", "strengths", "weaknesses"
    },
    
    Topic.DAILY_GUIDANCE.value: {
        "today", "daily", "now", "this week", "this month", "guidance",
        "current", "immediate", "right now", "tomorrow"
    },
}


# Topic to Chart Levers mapping
TOPIC_CHART_LEVERS: Dict[str, Dict[str, List]] = {
    Topic.SELF_PSYCHOLOGY.value: {
        "houses": [1, 4, 5, 12],
        "planets": ["Lagna Lord", "Moon", "Rahu", "Ketu"],
        "divisional_charts": ["D1"],
        "key_factors": ["ascendant_strength", "moon_stability", "atmakaraka"]
    },
    
    Topic.CAREER.value: {
        "houses": [2, 6, 10, 11],
        "planets": ["10th Lord", "Sun", "Saturn", "Rahu", "Mercury"],
        "divisional_charts": ["D1", "D10"],
        "key_factors": ["10th_house_strength", "saturn_position", "career_yogas"]
    },
    
    Topic.MONEY.value: {
        "houses": [2, 11, 8, 5],
        "planets": ["Jupiter", "Venus", "2nd Lord", "11th Lord"],
        "divisional_charts": ["D1"],
        "key_factors": ["dhana_yogas", "2nd_11th_connection", "jupiter_strength"]
    },
    
    Topic.ROMANTIC_RELATIONSHIPS.value: {
        "houses": [5, 7, 8],
        "planets": ["Venus", "Moon", "Mars", "5th Lord"],
        "divisional_charts": ["D1", "D9"],
        "key_factors": ["venus_strength", "5th_house_romance", "emotional_compatibility"]
    },
    
    Topic.MARRIAGE_PARTNERSHIP.value: {
        "houses": [7, 8, 2, 4],
        "planets": ["7th Lord", "Venus", "Jupiter", "Mars"],
        "divisional_charts": ["D1", "D9"],
        "key_factors": ["7th_house_strength", "navamsa_7th", "manglik_dosha"]
    },
    
    Topic.FAMILY_HOME.value: {
        "houses": [2, 4, 8],
        "planets": ["Moon", "4th Lord", "Venus"],
        "divisional_charts": ["D1", "D4"],
        "key_factors": ["4th_house_strength", "moon_position", "ancestral_karma"]
    },
    
    Topic.FRIENDS_SOCIAL.value: {
        "houses": [3, 11],
        "planets": ["Mercury", "11th Lord", "3rd Lord"],
        "divisional_charts": ["D1"],
        "key_factors": ["11th_house_gains", "social_yogas"]
    },
    
    Topic.LEARNING_EDUCATION.value: {
        "houses": [3, 4, 5, 9],
        "planets": ["Mercury", "Jupiter", "5th Lord", "9th Lord"],
        "divisional_charts": ["D1", "D24"],
        "key_factors": ["mercury_strength", "5th_9th_axis", "vidya_yogas"]
    },
    
    Topic.HEALTH_ENERGY.value: {
        "houses": [1, 6, 8, 12],
        "planets": ["Lagna Lord", "Sun", "Mars", "Saturn"],
        "divisional_charts": ["D1"],
        "key_factors": ["ascendant_vitality", "6th_house_diseases", "sun_strength"]
    },
    
    Topic.SPIRITUALITY.value: {
        "houses": [5, 9, 12],
        "planets": ["Jupiter", "Ketu", "9th Lord", "12th Lord"],
        "divisional_charts": ["D1", "D20"],
        "key_factors": ["moksha_houses", "jupiter_ketu_connection", "dharma_trikona"]
    },
    
    Topic.TRAVEL_RELOCATION.value: {
        "houses": [3, 4, 9, 12],
        "planets": ["Rahu", "9th Lord", "12th Lord", "4th Lord"],
        "divisional_charts": ["D1"],
        "key_factors": ["foreign_settlement_yoga", "4th_12th_connection", "rahu_position"]
    },
    
    Topic.LEGAL_CONTRACTS.value: {
        "houses": [6, 7, 9],
        "planets": ["Mars", "Saturn", "6th Lord", "7th Lord"],
        "divisional_charts": ["D1"],
        "key_factors": ["6th_house_disputes", "mars_saturn_aspect", "legal_yogas"]
    },
    
    Topic.DAILY_GUIDANCE.value: {
        "houses": [1, 5, 9],
        "planets": ["Moon", "Lagna Lord", "Transit planets"],
        "divisional_charts": ["D1"],
        "key_factors": ["current_transits", "moon_transit", "dasha_timing"]
    },
    
    Topic.GENERAL.value: {
        "houses": [1, 5, 9, 10],
        "planets": ["Lagna Lord", "Moon", "Sun", "Jupiter"],
        "divisional_charts": ["D1"],
        "key_factors": ["dharma_trikona", "overall_strength"]
    },
}


def classify_topic(
    user_message: str,
    action_id: Optional[str] = None,
    current_topic: Optional[str] = None
) -> str:
    """
    Classify the topic from user message or action.
    
    Priority:
    1. action_id mapping (if present)
    2. Keyword matching in message
    3. Current topic (if present)
    4. Default to 'general'
    
    Args:
        user_message: User's message text
        action_id: Optional action ID from UI chip
        current_topic: Current topic from conversation state
        
    Returns:
        Topic string (from Topic enum values)
    """
    
    # Rule 1: Action ID takes priority
    if action_id:
        mapped_topic = ACTION_TO_TOPIC.get(action_id)
        if mapped_topic:
            logger.info(f"Topic from action_id '{action_id}': {mapped_topic}")
            return mapped_topic
        elif mapped_topic is None and action_id in ["deep_dive", "go_deeper"]:
            # Deep dive preserves current topic
            if current_topic:
                logger.info(f"Deep dive - keeping topic: {current_topic}")
                return current_topic
    
    # Rule 2: Keyword matching
    message_lower = user_message.lower()
    words = set(re.findall(r'\b\w+\b', message_lower))
    
    # Also check for multi-word phrases
    phrases_to_check = [
        message_lower  # Full message for phrase matching
    ]
    
    # Score each topic
    topic_scores: Dict[str, int] = {}
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # Single word match
            if ' ' not in keyword and keyword in words:
                score += 1
            # Multi-word phrase match
            elif ' ' in keyword and keyword in message_lower:
                score += 2  # Phrases worth more
        
        if score > 0:
            topic_scores[topic] = score
    
    # Return highest scoring topic
    if topic_scores:
        best_topic = max(topic_scores, key=topic_scores.get)
        logger.info(f"Topic from keywords: {best_topic} (score: {topic_scores[best_topic]})")
        return best_topic
    
    # Rule 3: Fallback to current topic
    if current_topic:
        logger.info(f"Using current topic: {current_topic}")
        return current_topic
    
    # Rule 4: Default
    logger.info("Defaulting to 'general' topic")
    return Topic.GENERAL.value


def get_chart_levers(topic: str) -> Dict[str, List]:
    """
    Get the chart levers (houses, planets) relevant to a topic.
    
    Args:
        topic: Topic string
        
    Returns:
        Dict with houses, planets, divisional_charts, key_factors
    """
    return TOPIC_CHART_LEVERS.get(topic, TOPIC_CHART_LEVERS[Topic.GENERAL.value])


def get_suggested_topics_for_mode(mode: str) -> List[str]:
    """
    Get suggested topics based on conversation mode.
    
    Args:
        mode: Conversation mode
        
    Returns:
        List of suggested topic values
    """
    if mode == "BIRTH_COLLECTION":
        return []  # No topic suggestions during birth collection
    
    if mode == "PAST_THEMES":
        return [
            Topic.CAREER.value,
            Topic.ROMANTIC_RELATIONSHIPS.value,
            Topic.MONEY.value,
            Topic.HEALTH_ENERGY.value
        ]
    
    # Default suggestions
    return [
        Topic.CAREER.value,
        Topic.ROMANTIC_RELATIONSHIPS.value,
        Topic.MONEY.value,
        Topic.DAILY_GUIDANCE.value
    ]
