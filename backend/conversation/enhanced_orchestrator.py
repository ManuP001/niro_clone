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
from .intent import detect_intent_and_context

# Import from astro_client package (use absolute imports for compatibility)
from backend.astro_client import (
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
from backend.astro_client.vedic_api import vedic_api_client
from backend.astro_client.reading_pack import build_reading_pack
from backend.observability.data_coverage import (
    validate_api_profile,
    validate_api_transits,
    validate_astro_features,
)
from backend.observability.pipeline_logger import (
    make_request_id,
    safe_truncate,
    write_snapshot,
    log_stage,
    detect_missing_data_phrases,
)
from backend.observability.time_context import infer_time_context

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
        # STAGE A: START - Generate request ID and log initialization
        request_id = make_request_id()
        now = datetime.utcnow()
        
        # Detect intent and time context (lightweight, no LLM)
        intent_info = detect_intent_and_context(request.message)
        time_context = intent_info['time_context']
        intent = intent_info['intent']
        
        log_stage(
            "START",
            request.sessionId,
            request_id,
            user_message=safe_truncate(request.message, 300),
            time_context=time_context,
            intent=intent,
            action_id=request.actionId or "null"
        )
        
        # Write input snapshot if debug enabled
        write_snapshot(
            "input_payload",
            request.sessionId,
            request_id,
            {
                "message": request.message,
                "actionId": request.actionId,
                "subjectData": request.subjectData,
                "time_context": time_context,
            },
            force=False
        )
        
        logger.info(f"Processing message for session {request.sessionId} request={request_id}")
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
        extraction_method = "none"
        extracted = False
        extraction_confidence = None
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
            extraction_method = "subjectData"
            extracted = True
            logger.info(f"Set birth details from subjectData for session {request.sessionId}")
        elif state.birth_details is None:
            extracted_details = self._extract_birth_details(request.message)
            if extracted_details:
                state.birth_details = extracted_details
                extraction_method = "regex"  # Default extractor is regex-first
                extracted = True
                logger.info(f"Extracted birth details from message for session {request.sessionId}")
            else:
                extraction_method = "none"
        else:
            extraction_method = "previous_state"
            extracted = True
        
        # STAGE B: BIRTH_EXTRACTION - Log extraction results
        if state.birth_details:
            log_stage(
                "BIRTH_EXTRACTION",
                request.sessionId,
                request_id,
                extracted=extracted,
                extraction_method=extraction_method,
                dob=state.birth_details.dob,
                tob=state.birth_details.tob,
                location=state.birth_details.location,
                confidence=extraction_confidence or "N/A"
            )
            
            # Write snapshot if extraction failed or debug enabled
            write_snapshot(
                "birth_extraction",
                request.sessionId,
                request_id,
                {
                    "extracted": extracted,
                    "method": extraction_method,
                    "birth_details": {
                        "dob": str(state.birth_details.dob),
                        "tob": state.birth_details.tob,
                        "location": state.birth_details.location,
                    }
                },
                force=False
            )
        else:
            log_stage(
                "BIRTH_EXTRACTION",
                request.sessionId,
                request_id,
                extracted="false",
                extraction_method="none",
                confidence="N/A"
            )
        
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
        
        # STAGE C: ROUTING / TOPIC
        log_stage(
            "ROUTING",
            request.sessionId,
            request_id,
            mode=mode,
            topic=topic,
            time_context=time_context,
            intent=intent
        )
        
        logger.info(f"Routed to mode={mode}, topic={topic}, intent={intent}")
        niro_logger.info(f"[ROUTING] mode={mode} topic={topic} time_context={time_context} intent={intent}")
        
        # Step 4: Ensure astro profile and transits (if birth details available)
        profile = None
        transits = None
        astro_features = {}
        features_coverage = {"ok": 0, "missing": 0, "missing_keys": []}  # Default empty coverage
        profile_coverage = {"ok": 0, "missing": 0, "missing_keys": []}  # Default empty coverage
        transits_coverage = {"ok": 0, "missing": 0, "missing_keys": []}  # Default empty coverage
        
        if state.birth_details and mode != ConversationMode.NEED_BIRTH_DETAILS.value:
            try:
                # Convert conversation birth details to astro format
                astro_birth = self._convert_birth_details(state.birth_details)
                user_id = request.sessionId
                
                # STAGE D: API_REQUEST_PROFILE
                log_stage(
                    "API_PROFILE_REQ",
                    request.sessionId,
                    request_id,
                    dob=astro_birth.dob,
                    tob=astro_birth.tob,
                    location=astro_birth.location,
                    timezone=astro_birth.timezone
                )
                
                # Get or fetch profile
                niro_logger.info("[PROFILE] fetching or loading cached profile")
                profile = await get_astro_profile(user_id)
                if not profile:
                    logger.info(f"Fetching new astro profile for {user_id}")
                    profile = await vedic_api_client.fetch_full_profile(astro_birth, user_id)
                    await save_astro_profile(profile)
                    logger.debug("RAW_ASTRO_PROFILE: %s", profile.model_dump_json()[:5000])
                
                # STAGE D (continued): API_PROFILE_RES with coverage validation
                profile_coverage = validate_api_profile(
                    profile,
                    session_id=user_id,
                    logs_dir=logs_dir
                )
                
                # Log coverage results
                log_stage(
                    "API_PROFILE_RES",
                    request.sessionId,
                    request_id,
                    ok=profile_coverage['ok'],
                    missing=profile_coverage['missing'],
                    missing_count=len(profile_coverage['missing_keys']),
                    missing_keys=str(profile_coverage['missing_keys'][:5]),  # First 5
                    present_keys=str(list(profile.model_dump().keys())[:5])  # Sample
                )
                
                niro_logger.info(
                    f"[DATA COVERAGE] session={user_id} stage=api_profile ok={profile_coverage['ok']} "
                    f"missing={profile_coverage['missing']} missing_keys={profile_coverage['missing_keys']}"
                )
                
                # Write detailed snapshot if missing data
                if profile_coverage['missing'] > 0:
                    write_snapshot(
                        "api_profile_response",
                        request.sessionId,
                        request_id,
                        {
                            "coverage": profile_coverage,
                            "birth_details": {
                                "dob": str(profile.birth_details.dob),
                                "tob": profile.birth_details.tob,
                                "location": profile.birth_details.location,
                            },
                            "core_signs": {
                                "ascendant": profile.ascendant,
                                "moon_sign": profile.moon_sign,
                                "sun_sign": profile.sun_sign,
                            },
                            "sample_planets": [
                                {"planet": p.planet, "sign": p.sign}
                                for p in (profile.planets[:2] if profile.planets else [])
                            ],
                            "sample_houses": [
                                {"house": h.house_num, "sign": h.sign}
                                for h in (profile.houses[:2] if profile.houses else [])
                            ],
                        },
                        force=True
                    )
                
                # STAGE E: API_TRANSITS_REQ / RES
                log_stage(
                    "API_TRANSITS_REQ",
                    request.sessionId,
                    request_id,
                    date_range=f"{now.date()}"
                )
                
                # Get or refresh transits (automatically fetches if stale or missing)
                # Transits are optional - gracefully handle failures
                niro_logger.info("[TRANSITS] fetching or loading cached transits")
                transits = None
                transits_coverage = {'ok': 0, 'missing': 0, 'missing_keys': []}
                
                try:
                    transits = await get_or_refresh_transits(user_id, astro_birth, now)
                    logger.debug("RAW_ASTRO_TRANSITS: %s", transits.model_dump_json()[:5000])
                    
                    # Validate API transits data coverage
                    transits_coverage = validate_api_transits(
                        transits,
                        session_id=user_id,
                        logs_dir=logs_dir
                    )
                except Exception as te:
                    logger.warning(f"[TRANSITS] Failed to fetch transits (non-blocking): {te}")
                    niro_logger.info(f"[TRANSITS] Skipping transits due to error: {te}")
                    # Create empty transits object
                    from backend.astro_client.models import TransitsData
                    transits = TransitsData(events=[], data_available=False)
                
                log_stage(
                    "API_TRANSITS_RES",
                    request.sessionId,
                    request_id,
                    ok=transits_coverage['ok'],
                    missing=transits_coverage['missing'],
                    event_count=len(transits.events) if transits.events else 0
                )
                
                niro_logger.info(
                    f"[DATA COVERAGE] session={user_id} stage=api_transits ok={transits_coverage['ok']} "
                    f"missing={transits_coverage['missing']} missing_keys={transits_coverage['missing_keys']}"
                )
                
                # Write detailed snapshot if missing data
                if transits_coverage['missing'] > 0:
                    write_snapshot(
                        "api_transits_response",
                        request.sessionId,
                        request_id,
                        {
                            "coverage": transits_coverage,
                            "event_count": len(transits.events) if transits.events else 0,
                            "sample_events": [
                                {
                                    "planet": e.planet,
                                    "affected_house": e.affected_house,
                                    "start_date": str(e.start_date),
                                }
                                for e in (transits.events[:3] if transits.events else [])
                            ],
                        },
                        force=True
                    )
                
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
                
                # STAGE F: ASTRO_FEATURES validation
                features_coverage = validate_astro_features(
                    astro_features,
                    topic=topic,
                    session_id=user_id,
                    logs_dir=logs_dir
                )
                
                log_stage(
                    "FEATURES",
                    request.sessionId,
                    request_id,
                    ok=features_coverage['ok'],
                    missing=features_coverage['missing'],
                    focus_factors_count=len(astro_features.get('focus_factors', [])),
                    transits_count=len(astro_features.get('transits', [])),
                    key_rules_count=len(astro_features.get('key_rules', []))
                )
                
                niro_logger.info(
                    f"[DATA COVERAGE] session={user_id} stage=astro_features ok={features_coverage['ok']} "
                    f"missing={features_coverage['missing']} missing_keys={features_coverage['missing_keys']}"
                )
                
                # Write snapshot if missing data
                if features_coverage['missing'] > 0:
                    write_snapshot(
                        "astro_features",
                        request.sessionId,
                        request_id,
                        {
                            "coverage": features_coverage,
                            "ascendant": astro_features.get("ascendant"),
                            "moon_sign": astro_features.get("moon_sign"),
                            "sun_sign": astro_features.get("sun_sign"),
                            "mahadasha": astro_features.get("mahadasha"),
                            "antardasha": astro_features.get("antardasha"),
                            "focus_factors_sample": astro_features.get("focus_factors", [])[:3],
                            "transits_sample": astro_features.get("transits", [])[:3],
                            "key_rules_sample": astro_features.get("key_rules", [])[:3],
                        },
                        force=True
                    )
                
                logger.debug(
                    "ASTRO_FEATURES_SNAPSHOT: %s",
                    json.dumps(astro_features, default=str)[:5000]
                )
                
                logger.info(f"Built astro_features with {len(astro_features.get('focus_factors', []))} focus factors")
                niro_logger.info(f"[ASTRO FEATURES] built keys={list(astro_features.keys())}\nfocus_factors={astro_features.get('focus_factors')}")
                
            except Exception as e:
                logger.error(f"Error building astro features: {e}", exc_info=True)
                log_stage(
                    "FEATURES",
                    request.sessionId,
                    request_id,
                    error=safe_truncate(str(e), 200)
                )
        
        # Step 6: Build LLM payload and generate response
        # First, build the reading pack from astro_features and coverage results
        reading_pack = build_reading_pack(
            user_question=request.message,
            topic=topic,
            time_context=time_context,
            astro_features=astro_features,
            missing_keys=features_coverage.get('missing_keys', []),
            intent=intent
        )
        
        # Log signal scoring summary
        signal_scores = [s.get('score', 0) for s in reading_pack.get('signals', [])]
        logger.info(
            f"[SIGNAL_SCORING] topic={topic} kept={len(reading_pack.get('signals', []))} "
            f"total_signals_evaluated={sum(1 for s in astro_features.get('focus_factors', []))} "
            f"top_scores={signal_scores}"
        )
        
        # Build LLM payload with reading_pack
        llm_payload = {
            'mode': mode,
            'topic': topic,
            'time_context': time_context,
            'intent': intent,
            'user_question': request.message,
            'astro_features': astro_features,
            'reading_pack': reading_pack,
            'data_coverage': {
                'profile': profile_coverage if profile_coverage else {},
                'transits': transits_coverage if transits_coverage else {},
                'features': features_coverage
            },
            'session_id': request.sessionId,
            'timestamp': now.isoformat() + 'Z'
        }
        
        # STAGE G: LLM_PROMPT - Log prompt details before calling LLM
        # Get the actual prompt that will be sent (simplified for logging)
        llm_prompt_summary = {
            "model": "niro_llm",
            "payload_keys": list(llm_payload.keys()),
            "payload_hash": str(hash(json.dumps(llm_payload, default=str)))[:8],
        }
        
        log_stage(
            "LLM_PROMPT",
            request.sessionId,
            request_id,
            model="niro_llm",
            payload_size=len(json.dumps(llm_payload, default=str)),
            topic=topic,
            mode=mode
        )
        
        # Log reading pack summary
        log_stage(
            "READING_PACK",
            request.sessionId,
            request_id,
            signals=len(reading_pack.get('signals', [])),
            timing_windows=len(reading_pack.get('timing_windows', [])),
            gaps=len(reading_pack.get('data_gaps', []))
        )
        
        # Write full prompt snapshot if debug or missing data
        if features_coverage.get('missing', 0) > 0:
            write_snapshot(
                "llm_prompt",
                request.sessionId,
                request_id,
                {
                    "payload": llm_payload,
                    "features_coverage": features_coverage,
                },
                ext="txt",
                force=True
            )
        
        niro_logger.info(f"[LLM INPUT] payload={llm_payload}")

        llm_response = call_niro_llm(llm_payload)
        
        # STAGE H: LLM_OUTPUT
        output_text = str(llm_response.get('rawText', ''))
        has_missing_phrase = detect_missing_data_phrases(output_text)
        
        log_stage(
            "LLM_OUTPUT",
            request.sessionId,
            request_id,
            output_length=len(output_text),
            parse_success="true",
            contains_missing_phrase=has_missing_phrase
        )
        
        # QUALITY_ALERT: If features are complete but LLM claims missing data
        if features_coverage.get('missing', 0) == 0 and has_missing_phrase:
            log_stage(
                "QUALITY_ALERT",
                request.sessionId,
                request_id,
                reason="LLM_claims_missing_but_features_complete",
                features_ok=features_coverage['ok'],
                features_missing=features_coverage['missing']
            )
            
            write_snapshot(
                "quality_alert_missing_data",
                request.sessionId,
                request_id,
                {
                    "alert": "LLM output claims missing data despite complete features",
                    "llm_output": output_text,
                    "features_coverage": features_coverage,
                    "llm_payload": llm_payload,
                },
                ext="txt",
                force=True
            )
        
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
        
        # STAGE I: END - Log completion
        elapsed_ms = int((datetime.utcnow() - now).total_seconds() * 1000)
        
        log_stage(
            "END",
            request.sessionId,
            request_id,
            elapsed_ms=elapsed_ms,
            mode=mode,
            topic=topic,
            response_length=len(reply.rawText if reply.rawText else ""),
            profile_fetched=profile is not None,
            transits_fetched=transits is not None
        )
        
        logger.info(
            "PIPELINE_END: session=%s final_mode=%s final_focus=%s feature_keys=%s elapsed_ms=%s",
            request.sessionId,
            mode,
            topic,
            list(astro_features.keys()) if astro_features else None,
            elapsed_ms
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
        
        if mode == ConversationMode.NEED_BIRTH_DETAILS.value:
            actions = [
                SuggestedAction(id='help_dob', label='How to find my birth time?'),
                SuggestedAction(id='example_format', label='Show example format'),
            ]
        elif mode == ConversationMode.NORMAL_READING.value:
            # Topic-specific actions
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
                # Default actions for general reading
                actions = [
                    SuggestedAction(id='focus_career', label='Career'),
                    SuggestedAction(id='focus_relationship', label='Relationships'),
                    SuggestedAction(id='focus_money', label='Money'),
                ]
        else:
            # Fallback actions
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
