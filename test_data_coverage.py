#!/usr/bin/env python3
"""
Test script for data coverage validation.
Validates that the data_coverage module works as expected.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from observability.data_coverage import (
    get_path,
    check_required,
    validate_api_profile,
    validate_api_transits,
    validate_astro_features,
    REQUIRED_PROFILE_PATHS,
    REQUIRED_TRANSITS_PATHS,
    REQUIRED_FEATURES_PATHS,
)


def test_get_path():
    """Test path accessor function"""
    print("Testing get_path()...")
    
    # Test dict access
    obj = {"birth_details": {"dob": "2000-01-01", "tob": "10:30"}}
    assert get_path(obj, "birth_details.dob") == "2000-01-01"
    assert get_path(obj, "birth_details.tob") == "10:30"
    assert get_path(obj, "birth_details.missing") is None
    
    # Test list access
    obj = {"planets": [{"name": "Sun"}, {"name": "Moon"}]}
    assert get_path(obj, "planets[0].name") == "Sun"
    assert get_path(obj, "planets[1].name") == "Moon"
    assert get_path(obj, "planets[5].name") is None
    
    # Test mixed access
    obj = {"data": {"items": [{"value": "test"}]}}
    assert get_path(obj, "data.items[0].value") == "test"
    
    print("  ✓ get_path() works correctly")


def test_check_required():
    """Test required fields validator"""
    print("Testing check_required()...")
    
    # Test complete data
    obj = {
        "birth_details": {"dob": "2000-01-01", "tob": "10:30", "location": "NYC"},
        "ascendant": "Aries",
        "moon_sign": "Taurus",
    }
    result = check_required(obj, ["birth_details.dob", "ascendant", "moon_sign"])
    assert result["ok"] == 3
    assert result["missing"] == 0
    assert len(result["missing_keys"]) == 0
    
    # Test missing data
    result = check_required(obj, ["birth_details.dob", "missing_field", "ascendant"])
    assert result["ok"] == 2
    assert result["missing"] == 1
    assert "missing_field" in result["missing_keys"]
    
    print("  ✓ check_required() works correctly")


def test_validate_api_profile():
    """Test profile validation"""
    print("Testing validate_api_profile()...")
    
    # Create a test profile
    profile = {
        "birth_details": {
            "dob": date(2000, 1, 1),
            "tob": "10:30",
            "location": "NYC",
        },
        "ascendant": "Aries",
        "moon_sign": "Taurus",
        "sun_sign": "Capricorn",
        "planets": [{"planet": "Sun", "sign": "Capricorn"}],
        "houses": [{"house_num": 1, "sign": "Aries"}],
        "current_mahadasha": {
            "planet": "Sun",
            "start_date": date(2020, 1, 1),
            "end_date": date(2026, 1, 1),
        },
        "current_antardasha": {
            "planet": "Moon",
            "start_date": date(2023, 1, 1),
            "end_date": date(2025, 1, 1),
        },
    }
    
    result = validate_api_profile(profile)
    assert result["ok"] > 0
    assert "missing_keys" in result
    assert "present_keys" in result
    
    print(f"  ✓ validate_api_profile() works: ok={result['ok']}, missing={result['missing']}")


def test_validate_api_transits():
    """Test transits validation"""
    print("Testing validate_api_transits()...")
    
    transits = {
        "events": [
            {
                "planet": "Saturn",
                "affected_house": 7,
                "start_date": date(2024, 1, 1),
                "event_type": "ingress",
            }
        ]
    }
    
    result = validate_api_transits(transits)
    assert result["ok"] > 0
    assert "missing_keys" in result
    
    print(f"  ✓ validate_api_transits() works: ok={result['ok']}, missing={result['missing']}")


def test_validate_astro_features():
    """Test astro features validation"""
    print("Testing validate_astro_features()...")
    
    features = {
        "ascendant": "Aries",
        "moon_sign": "Taurus",
        "sun_sign": "Capricorn",
        "mahadasha": {"planet": "Sun", "start_date": date(2020, 1, 1)},
        "antardasha": {"planet": "Moon", "start_date": date(2023, 1, 1)},
        "focus_factors": ["House 7", "Venus strength"],
        "transits": [{"planet": "Saturn"}],
    }
    
    result = validate_astro_features(features, topic="career")
    assert result["ok"] > 0
    assert result["topic"] == "career"
    
    print(f"  ✓ validate_astro_features() works: ok={result['ok']}, missing={result['missing']}")


def test_snapshot_on_missing():
    """Test that snapshots are created when data is missing"""
    print("Testing snapshot creation on missing data...")
    
    logs_dir = Path(__file__).parent / "logs" / "test"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Incomplete profile
    incomplete_profile = {
        "ascendant": "Aries",
        # Missing many required fields
    }
    
    result = validate_api_profile(
        incomplete_profile,
        session_id="test_session_123",
        logs_dir=logs_dir
    )
    
    assert result["missing"] > 0
    assert result["snapshot_path"] is not None
    
    # Check snapshot file was created
    snapshot_path = Path(result["snapshot_path"])
    assert snapshot_path.exists()
    
    # Verify snapshot content
    with open(snapshot_path) as f:
        snapshot = json.load(f)
    
    assert snapshot["stage"] == "api_profile"
    assert snapshot["session_id"] == "test_session_123"
    assert "coverage" in snapshot
    assert "snapshot" in snapshot
    
    print(f"  ✓ Snapshot created: {snapshot_path}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("DATA COVERAGE VALIDATOR TEST SUITE")
    print("="*60 + "\n")
    
    try:
        test_get_path()
        test_check_required()
        test_validate_api_profile()
        test_validate_api_transits()
        test_validate_astro_features()
        test_snapshot_on_missing()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
