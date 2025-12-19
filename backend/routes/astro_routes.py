"""
Refactored astrology endpoints.

Single source of truth: Backend computes, persists, serves canonical AstroProfile.
No frontend provider calls. No silent fallbacks. Explicit errors.
"""

import uuid
import logging
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from datetime import datetime

from backend.models.astro_models import (
    OnboardingCompleteRequest, OnboardingCompleteResponse,
    BirthProfile, AstroProfile, AstroProfileResponse,
    LLMContext, PersonalityHighlight,
    RecomputeAstroRequest
)
from backend.models.pipeline_models import (
    PipelineTrace, DebugPipelineTraceResponse, StepStatus
)
from backend.services.astro_database import get_astro_db
from backend.services.pipeline_tracer import PipelineTracer, set_current_tracer, get_current_tracer
from backend.services.location_normalizer import LocationNormalizer
from backend.services.astro_compute_engine import AstroComputeEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/astro", tags=["astrology"])

# Services
location_normalizer = LocationNormalizer()
compute_engine = AstroComputeEngine()


@router.post("/onboarding/complete", response_model=OnboardingCompleteResponse)
async def complete_onboarding(
    request: OnboardingCompleteRequest,
    authorization: Optional[str] = Header(None)
):
    """
    User submits birth details to complete onboarding.
    
    Pipeline:
    1. Create BirthProfile (raw input)
    2. Normalize location (place_text → lat/lon/tz)
    3. Compute AstroProfile (provider call)
    4. Persist both
    5. Return trace
    """
    # Get user from token (simplified - use real auth)
    user_id = "test_user"  # TODO: Extract from JWT
    
    # Create tracer for this run
    tracer = PipelineTracer(user_id)
    set_current_tracer(tracer)
    
    db = await get_astro_db()
    
    try:
        # Step 1: Onboarding capture
        tracer.start_step(
            "ONBOARDING_CAPTURE",
            "Capture Birth Details",
            {
                "name": request.name,
                "dob": request.dob,
                "place": request.place_text
            }
        )
        
        # Create BirthProfile
        birth_profile = BirthProfile(
            user_id=user_id,
            name=request.name,
            dob=request.dob,
            tob=request.tob,
            place_text=request.place_text
        )
        
        birth_profile_id = str(uuid.uuid4())
        await db.save_birth_profile(birth_profile, birth_profile_id)
        
        tracer.end_step_success(
            "ONBOARDING_CAPTURE",
            {"birth_profile_id": birth_profile_id},
            artifact_ids=[birth_profile_id]
        )
        
        # Step 2: Location normalization
        tracer.start_step(
            "LOCATION_NORMALIZE",
            "Normalize Location",
            {"place_text": request.place_text}
        )
        
        error, normalized_profile = await location_normalizer.normalize(birth_profile)
        if error:
            tracer.end_step_fail(
                "LOCATION_NORMALIZE",
                error.code.value,
                error.message,
                error.details
            )
            
            trace = tracer.build_trace(
                overall_status=StepStatus.FAILED,
                overall_quality_flags=[]
            )
            await db.save_pipeline_trace(trace)
            
            return OnboardingCompleteResponse(
                birth_profile_id=birth_profile_id,
                astro_profile_id="",
                status="error",
                error=error,
                message=f"Location normalization failed: {error.message}"
            )
        
        # Update UTC offset
        utc_offset = location_normalizer.get_utc_offset_minutes(
            normalized_profile.timezone,
            normalized_profile.dob
        )
        normalized_profile.utc_offset_minutes = utc_offset
        
        tracer.end_step_success(
            "LOCATION_NORMALIZE",
            {
                "lat": normalized_profile.lat,
                "lon": normalized_profile.lon,
                "timezone": normalized_profile.timezone,
                "utc_offset_minutes": utc_offset
            }
        )
        
        # Step 3-6: Compute astro profile
        astro_profile, astro_error = await compute_engine.compute(
            normalized_profile,
            provider="vedic_api",
            force=False
        )
        
        if astro_error:
            # Still persist the error profile
            astro_profile_id = str(uuid.uuid4())
            await db.save_astro_profile(astro_profile, astro_profile_id)
            
            trace = tracer.build_trace(
                overall_status=StepStatus.FAILED,
                overall_quality_flags=[],
                final_astro_profile_id=astro_profile_id
            )
            await db.save_pipeline_trace(trace)
            
            return OnboardingCompleteResponse(
                birth_profile_id=birth_profile_id,
                astro_profile_id=astro_profile_id,
                status="error",
                error=astro_error,
                message=f"Astro computation failed: {astro_error.message}"
            )
        
        astro_profile_id = str(uuid.uuid4())
        await db.save_astro_profile(astro_profile, astro_profile_id)
        
        # Build trace
        trace = tracer.build_trace(
            overall_status=StepStatus.SUCCESS,
            overall_quality_flags=[],
            final_astro_profile_id=astro_profile_id
        )
        await db.save_pipeline_trace(trace)
        
        logger.info(f"✓ Onboarding complete: user={user_id}, trace={trace.run_id[:8]}")
        
        return OnboardingCompleteResponse(
            birth_profile_id=birth_profile_id,
            astro_profile_id=astro_profile_id,
            status="ok",
            error=None,
            message="Onboarding completed successfully"
        )
    
    except Exception as e:
        logger.error(f"❌ Onboarding error: {e}")
        
        trace = tracer.build_trace(
            overall_status=StepStatus.FAILED,
            overall_quality_flags=[]
        )
        await db.save_pipeline_trace(trace)
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=AstroProfileResponse)
async def get_astro_profile(
    authorization: Optional[str] = Header(None)
):
    """
    Get user's current astro profile.
    Reads only from persisted data - no provider calls.
    """
    user_id = "test_user"  # TODO: Extract from JWT
    
    db = await get_astro_db()
    profile = await db.get_astro_profile_by_user(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="No astro profile found")
    
    return AstroProfileResponse(
        data=profile,
        cached=False,  # TODO: Check if it's cached
        served_at=datetime.utcnow()
    )


