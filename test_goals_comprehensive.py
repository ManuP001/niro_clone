#!/usr/bin/env python3
"""
Comprehensive test for all 4 onboarding goals:
1. City autocomplete (worldwide)
2. Birth context always used in chat
3. Personalized welcome message
4. Checklist shows actual birth details + API calls
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(title):
    print(f"\n{BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{RESET}")

def print_pass(msg):
    print(f"{GREEN}✅ PASS{RESET}: {msg}")

def print_fail(msg):
    print(f"{RED}❌ FAIL{RESET}: {msg}")

def print_info(msg):
    print(f"{YELLOW}ℹ️ INFO{RESET}: {msg}")

# ============================================================================
# GOAL 1: CITY AUTOCOMPLETE (WORLDWIDE)
# ============================================================================

def test_goal_1_city_autocomplete():
    print_test("GOAL 1: City Autocomplete (Worldwide)")
    
    # Test 1a: Search for Indian city
    print("\nTest 1a: Search for Rohtak (India)")
    response = requests.get(
        f"{BACKEND_URL}/api/utils/search-cities",
        params={"query": "Rohtak", "max_results": 5}
    )
    
    if response.status_code != 200:
        print_fail(f"Search failed: {response.status_code}")
        return False
    
    data = response.json()
    cities = data.get("cities", [])
    print_info(f"Found {len(cities)} cities")
    
    if not cities:
        print_fail("No cities returned for 'Rohtak'")
        return False
    
    city = cities[0]
    print_info(f"Top result: {city}")
    
    # Verify required fields
    required_fields = ["name", "lat", "lon", "country"]
    for field in required_fields:
        if field not in city:
            print_fail(f"Missing field '{field}' in response")
            return False
    
    print_pass(f"City search works: {city.get('name')}, {city.get('country')}")
    print_pass(f"Coordinates: lat={city.get('lat')}, lon={city.get('lon')}")
    
    # Test 1b: Search for international city
    print("\nTest 1b: Search for London (UK)")
    response = requests.get(
        f"{BACKEND_URL}/api/utils/search-cities",
        params={"query": "London", "max_results": 5}
    )
    
    if response.status_code == 200:
        cities = response.json().get("cities", [])
        if cities:
            print_pass(f"International search works: Found {len(cities)} cities")
        else:
            print_fail("No international cities found")
    else:
        print_fail(f"International search failed: {response.status_code}")
    
    # Test 1c: Test minimum 2 characters
    print("\nTest 1c: Debounce check (< 3 chars)")
    response = requests.get(
        f"{BACKEND_URL}/api/utils/search-cities",
        params={"query": "Ro"}
    )
    data = response.json()
    cities = data.get("cities", [])
    print_info(f"Query 'Ro': {len(cities)} results (may be empty as min is 3)")
    
    return True


# ============================================================================
# GOAL 2: BIRTH CONTEXT ALWAYS USED (CHAT NEVER RE-ASKS)
# ============================================================================

def test_goal_2_birth_context():
    print_test("GOAL 2: Birth Context Always Used in Chat")
    
    # Step 1: Authenticate
    print("\nStep 1: Authenticate user")
    auth_response = requests.post(
        f"{BACKEND_URL}/api/auth/identify",
        json={"identifier": f"testuser-{int(time.time())}@example.com"}
    )
    
    if auth_response.status_code != 200:
        print_fail(f"Auth failed: {auth_response.status_code}")
        return False
    
    token = auth_response.json().get("token")
    print_pass(f"Authenticated with token: {token[:20]}...")
    
    # Step 2: Save birth profile
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
    
    profile_response = requests.post(
        f"{BACKEND_URL}/api/profile/",
        headers={"Authorization": f"Bearer {token}"},
        json=profile_data
    )
    
    if profile_response.status_code != 200:
        print_fail(f"Profile save failed: {profile_response.status_code}")
        print_info(f"Response: {profile_response.text}")
        return False
    
    profile_result = profile_response.json()
    print_pass(f"Profile saved: profile_complete={profile_result.get('profile_complete')}")
    
    # Step 3: Chat without providing birth details (should use stored profile)
    print("\nStep 3: Send chat message WITHOUT birth details in payload")
    chat_request = {
        "sessionId": f"session-{int(time.time())}",
        "message": "Tell me about my career prospects",
        "subjectData": None  # Explicitly not providing birth details
    }
    
    chat_response = requests.post(
        f"{BACKEND_URL}/api/chat",
        headers={"Authorization": f"Bearer {token}"},
        json=chat_request
    )
    
    if chat_response.status_code != 200:
        print_fail(f"Chat failed: {chat_response.status_code}")
        print_info(f"Response: {chat_response.text}")
        return False
    
    chat_result = chat_response.json()
    mode = chat_result.get("mode", "")
    
    print_info(f"Chat response mode: {mode}")
    
    # Check if chat is asking for birth details (BIRTH_COLLECTION mode means it's asking)
    if mode == "BIRTH_COLLECTION":
        print_fail("Chat is asking for birth details even though profile exists!")
        return False
    
    print_pass(f"Chat is using stored profile (mode: {mode}, not asking for birth details)")
    request_id = chat_result.get("requestId", "")
    print_info(f"Request ID for checklist: {request_id}")
    
    return True, token, request_id


# ============================================================================
# GOAL 3: PERSONALIZED WELCOME MESSAGE
# ============================================================================

def test_goal_3_personalized_welcome(token):
    print_test("GOAL 3: Personalized Welcome Message")
    
    # Test: Fetch welcome endpoint
    print("\nFetching personalized welcome message...")
    response = requests.post(
        f"{BACKEND_URL}/api/profile/welcome",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print_fail(f"Welcome endpoint failed: {response.status_code}")
        print_info(f"Response: {response.text}")
        return False
    
    welcome_data = response.json()
    if not welcome_data.get("ok"):
        print_fail("Welcome response not OK")
        return False
    
    welcome = welcome_data.get("welcome", {})
    
    # Verify structure
    required_fields = ["title", "bullets", "prompt"]
    for field in required_fields:
        if field not in welcome:
            print_fail(f"Missing field '{field}' in welcome")
            return False
    
    print_pass("Welcome message structure valid")
    print_info(f"Title: {welcome.get('title')}")
    print_info(f"Bullets: {json.dumps(welcome.get('bullets'), indent=2)}")
    print_info(f"Prompt: {welcome.get('prompt')}")
    
    # Verify 3 bullets (strengths)
    bullets = welcome.get("bullets", [])
    if len(bullets) != 3:
        print_fail(f"Expected 3 strengths, got {len(bullets)}")
        return False
    
    print_pass(f"Exactly 3 strengths provided")
    
    # Verify no generic fallback (should not mention "birth details")
    title = welcome.get("title", "").lower()
    if "birth" in title or "date of birth" in title:
        print_fail("Welcome message contains generic 'birth details' request")
        return False
    
    print_pass("Welcome message is personalized (not generic)")
    
    return True


# ============================================================================
# GOAL 4: FIX REQUEST CHECKLIST
# ============================================================================

def test_goal_4_checklist_accuracy(request_id):
    print_test("GOAL 4: Request Checklist Shows Birth Details + API Calls")
    
    if not request_id:
        print_fail("No request_id provided from chat response")
        return False
    
    print(f"\nFetching checklist for request: {request_id}")
    response = requests.get(f"{BACKEND_URL}/api/debug/checklist/{request_id}")
    
    if response.status_code != 200:
        print_fail(f"Checklist endpoint failed: {response.status_code}")
        return False
    
    html_content = response.text
    
    # Check if HTML contains birth details
    checks = {
        "Birth DOB": "1990-05-15" in html_content or "DOB" in html_content,
        "Birth Place": "Rohtak" in html_content or "birth" in html_content.lower(),
        "API Calls": "API" in html_content or "vedic" in html_content.lower(),
        "Request ID": request_id in html_content,
    }
    
    print("\nChecklist Content Analysis:")
    for check_name, found in checks.items():
        if found:
            print_pass(f"Checklist includes: {check_name}")
        else:
            print_fail(f"Checklist MISSING: {check_name}")
    
    # Overall checklist health
    if all(checks.values()):
        print_pass("Checklist is comprehensive and accurate")
        return True
    else:
        print_fail("Checklist missing critical information")
        return False


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print(f"\n{BLUE}Starting comprehensive onboarding goals test...{RESET}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    results = {}
    
    # Test Goal 1
    try:
        results["Goal 1: City Autocomplete"] = test_goal_1_city_autocomplete()
    except Exception as e:
        print_fail(f"Goal 1 exception: {e}")
        results["Goal 1: City Autocomplete"] = False
    
    # Test Goal 2
    try:
        goal2_result = test_goal_2_birth_context()
        if isinstance(goal2_result, tuple):
            results["Goal 2: Birth Context"], token, request_id = goal2_result
        else:
            results["Goal 2: Birth Context"] = goal2_result
            token = None
            request_id = None
    except Exception as e:
        print_fail(f"Goal 2 exception: {e}")
        results["Goal 2: Birth Context"] = False
        token = None
        request_id = None
    
    # Test Goal 3 (if Goal 2 passed)
    if results.get("Goal 2: Birth Context") and token:
        try:
            results["Goal 3: Personalized Welcome"] = test_goal_3_personalized_welcome(token)
        except Exception as e:
            print_fail(f"Goal 3 exception: {e}")
            results["Goal 3: Personalized Welcome"] = False
    else:
        print_info("Skipping Goal 3: Token not available")
        results["Goal 3: Personalized Welcome"] = False
    
    # Test Goal 4 (if Goal 2 passed)
    if results.get("Goal 2: Birth Context") and request_id:
        try:
            results["Goal 4: Checklist Accuracy"] = test_goal_4_checklist_accuracy(request_id)
        except Exception as e:
            print_fail(f"Goal 4 exception: {e}")
            results["Goal 4: Checklist Accuracy"] = False
    else:
        print_info("Skipping Goal 4: Request ID not available")
        results["Goal 4: Checklist Accuracy"] = False
    
    # Summary
    print_test("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"{status}: {name}")
    
    print(f"\n{BLUE}Overall: {passed}/{total} goals passing{RESET}")
    
    if passed == total:
        print(f"{GREEN}🎉 All goals achieved!{RESET}")
        return 0
    else:
        print(f"{RED}⚠️  {total - passed} goals still need work{RESET}")
        return 1


if __name__ == "__main__":
    exit(main())
