"""
North Indian Chart Renderer

Generates SVG for North Indian (diamond) style Kundli chart.

KEY CONCEPT: Houses are FIXED positions, signs MOVE based on ascendant.

Traditional Layout (Houses are fixed):
```
          [H12]  [H1]   [H2]
     [H11]                   [H3]
     [H10]       Asc         [H4]
     [H9]                    [H5]
          [H8]   [H7]   [H6]
```

- House 1 (Lagna) is at TOP CENTER
- Houses proceed COUNTER-CLOCKWISE
- Sign NUMBER displayed in each house shows which sign occupies it
- Planets placed by their HOUSE number (not sign)
"""

import logging
from typing import List, Optional, Dict, Any

from .models import NormalizedChart, PlanetInfo, PLANET_ORDER, sign_num_to_name

logger = logging.getLogger(__name__)


# ============ CONSTANTS ============
PLANET_ABBR = {
    'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me',
    'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa', 'Rahu': 'Ra', 'Ketu': 'Ke'
}


def render_north_indian_chart(
    chart: NormalizedChart,
    show_sign_numbers: bool = True,
    show_sign_names: bool = False,
    show_degrees: bool = False,
    title: Optional[str] = None
) -> str:
    """
    Render a North Indian style birth chart as SVG.
    
    Args:
        chart: Normalized chart data
        show_sign_numbers: Show sign number (1-12) in each house
        show_sign_names: Show sign abbreviation instead of number
        show_degrees: Show planet degrees (small text)
        title: Optional custom title
    
    Returns:
        SVG string
    """
    logger.info(f"[NORTH_RENDERER] Rendering chart with ascendant sign {chart.ascendant.sign}")
    
    asc_sign = chart.ascendant.sign  # 1-12
    asc_sign_name = sign_num_to_name(asc_sign)
    
    # Group planets by HOUSE
    planets_by_house = {i: [] for i in range(1, 13)}
    for p in chart.planets:
        abbr = p.display_label  # Includes (R) if retrograde
        planets_by_house[p.house].append(abbr)
    
    # Sort planets in each house by canonical order
    for house in planets_by_house:
        planets_by_house[house].sort(
            key=lambda x: PLANET_ORDER.index(x.replace('(R)', '')) if x.replace('(R)', '') in PLANET_ORDER else 99
        )
    
    # Chart dimensions
    size = 400
    pad = 50
    total_w = size + 2 * pad
    total_h = size + pad + 30
    
    # Center of chart
    cx = total_w // 2
    cy = pad + size // 2
    half = size // 2
    q = size // 4
    
    # Colors
    bg = "#FFFEF5"
    line = "#8B4513"
    text = "#4A3728"
    planet_color = "#B22222"
    sign_color = "#666666"
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
  
  <!-- Outer Square -->
  <rect x="{cx-half}" y="{cy-half}" width="{size}" height="{size}" fill="none" stroke="{line}" stroke-width="2"/>
  
  <!-- Diagonals -->
  <line x1="{cx-half}" y1="{cy-half}" x2="{cx+half}" y2="{cy+half}" stroke="{line}" stroke-width="1.5"/>
  <line x1="{cx+half}" y1="{cy-half}" x2="{cx-half}" y2="{cy+half}" stroke="{line}" stroke-width="1.5"/>
  
  <!-- Inner Diamond -->
  <polygon points="{cx},{cy-half} {cx+half},{cy} {cx},{cy+half} {cx-half},{cy}" fill="none" stroke="{line}" stroke-width="1.5"/>''']
    
    # House positions (FIXED in North Indian)
    # Layout: House 1 at top center, counter-clockwise
    # Position map: house_num -> (sign_x, sign_y, planet_x, planet_y)
    house_positions = {
        1:  (cx, cy - half + 15, cx, cy - half + 50),              # Top center (Lagna)
        2:  (cx + q, cy - half + 15, cx + q, cy - half + 50),      # Top right
        3:  (cx + half - 15, cy - q, cx + half - 50, cy - q),      # Right upper
        4:  (cx + half - 15, cy, cx + half - 50, cy),              # Right middle
        5:  (cx + half - 15, cy + q, cx + half - 50, cy + q),      # Right lower
        6:  (cx + q, cy + half - 15, cx + q, cy + half - 50),      # Bottom right
        7:  (cx, cy + half - 15, cx, cy + half - 50),              # Bottom center
        8:  (cx - q, cy + half - 15, cx - q, cy + half - 50),      # Bottom left
        9:  (cx - half + 15, cy + q, cx - half + 50, cy + q),      # Left lower
        10: (cx - half + 15, cy, cx - half + 50, cy),              # Left middle
        11: (cx - half + 15, cy - q, cx - half + 50, cy - q),      # Left upper
        12: (cx - q, cy - half + 15, cx - q, cy - half + 50),      # Top left
    }
    
    # Render each house
    for house_num, (sx, sy, px, py) in house_positions.items():
        sign_num = chart.get_sign_for_house(house_num)
        
        # Sign indicator (number or abbreviation)
        if show_sign_names:
            sign_label = sign_num_to_name(sign_num)[:2]
        else:
            sign_label = str(sign_num)
        
        svg_parts.append(
            f'  <text x="{sx}" y="{sy}" text-anchor="middle" '
            f'font-family="Georgia,serif" font-size="11" fill="{sign_color}">{sign_label}</text>'
        )
        
        # Planets
        planet_list = planets_by_house.get(house_num, [])
        if planet_list:
            if len(planet_list) <= 2:
                planet_str = ' '.join(planet_list)
                svg_parts.append(
                    f'  <text x="{px}" y="{py}" text-anchor="middle" '
                    f'font-family="Georgia,serif" font-size="13" font-weight="bold" '
                    f'fill="{planet_color}">{planet_str}</text>'
                )
            else:
                # Stack vertically for multiple planets
                start_y = py - (len(planet_list) - 1) * 7
                for i, pl in enumerate(planet_list):
                    svg_parts.append(
                        f'  <text x="{px}" y="{start_y + i*14}" text-anchor="middle" '
                        f'font-family="Georgia,serif" font-size="12" font-weight="bold" '
                        f'fill="{planet_color}">{pl}</text>'
                    )
    
    # Ascendant marker in center
    svg_parts.append(
        f'  <text x="{cx}" y="{cy + 4}" text-anchor="middle" '
        f'font-family="Georgia,serif" font-size="12" fill="{asc_color}" '
        f'font-style="italic">Asc</text>'
    )
    
    svg_parts.append('</svg>')
    
    svg = '\n'.join(svg_parts)
    logger.info(f"[NORTH_RENDERER] Generated SVG ({len(svg)} bytes)")
    
    return svg