@router.get("/kundli-svg")
async def get_kundli_svg(
    authorization: Optional[str] = Header(None)
):
    """
    Get SVG for Kundli tab rendering.
    Explicit error if missing (no fallback).
    """
    user_id = "test_user"  # TODO: Extract from JWT
    
    db = await get_astro_db()
    profile = await db.get_astro_profile_by_user(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="No astro profile found")
    
    if not profile.kundli_svg:
        raise HTTPException(
            status_code=422,
            detail="SVG not available - astro computation may have failed"
        )
    
    return {
        "svg": profile.kundli_svg,
        "provider": profile.provider,
        "computed_at": profile.computed_at
    }


@router.post("/recompute")
async def recompute_astro(
    request: RecomputeAstroRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Force recomputation of astro profile with potentially different provider.
    """
    user_id = "test_user"  # TODO: Extract from JWT
    
    tracer = PipelineTracer(user_id)
    set_current_tracer(tracer)
    
    db = await get_astro_db()
    birth_profile = await db.get_birth_profile_by_user(user_id)
    
    if not birth_profile:
        raise HTTPException(status_code=404, detail="Birth profile not found")
    
    # Recompute with new provider (or same if not specified)
    provider = request.provider or "vedic_api"
    astro_profile, error = await compute_engine.compute(
        birth_profile,
        provider=provider,
        force=True  # Force recomputation
    )
    
    if error:
        trace = tracer.build_trace(overall_status=StepStatus.FAILED)
        await db.save_pipeline_trace(trace)
        raise HTTPException(status_code=422, detail=error.message)
    
    astro_profile_id = str(uuid.uuid4())
    await db.save_astro_profile(astro_profile, astro_profile_id)
    
    trace = tracer.build_trace(
        overall_status=StepStatus.SUCCESS,
        final_astro_profile_id=astro_profile_id
    )
    await db.save_pipeline_trace(trace)
    
    return {
        "status": "ok",
        "astro_profile_id": astro_profile_id,
        "trace_id": trace.run_id
    }


@router.get("/chat-context")
async def get_chat_context(
    authorization: Optional[str] = Header(None)
):
    """
    Get LLM context derived from persisted AstroProfile.
    This is what welcome message + chat use (not raw provider data).
    """
    user_id = "test_user"  # TODO: Extract from JWT
    
    db = await get_astro_db()
    astro_profile = await db.get_astro_profile_by_user(user_id)
    birth_profile = await db.get_birth_profile_by_user(user_id)
    
    if not astro_profile or not birth_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Build LLMContext from astro profile
    sun_sign = next((p.sign for p in astro_profile.planets if p.name == "Sun"), "Unknown")
    moon_sign = next((p.sign for p in astro_profile.planets if p.name == "Moon"), "Unknown")
    
    birth_summary = f"Born {birth_profile.dob} at {birth_profile.tob} in {birth_profile.place_text}"
    
    # Build personality highlights from astro
    highlights = [
        PersonalityHighlight(
            title="Sun Sign Influence",
            description=f"Your core identity is shaped by {sun_sign}",
            astrological_basis=f"Sun in {sun_sign}"
        ),
        PersonalityHighlight(
            title="Emotional Nature",
            description=f"Your emotions are governed by {moon_sign}",
            astrological_basis=f"Moon in {moon_sign}"
        ),
        PersonalityHighlight(
            title="Ascendant Expression",
            description=f"You appear as {astro_profile.ascendant.sign} to the world",
            astrological_basis=f"Ascendant in {astro_profile.ascendant.sign}"
        )
    ]
    
    context = LLMContext(
        user_id=user_id,
        user_name=birth_profile.name,
        birth_summary=birth_summary,
        personality_highlights=highlights,
        sun_sign=sun_sign,
        moon_sign=moon_sign,
        ascendant_sign=astro_profile.ascendant.sign,
        guardrails=[
            "Do not invent astro data that is missing",
            "Do not make predictions beyond the scope of birth chart analysis",
            "Flag any missing planets or houses explicitly",
            "Use only the provided placements and aspects"
        ],
        profile_id=user_id  # In real system, use actual profile ID
    )
    
    return context
