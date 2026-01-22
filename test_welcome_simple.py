#!/usr/bin/env python3
"""
Simple test for welcome endpoint
"""

import requests
import json

# Backend URL from environment
BACKEND_URL = "https://onboard-overhaul.preview.emergentagent.com/api"

def test_welcome_simple():
    """Test Welcome Message Endpoint with detailed error logging"""
    print("Testing Welcome Message Endpoint...")
    
    try:
        session = requests.Session()
        
        # Step 1: Register a new user
        register_payload = {
            "identifier": f"welcome-test-{int(__import__('time').time())}@example.com"
        }
        
        response = session.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ User Registration failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        auth_data = response.json()
        token = auth_data.get("token")
        user_id = auth_data.get("user_id")
        
        print(f"✅ User registered: {user_id}")
        
        # Step 2: Create profile with birth details
        profile_payload = {
            "name": "Test User",
            "dob": "1990-05-15",
            "tob": "14:30",
            "location": "Mumbai",
            "birth_place_lat": 19.08,
            "birth_place_lon": 72.88,
            "birth_place_tz": 5.5
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = session.post(f"{BACKEND_URL}/profile/", 
                               json=profile_payload, 
                               headers=headers, 
                               timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Profile Creation failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        profile_result = response.json()
        print(f"✅ Profile created: {profile_result}")
        
        # Step 3: Call welcome endpoint
        print("Calling welcome endpoint...")
        response = session.post(f"{BACKEND_URL}/profile/welcome", 
                               headers=headers, 
                               timeout=30)
        
        print(f"Welcome response status: {response.status_code}")
        print(f"Welcome response headers: {dict(response.headers)}")
        print(f"Welcome response text: {response.text}")
        
        if response.status_code != 200:
            print(f"❌ Welcome endpoint failed: HTTP {response.status_code}")
            return False
        
        welcome_data = response.json()
        print(f"✅ Welcome data: {welcome_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_welcome_simple()