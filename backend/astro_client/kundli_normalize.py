"""
Kundli Data Normalization Layer (Strict)

Converts raw VedicAstro API response to normalized data.
FAILS HARD if any required field is missing.

Normalized Output Shape:
{
  "ascendant_sign": "Sagittarius",
  "ascendant_degree": 27.0,
  "planets": [
    {
      "name": "Sun",
      "code": "Su",
      "sign": "Capricorn",
      "sign_num": 10,
      "house": 2,
      "degree": 10.08,
      "is_retrograde": false
    },
    ...
  ]
}
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


# ============ CONSTANTS ============

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_CODES = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]

PLANET_CODES = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"
}

PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# API key mapping
API_PLANET_KEYS = {
    "1": "Sun", "2": "Moon", "3": "Mars", "4": "Mercury",
    "5": "Jupiter", "6": "Venus", "7": "Saturn", "8": "Rahu", "9": "Ketu"
}


def sign_name_to_num(name: str) -> int:
    """Convert sign name to number (1-12). Returns 0 if invalid."""
    try:
        return SIGN_NAMES.index(name) + 1
    except ValueError:
        return 0


def sign_num_to_name(num: int) -> str:
    """Convert sign number (1-12) to name."""
    if 1 <= num <= 12:
        return SIGN_NAMES[num - 1]
    return "Unknown"


def sign_num_to_code(num: int) -> str:
    """Convert sign number (1-12) to short code."""
    if 1 <= num <= 12:
        return SIGN_CODES[num - 1]
    return "??"


# ============ VALIDATION ============

class NormalizationError(Exception):
    """Raised when normalization fails due to missing/invalid data."""
    pass


def _validate_required(data: Dict, field: str, context: str) -> Any:
    """Validate that a required field exists. FAIL HARD if missing."""
    if field not in data or data[field] is None:
        raise NormalizationError(f"MISSING REQUIRED FIELD: '{field}' in {context}")
    return data[field]


def _validate_sign(sign_name: str, context: str) -> Tuple[str, int]:
    """Validate sign name is canonical. Returns (name, number)."""
    if sign_name not in SIGN_NAMES:
        raise NormalizationError(f"INVALID SIGN: '{sign_name}' in {context}. Must be one of {SIGN_NAMES}")
    return sign_name, sign_name_to_num(sign_name)


def _validate_degree(degree: Any, context: str) -> float:
    """Validate and normalize degree. Must be 0-30."""
    try:
        deg = float(degree)
    except (TypeError, ValueError):
        raise NormalizationError(f"INVALID DEGREE: '{degree}' in {context}. Must be numeric.")
    
    if deg < 0 or deg >= 30:
        # Normalize to 0-30 range
        deg = deg % 30
    
    return round(deg, 2)


def _validate_house(house: Any, context: str) -> int:
    """Validate house number. Must be 1-12."""
    try:
        h = int(house)
    except (TypeError, ValueError):
        raise NormalizationError(f"INVALID HOUSE: '{house}' in {context}. Must be 1-12.")
    
    if h < 1 or h > 12:
        raise NormalizationError(f"INVALID HOUSE: {h} in {context}. Must be 1-12.")
    
    return h


# ============ NORMALIZATION ============

def normalize_kundli_data(api_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize VedicAstro API response into strict format.
    
    FAILS HARD if any required field is missing.
    
    Args:
        api_response: Raw response from VedicAstroAPI /horoscope/planet-details
        
    Returns:
        Normalized data dict
        
    Raises:
        NormalizationError: If any required field is missing or invalid
    """
    logger.info("[NORMALIZE] Starting strict normalization")
    
    # Handle nested 'response' key
    if 'response' in api_response:
        data = api_response['response']
    else:
        data = api_response
    
    # ============ ASCENDANT ============
    asc_data = data.get("0")
    if not asc_data:
        raise NormalizationError("MISSING ASCENDANT DATA (key '0')")
    
    asc_sign_name = _validate_required(asc_data, "zodiac", "Ascendant")
    asc_sign_name, asc_sign_num = _validate_sign(asc_sign_name, "Ascendant")
    asc_degree = _validate_degree(_validate_required(asc_data, "local_degree", "Ascendant"), "Ascendant")
    
    logger.info(f"[NORMALIZE] Ascendant: {asc_sign_name} @ {asc_degree}°")
    
    # ============ PLANETS ============
    planets = []
    
    for api_key, planet_name in API_PLANET_KEYS.items():
        p_data = data.get(api_key)
        if not p_data:
            raise NormalizationError(f"MISSING PLANET DATA: {planet_name} (key '{api_key}')")
        
        # Extract and validate fields
        p_sign_name = _validate_required(p_data, "zodiac", planet_name)
        p_sign_name, p_sign_num = _validate_sign(p_sign_name, planet_name)
        
        p_degree = _validate_degree(
            _validate_required(p_data, "local_degree", planet_name),
            planet_name
        )
        
        p_house = _validate_house(
            _validate_required(p_data, "house", planet_name),
            planet_name
        )
        
        # Retrograde - MUST use API value exactly
        p_retro = bool(p_data.get("retro", False))
        
        planets.append({
            "name": planet_name,
            "code": PLANET_CODES[planet_name],
            "sign": p_sign_name,
            "sign_num": p_sign_num,
            "house": p_house,
            "degree": p_degree,
            "is_retrograde": p_retro
        })
        
        retro_str = "(R)" if p_retro else ""
        logger.debug(f"[NORMALIZE] {planet_name}: {p_sign_name} H{p_house} @ {p_degree}° {retro_str}")
    
    # ============ COMPUTE HOUSE-SIGN MAPPING ============
    # In Whole Sign house system:
    # House 1 = Ascendant sign
    # House N = (Ascendant sign + N - 2) mod 12 + 1
    houses = []
    for house_num in range(1, 13):
        sign_num = ((asc_sign_num - 1) + (house_num - 1)) % 12 + 1
        houses.append({
            "house": house_num,
            "sign": sign_num_to_name(sign_num),
            "sign_num": sign_num,
            "sign_code": sign_num_to_code(sign_num)
        })
    
    # Build normalized output
    normalized = {
        "ascendant_sign": asc_sign_name,
        "ascendant_sign_num": asc_sign_num,
        "ascendant_degree": asc_degree,
        "houses": houses,
        "planets": planets
    }
    
    logger.info(f"[NORMALIZE] Complete: {len(planets)} planets normalized")
    
    return normalized


def validate_normalized_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate normalized data for rendering.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Check ascendant
    if "ascendant_sign" not in data:
        errors.append("Missing ascendant_sign")
    elif data["ascendant_sign"] not in SIGN_NAMES:
        errors.append(f"Invalid ascendant_sign: {data['ascendant_sign']}")
    
    if "ascendant_degree" not in data:
        errors.append("Missing ascendant_degree")
    
    # Check planets
    if "planets" not in data:
        errors.append("Missing planets array")
    else:
        for p in data["planets"]:
            if "name" not in p:
                errors.append(f"Planet missing name")
            if "sign" not in p:
                errors.append(f"Planet {p.get('name', '?')} missing sign")
            elif p["sign"] not in SIGN_NAMES:
                errors.append(f"Planet {p['name']} has invalid sign: {p['sign']}")
            if "degree" not in p:
                errors.append(f"Planet {p.get('name', '?')} missing degree")
            if "is_retrograde" not in p:
                errors.append(f"Planet {p.get('name', '?')} missing is_retrograde")
    
    return len(errors) == 0, errors
