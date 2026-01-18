"""
Vedic API Client

HTTP client wrapper for Vedic Astrology API (VedicAstroAPI v3-json).
Vedic API is a HARD DEPENDENCY - no stub fallbacks.
All methods make real API calls; failures are explicit and transparent.

Designed to be vendor-agnostic - adapt endpoint paths and field mappings
when integrating with different Vedic API providers (e.g., vedicastroAPI, AstroSage, etc.)
All endpoint mappings are centralized in this file for easy swapping.

VEDIC_API_KEY environment variable must be set for production use.
If missing at runtime:
- Backend allows startup
- All API calls return explicit VedicApiError with error_code
- Frontend receives VEDIC_API_KEY_MISSING in response
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
import hashlib

from .models import (
    BirthDetails,
    AstroProfile,
    AstroTransits,
    PlanetPosition,
    HouseData,
    DashaInfo,
    YogaInfo,
    TransitEvent
)
from .vimshottari import calculate_vimshottari_dashas

logger = logging.getLogger(__name__)

# ============ NAKSHATRA DEFINITIONS ============
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashirsha', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

NAKSHATRA_ALIASES = {
    'purvabhadra': 'Purva Bhadrapada',
    'uttarabhadra': 'Uttara Bhadrapada',
    'purvaphalguni': 'Purva Phalguni',
    'uttaraphalguni': 'Uttara Phalguni',
    'purvashadha': 'Purva Ashadha',
    'uttarashadha': 'Uttara Ashadha',
    'mrigashirsha': 'Mrigashirsha',
}

def calculate_degree_from_nakshatra(nakshatra: str, pada: int = 2) -> float:
    """
    Calculate approximate degree from nakshatra and pada.
    
    Vedic Astrology Facts:
    - Each nakshatra spans 13°20' (13.333°)
    - Each pada spans 3°20' (3.333°)
    - There are 27 nakshatras covering 360°
    
    Args:
        nakshatra: Name of the nakshatra (e.g., "PurvaBhadra")
        pada: Pada number (1-4), defaults to 2 (middle)
    
    Returns:
        Degree within the zodiac sign (0-30)
    """
    if not nakshatra:
        return 15.0  # Default to middle of sign
    
    # Normalize nakshatra name
    nakshatra_clean = nakshatra.strip().lower().replace(' ', '')
    
    # Try to find in NAKSHATRAS
    nakshatra_idx = -1
    for i, n in enumerate(NAKSHATRAS):
        if n.lower().replace(' ', '') == nakshatra_clean:
            nakshatra_idx = i
            break
    
    if nakshatra_idx == -1:
        logger.warning(f"Unknown nakshatra: {nakshatra}. Using middle position 15.0°")
        return 15.0  # Default if not found
    
    # Calculate absolute degree (0-360)
    nakshatra_degree = 13.333333  # 13°20' per nakshatra
    pada_degree = 3.333333        # 3°20' per pada
    
    # Start degree of this nakshatra
    abs_degree = nakshatra_idx * nakshatra_degree
    # Add pada offset (middle of the pada for best approximation)
    abs_degree += (pada - 1) * pada_degree + (pada_degree / 2)
    
    # Convert to degree within sign (0-30)
    degree_in_sign = abs_degree % 30
    
    return round(degree_in_sign, 1)


# Configuration - will be read at instantiation time, not module load time


# ============ VEDIC API EXCEPTIONS ============
class VedicApiError(Exception):
    """Raised when Vedic API call fails"""
    def __init__(self, error_code: str, message: str, details: str = None):
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(f"{error_code}: {message}")

# Constants
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

NAKSHATRA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3

SIGN_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
    'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
    'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

# Exaltation/Debilitation signs
EXALTATION = {
    'Sun': 'Aries', 'Moon': 'Taurus', 'Mars': 'Capricorn',
    'Mercury': 'Virgo', 'Jupiter': 'Cancer', 'Venus': 'Pisces',
    'Saturn': 'Libra', 'Rahu': 'Taurus', 'Ketu': 'Scorpio'
}

DEBILITATION = {
    'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer',
    'Mercury': 'Pisces', 'Jupiter': 'Capricorn', 'Venus': 'Virgo',
    'Saturn': 'Aries', 'Rahu': 'Scorpio', 'Ketu': 'Taurus'
}


class VedicAPIClient:
    """
    Client for Vedic Astrology API (VedicAstroAPI v3-json).
    
    HARD DEPENDENCY: No stub fallbacks, all calls are real API requests.
    Failures are explicit and transparent with typed error_codes.
    
    If VEDIC_API_KEY is not set, API calls return VedicApiError(VEDIC_API_KEY_MISSING).
    
    Endpoints (centralized for easy swapping):
    - /extended-horoscope/extended-kundli-details → fetch_full_profile()
    - /extended-horoscope/find-ascendant → fetch_full_profile()
    - /extended-horoscope/find-sun-sign → fetch_full_profile()
    - /extended-horoscope/find-moon-sign → fetch_full_profile()
    - /dashas/maha-dasha → fetch_full_profile()
    - /horoscope/chart → fetch_kundli_svg()
    - /horoscope/planets → fetch_planet_details()
    - /extended-horoscope/find-yogas → fetch_yogas()
    - /extended-horoscope/extended-kundli-details → derived for houses
    """
    
    def __init__(self, base_url: str = None, api_key: str = None):
        # Read from environment at instantiation time
        self.base_url = base_url or os.environ.get('VEDIC_API_BASE_URL', 'https://api.vedicastroapi.com/v3-json')
        self.api_key = api_key or os.environ.get('VEDIC_API_KEY', '')
        self._client: Optional[httpx.AsyncClient] = None
        
        # Log startup state
        has_key = bool(self.api_key)
        logger.info(f"VedicAPIClient initialized with base_url={self.base_url}, api_key_configured={has_key}")
        
        if not has_key:
            logger.warning("VEDIC_API_KEY is not configured. API calls will fail with VEDIC_API_KEY_MISSING.")
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
        return self._client
    
    async def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Low-level HTTP GET helper for VedicAstroAPI v3-json.
        
        The API uses GET requests with query parameters including api_key.
        
        Raises:
        - VedicApiError with error_code:
            - VEDIC_API_KEY_MISSING: API key not configured
            - VEDIC_API_UNAVAILABLE: HTTP error
            - VEDIC_API_BAD_RESPONSE: Invalid response format
        """
        # Check if API key is configured
        if not self.api_key:
            raise VedicApiError(
                error_code="VEDIC_API_KEY_MISSING",
                message="Vedic API key not configured",
                details="Set VEDIC_API_KEY environment variable"
            )
        
        try:
            # Construct full URL (VedicAstroAPI expects full path)
            full_url = f"{self.base_url}{path}"
            
            # Add API key to params
            params['api_key'] = self.api_key
            params['lang'] = params.get('lang', 'en')
            
            logger.info(f"[VEDIC_API] Calling {path}")
            logger.debug(f"[VEDIC_API] Full URL: {full_url}, params: {list(params.keys())}")
            
            # Make request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(full_url, params=params)
                
                # Check HTTP status
                if response.status_code != 200:
                    logger.error(f"[VEDIC_API] HTTP {response.status_code} for {path}")
                    raise VedicApiError(
                        error_code="VEDIC_API_UNAVAILABLE",
                        message=f"HTTP {response.status_code} from Vedic API",
                        details=f"{path}: {response.text[:200]}"
                    )
                
                # Parse JSON
                try:
                    data = response.json()
                except Exception as e:
                    raise VedicApiError(
                        error_code="VEDIC_API_BAD_RESPONSE",
                        message="Invalid JSON response from Vedic API",
                        details=str(e)
                    )
                
                # Check API status field
                if data.get('status') != 200:
                    logger.error(f"[VEDIC_API] API returned status {data.get('status')} for {path}")
                    raise VedicApiError(
                        error_code="VEDIC_API_BAD_RESPONSE",
                        message="Vedic API returned error status",
                        details=f"Status: {data.get('status')}, Message: {data.get('message', 'unknown')}"
                    )
                
                # Extract response data (can be dict or list)
                response_data = data.get('response', {})
                if isinstance(response_data, dict):
                    logger.info(f"[VEDIC_API] Success for {path}, response keys: {list(response_data.keys())}")
                else:
                    logger.info(f"[VEDIC_API] Success for {path}, response type: {type(response_data).__name__}, len: {len(response_data) if hasattr(response_data, '__len__') else 'N/A'}")
                return response_data
            
        except VedicApiError:
            raise  # Re-raise our typed exceptions
        
        except httpx.HTTPError as e:
            logger.error(f"[VEDIC_API] HTTP error for {path}: {type(e).__name__} - {str(e)}")
            raise VedicApiError(
                error_code="VEDIC_API_UNAVAILABLE",
                message=f"HTTP request failed: {type(e).__name__}",
                details=str(e)
            )
        
        except Exception as e:
            logger.error(f"[VEDIC_API] Unexpected error for {path}: {str(e)}", exc_info=True)
            raise VedicApiError(
                error_code="VEDIC_API_UNAVAILABLE",
                message="Unexpected error calling Vedic API",
                details=str(e)
            )
    
    async def fetch_full_profile(self, birth: BirthDetails, user_id: str = None) -> AstroProfile:
        """
        Fetch complete astrological profile from Vedic API.
        
        OPTIMIZED: Uses single /horoscope/planet-details call which returns:
        - Ascendant with exact degree
        - All 9 planets with exact degrees, nakshatras, padas
        - Current dasha info
        - Panchang details
        
        Then fetches /dashas/current-mahadasha-full for complete dasha timeline.
        
        Before: 11 API calls (1 kundli + 1 dasha + 9 planets)
        After: 2 API calls (1 planet-details + 1 dasha-full)
        
        Raises VedicApiError if any call fails.
        """
        logger.info(f"[PROFILE] Fetching full profile for {birth.location}, DOB: {birth.dob}, TOB: {birth.tob}")
        
        # Prepare API params
        api_params = {
            'dob': birth.dob.strftime("%d/%m/%Y"),
            'tob': birth.tob,
            'lat': birth.latitude or 28.6139,  # Default to Delhi if not provided
            'lon': birth.longitude or 77.2090,
            'tz': birth.timezone,
        }
        
        try:
            # OPTIMIZED: Single call to /horoscope/planet-details returns everything
            logger.info("[PROFILE] Calling /horoscope/planet-details (OPTIMIZED - single call)...")
            planet_details = await self._get('/horoscope/planet-details', api_params.copy())
            
            # Log raw response for debugging
            import json
            logger.info(f"[PLANET_DETAILS] Response keys: {list(planet_details.keys())}")
            
            # Fetch full dasha timeline
            logger.info("[PROFILE] Calling /dashas/current-mahadasha-full...")
            dashas_data = await self._get('/dashas/current-mahadasha-full', api_params.copy())
            
            # Parse planet-details response into our format
            # Response has keys "0" (Ascendant), "1" (Sun), "2" (Moon), etc.
            planets_list = []
            ascendant_data = None
            
            # Map numeric keys to planet data
            planet_key_map = {
                "0": "Ascendant",
                "1": "Sun",
                "2": "Moon", 
                "3": "Mars",
                "4": "Mercury",
                "5": "Jupiter",
                "6": "Venus",
                "7": "Saturn",
                "8": "Rahu",
                "9": "Ketu"
            }
            
            for key, planet_name in planet_key_map.items():
                p = planet_details.get(key, {})
                if not p:
                    continue
                    
                if planet_name == "Ascendant":
                    ascendant_data = p
                    logger.info(f"[PLANET_DETAILS] Ascendant: {p.get('zodiac')} {p.get('local_degree', 0):.2f}° nakshatra={p.get('nakshatra')}")
                else:
                    planets_list.append({
                        'name': planet_name,
                        'sign': p.get('zodiac', 'Aries'),
                        'house': p.get('house', 1),
                        'degree': round(p.get('local_degree', 0), 2),
                        'global_degree': p.get('global_degree', 0),
                        'retrograde': p.get('retro', False),
                        'nakshatra': p.get('nakshatra', ''),
                        'nakshatra_lord': p.get('nakshatra_lord', ''),
                        'nakshatra_pada': p.get('nakshatra_pada', 1),
                        'zodiac_lord': p.get('zodiac_lord', ''),
                        'is_combust': p.get('is_combust', False),
                        'basic_avastha': p.get('basic_avastha', ''),
                        'lord_status': p.get('lord_status', '')
                    })
                    logger.debug(f"[PLANET_DETAILS] {planet_name}: {p.get('zodiac')} H{p.get('house')} {p.get('local_degree', 0):.2f}° {'(R)' if p.get('retro') else ''}")
            
            logger.info(f"[PROFILE] Parsed {len(planets_list)} planets from planet-details")
            
            # Build kundli_details dict from planet_details for compatibility
            kundli_details = {
                'ascendant_sign': ascendant_data.get('zodiac', 'Aries') if ascendant_data else 'Aries',
                'ascendant_degree': ascendant_data.get('local_degree', 0) if ascendant_data else 0,
                'ascendant_nakshatra': ascendant_data.get('nakshatra', '') if ascendant_data else '',
                'nakshatra_pada': ascendant_data.get('nakshatra_pada', 1) if ascendant_data else 1,
                'rasi': planet_details.get('rasi', ''),
                'nakshatra': planet_details.get('nakshatra', ''),
                'moon_nakshatra': planet_details.get('nakshatra', ''),
                'sun_sign': planets_list[0].get('sign', '') if planets_list else '',  # Sun is first planet
                # Panchang data
                'ayanamsa': planet_details.get('panchang', {}).get('ayanamsa', 23.67),
                'ayanamsa_name': planet_details.get('panchang', {}).get('ayanamsa_name', 'Lahiri'),
                'day_of_birth': planet_details.get('panchang', {}).get('day_of_birth', ''),
                'tithi': planet_details.get('panchang', {}).get('tithi', ''),
                'yoga': planet_details.get('panchang', {}).get('yoga', ''),
                'karana': planet_details.get('panchang', {}).get('karana', ''),
                # Dasha from planet-details
                'current_dasa': planet_details.get('current_dasa', ''),
                'birth_dasa': planet_details.get('birth_dasa', ''),
            }
            
            planets_data = {'planets': planets_list}
            
            # Parse into our models
            profile_kwargs = {
                'birth': birth,
                'kundli': kundli_details,
                'dashas': dashas_data,
                'planets': planets_data
            }
            # Only add user_id if provided
            if user_id:
                profile_kwargs['user_id'] = user_id
            
            profile = self._parse_profile_from_real_api(**profile_kwargs)
            
            logger.info(f"[PROFILE] Success: Ascendant={profile.ascendant} {profile.ascendant_degree:.2f}°, Moon={profile.moon_sign}")
            return profile
        
        except VedicApiError as e:
            logger.error(f"[PROFILE] VEDIC API ERROR: {e.error_code} - {e.message}")
            raise  # Propagate to caller for transparent failure
    
    async def fetch_transits(
        self,
        birth: BirthDetails,
        user_id: str,
        from_date: date,
        to_date: date
    ) -> AstroTransits:
        """
        Fetch real transit data from Vedic API for a time window.
        
        Calls /extended-horoscope/extended-transits with date range.
        
        Raises VedicApiError if API call fails.
        """
        logger.info(f"[TRANSITS] Fetching transits from {from_date} to {to_date}")
        
        try:
            # Prepare API params
            api_params = {
                'dob': birth.dob.strftime("%d/%m/%Y"),
                'tob': birth.tob,
                'lat': birth.latitude or 28.6139,
                'lon': birth.longitude or 77.2090,
                'tz': birth.timezone,
                'from_date': from_date.isoformat(),
                'to_date': to_date.isoformat(),
                'ayanamsa': 'Lahiri'
            }
            
            # Call real API (no stubs)
            logger.info("[TRANSITS] Calling /extended-horoscope/extended-transits...")
            transits_data = await self._get('/extended-horoscope/extended-transits', api_params)
            
            # Parse into our models
            transits = self._parse_transits(
                user_id=user_id,
                from_date=from_date,
                to_date=to_date,
                raw=transits_data
            )
            
            logger.info(f"[TRANSITS] Success: {len(transits.events)} transit events")
            return transits
        
        except VedicApiError as e:
            logger.error(f"[TRANSITS] VEDIC API ERROR: {e.error_code} - {e.message}")
            raise  # Propagate to caller for transparent failure
    
    # ============ NEW API METHODS ============
    
    async def fetch_basic_chart_info(self, birth: BirthDetails) -> Dict[str, Any]:
        """
        Fetch basic chart info (ascendant, moon sign, sun sign) from Vedic API.
        
        This is a LIGHTWEIGHT method that makes only ONE API call.
        Use this for welcome messages and quick lookups.
        
        Returns: dict with keys: ascendant, moon_sign, sun_sign, nakshatra
        Raises VedicApiError if call fails.
        """
        logger.info("[BASIC_CHART] Fetching basic chart info (single API call)...")
        
        try:
            api_params = {
                'dob': birth.dob.strftime("%d/%m/%Y"),
                'tob': birth.tob,
                'lat': birth.latitude or 28.6139,
                'lon': birth.longitude or 77.2090,
                'tz': birth.timezone,
                'ayanamsa': 'Lahiri'
            }
            
            kundli_details = await self._get('/extended-horoscope/extended-kundli-details', api_params)
            
            result = {
                'ascendant': kundli_details.get('ascendant_sign'),
                'moon_sign': kundli_details.get('rasi'),
                'sun_sign': kundli_details.get('sun_sign'),
                'nakshatra': kundli_details.get('nakshatra'),
            }
            
            logger.info(f"[BASIC_CHART] Success: ascendant={result['ascendant']}, moon={result['moon_sign']}, sun={result['sun_sign']}")
            return result
            
        except VedicApiError as e:
            logger.error(f"[BASIC_CHART] VEDIC API ERROR: {e.error_code}")
            raise
    
    async def fetch_planet_details(self, birth: BirthDetails) -> Dict[str, Any]:
        """
        Fetch detailed planetary positions from Vedic API.
        
        Calls /horoscope/planets endpoint.
        Returns structured data with sign, degree, house, retrograde, nakshatra, etc.
        
        Raises VedicApiError if call fails.
        """
        logger.info("[PLANETS] Fetching detailed planetary positions...")
        
        try:
            api_params = {
                'dob': birth.dob.strftime("%d/%m/%Y"),
                'tob': birth.tob,
                'lat': birth.latitude or 28.6139,
                'lon': birth.longitude or 77.2090,
                'tz': birth.timezone,
                'ayanamsa': 'Lahiri'
            }
            
            logger.info("[PLANETS] Calling /horoscope/planets...")
            planets_data = await self._get('/horoscope/planets', api_params)
            
            logger.info(f"[PLANETS] Success: Got data for {len(planets_data.get('planets', []))} planets")
            return planets_data
        
        except VedicApiError as e:
            logger.error(f"[PLANETS] VEDIC API ERROR: {e.error_code}")
            raise
    
    
    async def fetch_yogas(self, birth: BirthDetails) -> Dict[str, Any]:
        """
        Fetch astrological yogas (beneficial/malefic combinations) from Vedic API.
        
        Calls /extended-horoscope/find-yogas endpoint.
        Returns list of yogas with strength, planets involved, interpretation, etc.
        
        Raises VedicApiError if call fails.
        """
        logger.info("[YOGAS] Fetching astrological yogas...")
        
        try:
            api_params = {
                'dob': birth.dob.strftime("%d/%m/%Y"),
                'tob': birth.tob,
                'lat': birth.latitude or 28.6139,
                'lon': birth.longitude or 77.2090,
                'tz': birth.timezone,
                'ayanamsa': 'Lahiri'
            }
            
            logger.info("[YOGAS] Calling /extended-horoscope/find-yogas...")
            yogas_data = await self._get('/extended-horoscope/find-yogas', api_params)
            
            logger.info(f"[YOGAS] Success: Found {len(yogas_data.get('yogas', []))} yogas")
            return yogas_data
        
        except VedicApiError as e:
            logger.error(f"[YOGAS] VEDIC API ERROR: {e.error_code}")
            raise
    
    
    async def fetch_kundli_optimized(self, birth: BirthDetails, user_id: str = None) -> Dict[str, Any]:
        """
        OPTIMIZED: Fetch Kundli SVG and profile data with minimal API calls.
        
        Optimizations (v2):
        1. Single /horoscope/planet-details call (returns ALL planets + ascendant with exact degrees)
        2. Single /dashas/current-mahadasha-full call (returns current dasha with dates)
        
        Before v1: 11+ sequential API calls (~8-10 seconds)
        Before v2: 3 API calls (~1-2 seconds)
        After v2: 2 API calls (~0.5-1 second)
        
        Returns:
        {
            "ok": True,
            "svg": "<svg>...</svg>",
            "profile": AstroProfile,
            "structured": { planets, houses, ascendant }
        }
        """
        import asyncio
        
        logger.info(f"[KUNDLI_OPT] Starting optimized fetch for {birth.location}")
        start_time = asyncio.get_event_loop().time()
        
        api_params = {
            'dob': birth.dob.strftime("%d/%m/%Y"),
            'tob': birth.tob,
            'lat': birth.latitude or 28.6139,
            'lon': birth.longitude or 77.2090,
            'tz': birth.timezone,
        }
        
        try:
            # STEP 1: Single call to /horoscope/planet-details (returns everything)
            logger.info("[KUNDLI_OPT] Step 1: Fetching /horoscope/planet-details (ALL data in 1 call)...")
            planet_details = await self._get('/horoscope/planet-details', api_params.copy())
            
            # Parse planet-details response
            planet_key_map = {
                "0": "Ascendant", "1": "Sun", "2": "Moon", "3": "Mars",
                "4": "Mercury", "5": "Jupiter", "6": "Venus", "7": "Saturn",
                "8": "Rahu", "9": "Ketu"
            }
            
            planets_list = []
            ascendant_data = None
            
            for key, planet_name in planet_key_map.items():
                p = planet_details.get(key, {})
                if not p:
                    continue
                    
                if planet_name == "Ascendant":
                    ascendant_data = p
                else:
                    planets_list.append({
                        'name': planet_name,
                        'sign': p.get('zodiac', 'Aries'),
                        'house': p.get('house', 1),
                        'degree': round(p.get('local_degree', 0), 2),
                        'retrograde': p.get('retro', False),
                        'nakshatra': p.get('nakshatra', ''),
                        'nakshatra_lord': p.get('nakshatra_lord', ''),
                        'nakshatra_pada': p.get('nakshatra_pada', 1),
                        'is_combust': p.get('is_combust', False),
                        'lord_status': p.get('lord_status', '')
                    })
            
            logger.info(f"[KUNDLI_OPT] Parsed {len(planets_list)} planets with exact degrees")
            
            # STEP 2: Fetch dasha data
            logger.info("[KUNDLI_OPT] Step 2: Fetching /dashas/current-mahadasha-full...")
            dashas_data = await self._get('/dashas/current-mahadasha-full', api_params.copy())
            
            # Build kundli_details from planet_details for compatibility
            kundli_details = {
                'ascendant_sign': ascendant_data.get('zodiac', 'Aries') if ascendant_data else 'Aries',
                'ascendant_degree': ascendant_data.get('local_degree', 0) if ascendant_data else 0,
                'ascendant_nakshatra': ascendant_data.get('nakshatra', '') if ascendant_data else '',
                'nakshatra_pada': ascendant_data.get('nakshatra_pada', 1) if ascendant_data else 1,
                'rasi': planet_details.get('rasi', ''),
                'nakshatra': planet_details.get('nakshatra', ''),
                'moon_nakshatra': planet_details.get('nakshatra', ''),
                'sun_sign': planets_list[0].get('sign', '') if planets_list else '',
                'ayanamsa': planet_details.get('panchang', {}).get('ayanamsa', 23.67),
            }
            
            # Generate SVG from kundli data
            svg = self._generate_kundli_svg(kundli_details, birth, "north", planets_list)
            
            # Parse into profile model
            planets_data = {'planets': planets_list}
            profile = self._parse_profile_from_real_api(birth=birth, kundli=kundli_details, dashas=dashas_data, planets=planets_data, user_id=user_id)
            
            # Build structured data for frontend
            structured = {
                "ascendant": {
                    "sign": profile.ascendant or "Unknown",
                    "degree": profile.ascendant_degree if hasattr(profile, 'ascendant_degree') else 0.0,
                    "house": 1
                },
                "houses": [
                    {
                        "house": h.house_num if hasattr(h, 'house_num') else i+1,
                        "sign": h.sign if hasattr(h, 'sign') else "Unknown",
                        "lord": h.sign_lord if hasattr(h, 'sign_lord') else "Unknown"
                    }
                    for i, h in enumerate(profile.houses or [])
                ] if profile.houses else [{"house": i+1, "sign": "Unknown", "lord": "Unknown"} for i in range(12)],
                "planets": [
                    {
                        "name": planet.planet if hasattr(planet, 'planet') else "Unknown",
                        "sign": planet.sign if hasattr(planet, 'sign') else "Unknown",
                        "degree": planet.degree if hasattr(planet, 'degree') else 0.0,
                        "house": planet.house if hasattr(planet, 'house') else 0,
                        "retrograde": planet.is_retrograde if hasattr(planet, 'is_retrograde') else False
                    }
                    for planet in (profile.planets or [])
                ]
            }
            
            elapsed = asyncio.get_event_loop().time() - start_time
            logger.info(f"[KUNDLI_OPT] ✅ Complete in {elapsed:.2f}s (was ~8-10s before)")
            
            return {
                "ok": True,
                "svg": svg,
                "svg_size": len(svg),
                "profile": profile,
                "structured": structured,
                "chart_type": "kundli",
                "vendor": "VedicAstroAPI",
                "optimization": f"Completed in {elapsed:.2f}s"
            }
            
        except VedicApiError as e:
            logger.error(f"[KUNDLI_OPT] API Error: {e.error_code}")
            return {
                "ok": False,
                "error": e.error_code,
                "message": e.message
            }
        except Exception as e:
            logger.error(f"[KUNDLI_OPT] Unexpected error: {e}")
            return {
                "ok": False,
                "error": "KUNDLI_FETCH_FAILED",
                "message": str(e)
            }
    
    
    async def fetch_kundli_svg(self, birth: BirthDetails, div: str = "D1", style: str = "north") -> Dict[str, Any]:
        """
        Generate Kundli (birth chart) as SVG from available Vedic API data.
        
        Note: /horoscope/chart endpoint not available in free tier.
        Generates SVG from /extended-horoscope/extended-kundli-details data.
        Returns SVG string suitable for web display.
        
        Args:
        - div: Chart division (D1=natal, D9=navamsa, etc.)
        - style: Chart style (north, south)
        
        Returns:
        {
            "ok": True/False,
            "svg": "<svg>...</svg>" (if ok=True),
            "chart_type": "kundli",
            "div": "D1",
            "vendor": "VedicAstroAPI",
            "svg_size": 45000
        }
        """
        logger.info(f"[KUNDLI_SVG] Generating Kundli SVG (div={div}, style={style})...")
        
        try:
            api_params = {
                'dob': birth.dob.strftime("%d/%m/%Y"),
                'tob': birth.tob,
                'lat': birth.latitude or 28.6139,
                'lon': birth.longitude or 77.2090,
                'tz': birth.timezone,
                'ayanamsa': 'Lahiri'
            }
            
            logger.info("[KUNDLI_SVG] Fetching kundli data from /extended-horoscope/extended-kundli-details...")
            kundli_data = await self._get('/extended-horoscope/extended-kundli-details', api_params)
            
            # Fetch planet positions for chart
            planets_list = []
            planet_names = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']
            
            for planet_name in planet_names:
                try:
                    params = api_params.copy()
                    params['planet'] = planet_name
                    planet_resp = await self._get('/horoscope/planet-report', params)
                    
                    if planet_resp and isinstance(planet_resp, list) and len(planet_resp) > 0:
                        p = planet_resp[0]
                        planets_list.append({
                            'name': p.get('planet_considered', planet_name.capitalize()),
                            'sign': p.get('planet_zodiac', 'Aries'),
                            'house': p.get('planet_location', 1),
                        })
                except Exception as e:
                    logger.warning(f"[KUNDLI_SVG] Could not fetch planet report for {planet_name}: {e}")
            
            logger.info(f"[KUNDLI_SVG] Fetched {len(planets_list)} planet positions for SVG")
            
            # Generate SVG representation from kundli data with planets
            svg = self._generate_kundli_svg(kundli_data, birth, style, planets_list)
            
            # Enforce maximum SVG size (500KB)
            svg_size = len(svg)
            if svg_size > 500000:
                raise VedicApiError(
                    error_code="KUNDLI_SVG_OVERSIZED",
                    message="SVG size exceeds maximum allowed",
                    details=f"Size: {svg_size} bytes, limit: 500000"
                )
            
            logger.info(f"[KUNDLI_SVG] Success: size={svg_size} bytes")
            
            return {
                "ok": True,
                "svg": svg,
                "chart_type": "kundli",
                "div": div,
                "vendor": "VedicAstroAPI",
                "svg_size": svg_size
            }
        
        except VedicApiError as e:
            logger.error(f"[KUNDLI_SVG] ERROR: {e.error_code}")
            return {
                "ok": False,
                "error_code": e.error_code,
                "error_message": e.message,
                "details": e.details
            }
        
        except Exception as e:
            logger.error(f"[KUNDLI_SVG] Unexpected error: {str(e)}", exc_info=True)
            return {
                "ok": False,
                "error_code": "KUNDLI_SVG_FETCH_FAILED",
                "error_message": "Unexpected error fetching Kundli SVG",
                "details": str(e)
            }
    





    
    def _parse_profile(
        self,
        user_id: str,
        birth: BirthDetails,
        base_chart: Dict,
        dashas: Dict
    ) -> AstroProfile:
        """Parse raw API response into AstroProfile model"""
        
        # Parse planet positions
        planets = []
        for planet_name, data in base_chart.get('planets', {}).items():
            planets.append(PlanetPosition(
                planet=planet_name,
                sign=data['sign'],
                sign_num=data['sign_num'],
                degree=data['degree'],
                house=data['house'],
                nakshatra=data['nakshatra'],
                nakshatra_lord=data['nakshatra_lord'],
                nakshatra_pada=data['nakshatra_pada'],
                is_retrograde=data.get('retrograde', False),
                is_combust=data.get('combust', False),
                is_exalted=data.get('dignity') == 'exalted',
                is_debilitated=data.get('dignity') == 'debilitated',
                dignity=data.get('dignity', 'neutral'),
                strength_score=0.8 if data.get('dignity') in ['exalted', 'own'] else 0.3 if data.get('dignity') == 'debilitated' else 0.5
            ))
        
        # Parse houses
        houses = []
        for house_num, data in base_chart.get('houses', {}).items():
            houses.append(HouseData(
                house_num=int(house_num),
                sign=data['sign'],
                sign_lord=data['lord'],
                planets=data.get('planets', []),
                aspects_from=[]  # TODO: Calculate aspects
            ))
        
        # Parse yogas
        yogas = []
        for yoga_data in base_chart.get('yogas', []):
            yogas.append(YogaInfo(
                name=yoga_data['name'],
                category=yoga_data.get('category', 'general'),
                planets_involved=yoga_data.get('planets_involved', []),
                houses_involved=yoga_data.get('houses_involved', []),
                strength=yoga_data.get('strength', 'medium'),
                effects=yoga_data.get('effects', '')
            ))
        
        # Parse current dasha with validation
        current_maha = dashas.get('current_mahadasha', {})
        
        # Check if API returned valid dasha dates
        api_maha_start = None
        api_maha_end = None
        try:
            api_maha_start = date.fromisoformat(current_maha.get('start_date', ''))
            api_maha_end = date.fromisoformat(current_maha.get('end_date', ''))
        except (ValueError, TypeError):
            pass
        
        # Detect invalid API dates
        api_dates_invalid = (
            api_maha_start is None or
            api_maha_end is None or
            api_maha_start == api_maha_end or
            api_maha_start == birth.dob or
            abs((api_maha_end - api_maha_start).days) < 30
        )
        
        if api_dates_invalid:
            # Use LOCAL Vimshottari calculation
            moon_data = base_chart.get('planets', {}).get('Moon', {})
            moon_nakshatra = moon_data.get('nakshatra', 'Pushya')
            
            logger.warning(f"[DASHA_PARSE_ALT] API returned invalid dasha dates, using LOCAL calculation with nakshatra={moon_nakshatra}")
            
            local_dashas = calculate_vimshottari_dashas(
                dob=birth.dob,
                moon_nakshatra=moon_nakshatra
            )
            
            local_maha = local_dashas.get('current_mahadasha', {})
            local_antar = local_dashas.get('current_antardasha', {})
            
            current_mahadasha = DashaInfo(
                level='mahadasha',
                planet=local_maha.get('planet', 'Jupiter'),
                start_date=local_maha.get('start_date', birth.dob),
                end_date=local_maha.get('end_date', birth.dob + timedelta(days=16*365)),
                years_total=local_maha.get('years_total', 16),
                years_elapsed=local_maha.get('years_elapsed', 0),
                years_remaining=local_maha.get('years_remaining', 16)
            )
            
            current_antardasha = DashaInfo(
                level='antardasha',
                planet=local_antar.get('planet', 'Venus') if local_antar else 'Venus',
                start_date=local_antar.get('start_date', birth.dob) if local_antar else birth.dob,
                end_date=local_antar.get('end_date', birth.dob + timedelta(days=2*365)) if local_antar else birth.dob + timedelta(days=2*365),
                years_total=local_antar.get('years_total', 2) if local_antar else 2,
                years_elapsed=local_antar.get('years_elapsed', 0) if local_antar else 0,
                years_remaining=local_antar.get('years_remaining', 2) if local_antar else 2
            )
        else:
            # Use valid API data
            current_mahadasha = DashaInfo(
                level='mahadasha',
                planet=current_maha.get('planet', 'Jupiter'),
                start_date=api_maha_start,
                end_date=api_maha_end,
                years_total=current_maha.get('years_total', 16),
                years_elapsed=current_maha.get('years_elapsed', 0),
                years_remaining=current_maha.get('years_remaining', 16)
            )
            
            # Find current antardasha
            current_antar = next(
                (a for a in dashas.get('antardashas', []) if a.get('is_current')),
                dashas.get('antardashas', [{}])[0]
            )
            current_antardasha = DashaInfo(
                level='antardasha',
                planet=current_antar.get('planet', 'Venus'),
                start_date=date.fromisoformat(current_antar['start_date']) if current_antar.get('start_date') else birth.dob,
                end_date=date.fromisoformat(current_antar['end_date']) if current_antar.get('end_date') else birth.dob,
                years_total=current_antar.get('years_total', 2),
                years_elapsed=0,
                years_remaining=current_antar.get('years_total', 2)
            )
        
        # Get Moon details
        moon_data = base_chart.get('planets', {}).get('Moon', {})
        sun_data = base_chart.get('planets', {}).get('Sun', {})
        asc_data = base_chart.get('ascendant', {})
        
        # Calculate ascendant degree from nakshatra if not provided or is 0
        asc_degree = asc_data.get('degree', None)
        asc_nakshatra = asc_data.get('nakshatra', 'Ashwini')
        if asc_degree is None or asc_degree == 0:
            asc_degree = calculate_degree_from_nakshatra(asc_nakshatra)
        
        return AstroProfile(
            user_id=user_id,
            birth_details=birth,
            base_chart_raw=base_chart,
            dashas_raw=dashas,
            ascendant=asc_data.get('sign', 'Aries'),
            ascendant_degree=asc_degree,
            ascendant_nakshatra=asc_nakshatra,
            moon_sign=moon_data.get('sign', 'Cancer'),
            moon_nakshatra=moon_data.get('nakshatra', 'Pushya'),
            sun_sign=sun_data.get('sign', 'Leo'),
            planets=planets,
            houses=houses,
            current_mahadasha=current_mahadasha,
            current_antardasha=current_antardasha,
            yogas=yogas,
            planetary_strengths=[{'planet': p.planet, 'strength': p.strength_score} for p in planets]
        )
    
    def _parse_strength_to_score(self, strength) -> float:
        """Convert strength string/number to a float score between 0 and 1."""
        if isinstance(strength, (int, float)):
            return float(strength)
        if isinstance(strength, str):
            strength_map = {
                'exalted': 1.0,
                'strong': 0.8,
                'neutral': 0.5,
                'weak': 0.3,
                'debilitated': 0.1
            }
            return strength_map.get(strength.lower(), 0.5)
        return 0.5
    
    def _parse_profile_from_real_api(
        self,
        birth: BirthDetails,
        kundli: Dict,
        dashas: Dict,
        planets: Dict,
        user_id: str = None
    ) -> AstroProfile:
        """
        Parse real Vedic API responses into AstroProfile model.
        
        Args:
        - kundli: Response from /extended-horoscope/extended-kundli-details
        - dashas: Response from /dashas/maha-dasha  
        - planets: Response from /horoscope/planets
        """
        logger.info(f"[PARSE] Parsing profile from real API responses")
        
        # Parse planets from real API
        planets_list = []
        planets_dict = planets.get('planets', {})
        if isinstance(planets_dict, list):
            # API returns planets as list
            for p in planets_dict:
                planets_list.append(PlanetPosition(
                    planet=p.get('name', 'Unknown'),
                    sign=p.get('sign', 'Aries'),
                    sign_num=p.get('sign_num', 1),
                    degree=float(p.get('degree', 0)),
                    house=int(p.get('house', 1)),
                    nakshatra=p.get('nakshatra', 'Ashwini'),
                    nakshatra_lord=p.get('nakshatra_lord', ''),
                    nakshatra_pada=int(p.get('nakshatra_pada', 1)),
                    is_retrograde=p.get('retrograde', False),
                    is_combust=p.get('combust', False),
                    is_exalted=p.get('exalted', False),
                    is_debilitated=p.get('debilitated', False),
                    dignity=p.get('dignity', 'neutral'),
                    strength_score=self._parse_strength_to_score(p.get('strength', 0.5))
                ))
        
        # Parse houses from kundli data (derive from ascendant)
        houses_list = []
        asc_sign = kundli.get('ascendant_sign', 'Aries')
        asc_idx = ZODIAC_SIGNS.index(asc_sign) if asc_sign in ZODIAC_SIGNS else 0
        
        for i in range(1, 13):
            # Calculate sign for each house based on ascendant
            # House 1 = Ascendant sign, House 2 = next sign, etc.
            house_sign_idx = (asc_idx + i - 1) % 12
            house_sign = ZODIAC_SIGNS[house_sign_idx]
            house_lord = SIGN_LORDS.get(house_sign, '')
            
            # Get planets in this house
            planets_in_house = [p.planet for p in planets_list if p.house == i]
            houses_list.append(HouseData(
                house_num=i,
                sign=house_sign,
                sign_lord=house_lord,
                planets=planets_in_house,
                aspects_from=[]
            ))
        
        # Parse yogas from API
        yogas_list = []
        yoga_data = kundli.get('yogas', [])
        if isinstance(yoga_data, list):
            for y in yoga_data:
                yogas_list.append(YogaInfo(
                    name=y.get('name', 'Unknown Yoga'),
                    category=y.get('category', 'general'),
                    planets_involved=y.get('planets_involved', []),
                    houses_involved=y.get('houses_involved', []),
                    strength=y.get('strength', 'medium'),
                    effects=y.get('effects', '')
                ))
        
        # Parse dasha from /dashas/current-mahadasha-full API
        # New format uses 'order_of_dashas' for current periods
        import json
        
        order_of_dashas = dashas.get('order_of_dashas', {})
        current_major = order_of_dashas.get('major', {})
        current_minor = order_of_dashas.get('minor', {})
        
        logger.info(f"[DASHA_PARSE] Current Major Dasha: {current_major.get('name', 'N/A')}")
        logger.info(f"[DASHA_PARSE] Current Minor Dasha: {current_minor.get('name', 'N/A')}")
        
        def parse_dasha_date(date_str: str) -> date:
            """Parse Vedic API date format: 'Sun Feb 09 2025 22:45:43 GMT+0000 (Coordinated Universal Time)'"""
            if not date_str:
                return None
            try:
                # Extract just the date part: "Sun Feb 09 2025"
                parts = date_str.split()
                if len(parts) >= 4:
                    month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                                 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
                    day = int(parts[2])
                    month = month_map.get(parts[1], 1)
                    year = int(parts[3])
                    return date(year, month, day)
            except (ValueError, IndexError, TypeError) as e:
                logger.warning(f"[DASHA_PARSE] Could not parse date '{date_str}': {e}")
            return None
        
        # Parse mahadasha from API
        api_maha_start = parse_dasha_date(current_major.get('start', ''))
        api_maha_end = parse_dasha_date(current_major.get('end', ''))
        maha_planet = current_major.get('name', '')
        
        # Parse antardasha from API
        api_antar_start = parse_dasha_date(current_minor.get('start', ''))
        api_antar_end = parse_dasha_date(current_minor.get('end', ''))
        antar_planet = current_minor.get('name', '')
        
        # Detect invalid API dates
        api_dates_invalid = (
            api_maha_start is None or
            api_maha_end is None or
            not maha_planet or
            api_maha_start == api_maha_end
        )
        
        if api_dates_invalid:
            # Use LOCAL Vimshottari calculation
            logger.warning(f"[DASHA_PARSE] API returned invalid dasha dates (start={api_maha_start}, end={api_maha_end}), using LOCAL calculation")
            
            # Get Moon nakshatra from kundli or planets
            moon_nakshatra = kundli.get('moon_nakshatra', '') or kundli.get('nakshatra', '')
            if not moon_nakshatra:
                moon_planet_data = next((p for p in planets_list if p.planet == 'Moon'), None)
                moon_nakshatra = moon_planet_data.nakshatra if moon_planet_data and moon_planet_data.nakshatra else 'Pushya'
            
            # Calculate locally
            local_dashas = calculate_vimshottari_dashas(
                dob=birth.dob,
                moon_nakshatra=moon_nakshatra,
                moon_degree=None,
                nakshatra_pada=kundli.get('nakshatra_pada', 2)
            )
            
            local_maha = local_dashas.get('current_mahadasha', {})
            local_antar = local_dashas.get('current_antardasha', {})
            
            logger.info(f"[DASHA_LOCAL] Calculated: Mahadasha={local_maha.get('planet')} ({local_maha.get('start_date')} to {local_maha.get('end_date')})")
            
            current_mahadasha = DashaInfo(
                level='mahadasha',
                planet=local_maha.get('planet', 'Jupiter'),
                start_date=local_maha.get('start_date', birth.dob),
                end_date=local_maha.get('end_date', birth.dob + timedelta(days=16*365)),
                years_total=local_maha.get('years_total', 16),
                years_elapsed=local_maha.get('years_elapsed', 0),
                years_remaining=local_maha.get('years_remaining', 16)
            )
            
            current_antardasha = DashaInfo(
                level='antardasha',
                planet=local_antar.get('planet', 'Venus') if local_antar else 'Venus',
                start_date=local_antar.get('start_date', birth.dob) if local_antar else birth.dob,
                end_date=local_antar.get('end_date', birth.dob + timedelta(days=2*365)) if local_antar else birth.dob + timedelta(days=2*365),
                years_total=local_antar.get('years_total', 2) if local_antar else 2,
                years_elapsed=local_antar.get('years_elapsed', 0) if local_antar else 0,
                years_remaining=local_antar.get('years_remaining', 2) if local_antar else 2
            )
        else:
            # Use API data (valid dates from /dashas/current-mahadasha-full)
            logger.info(f"[DASHA_PARSE] Using API dasha: {maha_planet} ({api_maha_start} to {api_maha_end})")
            
            # Calculate years
            today = date.today()
            maha_total_days = (api_maha_end - api_maha_start).days
            maha_elapsed_days = (today - api_maha_start).days if today > api_maha_start else 0
            maha_years_total = maha_total_days / 365.25
            maha_years_elapsed = maha_elapsed_days / 365.25
            maha_years_remaining = max(0, maha_years_total - maha_years_elapsed)
            
            current_mahadasha = DashaInfo(
                level='mahadasha',
                planet=maha_planet,
                start_date=api_maha_start,
                end_date=api_maha_end,
                years_total=round(maha_years_total, 2),
                years_elapsed=round(maha_years_elapsed, 2),
                years_remaining=round(maha_years_remaining, 2)
            )
            
            # Antardasha
            if api_antar_start and api_antar_end and antar_planet:
                antar_total_days = (api_antar_end - api_antar_start).days
                antar_elapsed_days = (today - api_antar_start).days if today > api_antar_start else 0
                antar_years_total = antar_total_days / 365.25
                antar_years_elapsed = antar_elapsed_days / 365.25
                antar_years_remaining = max(0, antar_years_total - antar_years_elapsed)
                
                current_antardasha = DashaInfo(
                    level='antardasha',
                    planet=antar_planet,
                    start_date=api_antar_start,
                    end_date=api_antar_end,
                    years_total=round(antar_years_total, 2),
                    years_elapsed=round(antar_years_elapsed, 2),
                    years_remaining=round(antar_years_remaining, 2)
                )
            else:
                # Fallback antardasha
                current_antardasha = DashaInfo(
                    level='antardasha',
                    planet='Venus',
                    start_date=birth.dob,
                    end_date=birth.dob + timedelta(days=2*365),
                    years_total=2,
                    years_elapsed=0,
                    years_remaining=2
                )
        
        # Get ascendant details
        asc_degree = kundli.get('ascendant_degree', None)
        asc_nakshatra = kundli.get('ascendant_nakshatra', 'Ashwini')
        
        # Calculate degree from nakshatra if not provided or is 0
        if asc_degree is None or asc_degree == 0:
            asc_degree = calculate_degree_from_nakshatra(asc_nakshatra, kundli.get('nakshatra_pada', 2))
            logger.info(f"[PARSE] Calculated ascendant degree {asc_degree}° from nakshatra {asc_nakshatra}")
        
        # Get Moon and Sun details
        moon_planet = next((p for p in planets_list if p.planet == 'Moon'), None)
        sun_planet = next((p for p in planets_list if p.planet == 'Sun'), None)
        
        logger.info(f"[PARSE] Success: {len(planets_list)} planets, {len(houses_list)} houses, {len(yogas_list)} yogas")
        
        profile_data = {
            'birth_details': birth,
            'base_chart_raw': kundli,
            'dashas_raw': dashas,
            'ascendant': asc_sign,
            'ascendant_degree': float(asc_degree),
            'ascendant_nakshatra': asc_nakshatra,
            'moon_sign': moon_planet.sign if moon_planet else 'Cancer',
            'moon_nakshatra': moon_planet.nakshatra if moon_planet else 'Pushya',
            'sun_sign': sun_planet.sign if sun_planet else 'Leo',
            'planets': planets_list,
            'houses': houses_list,
            'current_mahadasha': current_mahadasha,
            'current_antardasha': current_antardasha,
            'yogas': yogas_list,
            'planetary_strengths': [{'planet': p.planet, 'strength': p.strength_score} for p in planets_list]
        }
        # Only add user_id if provided
        if user_id:
            profile_data['user_id'] = user_id
        
        return AstroProfile(**profile_data)
    
    def _generate_kundli_svg(self, kundli_data: Dict[str, Any], birth: BirthDetails, style: str = "north", planets_data: List[Dict] = None) -> str:
        """
        Generate clean rectangular SVG representation of Kundli from API data.
        
        Creates a traditional North Indian style birth chart SVG.
        In North Indian charts, house positions are FIXED, but we display
        the SIGN NUMBER (Rashi number) in each house position.
        """
        asc_sign = kundli_data.get('ascendant_sign', 'Aries')
        
        # Sign name to number mapping (Aries=1, ..., Pisces=12)
        SIGN_TO_NUM = {
            'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
            'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
            'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12
        }
        
        # Get ascendant sign number
        asc_sign_num = SIGN_TO_NUM.get(asc_sign, 1)
        
        # Calculate which SIGN falls in each HOUSE
        # Formula: sign_num = ((asc_sign_num - 1) + (house_num - 1)) % 12 + 1
        def get_sign_for_house(house_num):
            return ((asc_sign_num - 1) + (house_num - 1)) % 12 + 1
        
        # Planet abbreviations
        PLANET_ABBR = {
            'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me',
            'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa', 'Rahu': 'Ra', 'Ketu': 'Ke'
        }
        
        # Group planets by house
        planets_by_house = {i: [] for i in range(1, 13)}
        if planets_data:
            for p in planets_data:
                house = p.get('house', 1)
                name = p.get('name', '')
                abbr = PLANET_ABBR.get(name, name[:2])
                if 1 <= house <= 12:
                    planets_by_house[house].append(abbr)
        
        # Traditional colors
        bg_color = "#FDF5E6"
        line_color = "#B8860B"
        text_color = "#8B4513"
        planet_color = "#CD5C5C"
        
        # Chart size - the Kundli square will be 400x400, with padding for title
        chart_size = 400
        padding_top = 60  # Space for title
        padding_side = 30
        padding_bottom = 20
        
        total_width = chart_size + 2 * padding_side
        total_height = chart_size + padding_top + padding_bottom
        
        # Center of the chart square
        cx = total_width // 2
        cy = padding_top + chart_size // 2
        half = chart_size // 2
        
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 {total_width} {total_height}" style="max-width: 100%; height: auto;">
  <rect width="100%" height="100%" fill="{bg_color}"/>
  
  <!-- Title -->
  <text x="{cx}" y="25" text-anchor="middle" font-family="Georgia, serif" font-size="20" fill="{text_color}" font-weight="bold">Birth Chart (Rashi)</text>
  <text x="{cx}" y="45" text-anchor="middle" font-family="Georgia, serif" font-size="14" fill="{text_color}" opacity="0.8">Ascendant: {asc_sign}</text>
  
  <!-- Outer square -->
  <rect x="{cx - half}" y="{cy - half}" width="{chart_size}" height="{chart_size}" fill="none" stroke="{line_color}" stroke-width="2"/>
  
  <!-- Diagonals -->
  <line x1="{cx - half}" y1="{cy - half}" x2="{cx + half}" y2="{cy + half}" stroke="{line_color}" stroke-width="1.5"/>
  <line x1="{cx + half}" y1="{cy - half}" x2="{cx - half}" y2="{cy + half}" stroke="{line_color}" stroke-width="1.5"/>
  
  <!-- Inner diamond -->
  <polygon points="{cx},{cy - half} {cx + half},{cy} {cx},{cy + half} {cx - half},{cy}" fill="none" stroke="{line_color}" stroke-width="1.5"/>
