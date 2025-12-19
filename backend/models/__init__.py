"""
Backend data models package.

Contains both legacy models (User, Transaction, etc.) and new astro models.
"""

# Legacy models (from original models.py, now in legacy_models.py)
from backend.models.legacy_models import (
    User, UserCreate,
    Transaction, TransactionCreate, MockPaymentVerify,
    Report, ReportRequest, ReportResponse, ReportStatus,
    FollowUpQuestion, FollowUpResponse,
    PriceConfig, PriceUpdate, ReportType, PaymentStatus,
    UserBirthDetails, Gender, VisualData
)

# New astro models
from backend.models.astro_models import (
    BirthProfile,
    AstroProfile,
    Ascendant,
    Planet,
    House,
    LLMContext,
    PersonalityHighlight,
    OnboardingCompleteRequest,
    OnboardingCompleteResponse,
    AstroProfileResponse,
    RecomputeAstroRequest,
    AstroErrorCode,
    AstroError
)

from backend.models.pipeline_models import (
    PipelineTrace,
    PipelineStep,
    StepStatus,
    QualityFlag,
    DebugPipelineTraceResponse
)

__all__ = [
    # Legacy models
    "User",
    "UserCreate",
    "UserBirthDetails",
    "Gender",
    "Transaction",
    "TransactionCreate",
    "MockPaymentVerify",
    "Report",
    "ReportRequest",
    "ReportResponse",
    "ReportStatus",
    "FollowUpQuestion",
    "FollowUpResponse",
    "PriceConfig",
    "PriceUpdate",
    "ReportType",
    "PaymentStatus",
    "VisualData",
    # Astro models
    "BirthProfile",
    "AstroProfile",
    "Ascendant",
    "Planet",
    "House",
    "LLMContext",
    "PersonalityHighlight",
    "OnboardingCompleteRequest",
    "OnboardingCompleteResponse",
    "AstroProfileResponse",
    "RecomputeAstroRequest",
    "AstroErrorCode",
    "AstroError",
    # Pipeline models
    "PipelineTrace",
    "PipelineStep",
    "StepStatus",
    "QualityFlag",
    "DebugPipelineTraceResponse",
]
