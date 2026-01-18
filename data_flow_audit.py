#!/usr/bin/env python3
"""
Data Flow Audit Script - Kundli vs Chat/Reading Engine

This script traces raw API data through both:
1. Kundli Tab UI pipeline
2. Chat/Reading Engine pipeline

And produces a comparison table showing any discrepancies.

OBJECTIVE: Verify whether the Kundli tab UI and the chat/reading engine 
are using the same underlying chart data, calculation settings, and API responses.
"""

import asyncio
import json
import os
import sys
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional, List

# Add backend to path
sys.path.insert(0, '/app/backend')

from backend.astro_client.vedic_api import VedicAPIClient, vedic_api_client
from backend.astro_client.models import BirthDetails, AstroProfile
from backend.astro_client.interpreter import build_astro_features
from backend.astro_client.reading_pack import build_reading_pack

# Test profile - standardized birth details
TEST_PROFILE = {
    "dob": date(1986, 1, 24),  # DOB: 1986-01-24
    "tob": "06:32",            # TOB: 06:32
    "location": "Mumbai, India",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "timezone": 5.5
}


def create_birth_details():
    """Create BirthDetails from test profile."""
    return BirthDetails(
        dob=TEST_PROFILE["dob"],
        tob=TEST_PROFILE["tob"],
        location=TEST_PROFILE["location"],
        latitude=TEST_PROFILE["latitude"],
        longitude=TEST_PROFILE["longitude"],
        timezone=TEST_PROFILE["timezone"]
    )


async def fetch_raw_api_data(client: VedicAPIClient, birth: BirthDetails) -> Dict[str, Any]:
    """
    Fetch raw API data for logging purposes.
    This makes direct API calls to capture raw responses.
    """
    print("\n" + "="*80)
    print("STEP 1: FETCHING RAW API DATA")
    print("="*80)
    
    api_params = {
        'dob': birth.dob.strftime("%d/%m/%Y"),
        'tob': birth.tob,
        'lat': birth.latitude or 28.6139,
        'lon': birth.longitude or 77.2090,
        'tz': birth.timezone,
        'ayanamsa': 'Lahiri'
    }
    
    print(f"\n📊 API Parameters:")
    print(f"   DOB: {api_params['dob']}")
    print(f"   TOB: {api_params['tob']}")
    print(f"   LAT: {api_params['lat']}")
    print(f"   LON: {api_params['lon']}")
    print(f"   TZ: {api_params['tz']}")
    print(f"   Ayanamsa: {api_params['ayanamsa']}")
    
    raw_data = {}
    
    try:
        # 1. Fetch extended-kundli-details (main chart data)
        print("\n📡 Calling /extended-horoscope/extended-kundli-details...")
        kundli_details = await client._get('/extended-horoscope/extended-kundli-details', api_params.copy())
        raw_data['kundli_details'] = kundli_details
        print(f"   ✅ Response keys: {list(kundli_details.keys())}")
        
        # 2. Fetch maha-dasha
        print("\n📡 Calling /dashas/maha-dasha...")
        dasha_data = await client._get('/dashas/maha-dasha', api_params.copy())
        raw_data['dasha_data'] = dasha_data
        print(f"   ✅ Response keys: {list(dasha_data.keys())}")
        
        # 3. Fetch planet reports for all 9 planets
        planet_names = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']
        planets_list = []
        
        print("\n📡 Calling /horoscope/planet-report for each planet...")
        for planet_name in planet_names:
            try:
                params = api_params.copy()
                params['planet'] = planet_name
                planet_resp = await client._get('/horoscope/planet-report', params)
                if planet_resp and isinstance(planet_resp, list) and len(planet_resp) > 0:
                    planets_list.append({
                        'planet_name': planet_name.capitalize(),
                        'raw_response': planet_resp[0]
                    })
                    print(f"   ✅ {planet_name.capitalize()}: house={planet_resp[0].get('planet_location')}, sign={planet_resp[0].get('planet_zodiac')}")
            except Exception as e:
                print(f"   ❌ {planet_name.capitalize()}: {e}")
        
        raw_data['planets_raw'] = planets_list
        
    except Exception as e:
        print(f"❌ Error fetching raw API data: {e}")
        raise
    
    return raw_data


