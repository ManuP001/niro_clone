#!/usr/bin/env python3
"""
Test specific chat fixes for NIRO application
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://mystic-portal-18.preview.emergentagent.com/api"

def test_welcome_message_endpoint():
    """Test Welcome Message Endpoint Fix - POST /api/profile/welcome"""
    print("Testing Welcome Message Endpoint Fix...")
    
    try:
        session = requests.Session()
        
        # Step 1: Register a new user
        register_payload = {
            "identifier": "chatfix-test@example.com"
        }
        
        response = session.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ User Registration failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        auth_data = response.json()
        token = auth_data.get("token")
        user_id = auth_data.get("user_id")
        
        if not token:
            print(f"❌ No token received: {auth_data}")
            return False
        
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
        if not profile_result.get("ok") or not profile_result.get("profile_complete"):
            print(f"❌ Profile not completed: {profile_result}")
            return False
        
        print("✅ Birth details saved successfully")
        
        # Step 3: Call welcome endpoint and measure speed
        start_time = time.time()
        response = session.post(f"{BACKEND_URL}/profile/welcome", 
                               headers=headers, 
                               timeout=30)
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code != 200:
            print(f"❌ Welcome endpoint failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        welcome_data = response.json()
        
        # Verify response structure
        if not welcome_data.get("ok"):
            print(f"❌ Welcome failed: {welcome_data.get('message')}")
            return False
        
        # Verify personalized message exists
        message = welcome_data.get("message", "")
        if not message or len(message) < 50:
            print(f"❌ Message too short or missing: '{message}'")
            return False
        
        # Check for astrological traits (ascendant, moon_sign, sun_sign)
        astro_traits = ["ascendant", "moon", "sun", "sign", "trait"]
        has_astro_content = any(trait.lower() in message.lower() for trait in astro_traits)
        
        if not has_astro_content:
            print(f"❌ No astrological traits detected in message: '{message}'")
            return False
        
        # Verify speed (should be fast - single API call)
        if response_time > 10.0:  # Allow up to 10 seconds for API call
            print(f"❌ Response too slow: {response_time:.2f}s (expected < 10s)")
            return False
        
        print(f"✅ FAST personalized welcome message in {response_time:.2f}s with astrological content")
        print(f"   Message preview: {message[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_chat_endpoint():
    """Test Chat Endpoint Fix - POST /api/chat with proper rawText response"""
    print("\nTesting Chat Endpoint Fix...")
    
    try:
        session = requests.Session()
        
        # Use the same user session from welcome test
        register_payload = {
            "identifier": "chatfix-test@example.com"
        }
        
        response = session.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ User Registration failed: HTTP {response.status_code}")
            return False
        
        auth_data = response.json()
        token = auth_data.get("token")
        
        # Create unique session ID
        session_id = f"chatfix_{uuid.uuid4().hex[:8]}"
        
        # Send chat message with authentication
        chat_payload = {
            "sessionId": session_id,
            "message": "should I start a business or a job?",
            "actionId": None
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = session.post(f"{BACKEND_URL}/chat", 
                               json=chat_payload, 
                               headers=headers, 
                               timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Chat endpoint failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        chat_data = response.json()
        
        # Verify response structure
        if "reply" not in chat_data:
            print(f"❌ No 'reply' field in response: {chat_data}")
            return False
        
        reply = chat_data.get("reply", {})
        
        # Verify rawText exists and has content
        raw_text = reply.get("rawText", "")
        if not raw_text or len(raw_text) < 20:
            print(f"❌ rawText missing or too short: '{raw_text}'")
            return False
        
        # Verify no error messages
        error_indicators = [
            "Sorry, I encountered an error",
            "Unable to generate response",
            "Service unavailable",
            "Please check API configuration"
        ]
        
        for error_msg in error_indicators:
            if error_msg.lower() in raw_text.lower():
                print(f"❌ Error message detected in rawText: '{error_msg}'")
                return False
        
        # Verify the response is about career/business decision
        business_keywords = ["business", "job", "career", "work", "profession", "employment"]
        has_relevant_content = any(keyword.lower() in raw_text.lower() for keyword in business_keywords)
        
        if not has_relevant_content:
            print(f"❌ Response doesn't address business/job question: '{raw_text}'")
            return False
        
        print(f"✅ Chat response with proper rawText ({len(raw_text)} chars) addressing business/job question")
        print(f"   rawText preview: {raw_text[:100]}...")
        
        # Check summary field (can be empty)
        summary = reply.get("summary", "")
        print(f"   Summary: {summary[:50] if summary else '(empty - acceptable)'}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING NIRO CHAT FIXES")
    print("Testing two specific fixes for the NIRO chat application")
    print("=" * 80)
    
    # Test 1: Welcome Message Endpoint
    welcome_success = test_welcome_message_endpoint()
    
    # Test 2: Chat Endpoint
    chat_success = test_chat_endpoint()
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    print(f"Welcome Message Endpoint: {'✅ PASS' if welcome_success else '❌ FAIL'}")
    print(f"Chat Endpoint: {'✅ PASS' if chat_success else '❌ FAIL'}")
    
    if welcome_success and chat_success:
        print("\n🎉 ALL CHAT FIXES WORKING CORRECTLY!")
    else:
        print("\n⚠️  SOME FIXES NEED ATTENTION")
    
    print("=" * 60)