#!/usr/bin/env python3
"""
Chat Quality Enhancement Tests - Focused Testing
Tests the 6 specific Chat Quality Enhancement features from the review request
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://astro-admin-5.preview.emergentagent.com/api"

class ChatQualityTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if response_data and not success:
            print(f"   Response: {response_data}")
    
    def test_chat_quality_trust_widget_no_confidence(self):
        """Test TRUST WIDGET - NO CONFIDENCE: Verify response.trustWidget does NOT contain confidence field"""
        try:
            # Step 1: Create test user and profile
            register_payload = {
                "identifier": "quality-test@example.com"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Quality Test - User Registration", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            auth_data = response.json()
            token = auth_data.get("token")
            
            # Create profile with birth details
            profile_payload = {
                "name": "Quality Test",
                "dob": "1990-05-15",
                "tob": "14:30",
                "location": "Mumbai",
                "birth_place_lat": 19.08,
                "birth_place_lon": 72.88,
                "birth_place_tz": 5.5
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.post(f"{BACKEND_URL}/profile/", 
                                       json=profile_payload, 
                                       headers=headers, 
                                       timeout=10)
            
            if response.status_code != 200:
                self.log_result("Quality Test - Profile Creation", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Step 2: Send career message
            session_id = f"quality-test-{uuid.uuid4().hex[:8]}"
            career_payload = {
                "sessionId": session_id,
                "message": "Tell me about my career",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", 
                                       json=career_payload, 
                                       headers=headers,
                                       timeout=30)
            
            if response.status_code != 200:
                self.log_result("Trust Widget No Confidence", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Step 3: Verify trustWidget structure
            if "trustWidget" not in data:
                self.log_result("Trust Widget No Confidence", False, 
                              "Missing trustWidget in response", data)
                return False
            
            trust_widget = data["trustWidget"]
            
            # CRITICAL: Verify NO confidence field
            if "confidence" in trust_widget:
                self.log_result("Trust Widget No Confidence", False, 
                              "CONFIDENCE FIELD FOUND - should be removed", trust_widget)
                return False
            
            # Verify drivers exists and has descriptive labels
            if "drivers" not in trust_widget:
                self.log_result("Trust Widget No Confidence", False, 
                              "Missing drivers field", trust_widget)
                return False
            
            drivers = trust_widget["drivers"]
            if not isinstance(drivers, list) or len(drivers) == 0:
                self.log_result("Trust Widget No Confidence", False, 
                              "Drivers should be non-empty list", drivers)
                return False
            
            # Verify only drivers and time_window fields (no confidence)
            allowed_fields = {"drivers", "time_window"}
            actual_fields = set(trust_widget.keys())
            extra_fields = actual_fields - allowed_fields
            
            if extra_fields:
                self.log_result("Trust Widget No Confidence", False, 
                              f"Extra fields found (should only have drivers, time_window): {extra_fields}", trust_widget)
                return False
            
            self.log_result("Trust Widget No Confidence", True, 
                          f"✅ NO confidence field found, has {len(drivers)} drivers, only allowed fields present")
            return True
            
        except Exception as e:
            self.log_result("Trust Widget No Confidence", False, f"Exception: {str(e)}")
            return False

    def test_chat_quality_signal_diversity(self):
        """Test SIGNAL DIVERSITY: Check signals are selected with different planets via debug endpoint"""
        try:
            # Step 1: Create test user and profile
            register_payload = {
                "identifier": "diversity-test@example.com"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Signal Diversity - User Registration", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            auth_data = response.json()
            token = auth_data.get("token")
            
            # Create profile with birth details
            profile_payload = {
                "name": "Diversity Test",
                "dob": "1990-05-15",
                "tob": "14:30",
                "location": "Mumbai",
                "birth_place_lat": 19.08,
                "birth_place_lon": 72.88,
                "birth_place_tz": 5.5
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.post(f"{BACKEND_URL}/profile/", 
                                       json=profile_payload, 
                                       headers=headers, 
                                       timeout=10)
            
            if response.status_code != 200:
                self.log_result("Signal Diversity - Profile Creation", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Step 2: Ask two different questions
            session_id = f"diversity-test-{uuid.uuid4().hex[:8]}"
            
            # First question: career
            career_payload = {
                "sessionId": session_id,
                "message": "Tell me about my career",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", 
                                       json=career_payload, 
                                       headers=headers,
                                       timeout=30)
            
            if response.status_code != 200:
                self.log_result("Signal Diversity - Career Question", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Second question: health
            health_payload = {
                "sessionId": session_id,
                "message": "What about my health?",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", 
                                       json=health_payload, 
                                       headers=headers,
                                       timeout=30)
            
            if response.status_code != 200:
                self.log_result("Signal Diversity - Health Question", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Step 3: Check debug endpoint for signal diversity
            response = self.session.get(f"{BACKEND_URL}/debug/candidate-signals/latest", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Signal Diversity", False, 
                              f"Debug endpoint HTTP {response.status_code}", response.text)
                return False
            
            debug_data = response.json()
            
            # Check if data structure has nested data field
            if "data" in debug_data and "candidates" in debug_data["data"]:
                candidates = debug_data["data"]["candidates"]
            elif "candidates" in debug_data:
                candidates = debug_data["candidates"]
            else:
                self.log_result("Signal Diversity", False, 
                              "Missing candidates array", debug_data)
                return False
            
            if not isinstance(candidates, list):
                self.log_result("Signal Diversity", False, 
                              "Candidates should be a list", candidates)
                return False
            
            # Check for planet diversity in kept signals
            kept_signals = [c for c in candidates if c.get("kept", False)]
            if len(kept_signals) == 0:
                self.log_result("Signal Diversity", False, 
                              "No kept signals found", candidates)
                return False
            
            # Extract planets from kept signals
            planets = [signal.get("planet", "Unknown") for signal in kept_signals]
            unique_planets = set(planets)
            
            # Verify diversity (should not all be same planet)
            if len(unique_planets) <= 1:
                self.log_result("Signal Diversity", False, 
                              f"All signals from same planet: {planets}", kept_signals)
                return False
            
            # Check for "selected_for_diversity" in kept_reason
            diversity_reasons = [signal.get("kept_reason", "") for signal in kept_signals]
            has_diversity_selection = any("selected_for_diversity" in reason for reason in diversity_reasons)
            
            # Check that we don't have old score-based selection
            has_score_selection = any("score >= 0.45" in reason for reason in diversity_reasons)
            
            if has_score_selection:
                self.log_result("Signal Diversity", False, 
                              "Found old score-based selection (should use diversity)", diversity_reasons)
                return False
            
            self.log_result("Signal Diversity", True, 
                          f"✅ Planet diversity confirmed: {len(unique_planets)} unique planets ({unique_planets}), diversity selection: {has_diversity_selection}")
            return True
            
        except Exception as e:
            self.log_result("Signal Diversity", False, f"Exception: {str(e)}")
            return False

    def test_chat_quality_explicit_intent_override(self):
        """Test EXPLICIT INTENT OVERRIDE: Short reply with explicit topic intent should not return clarifying question"""
        try:
            # Step 1: Create test user and profile
            register_payload = {
                "identifier": "intent-override-test@example.com"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Intent Override - User Registration", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            auth_data = response.json()
            token = auth_data.get("token")
            
            # Create profile with birth details
            profile_payload = {
                "name": "Intent Override Test",
                "dob": "1990-05-15",
                "tob": "14:30",
                "location": "Mumbai",
                "birth_place_lat": 19.08,
                "birth_place_lon": 72.88,
                "birth_place_tz": 5.5
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.post(f"{BACKEND_URL}/profile/", 
                                       json=profile_payload, 
                                       headers=headers, 
                                       timeout=10)
            
            if response.status_code != 200:
                self.log_result("Intent Override - Profile Creation", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Step 2: Send short message with explicit topic intent
            session_id = f"intent-override-{uuid.uuid4().hex[:8]}"
            short_payload = {
                "sessionId": session_id,
                "message": "career",  # Short reply that ALSO has explicit topic intent
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", 
                                       json=short_payload, 
                                       headers=headers,
                                       timeout=30)
            
            if response.status_code != 200:
                self.log_result("Explicit Intent Override", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Step 3: Verify it does NOT return a clarifying question but processes as career topic
            reply = data.get("reply", {})
            raw_text = reply.get("rawText", "")
            
            # Check for clarifying question indicators
            clarifying_indicators = [
                "could you tell me more",
                "what specifically",
                "can you be more specific",
                "what would you like to know",
                "please provide more details"
            ]
            
            found_clarifying = []
            for indicator in clarifying_indicators:
                if indicator.lower() in raw_text.lower():
                    found_clarifying.append(indicator)
            
            if found_clarifying:
                self.log_result("Explicit Intent Override", False, 
                              f"Found clarifying question when explicit intent should override: {found_clarifying}", raw_text[:200])
                return False
            
            # Verify it processed as career topic
            focus = data.get("focus")
            if focus != "career":
                self.log_result("Explicit Intent Override", False, 
                              f"Expected focus 'career', got '{focus}' - explicit intent not recognized", data)
                return False
            
            # Verify it has substantial content (not just a clarifying question)
            if len(raw_text) < 50:
                self.log_result("Explicit Intent Override", False, 
                              f"Response too short, likely clarifying question: '{raw_text}'", reply)
                return False
            
            self.log_result("Explicit Intent Override", True, 
                          f"✅ Explicit intent override working: 'career' processed as career topic, no clarifying question")
            return True
            
        except Exception as e:
            self.log_result("Explicit Intent Override", False, f"Exception: {str(e)}")
            return False

    def run_quality_tests(self):
        """Run Chat Quality Enhancement tests"""
        print("🎯 CHAT QUALITY ENHANCEMENT TESTING")
        print("=" * 60)
        
        tests = [
            ("Trust Widget No Confidence", self.test_chat_quality_trust_widget_no_confidence),
            ("Signal Diversity", self.test_chat_quality_signal_diversity),
            ("Explicit Intent Override", self.test_chat_quality_explicit_intent_override),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n--- Testing {test_name} ---")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ EXCEPTION in {test_name}: {str(e)}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 CHAT QUALITY TEST SUMMARY: {passed} passed, {failed} failed")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['message']}")
        
        return passed, failed

if __name__ == "__main__":
    tester = ChatQualityTester()
    tester.run_quality_tests()