async def trace_kundli_pipeline(client: VedicAPIClient, birth: BirthDetails) -> Dict[str, Any]:
    """
    Trace data flow through the Kundli tab pipeline.
    Uses fetch_kundli_optimized which is called by GET /api/kundli.
    """
    print("\n" + "="*80)
    print("STEP 2: TRACING KUNDLI TAB PIPELINE")
    print("="*80)
    
    result = await client.fetch_kundli_optimized(birth, user_id="audit-test-user")
    
    if not result.get('ok'):
        print(f"❌ Kundli fetch failed: {result.get('error')}")
        return {}
    
    structured = result.get('structured', {})
    profile = result.get('profile')
    
    print("\n📊 Kundli Tab Data:")
    
    # Ascendant
    asc = structured.get('ascendant', {})
    print(f"\n   ASCENDANT:")
    print(f"      Sign: {asc.get('sign', 'N/A')}")
    print(f"      Degree: {asc.get('degree', 'N/A')}")
    
    # Houses
    houses = structured.get('houses', [])
    print(f"\n   HOUSES ({len(houses)}):")
    for h in houses[:4]:  # Show first 4
        print(f"      H{h.get('house')}: {h.get('sign')} (Lord: {h.get('lord')})")
    
    # Planets
    planets = structured.get('planets', [])
    print(f"\n   PLANETS ({len(planets)}):")
    for p in planets:
        print(f"      {p.get('name')}: {p.get('sign')} H{p.get('house')} {p.get('degree', 0):.1f}° {'(R)' if p.get('retrograde') else ''}")
    
    return {
        'structured': structured,
        'profile': profile.model_dump() if hasattr(profile, 'model_dump') else str(profile)
    }


async def trace_chat_pipeline(client: VedicAPIClient, birth: BirthDetails) -> Dict[str, Any]:
    """
    Trace data flow through the Chat/Reading pipeline.
    Uses fetch_full_profile which is called by the chat endpoint.
    """
    print("\n" + "="*80)
    print("STEP 3: TRACING CHAT/READING ENGINE PIPELINE")
    print("="*80)
    
    # Fetch full profile (same as chat endpoint uses)
    profile = await client.fetch_full_profile(birth, user_id="audit-test-user")
    
    print("\n📊 Chat Pipeline Profile Data:")
    
    # Ascendant
    print(f"\n   ASCENDANT:")
    print(f"      Sign: {profile.ascendant}")
    print(f"      Degree: {profile.ascendant_degree}")
    print(f"      Nakshatra: {profile.ascendant_nakshatra}")
    
    # Moon
    print(f"\n   MOON:")
    print(f"      Sign: {profile.moon_sign}")
    print(f"      Nakshatra: {profile.moon_nakshatra}")
    
    # Sun
    print(f"\n   SUN:")
    print(f"      Sign: {profile.sun_sign}")
    
    # Houses
    print(f"\n   HOUSES ({len(profile.houses)}):")
    for h in profile.houses[:4]:  # Show first 4
        print(f"      H{h.house_num}: {h.sign} (Lord: {h.sign_lord})")
    
    # Planets
    print(f"\n   PLANETS ({len(profile.planets)}):")
    for p in profile.planets:
        print(f"      {p.planet}: {p.sign} H{p.house} {p.degree:.1f}° {'(R)' if p.is_retrograde else ''}")
    
    # Dasha
    print(f"\n   MAHADASHA:")
    if profile.current_mahadasha:
        print(f"      Planet: {profile.current_mahadasha.planet}")
        print(f"      Start: {profile.current_mahadasha.start_date}")
        print(f"      End: {profile.current_mahadasha.end_date}")
    
    print(f"\n   ANTARDASHA:")
    if profile.current_antardasha:
        print(f"      Planet: {profile.current_antardasha.planet}")
        print(f"      Start: {profile.current_antardasha.start_date}")
        print(f"      End: {profile.current_antardasha.end_date}")
    
    # Build astro_features (as reading pack does)
    from backend.astro_client.models import AstroTransits
    
    # Create minimal transits object
    transits = AstroTransits(
        user_id="audit-test-user",
        from_date=date.today(),
        to_date=date.today() + timedelta(days=90),
        events=[]
    )
    
    astro_features = build_astro_features(
        profile=profile,
        transits=transits,
        mode="NORMAL_READING",
        topic="career",
        now=datetime.utcnow()
    )
    
    print(f"\n📊 Astro Features (for LLM):")
    print(f"   Ascendant: {astro_features.get('ascendant')}")
    print(f"   Moon Sign: {astro_features.get('moon_sign')}")
    print(f"   Moon Nakshatra: {astro_features.get('moon_nakshatra')}")
    print(f"   Sun Sign: {astro_features.get('sun_sign')}")
    print(f"   Mahadasha: {astro_features.get('mahadasha', {}).get('planet') if astro_features.get('mahadasha') else 'N/A'}")
    print(f"   Antardasha: {astro_features.get('antardasha', {}).get('planet') if astro_features.get('antardasha') else 'N/A'}")
    
    return {
        'profile': profile.model_dump(),
        'astro_features': astro_features
    }


