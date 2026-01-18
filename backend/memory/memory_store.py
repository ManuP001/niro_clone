"""
Memory Storage for NIRO Chat

MongoDB-backed storage for user memory and conversation state.
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pymongo import MongoClient

from .models import (
    UserProfileMemory,
    ConversationState,
    ConversationSummary,
    SummaryStructured,
)

logger = logging.getLogger(__name__)


# ============================================================================
# MEMORY STORE
# ============================================================================

class MemoryStore:
    """
    MongoDB-backed storage for user memory and conversation state.
    """
    
    def __init__(self):
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = MongoClient(mongo_url)
        self.db = self.client.niro_db
        
        # Collections
        self.user_memory_collection = self.db.user_profile_memory
        self.conversation_state_collection = self.db.conversation_state
        self.conversation_summary_collection = self.db.conversation_summary
        
        # Create indexes
        self._ensure_indexes()
        
        logger.info("[MEMORY_STORE] Initialized with MongoDB")
    
    def _ensure_indexes(self):
        """Create indexes for efficient querying."""
        try:
            self.user_memory_collection.create_index("user_id", unique=True)
            self.conversation_state_collection.create_index([("session_id", 1), ("user_id", 1)])
            self.conversation_summary_collection.create_index([("session_id", 1), ("user_id", 1)])
        except Exception as e:
            logger.warning(f"[MEMORY_STORE] Index creation warning: {e}")
    
    # ========================================================================
    # USER PROFILE MEMORY
    # ========================================================================
    
    def get_user_memory(self, user_id: str) -> Optional[UserProfileMemory]:
        """Get user profile memory."""
        try:
            doc = self.user_memory_collection.find_one({"user_id": user_id})
            if doc:
                doc.pop('_id', None)
                # Parse datetime strings
                if 'created_at' in doc and isinstance(doc['created_at'], str):
                    doc['created_at'] = datetime.fromisoformat(doc['created_at'])
                if 'last_updated_at' in doc and isinstance(doc['last_updated_at'], str):
                    doc['last_updated_at'] = datetime.fromisoformat(doc['last_updated_at'])
                return UserProfileMemory(**doc)
            return None
        except Exception as e:
            logger.error(f"[MEMORY_STORE] Error getting user memory: {e}")
            return None
    
    def save_user_memory(self, memory: UserProfileMemory) -> bool:
        """Save or update user profile memory."""
        try:
            memory.last_updated_at = datetime.utcnow()
            data = memory.to_dict()
            
            self.user_memory_collection.update_one(
                {"user_id": memory.user_id},
                {"$set": data},
                upsert=True
            )
            logger.info(f"[MEMORY_STORE] Saved user memory for {memory.user_id}")
            return True
        except Exception as e:
            logger.error(f"[MEMORY_STORE] Error saving user memory: {e}")
            return False
    
    def get_or_create_user_memory(self, user_id: str) -> UserProfileMemory:
        """Get existing or create new user memory."""
        memory = self.get_user_memory(user_id)
        if not memory:
            memory = UserProfileMemory(user_id=user_id)
            self.save_user_memory(memory)
        return memory
    
    # ========================================================================
    # CONVERSATION STATE
    # ========================================================================
    
    def get_conversation_state(self, session_id: str, user_id: str) -> Optional[ConversationState]:
        """Get conversation state for a session."""
        try:
            doc = self.conversation_state_collection.find_one({
                "session_id": session_id,
                "user_id": user_id
            })
            if doc:
                doc.pop('_id', None)
                if 'created_at' in doc and isinstance(doc['created_at'], str):
                    doc['created_at'] = datetime.fromisoformat(doc['created_at'])
                if 'last_updated_at' in doc and isinstance(doc['last_updated_at'], str):
                    doc['last_updated_at'] = datetime.fromisoformat(doc['last_updated_at'])
                return ConversationState(**doc)
            return None
        except Exception as e:
            logger.error(f"[MEMORY_STORE] Error getting conversation state: {e}")
            return None
    
    def save_conversation_state(self, state: ConversationState) -> bool:
        """Save or update conversation state."""
        try:
            state.last_updated_at = datetime.utcnow()
            data = state.to_dict()
            
            self.conversation_state_collection.update_one(
                {"session_id": state.session_id, "user_id": state.user_id},
                {"$set": data},
                upsert=True
            )
            logger.debug(f"[MEMORY_STORE] Saved conversation state for session {state.session_id}")
            return True
        except Exception as e:
            logger.error(f"[MEMORY_STORE] Error saving conversation state: {e}")
            return False
    
    def get_or_create_conversation_state(self, session_id: str, user_id: str) -> ConversationState:
        """Get existing or create new conversation state."""
        state = self.get_conversation_state(session_id, user_id)
        if not state:
            state = ConversationState(session_id=session_id, user_id=user_id)
            self.save_conversation_state(state)
        return state
    
    # ========================================================================
    # CONVERSATION SUMMARY
    # ========================================================================
    
    def get_conversation_summary(self, session_id: str, user_id: str) -> Optional[ConversationSummary]:
        """Get conversation summary for a session."""
        try:
            doc = self.conversation_summary_collection.find_one({
                "session_id": session_id,
                "user_id": user_id
            })
            if doc:
                doc.pop('_id', None)
                if 'last_regenerated_at' in doc and isinstance(doc['last_regenerated_at'], str):
                    doc['last_regenerated_at'] = datetime.fromisoformat(doc['last_regenerated_at'])
                # Handle nested summary_structured
                if 'summary_structured' in doc and isinstance(doc['summary_structured'], dict):
                    doc['summary_structured'] = SummaryStructured(**doc['summary_structured'])
                return ConversationSummary(**doc)
            return None
        except Exception as e:
            logger.error(f"[MEMORY_STORE] Error getting conversation summary: {e}")
            return None
    
    def save_conversation_summary(self, summary: ConversationSummary) -> bool:
        """Save or update conversation summary."""
        try:
            summary.last_regenerated_at = datetime.utcnow()
            data = summary.to_dict()
            
            self.conversation_summary_collection.update_one(
                {"session_id": summary.session_id, "user_id": summary.user_id},
                {"$set": data},
                upsert=True
            )
            logger.debug(f"[MEMORY_STORE] Saved conversation summary for session {summary.session_id}")
            return True
        except Exception as e:
            logger.error(f"[MEMORY_STORE] Error saving conversation summary: {e}")
            return False
    
    def get_or_create_conversation_summary(self, session_id: str, user_id: str) -> ConversationSummary:
        """Get existing or create new conversation summary."""
        summary = self.get_conversation_summary(session_id, user_id)
        if not summary:
            summary = ConversationSummary(session_id=session_id, user_id=user_id)
            self.save_conversation_summary(summary)
        return summary
    
    # ========================================================================
    # RESET / CLEAR
    # ========================================================================
    
    def reset_user_memory(self, user_id: str) -> bool:
        """Clear all memory for a user."""
        try:
            self.user_memory_collection.delete_many({"user_id": user_id})
            self.conversation_state_collection.delete_many({"user_id": user_id})
            self.conversation_summary_collection.delete_many({"user_id": user_id})
            logger.info(f"[MEMORY_STORE] Reset all memory for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"[MEMORY_STORE] Error resetting memory: {e}")
            return False
    
    def reset_session_memory(self, session_id: str, user_id: str) -> bool:
        """Clear memory for a specific session."""
        try:
            self.conversation_state_collection.delete_many({
                "session_id": session_id,
                "user_id": user_id
            })
            self.conversation_summary_collection.delete_many({
                "session_id": session_id,
                "user_id": user_id
            })
            logger.info(f"[MEMORY_STORE] Reset session memory for {session_id}")
            return True
        except Exception as e:
            logger.error(f"[MEMORY_STORE] Error resetting session memory: {e}")
            return False
    
    # ========================================================================
    # RECENT SESSIONS
    # ========================================================================
    
    def get_recent_sessions(self, user_id: str, limit: int = 5) -> List[str]:
        """Get recent session IDs for a user."""
        try:
            docs = self.conversation_state_collection.find(
                {"user_id": user_id}
            ).sort("last_updated_at", -1).limit(limit)
            return [doc["session_id"] for doc in docs]
        except Exception as e:
            logger.error(f"[MEMORY_STORE] Error getting recent sessions: {e}")
            return []


# ============================================================================
# SINGLETON
# ============================================================================

_memory_store: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    """Get or create the MemoryStore singleton."""
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store
