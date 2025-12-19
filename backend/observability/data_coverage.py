"""Data Coverage Validator for NIRO Pipeline

Validates that astro profile, transits, and features contain required data.
Enables structured observability of data availability at each pipeline stage.
"""

from typing import Dict, List, Any, Optional, Union
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Define required paths for each data source
REQUIRED_PROFILE_PATHS = [
    "birth_details.dob",
    "birth_details.tob",
    "birth_details.location",
    "ascendant",
    "moon_sign",
    "sun_sign",
    "planets",
    "houses",
    "current_mahadasha.planet",
    "current_mahadasha.start_date",
    "current_mahadasha.end_date",
    "current_antardasha.planet",
    "current_antardasha.start_date",
    "current_antardasha.end_date",
]

REQUIRED_TRANSITS_PATHS = [
    "events",
    "events[0].planet",
    "events[0].affected_house",
    "events[0].start_date",
]

REQUIRED_FEATURES_PATHS = [
    "ascendant",
    "moon_sign",
    "sun_sign",
    "mahadasha.planet",
    "mahadasha.start_date",
    "antardasha.planet",
    "antardasha.start_date",
    "focus_factors",
    "transits",
]


def get_path(obj: Any, path: str) -> Optional[Any]:
    """
    Safely read a dotted or indexed path from an object.
    
    Supports:
    - Dotted paths: "birth_details.dob"
    - List indexing: "planets[0].name", "transits[0].planet"
    - Mixed: "data.items[2].value"
    
    Args:
        obj: Object to traverse (dict, list, or object with attributes)
        path: Dotted/indexed path string
        
    Returns:
        Value at path, or None if not found
    """
    if obj is None or not path:
        return None
    
    parts = []
    current = ""
    i = 0
    
    # Parse path into parts (handling brackets)
    while i < len(path):
        if path[i] == "[":
            if current:
                parts.append(("key", current))
                current = ""
            # Extract index
            j = i + 1
            while j < len(path) and path[j] != "]":
                j += 1
            index_str = path[i+1:j]
            try:
                index = int(index_str)
                parts.append(("index", index))
            except ValueError:
                # Not a valid index, skip
                pass
            i = j + 1
            if i < len(path) and path[i] == ".":
                i += 1
        elif path[i] == ".":
            if current:
                parts.append(("key", current))
                current = ""
            i += 1
        else:
            current += path[i]
            i += 1
    
    if current:
        parts.append(("key", current))
    
    # Traverse the parts
    current_val = obj
    for part_type, part_value in parts:
        if current_val is None:
            return None
        
        try:
            if part_type == "key":
                # Try dict access first
                if isinstance(current_val, dict):
                    current_val = current_val.get(part_value)
                else:
                    # Try attribute access
                    current_val = getattr(current_val, part_value, None)
            elif part_type == "index":
                if isinstance(current_val, (list, tuple)):
                    if part_value < len(current_val):
                        current_val = current_val[part_value]
                    else:
                        current_val = None
                else:
                    current_val = None
        except (KeyError, AttributeError, IndexError, TypeError):
            return None
    
    return current_val


def check_required(
    obj: Any,
    required_paths: List[str]
) -> Dict[str, Any]:
    """
    Check which required paths exist in an object.
    
    Args:
        obj: Object to check
        required_paths: List of required paths
        
    Returns:
        {
            "ok": int,           # Number of present paths
            "missing": int,      # Number of missing paths
            "missing_keys": list[str],  # Paths that are missing
            "present_keys": list[str],  # Paths that are present
        }
    """
    present = []
    missing = []
    
    for path in required_paths:
        value = get_path(obj, path)
        if value is not None:
            present.append(path)
        else:
            missing.append(path)
    
    return {
        "ok": len(present),
        "missing": len(missing),
        "missing_keys": missing,
        "present_keys": present,
    }


def _get_snapshot(obj: Any, max_list_items: int = 3) -> Dict[str, Any]:
    """
    Create a minimal JSON-safe snapshot of an object for logging.
    
    Includes top-level keys, first N items of lists, but NOT full payloads.
    
    Args:
        obj: Object to snapshot
        max_list_items: Maximum list items to include
        
    Returns:
        Simplified snapshot dict
    """
    if obj is None:
        return {}
    
    if isinstance(obj, dict):
        snapshot = {}
        for key, value in obj.items():
            if key.endswith("_raw") or key.startswith("_"):
                # Skip raw/private fields
                continue
            if isinstance(value, dict):
                snapshot[key] = f"<dict with {len(value)} keys>"
            elif isinstance(value, list):
                snapshot[key] = f"<list with {len(value)} items>"
                if value and max_list_items > 0:
                    try:
                        # Show first N items
                        snapshot[f"{key}_sample"] = [
                            str(v)[:100] for v in value[:max_list_items]
                        ]
                    except:
                        pass
            else:
                try:
                    snapshot[key] = str(value)[:200]
                except:
                    snapshot[key] = "<unserializable>"
        return snapshot
    elif isinstance(obj, list):
        return {
            "list_length": len(obj),
            "first_items": [str(v)[:100] for v in obj[:max_list_items]],
        }
    else:
        try:
            return {"value": str(obj)[:200]}
        except:
            return {"value": "<unserializable>"}


