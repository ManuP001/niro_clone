"""
Normalized Chart Data Contract

This module defines the exact data structure required by renderers.
Renderer must receive a single normalized object (post-API parsing).
Renderer must NOT interpret raw API data.

Key Concepts:
- North Indian: Houses are fixed positions, signs move based on ascendant
- South Indian: Signs are fixed positions, houses move based on ascendant
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Literal
from enum import Enum


# ============ CONSTANTS ============

# Canonical planet ordering for display
PLANET_ORDER = ['Su', 'Mo', 'Ma', 'Me', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke']

# Planet full name to abbreviation mapping
PLANET_ABBR = {
    'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me',
    'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa', 'Rahu': 'Ra', 'Ketu': 'Ke',
    # Also handle already abbreviated
    'Su': 'Su', 'Mo': 'Mo', 'Ma': 'Ma', 'Me': 'Me',
    'Ju': 'Ju', 'Ve': 'Ve', 'Sa': 'Sa', 'Ra': 'Ra', 'Ke': 'Ke'
}

# Sign names and numbers
SIGN_NAMES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

SIGN_ABBR = {
    'Aries': 'Ar', 'Taurus': 'Ta', 'Gemini': 'Ge', 'Cancer': 'Cn',
    'Leo': 'Le', 'Virgo': 'Vi', 'Libra': 'Li', 'Scorpio': 'Sc',
    'Sagittarius': 'Sg', 'Capricorn': 'Cp', 'Aquarius': 'Aq', 'Pisces': 'Pi'
}

# Sign number (1-12) to name
def sign_num_to_name(num: int) -> str:
    """Convert sign number (1-12) to sign name."""
    if 1 <= num <= 12:
        return SIGN_NAMES[num - 1]
    return 'Unknown'

def sign_name_to_num(name: str) -> int:
    """Convert sign name to number (1-12)."""
    try:
        return SIGN_NAMES.index(name) + 1
    except ValueError:
        return 0


# ============ ENUMS ============

class ChartStyle(str, Enum):
    """Chart rendering style."""
    NORTH = 'north'
    SOUTH = 'south'


class ChartType(str, Enum):
    """Chart division type."""
    D1 = 'D1'  # Rashi (main natal chart)
    D9 = 'D9'  # Navamsa
    D10 = 'D10'  # Dasamsa
    # Add more as needed


# ============ DATA MODELS ============

class ChartMetadata(BaseModel):
    """Chart metadata - describes the chart type and settings."""
    ayanamsa: str = Field(default='Lahiri', description='Ayanamsa used (e.g., Lahiri)')
    house_system: str = Field(default='Whole Sign', description='House system (recommend Whole Sign)')
    zodiac_type: str = Field(default='sidereal', description='Zodiac type (sidereal for Vedic)')
    chart_type: ChartType = Field(default=ChartType.D1, description='Chart division type')


class AscendantData(BaseModel):
    """Ascendant (Lagna) information."""
    sign: int = Field(..., ge=1, le=12, description='Sign number (1=Aries, 12=Pisces)')
    degree: float = Field(default=0.0, ge=0, lt=30, description='Degree within sign (0-30)')
    
    @property
    def sign_name(self) -> str:
        return sign_num_to_name(self.sign)


class HouseInfo(BaseModel):
    """House (Bhava) information."""
    house_number: int = Field(..., ge=1, le=12, description='House number (1-12)')
    sign: int = Field(..., ge=1, le=12, description='Sign number in this house (1-12)')
    
    @property
    def sign_name(self) -> str:
        return sign_num_to_name(self.sign)


class PlanetInfo(BaseModel):
    """Planet position information."""
    id: str = Field(..., description='Planet abbreviation (Su, Mo, Ma, Me, Ju, Ve, Sa, Ra, Ke)')
    sign: int = Field(..., ge=1, le=12, description='Sign number (1-12)')
    house: int = Field(..., ge=1, le=12, description='House number (1-12)')
    degree: float = Field(default=0.0, ge=0, lt=30, description='Degree within sign')
    retro: bool = Field(default=False, description='Is retrograde')
    
    @property
    def sign_name(self) -> str:
        return sign_num_to_name(self.sign)
    
    @property
    def display_label(self) -> str:
        """Get display label with retro marker if applicable."""
        if self.retro:
            return f"{self.id}(R)"
        return self.id


class NormalizedChart(BaseModel):
    """
    Normalized chart data contract.
    
    This is the ONLY data structure accepted by renderers.
    Renderers must NOT interpret raw API data directly.
    
    Invariants that must hold:
    1. Each planet must appear exactly once
    2. ascendant.sign must match houses[0].sign (for Whole Sign house system)
    3. planet.house must be consistent with the house/sign mapping
    """
    metadata: ChartMetadata = Field(default_factory=ChartMetadata)
    ascendant: AscendantData
    houses: List[HouseInfo] = Field(..., min_length=12, max_length=12)
    planets: List[PlanetInfo] = Field(..., min_length=1)
    
    # Optional display labels
    sign_labels: Optional[Dict[int, str]] = Field(
        default=None, 
        description='Optional map of sign numbers to localized labels'
    )
    
    @field_validator('houses')
    @classmethod
    def validate_houses(cls, v):
        """Ensure exactly 12 houses with correct numbers."""
        if len(v) != 12:
            raise ValueError('Must have exactly 12 houses')
        house_nums = {h.house_number for h in v}
        if house_nums != set(range(1, 13)):
            raise ValueError('Houses must be numbered 1-12')
        return sorted(v, key=lambda h: h.house_number)
    
    @field_validator('planets')
    @classmethod
    def validate_planets(cls, v):
        """Ensure no duplicate planets and proper ordering."""
        planet_ids = [p.id for p in v]
        if len(planet_ids) != len(set(planet_ids)):
            raise ValueError('Each planet must appear exactly once')
        # Sort by canonical order
        order_map = {p: i for i, p in enumerate(PLANET_ORDER)}
        return sorted(v, key=lambda p: order_map.get(p.id, 99))
    
    def validate_invariants(self) -> List[str]:
        """
        Validate chart invariants. Returns list of errors (empty if valid).
        
        Checks:
        1. Ascendant sign matches House 1 sign
        2. Each planet's house is consistent with sign placement
        """
        errors = []
        
        # Check 1: Ascendant sign = House 1 sign
        house_1 = next((h for h in self.houses if h.house_number == 1), None)
        if house_1 and house_1.sign != self.ascendant.sign:
            errors.append(
                f'Invariant violation: Ascendant sign ({self.ascendant.sign}) '
                f'does not match House 1 sign ({house_1.sign})'
            )
        
        # Check 2: Planet house consistency
        for planet in self.planets:
            expected_house = self._get_house_for_sign(planet.sign)
            if expected_house and planet.house != expected_house:
                errors.append(
                    f'Invariant violation: Planet {planet.id} in sign {planet.sign} '
                    f'should be in house {expected_house}, but is in house {planet.house}'
                )
        
        return errors
    
    def _get_house_for_sign(self, sign_num: int) -> Optional[int]:
        """Get house number for a given sign."""
        for house in self.houses:
            if house.sign == sign_num:
                return house.house_number
        return None
    
    def get_planets_in_house(self, house_num: int) -> List[PlanetInfo]:
        """Get all planets in a specific house, in canonical order."""
        return [p for p in self.planets if p.house == house_num]
    
    def get_planets_in_sign(self, sign_num: int) -> List[PlanetInfo]:
        """Get all planets in a specific sign, in canonical order."""
        return [p for p in self.planets if p.sign == sign_num]
    
    def get_house_for_sign(self, sign_num: int) -> int:
        """
        Calculate house number for a given sign.
        Formula: house = ((sign - ascendant) % 12) + 1
        """
        return ((sign_num - self.ascendant.sign) % 12) + 1
    
    def get_sign_for_house(self, house_num: int) -> int:
        """
        Calculate sign number for a given house.
        Formula: sign = ((ascendant - 1) + (house - 1)) % 12 + 1
        """
        return ((self.ascendant.sign - 1) + (house_num - 1)) % 12 + 1
