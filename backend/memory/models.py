"""
Memory Models for NIRO Chat

Persistent user memory + rolling conversation summary to reduce
generic/repetitive answers and build on established context.

Models:
- UserProfileMemory: Per-user stable facts and traits
- ConversationState: Per-session current context
- ConversationSummary: Rolling summary of conversation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# USER PROFILE MEMORY (per user, persists across sessions)
# ============================================================================

class UserProfileMemory(BaseModel):
    """
    Long-term memory for a user - stable facts about their chart
    that don't need to be re-established every session.
    """
    user_id: str
    
    # Birth profile reference (stored separately, just ID here)
    birth_profile_complete: bool = False
    
    # Stable astro traits (3-6 bullets max)
    # Example: ["Mercury-ruled mind with analytical bent", "Career sector activated by Jupiter"]
    astro_profile_summary: List[str] = Field(default_factory=list, max_length=6)
    
    # High confidence facts established through conversation
    # Example: ["User confirmed they work in tech", "Strong 10th house - career focused"]
    high_confidence_facts: List[str] = Field(default_factory=list)
    
    # Lower confidence notes (mentioned but not confirmed)
    # Example: ["Seems interested in entrepreneurship", "May have health concerns"]
    low_confidence_notes: List[str] = Field(default_factory=list)
    
    # Topics user has asked about (for tracking interest areas)
    explored_topics: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "birth_profile_complete": self.birth_profile_complete,
            "astro_profile_summary": self.astro_profile_summary,
            "high_confidence_facts": self.high_confidence_facts,
            "low_confidence_notes": self.low_confidence_notes,
            "explored_topics": self.explored_topics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated_at": self.last_updated_at.isoformat() if self.last_updated_at else None,
        }


# ============================================================================
# CONVERSATION STATE (per session, tracks current context)
# ============================================================================

class ConversationState(BaseModel):
    """
    Current conversation state for a session.
    Updated after every message exchange.
    """
    session_id: str
    user_id: str
    
    # Current active topics in this conversation
    current_topics: List[str] = Field(default_factory=list)
    
    # Last user question (verbatim)
    last_user_question: Optional[str] = None
    
    # Last AI answer summary (1-3 bullets of what was concluded)
    # Example: ["Career looks favorable in 2025-2026", "Mercury period supports communication roles"]
    last_ai_answer_summary: List[str] = Field(default_factory=list, max_length=3)
    
    # Open loops - questions/topics mentioned but not fully addressed
    # Example: ["Asked about marriage but conversation shifted to career"]
    open_loops: List[str] = Field(default_factory=list)
    
    # Run tracking
    last_run_id: Optional[str] = None
    message_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "current_topics": self.current_topics,
            "last_user_question": self.last_user_question,
            "last_ai_answer_summary": self.last_ai_answer_summary,
            "open_loops": self.open_loops,
            "last_run_id": self.last_run_id,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated_at": self.last_updated_at.isoformat() if self.last_updated_at else None,
        }


# ============================================================================
# CONVERSATION SUMMARY (rolling, regenerated every N turns)
# ============================================================================

class SummaryStructured(BaseModel):
    """Structured components of conversation summary."""
    # Facts confirmed in conversation
    confirmed_facts: List[str] = Field(default_factory=list)
    
    # Assumptions made (not explicitly confirmed)
    assumptions: List[str] = Field(default_factory=list)
    
    # User preferences detected
    user_preferences: List[str] = Field(default_factory=list)
    
    # Questions left unresolved
    unresolved_questions: List[str] = Field(default_factory=list)
    
    # Things to avoid repeating (already stated conclusions)
    avoid_repeating: List[str] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    """
    Rolling summary of conversation, regenerated every N turns.
    Used to inject context into the reading pipeline.
    """
    session_id: str
    user_id: str
    
    # Plain text summary (max 1200 chars)
    summary_text: str = Field(default="", max_length=1200)
    
    # Structured summary components
    summary_structured: SummaryStructured = Field(default_factory=SummaryStructured)
    
    # Tracking
    turn_count_at_generation: int = 0
    last_regenerated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "summary_text": self.summary_text,
            "summary_structured": {
                "confirmed_facts": self.summary_structured.confirmed_facts,
                "assumptions": self.summary_structured.assumptions,
                "user_preferences": self.summary_structured.user_preferences,
                "unresolved_questions": self.summary_structured.unresolved_questions,
                "avoid_repeating": self.summary_structured.avoid_repeating,
            },
            "turn_count_at_generation": self.turn_count_at_generation,
            "last_regenerated_at": self.last_regenerated_at.isoformat() if self.last_regenerated_at else None,
        }


# ============================================================================
# MEMORY CONTEXT (combined, passed to pipeline)
# ============================================================================

class MemoryContext(BaseModel):
    """
    Combined memory context passed to the reading pipeline.
    This is what gets injected before signal scoring + LLM generation.
    """
    # From user_profile_memory
    astro_profile_summary: List[str] = Field(default_factory=list)
    high_confidence_facts: List[str] = Field(default_factory=list)
    explored_topics: List[str] = Field(default_factory=list)
    
    # From conversation_state
    current_topics: List[str] = Field(default_factory=list)
    last_user_question: Optional[str] = None
    last_ai_answer_summary: List[str] = Field(default_factory=list)
    open_loops: List[str] = Field(default_factory=list)
    
    # From conversation_summary
    confirmed_facts: List[str] = Field(default_factory=list)
    avoid_repeating: List[str] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
    user_preferences: List[str] = Field(default_factory=list)
    
    # Meta
    has_prior_context: bool = False
    message_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "astro_profile_summary": self.astro_profile_summary,
            "high_confidence_facts": self.high_confidence_facts,
            "explored_topics": self.explored_topics,
            "current_topics": self.current_topics,
            "last_user_question": self.last_user_question,
            "last_ai_answer_summary": self.last_ai_answer_summary,
            "open_loops": self.open_loops,
            "confirmed_facts": self.confirmed_facts,
            "avoid_repeating": self.avoid_repeating,
            "unresolved_questions": self.unresolved_questions,
            "user_preferences": self.user_preferences,
            "has_prior_context": self.has_prior_context,
            "message_count": self.message_count,
        }
    
    def get_all_facts(self) -> List[str]:
        """Get all established facts (high confidence + confirmed)."""
        return list(set(self.high_confidence_facts + self.confirmed_facts))
    
    def get_context_for_prompt(self) -> str:
        """Generate context string for LLM prompt."""
        parts = []
        
        if self.confirmed_facts:
            parts.append("ESTABLISHED FACTS:\n" + "\n".join(f"• {f}" for f in self.confirmed_facts[:5]))
        
        if self.avoid_repeating:
            parts.append("AVOID REPEATING (already stated):\n" + "\n".join(f"• {a}" for a in self.avoid_repeating[:5]))
        
        if self.open_loops:
            parts.append("OPEN QUESTIONS FROM USER:\n" + "\n".join(f"• {o}" for o in self.open_loops[:3]))
        
        if self.last_ai_answer_summary:
            parts.append("LAST ANSWER COVERED:\n" + "\n".join(f"• {s}" for s in self.last_ai_answer_summary))
        
        return "\n\n".join(parts) if parts else ""