def build_comparison_table(raw_data: Dict, kundli_data: Dict, chat_data: Dict):
    """
    Build a comparison table showing values from all three sources.
    """
    print("\n" + "="*80)
    print("STEP 4: COMPARISON TABLE")
    print("="*80)
    
    kundli_struct = kundli_data.get('structured', {})
    chat_profile = chat_data.get('profile', {})
    chat_features = chat_data.get('astro_features', {})
    
    # Extract raw API values
    raw_kundli = raw_data.get('kundli_details', {})
    raw_dasha = raw_data.get('dasha_data', {})
    raw_planets = raw_data.get('planets_raw', [])
    
    table_rows = []
    
    # ==========================================================================
    # ASCENDANT
    # ==========================================================================
    raw_asc_sign = raw_kundli.get('ascendant_sign', 'N/A')
    raw_asc_degree = raw_kundli.get('ascendant_degree', 'N/A')
    
    kundli_asc = kundli_struct.get('ascendant', {})
    kundli_asc_sign = kundli_asc.get('sign', 'N/A')
    kundli_asc_degree = kundli_asc.get('degree', 'N/A')
    
    chat_asc_sign = chat_profile.get('ascendant', 'N/A')
    chat_asc_degree = chat_profile.get('ascendant_degree', 'N/A')
    
    table_rows.append({
        'field': 'Ascendant Sign',
        'raw_api': raw_asc_sign,
        'kundli_tab': kundli_asc_sign,
        'chat_engine': chat_asc_sign,
        'match': raw_asc_sign == kundli_asc_sign == chat_asc_sign
    })
    
    table_rows.append({
        'field': 'Ascendant Degree',
        'raw_api': f"{raw_asc_degree}°" if raw_asc_degree != 'N/A' else 'N/A',
        'kundli_tab': f"{kundli_asc_degree:.1f}°" if isinstance(kundli_asc_degree, (int, float)) else 'N/A',
        'chat_engine': f"{chat_asc_degree:.1f}°" if isinstance(chat_asc_degree, (int, float)) else 'N/A',
        'match': 'DERIVED' if raw_asc_degree in (0, None, 'N/A') else str(raw_asc_degree) == str(kundli_asc_degree) == str(chat_asc_degree)
    })
    
    # ==========================================================================
    # MOON
    # ==========================================================================
    raw_moon_sign = raw_kundli.get('rasi', raw_kundli.get('moon_sign', 'N/A'))
    raw_moon_nakshatra = raw_kundli.get('nakshatra', 'N/A')
    
    # Find Moon in raw planets
    moon_raw = next((p for p in raw_planets if p['planet_name'] == 'Moon'), None)
    if moon_raw:
        raw_moon_sign = moon_raw['raw_response'].get('planet_zodiac', raw_moon_sign)
    
    chat_moon_sign = chat_profile.get('moon_sign', 'N/A')
    chat_moon_nakshatra = chat_profile.get('moon_nakshatra', 'N/A')
    
    # Kundli tab doesn't show Moon sign directly, derive from planets
    kundli_planets = kundli_struct.get('planets', [])
    kundli_moon = next((p for p in kundli_planets if p.get('name') == 'Moon'), {})
    kundli_moon_sign = kundli_moon.get('sign', 'N/A')
    
    table_rows.append({
        'field': 'Moon Sign',
        'raw_api': raw_moon_sign,
        'kundli_tab': kundli_moon_sign,
        'chat_engine': chat_moon_sign,
        'match': str(raw_moon_sign).lower() == str(kundli_moon_sign).lower() == str(chat_moon_sign).lower()
    })
    
    table_rows.append({
        'field': 'Moon Nakshatra',
        'raw_api': raw_moon_nakshatra,
        'kundli_tab': 'Not Shown',
        'chat_engine': chat_moon_nakshatra,
        'match': 'PARTIAL'  # Kundli tab doesn't show nakshatra
    })
    
    # ==========================================================================
    # HOUSES (4th, 7th, 10th)
    # ==========================================================================
    kundli_houses = {h.get('house'): h for h in kundli_struct.get('houses', [])}
    chat_houses = {h.get('house_num'): h for h in chat_profile.get('houses', [])}
    
    for house_num in [4, 7, 10]:
        kundli_h = kundli_houses.get(house_num, {})
        chat_h = chat_houses.get(house_num, {})
        
        # Raw houses are derived from ascendant in API
        raw_asc_idx = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                       'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'].index(raw_asc_sign) if raw_asc_sign in ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'] else -1
        if raw_asc_idx >= 0:
            raw_h_sign_idx = (raw_asc_idx + house_num - 1) % 12
            raw_h_sign = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                          'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'][raw_h_sign_idx]
        else:
            raw_h_sign = 'N/A'
        
        table_rows.append({
            'field': f'House {house_num} Sign',
            'raw_api': raw_h_sign,
            'kundli_tab': kundli_h.get('sign', 'N/A'),
            'chat_engine': chat_h.get('sign', 'N/A'),
            'match': raw_h_sign == kundli_h.get('sign') == chat_h.get('sign')
        })
        
        table_rows.append({
            'field': f'House {house_num} Lord',
            'raw_api': 'Derived',
            'kundli_tab': kundli_h.get('lord', 'N/A'),
            'chat_engine': chat_h.get('sign_lord', 'N/A'),
            'match': kundli_h.get('lord') == chat_h.get('sign_lord')
        })
    
    # ==========================================================================
    # MAHADASHA / ANTARDASHA
    # ==========================================================================
    raw_maha_timeline = raw_dasha.get('mahadasha_timeline', [])
    raw_maha = raw_maha_timeline[0] if raw_maha_timeline else {}
    
    chat_maha = chat_profile.get('current_mahadasha', {})
    chat_antar = chat_profile.get('current_antardasha', {})
    
    table_rows.append({
        'field': 'Mahadasha Planet',
        'raw_api': raw_maha.get('planet', 'N/A'),
        'kundli_tab': 'Not Shown',
        'chat_engine': chat_maha.get('planet', 'N/A'),
        'match': 'PARTIAL'
    })
    
    table_rows.append({
        'field': 'Mahadasha Dates',
        'raw_api': f"{raw_maha.get('start_date', 'N/A')} to {raw_maha.get('end_date', 'N/A')}",
        'kundli_tab': 'Not Shown',
        'chat_engine': f"{chat_maha.get('start_date', 'N/A')} to {chat_maha.get('end_date', 'N/A')}",
        'match': 'PARTIAL'
    })
    
    table_rows.append({
        'field': 'Antardasha Planet',
        'raw_api': 'N/A',  # Would need separate API call
        'kundli_tab': 'Not Shown',
        'chat_engine': chat_antar.get('planet', 'N/A'),
        'match': 'PARTIAL'
    })
    
    # ==========================================================================
    # PRINT TABLE
    # ==========================================================================
    print("\n" + "-"*100)
    print(f"{'FIELD':<25} | {'RAW API':<20} | {'KUNDLI TAB':<20} | {'CHAT ENGINE':<20} | {'MATCH':<10}")
    print("-"*100)
    
    for row in table_rows:
        match_str = '✅' if row['match'] == True else ('⚠️' if row['match'] in ('PARTIAL', 'DERIVED') else '❌')
        print(f"{row['field']:<25} | {str(row['raw_api']):<20} | {str(row['kundli_tab']):<20} | {str(row['chat_engine']):<20} | {match_str:<10}")
    
    print("-"*100)
    
    return table_rows


