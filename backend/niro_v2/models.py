"""NIRO V2 Data Models

Strict schemas for packages, remedies, recommendations, and plans.
All IDs must come from catalog - no invented offerings.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid


# ============================================================================
# ENUMS
# ============================================================================

class Topic(str, Enum):
    CAREER = "career"
    RELATIONSHIPS = "relationships"
    MONEY = "money"
    HEALTH = "health"
    FAMILY = "family"
    CHILDREN = "children"


class Branch(str, Enum):
    REMEDIES_ONLY = "remedies_only"
    CONSULT_ONLY = "consult_only"
    COMBINED = "combined"


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionOwnership(str, Enum):
    ME = "me"
    FAMILY = "family"
    BOTH = "both"


class RemedyCategory(str, Enum):
    ASTROLOGICAL = "astrological"
    SPIRITUAL = "spiritual"
    HEALING = "healing"


class PlanStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class FulfillmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


# ============================================================================
# CONSULT POLICY
# ============================================================================

class LiveSessionPolicy(BaseModel):
    """Live session limits within consultation"""
    max_minutes_per_session: int = 60
    sessions_per_week_limit: int = 1
    total_sessions_included: int = 8


class ChatPolicy(BaseModel):
    """Chat support policy"""
    is_unlimited: bool = True
    sla_hours: int = 12
    availability: str = "within_validity"


class ConsultPolicy(BaseModel):
    """Defines 'unlimited consultation' guardrails per package"""
    policy_id: str
    name: str
    validity_weeks: int
    live_sessions: LiveSessionPolicy
    chat: ChatPolicy
    fair_use_summary: str
    catalog_version: str = "2025.01.15.001"


# ============================================================================
# SELF-GUIDED ITEMS
# ============================================================================

class ItemSchedule(BaseModel):
    """Scheduling for self-guided items"""
    day_start: int
    day_end: int
    is_repeating: bool = False
    repeat_frequency: Optional[str] = None  # "daily", "weekly", "twice_weekly"


class SelfGuidedItem(BaseModel):
    """Topic-specific self-guided solution"""
    item_id: str
    name: str
    type: str  # decision_framework, timing_analysis, action_plan, etc.
    description: str
    content_type: str  # interactive_tool, guided_content, audio, video, checklist
    duration_minutes: int
    schedule: ItemSchedule
    content_url: Optional[str] = None
    instructions_md: Optional[str] = None


# ============================================================================
# ADDITIONAL SERVICES
# ============================================================================

class AdditionalService(BaseModel):
    """Extra services bundled with package"""
    service_id: str
    name: str
    type: str  # career_report, forecast_3month, emergency_consult, etc.
    description: str
    delivery_type: str  # pdf_report, live_session, async_delivery
    delivery_timeline: str  # "Within 48 hours", "Scheduled session"


# ============================================================================
# PACKAGE
# ============================================================================

class PackageTargeting(BaseModel):
    """Package targeting and ranking metadata"""
    urgency_fit: List[str] = ["low", "medium", "high"]
    priority_score: int = 50
    compatible_concerns: List[str] = []


class Package(BaseModel):
    """Complete package definition"""
    package_id: str
    slug: str
    name: str
    tagline: str
    description: str
    hero_image_url: Optional[str] = None
    
    # Categorization
    topic: Topic
    branch: Branch
    
    # Duration & commitment
    duration_weeks: int
    daily_commitment_minutes: int
    
    # Pricing (no starter packs - meaningful prices only)
    price_inr: int
    
    # Section 3b: Consultation
    includes_consultation: bool
    consult_policy_id: Optional[str] = None
    
    # Section 3a: Self-guided solutions
    self_guided_items: List[SelfGuidedItem] = []
    
    # Section 3c: Additional services
    additional_services: List[AdditionalService] = []
    
    # Section 3d: Suggested remedy add-ons (IDs only)
    suggested_remedy_ids: List[str] = []
    
    # Targeting
    targeting: PackageTargeting = PackageTargeting()
    
    # Status
    is_active: bool = True
    catalog_version: str = "2025.01.15.001"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# REMEDY ADD-ON
# ============================================================================

class Remedy(BaseModel):
    """Paid add-on remedy"""
    remedy_id: str
    slug: str
    name: str
    description: str
    
    # Category
    category: RemedyCategory
    sub_type: str  # gemstone, yantra, puja, crystal, reiki, etc.
    
    # Pricing
    price_inr: int
    price_type: str = "fixed"  # fixed, range
    price_range_min: Optional[int] = None
    price_range_max: Optional[int] = None
    
    # Details
    what_included: List[str] = []
    how_it_works: List[str] = []
    delivery_timeline: str = "48 hours"
    fulfillment_type: str = "hybrid"  # digital, physical, service, hybrid
    requires_consultation: bool = False
    
    # Compatibility
    compatible_topics: List[str] = []
    compatible_concerns: List[str] = []
    
    # Display
    image_url: Optional[str] = None
    is_active: bool = True
    catalog_version: str = "2025.01.15.001"


# ============================================================================
# SITUATION INTAKE
# ============================================================================

class SituationIntake(BaseModel):
    """User's situation intake from onboarding"""
    intake_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    topic: Topic
    urgency: Urgency
    desired_outcome: str
    decision_ownership: DecisionOwnership
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# CHAT HANDOFF
# ============================================================================

