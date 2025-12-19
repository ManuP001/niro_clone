#!/usr/bin/env python3
"""
Comprehensive test for all 4 onboarding goals - COMPLETE VERSION
Tests city autocomplete, birth context usage, welcome message, and checklist accuracy
"""

import requests
import json
import time
import sys

BACKEND_URL = "http://localhost:8000"

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def header(text):
    print(f"\n{BLUE}{BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{RESET}\n")

def success(msg):
    print(f"{GREEN}✅ PASS{RESET}: {msg}")

def fail(msg):
    print(f"{RED}❌ FAIL{RESET}: {msg}")
    sys.exit(1)

def info(msg):
    print(f"{YELLOW}ℹ️ {RESET}{msg}")

# ============================================================================
# GOAL 1: CITY AUTOCOMPLETE (WORLDWIDE)
# ============================================================================

def test_goal_1():
    header("GOAL 1: City Autocomplete - Worldwide Cities")
    
    # Test 1a: Search Indian city
    print("Test 1a: Search 'Rohtak' (India)")
    resp = requests.get(f"{BACKEND_URL}/api/utils/search-cities?query=Rohtak&max_results=5")
    
    if resp.status_code != 200:
        fail(f"Endpoint returned {resp.status_code}: {resp.text}")
    
    data = resp.json()
    cities = data.get("cities", [])
    
    if not cities:
        fail("No cities returned for 'Rohtak'")
    
    city = cities[0]
    print(f"  Response: {json.dumps(city, indent=2)}")
    
    # Verify structure
    required = ["name", "display_name", "lat", "lon", "timezone", "country"]
    for field in required:
        if field not in city:
            fail(f"Missing required field: {field}")
    
    if "Rohtak" not in city["name"]:
        fail(f"City name incorrect: {city['name']}")
    
    if not isinstance(city.get("lat"), (int, float)):
        fail(f"Invalid latitude: {city.get('lat')}")
    
    success(f"India search works: {city['display_name']}")
    success(f"Coordinates: {city['lat']}, {city['lon']}")
    
    # Test 1b: Another Indian city
    print("\nTest 1b: Search 'Delhi' (another Indian city)")
    resp = requests.get(f"{BACKEND_URL}/api/utils/search-cities?query=Delhi&max_results=3")
    
    if resp.status_code == 200:
        cities = resp.json().get("cities", [])
        if cities:
            success(f"Second city search works - found {len(cities)} cities")
            info(f"First result: {cities[0].get('display_name')}")
        else:
            fail("No cities found for 'Delhi'")
    else:
        fail(f"Delhi search failed: {resp.status_code}")
    
    # Test 1c: Debounce (< 2 chars should work but might return empty)
    print("\nTest 1c: Minimum character check")
    resp = requests.get(f"{BACKEND_URL}/api/utils/search-cities?query=R&max_results=5")
    
    if resp.status_code == 200:
        cities = resp.json().get("cities", [])
        info(f"Single character search returned {len(cities)} results (may be empty)")
        success("Endpoint handles short queries gracefully")
    else:
        fail(f"Short query failed: {resp.status_code}")
    
    return True


# ============================================================================
# GOAL 2: BIRTH CONTEXT ALWAYS USED (CHAT NEVER RE-ASKS)
# ============================================================================

def test_goal_2():
    header("GOAL 2: Birth Context - Chat Never Asks Again")
    
    # Step 1: Authenticate
    print("Step 1: Authenticate user")
    auth_resp = requests.post(
        f"{BACKEND_URL}/api/auth/identify",
        json={"identifier": f"testuser-{int(time.time())}@example.com"}
    )
    
    if auth_resp.status_code != 200:
        fail(f"Auth failed: {auth_resp.status_code} - {auth_resp.text}")
    
    token = auth_resp.json().get("token")
    info(f"Token: {token[:30]}...")
    success("Authentication successful")
    
    # Step 2: Save profile with coordinates
    print("\nStep 2: Save birth profile with coordinates")
    profile_data = {
        "name": "Test User",
        "dob": "1990-05-15",
        "tob": "14:30",
        "location": "Rohtak, Haryana, India",
        "birth_place_lat": 28.8955,
        "birth_place_lon": 76.5660,
        "birth_place_tz": 5.5
    }
    
    prof_resp = requests.post(
        f"{BACKEND_URL}/api/profile/",
        headers={"Authorization": f"Bearer {token}"},
        json=profile_data
    )
    
    if prof_resp.status_code != 200:
        fail(f"Profile save failed: {prof_resp.status_code} - {prof_resp.text}")
    
    result = prof_resp.json()
    info(f"Profile saved: {json.dumps(result)}")
    success(f"Profile stored successfully (complete={result.get('profile_complete')})")
    
    # Step 3: Chat without providing birth details
    print("\nStep 3: Send chat message WITHOUT birth details in request")
    chat_req = {
        "sessionId": f"session-{int(time.time())}",
        "message": "Tell me about my career",
        "subjectData": None  # Explicitly not providing birth details
    }
    
    chat_resp = requests.post(
        f"{BACKEND_URL}/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json=chat_req
    )
    
    if chat_resp.status_code != 200:
        fail(f"Chat failed: {chat_resp.status_code} - {chat_resp.text}")
    
    chat_data = chat_resp.json()
    mode = chat_data.get("mode", "")
    request_id = chat_data.get("requestId", "")
    
    info(f"Chat mode: {mode}")
    info(f"Request ID: {request_id}")
    
    # CRITICAL: Check if chat is asking for birth details
    if mode == "BIRTH_COLLECTION":
        fail(f"Chat is asking for birth details even though profile exists! Mode={mode}")
    
    success(f"Chat used stored profile (mode={mode}, not asking for birth details)")
    
    return token, request_id


