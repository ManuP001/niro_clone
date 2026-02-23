"""NIRO Simplified V1 - Data Models

Models for experts, topics, scenarios, tiers, tools, and threads.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# ENUMS
# ============================================================================

class TopicId(str, Enum):
    """12 Life Topics"""
    CAREER = "career"
    MONEY = "money"
    HEALTH = "health"
    MARRIAGE = "marriage"
    CHILDREN = "children"
    LOVE = "love"
    BUSINESS = "business"
    TRAVEL = "travel"
    PROPERTY = "property"
    MENTAL_HEALTH = "mental_health"
    SPIRITUAL = "spiritual"
    LEGAL = "legal"


class TierLevel(str, Enum):
    """Pack tier levels"""
    STARTER = "starter"
    PLUS = "plus"
    PRO = "pro"


class ExpertModality(str, Enum):
    """Expert specialization types"""
    VEDIC_ASTROLOGER = "vedic_astrologer"
    WESTERN_ASTROLOGER = "western_astrologer"
    PALMIST = "palmist"
    NUMEROLOGIST = "numerologist"
    TAROT = "tarot"
    PSYCHIC = "psychic"
    LIFE_COACH = "life_coach"
    CAREER_COACH = "career_coach"
    RELATIONSHIP_COUNSELOR = "relationship_counselor"
    HEALER = "healer"
    SPIRITUAL_GUIDE = "spiritual_guide"
    LEGAL_ADVISOR = "legal_advisor"
    MARRIAGE_COUNSELOR = "marriage_counselor"
    FINANCIAL_ADVISOR = "financial_advisor"


class PlanStatus(str, Enum):
    """User plan status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ThreadStatus(str, Enum):
    """Expert thread status"""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class ToolType(str, Enum):
    """Free tool types"""
    QUIZ = "quiz"
    CHECKLIST = "checklist"
    FRAMEWORK = "framework"
    EXPLAINER = "explainer"
    PROMPTS = "prompts"
    WORKSHEET = "worksheet"


class ToolAccess(str, Enum):
    """Tool access levels"""
    PLUS_PRO_ONLY = "plus_pro_only"


# ============================================================================
# TOPIC MODEL
# ============================================================================

class Topic(BaseModel):
    """Life topic configuration"""
    topic_id: str
    label: str
    icon: str
    tagline: str
    color_scheme: str = "emerald"
    expert_modalities: List[str] = []
    is_active: bool = True
    display_order: int = 0


# ============================================================================
# EXPERT PROFILE MODEL
# ============================================================================

class ExpertProfile(BaseModel):
    """Expert profile for topic specialists"""
    expert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    photo_url: str = ""
    modality: str  # ExpertModality value
    modality_label: str = ""
    languages: List[str] = ["English", "Hindi"]
    topics: List[str] = []  # topic_ids this expert serves
    best_for_tags: List[str] = []  # e.g., ["Career transitions", "Timing decisions"]
    short_bio: str = ""
    experience_years: int = 5
    rating: float = 4.5  # Placeholder
    total_consultations: int = 100  # Social proof placeholder
    availability_status: str = "available"  # available, busy, offline
    is_active: bool = True
    display_order: int = 0
    offers_free_call: bool = False
    timezone: str = "Asia/Kolkata"
    weekly_availability: Dict[str, List[Dict[str, str]]] = {}


# ============================================================================
# SCENARIO CHIP MODEL
# ============================================================================

class ScenarioChip(BaseModel):
    """Scenario chip for topic landing page"""
    scenario_id: str
    topic_id: str
    label: str
    urgency_hint: str = "medium"  # low, medium, high
    recommended_tier: str = "plus"  # starter, plus, pro
    display_order: int = 0
    is_active: bool = True


# ============================================================================
# PACK TIER MODEL
# ============================================================================

class AccessPolicy(BaseModel):
    """Access policy for a tier"""
    chat_sla_hours: int = 24
    calls_enabled: bool = False
    calls_per_month: int = 0
    call_duration_minutes: int = 60
    max_active_expert_threads: int = 1  # -1 for unlimited
    free_tools_access: bool = False


