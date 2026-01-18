"""Data models for authentication and user management"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AuthToken(BaseModel):
    """JWT token response"""
    ok: bool
    token: str
    user_id: str


class User(BaseModel):
    """User model"""
    id: str
    identifier: str  # email or phone
    profile_complete: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OTPRequest(BaseModel):
    """Request OTP"""
    identifier: str  # email or phone


class OTPVerify(BaseModel):
    """Verify OTP"""
    identifier: str
    otp: str


class UserProfile(BaseModel):
    """User profile/birth details"""
    name: str
    dob: str  # YYYY-MM-DD
    tob: str  # HH:MM
    location: str
    birth_place_lat: Optional[float] = None
    birth_place_lon: Optional[float] = None
    birth_place_tz: Optional[float] = 5.5  # Default to IST
    gender: Optional[str] = None  # male, female, other
    marital_status: Optional[str] = None  # single, married, other
    profile_complete: bool = True


class UserProfileRequest(BaseModel):
    """Create/update user profile"""
    name: str
    dob: str
    tob: str
    location: str
    birth_place_lat: Optional[float] = None
    birth_place_lon: Optional[float] = None
    birth_place_tz: Optional[float] = 5.5
    gender: Optional[str] = None  # male, female, other
    marital_status: Optional[str] = None  # single, married, other


class UserResponse(BaseModel):
    """User info with profile status"""
    ok: bool
    user: User


class ProfileResponse(BaseModel):
    """Profile response"""
    ok: bool
    profile: Optional[UserProfile] = None


class ProfileUpdateResponse(BaseModel):
    """Profile update response"""
    ok: bool
    profile_complete: bool
