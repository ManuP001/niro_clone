"""Direct audit of reading_pack signal generation"""
import sys
sys.path.insert(0, '/app/backend')
import os
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from datetime import date, datetime

# Skip interpreter - directly test reading_pack with correct structure
# This is what the orchestrator actually passes

astro_features = {
    "ascendant": {"sign": "Sagittarius", "degree": 12.5},
    "moon_sign": "Capricorn", 
    "sun_sign": "Aquarius",
    "planets": [
        {"name": "Sun", "sign": "Capricorn", "house": 2, "degree": 9.78, "retrograde": False},
        {"name": "Moon", "sign": "Capricorn", "house": 2, "degree": 3.28, "retrograde": False},
        {"name": "Mercury", "sign": "Capricorn", "house": 2, "degree": 21.62, "retrograde": False},
        {"name": "Venus", "sign": "Sagittarius", "house": 1, "degree": 25.93, "retrograde": False},
        {"name": "Mars", "sign": "Scorpio", "house": 12, "degree": 19.1, "retrograde": False},
        {"name": "Jupiter", "sign": "Aquarius", "house": 3, "degree": 11.02, "retrograde": False},
        {"name": "Saturn", "sign": "Scorpio", "house": 12, "degree": 15.15, "retrograde": True},
        {"name": "Rahu", "sign": "Aries", "house": 5, "degree": 11.1, "retrograde": True},
        {"name": "Ketu", "sign": "Libra", "house": 11, "degree": 11.1, "retrograde": True},
    ],
    "houses": [
        {"number": i, "sign": s, "lord": l} for i, (s, l) in enumerate([
            ("Sagittarius", "Jupiter"), ("Capricorn", "Saturn"), ("Aquarius", "Saturn"),
            ("Pisces", "Jupiter"), ("Aries", "Mars"), ("Taurus", "Venus"),
            ("Gemini", "Mercury"), ("Cancer", "Moon"), ("Leo", "Sun"),
            ("Virgo", "Mercury"), ("Libra", "Venus"), ("Scorpio", "Mars")
        ], 1)
    ],
    # Mahadasha with date strings (as from Vedic API)
    "mahadasha": {
        "planet": "Jupiter",
        "start_date": "2020-03-15",
        "end_date": "2036-03-15",
        "years_remaining": 11.2
    },
    # Antardasha
    "antardasha": {
        "planet": "Saturn", 
        "start_date": "2023-01-01",
        "end_date": "2025-06-30",
        "years_remaining": 0.5
    },
    "yogas": [
        {"name": "Gaja Kesari Yoga", "interpretation": "Jupiter-Moon combination for wisdom"},
    ],
    # Transits from Vedic API
    "transits": [
        {
            "planet": "Saturn",
            "sign": "Pisces",
            "house": 4,
            "start_date": "2023-03-07",
            "end_date": "2026-02-28",
            "aspect": "Saturn transiting 4th house",
            "nature": "challenging"
        },
        {
            "planet": "Jupiter",
            "sign": "Gemini",
            "house": 7,
            "start_date": "2024-05-01",
            "end_date": "2025-05-01", 
            "aspect": "Jupiter transiting 7th house",
            "nature": "supportive"
        },
        {
            "planet": "Rahu",
            "sign": "Pisces",
            "house": 4,
            "start_date": "2023-10-30",
            "end_date": "2025-05-18",
            "aspect": "Rahu transiting 4th house",
            "nature": "transformative"
        }
    ],
    "focus_factors": [
        {"factor": "10th house lord", "strength": 0.8, "interpretation": "Strong career house lord"},
        {"factor": "Sun strength", "strength": 0.7, "interpretation": "Authority and leadership"},
    ],
    "key_rules": []
}

from astro_client.reading_pack import build_reading_pack, classify_signal_time_layer

print("="*80)
print("AUDIT: PAST vs FUTURE CAREER QUERY")
print("="*80)

# Test PAST query
print("\n--- PAST QUERY: 'How was my career in 2022?' ---\n")
past_pack = build_reading_pack(
    user_question="How was my career in 2022?",
    topic="career",
    time_context="past",
    astro_features=astro_features,
    missing_keys=[],
    intent='reflect',
    recent_planets=[]
)

# Test FUTURE query  
print("\n--- FUTURE QUERY: 'How will my career be in 2026?' ---\n")
future_pack = build_reading_pack(
    user_question="How will my career be in 2026?",
    topic="career",
    time_context="future",
    astro_features=astro_features,
    missing_keys=[],
    intent='reflect',
    recent_planets=[]
)

def analyze_pack(name, pack):
    signals = pack.get('signals', [])
    drivers = pack.get('drivers', [])
    
    time_layer = []
    static_natal = []
    
    for sig in signals:
        is_static, is_time, period = classify_signal_time_layer(sig)
        sig_info = {
            'planet': sig.get('planet'),
            'type': sig.get('type'),
            'score': sig.get('score_final', 0),
            'role': sig.get('role'),
            'period': period
        }
        if is_time:
            time_layer.append(sig_info)
        else:
            static_natal.append(sig_info)
    
    print(f"\n{name}:")
    print(f"  Total signals: {len(signals)}")
    print(f"  TIME_LAYER signals: {len(time_layer)}")
    print(f"  STATIC_NATAL signals: {len(static_natal)}")
    
    if time_layer:
        print(f"\n  TIME_LAYER signals (sorted by score):")
        for s in sorted(time_layer, key=lambda x: x['score'], reverse=True):
            print(f"    - {s['planet']} [{s['type']}] score={s['score']:.3f} role={s['role']} period={s['period']}")
    else:
        print(f"\n  ⚠️  NO TIME_LAYER SIGNALS!")
    
    print(f"\n  STATIC_NATAL signals (top 5):")
    for s in sorted(static_natal, key=lambda x: x['score'], reverse=True)[:5]:
        print(f"    - {s['planet']} [{s['type']}] score={s['score']:.3f} role={s['role']}")
    
    print(f"\n  FINAL DRIVERS ({len(drivers)}):")
    for d in drivers:
        is_static, is_time, period = classify_signal_time_layer(d)
        layer = "TIME" if is_time else "STATIC"
        print(f"    - {d.get('planet')} [{d.get('type')}] {layer} score={d.get('score_final', 0):.3f}")
    
    return [(d.get('planet'), d.get('type')) for d in drivers]

past_drivers = analyze_pack("PAST QUERY", past_pack)
future_drivers = analyze_pack("FUTURE QUERY", future_pack)

print("\n" + "="*80)
print("COMPARISON")
print("="*80)
print(f"\nPAST drivers: {past_drivers}")
print(f"FUTURE drivers: {future_drivers}")
print(f"\nIdentical? {past_drivers == future_drivers}")
