#!/usr/bin/env python3
"""
Quick test for new Chat UX features
"""

import requests
import json
import uuid

BACKEND_URL = "https://expert-browse-demo.preview.emergentagent.com/api"

def test_feedback_endpoint():
    """Test the feedback endpoint quickly"""
    print("Testing feedback endpoint...")
    
    session = requests.Session()
    
    feedback_payload = {
        "response_id": "test-123",
        "session_id": "test-session",
        "feedback": "positive"
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/chat/feedback", 
                               json=feedback_payload, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Feedback endpoint working")
                return True
            else:
                print(f"❌ Feedback endpoint failed: {data}")
                return False
        else:
            print(f"❌ Feedback endpoint HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Feedback endpoint exception: {e}")
        return False

def test_chat_response_structure():
    """Test if chat response has new UX fields"""
    print("Testing chat response structure...")
    
    session = requests.Session()
    
    # Create a simple chat request
    session_id = f"test-{uuid.uuid4().hex[:8]}"
    payload = {
        "sessionId": session_id,
        "message": "Hello"
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/chat", 
                               json=payload, 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for new UX fields
            ux_fields = ["trustWidget", "nextStepChips", "conversationState"]
            found_fields = []
            
            for field in ux_fields:
                if field in data:
                    found_fields.append(field)
            
            if len(found_fields) >= 2:
                print(f"✅ Chat response has UX fields: {found_fields}")
                return True
            else:
                print(f"❌ Chat response missing UX fields. Found: {found_fields}, Expected: {ux_fields}")
                print(f"Response keys: {list(data.keys())}")
                return False
        else:
            print(f"❌ Chat endpoint HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat endpoint exception: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🎨 QUICK UX FEATURES TEST")
    print("=" * 50)
    
    results = []
    results.append(test_feedback_endpoint())
    results.append(test_chat_response_structure())
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All UX features working!")
    else:
        print("⚠️ Some UX features need attention")