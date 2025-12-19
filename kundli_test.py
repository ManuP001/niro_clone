#!/usr/bin/env python3
"""
Kundli API Testing - Specific test for the review request
Tests the Kundli API endpoint to verify planets data, houses data, and SVG chart
"""

import requests
import json
import uuid
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://init-project-6.preview.emergentagent.com/api"

class KundliTester:
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
        """Test Kundli API Endpoint as per review request"""
        try:
            print("=== Testing Kundli API Endpoint ===")
            
            # Step 1: Register a test user at POST /api/auth/identify
            register_payload = {
                "identifier": "kundli_test@example.com"
            }
            
            print("Step 1: Registering test user...")
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
            
            # Step 2: Create profile at POST /api/profile/ with birth details
            profile_payload = {
                "name": "Kundli Test User",
                "dob": "1990-05-15",
                "tob": "10:30",
                "location": "New Delhi, India",
                "birth_place_lat": 28.6139,
                "birth_place_lon": 77.2090,
                "birth_place_tz": 5.5
            }
            
            print("Step 2: Creating profile with birth details...")
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
            
            # Step 3: Call GET /api/kundli with the token
            print("Step 3: Fetching Kundli chart...")
            response = self.session.get(f"{BACKEND_URL}/kundli", 
                                      headers=headers, 
                                      timeout=30)
            
            if response.status_code != 200:
                self.log_result("Kundli API Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            kundli_data = response.json()
            
            # Step 4: Verify response structure
            print("Step 4: Verifying response structure...")
            
            # Verify response.ok === true
            if not kundli_data.get("ok"):
                error_msg = kundli_data.get("message", "Unknown error")
                self.log_result("Kundli API - Response OK", False, 
                              f"Response not OK: {error_msg}", kundli_data)
                return False
            
            self.log_result("Kundli API - Response OK", True, "Response OK is true")
            
            # Verify SVG starts with "<?xml" or "<svg"
            svg_content = kundli_data.get("svg", "")
            if not svg_content:
                self.log_result("Kundli API - SVG Content", False, 
                              "Empty SVG content", kundli_data)
                return False
            
            if not (svg_content.startswith("<?xml") or svg_content.startswith("<svg")):
                self.log_result("Kundli API - SVG Format", False, 
                              f"SVG doesn't start with <?xml or <svg: '{svg_content[:50]}'", {"svg_start": svg_content[:100]})
                return False
            
            self.log_result("Kundli API - SVG Format", True, 
                          f"Valid SVG format, size: {len(svg_content)} bytes")
            
            # Verify structured data exists
            structured = kundli_data.get("structured", {})
            if not structured:
                self.log_result("Kundli API - Structured Data", False, 
                              "Empty structured data", kundli_data)
                return False
            
            # Verify response.structured.planets is an array with 9 elements
            planets = structured.get("planets", [])
            if not isinstance(planets, list):
                self.log_result("Kundli API - Planets Array", False, 
                              "Planets is not an array", structured)
                return False
            
            if len(planets) != 9:
                self.log_result("Kundli API - Planets Count", False, 
                              f"Expected 9 planets, got {len(planets)}", planets)
                return False
            
            self.log_result("Kundli API - Planets Count", True, 
                          f"Found {len(planets)} planets as expected")
            
            # Verify each planet has name, sign, house
            expected_planet_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
            planet_names = [planet.get("name", "") for planet in planets]
            
            for planet in planets:
                required_fields = ["name", "sign", "house"]
                missing_fields = [field for field in required_fields if field not in planet or not planet[field]]
                if missing_fields:
                    self.log_result("Kundli API - Planet Fields", False, 
                                  f"Planet {planet.get('name', 'Unknown')} missing fields: {missing_fields}", planet)
                    return False
            
            # Check if we have all expected planets
            missing_planets = [name for name in expected_planet_names if name not in planet_names]
            if missing_planets:
                self.log_result("Kundli API - Planet Names", False, 
                              f"Missing planets: {missing_planets}. Found: {planet_names}", planets)
                return False
            
            self.log_result("Kundli API - Planet Data", True, 
                          f"All 9 planets have required fields (name, sign, house): {planet_names}")
            
            # Verify response.structured.houses is an array with 12 elements
            houses = structured.get("houses", [])
            if not isinstance(houses, list):
                self.log_result("Kundli API - Houses Array", False, 
                              "Houses is not an array", structured)
                return False
            
            if len(houses) != 12:
                self.log_result("Kundli API - Houses Count", False, 
                              f"Expected 12 houses, got {len(houses)}", houses)
                return False
            
            self.log_result("Kundli API - Houses Count", True, 
                          f"Found {len(houses)} houses as expected")
            
            # Verify each house has proper house numbers, signs, and lords
            for i, house in enumerate(houses):
                # Check that required fields exist (lord can be empty string)
                required_fields = ["house", "sign", "lord"]
                missing_fields = [field for field in required_fields if field not in house]
                if missing_fields:
                    self.log_result("Kundli API - House Fields", False, 
                                  f"House {i+1} missing fields: {missing_fields}", house)
                    return False
                
                # Verify house number is correct
                expected_house_num = i + 1
                actual_house_num = house.get("house")
                if actual_house_num != expected_house_num:
                    self.log_result("Kundli API - House Numbers", False, 
                                  f"House {i+1} has incorrect house number: {actual_house_num}", house)
                    return False
            
            self.log_result("Kundli API - House Data", True, 
                          "All 12 houses have proper house numbers, signs, and lords")
            
            # Final success
            self.log_result("Kundli API Endpoint", True, 
                          f"✅ ALL VERIFICATIONS PASSED - SVG: {len(svg_content)} bytes, Planets: {len(planets)} with all required fields, Houses: {len(houses)} with proper structure")
            
            return True
            
        except Exception as e:
            self.log_result("Kundli API Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def run_tests(self):
        """Run all tests"""
        print("Starting Kundli API Testing...")
        print("=" * 60)
        
        success = self.test_kundli_api_endpoint()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 KUNDLI API TEST PASSED - All fixes verified!")
        else:
            print("❌ KUNDLI API TEST FAILED - Issues found")
        print("=" * 60)
        
        return success

if __name__ == "__main__":
    tester = KundliTester()
    success = tester.run_tests()
    exit(0 if success else 1)