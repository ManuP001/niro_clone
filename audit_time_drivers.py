"""Audit script to diagnose time differentiation in driver selection"""
import sys
sys.path.insert(0, '/app/backend')

from astro_client.reading_pack import (
    build_reading_pack, 
    SignalRole,
    classify_signal_time_layer,
    TIME_LAYER_TYPES
)
from astro_client.topics import get_topic_houses_and_planets
import json

# Mock astro features with realistic data including time-layer signals
MOCK_ASTRO_FEATURES = {
    "ascendant": {"sign": "Scorpio", "degree": 15.5},
    "moon_sign": "Capricorn",
    "sun_sign": "Aquarius",
    "houses": [
        {"number": 1, "sign": "Scorpio", "lord": "Mars"},
        {"number": 2, "sign": "Sagittarius", "lord": "Jupiter"},
        {"number": 3, "sign": "Capricorn", "lord": "Saturn"},
        {"number": 4, "sign": "Aquarius", "lord": "Saturn"},
        {"number": 5, "sign": "Pisces", "lord": "Jupiter"},
        {"number": 6, "sign": "Aries", "lord": "Mars"},
        {"number": 7, "sign": "Taurus", "lord": "Venus"},
        {"number": 8, "sign": "Gemini", "lord": "Mercury"},
        {"number": 9, "sign": "Cancer", "lord": "Moon"},
        {"number": 10, "sign": "Leo", "lord": "Sun"},
        {"number": 11, "sign": "Virgo", "lord": "Mercury"},
        {"number": 12, "sign": "Libra", "lord": "Venus"},
    ],
    "planets": [
        {"name": "Sun", "sign": "Aquarius", "house": 4, "degree": 10.5, "retrograde": False},
        {"name": "Moon", "sign": "Capricorn", "house": 3, "degree": 22.3, "retrograde": False},
        {"name": "Mercury", "sign": "Aquarius", "house": 4, "degree": 5.2, "retrograde": False},
        {"name": "Venus", "sign": "Pisces", "house": 5, "degree": 18.7, "retrograde": False},
        {"name": "Mars", "sign": "Aries", "house": 6, "degree": 12.1, "retrograde": False},
        {"name": "Jupiter", "sign": "Taurus", "house": 7, "degree": 8.9, "retrograde": False},
        {"name": "Saturn", "sign": "Scorpio", "house": 1, "degree": 25.4, "retrograde": True},
    ],
    # MAHADASHA - time-layer signal
    "mahadasha": {
        "planet": "Jupiter",
        "start_date": "2020-03-15",
        "end_date": "2036-03-15"
    },
    # ANTARDASHA - time-layer signal
    "antardasha": {
        "planet": "Saturn",
        "start_date": "2023-01-01",
        "end_date": "2025-06-30"
    },
    # Focus factors (natal positions)
    "focus_factors": [
        {"type": "planet_position", "planet": "Sun", "house": 10, "claim": "Sun in 10th house of career", "polarity": "positive"},
        {"type": "planet_position", "planet": "Mercury", "house": 10, "claim": "Mercury in 10th house - communication in career", "polarity": "positive"},
        {"type": "planet_position", "planet": "Saturn", "house": 1, "claim": "Saturn in Lagna - disciplined personality", "polarity": "mixed"},
        {"type": "yoga", "planet": "Jupiter", "claim": "Gaja Kesari Yoga - wisdom and fortune", "polarity": "positive"},
    ],
    # TRANSITS - time-layer signals
    "transits": [
        {
            "planet": "Saturn",
            "sign": "Pisces", 
            "house": 5,
            "start_date": "2023-03-01",
            "end_date": "2026-02-28",
            "aspect": "transit through 5th house"
        },
        {
            "planet": "Jupiter",
            "sign": "Taurus",
            "house": 7,
            "start_date": "2024-05-01", 
            "end_date": "2025-05-01",
            "aspect": "transit through 7th house"
        },
        {
            "planet": "Rahu",
            "sign": "Pisces",
            "house": 5,
            "start_date": "2023-10-01",
            "end_date": "2025-04-01",
            "aspect": "Rahu transit 5th house"
        }
    ]
}

