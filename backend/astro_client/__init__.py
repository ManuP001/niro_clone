"""
Astro Client Package for NIRO

Provides:
- Vedic astrology API integration
- AstroProfile and AstroTransits models
- Storage layer with DB-ready interface
- Topic classification and chart lever mapping
- Feature extraction for LLM consumption
- NIRO LLM integration
"""

from .models import (
    BirthDetails,
    AstroProfile,
    AstroTransits,
    PlanetPosition,
    HouseData,
    DashaInfo,
    TransitEvent
)
from .vedic_api import VedicAPIClient
from .storage import (
    save_astro_profile,
    get_astro_profile,
    save_astro_transits,
    get_astro_transits,
    get_or_refresh_transits,
    ensure_profile_and_transits
)
from .topics import (
    Topic,
    classify_topic,
    TOPIC_KEYWORDS,
    ACTION_TO_TOPIC,
    get_chart_levers
)
from .interpreter import build_astro_features
from .niro_llm import NiroLLMModule, call_niro_llm, NIRO_SYSTEM_PROMPT

__all__ = [
    # Models
    'BirthDetails',
    'AstroProfile',
    'AstroTransits',
    'PlanetPosition',
    'HouseData',
    'DashaInfo',
    'TransitEvent',
    # API Client
    'VedicAPIClient',
    # Storage
    'save_astro_profile',
    'get_astro_profile',
    'save_astro_transits',
    'get_astro_transits',
    'get_or_refresh_transits',
    'ensure_profile_and_transits',
    # Topics
    'Topic',
    'classify_topic',
    'TOPIC_KEYWORDS',
    'ACTION_TO_TOPIC',
    'get_chart_levers',
    # Interpreter
    'build_astro_features',
    # LLM
    'NiroLLMModule',
    'call_niro_llm',
    'NIRO_SYSTEM_PROMPT',
]
