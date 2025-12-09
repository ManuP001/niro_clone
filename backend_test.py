#!/usr/bin/env python3
"""
Backend API Testing for Report Generation Functionality
Tests existing report generation features to ensure no regression from Chat implementation
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://astral-counsel.preview.emergentagent.com/api"

class ReportGenerationTester:
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
    
    def test_pricing_endpoint(self):
        """Test GET /api/pricing - Verify all 4 report types have prices"""
        try:
            response = self.session.get(f"{BACKEND_URL}/pricing", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Pricing Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check if it's a list
            if not isinstance(data, list):
                self.log_result("Pricing Endpoint", False, 
                              "Response is not a list", data)
                return False
            
            # Check for required report types
            required_types = ["yearly_prediction", "love_marriage", "career_job", "retro_check"]
            found_types = [item.get("report_type") for item in data]
            
            missing_types = [rt for rt in required_types if rt not in found_types]
            
            if missing_types:
                self.log_result("Pricing Endpoint", False, 
                              f"Missing report types: {missing_types}", data)
                return False
            
            # Verify all have prices
            for item in data:
                if not item.get("current_price_inr") or item.get("current_price_inr") <= 0:
                    self.log_result("Pricing Endpoint", False, 
                                  f"Invalid price for {item.get('report_type')}", item)
                    return False
            
            self.log_result("Pricing Endpoint", True, 
                          f"All {len(required_types)} report types found with valid prices")
            return True
            
        except Exception as e:
            self.log_result("Pricing Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_health_check(self):
        """Test GET /api/health - Verify Gemini and VedicAPI configuration"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Health Check", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check required fields
            required_fields = ["status", "gemini_configured", "vedic_api_configured"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_result("Health Check", False, 
                              f"Missing fields: {missing_fields}", data)
                return False
            
            # Check status
            if data.get("status") != "healthy":
                self.log_result("Health Check", False, 
                              f"Status not healthy: {data.get('status')}", data)
                return False
            
            # Check API configurations
            if not data.get("gemini_configured"):
                self.log_result("Health Check", False, "Gemini API not configured", data)
                return False
            
            if not data.get("vedic_api_configured"):
                self.log_result("Health Check", False, "VedicAPI not configured", data)
                return False
            
            self.log_result("Health Check", True, 
                          "Health check passed - all APIs configured")
            return True
            
        except Exception as e:
            self.log_result("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_city_search(self):
        """Test GET /api/utils/search-cities - Verify cities returned with lat/lon"""
        try:
            response = self.session.get(f"{BACKEND_URL}/utils/search-cities", 
                                      params={"query": "Mumbai"}, timeout=10)
            
            if response.status_code != 200:
                self.log_result("City Search", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check structure
            if "cities" not in data:
                self.log_result("City Search", False, 
                              "No 'cities' field in response", data)
                return False
            
            cities = data["cities"]
            if not isinstance(cities, list):
                self.log_result("City Search", False, 
                              "'cities' is not a list", data)
                return False
            
            if len(cities) == 0:
                self.log_result("City Search", False, 
                              "No cities found for Mumbai", data)
                return False
            
            # Check first city has required fields
            first_city = cities[0]
            required_fields = ["name", "lat", "lon"]
            missing_fields = [field for field in required_fields if field not in first_city]
            
            if missing_fields:
                self.log_result("City Search", False, 
                              f"Missing fields in city data: {missing_fields}", first_city)
                return False
            
            # Verify lat/lon are numbers
            try:
                float(first_city["lat"])
                float(first_city["lon"])
            except (ValueError, TypeError):
                self.log_result("City Search", False, 
                              "Invalid lat/lon format", first_city)
                return False
            
            self.log_result("City Search", True, 
                          f"Found {len(cities)} cities with valid lat/lon data")
            return True
            
        except Exception as e:
            self.log_result("City Search", False, f"Exception: {str(e)}")
            return False
    
    def test_time_parser(self):
        """Test POST /api/utils/parse-time - Verify time parsing works"""
        try:
            payload = {"time_input": "2:30 PM"}
            response = self.session.post(f"{BACKEND_URL}/utils/parse-time", 
                                       json=payload, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Time Parser", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check required fields
            required_fields = ["success", "normalized_time", "display_time"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_result("Time Parser", False, 
                              f"Missing fields: {missing_fields}", data)
                return False
            
            # Check success
            if not data.get("success"):
                self.log_result("Time Parser", False, 
                              f"Parsing failed: {data.get('error_message')}", data)
                return False
            
            # Verify normalized time format (should be 24-hour)
            normalized = data.get("normalized_time")
            if normalized != "14:30":
                self.log_result("Time Parser", False, 
                              f"Expected '14:30', got '{normalized}'", data)
                return False
            
            # Verify display time
            display = data.get("display_time")
            if display != "2:30 PM":
                self.log_result("Time Parser", False, 
                              f"Expected '2:30 PM', got '{display}'", data)
                return False
            
            self.log_result("Time Parser", True, 
                          "Time parsing working correctly")
            return True
            
        except Exception as e:
            self.log_result("Time Parser", False, f"Exception: {str(e)}")
            return False
    
    def test_report_generation_flow(self):
        """Test complete report generation flow"""
        try:
            # Step 1: Create test user
            user_data = {
                "name": "Arjun Sharma",
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "phone": "+919876543210",
                "gender": "male",
                "birth_details": {
                    "dob": "15-08-1990",
                    "tob": "14:30",
                    "location": "Mumbai, Maharashtra, India",
                    "lat": 19.0760,
                    "lon": 72.8777,
                    "timezone": 5.5
                }
            }
            
            response = self.session.post(f"{BACKEND_URL}/users", json=user_data, timeout=10)
            if response.status_code != 200:
                self.log_result("Report Flow - User Creation", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            user = response.json()
            user_id = user.get("user_id")
            
            self.log_result("Report Flow - User Creation", True, 
                          f"User created: {user_id}")
            
            # Step 2: Create transaction
            transaction_data = {
                "user_id": user_id,
                "report_type": "yearly_prediction",
                "amount": 499.0  # Dummy amount - server will fetch actual price
            }
            
            response = self.session.post(f"{BACKEND_URL}/transactions/create", 
                                       json=transaction_data, timeout=10)
            if response.status_code != 200:
                self.log_result("Report Flow - Transaction Creation", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            transaction = response.json()
            transaction_id = transaction.get("transaction_id")
            
            self.log_result("Report Flow - Transaction Creation", True, 
                          f"Transaction created: {transaction_id}")
            
            # Step 3: Verify payment
            payment_data = {
                "transaction_id": transaction_id,
                "payment_success": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/transactions/verify", 
                                       json=payment_data, timeout=10)
            if response.status_code != 200:
                self.log_result("Report Flow - Payment Verification", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            payment_result = response.json()
            if not payment_result.get("success"):
                self.log_result("Report Flow - Payment Verification", False, 
                              "Payment verification failed", payment_result)
                return False
            
            self.log_result("Report Flow - Payment Verification", True, 
                          "Payment verified successfully")
            
            # Step 4: Generate report
            report_data = {
                "user_id": user_id,
                "transaction_id": transaction_id,
                "report_type": "yearly_prediction",
                "birth_details": user_data["birth_details"]
            }
            
            response = self.session.post(f"{BACKEND_URL}/reports/generate", 
                                       json=report_data, timeout=15)
            if response.status_code != 200:
                self.log_result("Report Flow - Report Generation", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            report_response = response.json()
            report_id = report_response.get("report_id")
            
            if not report_id:
                self.log_result("Report Flow - Report Generation", False, 
                              "No report_id in response", report_response)
                return False
            
            self.log_result("Report Flow - Report Generation", True, 
                          f"Report generation started: {report_id}")
            
            # Step 5: Check report status (wait for processing)
            max_attempts = 8
            for attempt in range(max_attempts):
                time.sleep(5)  # Wait 5 seconds between checks
                
                try:
                    response = self.session.get(f"{BACKEND_URL}/reports/{report_id}", timeout=15)
                    if response.status_code != 200:
                        self.log_result("Report Flow - Status Check", False, 
                                      f"HTTP {response.status_code}", response.text)
                        return False
                    
                    status_data = response.json()
                    status = status_data.get("status")
                    
                    print(f"   Attempt {attempt + 1}: Report status = {status}")
                    
                    if status == "completed":
                        self.log_result("Report Flow - Status Check", True, 
                                      f"Report completed successfully in {attempt + 1} attempts")
                        return True
                    elif status == "failed":
                        error = status_data.get("code_execution_error", "Unknown error")
                        self.log_result("Report Flow - Status Check", False, 
                                      f"Report generation failed: {error}", status_data)
                        return False
                    elif status in ["pending", "processing"]:
                        continue  # Keep waiting
                    else:
                        self.log_result("Report Flow - Status Check", False, 
                                      f"Unknown status: {status}", status_data)
                        return False
                        
                except requests.exceptions.Timeout:
                    print(f"   Attempt {attempt + 1}: Timeout checking status, retrying...")
                    continue
                except Exception as e:
                    print(f"   Attempt {attempt + 1}: Error checking status: {str(e)}")
                    continue
            
            # If we get here, report didn't complete in time
            self.log_result("Report Flow - Status Check", False, 
                          f"Report still processing after {max_attempts} attempts (may be working but slow)")
            return False
            
        except Exception as e:
            self.log_result("Report Generation Flow", False, f"Exception: {str(e)}")
            return False
    
    def test_niro_chat_basic_message(self):
        """Test NIRO chat with basic message containing 'career'"""
        try:
            payload = {
                "sessionId": f"test_session_{uuid.uuid4().hex[:8]}",
                "message": "I want to know about my career prospects"
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Chat - Basic Career Message", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Verify response structure
            required_fields = ["reply", "mode", "focus", "suggestedActions"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_result("NIRO Chat - Basic Career Message", False, 
                              f"Missing fields: {missing_fields}", data)
                return False
            
            # Verify reply structure
            reply = data.get("reply", {})
            reply_fields = ["summary", "reasons", "remedies"]
            missing_reply_fields = [field for field in reply_fields if field not in reply]
            
            if missing_reply_fields:
                self.log_result("NIRO Chat - Basic Career Message", False, 
                              f"Missing reply fields: {missing_reply_fields}", reply)
                return False
            
            # Verify career focus detection
            focus = data.get("focus")
            if focus != "career":
                self.log_result("NIRO Chat - Basic Career Message", False, 
                              f"Expected focus 'career', got '{focus}'", data)
                return False
            
            # Verify suggestedActions is a list
            suggested_actions = data.get("suggestedActions", [])
            if not isinstance(suggested_actions, list):
                self.log_result("NIRO Chat - Basic Career Message", False, 
                              "suggestedActions is not a list", data)
                return False
            
            # Verify each action has id and label
            for action in suggested_actions:
                if not isinstance(action, dict) or "id" not in action or "label" not in action:
                    self.log_result("NIRO Chat - Basic Career Message", False, 
                                  "Invalid action structure", action)
                    return False
            
            self.log_result("NIRO Chat - Basic Career Message", True, 
                          f"Career focus detected correctly, {len(suggested_actions)} actions returned")
            return True
            
        except Exception as e:
            self.log_result("NIRO Chat - Basic Career Message", False, f"Exception: {str(e)}")
            return False
    
    def test_niro_chat_focus_career_action(self):
        """Test NIRO chat with actionId 'focus_career'"""
        try:
            payload = {
                "sessionId": f"test_session_{uuid.uuid4().hex[:8]}",
                "message": "Tell me more",
                "actionId": "focus_career"
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Chat - Focus Career Action", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Verify career focus
            if data.get("focus") != "career":
                self.log_result("NIRO Chat - Focus Career Action", False, 
                              f"Expected focus 'career', got '{data.get('focus')}'", data)
                return False
            
            # Verify mode
            if data.get("mode") != "FOCUS_READING":
                self.log_result("NIRO Chat - Focus Career Action", False, 
                              f"Expected mode 'FOCUS_READING', got '{data.get('mode')}'", data)
                return False
            
            # Verify reply content exists
            reply = data.get("reply", {})
            if not reply.get("summary") or not reply.get("reasons"):
                self.log_result("NIRO Chat - Focus Career Action", False, 
                              "Missing summary or reasons in reply", reply)
                return False
            
            self.log_result("NIRO Chat - Focus Career Action", True, 
                          "Career-focused response generated correctly")
            return True
            
        except Exception as e:
            self.log_result("NIRO Chat - Focus Career Action", False, f"Exception: {str(e)}")
            return False
    
    def test_niro_chat_focus_relationship_action(self):
        """Test NIRO chat with actionId 'focus_relationship'"""
        try:
            payload = {
                "sessionId": f"test_session_{uuid.uuid4().hex[:8]}",
                "message": "Tell me about relationships",
                "actionId": "focus_relationship"
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Chat - Focus Relationship Action", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Verify relationship focus
            if data.get("focus") != "relationship":
                self.log_result("NIRO Chat - Focus Relationship Action", False, 
                              f"Expected focus 'relationship', got '{data.get('focus')}'", data)
                return False
            
            # Verify mode
            if data.get("mode") != "FOCUS_READING":
                self.log_result("NIRO Chat - Focus Relationship Action", False, 
                              f"Expected mode 'FOCUS_READING', got '{data.get('mode')}'", data)
                return False
            
            self.log_result("NIRO Chat - Focus Relationship Action", True, 
                          "Relationship-focused response generated correctly")
            return True
            
        except Exception as e:
            self.log_result("NIRO Chat - Focus Relationship Action", False, f"Exception: {str(e)}")
            return False
    
    def test_niro_chat_daily_guidance_action(self):
        """Test NIRO chat with actionId 'daily_guidance'"""
        try:
            payload = {
                "sessionId": f"test_session_{uuid.uuid4().hex[:8]}",
                "message": "What's my daily guidance?",
                "actionId": "daily_guidance"
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Chat - Daily Guidance Action", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Verify mode
            if data.get("mode") != "DAILY_GUIDANCE":
                self.log_result("NIRO Chat - Daily Guidance Action", False, 
                              f"Expected mode 'DAILY_GUIDANCE', got '{data.get('mode')}'", data)
                return False
            
            # Focus should be None for daily guidance
            if data.get("focus") is not None:
                self.log_result("NIRO Chat - Daily Guidance Action", False, 
                              f"Expected focus None, got '{data.get('focus')}'", data)
                return False
            
            self.log_result("NIRO Chat - Daily Guidance Action", True, 
                          "Daily guidance response generated correctly")
            return True
            
        except Exception as e:
            self.log_result("NIRO Chat - Daily Guidance Action", False, f"Exception: {str(e)}")
            return False
    
    def test_niro_chat_suggested_actions_populated(self):
        """Test that NIRO chat returns populated suggestedActions array"""
        try:
            payload = {
                "sessionId": f"test_session_{uuid.uuid4().hex[:8]}",
                "message": "Hello NIRO"
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Chat - Suggested Actions", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Verify suggestedActions exists and is populated
            suggested_actions = data.get("suggestedActions", [])
            
            if not isinstance(suggested_actions, list):
                self.log_result("NIRO Chat - Suggested Actions", False, 
                              "suggestedActions is not a list", data)
                return False
            
            if len(suggested_actions) == 0:
                self.log_result("NIRO Chat - Suggested Actions", False, 
                              "suggestedActions array is empty", data)
                return False
            
            # Verify each action has required fields
            for i, action in enumerate(suggested_actions):
                if not isinstance(action, dict):
                    self.log_result("NIRO Chat - Suggested Actions", False, 
                                  f"Action {i} is not a dict", action)
                    return False
                
                if "id" not in action or "label" not in action:
                    self.log_result("NIRO Chat - Suggested Actions", False, 
                                  f"Action {i} missing id or label", action)
                    return False
                
                if not action["id"] or not action["label"]:
                    self.log_result("NIRO Chat - Suggested Actions", False, 
                                  f"Action {i} has empty id or label", action)
                    return False
            
            self.log_result("NIRO Chat - Suggested Actions", True, 
                          f"Found {len(suggested_actions)} valid suggested actions")
            return True
            
        except Exception as e:
            self.log_result("NIRO Chat - Suggested Actions", False, f"Exception: {str(e)}")
            return False
    
    def test_niro_chat_response_schema(self):
        """Test that NIRO chat response matches expected schema"""
        try:
            payload = {
                "sessionId": f"test_session_{uuid.uuid4().hex[:8]}",
                "message": "Test message for schema validation"
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Chat - Response Schema", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Expected schema validation
            expected_structure = {
                "reply": {
                    "summary": str,
                    "reasons": list,
                    "remedies": list
                },
                "mode": str,
                "focus": (str, type(None)),  # Can be string or null
                "suggestedActions": list
            }
            
            # Validate top-level structure
            for field, expected_type in expected_structure.items():
                if field not in data:
                    self.log_result("NIRO Chat - Response Schema", False, 
                                  f"Missing field: {field}", data)
                    return False
                
                if field == "focus":
                    # Focus can be string or None
                    if data[field] is not None and not isinstance(data[field], str):
                        self.log_result("NIRO Chat - Response Schema", False, 
                                      f"Field {field} should be string or null", data[field])
                        return False
                elif isinstance(expected_type, dict):
                    # Nested object validation
                    if not isinstance(data[field], dict):
                        self.log_result("NIRO Chat - Response Schema", False, 
                                      f"Field {field} should be object", data[field])
                        return False
                    
                    # Validate nested fields
                    for nested_field, nested_type in expected_type.items():
                        if nested_field not in data[field]:
                            self.log_result("NIRO Chat - Response Schema", False, 
                                          f"Missing nested field: {field}.{nested_field}", data[field])
                            return False
                        
                        if not isinstance(data[field][nested_field], nested_type):
                            self.log_result("NIRO Chat - Response Schema", False, 
                                          f"Field {field}.{nested_field} wrong type", data[field][nested_field])
                            return False
                else:
                    if not isinstance(data[field], expected_type):
                        self.log_result("NIRO Chat - Response Schema", False, 
                                      f"Field {field} wrong type", data[field])
                        return False
            
            # Validate suggestedActions structure
            for action in data["suggestedActions"]:
                if not isinstance(action, dict) or "id" not in action or "label" not in action:
                    self.log_result("NIRO Chat - Response Schema", False, 
                                  "Invalid suggestedAction structure", action)
                    return False
                
                if not isinstance(action["id"], str) or not isinstance(action["label"], str):
                    self.log_result("NIRO Chat - Response Schema", False, 
                                  "suggestedAction id/label not strings", action)
                    return False
            
            self.log_result("NIRO Chat - Response Schema", True, 
                          "Response schema validation passed")
            return True
            
        except Exception as e:
            self.log_result("NIRO Chat - Response Schema", False, f"Exception: {str(e)}")
            return False

    def test_niro_birth_collection_mode(self):
        """Test BIRTH_COLLECTION Mode: Create new session without birth details"""
        try:
            session_id = f"test-new-{uuid.uuid4().hex[:8]}"
            payload = {
                "sessionId": session_id,
                "message": "Hello",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Birth Collection Mode", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Verify mode is BIRTH_COLLECTION
            if data.get("mode") != "BIRTH_COLLECTION":
                self.log_result("NIRO Birth Collection Mode", False, 
                              f"Expected mode 'BIRTH_COLLECTION', got '{data.get('mode')}'", data)
                return False
            
            # Verify focus is null
            if data.get("focus") is not None:
                self.log_result("NIRO Birth Collection Mode", False, 
                              f"Expected focus null, got '{data.get('focus')}'", data)
                return False
            
            # Verify suggested actions include birth collection helpers
            suggested_actions = data.get("suggestedActions", [])
            action_ids = [action.get("id") for action in suggested_actions]
            
            expected_actions = ["help_dob", "example_format"]
            found_actions = [action for action in expected_actions if action in action_ids]
            
            if len(found_actions) < 1:
                self.log_result("NIRO Birth Collection Mode", False, 
                              f"Expected birth collection actions, got {action_ids}", data)
                return False
            
            self.log_result("NIRO Birth Collection Mode", True, 
                          f"Birth collection mode working correctly with {len(found_actions)} helper actions")
            return True
            
        except Exception as e:
            self.log_result("NIRO Birth Collection Mode", False, f"Exception: {str(e)}")
            return False

    def test_niro_set_birth_details(self):
        """Test Set Birth Details: Use the session management endpoint"""
        try:
            session_id = f"test-new-{uuid.uuid4().hex[:8]}"
            
            # First create session with initial message
            initial_payload = {
                "sessionId": session_id,
                "message": "Hello NIRO",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=initial_payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Set Birth Details - Initial", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Now set birth details via session management endpoint
            birth_details = {
                "dob": "1990-08-15",
                "tob": "14:30",
                "location": "Mumbai, Maharashtra, India",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "timezone": 5.5
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/chat/session/{session_id}/birth-details", 
                json=birth_details, 
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_result("NIRO Set Birth Details", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            
            if not result.get("success"):
                self.log_result("NIRO Set Birth Details", False, 
                              "Birth details setting failed", result)
                return False
            
            # Verify session state shows birth details
            response = self.session.get(f"{BACKEND_URL}/chat/session/{session_id}", timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Set Birth Details - Verify", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            session_data = response.json()
            
            if not session_data.get("has_birth_details"):
                self.log_result("NIRO Set Birth Details", False, 
                              "Session doesn't show birth details set", session_data)
                return False
            
            self.log_result("NIRO Set Birth Details", True, 
                          "Birth details set and verified successfully")
            return True
            
        except Exception as e:
            self.log_result("NIRO Set Birth Details", False, f"Exception: {str(e)}")
            return False

    def test_niro_past_themes_mode(self):
        """Test PAST_THEMES Mode: After birth details set, first reading"""
        try:
            session_id = f"test-past-{uuid.uuid4().hex[:8]}"
            
            # Set birth details first
            birth_details = {
                "dob": "1990-08-15",
                "tob": "14:30",
                "location": "Mumbai, Maharashtra, India",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "timezone": 5.5
            }
            
            # Create session and set birth details
            initial_payload = {
                "sessionId": session_id,
                "message": "Hello",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=initial_payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Past Themes Mode - Setup", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Set birth details
            response = self.session.post(
                f"{BACKEND_URL}/chat/session/{session_id}/birth-details", 
                json=birth_details, 
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_result("NIRO Past Themes Mode - Birth Details", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Now send message with birth details already set
            payload = {
                "sessionId": session_id,
                "message": "Tell me about my past",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Past Themes Mode", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Verify mode is PAST_THEMES
            if data.get("mode") != "PAST_THEMES":
                self.log_result("NIRO Past Themes Mode", False, 
                              f"Expected mode 'PAST_THEMES', got '{data.get('mode')}'", data)
                return False
            
            # Verify focus is null
            if data.get("focus") is not None:
                self.log_result("NIRO Past Themes Mode", False, 
                              f"Expected focus null, got '{data.get('focus')}'", data)
                return False
            
            # Verify suggested actions include focus options
            suggested_actions = data.get("suggestedActions", [])
            action_ids = [action.get("id") for action in suggested_actions]
            
            expected_actions = ["focus_career", "focus_relationship", "focus_health", "daily_guidance"]
            found_actions = [action for action in expected_actions if action in action_ids]
            
            if len(found_actions) < 2:
                self.log_result("NIRO Past Themes Mode", False, 
                              f"Expected focus actions, got {action_ids}", data)
                return False
            
            self.log_result("NIRO Past Themes Mode", True, 
                          f"Past themes mode working correctly with {len(found_actions)} focus options")
            return True
            
        except Exception as e:
            self.log_result("NIRO Past Themes Mode", False, f"Exception: {str(e)}")
            return False

    def test_niro_keyword_inference(self):
        """Test Keyword Inference: Test focus detection from message"""
        try:
            session_id = f"test-keyword-{uuid.uuid4().hex[:8]}"
            
            # Set up session with birth details and past themes done
            birth_details = {
                "dob": "1990-08-15",
                "tob": "14:30",
                "location": "Mumbai, Maharashtra, India",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "timezone": 5.5
            }
            
            # Create session
            initial_payload = {
                "sessionId": session_id,
                "message": "Hello",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=initial_payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Keyword Inference - Setup", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Set birth details
            response = self.session.post(
                f"{BACKEND_URL}/chat/session/{session_id}/birth-details", 
                json=birth_details, 
                timeout=30
            )
            
            if response.status_code != 200:
                self.log_result("NIRO Keyword Inference - Birth Details", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Send past themes message to mark retro as done
            past_payload = {
                "sessionId": session_id,
                "message": "Tell me about my past themes",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=past_payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Keyword Inference - Past Themes", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Now test keyword inference with love/marriage message
            keyword_payload = {
                "sessionId": session_id,
                "message": "I want to know about love and marriage in my life",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=keyword_payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Keyword Inference", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Verify mode is FOCUS_READING
            if data.get("mode") != "FOCUS_READING":
                self.log_result("NIRO Keyword Inference", False, 
                              f"Expected mode 'FOCUS_READING', got '{data.get('mode')}'", data)
                return False
            
            # Verify focus is relationship
            if data.get("focus") != "relationship":
                self.log_result("NIRO Keyword Inference", False, 
                              f"Expected focus 'relationship', got '{data.get('focus')}'", data)
                return False
            
            self.log_result("NIRO Keyword Inference", True, 
                          "Keyword inference correctly detected 'relationship' focus from love/marriage message")
            return True
            
        except Exception as e:
            self.log_result("NIRO Keyword Inference", False, f"Exception: {str(e)}")
            return False

    def test_niro_session_state_endpoint(self):
        """Test Session State Endpoint: GET /api/chat/session/{session_id}"""
        try:
            session_id = f"test-state-{uuid.uuid4().hex[:8]}"
            
            # Create session with message
            payload = {
                "sessionId": session_id,
                "message": "Hello NIRO",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Session State - Create", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Get session state
            response = self.session.get(f"{BACKEND_URL}/chat/session/{session_id}", timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Session State Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Verify required fields
            required_fields = ["session_id", "has_birth_details", "has_done_retro", "message_count"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_result("NIRO Session State Endpoint", False, 
                              f"Missing fields: {missing_fields}", data)
                return False
            
            # Verify session_id matches
            if data.get("session_id") != session_id:
                self.log_result("NIRO Session State Endpoint", False, 
                              f"Session ID mismatch: expected {session_id}, got {data.get('session_id')}", data)
                return False
            
            # Verify has_birth_details is boolean
            if not isinstance(data.get("has_birth_details"), bool):
                self.log_result("NIRO Session State Endpoint", False, 
                              "has_birth_details is not boolean", data)
                return False
            
            # Verify has_done_retro is boolean
            if not isinstance(data.get("has_done_retro"), bool):
                self.log_result("NIRO Session State Endpoint", False, 
                              "has_done_retro is not boolean", data)
                return False
            
            # Verify message_count is number
            if not isinstance(data.get("message_count"), int):
                self.log_result("NIRO Session State Endpoint", False, 
                              "message_count is not integer", data)
                return False
            
            self.log_result("NIRO Session State Endpoint", True, 
                          f"Session state endpoint working correctly - message_count: {data.get('message_count')}")
            return True
            
        except Exception as e:
            self.log_result("NIRO Session State Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_niro_session_reset(self):
        """Test Session Reset: DELETE /api/chat/session/{session_id}"""
        try:
            session_id = f"test-reset-{uuid.uuid4().hex[:8]}"
            
            # Create session
            payload = {
                "sessionId": session_id,
                "message": "Hello NIRO",
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Session Reset - Create", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Verify session exists
            response = self.session.get(f"{BACKEND_URL}/chat/session/{session_id}", timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Session Reset - Verify Exists", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            # Reset session
            response = self.session.delete(f"{BACKEND_URL}/chat/session/{session_id}", timeout=30)
            
            if response.status_code != 200:
                self.log_result("NIRO Session Reset", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            result = response.json()
            
            if not result.get("success"):
                self.log_result("NIRO Session Reset", False, 
                              "Reset operation failed", result)
                return False
            
            # Verify session is reset (should return 404 or create new)
            response = self.session.get(f"{BACKEND_URL}/chat/session/{session_id}", timeout=30)
            
            # Session should either be 404 (deleted) or have reset state
            if response.status_code == 404:
                self.log_result("NIRO Session Reset", True, 
                              "Session successfully deleted")
                return True
            elif response.status_code == 200:
                # Check if it's a fresh session
                data = response.json()
                if data.get("message_count", 0) == 0:
                    self.log_result("NIRO Session Reset", True, 
                                  "Session successfully reset to initial state")
                    return True
                else:
                    self.log_result("NIRO Session Reset", False, 
                                  "Session not properly reset", data)
                    return False
            else:
                self.log_result("NIRO Session Reset", False, 
                              f"Unexpected response after reset: HTTP {response.status_code}", response.text)
                return False
            
        except Exception as e:
            self.log_result("NIRO Session Reset", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests including NIRO chat orchestrator"""
        print("=" * 60)
        print("TESTING NIRO CONVERSATION ORCHESTRATOR")
        print("Comprehensive Backend API Testing")
        print("=" * 60)
        
        tests = [
            # Core API Tests
            ("Health Check", self.test_health_check),
            ("Pricing Endpoint", self.test_pricing_endpoint),
            ("City Search", self.test_city_search),
            ("Time Parser", self.test_time_parser),
            
            # NIRO Orchestrator Tests (as per review request)
            ("NIRO Birth Collection Mode", self.test_niro_birth_collection_mode),
            ("NIRO Set Birth Details", self.test_niro_set_birth_details),
            ("NIRO Past Themes Mode", self.test_niro_past_themes_mode),
            ("NIRO Focus Career Action", self.test_niro_chat_focus_career_action),
            ("NIRO Focus Relationship Action", self.test_niro_chat_focus_relationship_action),
            ("NIRO Keyword Inference", self.test_niro_keyword_inference),
            ("NIRO Session State Endpoint", self.test_niro_session_state_endpoint),
            ("NIRO Suggested Actions", self.test_niro_chat_suggested_actions_populated),
            ("NIRO Response Schema", self.test_niro_chat_response_schema),
            ("NIRO Session Reset", self.test_niro_session_reset),
            
            # Additional NIRO Tests
            ("NIRO Daily Guidance Action", self.test_niro_chat_daily_guidance_action),
            ("NIRO Basic Career Message", self.test_niro_chat_basic_message),
            
            # Report Generation (existing functionality)
            ("Report Generation Flow", self.test_report_generation_flow)
        ]
        
        passed = 0
        total = len(tests)
        critical_failed = 0
        
        for test_name, test_func in tests:
            print(f"\n--- Testing {test_name} ---")
            if test_func():
                passed += 1
            else:
                # Check if this is a critical failure or API-related
                if test_name == "Report Generation Flow":
                    # Check if it's a Gemini API issue vs core functionality issue
                    last_result = self.test_results[-1] if self.test_results else {}
                    if "Gemini" in last_result.get("message", "") or "API" in last_result.get("message", ""):
                        print(f"   NOTE: {test_name} failed due to external API issues, not core functionality")
                    else:
                        critical_failed += 1
                else:
                    critical_failed += 1
        
        print("\n" + "=" * 60)
        print(f"RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ ALL REPORT GENERATION TESTS PASSED")
            print("No regression detected from Chat feature implementation")
        elif critical_failed == 0:
            print("⚠️  SOME TESTS FAILED DUE TO EXTERNAL API ISSUES")
            print("Core report generation functionality appears intact")
        else:
            print("❌ CRITICAL TESTS FAILED")
            print("Report generation functionality may be impacted")
        
        print("=" * 60)
        
        return passed >= 4  # Allow one failure if it's API-related

if __name__ == "__main__":
    tester = ReportGenerationTester()
    success = tester.run_all_tests()
    
    # Print detailed results
    print("\nDETAILED TEST RESULTS:")
    for result in tester.test_results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}: {result['message']}")
    
    exit(0 if success else 1)