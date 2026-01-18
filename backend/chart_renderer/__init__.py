"""
Chart Renderer Module

Provides deterministic, astrologically correct chart rendering
for both North Indian and South Indian layouts.

Usage:
    from chart_renderer import normalize_chart, render_north, render_south
    
    # Normalize raw API data
    normalized = normalize_chart(raw_data)
    
    # Render SVG
    svg = render_north(normalized)  # or render_south(normalized)
"""

from .models import NormalizedChart, ChartMetadata, AscendantData, HouseInfo, PlanetInfo
from .normalize_chart import normalize_chart, validate_chart
from .renderer_north import render_north_indian_chart
from .renderer_south import render_south_indian_chart

__all__ = [
    'NormalizedChart',
    'ChartMetadata', 
    'AscendantData',
    'HouseInfo',
    'PlanetInfo',
    'normalize_chart',
    'validate_chart',
    'render_north_indian_chart',
    'render_south_indian_chart',
]