class BirthDetails(BaseModel):
    """User's birth details for astro calculations"""
    name: str
    dob: str  # ISO format
    tob: str  # HH:MM
    tob_known: bool = True
    place: str
    lat: float
    lon: float
    timezone: str = "Asia/Kolkata"


class ChartSummary(BaseModel):
    """Key chart insights for context"""
    ascendant: Optional[str] = None
    moon_sign: Optional[str] = None
    current_dasha: Optional[str] = None
    key_transits: List[str] = []


class UserContext(BaseModel):
    """Full user context for chat handoff"""
    name: str
    birth_details: BirthDetails
    chart_summary: Optional[ChartSummary] = None


class CatalogPackageContext(BaseModel):
    """Minimal package info for chat context"""
    package_id: str
    topic: str
    branch: str
    price_inr: int
    has_consultation: bool
    duration_weeks: int
    priority_score: int


class CatalogRemedyContext(BaseModel):
    """Minimal remedy info for chat context"""
    remedy_id: str
    category: str
    price_inr: int
    compatible_topics: List[str]


class CatalogContext(BaseModel):
    """Catalog context sent to chat engine"""
    available_packages: List[CatalogPackageContext]
    available_remedies: List[CatalogRemedyContext]


class IntakeSignals(BaseModel):
    """Intake signals from onboarding"""
    topic: str
    urgency: str
    desired_outcome: str
    decision_ownership: str


class HandoffVersions(BaseModel):
    """Version tracking for audit"""
    prompt_version: str = "v2.0.0"
    catalog_version: str = "2025.01.15.001"


class ChatHandoffPayload(BaseModel):
    """Complete handoff payload to chat engine"""
    session_id: str
    user_id: str
    mode: str = "PACKAGE_RECOMMENDATION"
    versions: HandoffVersions
    user_context: UserContext
    intake_signals: IntakeSignals
    catalog_context: CatalogContext
    instructions: Dict[str, str] = {
        "step_a": "Extract structured situation signals from conversation",
        "step_b": "Recommend ONLY from package_ids and remedy_ids provided in catalog_context",
        "constraint": "DO NOT invent or suggest any offering not in catalog_context"
    }


# ============================================================================
# CHAT RESPONSE (FROM CHAT ENGINE)
# ============================================================================

class StepAExtraction(BaseModel):
    """Extracted situation signals from chat"""
    situation_summary: str
    topic_confirmed: str
    urgency_level: str
    sentiment: str = "neutral"
    key_concerns: List[str] = []
    wants_consultation: bool = False
    specific_needs: List[str] = []


