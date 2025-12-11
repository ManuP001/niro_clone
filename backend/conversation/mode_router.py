"""
Mode Router for NIRO Conversation
Determines the conversation mode based on birth details availability.
Simplified to 2-mode system: NEED_BIRTH_DETAILS or NORMAL_READING.
"""

from typing import Tuple, Optional, Set
import re
import logging

from .models import ConversationState, ConversationMode

logger = logging.getLogger(__name__)


class ModeRouter:
    """
    Routes conversation to appropriate mode based on:
    - Birth details availability (complete or incomplete)
    - User message content for focus detection
    - Action ID from quick reply chips
    """
    
    # Keyword sets for focus detection
    CAREER_KEYWORDS: Set[str] = {
        'job', 'career', 'work', 'promotion', 'salary', 'business',
        'profession', 'employment', 'boss', 'colleague', 'office',
        'interview', 'resign', 'fired', 'hired', 'income', 'earning'
    }
    
    RELATIONSHIP_KEYWORDS: Set[str] = {
        'relationship', 'love', 'partner', 'marriage', 'spouse', 'husband',
        'wife', 'boyfriend', 'girlfriend', 'dating', 'romance', 'divorce',
        'breakup', 'engagement', 'wedding', 'family', 'children', 'kids'
    }
    
    HEALTH_KEYWORDS: Set[str] = {
        'health', 'illness', 'disease', 'doctor', 'hospital', 'medicine',
        'surgery', 'fitness', 'wellness', 'mental', 'stress', 'anxiety',
        'depression', 'sleep', 'diet', 'exercise', 'energy', 'tired'
    }
    
    FINANCE_KEYWORDS: Set[str] = {
        'money', 'finance', 'investment', 'property', 'wealth', 'debt',
        'loan', 'savings', 'stock', 'trading', 'real estate', 'inheritance'
    }
    
    SPIRITUALITY_KEYWORDS: Set[str] = {
        'spiritual', 'meditation', 'moksha', 'karma', 'dharma', 'purpose',
        'meaning', 'enlightenment', 'guru', 'temple', 'prayer', 'mantra'
    }
    
    # Action ID to focus mapping
    ACTION_TO_FOCUS = {
        'focus_career': 'career',
        'focus_relationship': 'relationship',
        'focus_health': 'health',
        'focus_finance': 'finance',
        'focus_spirituality': 'spirituality',
        'ask_career': 'career',
        'ask_relationship': 'relationship',
        'ask_timing': None,  # Timing is mode modifier, not focus
        'daily_guidance': None,
        'deep_dive': None,  # Keep current focus
    }
    
    def __init__(self):
        logger.info("ModeRouter initialized (2-mode system: NEED_BIRTH_DETAILS / NORMAL_READING)")
    
    def route_mode(
        self,
        state: ConversationState,
        user_message: str,
        action_id: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Determine mode and focus for the current turn.
        
        Simplified logic:
        - If birth_details is missing or incomplete -> NEED_BIRTH_DETAILS
        - Else -> NORMAL_READING
        
        Args:
            state: Current conversation state
            user_message: User's message text
            action_id: Optional action ID from quick reply chip
            
        Returns:
            Tuple of (mode, focus)
        """
        logger.debug(f"Routing: current_mode={state.mode}, action_id={action_id}")
        
        # Rule 1: If birth_details is missing or incomplete -> NEED_BIRTH_DETAILS
        if not self._has_complete_birth_details(state):
            logger.info("Birth details missing/incomplete -> NEED_BIRTH_DETAILS mode")
            return ConversationMode.NEED_BIRTH_DETAILS.value, None
        
        # Rule 2: Birth details complete -> NORMAL_READING
        # Now determine focus from action_id or message content
        
        # Check actionId for explicit focus
        if action_id and action_id in self.ACTION_TO_FOCUS:
            focus = self.ACTION_TO_FOCUS[action_id]
            if focus is None and action_id == 'deep_dive':
                focus = state.focus  # Keep current focus for deep dive
            
            if focus:
                logger.info(f"Action {action_id} -> NORMAL_READING, focus={focus}")
                return ConversationMode.NORMAL_READING.value, focus
        
        # Infer focus from message keywords
        inferred_focus = self._infer_focus_from_message(user_message)
        
        if inferred_focus:
            logger.info(f"Inferred focus from message: {inferred_focus}")
            return ConversationMode.NORMAL_READING.value, inferred_focus
        
        # Keep previous focus if exists, else None (general reading)
        if state.focus:
            logger.info(f"Keeping previous focus: {state.focus}")
            return ConversationMode.NORMAL_READING.value, state.focus
        
        logger.info("No specific focus -> NORMAL_READING mode (general)")
        return ConversationMode.NORMAL_READING.value, None
    
    def _has_complete_birth_details(self, state: ConversationState) -> bool:
        """
        Check if birth details are complete (has dob, tob, and location).
        
        Args:
            state: Current conversation state
            
        Returns:
            True if all required fields present, False otherwise
        """
        if state.birth_details is None:
            return False
        
        bd = state.birth_details
        has_dob = bool(bd.dob)
        has_tob = bool(bd.tob)
        has_location = bool(bd.location)
        
        complete = has_dob and has_tob and has_location
        logger.debug(f"Birth details check: dob={has_dob}, tob={has_tob}, location={has_location} -> complete={complete}")
        
        return complete
    
    def _infer_focus_from_message(self, message: str) -> Optional[str]:
        """
        Infer focus area from keywords in the message.
        
        Args:
            message: User's message text
            
        Returns:
            Focus area string or None
        """
        # Normalize message for keyword matching
        words = set(re.findall(r'\b\w+\b', message.lower()))
        
        # Check each keyword set (order matters - more specific first)
        keyword_sets = [
            (self.CAREER_KEYWORDS, 'career'),
            (self.RELATIONSHIP_KEYWORDS, 'relationship'),
            (self.HEALTH_KEYWORDS, 'health'),
            (self.FINANCE_KEYWORDS, 'finance'),
            (self.SPIRITUALITY_KEYWORDS, 'spirituality'),
        ]
        
        # Count matches for each category
        max_matches = 0
        best_focus = None
        
        for keyword_set, focus in keyword_sets:
            matches = len(words.intersection(keyword_set))
            if matches > max_matches:
                max_matches = matches
                best_focus = focus
        
        # Only return if we have at least one match
        if max_matches > 0:
            logger.debug(f"Keyword match: {best_focus} with {max_matches} matches")
            return best_focus
        
        return None
    
    def should_collect_birth_details(self, state: ConversationState) -> bool:
        """Check if we need to collect birth details"""
        return not self._has_complete_birth_details(state)
