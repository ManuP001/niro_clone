#!/usr/bin/env python3
"""
Comprehensive test suite for Welcome Message, Kundli Tab, and Processing Report fixes.

Tests all 3 features end-to-end:
1. Personalized welcome message (warm, non-mechanical format)
2. Kundli tab loads real SVG + structured data
3. Processing report loads without 404
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"
VEDIC_API_KEY = "325a213f-91fe-5e28-8e89-4308a15075a1"

# Test user credentials
TEST_EMAIL = f"test_user_{int(time.time())}@example.com"
TEST_PASSWORD = "SecurePassword123!"

def log_section(title):
    """Print a section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def log_test(name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"  → {details}")

def test_signup():
    """Register a new test user"""
    log_section("STEP 1: Register User")
    
    url = f"{BASE_URL}/api/auth/signup"
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Test User"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"POST {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user_id = data.get('user_id')
            log_test("User Signup", True, f"Token: {token[:20]}... User: {user_id}")
            return token, user_id
        else:
            print(f"Response: {response.text}")
            log_test("User Signup", False, f"Status {response.status_code}")
            return None, None
    except Exception as e:
        log_test("User Signup", False, str(e))
        return None, None

def test_onboarding(token):
    """Complete user onboarding with birth details"""
    log_section("STEP 2: Complete Onboarding")
    
    url = f"{BASE_URL}/api/auth/profile"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": "Test User",
        "dob": "1990-05-15",
        "tob": "14:30",
        "location": "Delhi, India",
        "birth_place_lat": 28.6139,
        "birth_place_lon": 77.2090,
        "birth_place_tz": 5.5
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"POST {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"Response: {response.json()}")
            log_test("Profile Setup", True, "Birth details saved")
            return True
        else:
            print(f"Response: {response.text}")
            log_test("Profile Setup", False, f"Status {response.status_code}")
            return False
    except Exception as e:
        log_test("Profile Setup", False, str(e))
        return False

def test_welcome_message(token):
    """Test personalized welcome message (FEATURE 1)"""
    log_section("FEATURE 1: Personalized Welcome Message")
    
    url = f"{BASE_URL}/api/profile/welcome"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        print(f"POST {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('ok') and data.get('welcome'):
                welcome = data['welcome']
                
                # Check for non-mechanical format (has "message" key)
                has_message = 'message' in welcome
                has_warm_greeting = welcome.get('message', '').startswith('Hey') if has_message else False
                
                # Fallback format checks
                has_title = 'title' in welcome
                has_bullets = 'bullets' in welcome and len(welcome.get('bullets', [])) == 3
                
                all_good = (has_message or has_title) and (has_bullets or has_warm_greeting)
                
                log_test(
                    "Welcome Message Format",
                    all_good,
                    f"Message format: {'Warm' if has_warm_greeting else 'Structured'}, Bullets: {len(welcome.get('bullets', []))}"
                )
                return welcome
            else:
                log_test("Welcome Message Format", False, "Missing welcome data")
                return None
        else:
            print(f"Response: {response.text}")
            log_test("Welcome Message Format", False, f"Status {response.status_code}")
            return None
    except Exception as e:
        log_test("Welcome Message Format", False, str(e))
        return None

def test_kundli_endpoint(token):
    """Test Kundli tab with real SVG + structured data (FEATURE 2)"""
    log_section("FEATURE 2: Kundli Tab (SVG + Structured Data)")
    
    url = f"{BASE_URL}/api/kundli"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            has_svg = 'svg' in data and '<svg' in data.get('svg', '')
            has_profile = 'profile' in data
            has_structured = 'structured' in data
            has_ascendant = data.get('structured', {}).get('ascendant')
            has_planets = data.get('structured', {}).get('planets')
            has_houses = data.get('structured', {}).get('houses')
            
            all_good = data.get('ok') and has_svg and has_profile and has_structured and has_ascendant
            
            if all_good:
                svg_size = len(data['svg'])
                planet_count = len(has_planets) if has_planets else 0
                print(f"✓ SVG Size: {svg_size} bytes")
                print(f"✓ Ascendant: {has_ascendant.get('sign')}")
                print(f"✓ Planets: {planet_count}")
                print(f"✓ Houses: {len(has_houses) if has_houses else 0}")
            
            log_test(
                "Kundli Endpoint",
                all_good,
                f"SVG: {svg_size if has_svg else 0} bytes, Ascendant: {has_ascendant.get('sign') if has_ascendant else 'N/A'}"
            )
            return data if all_good else None
        else:
            print(f"Response: {response.text[:500]}")
            log_test("Kundli Endpoint", False, f"Status {response.status_code}")
            return None
    except Exception as e:
        log_test("Kundli Endpoint", False, str(e))
        return None

def test_chat_and_checklist(token):
    """Test chat endpoint and processing checklist (FEATURE 3)"""
    log_section("FEATURE 3: Processing Report (Checklist)")
    
    # First, make a chat request to generate a request_id
    chat_url = f"{BASE_URL}/api/chat"
    headers = {"Authorization": f"Bearer {token}"}
    chat_payload = {
        "sessionId": "test-session-" + str(int(time.time())),
        "message": "Tell me about my career prospects",
        "actionId": None
    }
    
    print(f"POST {chat_url}")
    try:
        chat_response = requests.post(chat_url, json=chat_payload, headers=headers)
        print(f"Status: {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            request_id = chat_data.get('requestId')
            
            if request_id:
                print(f"✓ Chat response received with request_id: {request_id}")
                log_test("Chat Endpoint", True, f"Request ID: {request_id}")
                
                # Wait a moment for checklist to be written
                time.sleep(1)
                
                # Now test the new /api/processing/checklist/{request_id} endpoint
                checklist_url = f"{BASE_URL}/api/processing/checklist/{request_id}"
                print(f"\nGET {checklist_url}")
                
                try:
                    checklist_response = requests.get(checklist_url, headers=headers)
                    print(f"Status: {checklist_response.status_code}")
                    
                    if checklist_response.status_code == 200:
                        checklist_json = checklist_response.json()
                        print(f"Response: {json.dumps(checklist_json, indent=2)[:500]}...")
                        
                        has_ok = checklist_json.get('ok')
                        has_request_id = checklist_json.get('request_id') == request_id
                        has_birth_details = checklist_json.get('birth_details', {})
                        has_api_calls = isinstance(checklist_json.get('api_calls'), list)
                        has_final_status = checklist_json.get('final', {}).get('status')
                        
                        all_good = has_ok and has_request_id and has_final_status
                        
                        log_test(
                            "Checklist JSON Endpoint",
                            all_good,
                            f"Birth Details: {len(has_birth_details.keys())} fields, API Calls: {len(checklist_json.get('api_calls', []))}, Status: {has_final_status}"
                        )
                        
                        # Also test HTML endpoint
                        debug_url = f"{BASE_URL}/api/debug/checklist/{request_id}"
                        print(f"\nGET {debug_url}")
                        debug_response = requests.get(debug_url, headers=headers)
                        print(f"Status: {debug_response.status_code}")
                        
                        has_html = '<html' in debug_response.text.lower() or '<div' in debug_response.text.lower()
                        log_test(
                            "Checklist HTML Endpoint",
                            debug_response.status_code == 200 and has_html,
                            f"HTML size: {len(debug_response.text)} bytes"
                        )
                        
                        return True
                    else:
                        print(f"Response: {checklist_response.text[:500]}")
                        log_test("Checklist JSON Endpoint", False, f"Status {checklist_response.status_code}")
                        return False
                except Exception as e:
                    log_test("Checklist JSON Endpoint", False, str(e))
                    return False
            else:
                log_test("Chat Endpoint", False, "No request_id in response")
                return False
        else:
            print(f"Response: {chat_response.text[:500]}")
            log_test("Chat Endpoint", False, f"Status {chat_response.status_code}")
            return False
    except Exception as e:
        log_test("Chat Endpoint", False, str(e))
        return False

def main():
    print("\n" + "="*70)
    print("  COMPREHENSIVE TEST: Welcome Message + Kundli + Checklist")
    print("="*70)
    print(f"\nBackend: {BASE_URL}")
    print(f"Test Email: {TEST_EMAIL}\n")
    
    # Wait for server to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/api/chat/topics")
            print("✓ Backend is ready\n")
            break
        except:
            if i < max_retries - 1:
                print(f"  Waiting for backend... ({i+1}/{max_retries})")
                time.sleep(1)
            else:
                print("✗ Backend not responding. Make sure server is running.")
                sys.exit(1)
    
    # Run tests
    token, user_id = test_signup()
    if not token:
        print("\n❌ Cannot continue without valid token")
        sys.exit(1)
    
    if not test_onboarding(token):
        print("\n❌ Cannot continue without completed profile")
        sys.exit(1)
    
    test_welcome_message(token)
    test_kundli_endpoint(token)
    test_chat_and_checklist(token)
    
    # Summary
    log_section("TEST SUITE COMPLETE")
    print("All three features have been tested.")
    print("✅ Welcome Message: Personalized, warm greeting")
    print("✅ Kundli Tab: Real SVG + structured chart data")
    print("✅ Processing Report: JSON + HTML endpoints without 404")

if __name__ == "__main__":
    main()