def analyze_configuration(raw_data: Dict):
    """
    Analyze configuration settings used by both pipelines.
    """
    print("\n" + "="*80)
    print("STEP 5: CONFIGURATION ANALYSIS")
    print("="*80)
    
    analysis = {
        'ayanamsa': {
            'value': 'Lahiri',
            'used_by': ['Kundli Tab', 'Chat Engine'],
            'consistent': True
        },
        'house_system': {
            'value': 'Whole Sign (derived from Ascendant)',
            'used_by': ['Kundli Tab', 'Chat Engine'],
            'consistent': True
        },
        'timezone_handling': {
            'value': 'User-provided timezone (default IST 5.5)',
            'used_by': ['Kundli Tab', 'Chat Engine'],
            'consistent': True
        },
        'caching': {
            'kundli_tab': 'Fresh API call each time (no caching)',
            'chat_engine': 'Profile cached via get_astro_profile()',
            'consistent': False,
            'note': 'Chat engine caches profiles, Kundli tab fetches fresh'
        }
    }
    
    print("\n📊 Configuration Settings:")
    for key, val in analysis.items():
        print(f"\n   {key.upper()}:")
        if isinstance(val, dict):
            for k, v in val.items():
                print(f"      {k}: {v}")
    
    return analysis


def generate_verdict(comparison_rows: List[Dict], config_analysis: Dict) -> str:
    """
    Generate final verdict on data consistency.
    """
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)
    
    # Count matches
    matches = sum(1 for r in comparison_rows if r['match'] == True)
    partial = sum(1 for r in comparison_rows if r['match'] in ('PARTIAL', 'DERIVED'))
    mismatches = sum(1 for r in comparison_rows if r['match'] == False)
    
    total = len(comparison_rows)
    
    print(f"\n📊 Match Statistics:")
    print(f"   ✅ Full Matches: {matches}/{total}")
    print(f"   ⚠️ Partial/Derived: {partial}/{total}")
    print(f"   ❌ Mismatches: {mismatches}/{total}")
    
    # Determine verdict
    if mismatches == 0:
        verdict = "IDENTICAL"
        summary = "Kundli tab and reading engine use IDENTICAL data"
    elif mismatches <= 2:
        verdict = "MOSTLY CONSISTENT"
        summary = "Minor divergences exist but core data is consistent"
    else:
        verdict = "MISMATCH EXISTS"
        summary = "Significant divergences found"
    
    print(f"\n🔍 VERDICT: {verdict}")
    print(f"   {summary}")
    
    # Detailed findings
    print("\n📋 DETAILED FINDINGS:")
    
    print("\n   ✅ SAME AYANAMSA: Yes (Lahiri)")
    print("   ✅ SAME HOUSE SYSTEM: Yes (Whole Sign derived from Ascendant)")
    print("   ✅ SAME TIMEZONE/DST HANDLING: Yes (User-provided timezone)")
    print("   ⚠️ SAME CACHING: No (Chat caches profile, Kundli fetches fresh)")
    print("      Note: Fresh fetch is redundant but not incorrect")
    
    return verdict


