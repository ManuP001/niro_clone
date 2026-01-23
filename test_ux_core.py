#!/usr/bin/env python3
"""
Test Chat UX features without authentication (basic functionality)
"""

import requests
import json
import uuid
import re

BACKEND_URL = "https://nirobugs.preview.emergentagent.com/api"

def test_basic_chat_ux_features():
    """Test basic chat UX features without authentication"""
    print("Testing basic chat UX features...")
    
    session = requests.Session()
    session_id = f"test-{uuid.uuid4().hex[:8]}"
    
    # Test basic chat request
    payload = {
        "sessionId": session_id,
        "message": "Hello, tell me about my career prospects"
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/chat", json=payload, timeout=45)
        
        if response.status_code != 200:
            print(f"❌ Chat request failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        print(f"✅ Chat request successful")
        
        # Check for UX upgrade fields
        ux_fields = {
            "trustWidget": "Trust Widget",
            "nextStepChips": "Next Step Chips", 
            "conversationState": "Conversation State",
            "showFeedback": "Show Feedback Flag"
        }
        
        found_fields = []
        missing_fields = []
        
        for field, description in ux_fields.items():
            if field in data:
                found_fields.append(description)
                
                # Validate structure
                if field == "trustWidget" and data[field]:
                    trust_widget = data[field]
                    if "drivers" in trust_widget and "confidence" in trust_widget:
                        drivers = trust_widget["drivers"]
                        confidence = trust_widget["confidence"]
                        
                        # Check for human-readable drivers (no S1/S2 labels)
                        has_signal_ids = False
                        for driver in drivers:
                            if isinstance(driver, dict) and "label" in driver:
                                if re.search(r'\[S\d+\]', driver["label"]):
                                    has_signal_ids = True
                                    break
                        
                        if not has_signal_ids and confidence in ["Low", "Medium", "High"]:
                            print(f"  ✅ Trust Widget: {len(drivers)} drivers, confidence={confidence}")
                        else:
                            print(f"  ⚠️ Trust Widget: Invalid format (signal IDs: {has_signal_ids}, confidence: {confidence})")
                    else:
                        print(f"  ⚠️ Trust Widget: Missing drivers or confidence")
                
                elif field == "nextStepChips":
                    chips = data[field]
                    if isinstance(chips, list) and len(chips) > 0:
                        valid_chips = all(
                            isinstance(chip, dict) and "id" in chip and "label" in chip 
                            for chip in chips
                        )
                        if valid_chips:
                            print(f"  ✅ Next Step Chips: {len(chips)} valid chips")
                        else:
                            print(f"  ⚠️ Next Step Chips: Invalid format")
                    else:
                        print(f"  ⚠️ Next Step Chips: Empty or invalid")
                
                elif field == "conversationState":
                    conv_state = data[field]
                    if isinstance(conv_state, dict):
                        required_fields = ["current_topic", "message_count"]
                        has_required = all(f in conv_state for f in required_fields)
                        if has_required:
                            print(f"  ✅ Conversation State: topic={conv_state.get('current_topic')}, count={conv_state.get('message_count')}")
                        else:
                            print(f"  ⚠️ Conversation State: Missing required fields")
                    else:
                        print(f"  ⚠️ Conversation State: Invalid format")
                
                elif field == "showFeedback":
                    print(f"  ✅ Show Feedback: {data[field]}")
            else:
                missing_fields.append(description)
        
        print(f"\n📊 UX Fields Found: {len(found_fields)}/4")
        print(f"✅ Present: {', '.join(found_fields)}")
        if missing_fields:
            print(f"❌ Missing: {', '.join(missing_fields)}")
        
        return len(found_fields) >= 3  # At least 3 out of 4 UX fields should be present
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_feedback_endpoint():
    """Test feedback endpoint"""
    print("\nTesting feedback endpoint...")
    
    session = requests.Session()
    
    feedback_payload = {
        "response_id": "test-123",
        "session_id": "test-session",
        "feedback": "positive"
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/chat/feedback", json=feedback_payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Feedback endpoint working")
                return True
            else:
                print(f"❌ Feedback failed: {data}")
                return False
        else:
            print(f"❌ Feedback HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Feedback exception: {e}")
        return False

def test_short_reply_detection():
    """Test short reply detection without authentication"""
    print("\nTesting short reply detection...")
    
    session = requests.Session()
    session_id = f"test-short-{uuid.uuid4().hex[:8]}"
    
    try:
        # First message
        payload1 = {
            "sessionId": session_id,
            "message": "Tell me about career"
        }
        
        response1 = session.post(f"{BACKEND_URL}/chat", json=payload1, timeout=45)
        if response1.status_code != 200:
            print(f"❌ First message failed: HTTP {response1.status_code}")
            return False
        
        data1 = response1.json()
        conv_state1 = data1.get("conversationState", {})
        
        # Short reply
        payload2 = {
            "sessionId": session_id,
            "message": "yes"
        }
        
        response2 = session.post(f"{BACKEND_URL}/chat", json=payload2, timeout=45)
        if response2.status_code != 200:
            print(f"❌ Short reply failed: HTTP {response2.status_code}")
            return False
        
        data2 = response2.json()
        conv_state2 = data2.get("conversationState", {})
        reply_text = data2.get("reply", {}).get("rawText", "")
        
        # Check if message count increased
        count1 = conv_state1.get("message_count", 0)
        count2 = conv_state2.get("message_count", 0)
        
        # Check if reply is substantial (context resolved)
        is_substantial = len(reply_text) > 50
        
        if count2 > count1 and is_substantial:
            print(f"✅ Short reply detection: count {count1}→{count2}, reply length: {len(reply_text)}")
            return True
        else:
            print(f"❌ Short reply detection failed: count {count1}→{count2}, reply length: {len(reply_text)}")
            return False
        
    except Exception as e:
        print(f"❌ Short reply exception: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("🎨 CHAT UX UPGRADES - CORE FUNCTIONALITY TEST")
    print("=" * 80)
    
    results = []
    results.append(test_basic_chat_ux_features())
    results.append(test_feedback_endpoint())
    results.append(test_short_reply_detection())
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 80)
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed")
    print("=" * 80)
    
    if passed == total:
        print("🎉 ALL CORE UX FEATURES WORKING!")
    elif passed >= 2:
        print("✅ MOST UX FEATURES WORKING - Minor issues detected")
    else:
        print("⚠️ SIGNIFICANT UX ISSUES DETECTED")
    
    print(f"\nSuccess Rate: {passed/total*100:.1f}%")