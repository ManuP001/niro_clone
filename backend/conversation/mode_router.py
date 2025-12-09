"""
Mode Router for NIRO Conversation
Determines the conversation mode and focus based on state and user input.
"""

from typing import Tuple, Optional, Set
import re
import logging

from .models import ConversationState, ConversationMode

logger = logging.getLogger(__name__)


class ModeRouter:
    """
    Routes conversation to appropriate mode and focus based on:
    - Current conversation state
    - User message content
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
    
    # Action ID to mode mapping
    ACTION_TO_MODE = {
        'daily_guidance': ConversationMode.DAILY_GUIDANCE,
        'past_themes': ConversationMode.PAST_THEMES,
        'general_guidance': ConversationMode.GENERAL_GUIDANCE,
    }
    
    def __init__(self):
        logger.info("ModeRouter initialized")
    
    def route_mode(
        self,
        state: ConversationState,
        user_message: str,
        action_id: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Determine mode and focus for the current turn.
        
        Args:
            state: Current conversation state
            user_message: User's message text
            action_id: Optional action ID from quick reply chip
            
        Returns:
            Tuple of (mode, focus)
        """
        logger.debug(f"Routing: current_mode={state.mode}, action_id={action_id}")
        
        # Rule 1: If birth_details is missing -> BIRTH_COLLECTION
        if state.birth_details is None:
            logger.info("No birth details -> BIRTH_COLLECTION mode")
            return ConversationMode.BIRTH_COLLECTION.value, None
        
        # Rule 2: If retro analysis hasn't been done -> PAST_THEMES (first reading)
        if not state.has_done_retro:
            logger.info("Retro not done -> PAST_THEMES mode")
            return ConversationMode.PAST_THEMES.value, None
        
        # Rule 3: Check actionId for explicit mode/focus
        if action_id:
            # Check for mode override
            if action_id in self.ACTION_TO_MODE:
                mode = self.ACTION_TO_MODE[action_id].value
                focus = state.focus  # Keep existing focus
                logger.info(f"Action {action_id} -> mode={mode}, focus={focus}")
                return mode, focus
            
            # Check for focus override
            if action_id in self.ACTION_TO_FOCUS:
                focus = self.ACTION_TO_FOCUS[action_id]
                if focus is None and action_id == 'deep_dive':
                    focus = state.focus  # Keep current focus for deep dive
                
                if focus:
                    logger.info(f"Action {action_id} -> FOCUS_READING, focus={focus}")
                    return ConversationMode.FOCUS_READING.value, focus
        
        # Rule 4: Infer focus from message keywords
        inferred_focus = self._infer_focus_from_message(user_message)
        
        if inferred_focus:
            logger.info(f"Inferred focus from message: {inferred_focus}")
            return ConversationMode.FOCUS_READING.value, inferred_focus
        
        # Rule 5: Keep previous focus if exists, else GENERAL_GUIDANCE
        if state.focus:
            logger.info(f"Keeping previous focus: {state.focus}")
            return ConversationMode.FOCUS_READING.value, state.focus
        
        logger.info("No specific focus -> GENERAL_GUIDANCE mode")
        return ConversationMode.GENERAL_GUIDANCE.value, None
    
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
        return state.birth_details is None
    
    def should_do_retro(self, state: ConversationState) -> bool:
        """Check if we should do retrograde/past themes analysis"""
        return state.birth_details is not None and not state.has_done_retro
