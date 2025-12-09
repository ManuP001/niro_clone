"""
Astro Profile & Transits Storage Layer

In-memory storage with DB-ready interface.
Design allows easy swap to Redis, MongoDB, or Postgres.

TODO: Implement RedisStorage or MongoStorage when needed.
"""

import logging
from typing import Dict, Optional
from datetime import datetime, date, timedelta
from abc import ABC, abstractmethod

from .models import AstroProfile, AstroTransits, BirthDetails
from .vedic_api import vedic_api_client

logger = logging.getLogger(__name__)

# Configuration
TRANSITS_TTL_HOURS = 24  # Refresh transits every 24 hours
TRANSIT_PAST_YEARS = 2    # Look back 2 years for past themes
TRANSIT_FUTURE_YEARS = 1  # Look forward 1 year


class AstroStorage(ABC):
    """Abstract base class for astro data storage"""
    
    @abstractmethod
    async def save_profile(self, profile: AstroProfile) -> None:
        pass
    
    @abstractmethod
    async def get_profile(self, user_id: str) -> Optional[AstroProfile]:
        pass
    
    @abstractmethod
    async def delete_profile(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    async def save_transits(self, transits: AstroTransits) -> None:
        pass
    
    @abstractmethod
    async def get_transits(self, user_id: str) -> Optional[AstroTransits]:
        pass
    
    @abstractmethod
    async def delete_transits(self, user_id: str) -> bool:
        pass


class InMemoryAstroStorage(AstroStorage):
    """
    In-memory storage for astro profiles and transits.
    Suitable for development and single-instance deployments.
    """
    
    def __init__(self):
        self._profiles: Dict[str, AstroProfile] = {}
        self._transits: Dict[str, AstroTransits] = {}
        logger.info("InMemoryAstroStorage initialized")
    
    async def save_profile(self, profile: AstroProfile) -> None:
        profile.updated_at = datetime.utcnow()
        self._profiles[profile.user_id] = profile
        logger.info(f"Saved profile for user {profile.user_id}")
    
    async def get_profile(self, user_id: str) -> Optional[AstroProfile]:
        profile = self._profiles.get(user_id)
        if profile:
            logger.debug(f"Retrieved profile for user {user_id}")
        return profile
    
    async def delete_profile(self, user_id: str) -> bool:
        if user_id in self._profiles:
            del self._profiles[user_id]
            logger.info(f"Deleted profile for user {user_id}")
            return True
        return False
    
    async def save_transits(self, transits: AstroTransits) -> None:
        transits.computed_at = datetime.utcnow()
        self._transits[transits.user_id] = transits
        logger.info(f"Saved transits for user {transits.user_id}")
    
    async def get_transits(self, user_id: str) -> Optional[AstroTransits]:
        transits = self._transits.get(user_id)
        if transits:
            logger.debug(f"Retrieved transits for user {user_id}")
        return transits
    
    async def delete_transits(self, user_id: str) -> bool:
        if user_id in self._transits:
            del self._transits[user_id]
            logger.info(f"Deleted transits for user {user_id}")
            return True
        return False
    
    def count_profiles(self) -> int:
        return len(self._profiles)
    
    def count_transits(self) -> int:
        return len(self._transits)


# Singleton storage instance
_storage = InMemoryAstroStorage()


# Public API functions
async def save_astro_profile(profile: AstroProfile) -> None:
    """Save an astro profile"""
    await _storage.save_profile(profile)


async def get_astro_profile(user_id: str) -> Optional[AstroProfile]:
    """Get an astro profile by user ID"""
    return await _storage.get_profile(user_id)


async def delete_astro_profile(user_id: str) -> bool:
    """Delete an astro profile"""
    return await _storage.delete_profile(user_id)


async def save_astro_transits(transits: AstroTransits) -> None:
    """Save astro transits"""
    await _storage.save_transits(transits)


async def get_astro_transits(user_id: str) -> Optional[AstroTransits]:
    """Get astro transits by user ID"""
    return await _storage.get_transits(user_id)


async def delete_astro_transits(user_id: str) -> bool:
    """Delete astro transits"""
    return await _storage.delete_transits(user_id)


async def get_or_refresh_transits(
    user_id: str,
    birth: BirthDetails,
    now: datetime = None
) -> AstroTransits:
    """
    Get transits from storage or refresh if stale.
    
    Refresh conditions:
    1. No existing transits
    2. Existing transits older than TRANSITS_TTL_HOURS
    3. Date window doesn't cover required range
    
    Args:
        user_id: User identifier
        birth: Birth details for transit calculation
        now: Current datetime (default: utcnow)
        
    Returns:
        Fresh or cached AstroTransits
    """
    now = now or datetime.utcnow()
    today = now.date()
    
    # Calculate required date window
    required_from = today - timedelta(days=int(TRANSIT_PAST_YEARS * 365.25))
    required_to = today + timedelta(days=int(TRANSIT_FUTURE_YEARS * 365.25))
    
    # Try to get existing transits
    existing = await get_astro_transits(user_id)
    
    if existing:
        # Check if still valid
        age_hours = (now - existing.computed_at).total_seconds() / 3600
        covers_range = existing.from_date <= required_from and existing.to_date >= required_to
        
        if age_hours < TRANSITS_TTL_HOURS and covers_range:
            logger.debug(f"Using cached transits for user {user_id} (age: {age_hours:.1f}h)")
            return existing
        else:
            logger.info(f"Transits stale for user {user_id} (age: {age_hours:.1f}h, covers_range: {covers_range})")
    
    # Fetch fresh transits
    logger.info(f"Fetching fresh transits for user {user_id}")
    transits = await vedic_api_client.fetch_transits(
        birth=birth,
        user_id=user_id,
        from_date=required_from,
        to_date=required_to
    )
    
    # Save and return
    await save_astro_transits(transits)
    return transits


async def ensure_profile_and_transits(
    user_id: str,
    birth: BirthDetails,
    now: datetime = None
) -> tuple[AstroProfile, AstroTransits]:
    """
    Ensure user has both profile and transits.
    Creates profile if missing, refreshes transits if stale.
    
    Args:
        user_id: User identifier
        birth: Birth details
        now: Current datetime
        
    Returns:
        Tuple of (AstroProfile, AstroTransits)
    """
    now = now or datetime.utcnow()
    
    # Get or create profile
    profile = await get_astro_profile(user_id)
    if not profile:
        logger.info(f"Creating new profile for user {user_id}")
        profile = await vedic_api_client.fetch_full_profile(birth, user_id)
        await save_astro_profile(profile)
    
    # Get or refresh transits
    transits = await get_or_refresh_transits(user_id, birth, now)
    
    return profile, transits


# Future implementations:
# 
# class RedisAstroStorage(AstroStorage):
#     """Redis-backed storage for distributed deployments"""
#     def __init__(self, redis_url: str):
#         self.redis = redis.from_url(redis_url)
#     ...
#
# class MongoAstroStorage(AstroStorage):
#     """MongoDB-backed storage for persistent profiles"""
#     def __init__(self, mongo_url: str, db_name: str):
#         self.client = AsyncIOMotorClient(mongo_url)
#         self.db = self.client[db_name]
#     ...
