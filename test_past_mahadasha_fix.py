"""Test: Past query Mahadasha time overlap fix"""
import sys
sys.path.insert(0, '/app/backend')

from astro_client.reading_pack import build_reading_pack, classify_signal_time_layer

# Test data with Mahadasha spanning 2020-2036 (covers 2022)
# and Antardasha spanning 2023-2025 (does NOT cover 2022)
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
        {"name": "Sun", "sign": "Capricorn", "house": 10, "degree": 9.78},  # In 10th for career
        {"name": "Mercury", "sign": "Capricorn", "house": 10, "degree": 21.62},  # In 10th for career
        {"name": "Saturn", "sign": "Scorpio", "house": 12, "degree": 15.15},
    ],
    # Mahadasha: Jupiter 2020-2036 (COVERS 2022)
    "mahadasha": {
        "planet": "Jupiter",  # Not a career karaka
        "start_date": "2020-03-15",
        "end_date": "2036-03-15",
    },
    # Antardasha: Saturn 2023-2025 (does NOT cover 2022)
    "antardasha": {
        "planet": "Saturn",
        "start_date": "2023-01-01",
        "end_date": "2025-06-30",
    },
    "transits": [],  # No transits for past
    "focus_factors": [],
}

def test_query(question, time_context, expected_mahadasha):
    print(f"\n{'='*70}")
    print(f"TEST: '{question}'")
    print(f"time_context={time_context}, expected_mahadasha_in_drivers={expected_mahadasha}")
    print('='*70)
    
    pack = build_reading_pack(
        user_question=question,
        topic="career",
        time_context=time_context,
        astro_features=astro_features,
        missing_keys=[],
        intent='reflect',
        recent_planets=[]
    )
    
    signals = pack.get('signals', [])
    drivers = pack.get('drivers', [])
    
    # Check Mahadasha inclusion
    maha_signals = [s for s in signals if 'mahadasha' in s.get('claim', '').lower()]
    maha_in_drivers = [d for d in drivers if 'mahadasha' in d.get('claim', '').lower()]
    
    print(f"\nMahadasha signals found: {len(maha_signals)}")
    for m in maha_signals:
        print(f"  - {m.get('planet')} score={m.get('score_final', 0):.3f}")
        print(f"    time_overlap={m.get('time_overlap')}, window={m.get('overlap_window')}")
        print(f"    inclusion_reason={m.get('_inclusion_reason')}")
    
    print(f"\nAll signals ({len(signals)}):")
    for s in sorted(signals, key=lambda x: x.get('score_final', 0), reverse=True):
        is_static, is_time, period = classify_signal_time_layer(s)
        layer = "TIME" if is_time else "STATIC"
        print(f"  - {s.get('planet')} [{s.get('type')}] {layer} score={s.get('score_final', 0):.3f}")
    
    print(f"\nFinal Drivers ({len(drivers)}):")
    for d in drivers:
        is_static, is_time, period = classify_signal_time_layer(d)
        layer = "TIME" if is_time else "STATIC"
        print(f"  - {d.get('planet')} [{d.get('type')}] {layer} score={d.get('score_final', 0):.3f}")
        print(f"    claim: {d.get('claim', '')[:50]}")
    
    # Verify expectation
    has_mahadasha_driver = len(maha_in_drivers) > 0
    
    if has_mahadasha_driver == expected_mahadasha:
        print(f"\n✅ PASS: Mahadasha in drivers = {has_mahadasha_driver} (expected {expected_mahadasha})")
        return True
    else:
        print(f"\n❌ FAIL: Mahadasha in drivers = {has_mahadasha_driver} (expected {expected_mahadasha})")
        return False

# Run acceptance tests
print("\n" + "="*70)
print("ACCEPTANCE TESTS: Past Query Mahadasha Fix")
print("="*70)

results = []

# Test 1: Past query with year inside Mahadasha range → SHOULD include Mahadasha
results.append(("Past 2022 (inside Mahadasha)", 
    test_query("How was my career in 2022?", "past", expected_mahadasha=True)))

# Test 2: Future query → unchanged behavior (topic gating applies)
results.append(("Future 2026", 
    test_query("How will my career be in 2026?", "future", expected_mahadasha=False)))

# Test 3: Past query with year OUTSIDE Mahadasha range → no forced inclusion
results.append(("Past 2018 (outside Mahadasha)", 
    test_query("How was my career in 2018?", "past", expected_mahadasha=False)))

# Test 4: Present query → unchanged behavior
results.append(("Present (timeless)", 
    test_query("How is my career now?", "present", expected_mahadasha=False)))

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
all_pass = True
for name, passed in results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}: {name}")
    if not passed:
        all_pass = False

print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_pass else '❌ SOME TESTS FAILED'}")
