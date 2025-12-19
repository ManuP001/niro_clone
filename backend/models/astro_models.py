"""
Canonical astrology domain models - Single Source of Truth.

These models represent the exact contract between:
- Backend astro computation
- Frontend UI rendering
- LLM context building
- Pipeline observability

No defaults. No guessing. Explicit errors only.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class AstroStatus(str, Enum):
    """Status of astrology computation."""
    OK = "ok"
    ERROR = "error"
    DEGRADED = "degraded"  # Partial data, but usable


class AstroErrorCode(str, Enum):
    """Structured error codes for astro failures."""
    PROVIDER_AUTH_FAILED = "provider_auth_failed"
    PROVIDER_RATE_LIMIT = "provider_rate_limit"
    PROVIDER_BAD_RESPONSE = "provider_bad_response"
    GEOCODE_FAILED = "geocode_failed"
    PROFILE_INCOMPLETE = "profile_incomplete"
    INVALID_BIRTH_DATA = "invalid_birth_data"
    UNKNOWN = "unknown"


class AstroError(BaseModel):
    """Structured error information."""
    code: AstroErrorCode
    message: str
    details: Optional[str] = None


class BirthProfile(BaseModel):
    """
    Raw + normalized birth input data.
    This is created at onboarding, never modified.
    """
    user_id: str
    name: str
    dob: str  # YYYY-MM-DD
    tob: str  # HH:MM in 24h format
    place_text: str
    lat: Optional[float] = None  # Computed from place_text
    lon: Optional[float] = None  # Computed from place_text
    timezone: Optional[str] = None  # IANA timezone
    utc_offset_minutes: Optional[int] = None  # For exact moment
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Planet(BaseModel):
    """
    Single planet placement in the zodiac.
    """
    name: str  # Sun, Moon, Mars, Mercury, etc.
    sign: str  # Aries, Taurus, ... Pisces
    degree: float  # 0.0-29.999... (NOT allowing 0.0 default!)
    minute: Optional[float] = None  # 0.0-59.999...
    second: Optional[float] = None  # 0.0-59.999...
    house: Optional[int] = None  # 1-12
    retrograde: bool = False
    
    @validator('degree')
    def degree_not_zero_default(cls, v):
        """Catch obviously wrong degrees."""
        if v is None:
            raise ValueError("degree cannot be None")
        return v


class House(BaseModel):
    """
    Single house cusp definition (12 total).
    """
    house: int  # 1-12
    sign: str  # Aries, Taurus, ... Pisces
    degree: Optional[float] = None  # Cusp degree
    minute: Optional[float] = None
    
    @validator('house')
    def house_in_range(cls, v):
        if not 1 <= v <= 12:
            raise ValueError("house must be 1-12")
        return v


class Ascendant(BaseModel):
    """
    Ascendant (Lagna) - first house cusp.
    """
    sign: str  # Aries, Taurus, ... Pisces
    degree: float
    minute: Optional[float] = None
    house: int = 1  # Always house 1


class AstroProfile(BaseModel):
    """
    Provider-agnostic canonical astrology profile.
    
    This is the ONLY object the UI, LLM, and debug tools read.
    Computed once per BirthProfile, cached, never auto-fallback.
    """
    user_id: str
    provider: str  # "vedic_api", "gemini_calc", "mock", etc.
    provider_request_hash: Optional[str] = None  # SHA256 of input
    computed_at: datetime
    
    # Core astro data (all explicit, no defaults)
    ascendant: Ascendant
    planets: List[Planet]  # 9-10 planets minimum
    houses: List[House]  # Exactly 12
    
    # SVG rendering
    kundli_svg: Optional[str] = None
    
    # Status
    status: AstroStatus
    error: Optional[AstroError] = None
    
    # Debugging
    raw_provider_payload: Optional[dict] = None  # Only if debugging enabled
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class PersonalityHighlight(BaseModel):
    """One personality trait derived from astro."""
    title: str
    description: str
    astrological_basis: str  # "Sun in Leo", "Moon aspects", etc.


class LLMContext(BaseModel):
    """
    Derived context for LLM chat/welcome generation.
    Built only from persisted AstroProfile - never invented.
    """
    user_id: str
    user_name: str
    birth_summary: str  # "Born June 21, 1990 at 14:30 in New York"
    
    # Personality insights (max 3)
    personality_highlights: List[PersonalityHighlight]
    
    # Key placements
    sun_sign: str
    moon_sign: str
    ascendant_sign: str
    
    # Guardrails for LLM
    guardrails: List[str] = Field(default_factory=list)
    # e.g., "Do not invent predictions", "Do not invent missing planets"
    
    # Built from this profile
    profile_id: str  # reference to AstroProfile._id
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# Request/Response schemas for API contracts

class OnboardingCompleteRequest(BaseModel):
    """User submits birth details to complete onboarding."""
    name: str
    dob: str  # YYYY-MM-DD
    tob: str  # HH:MM
    place_text: str


class OnboardingCompleteResponse(BaseModel):
    """Response after onboarding completion."""
    birth_profile_id: str
    astro_profile_id: str
    status: AstroStatus
    error: Optional[AstroError] = None
    message: str


class RecomputeAstroRequest(BaseModel):
    """Force recomputation of astro profile."""
    provider: Optional[str] = None  # Use different provider


class AstroProfileResponse(BaseModel):
    """Return persisted astro profile."""
    data: AstroProfile
    cached: bool  # Was this cached?
    served_at: datetime
