"""Audit with REAL user data to see what signals are actually generated"""
import sys
sys.path.insert(0, '/app/backend')
import asyncio
import os

# Load env
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from astro_client.reading_pack import (
    build_reading_pack, 
    classify_signal_time_layer,
)

async def get_real_astro_features():
    """Get real astro features from a test user"""
    from services.astro_database import get_astro_db
    from motor.motor_asyncio import AsyncIOMotorClient
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.niro
    
    # Find a user with complete profile
    user = await db.users.find_one({"profile.complete": True})
    if not user:
        print("No user with complete profile found")
        return None
    
    print(f"Found user: {user.get('email', 'unknown')}")
    
    # Get their astro profile from the Vedic API cache
    profile = user.get('profile', {})
    print(f"Profile: dob={profile.get('dob')}, tob={profile.get('tob')}, location={profile.get('location')}")
    
    # Try to get cached astro data
    astro_db = await get_astro_db()
    
    # Check if we have astro profile cached
    astro_profiles = await db.astro_profiles.find_one({"user_id": str(user['_id'])})
    if astro_profiles:
        import json
        data = json.loads(astro_profiles.get('data_json', '{}'))
        print(f"\nCached astro profile found with keys: {list(data.keys())}")
        return data
    
    print("No cached astro profile - would need to call Vedic API")
    return None

async def main():
    # Get real features
    features = await get_real_astro_features()
    
    if not features:
        print("\nUsing previously fetched astro_features structure...")
        # Let me check what structure the real API returns
        return
    
    print("\n" + "="*80)
    print("REAL DATA SIGNAL ANALYSIS")
    print("="*80)
    
    # Check what time-layer data exists
    print(f"\nMAHADASHA: {features.get('mahadasha')}")
    print(f"ANTARDASHA: {features.get('antardasha')}")
    print(f"TRANSITS count: {len(features.get('transits', []))}")
    
    if features.get('transits'):
        print("\nTRANSIT DATA STRUCTURE:")
        for t in features.get('transits', [])[:3]:
            print(f"  - {t}")
    
    # Build reading pack
    pack = build_reading_pack(
        user_question="How will my career be in 2026?",
        topic="career",
        time_context="future",
        astro_features=features,
        missing_keys=[],
        intent='reflect',
        recent_planets=[]
    )
    
    signals = pack.get('signals', [])
    drivers = pack.get('drivers', [])
    
    print(f"\nSIGNALS GENERATED: {len(signals)}")
    
    time_count = 0
    static_count = 0
    for sig in signals:
        is_static, is_time, period = classify_signal_time_layer(sig)
        layer = "TIME" if is_time else "STATIC"
        print(f"  - {sig.get('planet')} [{sig.get('type')}] {layer} score={sig.get('score_final', 0):.3f}")
        if is_time:
            time_count += 1
        else:
            static_count += 1
    
    print(f"\nTIME_LAYER signals: {time_count}")
    print(f"STATIC_NATAL signals: {static_count}")
    
    print(f"\nFINAL DRIVERS ({len(drivers)}):")
    for d in drivers:
        is_static, is_time, period = classify_signal_time_layer(d)
        layer = "TIME" if is_time else "STATIC"
        print(f"  - {d.get('planet')} [{d.get('type')}] {layer}")

asyncio.run(main())
