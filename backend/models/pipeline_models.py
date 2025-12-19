"""
Pipeline observability models.

Tracks every step of the astro computation + data flow.
Powers the Match → Checklist debug tab.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class StepStatus(str, Enum):
    """Status of a pipeline step."""
    NOT_STARTED = "not_started"
    STARTED = "started"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class QualityFlag(str, Enum):
    """Quality issues detected during pipeline."""
    PLANET_DEGREES_ALL_ZERO = "planet_degrees_all_zero"
    HOUSES_ALL_SAME_SIGN = "houses_all_same_sign"
    SVG_MISSING = "svg_missing"
    FALLBACK_USED = "fallback_used"
    USING_CACHED_PROFILE = "using_cached_profile"
    PROFILE_INCOMPLETE = "profile_incomplete"
    PROVIDER_DEGRADED = "provider_degraded"
    GEOCODING_APPROXIMATE = "geocoding_approximate"


class PipelineStep(BaseModel):
    """
    Single step in the astro pipeline.
    """
    step_id: str  # e.g., "ONBOARDING_CAPTURE", "LOCATION_NORMALIZE"
    display_name: str  # "Onboarding Capture", "Location Normalization"
    status: StepStatus
    
    # Timing
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_ms: Optional[int] = None  # Computed from started/ended
    
    # Data
    inputs: Dict[str, Any] = Field(default_factory=dict)  # Sanitized (no secrets)
    outputs: Dict[str, Any] = Field(default_factory=dict)  # Sanitized
    
    # Error tracking
    error: Optional[Dict[str, str]] = None  # {"code": "...", "message": "..."}
    
    # Artifacts
    artifact_ids: List[str] = Field(default_factory=list)
    # References to created objects (profile IDs, file paths, etc.)
    
    # Quality
    quality_flags: List[QualityFlag] = Field(default_factory=list)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class PipelineTrace(BaseModel):
    """
    Complete execution trace of one astro pipeline run.
    """
    run_id: str  # UUID
    user_id: str
    created_at: datetime
    
    # All steps in order
    steps: List[PipelineStep] = Field(default_factory=list)
    
    # Overall status
    overall_status: StepStatus
    overall_quality_flags: List[QualityFlag] = Field(default_factory=list)
    
    # Summary
    total_duration_ms: int
    success: bool  # All critical steps succeeded
    degraded: bool  # Some non-critical steps failed or flagged
    
    # Final output reference
    final_astro_profile_id: Optional[str] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
    
    def get_step(self, step_id: str) -> Optional[PipelineStep]:
        """Get step by ID."""
        return next((s for s in self.steps if s.step_id == step_id), None)


class DebugPipelineTraceResponse(BaseModel):
    """Return pipeline trace for debug viewing."""
    trace: PipelineTrace
    rendered_at: datetime
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
