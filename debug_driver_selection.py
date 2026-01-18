"""Debug why Jupiter Mahadasha (score=1.0) isn't selected as driver"""
import sys
sys.path.insert(0, '/app/backend')

from astro_client.reading_pack import build_reading_pack, classify_signal_time_layer, SignalRole

astro_features = {
    "houses": [
        {"number": i, "sign": s, "lord": l} for i, (s, l) in enumerate([
            ("Sagittarius", "Jupiter"), ("Capricorn", "Saturn"), ("Aquarius", "Saturn"),
            ("Pisces", "Jupiter"), ("Aries", "Mars"), ("Taurus", "Venus"),
            ("Gemini", "Mercury"), ("Cancer", "Moon"), ("Leo", "Sun"),
            ("Virgo", "Mercury"), ("Libra", "Venus"), ("Scorpio", "Mars")
        ], 1)
    ],
    "planets": [
        {"name": "Sun", "sign": "Capricorn", "house": 10, "degree": 9.78},
        {"name": "Mercury", "sign": "Capricorn", "house": 10, "degree": 21.62},
        {"name": "Saturn", "sign": "Scorpio", "house": 12, "degree": 15.15},
    ],
    "mahadasha": {
        "planet": "Jupiter",
        "start_date": "2020-03-15",
        "end_date": "2036-03-15",
    },
    "antardasha": {
        "planet": "Saturn",
        "start_date": "2023-01-01",
        "end_date": "2025-06-30",
    },
    "transits": [],
    "focus_factors": [],
}

pack = build_reading_pack(
    user_question="How was my career in 2022?",
    topic="career",
    time_context="past",
    astro_features=astro_features,
    missing_keys=[],
    intent='reflect',
    recent_planets=[]
)

signals = pack.get('signals', [])
drivers = pack.get('drivers', [])

print("ALL SIGNALS (sorted by score):")
for s in sorted(signals, key=lambda x: x.get('score_final', 0), reverse=True):
    role = s.get('role', 'UNKNOWN')
    planet = s.get('planet', '?')
    sig_type = s.get('type', '?')
    score = s.get('score_final', 0)
    breakdown = s.get('_scoring_breakdown', {})
    
    print(f"\n{planet} [{sig_type}] score={score:.3f} role={role}")
    print(f"  time_overlap={s.get('time_overlap')}")
    print(f"  inclusion_reason={s.get('_inclusion_reason')}")
    print(f"  breakdown keys: {list(breakdown.keys())}")
    
    # Check if BASELINE_CONTEXT is blocking
    if role == SignalRole.BASELINE_CONTEXT.value:
        print(f"  ⚠️  BASELINE_CONTEXT - will be excluded for specific topic!")

print("\n" + "="*50)
print("DRIVER SELECTION LOG:")
# Get debug info if available
debug = pack.get('_candidate_signals_debug', {})
if debug:
    selection_log = debug.get('driver_selection_log', [])
    for log in selection_log:
        print(f"  {log}")
