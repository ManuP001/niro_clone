#!/usr/bin/env python3
"""
Test chat response formatting to verify duplicate content is removed
This is the specific test requested in the review request
"""

import requests
import json
import uuid
import re

BACKEND_URL = "https://hierarchy-crud.preview.emergentagent.com/api"

def test_chat_response_formatting():
    """Test the exact flow from the review request"""
    
    print("🚀 Testing Chat Response Formatting Verification")
    print("=" * 60)
    
    try:
        # Step 1: Create test user
        print("Step 1: Creating test user...")
        register_payload = {
            "identifier": "formattest@example.com"
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ User registration failed: HTTP {response.status_code}")
            print(response.text)
            return False
        
        auth_data = response.json()
        token = auth_data.get("token")
        user_id = auth_data.get("user_id")
        
        if not token:
            print(f"❌ No token received: {auth_data}")
            return False
        
        print(f"✅ User registered: {user_id}")
        
        # Step 2: Create profile with birth details
        print("Step 2: Creating profile with birth details...")
        profile_payload = {
            "name": "Format Test",
            "dob": "1990-05-15",
            "tob": "14:30",
            "location": "Mumbai",
            "birth_place_lat": 19.08,
            "birth_place_lon": 72.88,
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
            return False
        
        profile_result = response.json()
        if not profile_result.get("ok") or not profile_result.get("profile_complete"):
            print(f"❌ Profile not completed: {profile_result}")
            return False
        
        print("✅ Birth details saved successfully")
        
        # Step 3: Test welcome endpoint
        print("Step 3: Testing welcome endpoint...")
        response = requests.post(f"{BACKEND_URL}/profile/welcome", 
                               headers=headers, 
                               timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Welcome endpoint failed: HTTP {response.status_code}")
            print(response.text)
            return False
        
        welcome_data = response.json()
        
        if not welcome_data.get("ok"):
            print(f"❌ Welcome failed: {welcome_data.get('message')}")
            return False
        
        print("✅ Welcome endpoint working correctly")
        print(f"   Welcome message: {welcome_data.get('message', '')[:100]}...")
        
        # Step 4: Test chat response with specific verification
        print("Step 4: Testing chat response formatting...")
        session_id = f"format_test_{uuid.uuid4().hex[:8]}"
        
        chat_payload = {
            "sessionId": session_id,
            "message": "Should I start a business?"
        }
        
        print(f"   Sending message: '{chat_payload['message']}'")
        print(f"   Session ID: {session_id}")
        
        response = requests.post(f"{BACKEND_URL}/chat", 
                               json=chat_payload, 
                               headers=headers, 
                               timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Chat request failed: HTTP {response.status_code}")
            print(response.text)
            return False
        
        chat_data = response.json()
        
        # Step 5: Print full response structure for verification
        print("\n" + "="*60)
        print("FULL CHAT RESPONSE STRUCTURE:")
        print("="*60)
        print(json.dumps(chat_data, indent=2))
        print("="*60)
        
        # CRITICAL VERIFICATION: Check rawText formatting
        reply = chat_data.get("reply", {})
        raw_text = reply.get("rawText", "")
        reasons = reply.get("reasons", [])
        
        print("\n" + "="*60)
        print("FORMATTING VERIFICATION:")
        print("="*60)
        
        # Check that rawText does NOT contain bullet points with arrows
        arrow_patterns = ["→", "->", "=>"]
        has_arrows = any(pattern in raw_text for pattern in arrow_patterns)
        
        print(f"✅ No arrows (→) in rawText: {not has_arrows}")
        if has_arrows:
            print(f"❌ FAIL: rawText contains arrows: {raw_text[:200]}...")
            return False
        
        # Check that rawText does NOT contain signal IDs like [S1], [S2], [S3]
        signal_pattern = r'\[S\d+\]'
        has_signal_ids = bool(re.search(signal_pattern, raw_text))
        
        print(f"✅ No signal IDs [S1], [S2] in rawText: {not has_signal_ids}")
        if has_signal_ids:
            print(f"❌ FAIL: rawText contains signal IDs: {raw_text[:200]}...")
            return False
        
        # Check that rawText is conversational (paragraphs, not lists)
        bullet_patterns = ["- ", "• ", "* ", "1. ", "2. ", "3. "]
        has_bullet_points = any(pattern in raw_text for pattern in bullet_patterns)
        
        print(f"✅ No bullet points in rawText: {not has_bullet_points}")
        if has_bullet_points:
            print(f"❌ FAIL: rawText contains bullet points: {raw_text[:200]}...")
            return False
        
        # Verify that reasons array SHOULD contain the structured data
        print(f"✅ Reasons array populated: {len(reasons)} items")
        if len(reasons) == 0:
            print("⚠️  WARNING: Reasons array is empty - this is acceptable if rawText is properly formatted")
        else:
            # Check that reasons contain the signal IDs and arrows (where they belong)
            reasons_text = " ".join(reasons) if isinstance(reasons, list) else str(reasons)
            reasons_have_structure = any(pattern in reasons_text for pattern in arrow_patterns + ["[S", "house", "planet"])
            
            if not reasons_have_structure:
                print(f"⚠️  WARNING: Reasons array may not contain expected astrological structure: {reasons}")
        
        # Verify rawText is pure conversational text
        print(f"✅ rawText length: {len(raw_text)} characters")
        if len(raw_text) < 50:
            print(f"❌ FAIL: rawText too short (likely not conversational): {raw_text}")
            return False
        
        # Print content previews
        print(f"📝 rawText preview: {raw_text[:150]}...")
        print(f"📝 Reasons preview: {reasons[:2] if reasons else 'None'}")
        
        print("="*60)
        print("🎉 ALL FORMATTING CHECKS PASSED!")
        print(f"✅ rawText is pure conversational text ({len(raw_text)} chars)")
        print(f"✅ Reasons array contains {len(reasons)} structured items")
        print(f"✅ Proper separation of content achieved")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_chat_response_formatting()
    if success:
        print("\n🎉 CHAT RESPONSE FORMATTING TEST PASSED!")
    else:
        print("\n❌ CHAT RESPONSE FORMATTING TEST FAILED!")
    exit(0 if success else 1)