"""
Memory Service for NIRO Chat

High-level service for managing user memory and conversation context.
Handles:
- Loading combined memory context for pipeline injection
- Updating memory after user/AI messages
- Regenerating conversation summaries
- Extracting "avoid repeating" items
"""

import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from .models import (
    UserProfileMemory,
    ConversationState,
    ConversationSummary,
    SummaryStructured,
    MemoryContext,
)
from .memory_store import get_memory_store

logger = logging.getLogger(__name__)

# How often to regenerate conversation summary
SUMMARY_REGENERATION_INTERVAL = 4  # Every 4 turns


# ============================================================================
# MEMORY SERVICE
# ============================================================================

class MemoryService:
    """
    High-level service for managing conversation memory.
    
    Main responsibilities:
    1. Load combined memory context before pipeline processing
    2. Update memory after each message exchange
    3. Regenerate rolling summaries periodically
    4. Extract "avoid repeating" items from recent answers
    """
    
    def __init__(self):
        self.store = get_memory_store()
        logger.info("[MEMORY_SERVICE] Initialized")
    
    # ========================================================================
    # LOAD MEMORY CONTEXT (for pipeline injection)
    # ========================================================================
    
    def load_memory_context(
        self,
        user_id: str,
        session_id: str
    ) -> MemoryContext:
        """
        Load combined memory context for pipeline injection.
        
        This is called BEFORE signal scoring + LLM generation.
        Returns a MemoryContext object with all relevant context.
        """
        logger.info(f"[MEMORY_SERVICE] Loading memory context for user={user_id}, session={session_id}")
        
        # Load components
        user_memory = self.store.get_user_memory(user_id)
        conv_state = self.store.get_conversation_state(session_id, user_id)
        conv_summary = self.store.get_conversation_summary(session_id, user_id)
        
        # Build combined context
        context = MemoryContext(
            # From user_profile_memory
            astro_profile_summary=user_memory.astro_profile_summary if user_memory else [],
            high_confidence_facts=user_memory.high_confidence_facts if user_memory else [],
            explored_topics=user_memory.explored_topics if user_memory else [],
            
            # From conversation_state
            current_topics=conv_state.current_topics if conv_state else [],
            last_user_question=conv_state.last_user_question if conv_state else None,
            last_ai_answer_summary=conv_state.last_ai_answer_summary if conv_state else [],
            open_loops=conv_state.open_loops if conv_state else [],
            
            # From conversation_summary
            confirmed_facts=conv_summary.summary_structured.confirmed_facts if conv_summary else [],
            avoid_repeating=conv_summary.summary_structured.avoid_repeating if conv_summary else [],
            unresolved_questions=conv_summary.summary_structured.unresolved_questions if conv_summary else [],
            user_preferences=conv_summary.summary_structured.user_preferences if conv_summary else [],
            
            # Meta
            has_prior_context=(conv_state is not None and conv_state.message_count > 0),
            message_count=conv_state.message_count if conv_state else 0,
        )
        
        logger.info(
            f"[MEMORY_SERVICE] Loaded context: has_prior={context.has_prior_context}, "
            f"facts={len(context.confirmed_facts)}, avoid={len(context.avoid_repeating)}, "
            f"msg_count={context.message_count}"
        )
        
        return context
    
    # ========================================================================
    # UPDATE AFTER USER MESSAGE
    # ========================================================================
    
    def update_after_user_message(
        self,
        user_id: str,
        session_id: str,
        user_question: str,
        detected_topics: List[str],
        run_id: Optional[str] = None
    ) -> ConversationState:
        """
        Update conversation state after receiving a user message.
        
        Called at the START of processing each user message.
        """
        logger.info(f"[MEMORY_SERVICE] Updating after user message: {user_question[:50]}...")
        
        # Get or create state
        state = self.store.get_or_create_conversation_state(session_id, user_id)
        
        # Update fields
        state.last_user_question = user_question
        state.current_topics = detected_topics[:3]  # Keep top 3 topics
        state.last_run_id = run_id
        state.message_count += 1
        
        # Check if this question is a follow-up to an open loop
        self._check_and_close_loops(state, user_question)
        
        # Save
        self.store.save_conversation_state(state)
        
        # Also update user memory with explored topics
        self._update_explored_topics(user_id, detected_topics)
        
        return state
    
    def _check_and_close_loops(self, state: ConversationState, question: str):
        """Check if current question addresses any open loops."""
        if not state.open_loops:
            return
        
        q_lower = question.lower()
        closed = []
        
        for loop in state.open_loops:
            # Simple keyword matching
            loop_keywords = set(loop.lower().split())
            if any(kw in q_lower for kw in loop_keywords if len(kw) > 3):
                closed.append(loop)
        
        # Remove closed loops
        for loop in closed:
            state.open_loops.remove(loop)
            logger.info(f"[MEMORY_SERVICE] Closed open loop: {loop}")
    
    def _update_explored_topics(self, user_id: str, topics: List[str]):
        """Update user's explored topics."""
        user_memory = self.store.get_or_create_user_memory(user_id)
        
        for topic in topics:
            if topic and topic not in user_memory.explored_topics:
                user_memory.explored_topics.append(topic)
        
        # Keep only last 10 topics
        user_memory.explored_topics = user_memory.explored_topics[-10:]
        self.store.save_user_memory(user_memory)
    
    # ========================================================================
    # UPDATE AFTER AI RESPONSE
    # ========================================================================
    
    def update_after_ai_response(
        self,
        user_id: str,
        session_id: str,
        ai_response: str,
        drivers: List[Dict[str, Any]],
        topic: str
    ) -> Tuple[ConversationState, bool]:
        """
        Update conversation state after AI response.
        
        Called at the END of processing, after LLM generation.
        
        Returns:
            (updated_state, should_regenerate_summary)
        """
        logger.info(f"[MEMORY_SERVICE] Updating after AI response, topic={topic}")
        
        # Get state
        state = self.store.get_or_create_conversation_state(session_id, user_id)
        
        # Extract summary bullets from AI response
        answer_summary = self._extract_answer_summary(ai_response)
        state.last_ai_answer_summary = answer_summary
        
        # Save state
        self.store.save_conversation_state(state)
        
        # Update conversation summary
        self._update_avoid_repeating(session_id, user_id, answer_summary, drivers)
        
        # Check if we should regenerate full summary
        should_regenerate = (state.message_count % SUMMARY_REGENERATION_INTERVAL == 0)
        
        if should_regenerate:
            self.regenerate_conversation_summary(user_id, session_id, state)
        
        # Update user profile memory with any high-confidence facts
        self._extract_and_save_facts(user_id, ai_response, drivers, topic)
        
        return state, should_regenerate
    
    def _extract_answer_summary(self, ai_response: str) -> List[str]:
        """
        Extract 1-3 key conclusion bullets from AI response.
        
        Uses heuristics to find the main takeaways.
        """
        summary = []
        
        # Look for key patterns in response
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip bullet point suggestions
            if line.startswith('•') and 'suggest' in line.lower():
                continue
            
            # Look for conclusion-type sentences
            if any(pattern in line.lower() for pattern in [
                'looks favorable', 'looks challenging', 'is strong', 'is weak',
                'supports', 'indicates', 'suggests', 'period is', 'phase is',
                'good time for', 'not ideal for', 'well-suited', 'aligned with'
            ]):
                # Clean and add
                clean_line = line.strip('• -').strip()
                if 10 < len(clean_line) < 150:
                    summary.append(clean_line)
                    if len(summary) >= 3:
                        break
        
        # If no conclusions found, take first substantive sentence
        if not summary:
            for line in lines[:5]:
                line = line.strip()
                if len(line) > 30 and not line.startswith('•'):
                    summary.append(line[:150])
                    break
        
        return summary[:3]
    
    def _update_avoid_repeating(
        self,
        session_id: str,
        user_id: str,
        answer_summary: List[str],
        drivers: List[Dict[str, Any]]
    ):
        """Update the avoid_repeating list with recent conclusions."""
        summary = self.store.get_or_create_conversation_summary(session_id, user_id)
        
        # Add new items to avoid_repeating
        for item in answer_summary:
            if item and item not in summary.summary_structured.avoid_repeating:
                summary.summary_structured.avoid_repeating.append(item)
        
        # Also add driver-based facts
        for driver in drivers[:3]:
            claim = driver.get('claim', '') or driver.get('text_human', '')
            if claim and len(claim) > 10:
                short_claim = claim[:100]
                if short_claim not in summary.summary_structured.avoid_repeating:
                    summary.summary_structured.avoid_repeating.append(short_claim)
        
        # Keep only last 10 items
        summary.summary_structured.avoid_repeating = summary.summary_structured.avoid_repeating[-10:]
        
        self.store.save_conversation_summary(summary)
    
    def _extract_and_save_facts(
        self,
        user_id: str,
        ai_response: str,
        drivers: List[Dict[str, Any]],
        topic: str
    ):
        """Extract high-confidence facts and save to user memory."""
        user_memory = self.store.get_or_create_user_memory(user_id)
        
        # Extract facts from drivers (these are chart-based, high confidence)
        for driver in drivers[:3]:
            planet = driver.get('planet', '')
            claim = driver.get('text_human', '') or driver.get('claim', '')
            
            if planet and claim:
                # Create fact statement
                fact = f"{planet}: {claim[:80]}"
                if fact not in user_memory.high_confidence_facts:
                    user_memory.high_confidence_facts.append(fact)
        
        # Keep only last 15 facts
        user_memory.high_confidence_facts = user_memory.high_confidence_facts[-15:]
        
        self.store.save_user_memory(user_memory)
    
    # ========================================================================
    # REGENERATE CONVERSATION SUMMARY
    # ========================================================================
    
    def regenerate_conversation_summary(
        self,
        user_id: str,
        session_id: str,
        state: Optional[ConversationState] = None
    ) -> ConversationSummary:
        """
        Regenerate the rolling conversation summary.
        
        Called every N turns (default 4).
        Uses local heuristics - no LLM call needed.
        """
        logger.info(f"[MEMORY_SERVICE] Regenerating conversation summary for session={session_id}")
        
        if not state:
            state = self.store.get_conversation_state(session_id, user_id)
        
        summary = self.store.get_or_create_conversation_summary(session_id, user_id)
        
        # Build structured summary from state
        structured = SummaryStructured(
            confirmed_facts=summary.summary_structured.confirmed_facts,
            assumptions=summary.summary_structured.assumptions,
            user_preferences=summary.summary_structured.user_preferences,
            unresolved_questions=state.open_loops if state else [],
            avoid_repeating=summary.summary_structured.avoid_repeating,
        )
        
        # Add current topics to confirmed facts if mentioned multiple times
        if state and state.current_topics:
            for topic in state.current_topics:
                topic_fact = f"User interested in {topic}"
                if topic_fact not in structured.confirmed_facts:
                    structured.confirmed_facts.append(topic_fact)
        
        # Generate text summary
        text_parts = []
        if structured.confirmed_facts:
            text_parts.append(f"Confirmed: {'; '.join(structured.confirmed_facts[:3])}")
        if structured.avoid_repeating:
            text_parts.append(f"Already covered: {'; '.join(structured.avoid_repeating[:3])}")
        if structured.unresolved_questions:
            text_parts.append(f"Open questions: {'; '.join(structured.unresolved_questions[:2])}")
        
        summary.summary_text = " | ".join(text_parts)[:1200]
        summary.summary_structured = structured
        summary.turn_count_at_generation = state.message_count if state else 0
        
        self.store.save_conversation_summary(summary)
        
        logger.info(f"[MEMORY_SERVICE] Summary regenerated: {summary.summary_text[:100]}...")
        
        return summary
    
    # ========================================================================
    # ASTRO PROFILE SUMMARY (stable traits)
    # ========================================================================
    
    def update_astro_profile_summary(
        self,
        user_id: str,
        summary_bullets: List[str]
    ):
        """
        Update the stable astro profile summary for a user.
        
        Called once after full chart analysis, contains stable traits.
        """
        user_memory = self.store.get_or_create_user_memory(user_id)
        user_memory.astro_profile_summary = summary_bullets[:6]
        user_memory.birth_profile_complete = True
        self.store.save_user_memory(user_memory)
        
        logger.info(f"[MEMORY_SERVICE] Updated astro profile summary for {user_id}")
    
    # ========================================================================
    # RESET
    # ========================================================================
    
    def reset_user_memory(self, user_id: str) -> bool:
        """Reset all memory for a user."""
        return self.store.reset_user_memory(user_id)
    
    def reset_session_memory(self, session_id: str, user_id: str) -> bool:
        """Reset memory for a specific session."""
        return self.store.reset_session_memory(session_id, user_id)
    
    # ========================================================================
    # DEBUG / INSPECTION
    # ========================================================================
    
    def get_debug_info(self, user_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get debug info about memory state."""
        user_memory = self.store.get_user_memory(user_id)
        
        info = {
            "user_memory": user_memory.to_dict() if user_memory else None,
            "conversation_state": None,
            "conversation_summary": None,
        }
        
        if session_id:
            conv_state = self.store.get_conversation_state(session_id, user_id)
            conv_summary = self.store.get_conversation_summary(session_id, user_id)
            info["conversation_state"] = conv_state.to_dict() if conv_state else None
            info["conversation_summary"] = conv_summary.to_dict() if conv_summary else None
        
        return info


# ============================================================================
# SINGLETON
# ============================================================================

_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """Get or create the MemoryService singleton."""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
