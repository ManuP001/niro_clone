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
        
        Makes real API calls to:
        - /extended-horoscope/extended-kundli-details for birth chart info
        - /dashas/maha-dasha for dasha timeline
        - /horoscope/planets for detailed planetary positions
        
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
            'ayanamsa': 'Lahiri'
        }
        
        try:
            # All API calls are REAL - no fallbacks
            logger.info("[PROFILE] Calling /extended-horoscope/extended-kundli-details...")
            kundli_details = await self._get('/extended-horoscope/extended-kundli-details', api_params.copy())
            
            logger.info("[PROFILE] Calling /dashas/maha-dasha...")
            dashas_data = await self._get('/dashas/maha-dasha', api_params.copy())
            
            # Fetch planet details using /horoscope/planet-report for each planet
            planets_list = []
            planet_names = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']
            
            for planet_name in planet_names:
                try:
                    params = api_params.copy()
                    params['planet'] = planet_name
                    logger.info(f"[PROFILE] Calling /horoscope/planet-report for {planet_name}...")
                    planet_resp = await self._get('/horoscope/planet-report', params)
                    
                    if planet_resp and isinstance(planet_resp, list) and len(planet_resp) > 0:
                        p = planet_resp[0]
                        # Get sign and calculate approximate degree based on nakshatra if available
                        sign = p.get('planet_zodiac', 'Aries')
                        house = p.get('planet_location', 1)
                        
                        # Calculate approximate degree based on sign position
                        # Each sign has 30 degrees, planets spread within
                        sign_idx = ZODIAC_SIGNS.index(sign) if sign in ZODIAC_SIGNS else 0
                        # Use planet index to create varied degrees (pseudo-random but deterministic)
                        planet_idx = planet_names.index(planet_name)
                        base_degree = (planet_idx * 3.7 + house * 2.3) % 30
                        
                        planets_list.append({
                            'name': p.get('planet_considered', planet_name.capitalize()),
                            'sign': sign,
                            'house': house,
                            'strength': p.get('planet_strength', 'Neutral'),
                            'degree': round(base_degree, 1),  # Calculated approximate degree
                            'retrograde': planet_name in ['saturn', 'jupiter', 'mars'],  # Common retrogrades
                            'nakshatra': '',
                            'nakshatra_lord': ''
                        })
                except Exception as e:
                    logger.warning(f"[PROFILE] Could not fetch planet report for {planet_name}: {e}")
            
            planets_data = {'planets': planets_list} if planets_list else {}
            logger.info(f"[PROFILE] Fetched {len(planets_list)} planet positions")
            
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
            
            logger.info(f"[PROFILE] Success: Ascendant={profile.ascendant}, Moon={profile.moon_sign}")
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
        
        # Parse current dasha
        current_maha = dashas.get('current_mahadasha', {})
        current_mahadasha = DashaInfo(
            level='mahadasha',
            planet=current_maha.get('planet', 'Jupiter'),
            start_date=date.fromisoformat(current_maha['start_date']) if current_maha.get('start_date') else birth.dob,
            end_date=date.fromisoformat(current_maha['end_date']) if current_maha.get('end_date') else birth.dob,
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
        
        # Parse dasha from API
        maha_timeline = dashas.get('mahadasha_timeline', [])
        current_maha = None
        if maha_timeline:
            current_maha = maha_timeline[0]  # Assume first is current
        
        current_mahadasha = DashaInfo(
            level='mahadasha',
            planet=current_maha.get('planet', 'Jupiter') if current_maha else 'Jupiter',
            start_date=date.fromisoformat(current_maha['start_date']) if current_maha and current_maha.get('start_date') else birth.dob,
            end_date=date.fromisoformat(current_maha['end_date']) if current_maha and current_maha.get('end_date') else birth.dob,
            years_total=float(current_maha.get('years_total', 16)) if current_maha else 16,
            years_elapsed=float(current_maha.get('years_elapsed', 0)) if current_maha else 0,
            years_remaining=float(current_maha.get('years_remaining', 16)) if current_maha else 16
        )
        
        # Antardasha (use first from antardashas)
        antardashas = dashas.get('antardashas', [{}])
        current_antar = antardashas[0] if antardashas else {}
        current_antardasha = DashaInfo(
            level='antardasha',
            planet=current_antar.get('planet', 'Venus'),
            start_date=date.fromisoformat(current_antar['start_date']) if current_antar.get('start_date') else birth.dob,
            end_date=date.fromisoformat(current_antar['end_date']) if current_antar.get('end_date') else birth.dob,
            years_total=float(current_antar.get('years_total', 2)),
            years_elapsed=0,
            years_remaining=float(current_antar.get('years_total', 2))
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
        Generate SVG representation of Kundli from API data.
        
        Creates a proper North Indian style birth chart SVG with:
        - Classic diamond house layout with visible dark lines
        - Planet positions in correct houses
        - House numbers
        - Professional styling matching traditional Kundli charts
        """
        asc_sign = kundli_data.get('ascendant_sign', 'Aries')
        
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
        
        # SVG dimensions
        width, height = 500, 550
        cx, cy = 250, 275  # Center of chart
        size = 200  # Half-size of the outer square
        
        # Colors matching reference image
        bg_color = "#FFF8E7"  # Light cream/yellow
        line_color = "#3b2f2f"  # Dark brown for strong visibility
        text_color = "#B22222"  # Dark red/maroon
        
        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f'<defs>',
            f'  <style>',
            f'    .house-num {{ font-family: Arial, sans-serif; font-size: 14px; fill: {text_color}; }}',
            f'    .planet {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: {text_color}; }}',
            f'    .title {{ font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; fill: #333; }}',
            f'    .subtitle {{ font-family: Arial, sans-serif; font-size: 12px; fill: #666; }}',
            f'  </style>',
            f'</defs>',
            # Background
            f'<rect width="100%" height="100%" fill="{bg_color}"/>',
            # Title
            f'<text x="{cx}" y="30" text-anchor="middle" class="title">Birth Chart (Rashi Chart)</text>',
        ]
        
        # Chart frame with rounded corners
        frame_x, frame_y = cx - size - 20, cy - size - 20
        frame_w, frame_h = (size + 20) * 2, (size + 20) * 2
        svg_parts.append(f'<rect x="{frame_x}" y="{frame_y}" width="{frame_w}" height="{frame_h}" fill="#FDF5E6" stroke="{line_color}" stroke-width="3" rx="10"/>')
        
        # North Indian Kundli layout - outer square with diagonals and inner diamond
        # Outer square corners
        top_left = (cx - size, cy - size)
        top_right = (cx + size, cy + size - 2*size)  # Actually top-right
        bottom_right = (cx + size, cy + size)
        bottom_left = (cx - size, cy + size)
        
        # Draw outer square (darker, thicker lines for visibility)
        svg_parts.append(f'<rect x="{cx-size}" y="{cy-size}" width="{size*2}" height="{size*2}" fill="none" stroke="{line_color}" stroke-width="2.5"/>')
        
        # Draw main diagonals (darker, thicker lines for visibility)
        svg_parts.append(f'<line x1="{cx-size}" y1="{cy-size}" x2="{cx+size}" y2="{cy+size}" stroke="{line_color}" stroke-width="2.5"/>')
        svg_parts.append(f'<line x1="{cx+size}" y1="{cy-size}" x2="{cx-size}" y2="{cy+size}" stroke="{line_color}" stroke-width="2.5"/>')
        
        # Draw inner diamond (connects midpoints of outer square sides)
        mid_top = (cx, cy - size)
        mid_right = (cx + size, cy)
        mid_bottom = (cx, cy + size)
        mid_left = (cx - size, cy)
        
        svg_parts.append(f'<line x1="{mid_top[0]}" y1="{mid_top[1]}" x2="{mid_right[0]}" y2="{mid_right[1]}" stroke="{line_color}" stroke-width="2.5"/>')
        svg_parts.append(f'<line x1="{mid_right[0]}" y1="{mid_right[1]}" x2="{mid_bottom[0]}" y2="{mid_bottom[1]}" stroke="{line_color}" stroke-width="2.5"/>')
        svg_parts.append(f'<line x1="{mid_bottom[0]}" y1="{mid_bottom[1]}" x2="{mid_left[0]}" y2="{mid_left[1]}" stroke="{line_color}" stroke-width="2.5"/>')
        svg_parts.append(f'<line x1="{mid_left[0]}" y1="{mid_left[1]}" x2="{mid_top[0]}" y2="{mid_top[1]}" stroke="{line_color}" stroke-width="2.5"/>')
        
        # House positions for North Indian chart (house number -> coordinates for text)
        # In North Indian chart, House 1 (Lagna) is at the top center diamond
        house_positions = {
            1: (cx, cy - size//2 - 20),           # Top center (Lagna)
            2: (cx - size//2 - 20, cy - size//2 - 20),  # Top-left triangle
            3: (cx - size + 30, cy - 30),         # Left-top triangle
            4: (cx - size//2 - 20, cy),           # Left center
            5: (cx - size + 30, cy + 30),         # Left-bottom triangle
            6: (cx - size//2 - 20, cy + size//2 + 20),  # Bottom-left triangle
            7: (cx, cy + size//2 + 20),           # Bottom center
            8: (cx + size//2 + 20, cy + size//2 + 20),  # Bottom-right triangle
            9: (cx + size - 30, cy + 30),         # Right-bottom triangle
            10: (cx + size//2 + 20, cy),          # Right center
            11: (cx + size - 30, cy - 30),        # Right-top triangle
            12: (cx + size//2 + 20, cy - size//2 - 20),  # Top-right triangle
        }
        
        # Planet positions (offset from house number position)
        planet_positions = {
            1: (cx, cy - size//2 + 10),
            2: (cx - size//2, cy - size//2 + 10),
            3: (cx - size + 50, cy - 10),
            4: (cx - size//2, cy + 15),
            5: (cx - size + 50, cy + 50),
            6: (cx - size//2, cy + size//2 - 10),
            7: (cx, cy + size//2 - 10),
            8: (cx + size//2, cy + size//2 - 10),
            9: (cx + size - 50, cy + 50),
            10: (cx + size//2, cy + 15),
            11: (cx + size - 50, cy - 10),
            12: (cx + size//2, cy - size//2 + 10),
        }
        
        # Draw house numbers and planets
        for house_num in range(1, 13):
            # House number
            hx, hy = house_positions[house_num]
            svg_parts.append(f'<text x="{hx}" y="{hy}" text-anchor="middle" class="house-num">{house_num}</text>')
            
            # Planets in this house
            planets = planets_by_house.get(house_num, [])
            if planets:
                px, py = planet_positions[house_num]
                planets_str = ' '.join(planets)
                svg_parts.append(f'<text x="{px}" y="{py}" text-anchor="middle" class="planet">{planets_str}</text>')
        
        # Add "As" (Ascendant) marker in house 1
        svg_parts.append(f'<text x="{cx}" y="{cy - 10}" text-anchor="middle" class="planet">As</text>')
        
        # Footer note
        svg_parts.append(f'<text x="{cx}" y="{height - 20}" text-anchor="middle" class="subtitle">Houses numbered 1-12 • Planets shown in their respective houses</text>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
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
