"""
Conversation Orchestrator for NIRO
Main orchestration logic that ties all components together.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from .models import (
    ConversationState,
    ConversationMode,
    BirthDetails,
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

logger = logging.getLogger(__name__)


class ConversationOrchestrator:
    """
    Main orchestrator for NIRO conversations.
    
    Coordinates:
    - Session state management
    - Mode/focus routing
    - Astro engine calculations
    - LLM response generation
    - Suggested actions
    """
    
    def __init__(
        self,
        session_store: Optional[SessionStore] = None,
        mode_router: Optional[ModeRouter] = None,
        astro_engine: Optional[AstroEngine] = None,
        niro_llm: Optional[NiroLLM] = None
    ):
        """
        Initialize orchestrator with components.
        
        Args:
            session_store: Session storage backend (default: InMemorySessionStore)
            mode_router: Mode routing logic (default: ModeRouter)
            astro_engine: Astro calculation engine (default: AstroEngine)
            niro_llm: LLM response generator (default: NiroLLM)
        """
        self.session_store = session_store or InMemorySessionStore()
        self.mode_router = mode_router or ModeRouter()
        self.astro_engine = astro_engine or AstroEngine()
        self.niro_llm = niro_llm or NiroLLM()
        
        logger.info("ConversationOrchestrator initialized")
    
    async def process_message(
        self,
        request: ChatRequest
    ) -> ChatResponse:
        """
        Process a chat message and generate response.
        
        Flow:
        1. Load or create conversation state
        2. Route to appropriate mode/focus
        3. Compute astro features if needed
        4. Generate LLM response
        5. Build suggested actions
        6. Update state and return response
        
        Args:
            request: ChatRequest with sessionId, message, actionId
            
        Returns:
            ChatResponse with reply, mode, focus, suggestedActions
        """
        logger.info(f"Processing message for session {request.sessionId}")
        
        # Step 1: Load or create conversation state
        state = self.session_store.get_or_create(request.sessionId)
        state.message_count += 1
        
        # Step 2: Check for birth details in message (simple extraction)
        if state.birth_details is None:
            extracted_details = self._try_extract_birth_details(request.message)
            if extracted_details:
                state.birth_details = extracted_details
                self.session_store.set(request.sessionId, state)
                logger.info(f"Extracted birth details for session {request.sessionId}")
        
        # Step 3: Route to mode and focus
        mode, focus = self.mode_router.route_mode(
            state=state,
            user_message=request.message,
            action_id=request.actionId
        )
        
        # Update state with new mode/focus
        state.mode = ConversationMode(mode)
        state.focus = focus
        
        # Step 4: Compute astro features if we have birth details
        astro_features = {}
        if state.birth_details and mode != ConversationMode.BIRTH_COLLECTION.value:
            now = datetime.utcnow()
            
            # Get raw astro data
            astro_raw = self.astro_engine.compute_astro_raw(
                birth_details=state.birth_details,
                mode=mode,
                focus=focus,
                now=now
            )
            
            # Build normalized features
            astro_features = self.astro_engine.build_astro_features(
                raw=astro_raw,
                mode=mode,
                focus=focus
            )
        
        # Step 5: Build LLM payload and generate response
        payload = {
            'mode': mode,
            'focus': focus,
            'user_question': request.message,
            'astro_features': astro_features
        }
        
        llm_response = self.niro_llm.call_niro_llm(payload)
        
        # Step 6: Build suggested actions
        suggested_actions = self.build_suggested_actions(mode, focus)
        
        # Step 7: Update state
        if mode == ConversationMode.PAST_THEMES.value:
            state.has_done_retro = True
        
        self.session_store.set(request.sessionId, state)
        
        # Step 8: Build and return response
        reply = NiroReply(
            rawText=llm_response.get('rawText', ''),
            summary=llm_response.get('summary', ''),
            reasons=llm_response.get('reasons', []),
            remedies=llm_response.get('remedies', [])
        )
        
        response = ChatResponse(
            reply=reply,
            mode=mode,
            focus=focus,
            suggestedActions=suggested_actions
        )
        
        logger.info(f"Response generated: mode={mode}, focus={focus}")
        return response
    
    def build_suggested_actions(
        self,
        mode: str,
        focus: Optional[str]
    ) -> List[SuggestedAction]:
        """
        Build suggested follow-up actions based on mode and focus.
        
        Args:
            mode: Current conversation mode
            focus: Current focus area
            
        Returns:
            List of SuggestedAction for quick reply chips
        """
        actions = []
        
        if mode == ConversationMode.BIRTH_COLLECTION.value:
            # Encourage providing birth details
            actions = [
                SuggestedAction(id='help_dob', label='How to find my birth time?'),
                SuggestedAction(id='example_format', label='Show example format'),
            ]
        
        elif mode == ConversationMode.PAST_THEMES.value:
            # After past themes, suggest focus areas
            actions = [
                SuggestedAction(id='focus_career', label='Ask about career'),
                SuggestedAction(id='focus_relationship', label='Ask about relationships'),
                SuggestedAction(id='focus_health', label='Ask about health'),
                SuggestedAction(id='daily_guidance', label='Daily guidance'),
            ]
        
        elif mode == ConversationMode.FOCUS_READING.value:
            # Context-aware suggestions based on current focus
            if focus == 'career':
                actions = [
                    SuggestedAction(id='ask_timing', label='Timing for key changes'),
                    SuggestedAction(id='deep_dive', label='Go deeper on career'),
                    SuggestedAction(id='focus_finance', label='Ask about finances'),
                    SuggestedAction(id='daily_guidance', label='Daily guidance'),
                ]
            elif focus == 'relationship':
                actions = [
                    SuggestedAction(id='ask_timing', label='Timing for relationships'),
                    SuggestedAction(id='deep_dive', label='Go deeper on love'),
                    SuggestedAction(id='compatibility', label='Compatibility insights'),
                    SuggestedAction(id='focus_career', label='Ask about career'),
                ]
            elif focus == 'health':
                actions = [
                    SuggestedAction(id='wellness_tips', label='Wellness recommendations'),
                    SuggestedAction(id='deep_dive', label='Go deeper on health'),
                    SuggestedAction(id='focus_career', label='Ask about career'),
                    SuggestedAction(id='daily_guidance', label='Daily guidance'),
                ]
            else:
                actions = [
                    SuggestedAction(id='focus_career', label='Career insights'),
                    SuggestedAction(id='focus_relationship', label='Relationships'),
                    SuggestedAction(id='ask_timing', label='Best timing'),
                    SuggestedAction(id='daily_guidance', label='Daily guidance'),
                ]
        
        elif mode == ConversationMode.DAILY_GUIDANCE.value:
            actions = [
                SuggestedAction(id='weekly_outlook', label='This week\'s outlook'),
                SuggestedAction(id='focus_career', label='Career insights'),
                SuggestedAction(id='focus_relationship', label='Relationships'),
                SuggestedAction(id='past_themes', label='Review past 2 years'),
            ]
        
        else:  # GENERAL_GUIDANCE
            actions = [
                SuggestedAction(id='focus_career', label='Career'),
                SuggestedAction(id='focus_relationship', label='Relationships'),
                SuggestedAction(id='focus_health', label='Health'),
                SuggestedAction(id='daily_guidance', label='Daily guidance'),
            ]
        
        return actions
    
    def _try_extract_birth_details(self, message: str) -> Optional[BirthDetails]:
        """
        Try to extract birth details from a message.
        
        This is a simple extraction - for production, use NLP or LLM.
        
        Args:
            message: User message text
            
        Returns:
            BirthDetails if found, None otherwise
        """
        import re
        
        # Simple patterns for date extraction
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD
        ]
        
        # Time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',  # HH:MM am/pm
            r'(\d{1,2})\s*(am|pm)',  # H am/pm
        ]
        
        # Location patterns (simple - city names)
        location_patterns = [
            r'(?:born in|from|at|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        dob = None
        tob = None
        location = None
        
        # Try to extract date
        for pattern in date_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups[0]) == 4:  # YYYY-MM-DD
                    dob = f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                else:  # DD-MM-YYYY
                    dob = f"{groups[2]}-{groups[1].zfill(2)}-{groups[0].zfill(2)}"
                break
        
        # Try to extract time
        for pattern in time_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                groups = match.groups()
                hour = int(groups[0])
                minute = int(groups[1]) if len(groups) > 1 and groups[1] else 0
                meridiem = groups[-1].lower() if groups[-1] else None
                
                if meridiem == 'pm' and hour != 12:
                    hour += 12
                elif meridiem == 'am' and hour == 12:
                    hour = 0
                
                tob = f"{hour:02d}:{minute:02d}"
                break
        
        # Try to extract location
        for pattern in location_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                location = match.group(1)
                break
        
        # Only return if we have all three
        if dob and tob and location:
            logger.info(f"Extracted: dob={dob}, tob={tob}, location={location}")
            return BirthDetails(dob=dob, tob=tob, location=location)
        
        return None
    
    def set_birth_details(
        self,
        session_id: str,
        birth_details: BirthDetails
    ) -> bool:
        """
        Manually set birth details for a session.
        
        Args:
            session_id: Session identifier
            birth_details: Birth details to set
            
        Returns:
            True if successful
        """
        state = self.session_store.get(session_id)
        if state:
            state.birth_details = birth_details
            self.session_store.set(session_id, state)
            logger.info(f"Set birth details for session {session_id}")
            return True
        return False
    
    def get_session_state(self, session_id: str) -> Optional[ConversationState]:
        """Get current state for a session"""
        return self.session_store.get(session_id)
    
    def reset_session(self, session_id: str) -> bool:
        """Reset a session to initial state"""
        return self.session_store.delete(session_id)
