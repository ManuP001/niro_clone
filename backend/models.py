from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
from enum import Enum

class ReportType(str, Enum):
    YEARLY_PREDICTION = "yearly_prediction"
    LOVE_MARRIAGE = "love_marriage"
    CAREER_JOB = "career_job"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class ReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# ============= USER MODELS =============

class UserBirthDetails(BaseModel):
    """User's birth details for astrological calculations"""
    dob: str = Field(..., description="Date of birth (DD-MM-YYYY)")
    tob: str = Field(..., description="Time of birth (HH:MM format, 24-hour)")
    lat: float = Field(..., description="Latitude of birth location")
    lon: float = Field(..., description="Longitude of birth location")
    location: str = Field(..., description="Birth location name")
    timezone: float = Field(default=5.5, description="Timezone offset (IST = 5.5)")

class User(BaseModel):
    """User model"""
    model_config = ConfigDict(extra="ignore")
    
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_details: UserBirthDetails
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    """Model for creating new user"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    birth_details: UserBirthDetails

# ============= TRANSACTION MODELS =============

class Transaction(BaseModel):
    """Payment transaction model"""
    model_config = ConfigDict(extra="ignore")
    
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    report_type: ReportType
    amount: float
    currency: str = "INR"
    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_method: str = "UPI"
    payment_gateway_ref: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class TransactionCreate(BaseModel):
    """Model for creating transaction"""
    user_id: str
    report_type: ReportType
    amount: float

class MockPaymentVerify(BaseModel):
    """Mock payment verification (for MVP)"""
    transaction_id: str
    payment_success: bool = True

# ============= REPORT MODELS =============

class ReportRequest(BaseModel):
    """Request model for generating astrological report"""
    user_id: str
    transaction_id: str
    report_type: ReportType
    birth_details: UserBirthDetails
    partner_details: Optional[UserBirthDetails] = None  # For love_marriage report

class Report(BaseModel):
    """Generated astrological report"""
    model_config = ConfigDict(extra="ignore")
    
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    transaction_id: str
    report_type: ReportType
    status: ReportStatus = ReportStatus.PENDING
    
    # Raw data from VedicAstroAPI
    raw_json: Optional[Dict[str, Any]] = None
    
    # AI-generated code
    generated_code: Optional[str] = None
    code_execution_success: bool = False
    code_execution_error: Optional[str] = None
    
    # Interpreted report
    interpreted_text: Optional[str] = None
    
    # PDF
    pdf_url: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None

class ReportResponse(BaseModel):
    """Response model for report generation"""
    report_id: str
    status: ReportStatus
    report_type: ReportType
    interpreted_text: Optional[str] = None
    pdf_url: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    error_message: Optional[str] = None

# ============= FOLLOW-UP MODELS =============

class FollowUpQuestion(BaseModel):
    """Follow-up question about a report"""
    report_id: str
    question: str

class FollowUpResponse(BaseModel):
    """Response to follow-up question"""
    report_id: str
    question: str
    answer: str
    answered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============= PRICING MODELS =============

class PriceConfig(BaseModel):
    """Pricing configuration for report types"""
    model_config = ConfigDict(extra="ignore")
    
    price_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: ReportType
    current_price_inr: float
    currency: str = "INR"
    is_active: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PriceUpdate(BaseModel):
    """Model for updating price"""
    report_type: ReportType
    new_price_inr: float
