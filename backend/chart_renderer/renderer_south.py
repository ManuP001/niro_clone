"""
South Indian Chart Renderer

Generates SVG for South Indian (square) style Kundli chart.

KEY CONCEPT: Signs are FIXED positions, houses MOVE based on ascendant.

Traditional Layout (Signs are fixed - Pisces/12 at top-left, going clockwise):
```
    [Pi/12] [Ar/1]  [Ta/2]  [Ge/3]
    [Aq/11]                 [Cn/4]
    [Cp/10]                 [Le/5]
    [Sg/9]  [Sc/8]  [Li/7]  [Vi/6]
```

- Signs are FIXED in position (never move)
- House number = relative position from ascendant sign
- Planets placed by their SIGN (not house)
- Ascendant sign cell is highlighted
"""

import logging
from typing import List, Optional, Dict, Any

from .models import NormalizedChart, PlanetInfo, PLANET_ORDER, sign_num_to_name

logger = logging.getLogger(__name__)


# ============ SIGN POSITION MAP (FIXED) ============
# Maps sign number (1-12) to grid position (row, col) in 4x4 grid
# Center 2x2 is empty/decorative
SIGN_GRID_POSITIONS = {
    12: (0, 0),  # Pisces - top left
    1:  (0, 1),  # Aries
    2:  (0, 2),  # Taurus
    3:  (0, 3),  # Gemini - top right
    4:  (1, 3),  # Cancer
    5:  (2, 3),  # Leo
    6:  (3, 3),  # Virgo - bottom right
    7:  (3, 2),  # Libra
    8:  (3, 1),  # Scorpio
    9:  (3, 0),  # Sagittarius - bottom left
    10: (2, 0),  # Capricorn
    11: (1, 0),  # Aquarius
}