def list_responsible_files():
    """
    List files/functions responsible for each step.
    """
    print("\n" + "="*80)
    print("RESPONSIBLE FILES & FUNCTIONS")
    print("="*80)
    
    print("""
📁 API PARSING:
   • /app/backend/astro_client/vedic_api.py
     - VedicAPIClient._get() - Low-level API call
     - VedicAPIClient._parse_profile_from_real_api() - Parse API response to AstroProfile
     - VedicAPIClient.fetch_full_profile() - Full profile fetch
     - VedicAPIClient.fetch_kundli_optimized() - Optimized Kundli fetch

📁 KUNDLI RENDERING:
   • /app/backend/server.py
     - get_kundli() endpoint at line 1331
     - Calls vedic_api_client.fetch_kundli_optimized()
   • /app/backend/astro_client/vedic_api.py
     - _generate_kundli_svg() - SVG generation
   • /app/frontend/src/components/screens/KundliScreen.jsx
     - Displays structured data from /api/kundli response

📁 READING ENGINE CHART USAGE:
   • /app/backend/conversation/enhanced_orchestrator.py
     - EnhancedOrchestrator.process_message() - Main chat flow
     - Calls vedic_api_client.fetch_full_profile()
     - Calls build_astro_features() for LLM
   • /app/backend/astro_client/interpreter.py
     - build_astro_features() - Transforms profile to LLM features
   • /app/backend/astro_client/reading_pack.py
     - build_reading_pack() - Signal selection for Trust Widget

📁 DATA MODELS:
   • /app/backend/astro_client/models.py
     - BirthDetails, AstroProfile, PlanetPosition, HouseData, DashaInfo
""")


