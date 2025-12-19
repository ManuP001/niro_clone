"""Observability module for NIRO pipeline

Provides:
- Data coverage validation
- Structured logging with request IDs
- Time context detection
- Safe snapshot utilities
"""

from .data_coverage import (
    get_path,
    check_required,
    validate_api_profile,
    validate_api_transits,
    validate_astro_features,
    REQUIRED_PROFILE_PATHS,
    REQUIRED_TRANSITS_PATHS,
    REQUIRED_FEATURES_PATHS,
)

from .pipeline_logger import (
    make_request_id,
    safe_truncate,
    safe_json,
    write_snapshot,
    log_stage,
    detect_missing_data_phrases,
    NIRO_DEBUG_LOGS,
    NIRO_LOG_DIR,
)

from .time_context import (
    infer_time_context,
    TimeContext,
)

__all__ = [
    # Data coverage
    "get_path",
    "check_required",
    "validate_api_profile",
    "validate_api_transits",
    "validate_astro_features",
    "REQUIRED_PROFILE_PATHS",
    "REQUIRED_TRANSITS_PATHS",
    "REQUIRED_FEATURES_PATHS",
    # Pipeline logger
    "make_request_id",
    "safe_truncate",
    "safe_json",
    "write_snapshot",
    "log_stage",
    "detect_missing_data_phrases",
    "NIRO_DEBUG_LOGS",
    "NIRO_LOG_DIR",
    # Time context
    "infer_time_context",
    "TimeContext",
]