class PackTier(BaseModel):
    """Pack tier configuration (Starter/Plus/Pro)"""
    tier_id: str  # e.g., career_starter, career_plus
    topic_id: str
    tier_level: str  # starter, plus, pro
    name: str
    tagline: str = ""
    price_inr: int
    validity_weeks: int
    is_recommended: bool = False
    access_policy: AccessPolicy
    features: List[str] = []
    display_order: int = 0
    is_active: bool = True
    catalog_version: str = "2025.01.v1"


# ============================================================================
# FREE TOOL MODEL
# ============================================================================

class TopicFreeTool(BaseModel):
    """Free tool for topic (Plus/Pro only)"""
    tool_id: str
    topic_id: str
    title: str
    short_desc: str = ""
    tool_type: str  # quiz, checklist, framework, etc.
    content_url: str = ""
    content_md: str = ""
    access: str = "plus_pro_only"
    display_order: int = 0
    is_active: bool = True


# ============================================================================
# USER STATE MODEL
# ============================================================================

class ActivePlanSummary(BaseModel):
    """Summary of an active plan"""
    plan_id: str
    topic_id: str
    topic_label: str
    tier_level: str
    tier_name: str
    weeks_remaining: int
    calls_remaining: int = 0
    threads_count: int = 0


class RecentThreadSummary(BaseModel):
    """Summary of a recent expert thread"""
    thread_id: str
    expert_id: str
    expert_name: str
    expert_modality: str
    last_message_at: Optional[datetime] = None


class UserState(BaseModel):
    """User state for home screen routing"""
    user_id: str
    is_new_user: bool = True  # Has never purchased
    has_active_plan: bool = False
    active_plans: List[ActivePlanSummary] = []
    recent_expert_threads: List[RecentThreadSummary] = []
    additional_topic_passes: List[str] = []  # topic_ids unlocked via passes
    free_call_status: Optional[str] = None   # "scheduled" | "completed" | None
    free_call_expert_id: Optional[str] = None
    free_call_expert_name: Optional[str] = None
    free_call_topic_id: Optional[str] = None


# ============================================================================
# USER PLAN MODEL
# ============================================================================

class UserPlan(BaseModel):
    """User's purchased plan"""
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:12]}")
    user_id: str
    topic_id: str
    tier_id: str
    tier_level: str
    price_paid_inr: int
    status: str = "active"
    purchased_at: datetime = Field(default_factory=datetime.utcnow)
    starts_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    calls_used_this_month: int = 0
    calls_reset_date: Optional[datetime] = None
    selected_scenarios: List[str] = []  # scenario_ids selected
    intake_notes: str = ""


# ============================================================================
# EXPERT THREAD MODEL
# ============================================================================

class ExpertThread(BaseModel):
    """Expert conversation thread"""
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan_id: str
    user_id: str
    expert_id: str
    topic_id: str
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    message_count: int = 0


# ============================================================================
# TOPIC PASS MODEL
# ============================================================================

class AdditionalTopicPass(BaseModel):
    """Additional topic pass (₹2000)"""
    pass_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    parent_plan_id: str
    topic_id: str
    price_inr: int = 2000
    purchased_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: str = "active"


# ============================================================================
# UNLIMITED ACCESS CONDITIONS (DISPLAY)
# ============================================================================

class UnlimitedAccessConditions(BaseModel):
    """Static content for Section E"""
    chat_condition: Dict[str, Any] = {
        "title": "Unlimited Chat",
        "icon": "💬",
        "description": "Chat with experts as much as you need. Experts respond within 24 hours."
    }
    call_condition: Dict[str, Any] = {
        "title": "Video/In-Person Calls (Plus & Pro only)",
        "icon": "📞",
        "description": "Plus and Pro levels include scheduled calls with experts.",
        "details": [
            "Schedule as per expert availability",
            "Each call: max 60 minutes",
            "Plus: 2 calls/month | Pro: 4 calls/month"
        ]
    }
    topic_condition: Dict[str, Any] = {
        "title": "Single Topic Focus",
        "icon": "🎯",
        "description": "Each pack covers ONE life topic. Want to discuss another topic? Add a Topic Pass for ₹2,000."
    }
