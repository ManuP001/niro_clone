"""
Enhanced Conversation Orchestrator for NIRO

Integrates:
- Session state management
- Mode/topic routing
- Vedic API for astro profiles and transits
- Topic classification and chart lever mapping
- NIRO LLM with structured astro_features
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
import logging
import re

from .models import (
    ConversationState,
    ConversationMode,
    BirthDetails as ConvBirthDetails,
    SuggestedAction,
    NiroReply,
    ChatRequest,
    ChatResponse
)
from .session_store import SessionStore, InMemorySessionStore
from .mode_router import ModeRouter

# Import from astro_client package
from astro_client import (
    BirthDetails as AstroBirthDetails,
    AstroProfile,
    AstroTransits,
    VedicAPIClient,
    ensure_profile_and_transits,
    get_astro_profile,
    save_astro_profile,
    classify_topic,
    classify_topic_llm,
    TopicClassificationResult,
    Topic,
    ACTION_TO_TOPIC,
    build_astro_features,
    call_niro_llm
)

logger = logging.getLogger(__name__)


class EnhancedOrchestrator:
    """
    Enhanced orchestrator for NIRO conversations.
    
    Flow:
    1. Load/create session state
    2. Extract birth details if provided
    3. Route to mode and classify topic
    4. Ensure astro profile and transits
    5. Build topic-specific astro_features
    6. Call NIRO LLM with payload
    7. Build suggested actions
    8. Return structured response
    """
    
    def __init__(
        self,
        session_store: Optional[SessionStore] = None,
        mode_router: Optional[ModeRouter] = None,
        vedic_client: Optional[VedicAPIClient] = None
    ):
        """
        Initialize orchestrator with components.
        
        Args:
            session_store: Session storage backend
            mode_router: Mode routing logic
            vedic_client: Vedic API client for chart calculations
        """
        self.session_store = session_store or InMemorySessionStore()
        self.mode_router = mode_router or ModeRouter()
        self.vedic_client = vedic_client or VedicAPIClient()
        
        logger.info("EnhancedOrchestrator initialized")
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message and generate response.
        
        Args:
            request: ChatRequest with sessionId, message, actionId
            
        Returns:
            ChatResponse with reply, mode, focus/topic, suggestedActions
        """
        logger.info(f"Processing message for session {request.sessionId}")
        now = datetime.utcnow()
        
        # Step 1: Load or create session state
        state = self.session_store.get_or_create(request.sessionId)
        state.message_count += 1
        
        # Step 2: Try to extract birth details from message
        if state.birth_details is None:
            extracted_details = self._extract_birth_details(request.message)
            if extracted_details:
                state.birth_details = extracted_details
                logger.info(f"Extracted birth details for session {request.sessionId}")
        
        # Step 3: Route mode and classify topic
        mode, _ = self.mode_router.route_mode(
            state=state,
            user_message=request.message,
            action_id=request.actionId
        )
        
        # Classify topic (richer taxonomy)
        topic = classify_topic(
            user_message=request.message,
            action_id=request.actionId,
            current_topic=state.focus  # Use focus as current topic
        )
        
        # Update state
        state.mode = ConversationMode(mode)
        state.focus = topic  # Store topic in focus field
        
        logger.info(f"Routed to mode={mode}, topic={topic}")
        
        # Step 4: Ensure astro profile and transits (if birth details available)
        astro_features = {}
        profile = None
        transits = None
        
        if state.birth_details and mode != ConversationMode.BIRTH_COLLECTION.value:
            try:
                # Convert conversation birth details to astro format
                astro_birth = self._convert_birth_details(state.birth_details)
                
                # Ensure profile and transits exist
                profile, transits = await ensure_profile_and_transits(
                    user_id=request.sessionId,
                    birth=astro_birth,
                    now=now
                )
                
                # Step 5: Build topic-specific astro_features
                astro_features = build_astro_features(
                    profile=profile,
                    transits=transits,
                    mode=mode,
                    topic=topic,
                    now=now
                )
                
                logger.info(f"Built astro_features with {len(astro_features.get('focus_factors', []))} focus factors")
                
            except Exception as e:
                logger.error(f"Error building astro features: {e}", exc_info=True)
                # Continue with empty features - LLM will handle gracefully
        
        # Step 6: Build LLM payload and generate response
        payload = {
            'mode': mode,
            'topic': topic,
            'user_question': request.message,
            'astro_features': astro_features
        }
        
        llm_response = call_niro_llm(payload)
        
        # Step 7: Build suggested actions based on mode and topic
        suggested_actions = self._build_suggested_actions(mode, topic)
        
        # Step 8: Update state
        if mode == ConversationMode.PAST_THEMES.value:
            state.has_done_retro = True
        
        self.session_store.set(request.sessionId, state)
        
        # Build and return response
        reply = NiroReply(
            rawText=llm_response.get('rawText', ''),
            summary=llm_response.get('summary', ''),
            reasons=llm_response.get('reasons', []),
            remedies=llm_response.get('remedies', [])
        )
        
        response = ChatResponse(
            reply=reply,
            mode=mode,
            focus=topic,  # Return topic as focus for backward compatibility
            suggestedActions=suggested_actions
        )
        
        logger.info(f"Response generated: mode={mode}, topic={topic}")
        return response
    
    def _convert_birth_details(self, conv_birth: ConvBirthDetails) -> AstroBirthDetails:
        """
        Convert conversation birth details to astro_client format.
        """
        # Parse dob string to date if needed
        dob = conv_birth.dob
        if isinstance(dob, str):
            dob = date.fromisoformat(dob)
        
        return AstroBirthDetails(
            dob=dob,
            tob=conv_birth.tob,
            location=conv_birth.location,
            latitude=conv_birth.latitude,
            longitude=conv_birth.longitude,
            timezone=conv_birth.timezone or 5.5
        )
    
    def _extract_birth_details(self, message: str) -> Optional[ConvBirthDetails]:
        """
        Try to extract birth details from a message.
        """
        # Date patterns
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD
        ]
        
        # Time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',  # HH:MM am/pm
            r'(\d{1,2})\s*(am|pm)',  # H am/pm
        ]
        
        # Location patterns
        location_patterns = [
            r'(?:born in|from|at|in)\s+([A-Z][a-zA-Z]+(?:[\s,]+[A-Z][a-zA-Z]+)*)',
        ]
        
        dob = None
        tob = None
        location = None
        
        # Extract date
        for pattern in date_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups[0]) == 4:  # YYYY-MM-DD
                    dob = f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                else:  # DD-MM-YYYY
                    dob = f"{groups[2]}-{groups[1].zfill(2)}-{groups[0].zfill(2)}"
                break
        
        # Extract time
        for pattern in time_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                groups = match.groups()
                hour = int(groups[0])
                minute = int(groups[1]) if len(groups) > 1 and groups[1] and groups[1].isdigit() else 0
                meridiem = groups[-1].lower() if groups[-1] and groups[-1].lower() in ['am', 'pm'] else None
                
                if meridiem == 'pm' and hour != 12:
                    hour += 12
                elif meridiem == 'am' and hour == 12:
                    hour = 0
                
                tob = f"{hour:02d}:{minute:02d}"
                break
        
        # Extract location
        for pattern in location_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                break
        
        # Only return if we have all three
        if dob and tob and location:
            logger.info(f"Extracted: dob={dob}, tob={tob}, location={location}")
            return ConvBirthDetails(
                dob=dob,
                tob=tob,
                location=location
            )
        
        return None
    
    def _build_suggested_actions(self, mode: str, topic: str) -> List[SuggestedAction]:
        """
        Build suggested follow-up actions based on mode and topic.
        """
        actions = []
        
        if mode == ConversationMode.BIRTH_COLLECTION.value:
            actions = [
                SuggestedAction(id='help_dob', label='How to find my birth time?'),
                SuggestedAction(id='example_format', label='Show example format'),
            ]
        
        elif mode == ConversationMode.PAST_THEMES.value:
            actions = [
                SuggestedAction(id='focus_career', label='Career insights'),
                SuggestedAction(id='focus_relationship', label='Relationships'),
                SuggestedAction(id='focus_money', label='Money & finances'),
                SuggestedAction(id='focus_health', label='Health'),
            ]
        
        elif mode == ConversationMode.FOCUS_READING.value:
            # Topic-specific suggestions
            if topic == Topic.CAREER.value:
                actions = [
                    SuggestedAction(id='ask_timing', label='Best timing for changes'),
                    SuggestedAction(id='deep_dive', label='Go deeper on career'),
                    SuggestedAction(id='focus_money', label='Ask about money'),
                    SuggestedAction(id='daily_guidance', label='Daily guidance'),
                ]
            elif topic in [Topic.ROMANTIC_RELATIONSHIPS.value, Topic.MARRIAGE_PARTNERSHIP.value]:
                actions = [
                    SuggestedAction(id='ask_timing', label='Timing for relationships'),
                    SuggestedAction(id='deep_dive', label='Go deeper on love'),
                    SuggestedAction(id='compatibility', label='Compatibility insights'),
                    SuggestedAction(id='focus_career', label='Ask about career'),
                ]
            elif topic == Topic.MONEY.value:
                actions = [
                    SuggestedAction(id='ask_timing', label='Best timing for investments'),
                    SuggestedAction(id='deep_dive', label='Go deeper on finances'),
                    SuggestedAction(id='focus_career', label='Career & income'),
                    SuggestedAction(id='daily_guidance', label='Daily guidance'),
                ]
            elif topic == Topic.HEALTH_ENERGY.value:
                actions = [
                    SuggestedAction(id='wellness_tips', label='Wellness recommendations'),
                    SuggestedAction(id='deep_dive', label='Go deeper on health'),
                    SuggestedAction(id='focus_career', label='Ask about career'),
                    SuggestedAction(id='daily_guidance', label='Daily guidance'),
                ]
            else:
                actions = [
                    SuggestedAction(id='focus_career', label='Career'),
                    SuggestedAction(id='focus_relationship', label='Relationships'),
                    SuggestedAction(id='focus_money', label='Money'),
                    SuggestedAction(id='daily_guidance', label='Daily guidance'),
                ]
        
        elif mode == ConversationMode.DAILY_GUIDANCE.value:
            actions = [
                SuggestedAction(id='weekly_outlook', label='This week\'s outlook'),
                SuggestedAction(id='focus_career', label='Career today'),
                SuggestedAction(id='focus_relationship', label='Love today'),
                SuggestedAction(id='past_themes', label='Review past 2 years'),
            ]
        
        else:  # GENERAL_GUIDANCE
            actions = [
                SuggestedAction(id='focus_career', label='Career'),
                SuggestedAction(id='focus_relationship', label='Relationships'),
                SuggestedAction(id='focus_money', label='Money'),
                SuggestedAction(id='daily_guidance', label='Daily guidance'),
            ]
        
        return actions
    
    def set_birth_details(
        self,
        session_id: str,
        birth_details: ConvBirthDetails
    ) -> bool:
        """
        Manually set birth details for a session.
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
    
    async def get_astro_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the astro profile for a session (if exists).
        """
        profile = await get_astro_profile(session_id)
        if profile:
            return {
                'user_id': profile.user_id,
                'ascendant': profile.ascendant,
                'moon_sign': profile.moon_sign,
                'sun_sign': profile.sun_sign,
                'current_mahadasha': profile.current_mahadasha.planet if profile.current_mahadasha else None,
                'current_antardasha': profile.current_antardasha.planet if profile.current_antardasha else None,
                'yogas_count': len(profile.yogas),
                'created_at': profile.created_at.isoformat()
            }
        return None


# Factory function to create orchestrator
def create_enhanced_orchestrator() -> EnhancedOrchestrator:
    """Create and return an EnhancedOrchestrator instance"""
    return EnhancedOrchestrator()
