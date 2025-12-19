"""Centralized observability logger for NIRO pipeline

Provides structured logging, request ID generation, snapshot writing,
and safe truncation of data for debugging without exposing secrets.
"""

import uuid
import json
import logging
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

# Read config from environment
NIRO_DEBUG_LOGS = os.getenv("NIRO_DEBUG_LOGS", "").lower() in ("1", "true")

# Determine log directory - try /app/logs first, fall back to ./logs
_default_log_dir = "/app/logs"
try:
    Path(_default_log_dir).mkdir(parents=True, exist_ok=True)
    NIRO_LOG_DIR = Path(_default_log_dir)
except (OSError, PermissionError):
    # Fall back to local logs directory
    NIRO_LOG_DIR = Path(os.getcwd()) / "logs"

NIRO_LOG_DIR = Path(os.getenv("NIRO_LOG_DIR", str(NIRO_LOG_DIR)))

# Ensure log directory exists
try:
    NIRO_LOG_DIR.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    logger.warning(f"Cannot create log directory {NIRO_LOG_DIR}, will write to current dir")

# Get the niro_pipeline logger (initialized in enhanced_orchestrator)
niro_logger = logging.getLogger("niro_pipeline")


def make_request_id() -> str:
    """Generate a short unique request ID (UUID4 first 8 chars)"""
    return str(uuid.uuid4())[:8]


def safe_truncate(text: Optional[str], n: int = 300) -> str:
    """Safely truncate text to n chars, handle None"""
    if text is None:
        return ""
    text = str(text)
    if len(text) <= n:
        return text
    return text[:n] + "..."


def payload_hash(obj: Any) -> str:
    """Generate a short hash of a payload for deduplication"""
    try:
        text = json.dumps(obj, default=str, sort_keys=True)
        return hashlib.sha256(text.encode()).hexdigest()[:8]
    except:
        return "unknown"


def safe_json(obj: Any, max_depth: int = 2) -> Any:
    """Convert object to JSON-safe dict, limiting depth"""
    if obj is None:
        return None
    
    if isinstance(obj, (str, int, float, bool)):
        return obj
    
    if max_depth <= 0:
        return "<nested_too_deep>"
    
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            # Skip secrets
            if k.lower() in ("apikey", "api_key", "secret", "token", "password", "auth"):
                result[k] = "<redacted>"
            else:
                result[k] = safe_json(v, max_depth - 1)
        return result
    
    if isinstance(obj, (list, tuple)):
        return [safe_json(item, max_depth - 1) for item in obj]
    
    # Handle Pydantic models
    if hasattr(obj, "model_dump"):
        try:
            return safe_json(obj.model_dump(), max_depth - 1)
        except:
            pass
    
    if hasattr(obj, "__dict__"):
        try:
            return safe_json(obj.__dict__, max_depth - 1)
        except:
            pass
    
    try:
        return str(obj)
    except:
        return "<unserializable>"


def write_snapshot(
    kind: str,
    session_id: str,
    request_id: str,
    payload: Any,
    ext: str = "json",
    force: bool = False
) -> Optional[str]:
    """
    Write a snapshot file for debugging.
    
    Args:
        kind: Snapshot type (e.g., "api_profile_response", "llm_prompt")
        session_id: Session ID for correlation
        request_id: Request ID for correlation
        payload: Data to snapshot (will be truncated/minimized)
        ext: File extension (json or txt)
        force: If True, write even if NIRO_DEBUG_LOGS is False
        
    Returns:
        Path to written file, or None if not written
    """
    if not force and not NIRO_DEBUG_LOGS:
        return None
    
    timestamp = datetime.utcnow().isoformat().replace(":", "-")
    filename = f"{kind}_{session_id}_{request_id}_{timestamp}.{ext}"
    filepath = NIRO_LOG_DIR / filename
    
    try:
        if ext == "json":
            safe_payload = safe_json(payload)
            with open(filepath, "w") as f:
                json.dump(safe_payload, f, indent=2, default=str)
        else:  # txt
            text = str(payload)
            with open(filepath, "w") as f:
                f.write(text)
        
        logger.debug(f"Wrote snapshot: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Failed to write snapshot {kind}: {e}")
        return None


def log_stage(
    stage: str,
    session_id: str,
    request_id: str,
    **fields
) -> None:
    """
    Log a structured pipeline stage.
    
    Format: [STAGE_NAME] session=... request_id=... key=value key=value ...
    
    Args:
        stage: Stage name (START, BIRTH_EXTRACTION, ROUTING, etc.)
        session_id: Session ID
        request_id: Request ID
        **fields: Additional key=value pairs to log
    """
    # Build field strings, truncate long values
    field_strs = []
    for key, value in fields.items():
        if value is None:
            field_strs.append(f"{key}=null")
        elif isinstance(value, bool):
            field_strs.append(f"{key}={str(value).lower()}")
        elif isinstance(value, (int, float)):
            field_strs.append(f"{key}={value}")
        else:
            # Truncate strings/complex objects
            val_str = safe_truncate(str(value), 200)
            # Escape if contains spaces or special chars
            if " " in val_str or "=" in val_str:
                val_str = f'"{val_str}"'
            field_strs.append(f"{key}={val_str}")
    
    message = f"[{stage}] session={session_id} request_id={request_id} " + " ".join(field_strs)
    niro_logger.info(message)


def detect_missing_data_phrases(text: Optional[str]) -> bool:
    """Check if text contains phrases indicating missing data"""
    if not text:
        return False
    
    text_lower = text.lower()
    missing_phrases = [
        "missing astrological data",
        "missing data",
        "cannot assess due to missing",
        "not provided",
        "data not available",
        "insufficient data",
        "no data",
        "require.*data",  # regex
    ]
    
    for phrase in missing_phrases:
        if ".*" in phrase:  # regex pattern
            if re.search(phrase, text_lower):
                return True
        elif phrase in text_lower:
            return True
    
    return False
