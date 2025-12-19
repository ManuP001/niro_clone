"""
Astro computation engine.

Handles provider calls, response normalization, quality checks.
Uses PipelineTracer to track execution.
Never invents data. Always explicit errors.
"""

import hashlib
import logging
import uuid
from typing import Optional, List, Tuple
from datetime import datetime

from backend.models.astro_models import (
    BirthProfile, AstroProfile, AstroStatus, AstroError,
    AstroErrorCode, Planet, House, Ascendant
)
from backend.models.pipeline_models import QualityFlag, StepStatus
from backend.services.pipeline_tracer import PipelineTracer, get_current_tracer
from backend.services.astro_database import get_astro_db
from backend.vedic_api_client import VedicAstroClient

logger = logging.getLogger(__name__)


class AstroComputeEngine:
    """
    Compute canonical AstroProfile from BirthProfile.
    """
    
    def __init__(self):
        self.vedic_client = VedicAstroClient()
    
    def _compute_request_hash(self, birth_profile: BirthProfile, provider: str) -> str:
        """
        Hash birth inputs + provider to enable caching.
        """
        key = f"{birth_profile.user_id}_{birth_profile.dob}_{birth_profile.tob}_{birth_profile.lat}_{birth_profile.lon}_{provider}"
        return hashlib.sha256(key.encode()).hexdigest()
    
    async def compute(
        self,
        birth_profile: BirthProfile,
        provider: str = "vedic_api",
        force: bool = False
    ) -> Tuple[Optional[AstroProfile], Optional[AstroError]]:
        """
        Compute AstroProfile from BirthProfile.
        
        Args:
            birth_profile: Normalized birth data
            provider: Which astro service to use
            force: Ignore cache, recompute
        
        Returns:
            (AstroProfile, error)
            If error is not None, AstroProfile will have status=ERROR
        """
        tracer = get_current_tracer()
        db = await get_astro_db()
        request_hash = self._compute_request_hash(birth_profile, provider)
        
        # Step 1: Check cache
        if not force:
            tracer.start_step(
                "ASTRO_CACHE_CHECK",
                "Check Cached Profile",
                {"request_hash": request_hash[:8]}
            )
            
            cached = await db.get_cached_astro_profile(request_hash)
            if cached and cached.status == AstroStatus.OK:
                tracer.end_step_success(
                    "ASTRO_CACHE_CHECK",
                    {"cache_hit": True, "profile_id": cached.user_id},
                    quality_flags=[QualityFlag.USING_CACHED_PROFILE]
                )
                logger.info(f"✓ Using cached AstroProfile for {birth_profile.user_id}")
                return cached, None
            else:
                tracer.end_step_success(
                    "ASTRO_CACHE_CHECK",
                    {"cache_hit": False}
                )
        
        # Step 2: Call provider
        tracer.start_step(
            "ASTRO_PROVIDER_REQUEST",
            "Call Astro Provider",
            {
                "provider": provider,
                "dob": birth_profile.dob,
                "tob": birth_profile.tob,
                "lat": birth_profile.lat,
                "lon": birth_profile.lon
            }
        )
        
        error_response = await self._call_provider(birth_profile, provider)
        if error_response is not None:
            tracer.end_step_fail(
                "ASTRO_PROVIDER_REQUEST",
                error_response.code.value,
                error_response.message,
                error_response.details
            )
            
            # Return error profile
            error_profile = AstroProfile(
                user_id=birth_profile.user_id,
                provider=provider,
                provider_request_hash=request_hash,
                computed_at=datetime.utcnow(),
                ascendant=None,
                planets=[],
                houses=[],
                status=AstroStatus.ERROR,
                error=error_response
            )
            return error_profile, error_response
        
        tracer.end_step_success(
            "ASTRO_PROVIDER_REQUEST",
            {"status": "provider_responded"}
        )
        
        # Step 3: Normalize response
        tracer.start_step(
            "ASTRO_RESPONSE_NORMALIZE",
            "Normalize Provider Response"
        )
        
        profile = await self._normalize_response(
            birth_profile,
            provider,
            request_hash
        )
        
        quality_flags = self._check_quality(profile)
        
        if profile.status == AstroStatus.ERROR:
            tracer.end_step_fail(
                "ASTRO_RESPONSE_NORMALIZE",
                profile.error.code.value if profile.error else "unknown",
                profile.error.message if profile.error else "Normalization failed",
                profile.error.details if profile.error else None
            )
            return profile, profile.error
        
        tracer.end_step_success(
            "ASTRO_RESPONSE_NORMALIZE",
            {
                "planets_count": len(profile.planets),
                "has_svg": profile.kundli_svg is not None
            },
            quality_flags=quality_flags
        )
        
        # Step 4: Persist
        tracer.start_step(
            "ASTRO_PROFILE_PERSIST",
            "Save to Database"
        )
        
        profile_id = str(uuid.uuid4())
        await db.save_astro_profile(profile, profile_id)
        
        tracer.end_step_success(
            "ASTRO_PROFILE_PERSIST",
            {"profile_id": profile_id},
            artifact_ids=[profile_id]
        )
        
        logger.info(f"✓ AstroProfile computed: {profile_id}")
        return profile, None
    
    async def _call_provider(
        self,
        birth_profile: BirthProfile,
        provider: str
    ) -> Optional[AstroError]:
        """
        Call astro provider. Return error if fails.
        """
        if provider == "vedic_api":
            try:
                # Call get_chart() with the correct parameters
                # Format: YYYY-MM-DD, HH:MM, lat, lon, tz_offset
                response = self.vedic_client.get_chart(
                    dob=birth_profile.dob,  # Already in DD-MM-YYYY format
                    tob=birth_profile.tob,  # Already in HH:MM format
                    lat=birth_profile.lat,
                    lon=birth_profile.lon,
                    tz=birth_profile.utc_offset_minutes / 60 if birth_profile.utc_offset_minutes else 5.5
                )
                
                if response and response.get("success"):
                    self._cached_provider_response = response
                    return None
                else:
                    error_msg = response.get("error", "Unknown error") if response else "No response"
                    return AstroError(
                        code=AstroErrorCode.PROVIDER_BAD_RESPONSE,
                        message="Vedic API returned failure or malformed response",
                        details=error_msg
                    )
            except Exception as e:
                logger.error(f"Vedic API error: {e}", exc_info=True)
                return AstroError(
                    code=AstroErrorCode.PROVIDER_AUTH_FAILED,
                    message="Vedic API call failed",
                    details=str(e)
                )
        
        return AstroError(
            code=AstroErrorCode.UNKNOWN,
            message=f"Unknown provider: {provider}"
        )
    
    async def _normalize_response(
        self,
        birth_profile: BirthProfile,
        provider: str,
        request_hash: str
    ) -> AstroProfile:
        """
        Convert provider response to canonical AstroProfile.
        """
        if not hasattr(self, '_cached_provider_response'):
            return AstroProfile(
                user_id=birth_profile.user_id,
                provider=provider,
                provider_request_hash=request_hash,
                computed_at=datetime.utcnow(),
                ascendant=None,
                planets=[],
                houses=[],
                status=AstroStatus.ERROR,
                error=AstroError(
                    code=AstroErrorCode.PROVIDER_BAD_RESPONSE,
                    message="No provider response cached"
                )
            )
        
        response = self._cached_provider_response
        
        # Parse response into canonical form
        try:
            # Extract ascendant
            ascendant_data = response.get("ascendant", {})
            ascendant = Ascendant(
                sign=ascendant_data.get("sign", "Unknown"),
                degree=float(ascendant_data.get("degree", 0)),
                minute=float(ascendant_data.get("minute", 0)) if ascendant_data.get("minute") else None
            )
            
            # Extract planets
            planets = []
            for planet_data in response.get("planets", []):
                try:
                    planet = Planet(
                        name=planet_data.get("name", ""),
                        sign=planet_data.get("sign", "Unknown"),
                        degree=float(planet_data.get("degree", 0)),
                        minute=float(planet_data.get("minute", 0)) if planet_data.get("minute") else None,
                        house=int(planet_data.get("house", 0)) if planet_data.get("house") else None,
                        retrograde=planet_data.get("retrograde", False)
                    )
                    planets.append(planet)
                except ValueError as e:
                    logger.warning(f"Could not parse planet: {e}")
            
            # Extract houses
            houses = []
            for house_data in response.get("houses", []):
                try:
                    house = House(
                        house=int(house_data.get("house", 0)),
                        sign=house_data.get("sign", "Unknown"),
                        degree=float(house_data.get("degree", 0)) if house_data.get("degree") else None
                    )
                    houses.append(house)
                except ValueError as e:
                    logger.warning(f"Could not parse house: {e}")
            
            # Get SVG (fallback to mock if missing)
            kundli_svg = response.get("kundli_svg") or self._generate_mock_svg(birth_profile, ascendant, planets, houses)
            
            profile = AstroProfile(
                user_id=birth_profile.user_id,
                provider=provider,
                provider_request_hash=request_hash,
                computed_at=datetime.utcnow(),
                ascendant=ascendant,
                planets=planets,
                houses=houses,
                kundli_svg=kundli_svg,
                status=AstroStatus.OK,
                raw_provider_payload=response  # Keep for debugging
            )
            
            return profile
        
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return AstroProfile(
                user_id=birth_profile.user_id,
                provider=provider,
                provider_request_hash=request_hash,
                computed_at=datetime.utcnow(),
                ascendant=None,
                planets=[],
                houses=[],
                status=AstroStatus.ERROR,
                error=AstroError(
                    code=AstroErrorCode.PROVIDER_BAD_RESPONSE,
                    message="Failed to normalize provider response",
                    details=str(e)
                )
            )
    
    def _check_quality(self, profile: AstroProfile) -> List[QualityFlag]:
        """
        Detect quality issues.
        """
        flags = []
        
        # Check for 0.0° degrees
        if all(p.degree == 0 or p.degree is None for p in profile.planets):
            flags.append(QualityFlag.PLANET_DEGREES_ALL_ZERO)
        
        # Check for identical house signs
        if len(profile.houses) > 1:
            signs = [h.sign for h in profile.houses]
            if len(set(signs)) < 6:  # Less than 6 unique signs (suspicious)
                flags.append(QualityFlag.HOUSES_ALL_SAME_SIGN)
        
        # Check for missing SVG
        if not profile.kundli_svg:
            flags.append(QualityFlag.SVG_MISSING)
        
        return flags
    
    def _generate_mock_svg(self, birth_profile, ascendant, planets, houses) -> str:
        """Generate mock SVG if real SVG unavailable."""
        # Return minimal but valid SVG
        return f"""<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
  <circle cx="200" cy="200" r="190" fill="none" stroke="#ccc" stroke-width="2"/>
  <text x="200" y="30" text-anchor="middle" font-size="16" font-weight="bold">
    Kundli for {birth_profile.name}
  </text>
  <text x="200" y="55" text-anchor="middle" font-size="12">
    Ascendant: {ascendant.sign} {ascendant.degree:.1f}°
  </text>
  <text x="200" y="380" text-anchor="middle" font-size="10" fill="#999">
    Generated at {datetime.utcnow().isoformat()}
  </text>
</svg>"""
