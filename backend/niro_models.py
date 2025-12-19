"""
NIRO Chat Models
Pydantic models for the NIRO AI Vedic Astrology Chat
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SuggestedAction(BaseModel):
    """Quick reply action chip"""
    id: str = Field(..., description="Action identifier, e.g., 'focus_career'")
    label: str = Field(..., description="Display text for the chip")


class NiroReply(BaseModel):
    """Structured NIRO response with Summary, Reasons, and Remedies"""
    rawText: Optional[str] = Field(None, description="Full message as plain text (optional)")
    summary: str = Field(..., description="Summary paragraph")
    reasons: List[str] = Field(default_factory=list, description="List of reasons/explanations")
    remedies: List[str] = Field(default_factory=list, description="List of remedies (may be empty)")


class NiroChatRequest(BaseModel):
    """Request payload for NIRO chat"""
    sessionId: str = Field(..., description="Session identifier")
    message: str = Field(..., description="User message or chip label")
    actionId: Optional[str] = Field(None, description="Optional action identifier from chip click")


class NiroChatResponse(BaseModel):
    """Response payload from NIRO chat"""
    reply: NiroReply = Field(..., description="Structured NIRO reply")
    mode: str = Field(..., description="Response mode, e.g., 'FOCUS_READING', 'PAST_THEMES'")
    focus: Optional[str] = Field(None, description="Focus area: 'career', 'relationship', 'health', etc.")
    suggestedActions: List[SuggestedAction] = Field(
        default_factory=list,
        description="Quick reply actions for the user"
    )
