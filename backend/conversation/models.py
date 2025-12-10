"""
Conversation Models for NIRO Chat Orchestrator
Pydantic models for conversation state, birth details, and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ConversationMode(str, Enum):
    """Conversation modes for NIRO chat"""
    BIRTH_COLLECTION = "BIRTH_COLLECTION"
    PAST_THEMES = "PAST_THEMES"
    FOCUS_READING = "FOCUS_READING"
    GENERAL_GUIDANCE = "GENERAL_GUIDANCE"
    DAILY_GUIDANCE = "DAILY_GUIDANCE"


class FocusArea(str, Enum):
    """Focus areas for readings"""
    CAREER = "career"
    RELATIONSHIP = "relationship"
    HEALTH = "health"
    FINANCE = "finance"
    SPIRITUALITY = "spirituality"


class BirthDetails(BaseModel):
    """Birth details for astrological calculations"""
    dob: str = Field(..., description="Date of birth in ISO format (YYYY-MM-DD)")
    tob: str = Field(..., description="Time of birth (HH:MM format, 24h)")
    location: str = Field(..., description="Birth location (city, country)")
    latitude: Optional[float] = Field(None, description="Latitude of birth location")
    longitude: Optional[float] = Field(None, description="Longitude of birth location")
    timezone: Optional[float] = Field(5.5, description="Timezone offset from UTC")


class ConversationState(BaseModel):
    """State model for a conversation session"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mode: ConversationMode = Field(default=ConversationMode.BIRTH_COLLECTION)
    focus: Optional[str] = Field(None, description="Current focus area")
    birth_details: Optional[BirthDetails] = Field(None)
    has_done_retro: bool = Field(default=False, description="Whether retrograde analysis has been done")
    message_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class SuggestedAction(BaseModel):
    """Quick reply action chip"""
    id: str = Field(..., description="Action identifier")
    label: str = Field(..., description="Display label for the chip")


class NiroReply(BaseModel):
    """Structured NIRO response"""
    rawText: str = Field(..., description="Full response text")
    summary: str = Field(..., description="Summary paragraph")
    reasons: List[str] = Field(default_factory=list, description="List of reasons")
    remedies: List[str] = Field(default_factory=list, description="List of remedies")


class ChatRequest(BaseModel):
    """Request payload for /api/chat"""
    sessionId: str = Field(..., description="Session identifier")
    message: str = Field(..., description="User message")
    actionId: Optional[str] = Field(None, description="Action ID from chip click")


class ChatResponse(BaseModel):
    """Response payload from /api/chat"""
    reply: NiroReply
    mode: str
    focus: Optional[str]
    suggestedActions: List[SuggestedAction]
    _pipeline_metadata: Optional[Dict[str, Any]] = Field(default=None, exclude=True, description="Internal metadata for logging")


class AstroFeatures(BaseModel):
    """Normalized astro features from the astro engine"""
    birth_details: Optional[Dict[str, Any]] = None
    ascendant: Optional[str] = None
    moon_sign: Optional[str] = None
    sun_sign: Optional[str] = None
    mahadasha: Optional[Dict[str, Any]] = None
    antardasha: Optional[Dict[str, Any]] = None
    transits: List[Dict[str, Any]] = Field(default_factory=list)
    planetary_strengths: List[Dict[str, Any]] = Field(default_factory=list)
    yogas: List[Dict[str, Any]] = Field(default_factory=list)
    focus_factors: List[Dict[str, Any]] = Field(default_factory=list)
    past_events: List[Dict[str, Any]] = Field(default_factory=list)
    timing_windows: List[Dict[str, Any]] = Field(default_factory=list)
    key_rules: List[str] = Field(default_factory=list)


class NiroLLMPayload(BaseModel):
    """Payload for the NIRO LLM module"""
    mode: str
    focus: Optional[str]
    user_question: str
    astro_features: Dict[str, Any]