class StepBRecommendation(BaseModel):
    """Recommendation output - IDs only"""
    branch: str
    primary_package_id: str
    alternative_package_ids: List[str] = []
    suggested_remedy_ids: List[str] = []
    reasoning: str


class ChartInsight(BaseModel):
    """Factual chart insight for trust step"""
    insight: str
    relevance: str


class TrustElements(BaseModel):
    """Trust-building elements"""
    personalized_observation: Optional[str] = None
    timing_note: Optional[str] = None


class ChatRecommendationResponse(BaseModel):
    """Raw response from chat engine"""
    session_id: str
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    versions: HandoffVersions
    step_a_extraction: StepAExtraction
    step_b_recommendation: StepBRecommendation
    chart_insights: List[ChartInsight] = []
    trust_elements: Optional[TrustElements] = None


# ============================================================================
# VALIDATION
# ============================================================================

class ValidationErrorDetail(BaseModel):
    """Single validation error"""
    error_code: str  # UNKNOWN_PACKAGE_ID, UNKNOWN_REMEDY_ID, TOPIC_MISMATCH, etc.
    field: str
    received_value: str
    message: str


class RetryMessage(BaseModel):
    """Retry instruction for chat engine"""
    instruction: str
    allowed_package_ids: List[str]
    allowed_remedy_ids: List[str]
    retry_count: int
    max_retries: int = 2


class ValidationError(BaseModel):
    """Validation failure result"""
    session_id: str
    response_id: str
    validation_status: str = "INVALID"
    errors: List[ValidationErrorDetail]
    retry_message: RetryMessage
    logged_at: datetime = Field(default_factory=datetime.utcnow)
    versions: HandoffVersions


class AuditInfo(BaseModel):
    """Audit trail for validated recommendation"""
    prompt_version: str
    catalog_version: str
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validation_duration_ms: int = 0
    retry_count: int = 0


class ValidatedRecommendation(BaseModel):
    """Final validated recommendation"""
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    validation_status: str = "VALID"
    
    # Extracted situation
    situation: StepAExtraction
    chart_insights: List[ChartInsight]
    
    # Recommendation (validated IDs only)
    recommendation: StepBRecommendation
    
    # Audit trail
    audit: AuditInfo


# ============================================================================
# USER PLAN
# ============================================================================

class UserPlan(BaseModel):
    """User's purchased plan"""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    package_id: str
    recommendation_id: Optional[str] = None
    situation_id: Optional[str] = None
    
    # Status
    status: PlanStatus = PlanStatus.ACTIVE
    start_date: date
    end_date: date
    
    # Payment
    payment_id: str
    package_amount: int
    remedy_addons_amount: int = 0
    total_amount: int
    
    # Progress
    current_week: int = 1
    tasks_completed: int = 0
    tasks_total: int = 0
    
    # Consultation tracking
    consult_sessions_used: int = 0
    consult_sessions_limit: int = 0
    last_chat_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class UserPlanTask(BaseModel):
    """Individual task within a plan"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan_id: str
    item_id: str  # References SelfGuidedItem.item_id
    
    # Scheduling
    scheduled_date: date
    day_number: int
    sequence_order: int
    
    # Content
    name: str
    type: str
    description: str
    duration_minutes: int
    content_type: str
    
    # Status
    status: TaskStatus = TaskStatus.PENDING
    completed_at: Optional[datetime] = None
    
    # User input
    notes: Optional[str] = None
    rating: Optional[int] = None


class UserRemedyAddon(BaseModel):
    """Purchased remedy add-on"""
    addon_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan_id: str
    user_id: str
    remedy_id: str
    
    # Purchase
    purchased_at: datetime = Field(default_factory=datetime.utcnow)
    amount_paid: int
    payment_id: str
    
    # Fulfillment
    status: FulfillmentStatus = FulfillmentStatus.PENDING
    fulfilled_at: Optional[datetime] = None
    fulfillment_notes: Optional[str] = None
    delivery_details: Optional[Dict[str, Any]] = None