def render_south_indian_chart(
    chart: NormalizedChart,
    show_sign_numbers: bool = True,
    show_sign_names: bool = False,
    show_house_numbers: bool = True,
    show_degrees: bool = False,
    title: Optional[str] = None
) -> str:
    """
    Render a South Indian style birth chart as SVG.
    
    Args:
        chart: Normalized chart data
        show_sign_numbers: Show sign number (1-12) in each cell
        show_sign_names: Show sign abbreviation
        show_house_numbers: Show house number (derived from ascendant)
        show_degrees: Show planet degrees
        title: Optional custom title
    
    Returns:
        SVG string
    """
    logger.info(f"[SOUTH_RENDERER] Rendering chart with ascendant sign {chart.ascendant.sign}")
    
    asc_sign = chart.ascendant.sign  # 1-12
    asc_sign_name = sign_num_to_name(asc_sign)
    
    # Group planets by SIGN
    planets_by_sign = {i: [] for i in range(1, 13)}
    for p in chart.planets:
        abbr = p.display_label  # Includes (R) if retrograde
        planets_by_sign[p.sign].append(abbr)
    
    # Sort planets in each sign by canonical order
    for sign in planets_by_sign:
        planets_by_sign[sign].sort(
            key=lambda x: PLANET_ORDER.index(x.replace('(R)', '')) if x.replace('(R)', '') in PLANET_ORDER else 99
        )
    
    # Chart dimensions
    size = 400
    pad = 50
    total_w = size + 2 * pad
    total_h = size + pad + 30
    cell = size // 4
    
    # Grid origin
    gx = pad
    gy = pad
    cx = total_w // 2
    
    # Colors
    bg = "#FFFEF5"
    line = "#8B4513"
    text = "#4A3728"
    planet_color = "#B22222"
    sign_color = "#666666"
    house_color = "#4169E1"
    asc_bg = "#E8F5E9"
    asc_color = "#228B22"
    
    # Chart title
    if title is None:
        title = "Birth Chart (Rāśi)"
    
    svg_parts = [f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" style="max-width:100%;height:auto;">
  <rect width="100%" height="100%" fill="{bg}"/>
  
  <!-- Title -->
  <text x="{cx}" y="22" text-anchor="middle" font-family="Georgia,serif" font-size="18" font-weight="bold" fill="{text}">{title}</text>
  <text x="{cx}" y="40" text-anchor="middle" font-family="Georgia,serif" font-size="12" fill="{sign_color}">Ascendant: {asc_sign_name}</text>
  
  <!-- Outer Border -->
  <rect x="{gx}" y="{gy}" width="{size}" height="{size}" fill="none" stroke="{line}" stroke-width="2"/>
  
  <!-- Grid Lines -->
  <line x1="{gx+cell}" y1="{gy}" x2="{gx+cell}" y2="{gy+size}" stroke="{line}" stroke-width="1"/>
  <line x1="{gx+2*cell}" y1="{gy}" x2="{gx+2*cell}" y2="{gy+size}" stroke="{line}" stroke-width="1"/>
  <line x1="{gx+3*cell}" y1="{gy}" x2="{gx+3*cell}" y2="{gy+size}" stroke="{line}" stroke-width="1"/>
  <line x1="{gx}" y1="{gy+cell}" x2="{gx+size}" y2="{gy+cell}" stroke="{line}" stroke-width="1"/>
  <line x1="{gx}" y1="{gy+2*cell}" x2="{gx+size}" y2="{gy+2*cell}" stroke="{line}" stroke-width="1"/>
  <line x1="{gx}" y1="{gy+3*cell}" x2="{gx+size}" y2="{gy+3*cell}" stroke="{line}" stroke-width="1"/>''']
    
    # Render each sign cell
    for sign_num, (row, col) in SIGN_GRID_POSITIONS.items():
        cell_x = gx + col * cell
        cell_y = gy + row * cell
        cell_cx = cell_x + cell / 2
        cell_cy = cell_y + cell / 2
        
        house_num = chart.get_house_for_sign(sign_num)
        is_ascendant = (sign_num == asc_sign)
        
        # Highlight ascendant cell
        if is_ascendant:
            svg_parts.append(
                f'  <rect x="{cell_x+1}" y="{cell_y+1}" width="{cell-2}" height="{cell-2}" fill="{asc_bg}"/>'
            )
        
        # Sign number (top-left)
        if show_sign_numbers:
            svg_parts.append(
                f'  <text x="{cell_x+5}" y="{cell_y+14}" '
                f'font-family="Georgia,serif" font-size="10" fill="{sign_color}">{sign_num}</text>'
            )
        
        # House number (top-right)
        if show_house_numbers:
            svg_parts.append(
                f'  <text x="{cell_x+cell-5}" y="{cell_y+14}" text-anchor="end" '
                f'font-family="Georgia,serif" font-size="9" fill="{house_color}">H{house_num}</text>'
            )
        
        # Ascendant marker
        if is_ascendant:
            svg_parts.append(
                f'  <text x="{cell_cx}" y="{cell_y+cell-8}" text-anchor="middle" '
                f'font-family="Georgia,serif" font-size="10" font-weight="bold" fill="{asc_color}">Asc</text>'
            )
        
        # Planets
        planet_list = planets_by_sign.get(sign_num, [])
        if planet_list:
            if len(planet_list) <= 2:
                planet_str = ' '.join(planet_list)
                svg_parts.append(
                    f'  <text x="{cell_cx}" y="{cell_cy}" text-anchor="middle" '
                    f'font-family="Georgia,serif" font-size="12" font-weight="bold" '
                    f'fill="{planet_color}">{planet_str}</text>'
                )
            else:
                # Stack vertically
                start_y = cell_cy - (len(planet_list) - 1) * 6
                for i, pl in enumerate(planet_list):
                    svg_parts.append(
                        f'  <text x="{cell_cx}" y="{start_y + i*12}" text-anchor="middle" '
                        f'font-family="Georgia,serif" font-size="11" font-weight="bold" '
                        f'fill="{planet_color}">{pl}</text>'
                    )
    
    # Center area (empty in South Indian)
    center_x = gx + cell
    center_y = gy + cell
    svg_parts.append(f'  <rect x="{center_x}" y="{center_y}" width="{cell*2}" height="{cell*2}" fill="{bg}"/>')
    svg_parts.append(
        f'  <text x="{center_x+cell}" y="{center_y+cell-5}" text-anchor="middle" '
        f'font-family="Georgia,serif" font-size="11" fill="{sign_color}" opacity="0.5">South</text>'
    )
    svg_parts.append(
        f'  <text x="{center_x+cell}" y="{center_y+cell+10}" text-anchor="middle" '
        f'font-family="Georgia,serif" font-size="11" fill="{sign_color}" opacity="0.5">Indian</text>'
    )
    
    svg_parts.append('</svg>')
    
    svg = '\n'.join(svg_parts)
    logger.info(f"[SOUTH_RENDERER] Generated SVG ({len(svg)} bytes)")
    
    return svg