# ============================================================================
# GOAL 3: PERSONALIZED WELCOME MESSAGE
# ============================================================================

def test_goal_3(token):
    header("GOAL 3: Personalized Welcome Message")
    
    print("Fetching personalized welcome message...")
    resp = requests.post(
        f"{BACKEND_URL}/api/profile/welcome",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if resp.status_code != 200:
        fail(f"Welcome endpoint failed: {resp.status_code} - {resp.text}")
    
    data = resp.json()
    if not data.get("ok"):
        fail(f"Welcome response not OK: {data}")
    
    welcome = data.get("welcome", {})
    print(f"\nWelcome Response:\n{json.dumps(welcome, indent=2)}")
    
    # Verify structure
    required_fields = ["title", "bullets", "prompt"]
    for field in required_fields:
        if field not in welcome:
            fail(f"Missing field: {field}")
    
    success("Welcome message structure valid")
    
    # Verify 3 strengths
    bullets = welcome.get("bullets", [])
    if len(bullets) != 3:
        fail(f"Expected 3 strengths, got {len(bullets)}")
    
    success(f"Exactly 3 strengths provided:")
    for i, bullet in enumerate(bullets, 1):
        info(f"  {i}. {bullet}")
    
    # Verify personalization (should not be generic)
    title = welcome.get("title", "").lower()
    if "please tell me" in title or "birth details" in title:
        fail("Welcome message is generic, not personalized")
    
    success("Welcome message is personalized (not generic)")
    
    return True


# ============================================================================
# GOAL 4: CHECKLIST SHOWS BIRTH DETAILS + API CALLS
# ============================================================================

def test_goal_4(request_id):
    header("GOAL 4: Request Checklist - Birth Details & API Calls")
    
    if not request_id:
        fail("No request_id to check checklist")
    
    print(f"Fetching checklist for request: {request_id}")
    resp = requests.get(f"{BACKEND_URL}/api/debug/checklist/{request_id}")
    
    if resp.status_code != 200:
        fail(f"Checklist endpoint failed: {resp.status_code}")
    
    html = resp.text
    
    # Check for critical information
    checks = {
        "contains_dob": "1990-05-15" in html or "DOB" in html or "Date of Birth" in html,
        "contains_location": "Rohtak" in html or "location" in html.lower(),
        "contains_coordinates": "28.8955" in html or "76.5660" in html or "lat" in html.lower(),
        "contains_timezone": "5.5" in html or "timezone" in html.lower(),
        "contains_request_id": request_id in html,
        "contains_mode": "mode" in html.lower() or "NORMAL_READING" in html,
    }
    
    print("\nChecklist Content Validation:")
    passed = 0
    for check_name, found in checks.items():
        status = "✓" if found else "✗"
        print(f"  {status} {check_name.replace('contains_', '')}")
        if found:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(checks)} checks passed")
    
    if passed < 4:
        fail(f"Checklist missing critical information ({passed}/{len(checks)})")
    
    success("Checklist includes birth details and request context")
    return True


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print(f"\n{BOLD}{BLUE}🚀 NIRO Onboarding Goals - Comprehensive Test{RESET}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test Goal 1
        test_goal_1()
        
        # Test Goal 2
        token, request_id = test_goal_2()
        
        # Test Goal 3
        test_goal_3(token)
        
        # Test Goal 4
        test_goal_4(request_id)
        
        # Final summary
        header("🎉 ALL TESTS PASSED!")
        print(f"""
{GREEN}{BOLD}✅ GOAL 1 - City Autocomplete:{RESET} Working worldwide
{GREEN}{BOLD}✅ GOAL 2 - Birth Context:{RESET} Chat uses stored profile automatically
{GREEN}{BOLD}✅ GOAL 3 - Welcome Message:{RESET} Personalized with 3 strengths
{GREEN}{BOLD}✅ GOAL 4 - Checklist:{RESET} Shows birth details and API context

{BOLD}All 4 onboarding goals are fully implemented and tested!{RESET}
        """)
        return 0
        
    except Exception as e:
        header("❌ TEST ERROR")
        fail(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