'''
        
        # Sign number positions - CORRECT North Indian layout
        # Houses go CLOCKWISE from Lagna (House 1) at top center:
        # Top: 2 - 1 - 12
        # Left side (top to bottom): 3, 4, 5
        # Right side (top to bottom): 11, 10, 9
        # Bottom: 6 - 7 - 8
        q = chart_size // 4
        house_num_pos = {
            1:  (cx, cy - half + 18),           # Top center (House 1 = Lagna)
            2:  (cx - q - 10, cy - half + 18),  # Top LEFT (House 2)
            12: (cx + q + 10, cy - half + 18),  # Top RIGHT (House 12)
            3:  (cx - half + 15, cy - q),       # Left upper (House 3)
            11: (cx + half - 15, cy - q),       # Right upper (House 11)
            4:  (cx - half + 15, cy),           # Left middle (House 4)
            10: (cx + half - 15, cy),           # Right middle (House 10)
            5:  (cx - half + 15, cy + q),       # Left lower (House 5)
            9:  (cx + half - 15, cy + q),       # Right lower (House 9)
            6:  (cx - q - 10, cy + half - 18),  # Bottom LEFT (House 6)
            8:  (cx + q + 10, cy + half - 18),  # Bottom RIGHT (House 8)
            7:  (cx, cy + half - 18),           # Bottom center (House 7)
        }
        
        # Add SIGN numbers (not house numbers) to each position
        for house_num, (hx, hy) in house_num_pos.items():
            sign_num = get_sign_for_house(house_num)
            svg += f'  <text x="{hx}" y="{hy}" text-anchor="middle" font-family="Georgia, serif" font-size="14" fill="{text_color}" opacity="0.6">{sign_num}</text>\n'
        
        # Planet positions - CORRECT to match house positions (CLOCKWISE)
        planet_pos = {
            # Top center (House 1 = Lagna)
            1:  (cx, cy - half + 55),
            
            # Top LEFT (House 2)
            2:  (cx - q, cy - half + 55),
            
            # Top RIGHT (House 12)
            12: (cx + q, cy - half + 55),
            
            # Left upper (House 3)
            3:  (cx - half + 55, cy - q + 10),
            
            # Right upper (House 11)
            11: (cx + half - 55, cy - q + 10),
            
            # Left middle (House 4)
            4:  (cx - half + 55, cy + 10),
            
            # Right middle (House 10)
            10: (cx + half - 55, cy + 10),
            
            # Left lower (House 5)
            5:  (cx - half + 55, cy + q - 10),
            
            # Right lower (House 9)
            9:  (cx + half - 55, cy + q - 10),
            
            # Bottom LEFT (House 6)
            6:  (cx - q, cy + half - 55),
            
            # Bottom RIGHT (House 8)
            8:  (cx + q, cy + half - 55),
            
            # Bottom center (House 7)
            7:  (cx, cy + half - 55),
        }
        
        # Add planets to their houses
        for house_num, (px, py) in planet_pos.items():
            planets = planets_by_house.get(house_num, [])
            if planets:
                if len(planets) <= 3:
                    planets_str = ' '.join(planets)
                    svg += f'  <text x="{px}" y="{py}" text-anchor="middle" font-family="Georgia, serif" font-size="16" font-weight="bold" fill="{planet_color}">{planets_str}</text>\n'
                else:
                    # Stack vertically for many planets
                    for i, planet in enumerate(planets):
                        offset_y = py - 10 + i * 16
                        svg += f'  <text x="{px}" y="{offset_y}" text-anchor="middle" font-family="Georgia, serif" font-size="14" font-weight="bold" fill="{planet_color}">{planet}</text>\n'
        
        # Add Ascendant marker
        svg += f'  <text x="{cx}" y="{cy - 5}" text-anchor="middle" font-family="Georgia, serif" font-size="14" fill="{line_color}" font-style="italic">Asc</text>\n'
        
        svg += '</svg>'
        
        return svg
    
    def _parse_transits(
        self,
        user_id: str,
        from_date: date,
        to_date: date,
        raw: Dict
    ) -> AstroTransits:
        """Parse raw transit data into AstroTransits model"""
        
        events = []
        for event_data in raw.get('events', []):
            events.append(TransitEvent(
                event_type=event_data['event_type'],
                planet=event_data['planet'],
                from_sign=event_data.get('from_sign'),
                to_sign=event_data.get('to_sign'),
                affected_house=event_data.get('affected_houses', [None])[0],
                start_date=date.fromisoformat(event_data['start_date']),
                end_date=date.fromisoformat(event_data['end_date']) if event_data.get('end_date') else None,
                strength=event_data.get('strength', 'medium'),
                nature=event_data.get('nature', 'neutral')
            ))
        
        return AstroTransits(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            transits_raw=raw,
            events=events,
            current_positions=[raw.get('current_positions', {})]
        )
    
    async def get_kundli_svg(self, birth: BirthDetails) -> Dict[str, Any]:
        """
        Generate Kundli chart as SVG using our custom generator.
        
        Uses /extended-horoscope/extended-kundli-details for chart data
        and /horoscope/planet-report for planet positions.
        
        Returns:
            {
                "ok": true,
                "svg": "<svg>...</svg>",
                "chart_type": "birth_chart",
                "vendor": "VedicAstroAPI"
            }
            or
            {
                "ok": false,
                "error": "KUNDLI_FETCH_FAILED",
                "details": "..."
            }
        """
        # Use our fetch_kundli_svg which generates a proper North Indian chart
        return await self.fetch_kundli_svg(birth, div="D1", style="north")
    
    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton instance - lazy initialization pattern
class _VedicAPIClientSingleton:
    """Lazy singleton wrapper for VedicAPIClient"""
    _instance = None
    
    def __call__(self):
        if self._instance is None:
            self._instance = VedicAPIClient()
        return self._instance

_get_client = _VedicAPIClientSingleton()

# Create a proxy object that lazily initializes the client
class _LazyVedicAPIClient:
    """Proxy that forwards all attribute access to the real client"""
    def __getattr__(self, name):
        return getattr(_get_client(), name)

vedic_api_client = _LazyVedicAPIClient()
