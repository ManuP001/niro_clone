"""
Astro Engine Integration
Stubbed implementation for astrological calculations.
Replace with real engine integration later.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import random

from .models import BirthDetails, AstroFeatures

logger = logging.getLogger(__name__)


class AstroEngine:
    """
    Astro Engine for computing chart data.
    
    This is a STUB implementation. Replace compute_astro_raw() with
    actual VedicAPI or Swiss Ephemeris calculations.
    """
    
    # Zodiac signs for stub data
    ZODIAC_SIGNS = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    
    # Nakshatras for stub data
    NAKSHATRAS = [
        'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
        'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
        'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
        'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
        'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
    ]
    
    # Planets for stub data
    PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    
    # Mahadasha lords
    DASHA_LORDS = ['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus']
    
    def __init__(self):
        logger.info("AstroEngine initialized (STUB implementation)")
    
    def compute_astro_raw(
        self,
        birth_details: BirthDetails,
        mode: str,
        focus: Optional[str],
        now: datetime
    ) -> Dict[str, Any]:
        """
        Compute raw astrological data from birth details.
        
        STUB IMPLEMENTATION - Returns fake data for development.
        Replace with actual VedicAPI/Swiss Ephemeris integration.
        
        Args:
            birth_details: User's birth details
            mode: Current conversation mode
            focus: Current focus area (if any)
            now: Current datetime for transit calculations
            
        Returns:
            Raw chart data dictionary
        """
        logger.info(f"Computing astro data for mode={mode}, focus={focus}")
        logger.warning("Using STUB implementation - replace with real engine")
        
        # Generate deterministic but varied data based on birth details
        seed = hash(f"{birth_details.dob}-{birth_details.tob}-{birth_details.location}")
        random.seed(seed)
        
        # Generate stub planetary positions
        planets = {}
        for i, planet in enumerate(self.PLANETS):
            sign_idx = (seed + i) % 12
            degree = random.randint(0, 29)
            nakshatra_idx = (sign_idx * 2 + (1 if degree > 13 else 0)) % 27
            
            planets[planet] = {
                'sign': self.ZODIAC_SIGNS[sign_idx],
                'degree': degree,
                'nakshatra': self.NAKSHATRAS[nakshatra_idx],
                'house': ((sign_idx - (seed % 12)) % 12) + 1,
                'retrograde': planet in ['Saturn', 'Jupiter', 'Mars'] and random.random() > 0.7
            }
        
        # Generate stub houses
        houses = {}
        asc_sign_idx = seed % 12
        for i in range(1, 13):
            house_sign_idx = (asc_sign_idx + i - 1) % 12
            houses[str(i)] = {
                'sign': self.ZODIAC_SIGNS[house_sign_idx],
                'lord': self._get_house_lord(self.ZODIAC_SIGNS[house_sign_idx])
            }
        
        # Generate stub dasha
        dasha_lord_idx = (seed + now.year) % 9
        antardasha_lord_idx = (seed + now.month) % 9
        
        raw_data = {
            'success': True,
            'birth_details': birth_details.dict(),
            'calculation_time': now.isoformat(),
            'planets': planets,
            'houses': houses,
            'ascendant': {
                'sign': self.ZODIAC_SIGNS[asc_sign_idx],
                'degree': random.randint(0, 29),
                'nakshatra': self.NAKSHATRAS[(asc_sign_idx * 2) % 27]
            },
            'moon': {
                'sign': planets['Moon']['sign'],
                'nakshatra': planets['Moon']['nakshatra']
            },
            'sun': {
                'sign': planets['Sun']['sign']
            },
            'mahadasha': {
                'lord': self.DASHA_LORDS[dasha_lord_idx],
                'start_date': '2020-01-01',
                'end_date': '2027-01-01',
                'years_remaining': random.randint(1, 6)
            },
            'antardasha': {
                'lord': self.DASHA_LORDS[antardasha_lord_idx],
                'start_date': '2024-06-01',
                'end_date': '2025-06-01',
                'months_remaining': random.randint(1, 12)
            },
            'transits': self._generate_stub_transits(now),
            'yogas': self._generate_stub_yogas(planets),
        }
        
        logger.debug(f"Generated stub astro data with ascendant {raw_data['ascendant']['sign']}")
        return raw_data
    
    def build_astro_features(
        self,
        raw: Dict[str, Any],
        mode: str,
        focus: Optional[str]
    ) -> Dict[str, Any]:
        """
        Map astro engine output to a stable schema for NIRO LLM.
        
        Args:
            raw: Raw data from compute_astro_raw()
            mode: Current conversation mode
            focus: Current focus area
            
        Returns:
            Normalized astro features dictionary
        """
        logger.info(f"Building astro features for mode={mode}, focus={focus}")
        
        features = AstroFeatures(
            birth_details=raw.get('birth_details'),
            ascendant=raw.get('ascendant', {}).get('sign'),
            moon_sign=raw.get('moon', {}).get('sign'),
            sun_sign=raw.get('sun', {}).get('sign'),
            mahadasha=raw.get('mahadasha'),
            antardasha=raw.get('antardasha'),
            transits=raw.get('transits', []),
            planetary_strengths=self._extract_planetary_strengths(raw),
            yogas=raw.get('yogas', []),
            focus_factors=self._extract_focus_factors(raw, focus),
            past_events=self._generate_past_events(raw, mode),
            timing_windows=self._generate_timing_windows(raw, focus),
            key_rules=self._generate_key_rules(raw, mode, focus)
        )
        
        return features.dict()
    
    def _get_house_lord(self, sign: str) -> str:
        """Get the ruling planet of a sign"""
        rulers = {
            'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
            'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
            'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
        }
        return rulers.get(sign, 'Unknown')
    
    def _generate_stub_transits(self, now: datetime) -> list:
        """Generate stub transit data"""
        transits = []
        for planet in ['Saturn', 'Jupiter', 'Rahu']:
            sign_idx = (now.month + hash(planet)) % 12
            transits.append({
                'planet': planet,
                'sign': self.ZODIAC_SIGNS[sign_idx],
                'aspect_houses': [random.randint(1, 12) for _ in range(3)],
                'nature': random.choice(['favorable', 'challenging', 'neutral'])
            })
        return transits
    
    def _generate_stub_yogas(self, planets: dict) -> list:
        """Generate stub yoga combinations"""
        yogas = [
            {'name': 'Gajakesari Yoga', 'strength': 'medium', 'area': 'wisdom and fortune'},
            {'name': 'Budhaditya Yoga', 'strength': 'strong', 'area': 'intellect and communication'},
        ]
        return yogas
    
    def _extract_planetary_strengths(self, raw: dict) -> list:
        """Extract planetary strength indicators"""
        strengths = []
        for planet, data in raw.get('planets', {}).items():
            strengths.append({
                'planet': planet,
                'sign': data.get('sign'),
                'house': data.get('house'),
                'strength': random.choice(['strong', 'medium', 'weak']),
                'dignity': random.choice(['exalted', 'own sign', 'friendly', 'neutral', 'enemy', 'debilitated'])
            })
        return strengths
    
    def _extract_focus_factors(self, raw: dict, focus: Optional[str]) -> list:
        """Extract factors relevant to the focus area"""
        focus_houses = {
            'career': [10, 2, 6, 11],
            'relationship': [7, 5, 8, 4],
            'health': [1, 6, 8, 12],
            'finance': [2, 11, 5, 9],
            'spirituality': [9, 12, 5, 4]
        }
        
        if not focus:
            return []
        
        houses = focus_houses.get(focus, [])
        factors = []
        
        for house in houses:
            house_data = raw.get('houses', {}).get(str(house), {})
            factors.append({
                'house': house,
                'sign': house_data.get('sign'),
                'lord': house_data.get('lord'),
                'significance': f'House {house} relates to {focus}'
            })
        
        return factors
    
    def _generate_past_events(self, raw: dict, mode: str) -> list:
        """Generate past event markers for PAST_THEMES mode"""
        if mode != 'PAST_THEMES':
            return []
        
        events = [
            {'period': '2023', 'theme': 'career transition or growth opportunity', 'planetary_trigger': 'Saturn transit'},
            {'period': '2022-2023', 'theme': 'relationship changes or deepening', 'planetary_trigger': 'Jupiter aspect'},
            {'period': '2024', 'theme': 'financial gains or restructuring', 'planetary_trigger': 'Mahadasha influence'}
        ]
        return events
    
    def _generate_timing_windows(self, raw: dict, focus: Optional[str]) -> list:
        """Generate favorable timing windows"""
        windows = [
            {'period': 'Next 3 months', 'nature': 'favorable', 'activity': 'new initiatives'},
            {'period': 'Q2 2025', 'nature': 'neutral', 'activity': 'consolidation'},
            {'period': 'H2 2025', 'nature': 'very favorable', 'activity': 'major decisions'}
        ]
        return windows
    
    def _generate_key_rules(self, raw: dict, mode: str, focus: Optional[str]) -> list:
        """Generate key astrological rules to highlight"""
        rules = [
            f"Ascendant lord in {raw.get('planets', {}).get('Sun', {}).get('house', 1)}th house indicates {random.choice(['leadership', 'visibility', 'self-expression'])}",
            f"Moon in {raw.get('moon', {}).get('nakshatra', 'Rohini')} suggests {random.choice(['emotional depth', 'intuition', 'nurturing nature'])}",
            f"Current Mahadasha of {raw.get('mahadasha', {}).get('lord', 'Jupiter')} emphasizes {random.choice(['growth', 'transformation', 'discipline'])}"
        ]
        return rules
