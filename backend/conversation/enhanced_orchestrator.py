"""Enhanced Conversation Orchestrator for NIRO

Integrates:
- Session state management
- Mode/topic routing
- Vedic API for astro profiles and transits
- Topic classification and chart lever mapping
- NIRO LLM with structured astro_features
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
import logging
import os
from pathlib import Path
import re
import json

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
from .birth_extractor import HybridBirthDetailsExtractor
from .timeframe_classifier import classify_timeframe

# Import from astro_client package (go up one level: ..astro_client)
from ..astro_client import (
    BirthDetails as AstroBirthDetails,
    AstroProfile,
    AstroTransits,
    get_astro_profile,
    save_astro_profile,
    get_astro_transits,
    get_or_refresh_transits,
    save_astro_transits,
    classify_topic,
    Topic,
    build_astro_features,
    call_niro_llm
)
from ..astro_client.vedic_api import vedic_api_client

logger = logging.getLogger(__name__)

# NIRO pipeline logger (separate file handler)
# Use workspace-local logs directory at repo root: <repo>/logs
repo_root = Path(__file__).resolve().parents[2]
logs_dir = repo_root / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)
niro_logger = logging.getLogger("niro_pipeline")
niro_logger.setLevel(logging.INFO)
if not niro_logger.handlers:
    handler = logging.FileHandler(logs_dir / "niro_pipeline.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    niro_logger.addHandler(handler)


class EnhancedOrchestrator:
    """
    Enhanced orchestrator for NIRO conversations.
    
    Flow:
    1. Load/create session state
    2. Route mode
    3. Classify topic
    4. Ensure astro profile + transits exist
    5. Build topic-specific astro_features
    6. Call NIRO LLM with structured payload
    7. Return response
    """
    
    def __init__(
        self,
        session_store: Optional[SessionStore] = None,
        mode_router: Optional[ModeRouter] = None
    ):
        self.session_store = session_store or InMemorySessionStore()
        self.mode_router = mode_router or ModeRouter()
        self.birth_extractor = HybridBirthDetailsExtractor()
        
        logger.info("EnhancedOrchestrator initialized")
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message and generate response.
        
        Args:
            request: ChatRequest with sessionId, message, actionId, subjectData
            
        Returns:
            ChatResponse with reply, mode, focus/topic, suggestedActions
        """
        logger.info(f"Processing message for session {request.sessionId}")
        now = datetime.utcnow()
        niro_logger.info(f"[START] session={request.sessionId} message='{request.message}'")
        
        # Step 1: Load or create session state
        state = self.session_store.get_or_create(request.sessionId)
        state.message_count += 1
        
        logger.info(
            "PIPELINE_START: session=%s msg=%r message_count=%s",
            request.sessionId,
            request.message,
            state.message_count
        )
        
        # Handle birth details from subjectData or message
        if request.subjectData and request.subjectData.get('birthDetails'):
            bd = request.subjectData['birthDetails']
            state.birth_details = ConvBirthDetails(
                dob=bd.get('dob'),
                tob=bd.get('tob'),
                location=bd.get('location'),
                latitude=bd.get('latitude'),
                longitude=bd.get('longitude'),
                timezone=bd.get('timezone')
            )
            logger.info(f"Set birth details from subjectData for session {request.sessionId}")
        elif state.birth_details is None:
            extracted_details = self._extract_birth_details(request.message)
            if extracted_details:
                state.birth_details = extracted_details
                logger.info(f"Extracted birth details from message for session {request.sessionId}")
                niro_logger.info(f"[BIRTH EXTRACTION] extracted={bool(state.birth_details)}\ndetails={state.birth_details}")
        
        # Step 2: Route mode
        mode = self.mode_router.route_mode(
            state=state,
            user_message=request.message,
            action_id=request.actionId
        )[0]
        
        # Step 3: Classify topic
        topic = classify_topic(
            user_message=request.message,
            action_id=request.actionId,
            current_topic=state.focus
        )
        
        # Update state
        state.mode = ConversationMode(mode)
        state.focus = topic
        
        logger.info(f"Routed to mode={mode}, topic={topic}")
        niro_logger.info(f"[ROUTING] mode={mode} topic={topic}")
        
        # Step 4: Ensure astro profile and transits (if birth details available)
        profile = None
        transits = None
        astro_features = {}
        
        if state.birth_details and mode != ConversationMode.NEED_BIRTH_DETAILS.value:
            try:
                # Convert conversation birth details to astro format
                astro_birth = self._convert_birth_details(state.birth_details)
                user_id = request.sessionId
                
                # Get or fetch profile
                niro_logger.info("[PROFILE] fetching or loading cached profile")
                profile = await get_astro_profile(user_id)
                if not profile:
                    logger.info(f"Fetching new astro profile for {user_id}")
                    profile = await vedic_api_client.fetch_full_profile(astro_birth, user_id)
                    await save_astro_profile(profile)
                    logger.debug("RAW_ASTRO_PROFILE: %s", profile.model_dump_json()[:5000])
                
                # Get or refresh transits (automatically fetches if stale or missing)
                niro_logger.info("[TRANSITS] fetching or loading cached transits")
                transits = await get_or_refresh_transits(user_id, astro_birth, now)
                logger.debug("RAW_ASTRO_TRANSITS: %s", transits.model_dump_json()[:5000])
                
                # Classify timeframe from user question
                timeframe = classify_timeframe(request.message)
                niro_logger.info(f"[TIMEFRAME] detected={timeframe['description']} horizon_months={timeframe['horizon_months']}")
                
                # Step 5: Build topic-specific astro_features with timeframe hint
                astro_features = build_astro_features(
                    profile=profile,
                    transits=transits,
                    mode=mode,
                    topic=topic,
                    now=now,
                    timeframe_hint=timeframe
                )
                
                logger.debug(
                    "ASTRO_FEATURES_SNAPSHOT: %s",
                    json.dumps(astro_features, default=str)[:5000]
                )
                
                logger.info(f"Built astro_features with {len(astro_features.get('focus_factors', []))} focus factors")
                niro_logger.info(f"[ASTRO FEATURES] built keys={list(astro_features.keys())}\nfocus_factors={astro_features.get('focus_factors')}")
                
            except Exception as e:
                logger.error(f"Error building astro features: {e}", exc_info=True)
        
        # Step 6: Build LLM payload and generate response
        llm_payload = {
            'mode': mode,
            'topic': topic,
            'user_question': request.message,
            'astro_features': astro_features,
            'session_id': request.sessionId,
            'timestamp': now.isoformat() + 'Z'
        }
        niro_logger.info(f"[LLM INPUT] payload={llm_payload}")

        llm_response = call_niro_llm(llm_payload)
        niro_logger.info(f"[LLM OUTPUT] reply={llm_response}")
        
        # Step 7: Build suggested actions
        suggested_actions = self._build_suggested_actions(mode, topic)
        
        # Update state
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
            focus=topic,
            suggestedActions=suggested_actions
        )
        
        logger.info(
            "PIPELINE_END: session=%s final_mode=%s final_focus=%s feature_keys=%s",
            request.sessionId,
            mode,
            topic,
            list(astro_features.keys()) if astro_features else None
        )
        
        logger.info(f"Response generated: mode={mode}, topic={topic}")
        niro_logger.info(f"[END] session={request.sessionId}")
        return response
    
    def _convert_birth_details(self, conv_birth: ConvBirthDetails) -> AstroBirthDetails:
        """Convert conversation birth details to astro_client format."""
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
        """Extract birth details using the hybrid extractor (regex-first, LLM fallback)."""
        return self.birth_extractor.extract(message)
    
    def _build_suggested_actions(self, mode: str, topic: str) -> List[SuggestedAction]:
        """Build suggested follow-up actions based on mode and topic."""
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
            if topic == Topic.CAREER.value:
                actions = [
                    SuggestedAction(id='ask_timing', label='Best timing for changes'),
                    SuggestedAction(id='deep_dive', label='Go deeper on career'),
                    SuggestedAction(id='focus_money', label='Ask about money'),
                ]
            elif topic in [Topic.ROMANTIC_RELATIONSHIPS.value, Topic.MARRIAGE_PARTNERSHIP.value]:
                actions = [
                    SuggestedAction(id='ask_timing', label='Timing for relationships'),
                    SuggestedAction(id='deep_dive', label='Go deeper on love'),
                    SuggestedAction(id='focus_career', label='Ask about career'),
                ]
            else:
                actions = [
                    SuggestedAction(id='focus_career', label='Career'),
                    SuggestedAction(id='focus_relationship', label='Relationships'),
                    SuggestedAction(id='focus_money', label='Money'),
                ]
        else:
            actions = [
                SuggestedAction(id='focus_career', label='Career'),
                SuggestedAction(id='focus_relationship', label='Relationships'),
                SuggestedAction(id='focus_money', label='Money'),
            ]
        
        return actions
    
    def set_birth_details(self, session_id: str, birth_details: ConvBirthDetails) -> bool:
        """Manually set birth details for a session."""
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


def create_enhanced_orchestrator() -> EnhancedOrchestrator:
    """Create and return an EnhancedOrchestrator instance"""
    return EnhancedOrchestrator()
