#!/usr/bin/env python3
"""
Test script for NIRO exhaustive observability instrumentation.
Validates that all new modules work correctly.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("=" * 80)
print("NIRO OBSERVABILITY INSTRUMENTATION TEST SUITE")
print("=" * 80 + "\n")

# Test 1: Import pipeline_logger
print("Test 1: Import pipeline_logger module...")
try:
    from observability.pipeline_logger import (
        make_request_id,
        safe_truncate,
        safe_json,
        write_snapshot,
        log_stage,
        detect_missing_data_phrases,
        NIRO_DEBUG_LOGS,
        NIRO_LOG_DIR,
    )
    print("  ✓ All imports successful")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Import time_context
print("\nTest 2: Import time_context module...")
try:
    from observability.time_context import infer_time_context
    print("  ✓ All imports successful")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

# Test 3: Test make_request_id
print("\nTest 3: Generate request IDs...")
try:
    req_id_1 = make_request_id()
    req_id_2 = make_request_id()
    assert len(req_id_1) == 8, f"Expected 8 chars, got {len(req_id_1)}"
    assert req_id_1 != req_id_2, "IDs should be unique"
    print(f"  ✓ Generated unique IDs: {req_id_1}, {req_id_2}")
except Exception as e:
    print(f"  ✗ Test failed: {e}")
    sys.exit(1)

# Test 4: Test safe_truncate
print("\nTest 4: Safe text truncation...")
try:
    long_text = "x" * 500
    truncated = safe_truncate(long_text, 300)
    assert len(truncated) <= 303, "Should be truncated + '...'"
    assert truncated.endswith("..."), "Should have ellipsis"
    
    short_text = "hello"
    not_truncated = safe_truncate(short_text, 300)
    assert not_truncated == "hello", "Should not truncate short text"
    
    none_text = safe_truncate(None, 300)
    assert none_text == "", "Should handle None"
    
    print(f"  ✓ Truncation works: {truncated[:50]}...")
except Exception as e:
    print(f"  ✗ Test failed: {e}")
    sys.exit(1)

# Test 5: Test safe_json
print("\nTest 5: Safe JSON conversion...")
try:
    obj = {
        "name": "test",
        "secret": "should be redacted",
        "apikey": "should be redacted",
        "token": "should be redacted",
        "normal_field": "should pass through",
    }
    
    safe = safe_json(obj)
    assert safe["normal_field"] == "should pass through"
    assert safe["secret"] == "<redacted>"
    assert safe["apikey"] == "<redacted>"
    assert safe["token"] == "<redacted>"
    
    print(f"  ✓ Secrets properly redacted: {safe}")
except Exception as e:
    print(f"  ✗ Test failed: {e}")
    sys.exit(1)

# Test 6: Test infer_time_context
print("\nTest 6: Infer time context from messages...")
try:
    tests = [
        ("Will this be a good year?", "future"),
        ("When should I change jobs?", "future"),
        ("What happened last year?", "past"),
        ("Is this a good time right now?", "present"),
        ("Can you help me?", "unknown"),
    ]
    
    for message, expected in tests:
        result = infer_time_context(message)
        assert result == expected, f"Expected {expected}, got {result} for '{message}'"
        print(f"  ✓ '{message}' -> {result}")
except Exception as e:
    print(f"  ✗ Test failed: {e}")
    sys.exit(1)

# Test 7: Test detect_missing_data_phrases
print("\nTest 7: Detect missing data phrases in LLM output...")
try:
    has_missing_1 = detect_missing_data_phrases(
        "I cannot assess due to missing astrological data"
    )
    assert has_missing_1, "Should detect 'missing astrological data'"
    
    has_missing_2 = detect_missing_data_phrases(
        "The data was not provided"
    )
    assert has_missing_2, "Should detect 'not provided'"
    
    no_missing = detect_missing_data_phrases(
        "Based on your chart, you should pursue this opportunity"
    )
    assert not no_missing, "Should not detect missing phrases"
    
    print(f"  ✓ Detection works correctly")
except Exception as e:
    print(f"  ✗ Test failed: {e}")
    sys.exit(1)

# Test 8: Test write_snapshot
print("\nTest 8: Write snapshot files...")
try:
    test_log_dir = Path(__file__).parent / "logs" / "test_instrumentatio n"
    test_log_dir.mkdir(parents=True, exist_ok=True)
    
    snap_path = write_snapshot(
        "test_snapshot",
        "test_session",
        "a1b2c3d4",
        {"test": "data", "apikey": "secret"},
        ext="json",
        force=True
    )
    
    assert snap_path, "Should return snapshot path"
    assert Path(snap_path).exists(), f"Snapshot file should exist: {snap_path}"
    
    # Verify secrets are redacted
    import json
    with open(snap_path) as f:
        content = json.load(f)
    assert content.get("apikey") == "<redacted>", "Secrets should be redacted"
    
    print(f"  ✓ Snapshot created: {snap_path}")
except Exception as e:
    print(f"  ✗ Test failed: {e}")
    sys.exit(1)

# Test 9: Test log_stage (just verify it doesn't crash)
print("\nTest 9: Test structured logging...")
try:
    # This should not crash, but we can't easily test the actual log output
    # without setting up logging
    log_stage(
        "TEST_STAGE",
        "test_session",
        "a1b2c3d4",
        field1="value1",
        field2=123,
        field3=True
    )
    print(f"  ✓ log_stage() executed without errors")
except Exception as e:
    print(f"  ✗ Test failed: {e}")
    sys.exit(1)

# Test 10: Verify environment variables
print("\nTest 10: Check environment variables...")
try:
    debug_status = "enabled" if NIRO_DEBUG_LOGS else "disabled"
    print(f"  ✓ NIRO_DEBUG_LOGS: {debug_status}")
    print(f"  ✓ NIRO_LOG_DIR: {NIRO_LOG_DIR}")
except Exception as e:
    print(f"  ✗ Test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✓ ALL TESTS PASSED")
print("=" * 80)
print("\nObservability instrumentation is ready for production use.")
print("\nNext steps:")
print("  1. Run a chat request: curl -X POST http://localhost:8000/api/chat \\")
print("     -H 'Content-Type: application/json' \\")
print('     -d \'{"sessionId":"test-obs","message":"I was born on 01/01/2000...","actionId":null,"subjectData":null}\'')
print("  2. Check logs: tail -f /app/logs/niro_pipeline.log")
print("  3. View snapshots: ls -la /app/logs/")
