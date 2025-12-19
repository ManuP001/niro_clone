"""
Location normalization service.

Convert place_text → lat/lon + timezone.
Mandatory step - abort astro computation if fails.
"""

import logging
from typing import Optional, Tuple
from datetime import datetime
from zoneinfo import ZoneInfo
from backend.models.astro_models import BirthProfile, AstroError, AstroErrorCode

logger = logging.getLogger(__name__)


class LocationNormalizer:
    """
    Normalize location data.
    
    This is a simplified implementation.
    In production, use Google Geocoding API or similar.
    """
    
    # Simple mapping of Indian cities (for demo)
    CITY_DB = {
        "new york": {"lat": 40.7128, "lon": -74.0060, "tz": "America/New_York"},
        "london": {"lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
        "mumbai": {"lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata"},
        "delhi": {"lat": 28.7041, "lon": 77.1025, "tz": "Asia/Kolkata"},
        "bangalore": {"lat": 12.9716, "lon": 77.5946, "tz": "Asia/Kolkata"},
        "kolkata": {"lat": 22.5726, "lon": 88.3639, "tz": "Asia/Kolkata"},
        "chennai": {"lat": 13.0827, "lon": 80.2707, "tz": "Asia/Kolkata"},
        "hyderabad": {"lat": 17.3850, "lon": 78.4867, "tz": "Asia/Kolkata"},
    }
    
    async def normalize(self, birth_profile: BirthProfile) -> Tuple[Optional[AstroError], Optional[BirthProfile]]:
        """
        Normalize location data.
        
        Returns:
            (error, updated_profile)
            If error is None, profile has lat/lon/timezone set.
            If error is not None, do not proceed with astro computation.
        """
        place_lower = birth_profile.place_text.lower().strip()
        
        # Try exact match first
        if place_lower in self.CITY_DB:
            data = self.CITY_DB[place_lower]
            birth_profile.lat = data["lat"]
            birth_profile.lon = data["lon"]
            birth_profile.timezone = data["tz"]
            logger.info(f"✓ Location normalized: {birth_profile.place_text} → {data['tz']}")
            return None, birth_profile
        
        # Try partial match
        for city, data in self.CITY_DB.items():
            if place_lower.startswith(city) or city.startswith(place_lower):
                birth_profile.lat = data["lat"]
                birth_profile.lon = data["lon"]
                birth_profile.timezone = data["tz"]
                logger.info(f"✓ Location normalized (partial): {birth_profile.place_text} → {data['tz']}")
                return None, birth_profile
        
        # Could not normalize
        error = AstroError(
            code=AstroErrorCode.GEOCODE_FAILED,
            message=f"Could not normalize location: '{birth_profile.place_text}'",
            details="Add to CITY_DB or integrate real geocoding API"
        )
        logger.error(f"❌ {error.message}")
        return error, None
    
    def get_utc_offset_minutes(self, timezone: str, date_of_birth: str) -> int:
        """
        Compute UTC offset for given timezone and date.
        Accounts for DST.
        
        Args:
            timezone: IANA timezone string (e.g., "America/New_York")
            date_of_birth: YYYY-MM-DD format
        
        Returns:
            UTC offset in minutes
        """
        try:
            tz = ZoneInfo(timezone)
            # Use noon of the birth date to determine DST
            dt = datetime.fromisoformat(f"{date_of_birth}T12:00:00").replace(tzinfo=tz)
            # Get UTC offset
            offset = dt.utcoffset()
            if offset:
                return int(offset.total_seconds() / 60)
        except Exception as e:
            logger.warning(f"Could not compute UTC offset for {timezone}: {e}")
        
        return 0
