"""
NIRO Conversation Orchestrator Package

Provides:
- Conversation state management
- Mode/topic routing
- Session storage (in-memory, extensible to Redis/DB)
- Integration with Vedic API and NIRO LLM
"""

from .models import (
    ConversationMode,
    FocusArea,
    BirthDetails,
    ConversationState,
    SuggestedAction,
    NiroReply,
    ChatRequest,
    ChatResponse,
    AstroFeatures
)
from .session_store import SessionStore, InMemorySessionStore
from .mode_router import ModeRouter
from .astro_engine import AstroEngine
from .niro_llm import NiroLLM
from .orchestrator import ConversationOrchestrator
from .enhanced_orchestrator import EnhancedOrchestrator, create_enhanced_orchestrator

__all__ = [
    # Models
    'ConversationMode',
    'FocusArea',
    'BirthDetails',
    'ConversationState',
    'SuggestedAction',
    'NiroReply',
    'ChatRequest',
    'ChatResponse',
    'AstroFeatures',
    # Components
    'SessionStore',
    'InMemorySessionStore',
    'ModeRouter',
    'AstroEngine',
    'NiroLLM',
    'ConversationOrchestrator',
    # Enhanced Orchestrator
    'EnhancedOrchestrator',
    'create_enhanced_orchestrator',
]
