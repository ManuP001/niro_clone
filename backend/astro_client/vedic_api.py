"""
Vedic API Client

HTTP client wrapper for Vedic astrology API.
Designed to be vendor-agnostic - adapt endpoint paths and field mappings
when integrating with real API (e.g., vedicastroAPI, AstroSage, etc.)

TODO: Replace stub implementations with real API calls.
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
import random
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

# Configuration
VEDIC_API_BASE_URL = os.environ.get('VEDIC_API_BASE_URL', 'https://api.vedicastro.com/v1')
VEDIC_API_KEY = os.environ.get('VEDIC_API_KEY', '')
VEDIC_API_SECRET = os.environ.get('VEDIC_API_SECRET', '')

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
    Client for Vedic Astrology API.
    
    This is a STUB implementation that generates realistic fake data.
    Replace with real API integration when ready.
    """
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or VEDIC_API_BASE_URL
        self.api_key = api_key or VEDIC_API_KEY
        self._client: Optional[httpx.AsyncClient] = None
        logger.info(f"VedicAPIClient initialized (STUB mode - using generated data)")
    
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
        """
        try:
            # Don't use base_url in client, construct full URL manually
            # because VedicAstroAPI expects full path
            full_url = f"{self.base_url}{path}"
            
            # Add API key to params
            params['api_key'] = self.api_key
            params['lang'] = params.get('lang', 'en')
            
            logger.debug(f"Calling API: {full_url} with params: {list(params.keys())}")
            
            # Create a simple client without base_url
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(full_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Check if API returned an error
                if data.get('message') == 'Not Found':
                    logger.error(f"API endpoint not found: {full_url}")
                    return None
                
                if data.get('status') != 200:
                    logger.error(f"API error for {full_url}: {data}")
                    return None
                    
                logger.debug(f"API call successful for {path}")
                return data.get('response', {})
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling {path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling {path}: {e}")
            return None
    
    def _generate_deterministic_seed(self, birth: BirthDetails) -> int:
        """Generate deterministic seed from birth details for consistent fake data"""
        seed_str = f"{birth.dob}-{birth.tob}-{birth.location}"
        return int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    
    async def fetch_full_profile(self, birth: BirthDetails, user_id: str = None) -> AstroProfile:
        """
        Fetch complete astrological profile from Vedic API.
        
        Uses VedicAstroAPI v3-json endpoints:
        - /extended-horoscope/extended-kundli-details for detailed birth chart info
        - /extended-horoscope/find-ascendant for ascendant
        - /extended-horoscope/find-sun-sign for sun sign  
        - /extended-horoscope/find-moon-sign for moon sign
        - /dashas/maha-dasha for dasha timeline
        
        Note: Detailed planetary positions, yogas, and houses are still stubbed
        as those specific endpoints haven't been found yet.
        """
        logger.info(f"Fetching full profile for {birth.location}, {birth.dob}")
        
        # Prepare API params
        api_params = {
            'dob': birth.dob.strftime("%d/%m/%Y"),
            'tob': birth.tob,
            'lat': birth.latitude or 28.6139,  # Default to Delhi if not provided
            'lon': birth.longitude or 77.2090,
            'tz': birth.timezone
        }
        
        # Fetch real data from API
        kundli_details = await self._get('/extended-horoscope/extended-kundli-details', api_params)
        ascendant_data = await self._get('/extended-horoscope/find-ascendant', api_params)
        sun_sign_data = await self._get('/extended-horoscope/find-sun-sign', api_params)
        moon_sign_data = await self._get('/extended-horoscope/find-moon-sign', api_params)
        dashas_data = await self._get('/dashas/maha-dasha', api_params)
        
        # Check if API calls succeeded
        use_real_data = all([kundli_details, ascendant_data, sun_sign_data, moon_sign_data, dashas_data])
        
        seed = self._generate_deterministic_seed(birth)
        random.seed(seed)
        
        if use_real_data:
            logger.info("Using REAL data from VedicAstroAPI")
            # Build chart data combining real and stub data
            base_chart_raw = self._build_chart_from_real_data(
                birth, seed, kundli_details, ascendant_data, sun_sign_data, moon_sign_data
            )
            dashas_raw = self._build_dashas_from_real_data(dashas_data, birth)
        else:
            logger.warning("API calls failed - falling back to stub data")
            base_chart_raw = self._generate_stub_chart(birth, seed)
            dashas_raw = self._generate_stub_dashas(birth, seed)
        
        # Parse into our models
        profile = self._parse_profile(
            user_id=user_id or str(seed),
            birth=birth,
            base_chart=base_chart_raw,
            dashas=dashas_raw
        )
        
        logger.info(f"Profile generated: Ascendant={profile.ascendant}, Moon={profile.moon_sign}")
        return profile
    
    async def fetch_transits(
        self,
        birth: BirthDetails,
        user_id: str,
        from_date: date,
        to_date: date
    ) -> AstroTransits:
        """
        Fetch transit data for a time window.
        
        TODO: Replace stub with real API:
        - Call /transits/range with date window
        - Parse transit events
        """
        logger.info(f"Fetching transits from {from_date} to {to_date}")
        
        # Try real API (TODO: uncomment when ready)
        # transits_raw = await self._post('/transits/range', {
        #     **birth.to_api_format(),
        #     'from_date': from_date.isoformat(),
        #     'to_date': to_date.isoformat()
        # })
        
        # Generate stub data
        seed = self._generate_deterministic_seed(birth)
        random.seed(seed + from_date.toordinal())
        
        transits_raw = self._generate_stub_transits(birth, from_date, to_date, seed)
        
        transits = self._parse_transits(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            raw=transits_raw
        )
        
        logger.info(f"Generated {len(transits.events)} transit events")
        return transits
    
    
    def _build_chart_from_real_data(
        self,
        birth: BirthDetails,
        seed: int,
        kundli: Dict,
        ascendant: Dict,
        sun_sign: Dict,
        moon_sign: Dict
    ) -> Dict[str, Any]:
        """
        Build chart data combining real API data with stub planetary positions.
        
        Real data: ascendant, sun sign, moon sign, nakshatra
        Stubbed: detailed planetary positions, houses, yogas (endpoints not found yet)
        """
        # Get real ascendant info
        asc_sign = kundli.get('ascendant_sign', ascendant.get('ascendant', 'Aries'))
        asc_nakshatra = kundli.get('ascendant_nakshatra', 'Ashwini')
        
        # Get real moon info
        moon_rasi = kundli.get('rasi', moon_sign.get('moon_sign', 'Cancer'))
        moon_nakshatra = kundli.get('nakshatra', 'Pushya')
        moon_pada = kundli.get('nakshatra_pada', 1)
        
        # Get real sun sign
        sun_rasi = sun_sign.get('sun_sign', 'Leo')
        
        # Generate stub planetary positions (will be replaced when we find the right endpoint)
        random.seed(seed)
        asc_index = ZODIAC_SIGNS.index(asc_sign) if asc_sign in ZODIAC_SIGNS else 0
        
        # Generate planets with some real data
        planets = {}
        for i, planet in enumerate(PLANETS):
            sign_idx = (seed + i * 3) % 12
            degree = random.uniform(0, 29.99)
            nakshatra_idx = int((sign_idx * 30 + degree) / 13.33) % 27
            house = ((sign_idx - asc_index) % 12) + 1
            
            # Override Moon position with real data
            if planet == 'Moon':
                sign_idx = ZODIAC_SIGNS.index(moon_rasi) if moon_rasi in ZODIAC_SIGNS else sign_idx
                nakshatra_idx = NAKSHATRAS.index(moon_nakshatra) if moon_nakshatra in NAKSHATRAS else nakshatra_idx
                house = ((sign_idx - asc_index) % 12) + 1
                degree = (moon_pada - 1) * 3.33 + random.uniform(0, 3.33)  # Approximate pada position
            
            # Override Sun position with real data
            if planet == 'Sun':
                sign_idx = ZODIAC_SIGNS.index(sun_rasi) if sun_rasi in ZODIAC_SIGNS else sign_idx
                house = ((sign_idx - asc_index) % 12) + 1
            
            sign = ZODIAC_SIGNS[sign_idx]
            is_exalted = EXALTATION.get(planet) == sign
            is_debilitated = DEBILITATION.get(planet) == sign
            is_own_sign = SIGN_LORDS.get(sign) == planet
            
            dignity = "neutral"
            if is_exalted:
                dignity = "exalted"
            elif is_debilitated:
                dignity = "debilitated"
            elif is_own_sign:
                dignity = "own"
            
            is_retro = planet in ['Mars', 'Mercury', 'Jupiter', 'Saturn', 'Venus'] and random.random() > 0.7
            
            planets[planet] = {
                'sign': sign,
                'sign_num': sign_idx + 1,
                'degree': round(degree, 2),
                'house': house,
                'nakshatra': NAKSHATRAS[nakshatra_idx],
                'nakshatra_lord': NAKSHATRA_LORDS[nakshatra_idx],
                'nakshatra_pada': (int(degree) % 4) + 1,
                'retrograde': is_retro,
                'dignity': dignity,
                'combust': planet != 'Sun' and abs((seed + i) % 30 - 15) < 8 and random.random() > 0.8
            }
        
        # Generate houses
        houses = {}
        for i in range(1, 13):
            house_sign_idx = (asc_index + i - 1) % 12
            sign = ZODIAC_SIGNS[house_sign_idx]
            planets_in_house = [p for p, data in planets.items() if data['house'] == i]
            
            houses[str(i)] = {
                'sign': sign,
                'lord': SIGN_LORDS[sign],
                'planets': planets_in_house
            }
        
        # Generate yogas
        yogas = self._generate_stub_yogas(planets, houses, seed)
        
        return {
            'ascendant': {
                'sign': asc_sign,
                'degree': round(random.uniform(0, 30), 2),
                'nakshatra': asc_nakshatra
            },
            'planets': planets,
            'houses': houses,
            'yogas': yogas,
            'real_data_used': {
                'ascendant': True,
                'sun_sign': True,
                'moon_sign': True,
                'nakshatra': True,
                'detailed_positions': False,  # Still using approximations
                'yogas': False  # Still using stub logic
            }
        }
    
    def _build_dashas_from_real_data(self, dashas_api: Dict, birth: BirthDetails) -> Dict[str, Any]:
        """
        Build dasha data from real API response.
        """
        mahadasha_planets = dashas_api.get('mahadasha', [])
        mahadasha_dates = dashas_api.get('mahadasha_order', [])
        dasha_start = dashas_api.get('dasha_start_date', '')
        
        # Build dasha timeline
        dashas = []
        now = datetime.utcnow()
        
        DASHA_YEARS = {
            'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
            'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
        }
        
        for i, (planet, end_date_str) in enumerate(zip(mahadasha_planets, mahadasha_dates)):
            try:
                # Parse end date (format: "Fri Jun 28 1991")
                from datetime import datetime as dt
                end_date = dt.strptime(end_date_str.strip(), "%a %b %d %Y")
                
                # Calculate start date from previous end date
                if i == 0:
                    # First dasha - use birth date
                    start_date = datetime(birth.dob.year, birth.dob.month, birth.dob.day)
                else:
                    prev_end_str = mahadasha_dates[i-1].strip()
                    start_date = dt.strptime(prev_end_str, "%a %b %d %Y")
                
                years = DASHA_YEARS.get(planet, 10)
                
                # Calculate time elapsed/remaining
                if start_date.date() <= now.date() <= end_date.date():
                    elapsed = (now - start_date).days / 365.25
                    remaining = (end_date - now).days / 365.25
                    is_current = True
                elif now.date() > end_date.date():
                    elapsed = years
                    remaining = 0
                    is_current = False
                else:
                    elapsed = 0
                    remaining = years
                    is_current = False
                
                dashas.append({
                    'planet': planet,
                    'start_date': start_date.date().isoformat(),
                    'end_date': end_date.date().isoformat(),
                    'years_total': years,
                    'years_elapsed': round(elapsed, 2),
                    'years_remaining': round(remaining, 2),
                    'is_current': is_current
                })
            except Exception as e:
                logger.warning(f"Error parsing dasha for {planet}: {e}")
                continue
        
        # Find current mahadasha
        current_maha = next((d for d in dashas if d['is_current']), dashas[0] if dashas else None)
        
        # Generate antardasha within current mahadasha
        if current_maha:
            antardashas = self._generate_antardashas(current_maha, self._generate_deterministic_seed(birth))
        else:
            antardashas = []
        
        return {
            'mahadasha_timeline': dashas,
            'current_mahadasha': current_maha,
            'antardashas': antardashas,
            'real_data_used': True
        }
    def _generate_stub_chart(self, birth: BirthDetails, seed: int) -> Dict[str, Any]:
        """Generate realistic stub chart data"""
        random.seed(seed)
        
        # Determine ascendant based on birth time
        hour = int(birth.tob.split(':')[0])
        asc_index = (seed + hour) % 12
        ascendant = ZODIAC_SIGNS[asc_index]
        
        # Generate planet positions
        planets = {}
        for i, planet in enumerate(PLANETS):
            sign_idx = (seed + i * 3) % 12
            degree = random.uniform(0, 29.99)
            nakshatra_idx = int((sign_idx * 30 + degree) / 13.33) % 27
            house = ((sign_idx - asc_index) % 12) + 1
            
            # Check dignity
            sign = ZODIAC_SIGNS[sign_idx]
            is_exalted = EXALTATION.get(planet) == sign
            is_debilitated = DEBILITATION.get(planet) == sign
            is_own_sign = SIGN_LORDS.get(sign) == planet
            
            dignity = "neutral"
            if is_exalted:
                dignity = "exalted"
            elif is_debilitated:
                dignity = "debilitated"
            elif is_own_sign:
                dignity = "own"
            
            # Retrograde (only for Mars, Mercury, Jupiter, Saturn, Venus)
            is_retro = planet in ['Mars', 'Mercury', 'Jupiter', 'Saturn', 'Venus'] and random.random() > 0.7
            
            planets[planet] = {
                'sign': sign,
                'sign_num': sign_idx + 1,
                'degree': round(degree, 2),
                'house': house,
                'nakshatra': NAKSHATRAS[nakshatra_idx],
                'nakshatra_lord': NAKSHATRA_LORDS[nakshatra_idx],
                'nakshatra_pada': (int(degree) % 4) + 1,
                'retrograde': is_retro,
                'dignity': dignity,
                'combust': planet != 'Sun' and abs((seed + i) % 30 - 15) < 8 and random.random() > 0.8
            }
        
        # Generate houses
        houses = {}
        for i in range(1, 13):
            house_sign_idx = (asc_index + i - 1) % 12
            sign = ZODIAC_SIGNS[house_sign_idx]
            planets_in_house = [p for p, data in planets.items() if data['house'] == i]
            
            houses[str(i)] = {
                'sign': sign,
                'lord': SIGN_LORDS[sign],
                'planets': planets_in_house
            }
        
        # Generate yogas
        yogas = self._generate_stub_yogas(planets, houses, seed)
        
        return {
            'ascendant': {
                'sign': ascendant,
                'degree': round(random.uniform(0, 30), 2),
                'nakshatra': NAKSHATRAS[(asc_index * 2) % 27]
            },
            'planets': planets,
            'houses': houses,
            'yogas': yogas
        }
    
    def _generate_stub_dashas(self, birth: BirthDetails, seed: int) -> Dict[str, Any]:
        """Generate stub Vimshottari dasha data"""
        random.seed(seed)
        
        # Dasha periods in years
        DASHA_YEARS = {
            'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
            'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
        }
        DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
        
        # Determine starting dasha based on Moon's nakshatra
        start_idx = seed % 9
        
        # Build dasha timeline
        dashas = []
        current_date = datetime(birth.dob.year, birth.dob.month, birth.dob.day)
        now = datetime.utcnow()
        
        for cycle in range(3):  # 3 cycles to ensure we cover enough time
            for i in range(9):
                dasha_idx = (start_idx + i) % 9
                planet = DASHA_ORDER[dasha_idx]
                years = DASHA_YEARS[planet]
                
                end_date = current_date + timedelta(days=int(years * 365.25))
                
                # Calculate time elapsed/remaining
                if current_date <= now <= end_date:
                    elapsed = (now - current_date).days / 365.25
                    remaining = (end_date - now).days / 365.25
                    is_current = True
                elif now > end_date:
                    elapsed = years
                    remaining = 0
                    is_current = False
                else:
                    elapsed = 0
                    remaining = years
                    is_current = False
                
                dashas.append({
                    'planet': planet,
                    'start_date': current_date.date().isoformat(),
                    'end_date': end_date.date().isoformat(),
                    'years_total': years,
                    'years_elapsed': round(elapsed, 2),
                    'years_remaining': round(remaining, 2),
                    'is_current': is_current
                })
                
                current_date = end_date
        
        # Find current mahadasha
        current_maha = next((d for d in dashas if d['is_current']), dashas[0])
        
        # Generate antardasha within current mahadasha
        antardashas = self._generate_antardashas(current_maha, seed)
        
        return {
            'mahadasha_timeline': dashas,
            'current_mahadasha': current_maha,
            'antardashas': antardashas
        }
    
    def _generate_antardashas(self, mahadasha: Dict, seed: int) -> List[Dict]:
        """Generate antardasha periods within a mahadasha"""
        DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
        DASHA_YEARS = {
            'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
            'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
        }
        
        total_years = 120  # Total Vimshottari cycle
        maha_planet = mahadasha['planet']
        maha_years = mahadasha['years_total']
        start_idx = DASHA_ORDER.index(maha_planet)
        
        antardashas = []
        current = datetime.fromisoformat(mahadasha['start_date'])
        now = datetime.utcnow()
        
        for i in range(9):
            antar_idx = (start_idx + i) % 9
            antar_planet = DASHA_ORDER[antar_idx]
            antar_years = (DASHA_YEARS[maha_planet] * DASHA_YEARS[antar_planet]) / total_years
            
            end = current + timedelta(days=int(antar_years * 365.25))
            is_current = current.date() <= now.date() <= end.date()
            
            antardashas.append({
                'planet': antar_planet,
                'start_date': current.date().isoformat(),
                'end_date': end.date().isoformat(),
                'years_total': round(antar_years, 2),
                'is_current': is_current
            })
            
            current = end
        
        return antardashas
    
    def _generate_stub_yogas(self, planets: Dict, houses: Dict, seed: int) -> List[Dict]:
        """Generate realistic yoga combinations"""
        yogas = []
        
        # Check for Gajakesari Yoga (Jupiter in kendra from Moon)
        moon_house = planets['Moon']['house']
        jupiter_house = planets['Jupiter']['house']
        kendra_from_moon = [(moon_house + i - 1) % 12 + 1 for i in [1, 4, 7, 10]]
        if jupiter_house in kendra_from_moon:
            yogas.append({
                'name': 'Gajakesari Yoga',
                'category': 'raja',
                'planets_involved': ['Moon', 'Jupiter'],
                'houses_involved': [moon_house, jupiter_house],
                'strength': 'strong' if planets['Jupiter']['dignity'] in ['exalted', 'own'] else 'medium',
                'effects': 'Wisdom, fame, and prosperity'
            })
        
        # Check for Budhaditya Yoga (Sun-Mercury conjunction)
        if planets['Sun']['house'] == planets['Mercury']['house']:
            yogas.append({
                'name': 'Budhaditya Yoga',
                'category': 'raja',
                'planets_involved': ['Sun', 'Mercury'],
                'houses_involved': [planets['Sun']['house']],
                'strength': 'medium',
                'effects': 'Intelligence and communication skills'
            })
        
        # Check for Hamsa Yoga (Jupiter in kendra in own/exalted sign)
        if jupiter_house in [1, 4, 7, 10] and planets['Jupiter']['dignity'] in ['exalted', 'own']:
            yogas.append({
                'name': 'Hamsa Yoga',
                'category': 'pancha_mahapurusha',
                'planets_involved': ['Jupiter'],
                'houses_involved': [jupiter_house],
                'strength': 'strong',
                'effects': 'Righteous nature and spiritual wisdom'
            })
        
        # Add some common yogas based on seed for variety
        random.seed(seed)
        possible_yogas = [
            {'name': 'Chandra-Mangala Yoga', 'category': 'dhana', 'effects': 'Wealth through own efforts'},
            {'name': 'Shukra-Chandra Yoga', 'category': 'dhana', 'effects': 'Material comforts and beauty'},
            {'name': 'Neecha Bhanga Raja Yoga', 'category': 'raja', 'effects': 'Success after initial struggles'},
            {'name': 'Viparita Raja Yoga', 'category': 'raja', 'effects': 'Gains through adversity'},
        ]
        
        for yoga in possible_yogas:
            if random.random() > 0.6:
                yogas.append({
                    **yoga,
                    'planets_involved': random.sample(PLANETS[:7], 2),
                    'houses_involved': random.sample(range(1, 13), 2),
                    'strength': random.choice(['strong', 'medium', 'weak'])
                })
        
        return yogas
    
    def _generate_stub_transits(self, birth: BirthDetails, from_date: date, to_date: date, seed: int) -> Dict:
        """Generate stub transit data"""
        events = []
        current = from_date
        
        # Major transiting planets and their typical transit durations
        transit_speeds = {
            'Saturn': 912,  # ~2.5 years per sign (days)
            'Jupiter': 365,  # ~1 year per sign
            'Rahu': 548,  # ~18 months per sign
            'Mars': 45,  # ~45 days per sign
        }
        
        random.seed(seed + from_date.toordinal())
        
        for planet, days_per_sign in transit_speeds.items():
            # Generate ingress events
            transit_date = from_date
            sign_idx = (seed + hash(planet)) % 12
            
            while transit_date < to_date:
                # Sign change event
                if transit_date > from_date:
                    from_sign = ZODIAC_SIGNS[(sign_idx - 1) % 12]
                    to_sign = ZODIAC_SIGNS[sign_idx]
                    
                    events.append({
                        'event_type': 'ingress',
                        'planet': planet,
                        'from_sign': from_sign,
                        'to_sign': to_sign,
                        'affected_houses': [(sign_idx + i) % 12 + 1 for i in [0, 3, 6, 9]],  # Sign + aspects
                        'start_date': transit_date.isoformat(),
                        'strength': 'strong' if planet in ['Saturn', 'Jupiter'] else 'medium',
                        'nature': 'challenging' if planet == 'Saturn' else 'beneficial' if planet == 'Jupiter' else 'mixed'
                    })
                
                # Move to next sign
                transit_date += timedelta(days=days_per_sign + random.randint(-30, 30))
                sign_idx = (sign_idx + 1) % 12
        
        # Add retrograde events
        for planet in ['Saturn', 'Jupiter', 'Mars', 'Mercury']:
            retro_date = from_date + timedelta(days=random.randint(30, 180))
            if retro_date < to_date:
                events.append({
                    'event_type': 'retrograde_start',
                    'planet': planet,
                    'start_date': retro_date.isoformat(),
                    'end_date': (retro_date + timedelta(days=random.randint(60, 140))).isoformat(),
                    'strength': 'strong',
                    'nature': 'introspective'
                })
        
        return {
            'events': events,
            'current_positions': {p: {'sign': ZODIAC_SIGNS[(seed + i) % 12]} for i, p in enumerate(PLANETS)}
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
    
    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton instance
vedic_api_client = VedicAPIClient()