def audit_query(question: str, time_context: str, topic: str = "career"):
    """Audit a single query and return diagnostic data"""
    print(f"\n{'='*80}")
    print(f"QUERY: '{question}'")
    print(f"TIME_CONTEXT: {time_context}")
    print(f"{'='*80}")
    
    # Build reading pack
    pack = build_reading_pack(
        user_question=question,
        topic=topic,
        time_context=time_context,
        astro_features=MOCK_ASTRO_FEATURES,
        missing_keys=[],
        intent='reflect',
        recent_planets=[]
    )
    
    # Get all signals and debug data
    all_signals = pack.get('signals', [])
    drivers = pack.get('drivers', [])
    debug = pack.get('_candidate_signals_debug', {})
    
    # Classify signals by time layer
    time_layer_signals = []
    static_natal_signals = []
    
    for sig in all_signals:
        is_static, is_time, period = classify_signal_time_layer(sig)
        sig_info = {
            'planet': sig.get('planet', 'Unknown'),
            'type': sig.get('type', '?'),
            'role': sig.get('role', '?'),
            'score_final': sig.get('score_final', 0),
            'claim': sig.get('claim', '')[:50],
            'time_period': period,
            'is_time_layer': is_time,
            'is_static_natal': is_static
        }
        if is_time:
            time_layer_signals.append(sig_info)
        elif is_static:
            static_natal_signals.append(sig_info)
    
    # Print findings
    print(f"\n1. TIME_DRIVER SIGNALS GENERATED ({len(time_layer_signals)} found):")
    if time_layer_signals:
        for sig in sorted(time_layer_signals, key=lambda x: x['score_final'], reverse=True):
            print(f"   - {sig['planet']} [{sig['type']}] score={sig['score_final']:.3f} role={sig['role']}")
            print(f"     period={sig['time_period']} | claim='{sig['claim']}'")
    else:
        print("   ⚠️  NO TIME_LAYER SIGNALS FOUND!")
    
    print(f"\n2. STATIC_NATAL SIGNALS ({len(static_natal_signals)} found):")
    for sig in sorted(static_natal_signals, key=lambda x: x['score_final'], reverse=True)[:5]:
        print(f"   - {sig['planet']} [{sig['type']}] score={sig['score_final']:.3f} role={sig['role']}")
    
    print(f"\n3. FINAL DRIVERS SELECTED ({len(drivers)}):")
    for i, d in enumerate(drivers, 1):
        is_static, is_time, period = classify_signal_time_layer(d)
        layer = "TIME_LAYER" if is_time else "STATIC_NATAL"
        print(f"   #{i}: {d.get('planet', '?')} [{layer}] score={d.get('score_final', 0):.3f}")
        print(f"       type={d.get('type')} role={d.get('role')}")
    
    # Check if any TIME_DRIVER made it to drivers
    time_drivers_in_final = [d for d in drivers if classify_signal_time_layer(d)[1]]
    print(f"\n4. TIME_LAYER DRIVERS IN FINAL: {len(time_drivers_in_final)}")
    if time_context != 'timeless' and len(time_drivers_in_final) == 0:
        print("   ⚠️  WARNING: time_context != 'timeless' but NO time-layer drivers selected!")
    
    # Score comparison
    if time_layer_signals and static_natal_signals:
        max_time_score = max(s['score_final'] for s in time_layer_signals)
        max_static_score = max(s['score_final'] for s in static_natal_signals)
        print(f"\n5. SCORE COMPARISON:")
        print(f"   Max TIME_LAYER score: {max_time_score:.3f}")
        print(f"   Max STATIC_NATAL score: {max_static_score:.3f}")
        print(f"   Difference: {max_static_score - max_time_score:.3f}")
        if max_time_score < max_static_score:
            print("   ⚠️  Time signals always scoring LOWER than natal!")
    
    return {
        'time_context': time_context,
        'time_layer_count': len(time_layer_signals),
        'time_layer_signals': time_layer_signals,
        'drivers': [(d.get('planet'), d.get('type')) for d in drivers],
        'time_drivers_in_final': len(time_drivers_in_final)
    }

# Run audit for past and future queries
print("\n" + "="*80)
print("AUDIT: Past vs Future Career Query Time Differentiation")
print("="*80)

past_result = audit_query("How was my career in 2022?", "past", "career")
future_result = audit_query("How will my career be in 2026?", "future", "career")

# Compare results
print("\n" + "="*80)
print("COMPARISON SUMMARY")
print("="*80)

print(f"\nPAST query drivers: {past_result['drivers']}")
print(f"FUTURE query drivers: {future_result['drivers']}")

if past_result['drivers'] == future_result['drivers']:
    print("\n⚠️  PROBLEM CONFIRMED: Past and Future queries have IDENTICAL drivers!")
    print("\nROOT CAUSE ANALYSIS:")
    if past_result['time_layer_count'] == 0 and future_result['time_layer_count'] == 0:
        print("   → No TIME_LAYER signals being generated in reading_pack.signals")
    elif past_result['time_drivers_in_final'] == 0 and future_result['time_drivers_in_final'] == 0:
        print("   → TIME_LAYER signals exist but are NOT entering top 3 drivers")
        print("   → Static natal signals are outscoring time signals")
else:
    print("\n✅ Drivers are DIFFERENT between past and future queries")
