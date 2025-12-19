"""
Backend routes package.

Contains API route handlers for various features.
"""

from backend.routes.astro_routes import router as astro_router
from backend.routes.debug_routes import router as debug_router

__all__ = [
    "astro_router",
    "debug_router",
]
