"""
Structured logging system for NIRO pipeline

Logs each /api/chat request as a JSON line capturing:
- Topic classification (source, confidence)
- Astro profile usage
- Astro transit usage
- Astro features summary
- LLM payload summary
- LLM response summary
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Log directory
LOG_DIR = Path("/app/logs")
PIPELINE_LOG_FILE = LOG_DIR / "niro_pipeline.log"


def ensure_log_directory():
    """Ensure logs directory exists"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_pipeline_event(event: Dict[str, Any]) -> None:
    """
    Log a pipeline event as a JSON line to logs/niro_pipeline.log
    and emit via standard logging at INFO level.
    
    Args:
        event: Dictionary containing pipeline event data
    """
    try:
        ensure_log_directory()
        
        # Add timestamp if not present
        if 'timestamp' not in event:
            event['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Write to JSON log file
        with open(PIPELINE_LOG_FILE, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        # Also emit via standard logging (for supervisord logs)
        logger.info(f"NIRO_PIPELINE: {json.dumps(event, separators=(',', ':'))}")
        
    except Exception as e:
        logger.error(f"Failed to log pipeline event: {e}")


def create_pipeline_log_entry(
    session_id: str,
    user_id: str,
    user_message: str,
    action_id: Optional[str],
    mode: str,
    topic_classification: Dict[str, Any],
    astro_profile: Optional[Dict[str, Any]] = None,
    astro_transits: Optional[Dict[str, Any]] = None,
    astro_features_summary: Optional[Dict[str, Any]] = None,
    llm_payload_summary: Optional[Dict[str, Any]] = None,
    llm_response_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a structured pipeline log entry.
    
    Args:
        session_id: Session identifier
        user_id: User identifier
        user_message: User's input message
        action_id: Action ID from chip click, if any
        mode: Current conversation mode
        topic_classification: Topic classification result
        astro_profile: Summary of astro profile usage
        astro_transits: Summary of astro transits usage
        astro_features_summary: Summary of astro features
        llm_payload_summary: Summary of LLM input payload
        llm_response_summary: Summary of LLM response
        
    Returns:
        Dictionary ready to be logged
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "session_id": session_id,
        "user_id": user_id or "anonymous",
        "user_message": user_message[:200] if user_message else "",  # Truncate long messages
        "action_id": action_id,
        "mode": mode,
        "topic_classification": topic_classification or {},
        "astro_profile": astro_profile or {"used_cached": False, "ascendant": None, "moon_sign": None},
        "astro_transits": astro_transits or {"used_cached": False, "events_count": 0},
        "astro_features_summary": astro_features_summary or {
            "has_features": False,
            "focus_factors_count": 0,
            "key_rules_ids": [],
            "timing_windows_count": 0
        },
        "llm_payload_summary": llm_payload_summary or {
            "mode": mode,
            "topic": topic_classification.get("topic", "unknown"),
            "has_astro_features": False
        },
        "llm_response_summary": llm_response_summary or {
            "summary_preview": "",
            "reasons_count": 0,
            "remedies_count": 0
        }
    }
    
    return entry


def summarize_astro_profile(profile) -> Dict[str, Any]:
    """
    Create summary of astro profile for logging.
    
    Args:
        profile: AstroProfile object or None
        
    Returns:
        Summary dict
    """
    if not profile:
        return {
            "used_cached": False,
            "ascendant": None,
            "moon_sign": None
        }
    
    return {
        "used_cached": True,
        "ascendant": getattr(profile, 'ascendant', None),
        "moon_sign": getattr(profile, 'moon_sign', None)
    }


def summarize_astro_transits(transits) -> Dict[str, Any]:
    """
    Create summary of astro transits for logging.
    
    Args:
        transits: AstroTransits object or None
        
    Returns:
        Summary dict
    """
    if not transits:
        return {
            "used_cached": False,
            "events_count": 0
        }
    
    events = getattr(transits, 'events', [])
    return {
        "used_cached": True,
        "events_count": len(events) if events else 0
    }


def summarize_astro_features(features) -> Dict[str, Any]:
    """
    Create summary of astro features for logging.
    
    Args:
        features: AstroFeatures object or dict
        
    Returns:
        Summary dict
    """
    if not features:
        return {
            "has_features": False,
            "focus_factors_count": 0,
            "key_rules_ids": [],
            "timing_windows_count": 0
        }
    
    # Handle both dict and object
    if isinstance(features, dict):
        focus_factors = features.get('focus_factors', [])
        key_rules = features.get('key_rules', [])
        timing_windows = features.get('timing_windows', [])
    else:
        focus_factors = getattr(features, 'focus_factors', [])
        key_rules = getattr(features, 'key_rules', [])
        timing_windows = getattr(features, 'timing_windows', [])
    
    return {
        "has_features": True,
        "focus_factors_count": len(focus_factors) if focus_factors else 0,
        "key_rules_ids": [r.get('id', 'unknown') if isinstance(r, dict) else str(i) 
                          for i, r in enumerate((key_rules or [])[:5])],  # First 5
        "timing_windows_count": len(timing_windows) if timing_windows else 0
    }


def summarize_llm_payload(mode: str, topic: str, has_features: bool) -> Dict[str, Any]:
    """
    Create summary of LLM input payload.
    
    Args:
        mode: Conversation mode
        topic: Topic
        has_features: Whether astro features were included
        
    Returns:
        Summary dict
    """
    return {
        "mode": mode,
        "topic": topic,
        "has_astro_features": has_features
    }


def summarize_llm_response(response) -> Dict[str, Any]:
    """
    Create summary of LLM response.
    
    Args:
        response: NiroResponse object or dict
        
    Returns:
        Summary dict
    """
    if not response:
        return {
            "summary_preview": "",
            "reasons_count": 0,
            "remedies_count": 0
        }
    
    # Handle both dict and object
    if isinstance(response, dict):
        summary = response.get('summary', '')
        reasons = response.get('reasons', [])
        remedies = response.get('remedies', [])
    else:
        summary = getattr(response, 'summary', '')
        reasons = getattr(response, 'reasons', [])
        remedies = getattr(response, 'remedies', [])
    
    return {
        "summary_preview": (summary or '')[:120],  # First 120 chars
        "reasons_count": len(reasons) if reasons else 0,
        "remedies_count": len(remedies) if remedies else 0
    }
