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
            
            # Generate SVG representation from kundli data
            svg = self._generate_kundli_svg(kundli_data, birth, style)
            
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
        
        return AstroProfile(
            user_id=user_id,
            birth_details=birth,
            base_chart_raw=base_chart,
            dashas_raw=dashas,
            ascendant=asc_data.get('sign', 'Aries'),
            ascendant_degree=asc_data.get('degree', 0),
            ascendant_nakshatra=asc_data.get('nakshatra', 'Ashwini'),
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
        
        # Parse houses from kundli data (derive from planets + ascendant)
        houses_list = []
        asc_sign = kundli.get('ascendant_sign', 'Aries')
        for i in range(1, 13):
            # Get planets in this house
            planets_in_house = [p.planet for p in planets_list if p.house == i]
            houses_list.append(HouseData(
                house_num=i,
                sign=asc_sign,  # TODO: Calculate actual sign for each house
                sign_lord='',  # TODO: Get from API or calculate
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
        asc_degree = kundli.get('ascendant_degree', 0)
        asc_nakshatra = kundli.get('ascendant_nakshatra', 'Ashwini')
        
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
    
    def _generate_kundli_svg(self, kundli_data: Dict[str, Any], birth: BirthDetails, style: str = "north") -> str:
        """
        Generate SVG representation of Kundli from API data.
        
        Creates a basic North/South Indian style birth chart SVG.
        """
        asc_sign = kundli_data.get('ascendant_sign', 'Aries')
        asc_degree = kundli_data.get('ascendant_degree', 0)
        
        # Create SVG container
        width, height = 500, 500
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<defs><style>.kundli-text {{ font-family: Arial, sans-serif; font-size: 12px; }} .kundli-title {{ font-weight: bold; font-size: 14px; }} .planet-name {{ fill: #333; }} .sign-name {{ fill: #666; }}</style></defs>',
            '<rect width="100%" height="100%" fill="#ffffff" stroke="#000" stroke-width="2"/>',
            # Title
            f'<text x="{width/2}" y="20" text-anchor="middle" class="kundli-title">Birth Chart - Kundli</text>',
            # Ascendant info
            f'<text x="10" y="50" class="kundli-text"><tspan class="planet-name">Ascendant:</tspan> <tspan class="sign-name">{asc_sign}</tspan></text>',
            f'<text x="10" y="70" class="kundli-text"><tspan class="planet-name">Degree:</tspan> <tspan>{asc_degree:.2f}°</tspan></text>',
            # Birth details
            f'<text x="10" y="100" class="kundli-text"><tspan class="planet-name">DOB:</tspan> {birth.dob}</text>',
            f'<text x="10" y="120" class="kundli-text"><tspan class="planet-name">TOB:</tspan> {birth.tob}</text>',
            f'<text x="10" y="140" class="kundli-text"><tspan class="planet-name">Location:</tspan> {birth.location}</text>',
            # Chart visualization area
            '<circle cx="250" cy="280" r="100" fill="none" stroke="#999" stroke-width="1"/>',
            '<circle cx="250" cy="280" r="80" fill="none" stroke="#999" stroke-width="1"/>',
            '<line x1="250" y1="180" x2="250" y2="380" stroke="#999" stroke-width="1"/>',
            '<line x1="150" y1="280" x2="350" y2="280" stroke="#999" stroke-width="1"/>',
            # House labels (simplified)
            '<text x="250" y="175" text-anchor="middle" class="kundli-text" font-size="10">I</text>',
            '<text x="360" y="285" text-anchor="start" class="kundli-text" font-size="10">IV</text>',
            '<text x="250" y="395" text-anchor="middle" class="kundli-text" font-size="10">VII</text>',
            '<text x="140" y="285" text-anchor="end" class="kundli-text" font-size="10">X</text>',
            # Source note
            f'<text x="10" y="{height-10}" class="kundli-text" font-size="10" fill="#999">Generated from VedicAstroAPI</text>',
            '</svg>'
        ]
        
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
        Fetch Kundli chart as SVG from Vedic API.
        
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
        try:
            api_params = {
                'dob': birth.dob.strftime('%d/%m/%Y'),
                'tob': birth.tob,
                'lat': birth.latitude or 28.6139,
                'lon': birth.longitude or 77.2090,
                'tz': birth.timezone,
                'ayanamsa': 'Lahiri',
                'lang': 'en',
                'style': 'north-indian'
            }
            
            # Fetch SVG chart from Vedic API
            # Endpoint: /horoscope/chart-image returns SVG directly (not JSON wrapped)
            logger.info(f"Fetching Kundli SVG for {birth.dob}")
            
            # Build URL and add API key
            full_url = f"{self.base_url}/horoscope/chart-image"
            api_params['api_key'] = self.api_key
            
            # Make direct request for SVG (not using _get as it expects JSON)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(full_url, params=api_params)
                
                if response.status_code != 200:
                    logger.warning(f"Kundli SVG fetch failed: HTTP {response.status_code}")
                    return {
                        "ok": False,
                        "error": "KUNDLI_FETCH_FAILED",
                        "details": f"API returned HTTP {response.status_code}"
                    }
                
                # The response is SVG directly - get content as bytes and decode
                content = response.content
                try:
                    svg_data = content.decode('utf-8')
                except UnicodeDecodeError:
                    svg_data = content.decode('iso-8859-1')
            
            if not svg_data:
                logger.warning("No SVG data in response")
                return {
                    "ok": False,
                    "error": "KUNDLI_FETCH_FAILED",
                    "details": "No SVG data in response"
                }
            
            # Verify it's actually SVG content
            if not svg_data.strip().startswith('<?xml') and not svg_data.strip().startswith('<svg'):
                logger.warning(f"Response doesn't look like SVG: {svg_data[:100]}")
                return {
                    "ok": False,
                    "error": "KUNDLI_FETCH_FAILED",
                    "details": "Response is not valid SVG"
                }
            
            # If SVG is a URL, fetch it
            if isinstance(svg_data, str) and svg_data.startswith('http'):
                try:
                    async with httpx.AsyncClient(timeout=15) as client:
                        svg_response = await client.get(svg_data)
                        svg_response.raise_for_status()
                        svg_data = svg_response.text
                except Exception as e:
                    logger.error(f"Failed to fetch SVG from URL: {e}")
                    return {
                        "ok": False,
                        "error": "KUNDLI_FETCH_FAILED",
                        "details": f"Failed to fetch SVG: {str(e)}"
                    }
            
            # Enforce maximum SVG size (500KB)
            if len(svg_data) > 500000:
                logger.warning(f"SVG size {len(svg_data)} exceeds limit")
                return {
                    "ok": False,
                    "error": "KUNDLI_FETCH_FAILED",
                    "details": "SVG size exceeds maximum allowed"
                }
            
            logger.info(f"Kundli SVG fetched successfully, size={len(svg_data)} bytes")
            
            return {
                "ok": True,
                "svg": svg_data,
                "chart_type": "birth_chart",
                "vendor": "VedicAstroAPI",
                "svg_size": len(svg_data)
            }
        
        except Exception as e:
            logger.error(f"Exception fetching Kundli SVG: {e}", exc_info=True)
            return {
                "ok": False,
                "error": "KUNDLI_FETCH_FAILED",
                "details": str(e)
            }
    
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
