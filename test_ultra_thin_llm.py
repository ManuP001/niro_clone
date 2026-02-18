#!/usr/bin/env python3
"""
Ultra-Thin LLM Architecture Testing for NIRO Chat
Tests the specific review request requirements
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://responsive-dashboard-14.preview.emergentagent.com/api"

def test_ultra_thin_llm_architecture():
    """Test Ultra-Thin LLM Architecture for NIRO chat as per review request"""
    session = requests.Session()
    
    try:
        print("🔬 Testing Ultra-Thin LLM Architecture...")
        
        # Step 1: Create test user
        print("Step 1: Creating test user...")
        user_payload = {
            "identifier": "ultrathin-test@example.com"
        }
        
        response = session.post(f"{BACKEND_URL}/auth/identify", json=user_payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ User creation failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        user_data = response.json()
        token = user_data.get("token")
        
        if not token:
            print(f"❌ No token received: {user_data}")
            return False
        
        print(f"✅ User created with token")
        
        # Step 2: Create profile
        print("Step 2: Creating profile...")
        profile_payload = {
            "name": "Test User",
            "dob": "1990-05-15",
            "tob": "14:30",
            "location": "Mumbai",
            "lat": 19.08,
            "lon": 72.88
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = session.post(f"{BACKEND_URL}/profile/", json=profile_payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Profile creation failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print(f"✅ Profile created with birth details")
        
        # Step 3: Test Chat endpoint with business question
        print("Step 3: Testing chat with business question...")
        chat_payload = {
            "sessionId": f"ultrathin_{uuid.uuid4().hex[:8]}",
            "message": "Should I start a business?",
            "actionId": None
        }
        
        start_time = time.time()
        response = session.post(f"{BACKEND_URL}/chat", json=chat_payload, headers=headers, timeout=60)
        response_time = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ Chat business question failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        chat_data = response.json()
        
        # VERIFY: Response returns within reasonable time
        print(f"✅ Response time: {response_time:.2f}s")
        if response_time > 30:
            print(f"⚠️  Response time {response_time:.2f}s is quite slow")
        
        # VERIFY: reply.rawText contains natural conversational text
        reply = chat_data.get("reply", {})
        raw_text = reply.get("rawText", "")
        
        if not raw_text or len(raw_text) < 50:
            print(f"❌ rawText too short or missing: '{raw_text}'")
            return False
        
        print(f"✅ rawText contains {len(raw_text)} characters of content")
        
        # VERIFY: reply.rawText does NOT contain [S1], [S2] signal IDs
        signal_ids = ["[S1]", "[S2]", "[S3]", "[S4]", "[S5]"]
        found_signals = [sid for sid in signal_ids if sid in raw_text]
        
        if found_signals:
            print(f"❌ Found signal IDs in rawText: {found_signals}")
            print(f"Raw text preview: {raw_text[:200]}")
            return False
        
        print(f"✅ No signal IDs found in rawText")
        
        # VERIFY: reply.reasons array is populated
        reasons = reply.get("reasons", [])
        
        if not isinstance(reasons, list) or len(reasons) == 0:
            print(f"❌ Reasons array empty or invalid: {reasons}")
            return False
        
        print(f"✅ Reasons array populated with {len(reasons)} items")
        
        # VERIFY: trustWidget.drivers contains entries (if present)
        trust_widget = chat_data.get("trustWidget", {})
        if trust_widget:
            drivers = trust_widget.get("drivers", [])
            if not isinstance(drivers, list):
                print(f"❌ Trust widget drivers not a list: {drivers}")
                return False
            print(f"✅ Trust widget drivers: {len(drivers)} entries")
        else:
            print(f"ℹ️  No trust widget in response (may be expected)")
        
        # Step 4: Test greeting handling
        print("Step 4: Testing greeting handling...")
        greeting_payload = {
            "sessionId": f"ultrathin_greeting_{uuid.uuid4().hex[:8]}",
            "message": "hi",
            "actionId": None
        }
        
        start_time = time.time()
        response = session.post(f"{BACKEND_URL}/chat", json=greeting_payload, headers=headers, timeout=30)
        greeting_response_time = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ Greeting handling failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        greeting_data = response.json()
        
        # VERIFY: Quick response without full LLM call (preset response)
        print(f"✅ Greeting response time: {greeting_response_time:.2f}s")
        if greeting_response_time > 10:
            print(f"⚠️  Greeting response time {greeting_response_time:.2f}s is quite slow for preset")
        
        # Check if greeting has appropriate content
        greeting_reply = greeting_data.get("reply", {})
        greeting_text = greeting_reply.get("rawText", "")
        
        if not greeting_text:
            print(f"❌ No greeting response text")
            return False
        
        print(f"✅ Greeting response generated")
        
        print(f"\n🎉 Ultra-Thin LLM Architecture Test PASSED!")
        print(f"   Business response: {response_time:.2f}s")
        print(f"   Greeting response: {greeting_response_time:.2f}s")
        print(f"   Reasons: {len(reasons)} items")
        print(f"   No signal IDs found")
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def check_backend_logs():
    """Check backend logs for LLM optimization indicators"""
    try:
        print("\n📋 Checking backend logs for LLM optimization...")
        
        # We can't directly access logs, but we can check supervisor logs
        import subprocess
        
        try:
            # Check backend logs
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for LLM optimization indicators
                llm_indicators = [
                    "[LLM CALL] prompt_size=",
                    "[LLM RESPONSE]",
                    "prompt_size",
                    "tokens_in",
                    "tokens_out"
                ]
                
                found_indicators = []
                for indicator in llm_indicators:
                    if indicator in logs:
                        found_indicators.append(indicator)
                
                if found_indicators:
                    print(f"✅ Found LLM optimization indicators: {found_indicators}")
                    
                    # Look for prompt size information
                    lines = logs.split('\n')
                    for line in lines:
                        if "prompt_size=" in line:
                            print(f"   📏 {line.strip()}")
                        elif "[LLM RESPONSE]" in line:
                            print(f"   📤 {line.strip()}")
                else:
                    print(f"ℹ️  No specific LLM optimization indicators found in recent logs")
                
                return True
            else:
                print(f"⚠️  Could not read backend logs: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⚠️  Timeout reading backend logs")
            return False
        except FileNotFoundError:
            print(f"⚠️  Backend log file not found")
            return False
            
    except Exception as e:
        print(f"❌ Exception checking logs: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Ultra-Thin LLM Architecture Testing...")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    success = test_ultra_thin_llm_architecture()
    
    if success:
        check_backend_logs()
    
    print("=" * 60)
    if success:
        print("✅ ULTRA-THIN LLM ARCHITECTURE TEST COMPLETED SUCCESSFULLY")
    else:
        print("❌ ULTRA-THIN LLM ARCHITECTURE TEST FAILED")