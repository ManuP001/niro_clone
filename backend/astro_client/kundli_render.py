"""
Kundli SVG Renderer (Strict - Astrosage Reference)

Renders normalized kundli data into SVG using base templates.
Follows Astrosage behavior exactly.

KEY RULES:

1. NORTH INDIAN:
   - Houses are FIXED positions
   - Signs rotate ANTI-CLOCKWISE from Ascendant
   - House 1 at top center
   - Planets placed by HOUSE
   - Order planets by DEGREE ASCENDING

2. SOUTH INDIAN:
   - Signs are FIXED positions
   - Aries at TOP-LEFT, proceeding CLOCKWISE
   - Ascendant rendered INSIDE sign cell
   - Planets placed by SIGN
   - Order planets by DEGREE ASCENDING

3. BOTH:
   - Retrograde: ^Planet degree° (caret BEFORE planet)
   - Degree ALWAYS shown with °
   - Vertical stacking (no horizontal compression)
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


# ============ CONSTANTS ============

SIGN_CODES = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]

# Template paths
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
NORTH_TEMPLATE = os.path.join(TEMPLATE_DIR, "kundli_north_base.svg")
SOUTH_TEMPLATE = os.path.join(TEMPLATE_DIR, "kundli_south_base.svg")


# ============ RENDERING VALIDATION ============

class RenderingError(Exception):
    """Raised when rendering fails validation."""
    pass


def _validate_before_render(data: Dict[str, Any], style: str) -> None:
    """Validate data before rendering. FAIL HARD on issues."""
    
    if "ascendant_sign" not in data:
        raise RenderingError("VALIDATION FAILED: Missing ascendant_sign")
    
    if "planets" not in data or len(data["planets"]) == 0:
        raise RenderingError("VALIDATION FAILED: Missing or empty planets array")
    
    for p in data["planets"]:
        if "degree" not in p:
            raise RenderingError(f"VALIDATION FAILED: Planet {p.get('name', '?')} missing degree")
        if "is_retrograde" not in p:
            raise RenderingError(f"VALIDATION FAILED: Planet {p.get('name', '?')} missing is_retrograde")
        if "sign" not in p:
            raise RenderingError(f"VALIDATION FAILED: Planet {p.get('name', '?')} missing sign")
        if style == "north" and "house" not in p:
            raise RenderingError(f"VALIDATION FAILED: Planet {p.get('name', '?')} missing house (required for North Indian)")


# ============ PLANET TEXT FORMATTING ============

def _format_planet_text(planet: Dict[str, Any]) -> str:
    """
    Format planet text for display.
    
    Format: ^Su 10° (caret if retrograde, always show degree)
    
    RULES:
    - Caret ^ BEFORE planet code if is_retrograde=true
    - Degree ALWAYS shown with ° symbol
    - Use API is_retrograde value EXACTLY
    """
    code = planet.get("code", planet["name"][:2])
    degree = planet["degree"]
    is_retro = planet["is_retrograde"]
    
    # Build text
    if is_retro:
        return f"^{code} {degree:.0f}°"
    else:
        return f"{code} {degree:.0f}°"


def _build_planet_stack(planets: List[Dict[str, Any]], color: str = "#b84b4b") -> str:
    """
    Build vertically stacked planet text nodes.
    
    RULES:
    - Order by DEGREE ASCENDING
    - One planet per line
    - Centered alignment
    - Consistent font size (reduce if >5 planets)
    """
    if not planets:
        return ""
    
    # Sort by degree ascending
    sorted_planets = sorted(planets, key=lambda p: p["degree"])
    
    # Determine font size based on count
    count = len(sorted_planets)
    if count <= 3:
        font_size = 13
        line_height = 16
    elif count <= 5:
        font_size = 12
        line_height = 14
    else:
        font_size = 10
        line_height = 12
    
    # Build text nodes
    nodes = []
    for i, planet in enumerate(sorted_planets):
        text = _format_planet_text(planet)
        y_offset = i * line_height
        nodes.append(
            f'<text x="0" y="{y_offset}" text-anchor="middle" '
            f'font-family="Arial,sans-serif" font-size="{font_size}" '
            f'font-weight="bold" fill="{color}">{text}</text>'
        )
    
    return "\n        ".join(nodes)


# ============ NORTH INDIAN RENDERER ============

def render_north_indian(data: Dict[str, Any], title: Optional[str] = None) -> str:
    """
    Render North Indian chart from normalized data.
    
    NORTH INDIAN RULES:
    - Houses are FIXED positions
    - Signs rotate ANTI-CLOCKWISE from Ascendant
    - House 1 at top center (Lagna)
    - Planets placed by HOUSE number
    - Order planets by degree ascending within each house
    - Ascendant marker at center junction only
    
    Args:
        data: Normalized kundli data
        title: Optional chart title
        
    Returns:
        SVG string
    """
    logger.info("[RENDER_NORTH] Starting North Indian render")
    
    # Validate
    _validate_before_render(data, "north")
    
    # Load template
    with open(NORTH_TEMPLATE, 'r', encoding='utf-8') as f:
        svg = f.read()
    
    asc_sign = data["ascendant_sign"]
    asc_sign_num = data.get("ascendant_sign_num", 1)
    houses = data.get("houses", [])
    planets = data["planets"]
    
    # Update title
    if title:
        svg = re.sub(
            r'(<text[^>]*id="chart_title"[^>]*>)[^<]*(</text>)',
            f'\\1{title}\\2',
            svg
        )
    
    # Update ascendant label
    svg = svg.replace('Ascendant: --', f'Ascendant: {asc_sign}')
    
    # Group planets by HOUSE
    planets_by_house = {i: [] for i in range(1, 13)}
    for p in planets:
        house = p["house"]
        if 1 <= house <= 12:
            planets_by_house[house].append(p)
    
    # Render each house
    for house_num in range(1, 13):
        # Get sign for this house
        if houses:
            house_data = next((h for h in houses if h["house"] == house_num), None)
            if house_data:
                sign_code = house_data.get("sign_code", "??")
            else:
                sign_code = "??"
        else:
            # Compute sign: (asc_sign + house - 2) mod 12 + 1
            sign_num = ((asc_sign_num - 1) + (house_num - 1)) % 12 + 1
            sign_code = SIGN_CODES[sign_num - 1]
        
        # Update sign label in template
        pattern = f'(<text[^>]*id="house_{house_num}_sign"[^>]*>)[^<]*(</text>)'
        svg = re.sub(pattern, f'\\1{sign_code}\\2', svg)
        
        # Build planet stack
        house_planets = planets_by_house[house_num]
        if house_planets:
            planet_nodes = _build_planet_stack(house_planets)
            
            # Insert into template
            pattern = f'(<g[^>]*id="house_{house_num}_planets"[^>]*>)(</g>)'
            svg = re.sub(pattern, f'\\1{planet_nodes}\\2', svg)
    
    logger.info(f"[RENDER_NORTH] Complete ({len(svg)} bytes)")
    return svg


# ============ SOUTH INDIAN RENDERER ============

def render_south_indian(data: Dict[str, Any], title: Optional[str] = None) -> str:
    """
    Render South Indian chart from normalized data.
    
    SOUTH INDIAN RULES:
    - Signs are FIXED positions (Aries at top-left, clockwise)
    - Ascendant rendered INSIDE its sign cell
    - Planets placed by SIGN (not house)
    - Order planets by degree ascending within each sign
    
    Args:
        data: Normalized kundli data
        title: Optional chart title
        
    Returns:
        SVG string
    """
    logger.info("[RENDER_SOUTH] Starting South Indian render")
    
    # Validate
    _validate_before_render(data, "south")
    
    # Load template
    with open(SOUTH_TEMPLATE, 'r', encoding='utf-8') as f:
        svg = f.read()
    
    asc_sign = data["ascendant_sign"]
    asc_sign_num = data.get("ascendant_sign_num", 1)
    planets = data["planets"]
    
    # Update title
    if title:
        svg = re.sub(
            r'(<text[^>]*id="chart_title"[^>]*>)[^<]*(</text>)',
            f'\\1{title}\\2',
            svg
        )
    
    # Update ascendant label
    svg = svg.replace('Ascendant: --', f'Ascendant: {asc_sign}')
    
    # Group planets by SIGN (not house!)
    planets_by_sign = {i: [] for i in range(1, 13)}
    for p in planets:
        sign_num = p.get("sign_num")
        if not sign_num:
            # Derive from sign name
            sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            try:
                sign_num = sign_names.index(p["sign"]) + 1
            except ValueError:
                sign_num = 1
        
        if 1 <= sign_num <= 12:
            planets_by_sign[sign_num].append(p)
    
    # Render each sign cell
    for sign_num in range(1, 13):
        # Build content for this sign cell
        content_parts = []
        
        # Add Ascendant marker if this is the ascendant sign
        if sign_num == asc_sign_num:
            content_parts.append(
                '<text x="0" y="-5" text-anchor="middle" '
                'font-family="Georgia,serif" font-size="11" '
                'font-weight="bold" fill="#228B22">Asc</text>'
            )
        
        # Add planets
        sign_planets = planets_by_sign[sign_num]
        if sign_planets:
            # Offset Y to account for Asc marker if present
            y_offset = 12 if sign_num == asc_sign_num else 0
            planet_nodes = _build_planet_stack(sign_planets)
            # Adjust Y positions
            if y_offset > 0:
                planet_nodes = planet_nodes.replace('y="0"', f'y="{y_offset}"')
                # Adjust other y values
                for i in range(1, 10):
                    old_y = i * 16 if len(sign_planets) <= 3 else (i * 14 if len(sign_planets) <= 5 else i * 12)
                    new_y = old_y + y_offset
                    planet_nodes = planet_nodes.replace(f'y="{old_y}"', f'y="{new_y}"')
            content_parts.append(planet_nodes)
        
        # Insert content into template
        if content_parts:
            content = "\n        ".join(content_parts)
            pattern = f'(<g[^>]*id="sign_{sign_num}_content"[^>]*>)(</g>)'
            svg = re.sub(pattern, f'\\1{content}\\2', svg)
    
    logger.info(f"[RENDER_SOUTH] Complete ({len(svg)} bytes)")
    return svg


# ============ MAIN ENTRY POINT ============

def render_kundli_chart(
    data: Dict[str, Any],
    style: str = "north",
    title: Optional[str] = None
) -> str:
    """
    Main entry point for kundli rendering.
    
    Args:
        data: Normalized kundli data
        style: "north" or "south"
        title: Optional chart title
        
    Returns:
        SVG string
        
    Raises:
        RenderingError: If validation fails
    """
    style = style.lower()
    
    if style == "south":
        return render_south_indian(data, title)
    else:
        return render_north_indian(data, title)
