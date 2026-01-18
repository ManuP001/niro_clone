"""
Memory Module for NIRO Chat

Provides persistent user memory and rolling conversation summaries
to reduce generic/repetitive answers.
"""

from .models import (
    UserProfileMemory,
    ConversationState,
    ConversationSummary,
    SummaryStructured,
    MemoryContext,
)
from .memory_store import MemoryStore, get_memory_store
from .memory_service import MemoryService, get_memory_service

__all__ = [
    'UserProfileMemory',
    'ConversationState',
    'ConversationSummary',
    'SummaryStructured',
    'MemoryContext',
    'MemoryStore',
    'get_memory_store',
    'MemoryService',
    'get_memory_service',
]
