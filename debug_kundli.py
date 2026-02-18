#!/usr/bin/env python3
"""
Debug Kundli API to see what's actually being returned
"""

import requests
import json

# Backend URL from environment
BACKEND_URL = "https://responsive-refactor-2.preview.emergentagent.com/api"

def debug_kundli_api():
    """Debug the Kundli API endpoint"""
    
    # Step 1: Register a new user
    register_payload = {
        "identifier": "debug_kundli_test@example.com"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ User registration failed: HTTP {response.status_code}")
        print(response.text)
        return
    
    auth_data = response.json()
    token = auth_data.get("token")
    
    print(f"✅ User registered, token: {token[:20]}...")
    
    # Step 2: Complete onboarding with birth details
    profile_payload = {
        "name": "Debug User",
        "dob": "1990-05-15",
        "tob": "10:30",
        "location": "New Delhi, India",
        "birth_place_lat": 28.6139,
        "birth_place_lon": 77.2090,
        "birth_place_tz": 5.5
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BACKEND_URL}/profile/", 
                           json=profile_payload, 
                           headers=headers, 
                           timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Profile creation failed: HTTP {response.status_code}")
        print(response.text)
        return
    
    print("✅ Profile created successfully")
    
    # Step 3: Fetch Kundli chart
    response = requests.get(f"{BACKEND_URL}/kundli", 
                          headers=headers, 
                          timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Kundli API failed: HTTP {response.status_code}")
        print(response.text)
        return
    
    kundli_data = response.json()
    
    print("✅ Kundli API response received")
    print(f"Response keys: {list(kundli_data.keys())}")
    print(f"OK status: {kundli_data.get('ok')}")
    
    if kundli_data.get("ok"):
        svg_content = kundli_data.get("svg", "")
        print(f"SVG content length: {len(svg_content)}")
        print(f"SVG starts with: {repr(svg_content[:100])}")
        print(f"SVG ends with: {repr(svg_content[-100:])}")
        
        # Check if it's actually SVG
        if svg_content.startswith("<svg") or svg_content.startswith("<?xml"):
            print("✅ SVG content looks valid")
        else:
            print("❌ SVG content doesn't start with proper tags")
            
        # Check structured data
        structured = kundli_data.get("structured", {})
        print(f"Structured data keys: {list(structured.keys())}")
        
        if "houses" in structured:
            print(f"Houses count: {len(structured['houses'])}")
        if "planets" in structured:
            print(f"Planets count: {len(structured['planets'])}")
            
    else:
        print(f"❌ Kundli fetch failed: {kundli_data.get('message', 'Unknown error')}")
        print(f"Error: {kundli_data.get('error', 'No error code')}")

if __name__ == "__main__":
    debug_kundli_api()