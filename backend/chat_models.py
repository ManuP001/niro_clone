"""
Chat System Models for AstroTrust
Handles conversational astrology queries
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum
import uuid

class RequestType(str, Enum):
    NATAL = "natal"
    MARRIAGE = "marriage"
    RELATIONSHIP = "relationship"
    PANCHANG = "panchang"
    SYNASTRY = "synastry"

class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class PlaceData(BaseModel):
    """Place/location data for birth details"""
    city: str
    region: Optional[str] = None
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SubjectData(BaseModel):
    """Subject birth details"""
    name: str
    date_of_birth: str  # YYYY-MM-DD
    time_of_birth: Optional[str] = None  # HH:MM or "unknown"
    place_of_birth: PlaceData
    timezone: Optional[str] = "Asia/Kolkata"

class ContextPreferences(BaseModel):
    """User preferences for calculations"""
    ayanamsa: str = "Lahiri"
    house_system: str = "WholeSign"
    lang: str = "en"

class ChatContext(BaseModel):
    """Context for chat request"""
    request_type: RequestType = RequestType.NATAL
    partner: Optional[SubjectData] = None
    preferences: ContextPreferences = Field(default_factory=ContextPreferences)
    consent_given: bool = False

class ExtractedData(BaseModel):
    """Data extracted from user chat message"""
    user: Optional[SubjectData] = None
    context: ChatContext = Field(default_factory=ChatContext)
    confidence_score: float = 0.0  # 0-1 confidence in extraction
    missing_fields: List[str] = Field(default_factory=list)
    ambiguous_fields: List[str] = Field(default_factory=list)

class APITrigger(BaseModel):
    """Structured API trigger payload for VedicAstroAPI"""
    action: str = "generate_chart"
    payload: Dict[str, Any]
    meta: Dict[str, Any]

class ConfidenceMetadata(BaseModel):
    """Confidence and assumption metadata for interpretations"""
    overall_confidence: float  # 0-1
    assumptions: List[str]
    alternate_readings: List[Dict[str, Any]] = Field(default_factory=list)
    data_quality_notes: List[str] = Field(default_factory=list)

class ChatMessage(BaseModel):
    """Single chat message"""
    model_config = ConfigDict(extra="ignore")
    
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: ChatRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Optional metadata
    extracted_data: Optional[ExtractedData] = None
    api_trigger: Optional[Dict[str, Any]] = None
    confidence_metadata: Optional[ConfidenceMetadata] = None

class ChatSession(BaseModel):
    """Chat session with message history"""
    model_config = ConfigDict(extra="ignore")
    
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Session state
    current_context: Optional[ChatContext] = None
    extracted_data: Optional[ExtractedData] = None
    consent_given: bool = False
    
    # Metadata
    total_messages: int = 0
    status: str = "active"  # active, completed, abandoned

class ChatRequest(BaseModel):
    """Request to send a chat message"""
    session_id: Optional[str] = None
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Response from chat system"""
    session_id: str
    message: str
    role: ChatRole = ChatRole.ASSISTANT
    
    # Optional structured data
    extracted_data: Optional[ExtractedData] = None
    requires_followup: bool = False
    followup_question: Optional[str] = None
    
    # API trigger if ready
    api_trigger_ready: bool = False
    api_trigger: Optional[Dict[str, Any]] = None
    
    # Interpretation metadata
    confidence_metadata: Optional[ConfidenceMetadata] = None
