"""
Session Store for Conversation State
In-memory implementation with interface designed for easy swap to Redis/DB.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
from datetime import datetime
import logging

from .models import ConversationState, BirthDetails, ConversationMode

logger = logging.getLogger(__name__)


class SessionStore(ABC):
    """
    Abstract base class for session storage.
    Implement this interface for different backends (Redis, MongoDB, etc.)
    """
    
    @abstractmethod
    def get(self, session_id: str) -> Optional[ConversationState]:
        """Retrieve a conversation state by session ID"""
        pass
    
    @abstractmethod
    def set(self, session_id: str, state: ConversationState) -> None:
        """Store a conversation state"""
        pass
    
    @abstractmethod
    def delete(self, session_id: str) -> bool:
        """Delete a conversation state"""
        pass
    
    @abstractmethod
    def exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        pass


class InMemorySessionStore(SessionStore):
    """
    In-memory session store implementation.
    Suitable for development and single-instance deployments.
    
    For production, replace with RedisSessionStore or MongoSessionStore.
    """
    
    def __init__(self):
        self._store: Dict[str, ConversationState] = {}
        logger.info("InMemorySessionStore initialized")
    
    def get(self, session_id: str) -> Optional[ConversationState]:
        """
        Retrieve a conversation state by session ID.
        Returns None if not found.
        """
        state = self._store.get(session_id)
        if state:
            logger.debug(f"Retrieved session {session_id}: mode={state.mode}, focus={state.focus}")
        else:
            logger.debug(f"Session {session_id} not found")
        return state
    
    def set(self, session_id: str, state: ConversationState) -> None:
        """
        Store a conversation state.
        Updates the updated_at timestamp.
        """
        state.updated_at = datetime.utcnow()
        self._store[session_id] = state
        logger.debug(f"Stored session {session_id}: mode={state.mode}, focus={state.focus}")
    
    def delete(self, session_id: str) -> bool:
        """
        Delete a conversation state.
        Returns True if deleted, False if not found.
        """
        if session_id in self._store:
            del self._store[session_id]
            logger.debug(f"Deleted session {session_id}")
            return True
        return False
    
    def exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        return session_id in self._store
    
    def get_or_create(self, session_id: str) -> ConversationState:
        """
        Get existing state or create a new one.
        """
        state = self.get(session_id)
        if state is None:
            state = ConversationState(
                session_id=session_id,
                mode=ConversationMode.NEED_BIRTH_DETAILS
            )
            self.set(session_id, state)
            logger.info(f"Created new session {session_id}")
        return state
    
    def update_birth_details(
        self,
        session_id: str,
        birth_details: BirthDetails
    ) -> Optional[ConversationState]:
        """
        Update birth details for a session.
        """
        state = self.get(session_id)
        if state:
            state.birth_details = birth_details
            self.set(session_id, state)
            logger.info(f"Updated birth details for session {session_id}")
        return state
    
    def count(self) -> int:
        """Get total number of active sessions"""
        return len(self._store)
    
    def clear(self) -> None:
        """Clear all sessions (use with caution)"""
        self._store.clear()
        logger.warning("All sessions cleared")


# Future implementations:
# class RedisSessionStore(SessionStore):
#     """Redis-backed session store for distributed deployments"""
#     pass
#
# class MongoSessionStore(SessionStore):
#     """MongoDB-backed session store for persistent sessions"""
#     pass