def _write_snapshot(
    stage: str,
    session_id: str,
    coverage: Dict[str, Any],
    obj: Any,
    logs_dir: Path = None
) -> Optional[str]:
    """
    Write a snapshot file if data is missing.
    
    Args:
        stage: Stage name (api_profile, api_transits, astro_features)
        session_id: Session ID
        coverage: Result from check_required
        obj: Object that was checked
        logs_dir: Directory to write snapshots to
        
    Returns:
        Path to snapshot file if written, else None
    """
    if coverage["missing"] == 0:
        return None  # No missing data, no need to snapshot
    
    if logs_dir is None:
        logs_dir = Path("/app/logs")
    
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create snapshot
    timestamp = datetime.utcnow().isoformat().replace(":", "-")
    filename = f"api_snapshot_{stage}_{session_id}_{timestamp}.json"
    filepath = logs_dir / filename
    
    snapshot_data = {
        "stage": stage,
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "coverage": coverage,
        "snapshot": _get_snapshot(obj),
    }
    
    try:
        with open(filepath, "w") as f:
            json.dump(snapshot_data, f, indent=2, default=str)
        logger.debug(f"Wrote snapshot: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Failed to write snapshot: {e}")
        return None


def validate_api_profile(
    profile: Any,
    session_id: str = None,
    logs_dir: Path = None
) -> Dict[str, Any]:
    """
    Validate astro profile from Vedic API.
    
    Args:
        profile: AstroProfile object or dict
        session_id: Session ID (for snapshot naming)
        logs_dir: Directory to write snapshots
        
    Returns:
        {
            "ok": int,
            "missing": int,
            "missing_keys": list,
            "present_keys": list,
            "snapshot_path": str or None,
        }
    """
    coverage = check_required(profile, REQUIRED_PROFILE_PATHS)
    
    # Write snapshot if missing data
    snapshot_path = None
    if session_id and coverage["missing"] > 0:
        snapshot_path = _write_snapshot(
            "api_profile",
            session_id,
            coverage,
            profile,
            logs_dir
        )
    
    coverage["snapshot_path"] = snapshot_path
    return coverage


def validate_api_transits(
    transits: Any,
    session_id: str = None,
    logs_dir: Path = None
) -> Dict[str, Any]:
    """
    Validate transits data from Vedic API.
    
    Args:
        transits: AstroTransits object or dict
        session_id: Session ID (for snapshot naming)
        logs_dir: Directory to write snapshots
        
    Returns:
        {
            "ok": int,
            "missing": int,
            "missing_keys": list,
            "present_keys": list,
            "snapshot_path": str or None,
        }
    """
    coverage = check_required(transits, REQUIRED_TRANSITS_PATHS)
    
    # Write snapshot if missing data
    snapshot_path = None
    if session_id and coverage["missing"] > 0:
        snapshot_path = _write_snapshot(
            "api_transits",
            session_id,
            coverage,
            transits,
            logs_dir
        )
    
    coverage["snapshot_path"] = snapshot_path
    return coverage


def validate_astro_features(
    astro_features: Dict[str, Any],
    topic: str = None,
    session_id: str = None,
    logs_dir: Path = None
) -> Dict[str, Any]:
    """
    Validate astro features built for LLM consumption.
    
    Args:
        astro_features: Dict of astro features
        topic: Topic being analyzed (for context)
        session_id: Session ID (for snapshot naming)
        logs_dir: Directory to write snapshots
        
    Returns:
        {
            "ok": int,
            "missing": int,
            "missing_keys": list,
            "present_keys": list,
            "topic": str,
            "snapshot_path": str or None,
        }
    """
    coverage = check_required(astro_features, REQUIRED_FEATURES_PATHS)
    coverage["topic"] = topic
    
    # Write snapshot if missing data
    snapshot_path = None
    if session_id and coverage["missing"] > 0:
        snapshot_path = _write_snapshot(
            "astro_features",
            session_id,
            coverage,
            astro_features,
            logs_dir
        )
    
    coverage["snapshot_path"] = snapshot_path
    return coverage
