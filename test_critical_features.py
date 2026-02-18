#!/usr/bin/env python3
"""
Test only the critical features from the review request
"""

import requests
import json
import uuid
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://responsive-dashboard-14.preview.emergentagent.com/api"

class CriticalFeaturesTester:
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

    def test_kundli_api_endpoint(self):
        """Test Kundli API Endpoint (GET /api/kundli) - CRITICAL FEATURE"""
        try:
            # Step 1: Register a new user
            register_payload = {
                "identifier": f"test_kundli_{uuid.uuid4().hex[:8]}@example.com"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/identify", json=register_payload, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Kundli API - User Registration", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            auth_data = response.json()
            token = auth_data.get("token")
            user_id = auth_data.get("user_id")
            
            if not token:
                self.log_result("Kundli API - User Registration", False, 
                              "No token received", auth_data)
                return False
            
            self.log_result("Kundli API - User Registration", True, 
                          f"User registered: {user_id}")
            
            # Step 2: Complete onboarding with birth details
            profile_payload = {
                "name": "Test User",
                "dob": "1990-05-15",
                "tob": "10:30",
                "location": "New Delhi, India",
                "birth_place_lat": 28.6139,
                "birth_place_lon": 77.2090,
                "birth_place_tz": 5.5
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.post(f"{BACKEND_URL}/profile/", 
                                       json=profile_payload, 
                                       headers=headers, 
                                       timeout=10)
            
            if response.status_code != 200:
                self.log_result("Kundli API - Profile Creation", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            profile_result = response.json()
            if not profile_result.get("ok") or not profile_result.get("profile_complete"):
                self.log_result("Kundli API - Profile Creation", False, 
                              "Profile not completed", profile_result)
                return False
            
            self.log_result("Kundli API - Profile Creation", True, 
                          "Birth details saved successfully")
            
            # Step 3: Fetch Kundli chart
            response = self.session.get(f"{BACKEND_URL}/kundli", 
                                      headers=headers, 
                                      timeout=30)
            
            if response.status_code != 200:
                self.log_result("Kundli API Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            kundli_data = response.json()
            
            # Verify response structure
            required_fields = ["ok", "svg", "profile", "structured", "source"]
            missing_fields = [field for field in required_fields if field not in kundli_data]
            
            if missing_fields:
                self.log_result("Kundli API Endpoint", False, 
                              f"Missing fields: {missing_fields}", kundli_data)
                return False
            
            # Verify ok=true
            if not kundli_data.get("ok"):
                error_msg = kundli_data.get("message", "Unknown error")
                self.log_result("Kundli API Endpoint", False, 
                              f"Kundli fetch failed: {error_msg}", kundli_data)
                return False
            
            # Verify SVG content
            svg_content = kundli_data.get("svg", "")
            if not svg_content or len(svg_content) < 100:
                self.log_result("Kundli API Endpoint", False, 
                              f"Invalid SVG content (length: {len(svg_content)})", kundli_data)
                return False
            
            # SVG can start with <?xml declaration or <svg tag directly
            if not (svg_content.startswith("<svg") or svg_content.startswith("<?xml")) or not svg_content.rstrip().endswith("</svg>"):
                self.log_result("Kundli API Endpoint", False, 
                              "SVG content doesn't have proper SVG tags", svg_content[:200])
                return False
            
            # Verify structured data
            structured = kundli_data.get("structured", {})
            if "houses" not in structured or "planets" not in structured:
                self.log_result("Kundli API Endpoint", False, 
                              "Missing houses or planets in structured data", structured)
                return False
            
            houses = structured.get("houses", [])
            planets = structured.get("planets", [])
            
            if len(houses) != 12:
                self.log_result("Kundli API Endpoint", False, 
                              f"Expected 12 houses, got {len(houses)}", structured)
                return False
            
            # Note: planets might be 0 if API doesn't return planet data
            
            # Verify profile data
            profile = kundli_data.get("profile", {})
            expected_profile_fields = ["name", "dob", "tob", "location"]
            missing_profile_fields = [field for field in expected_profile_fields if field not in profile]
            
            if missing_profile_fields:
                self.log_result("Kundli API Endpoint", False, 
                              f"Missing profile fields: {missing_profile_fields}", profile)
                return False
            
            self.log_result("Kundli API Endpoint", True, 
                          f"Kundli API working! SVG size: {len(svg_content)} bytes, Houses: {len(houses)}, Planets: {len(planets)}")
            return True
            
        except Exception as e:
            self.log_result("Kundli API Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_checklist_api_endpoint(self):
        """Test Checklist API Endpoint (GET /api/debug/checklist/{request_id}) - CRITICAL FEATURE"""
        try:
            # Step 1: Make a chat request to get requestId
            session_id = f"test_checklist_{uuid.uuid4().hex[:8]}"
            
            chat_payload = {
                "sessionId": session_id,
                "message": "Tell me about my career prospects",
                "actionId": "focus_career",
                "subjectData": {
                    "name": "Test User",
                    "birthDetails": {
                        "dob": "1990-05-15",
                        "tob": "10:30",
                        "location": "New Delhi, India",
                        "latitude": 28.6139,
                        "longitude": 77.2090,
                        "timezone": 5.5
                    }
                }
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=chat_payload, timeout=30)
            
            if response.status_code != 200:
                self.log_result("Checklist API - Chat Request", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            chat_data = response.json()
            request_id = chat_data.get("requestId")
            
            if not request_id:
                self.log_result("Checklist API - Chat Request", False, 
                              "No requestId returned from chat", chat_data)
                return False
            
            self.log_result("Checklist API - Chat Request", True, 
                          f"Chat request successful, requestId: {request_id}")
            
            # Step 2: Test HTML checklist endpoint
            response = self.session.get(f"{BACKEND_URL}/debug/checklist/{request_id}", timeout=15)
            
            if response.status_code != 200:
                self.log_result("Checklist API - HTML Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            html_content = response.text
            
            # Verify HTML content structure
            if not html_content or len(html_content) < 100:
                self.log_result("Checklist API - HTML Endpoint", False, 
                              f"Invalid HTML content (length: {len(html_content)})", html_content[:200])
                return False
            
            # Check for HTML structure
            if "<html" not in html_content.lower() or "</html>" not in html_content.lower():
                self.log_result("Checklist API - HTML Endpoint", False, 
                              "Response doesn't contain proper HTML structure", html_content[:200])
                return False
            
            # Check for request ID in content
            if request_id not in html_content:
                self.log_result("Checklist API - HTML Endpoint", False, 
                              f"Request ID {request_id} not found in HTML content", html_content[:500])
                return False
            
            self.log_result("Checklist API - HTML Endpoint", True, 
                          f"HTML checklist working! Content size: {len(html_content)} bytes")
            
            # Step 3: Test JSON checklist endpoint
            response = self.session.get(f"{BACKEND_URL}/processing/checklist/{request_id}", timeout=15)
            
            if response.status_code != 200:
                self.log_result("Checklist API - JSON Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            json_data = response.json()
            
            # Verify JSON structure
            required_fields = ["ok", "request_id", "timestamp", "user_input", "birth_details", "api_calls", "reading_pack", "llm", "final"]
            missing_fields = [field for field in required_fields if field not in json_data]
            
            if missing_fields:
                self.log_result("Checklist API - JSON Endpoint", False, 
                              f"Missing fields: {missing_fields}", json_data)
                return False
            
            # Verify ok=true
            if not json_data.get("ok"):
                self.log_result("Checklist API - JSON Endpoint", False, 
                              "JSON response ok=false", json_data)
                return False
            
            # Verify request_id matches
            if json_data.get("request_id") != request_id:
                self.log_result("Checklist API - JSON Endpoint", False, 
                              f"Request ID mismatch: expected {request_id}, got {json_data.get('request_id')}", json_data)
                return False
            
            # Verify nested structures
            user_input = json_data.get("user_input", {})
            if not isinstance(user_input, dict) or "message" not in user_input:
                self.log_result("Checklist API - JSON Endpoint", False, 
                              "Invalid user_input structure", user_input)
                return False
            
            birth_details = json_data.get("birth_details", {})
            if not isinstance(birth_details, dict):
                self.log_result("Checklist API - JSON Endpoint", False, 
                              "Invalid birth_details structure", birth_details)
                return False
            
            api_calls = json_data.get("api_calls", [])
            if not isinstance(api_calls, list):
                self.log_result("Checklist API - JSON Endpoint", False, 
                              "Invalid api_calls structure", api_calls)
                return False
            
            reading_pack = json_data.get("reading_pack", {})
            if not isinstance(reading_pack, dict):
                self.log_result("Checklist API - JSON Endpoint", False, 
                              "Invalid reading_pack structure", reading_pack)
                return False
            
            llm = json_data.get("llm", {})
            if not isinstance(llm, dict) or "model" not in llm:
                self.log_result("Checklist API - JSON Endpoint", False, 
                              "Invalid llm structure", llm)
                return False
            
            final = json_data.get("final", {})
            if not isinstance(final, dict) or "status" not in final:
                self.log_result("Checklist API - JSON Endpoint", False, 
                              "Invalid final structure", final)
                return False
            
            self.log_result("Checklist API - JSON Endpoint", True, 
                          f"JSON checklist working! Model: {llm.get('model')}, Status: {final.get('status')}")
            
            self.log_result("Checklist API Endpoint", True, 
                          f"Both HTML and JSON checklist endpoints working for request {request_id}")
            return True
            
        except Exception as e:
            self.log_result("Checklist API Endpoint", False, f"Exception: {str(e)}")
            return False

    def run_critical_tests(self):
        """Run only the critical features tests"""
        print("=" * 80)
        print("TESTING CRITICAL FEATURES - USER REPORTED FAILURES")
        print("Focus: Kundli API & Checklist API")
        print("=" * 80)
        
        tests = [
            ("🚨 CRITICAL: Kundli API Endpoint", self.test_kundli_api_endpoint),
            ("🚨 CRITICAL: Checklist API Endpoint", self.test_checklist_api_endpoint),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- Testing {test_name} ---")
            if test_func():
                passed += 1
        
        print("\n" + "=" * 60)
        print(f"CRITICAL FEATURES RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ ALL CRITICAL FEATURES WORKING")
            print("Both Kundli API and Checklist API are functional")
        else:
            print("❌ CRITICAL FEATURES FAILING")
            print("User-reported issues confirmed")
        
        print("=" * 60)
        
        return passed == total

if __name__ == "__main__":
    tester = CriticalFeaturesTester()
    success = tester.run_critical_tests()
    
    # Print detailed results
    print("\nDETAILED TEST RESULTS:")
    for result in tester.test_results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}: {result['message']}")
    
    exit(0 if success else 1)