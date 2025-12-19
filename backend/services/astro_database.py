"""
Database layer for persistent astrology data.

SQLite with async support via aiosqlite.
"""

import aiosqlite
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from backend.models.astro_models import BirthProfile, AstroProfile, AstroStatus
from backend.models.pipeline_models import PipelineTrace

logger = logging.getLogger(__name__)


class AstroDatabase:
    """Handle birth profiles and astro profiles."""
    
    def __init__(self, db_path: str = "astro_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def init(self):
        """Create tables if they don't exist."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS birth_profiles (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    dob TEXT NOT NULL,
                    tob TEXT NOT NULL,
                    place_text TEXT NOT NULL,
                    lat REAL,
                    lon REAL,
                    timezone TEXT,
                    utc_offset_minutes INTEGER,
                    created_at TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    UNIQUE(user_id, dob, tob)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS astro_profiles (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    birth_profile_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    provider_request_hash TEXT,
                    computed_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    FOREIGN KEY (birth_profile_id) REFERENCES birth_profiles(id),
                    UNIQUE(user_id, provider_request_hash)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_traces (
                    run_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    data_json TEXT NOT NULL
                )
            """)
            
            await db.commit()
            logger.info("✓ Astro database initialized")
    
    async def save_birth_profile(self, profile: BirthProfile, profile_id: str) -> str:
        """Save birth profile. Return ID."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute("""
                INSERT OR REPLACE INTO birth_profiles
                (id, user_id, name, dob, tob, place_text, lat, lon, timezone, utc_offset_minutes, created_at, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                profile.user_id,
                profile.name,
                profile.dob,
                profile.tob,
                profile.place_text,
                profile.lat,
                profile.lon,
                profile.timezone,
                profile.utc_offset_minutes,
                profile.created_at.isoformat(),
                profile.json()
            ))
            await db.commit()
            logger.info(f"✓ BirthProfile saved: {profile_id}")
            return profile_id
    
    async def get_birth_profile(self, profile_id: str) -> Optional[BirthProfile]:
        """Load birth profile."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            cursor = await db.execute(
                "SELECT data_json FROM birth_profiles WHERE id = ?",
                (profile_id,)
            )
            row = await cursor.fetchone()
            if row:
                return BirthProfile.parse_raw(row[0])
        return None
    
    async def get_birth_profile_by_user(self, user_id: str) -> Optional[BirthProfile]:
        """Load latest birth profile for user."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            cursor = await db.execute(
                "SELECT data_json FROM birth_profiles WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            row = await cursor.fetchone()
            if row:
                return BirthProfile.parse_raw(row[0])
        return None
    
    async def save_astro_profile(self, profile: AstroProfile, profile_id: str) -> str:
        """Save astro profile. Return ID."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute("""
                INSERT OR REPLACE INTO astro_profiles
                (id, user_id, birth_profile_id, provider, provider_request_hash, computed_at, status, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                profile.user_id,
                "",  # Will be linked if needed
                profile.provider,
                profile.provider_request_hash,
                profile.computed_at.isoformat(),
                profile.status.value,
                profile.json()
            ))
            await db.commit()
            logger.info(f"✓ AstroProfile saved: {profile_id}")
            return profile_id
    
    async def get_astro_profile(self, profile_id: str) -> Optional[AstroProfile]:
        """Load astro profile."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            cursor = await db.execute(
                "SELECT data_json FROM astro_profiles WHERE id = ?",
                (profile_id,)
            )
            row = await cursor.fetchone()
            if row:
                return AstroProfile.parse_raw(row[0])
        return None
    
    async def get_astro_profile_by_user(self, user_id: str) -> Optional[AstroProfile]:
        """Load latest astro profile for user."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            cursor = await db.execute(
                "SELECT data_json FROM astro_profiles WHERE user_id = ? ORDER BY computed_at DESC LIMIT 1",
                (user_id,)
            )
            row = await cursor.fetchone()
            if row:
                return AstroProfile.parse_raw(row[0])
        return None
    
    async def get_cached_astro_profile(self, provider_request_hash: str) -> Optional[AstroProfile]:
        """Get cached profile by request hash (compute-once)."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            cursor = await db.execute(
                "SELECT data_json FROM astro_profiles WHERE provider_request_hash = ? ORDER BY computed_at DESC LIMIT 1",
                (provider_request_hash,)
            )
            row = await cursor.fetchone()
            if row:
                logger.info(f"✓ Using cached AstroProfile: {provider_request_hash[:8]}")
                return AstroProfile.parse_raw(row[0])
        return None
    
    async def save_pipeline_trace(self, trace: PipelineTrace) -> str:
        """Save pipeline trace for debugging."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            await db.execute("""
                INSERT OR REPLACE INTO pipeline_traces
                (run_id, user_id, created_at, data_json)
                VALUES (?, ?, ?, ?)
            """, (
                trace.run_id,
                trace.user_id,
                trace.created_at.isoformat(),
                trace.json()
            ))
            await db.commit()
            logger.info(f"✓ PipelineTrace saved: {trace.run_id}")
            return trace.run_id
    
    async def get_pipeline_trace(self, run_id: str) -> Optional[PipelineTrace]:
        """Load pipeline trace."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            cursor = await db.execute(
                "SELECT data_json FROM pipeline_traces WHERE run_id = ?",
                (run_id,)
            )
            row = await cursor.fetchone()
            if row:
                return PipelineTrace.parse_raw(row[0])
        return None
    
    async def get_latest_pipeline_trace(self, user_id: str) -> Optional[PipelineTrace]:
        """Load latest pipeline trace for user."""
        async with aiosqlite.connect(str(self.db_path)) as db:
            cursor = await db.execute(
                "SELECT data_json FROM pipeline_traces WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            row = await cursor.fetchone()
            if row:
                return PipelineTrace.parse_raw(row[0])
        return None


# Global instance
_db_instance: Optional[AstroDatabase] = None


async def get_astro_db() -> AstroDatabase:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = AstroDatabase("backend/data/astro_data.db")
        await _db_instance.init()
    return _db_instance
