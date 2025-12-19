#!/usr/bin/env python3
"""
Test script to verify the /api/kundli endpoint.
Tests both success and error cases.
"""

import asyncio
import sys
from pathlib import Path
from datetime import date

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_vedic_api():
    """Test VedicAPIClient directly"""
    print("\n" + "="*80)
    print("TESTING VEDIC API CLIENT")
    print("="*80)
    
    from backend.astro_client.vedic_api import VedicAPIClient, VedicApiError
    from backend.astro_client.models import BirthDetails
    
    # Create test birth details
    birth_details = BirthDetails(
        dob=date(1990, 1, 15),
        tob="14:30",
        location="Mumbai",
        latitude=19.0760,
        longitude=72.8777,
        timezone=5.5
    )
    
    print(f"\nTest Birth Details:")
    print(f"  DOB: {birth_details.dob}")
    print(f"  TOB: {birth_details.tob}")
    print(f"  Location: {birth_details.location}")
    print(f"  Lat/Lon: {birth_details.latitude}/{birth_details.longitude}")
    
    # Test 1: Missing API Key
    print("\n" + "-"*80)
    print("Test 1: Missing API Key")
    print("-"*80)
    
    import os
    old_key = os.environ.get('VEDIC_API_KEY')
    os.environ['VEDIC_API_KEY'] = ''
    
    client = VedicAPIClient()
    
    try:
        print("Attempting to fetch profile without API key...")
        profile = await client.fetch_full_profile(birth_details)
        print(f"❌ ERROR: Should have raised VedicApiError but got: {profile}")
    except VedicApiError as e:
        print(f"✅ Correctly raised VedicApiError:")
        print(f"   Error Code: {e.error_code}")
        print(f"   Message: {e.message}")
        print(f"   Details: {e.details}")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
    
    # Test 2: With API Key (if available)
    print("\n" + "-"*80)
    print("Test 2: With API Key (Real API Call)")
    print("-"*80)
    
    if old_key:
        os.environ['VEDIC_API_KEY'] = old_key
        client = VedicAPIClient()
        
        try:
            print(f"Attempting to fetch profile with API key: {old_key[:20]}...")
            profile = await client.fetch_full_profile(birth_details)
            print(f"✅ Successfully fetched profile:")
            print(f"   Ascendant: {profile.ascendant} ({profile.ascendant_degree}°)")
            print(f"   Moon Sign: {profile.moon_sign}")
            print(f"   Sun Sign: {profile.sun_sign}")
            print(f"   Planets: {len(profile.planets)} total")
            for planet in profile.planets[:3]:
                print(f"     - {planet.name}: {planet.sign} {planet.degree}° (House {planet.house})")
            if len(profile.planets) > 3:
                print(f"     ... and {len(profile.planets) - 3} more")
            print(f"   Houses: {len(profile.houses)}")
            print(f"   Yogas: {len(profile.yogas)}")
            
        except VedicApiError as e:
            print(f"⚠️  VedicApiError (API call failed):")
            print(f"   Error Code: {e.error_code}")
            print(f"   Message: {e.message}")
            if e.error_code == "VEDIC_API_KEY_MISSING":
                print(f"   → API key is not configured")
            elif e.error_code == "VEDIC_API_UNAVAILABLE":
                print(f"   → API is unreachable or returned HTTP error")
            elif e.error_code == "VEDIC_API_BAD_RESPONSE":
                print(f"   → API returned invalid/incomplete data")
        except Exception as e:
            print(f"❌ Unexpected error: {type(e).__name__}: {e}")
    else:
        print("⚠️  No API key configured - skipping real API test")
        print("   Set VEDIC_API_KEY environment variable to test real API calls")


async def test_kundli_svg():
    """Test Kundli SVG fetch"""
    print("\n" + "="*80)
    print("TESTING KUNDLI SVG FETCH")
    print("="*80)
    
    from backend.astro_client.vedic_api import VedicAPIClient, VedicApiError
    from backend.astro_client.models import BirthDetails
    import os
    
    birth_details = BirthDetails(
        dob=date(1990, 1, 15),
        tob="14:30",
        location="Mumbai",
        latitude=19.0760,
        longitude=72.8777,
        timezone=5.5
    )
    
    api_key = os.environ.get('VEDIC_API_KEY')
    
    if not api_key:
        print("\n⚠️  Skipping SVG test (no API key configured)")
        return
    
    client = VedicAPIClient()
    
    try:
        print(f"\nAttempting to fetch Kundli SVG...")
        svg_result = await client.fetch_kundli_svg(birth_details)
        
        if svg_result.get('ok'):
            svg_content = svg_result.get('svg', '')
            print(f"✅ Successfully fetched SVG:")
            print(f"   Size: {len(svg_content)} characters")
            print(f"   Contains <svg>: {svg_content[:50]}...")
            print(f"   Chart Type: {svg_result.get('chart_type')}")
            print(f"   Vendor: {svg_result.get('vendor')}")
        else:
            print(f"⚠️  SVG fetch returned ok=false:")
            print(f"   {svg_result}")
            
    except VedicApiError as e:
        print(f"⚠️  VedicApiError:")
        print(f"   Error Code: {e.error_code}")
        print(f"   Message: {e.message}")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")


async def test_niro_llm():
    """Test NIRO LLM behavior"""
    print("\n" + "="*80)
    print("TESTING NIRO LLM")
    print("="*80)
    
    from backend.conversation.niro_llm import NiroLLM
    import os
    
    openai_key = os.environ.get('OPENAI_API_KEY', '')
    gemini_key = os.environ.get('GEMINI_API_KEY', '')
    
    print(f"\nLLM Configuration:")
    print(f"  OpenAI Key: {'✅ Configured' if openai_key else '❌ Not configured'}")
    print(f"  Gemini Key: {'✅ Configured' if gemini_key else '❌ Not configured'}")
    
    # Test without real LLM
    print("\n" + "-"*80)
    print("Test: Call with no keys configured")
    print("-"*80)
    
    with __import__('unittest.mock').mock.patch.dict(os.environ, {
        'OPENAI_API_KEY': '',
        'GEMINI_API_KEY': ''
    }, clear=False):
        llm = NiroLLM()
        
        print(f"LLM initialized with use_real_llm={llm.use_real_llm}")
        
        payload = {
            'mode': 'GENERAL_GUIDANCE',
            'focus': None,
            'user_question': 'What does my chart say?',
            'astro_features': {'ascendant': 'Aries'}
        }
        
        try:
            print("Attempting to generate LLM response without API keys...")
            response = llm.call_niro_llm(payload)
            print(f"❌ ERROR: Should have raised RuntimeError but got response")
        except RuntimeError as e:
            print(f"✅ Correctly raised RuntimeError:")
            print(f"   Message: {str(e)}")
        except Exception as e:
            print(f"⚠️  Error (type may vary): {type(e).__name__}: {e}")


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "API AND COMPONENT TESTING".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    await test_vedic_api()
    await test_kundli_svg()
    await test_niro_llm()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80 + "\n")


if __name__ == '__main__':
    asyncio.run(main())
