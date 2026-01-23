#!/usr/bin/env python3
"""
Comprehensive test for Chat UX upgrades as per review request
"""

import requests
import json
import uuid
import re

BACKEND_URL = "https://niro-home-update.preview.emergentagent.com/api"

class ChatUXTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        
    def log_result(self, test_name, success, message):
        result = {
            "test": test_name,
            "success": success,
            "message": message
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_conversation_state_and_short_reply(self):
        """Test conversation state and short-reply detection"""
        try:
            # Step 1: Create user and profile
            register_payload = {"identifier": "ux-test@example.com"}
            response = self.session.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Conversation State Test", False, f"User registration failed: {response.status_code}")
                return False
            
            auth_data = response.json()
            token = auth_data.get("token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create profile
            profile_payload = {
                "name": "UX Test User",
                "dob": "1990-05-15",
                "tob": "14:30",
                "location": "Mumbai",
                "birth_place_lat": 19.08,
                "birth_place_lon": 72.88,
                "birth_place_tz": 5.5
            }
            
            response = self.session.post(f"{BACKEND_URL}/profile/", json=profile_payload, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_result("Conversation State Test", False, f"Profile creation failed: {response.status_code}")
                return False
            
            # Step 2: Send career message
            session_id = f"ux-test-{uuid.uuid4().hex[:8]}"
            career_payload = {
                "sessionId": session_id,
                "message": "tell me about career",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=career_payload, headers=headers, timeout=30)
            if response.status_code != 200:
                self.log_result("Conversation State Test", False, f"Career message failed: {response.status_code}")
                return False
            
            career_data = response.json()
            
            # Verify conversationState
            if "conversationState" not in career_data:
                self.log_result("Conversation State Test", False, "Missing conversationState")
                return False
            
            conv_state = career_data["conversationState"]
            if "current_topic" not in conv_state or "message_count" not in conv_state:
                self.log_result("Conversation State Test", False, f"Missing state fields: {conv_state}")
                return False
            
            # Step 3: Send short reply
            short_reply_payload = {
                "sessionId": session_id,
                "message": "yes",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=short_reply_payload, headers=headers, timeout=30)
            if response.status_code != 200:
                self.log_result("Conversation State Test", False, f"Short reply failed: {response.status_code}")
                return False
            
            short_reply_data = response.json()
            reply_text = short_reply_data.get("reply", {}).get("rawText", "")
            
            # Verify context resolution
            if len(reply_text) < 50:
                self.log_result("Conversation State Test", False, f"Short reply not resolved: '{reply_text}'")
                return False
            
            # Verify state update
            new_conv_state = short_reply_data.get("conversationState", {})
            if new_conv_state.get("message_count", 0) <= conv_state.get("message_count", 0):
                self.log_result("Conversation State Test", False, "Message count not incremented")
                return False
            
            self.log_result("Conversation State Test", True, f"Short reply resolved, count: {new_conv_state.get('message_count')}")
            return True
            
        except Exception as e:
            self.log_result("Conversation State Test", False, f"Exception: {str(e)}")
            return False
    
    def test_trust_widget_response(self):
        """Test Trust Widget response"""
        try:
            # Create authenticated session
            register_payload = {"identifier": "trust-test@example.com"}
            response = self.session.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Trust Widget Test", False, f"User registration failed: {response.status_code}")
                return False
            
            auth_data = response.json()
            token = auth_data.get("token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create profile
            profile_payload = {
                "name": "Trust Test User",
                "dob": "1990-05-15",
                "tob": "14:30",
                "location": "Mumbai",
                "birth_place_lat": 19.08,
                "birth_place_lon": 72.88,
                "birth_place_tz": 5.5
            }
            
            response = self.session.post(f"{BACKEND_URL}/profile/", json=profile_payload, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_result("Trust Widget Test", False, f"Profile creation failed: {response.status_code}")
                return False
            
            # Send career question
            session_id = f"trust-test-{uuid.uuid4().hex[:8]}"
            payload = {
                "sessionId": session_id,
                "message": "Should I change my career path?",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                self.log_result("Trust Widget Test", False, f"Chat request failed: {response.status_code}")
                return False
            
            data = response.json()
            
            # Verify trustWidget
            if "trustWidget" not in data:
                self.log_result("Trust Widget Test", False, "Missing trustWidget")
                return False
            
            trust_widget = data["trustWidget"]
            
            # Verify drivers array (human-readable, no S1/S2 labels)
            if "drivers" not in trust_widget:
                self.log_result("Trust Widget Test", False, "Missing drivers array")
                return False
            
            drivers = trust_widget["drivers"]
            if not isinstance(drivers, list):
                self.log_result("Trust Widget Test", False, "drivers is not an array")
                return False
            
            # Check for human-readable labels (no signal IDs)
            for i, driver in enumerate(drivers):
                if not isinstance(driver, dict) or "label" not in driver:
                    self.log_result("Trust Widget Test", False, f"Driver {i} missing label")
                    return False
                
                label = driver["label"]
                if re.search(r'\[S\d+\]', label):
                    self.log_result("Trust Widget Test", False, f"Driver contains signal ID: {label}")
                    return False
            
            # Verify confidence level
            if "confidence" not in trust_widget:
                self.log_result("Trust Widget Test", False, "Missing confidence level")
                return False
            
            confidence = trust_widget["confidence"]
            if confidence not in ["Low", "Medium", "High"]:
                self.log_result("Trust Widget Test", False, f"Invalid confidence: {confidence}")
                return False
            
            # Check time_window (optional)
            time_window = trust_widget.get("time_window")
            
            self.log_result("Trust Widget Test", True, 
                          f"Valid: {len(drivers)} drivers, confidence={confidence}, time_window={time_window}")
            return True
            
        except Exception as e:
            self.log_result("Trust Widget Test", False, f"Exception: {str(e)}")
            return False
    
    def test_next_step_chips(self):
        """Test Next Step Chips"""
        try:
            # Simple chat request
            session_id = f"chips-test-{uuid.uuid4().hex[:8]}"
            payload = {
                "sessionId": session_id,
                "message": "What should I focus on in my career?"
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            if response.status_code != 200:
                self.log_result("Next Step Chips Test", False, f"Chat request failed: {response.status_code}")
                return False
            
            data = response.json()
            
            # Verify nextStepChips
            if "nextStepChips" not in data:
                self.log_result("Next Step Chips Test", False, "Missing nextStepChips")
                return False
            
            chips = data["nextStepChips"]
            if not isinstance(chips, list):
                self.log_result("Next Step Chips Test", False, "nextStepChips is not an array")
                return False
            
            # Verify each chip has id and label
            for i, chip in enumerate(chips):
                if not isinstance(chip, dict):
                    self.log_result("Next Step Chips Test", False, f"Chip {i} is not an object")
                    return False
                
                if "id" not in chip or "label" not in chip:
                    self.log_result("Next Step Chips Test", False, f"Chip {i} missing id or label")
                    return False
                
                if not chip["id"] or not chip["label"]:
                    self.log_result("Next Step Chips Test", False, f"Chip {i} has empty id or label")
                    return False
            
            self.log_result("Next Step Chips Test", True, f"Found {len(chips)} valid chips")
            return True
            
        except Exception as e:
            self.log_result("Next Step Chips Test", False, f"Exception: {str(e)}")
            return False
    
    def test_feedback_endpoint(self):
        """Test Feedback Endpoint"""
        try:
            # Test positive feedback
            feedback_payload = {
                "response_id": "test-123",
                "session_id": "test-session",
                "feedback": "positive"
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat/feedback", json=feedback_payload, timeout=10)
            if response.status_code != 200:
                self.log_result("Feedback Endpoint Test", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            if not data.get("success"):
                self.log_result("Feedback Endpoint Test", False, f"Feedback failed: {data}")
                return False
            
            # Test negative feedback
            negative_payload = {
                "response_id": "test-456",
                "session_id": "test-session",
                "feedback": "negative"
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat/feedback", json=negative_payload, timeout=10)
            if response.status_code != 200:
                self.log_result("Feedback Endpoint Test", False, f"Negative feedback HTTP {response.status_code}")
                return False
            
            negative_data = response.json()
            if not negative_data.get("success"):
                self.log_result("Feedback Endpoint Test", False, f"Negative feedback failed: {negative_data}")
                return False
            
            self.log_result("Feedback Endpoint Test", True, "Both positive and negative feedback working")
            return True
            
        except Exception as e:
            self.log_result("Feedback Endpoint Test", False, f"Exception: {str(e)}")
            return False
    
    def test_conversation_state_in_response(self):
        """Test conversationState in response"""
        try:
            # Create authenticated session
            register_payload = {"identifier": "conv-state-test@example.com"}
            response = self.session.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Conversation State Response Test", False, f"User registration failed: {response.status_code}")
                return False
            
            auth_data = response.json()
            token = auth_data.get("token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create profile
            profile_payload = {
                "name": "Conv State User",
                "dob": "1990-05-15",
                "tob": "14:30",
                "location": "Mumbai",
                "birth_place_lat": 19.08,
                "birth_place_lon": 72.88,
                "birth_place_tz": 5.5
            }
            
            response = self.session.post(f"{BACKEND_URL}/profile/", json=profile_payload, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_result("Conversation State Response Test", False, f"Profile creation failed: {response.status_code}")
                return False
            
            # Send message with question
            session_id = f"conv-state-test-{uuid.uuid4().hex[:8]}"
            payload = {
                "sessionId": session_id,
                "message": "What are my career prospects? Should I change jobs?",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                self.log_result("Conversation State Response Test", False, f"Chat request failed: {response.status_code}")
                return False
            
            data = response.json()
            
            # Verify conversationState
            if "conversationState" not in data:
                self.log_result("Conversation State Response Test", False, "Missing conversationState")
                return False
            
            conv_state = data["conversationState"]
            
            # Verify required fields
            required_fields = ["current_topic", "message_count"]
            missing_fields = [field for field in required_fields if field not in conv_state]
            
            if missing_fields:
                self.log_result("Conversation State Response Test", False, f"Missing fields: {missing_fields}")
                return False
            
            # Verify current_topic is set
            current_topic = conv_state.get("current_topic")
            if not current_topic:
                self.log_result("Conversation State Response Test", False, "current_topic is empty")
                return False
            
            # Verify message_count
            message_count = conv_state.get("message_count")
            if not isinstance(message_count, int) or message_count <= 0:
                self.log_result("Conversation State Response Test", False, f"Invalid message_count: {message_count}")
                return False
            
            # Check for last_ai_question if there was a question
            reply_text = data.get("reply", {}).get("rawText", "")
            if "?" in reply_text:
                last_ai_question = conv_state.get("last_ai_question")
                if not last_ai_question:
                    self.log_result("Conversation State Response Test", False, "Missing last_ai_question despite question in response")
                    return False
            
            self.log_result("Conversation State Response Test", True, 
                          f"Valid: topic={current_topic}, count={message_count}")
            return True
            
        except Exception as e:
            self.log_result("Conversation State Response Test", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all UX upgrade tests"""
        print("=" * 80)
        print("🎨 TESTING NEW CHAT UX UPGRADES")
        print("=" * 80)
        
        tests = [
            ("Conversation State & Short Reply Detection", self.test_conversation_state_and_short_reply),
            ("Trust Widget Response", self.test_trust_widget_response),
            ("Next Step Chips", self.test_next_step_chips),
            ("Feedback Endpoint", self.test_feedback_endpoint),
            ("Conversation State in Response", self.test_conversation_state_in_response),
        ]
        
        for test_name, test_func in tests:
            print(f"\n--- Testing {test_name} ---")
            test_func()
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.results if result["success"])
        failed = len(self.results) - passed
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📈 SUCCESS RATE: {passed}/{len(self.results)} ({passed/len(self.results)*100:.1f}%)")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        print("\n" + "=" * 80)
        return passed, failed

if __name__ == "__main__":
    tester = ChatUXTester()
    passed, failed = tester.run_all_tests()
    
    if failed == 0:
        print("🎉 ALL CHAT UX UPGRADES WORKING PERFECTLY!")
    else:
        print(f"⚠️ {failed} tests need attention")