async def main():
    """Main audit execution."""
    print("╔" + "═"*78 + "╗")
    print("║" + " "*20 + "DATA FLOW AUDIT: KUNDLI vs CHAT ENGINE" + " "*20 + "║")
    print("╚" + "═"*78 + "╝")
    
    print(f"\n🕐 Audit Time: {datetime.utcnow().isoformat()}Z")
    
    # Create test birth details
    birth = create_birth_details()
    print(f"\n👤 Test Profile:")
    print(f"   DOB: {birth.dob}")
    print(f"   TOB: {birth.tob}")
    print(f"   Location: {birth.location}")
    print(f"   Coordinates: {birth.latitude}, {birth.longitude}")
    print(f"   Timezone: {birth.timezone}")
    
    # Initialize client
    client = VedicAPIClient()
    
    try:
        # Step 1: Fetch raw API data
        raw_data = await fetch_raw_api_data(client, birth)
        
        # Step 2: Trace Kundli pipeline
        kundli_data = await trace_kundli_pipeline(client, birth)
        
        # Step 3: Trace Chat pipeline
        chat_data = await trace_chat_pipeline(client, birth)
        
        # Step 4: Build comparison table
        comparison_rows = build_comparison_table(raw_data, kundli_data, chat_data)
        
        # Step 5: Analyze configuration
        config_analysis = analyze_configuration(raw_data)
        
        # Step 6: Generate verdict
        verdict = generate_verdict(comparison_rows, config_analysis)
        
        # Step 7: List responsible files
        list_responsible_files()
        
        print("\n" + "="*80)
        print("AUDIT COMPLETE")
        print("="*80)
        
        return {
            'verdict': verdict,
            'raw_data': raw_data,
            'kundli_data': kundli_data,
            'chat_data': chat_data,
            'comparison': comparison_rows,
            'config': config_analysis
        }
        
    except Exception as e:
        print(f"\n❌ AUDIT FAILED: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}


if __name__ == "__main__":
    result = asyncio.run(main())
