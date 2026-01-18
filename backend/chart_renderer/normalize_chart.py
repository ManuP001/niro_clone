"""
Chart Normalization Module

Converts raw Vedic API data into the normalized NormalizedChart contract.
This is the ONLY place where raw API parsing happens.
Renderers receive only NormalizedChart objects.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from .models import (
    NormalizedChart,
    ChartMetadata,
    AscendantData,
    HouseInfo,
    PlanetInfo,
    ChartType,
    PLANET_ABBR,
    SIGN_NAMES,
    sign_name_to_num
)

logger = logging.getLogger(__name__)


def normalize_chart(
    raw_planets: List[Dict[str, Any]],
    ascendant_sign: str,
    ascendant_degree: float = 0.0,
    ayanamsa: str = 'Lahiri',
    house_system: str = 'Whole Sign'
) -> NormalizedChart:
    """
    Normalize raw chart data into the NormalizedChart contract.
    
    Args:
        raw_planets: List of planet data dicts with keys:
            - name: Planet name (e.g., 'Sun', 'Moon')
            - sign: Sign name (e.g., 'Aries', 'Taurus')
            - house: House number (1-12)
            - degree: Degree within sign (0-30)
            - retrograde: Boolean (optional)
        ascendant_sign: Ascendant sign name (e.g., 'Aries')
        ascendant_degree: Ascendant degree within sign (0-30)
        ayanamsa: Ayanamsa used (default: Lahiri)
        house_system: House system (default: Whole Sign)
    
    Returns:
        NormalizedChart object ready for rendering
    
    Raises:
        ValueError: If required data is missing or invalid
    """
    logger.info(f"[NORMALIZE] Normalizing chart with ascendant {ascendant_sign}")
    
    # Convert ascendant sign name to number
    asc_sign_num = sign_name_to_num(ascendant_sign)
    if asc_sign_num == 0:
        raise ValueError(f"Invalid ascendant sign: {ascendant_sign}")
    
    # Create ascendant data
    ascendant = AscendantData(
        sign=asc_sign_num,
        degree=ascendant_degree
    )
    
    # Build houses (Whole Sign house system)
    houses = []
    for house_num in range(1, 13):
        # In Whole Sign, House N has sign = (ascendant + N - 1) mod 12
        house_sign = ((asc_sign_num - 1) + (house_num - 1)) % 12 + 1
        houses.append(HouseInfo(
            house_number=house_num,
            sign=house_sign
        ))
    
    # Normalize planets
    planets = []
    seen_planets = set()
    
    for p in raw_planets:
        # Get planet name and convert to abbreviation
        name = p.get('name', '')
        abbr = PLANET_ABBR.get(name, name[:2] if name else 'XX')
        
        # Skip duplicates
        if abbr in seen_planets:
            logger.warning(f"[NORMALIZE] Duplicate planet {abbr}, skipping")
            continue
        seen_planets.add(abbr)
        
        # Get sign (convert name to number if needed)
        sign = p.get('sign', 'Aries')
        if isinstance(sign, str):
            sign_num = sign_name_to_num(sign)
            if sign_num == 0:
                logger.warning(f"[NORMALIZE] Invalid sign '{sign}' for {name}, defaulting to Aries")
                sign_num = 1
        else:
            sign_num = int(sign)
        
        # Get house (use provided or calculate from sign)
        house = p.get('house')
        if house is None or not (1 <= house <= 12):
            # Calculate house from sign using Whole Sign
            house = ((sign_num - asc_sign_num) % 12) + 1
        
        # Get degree
        degree = float(p.get('degree', 0.0))
        if not (0 <= degree < 30):
            degree = degree % 30
        
        # Get retrograde status
        retro = bool(p.get('retrograde', False) or p.get('retro', False))
        
        planets.append(PlanetInfo(
            id=abbr,
            sign=sign_num,
            house=house,
            degree=degree,
            retro=retro
        ))
    
    # Create metadata
    metadata = ChartMetadata(
        ayanamsa=ayanamsa,
        house_system=house_system,
        zodiac_type='sidereal',
        chart_type=ChartType.D1
    )
    
    # Build normalized chart
    chart = NormalizedChart(
        metadata=metadata,
        ascendant=ascendant,
        houses=houses,
        planets=planets
    )
    
    logger.info(f"[NORMALIZE] Created chart with {len(planets)} planets, ascendant in {ascendant_sign}")
    
    return chart


def validate_chart(chart: NormalizedChart) -> Tuple[bool, List[str]]:
    """
    Validate a normalized chart for rendering.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = chart.validate_invariants()
    
    # Additional validation
    if len(chart.planets) < 9:
        errors.append(f"Expected 9 planets, found {len(chart.planets)}")
    
    if len(chart.houses) != 12:
        errors.append(f"Expected 12 houses, found {len(chart.houses)}")
    
    return len(errors) == 0, errors


def normalize_from_vedic_api_response(
    planet_details: Dict[str, Any],
    kundli_details: Optional[Dict[str, Any]] = None
) -> NormalizedChart:
    """
    Normalize chart from raw VedicAstroAPI responses.
    
    This handles the specific response format from:
    - /horoscope/planet-details
    - /extended-horoscope/extended-kundli-details
    
    Args:
        planet_details: Response from /horoscope/planet-details
        kundli_details: Optional response from extended-kundli-details
    
    Returns:
        NormalizedChart ready for rendering
    """
    logger.info("[NORMALIZE] Parsing VedicAstroAPI response")
    
    # Planet key mapping from API
    planet_key_map = {
        "0": "Ascendant", "1": "Sun", "2": "Moon", "3": "Mars",
        "4": "Mercury", "5": "Jupiter", "6": "Venus", "7": "Saturn",
        "8": "Rahu", "9": "Ketu"
    }
    
    # Extract ascendant
    asc_data = planet_details.get("0", {})
    ascendant_sign = asc_data.get('zodiac', 'Aries')
    ascendant_degree = float(asc_data.get('local_degree', 0))
    
    # Extract planets
    raw_planets = []
    for key, planet_name in planet_key_map.items():
        if planet_name == "Ascendant":
            continue
        
        p = planet_details.get(key, {})
        if not p:
            continue
        
        raw_planets.append({
            'name': planet_name,
            'sign': p.get('zodiac', 'Aries'),
            'house': p.get('house', 1),
            'degree': p.get('local_degree', 0),
            'retrograde': p.get('retro', False)
        })
    
    # Get ayanamsa from panchang if available
    panchang = planet_details.get('panchang', {})
    ayanamsa = panchang.get('ayanamsa_name', 'Lahiri')
    
    return normalize_chart(
        raw_planets=raw_planets,
        ascendant_sign=ascendant_sign,
        ascendant_degree=ascendant_degree,
        ayanamsa=ayanamsa
    )
