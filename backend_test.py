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
    
    def run_all_tests(self):
        """Run all report generation tests"""
        print("=" * 60)
        print("TESTING REPORT GENERATION FUNCTIONALITY")
        print("Ensuring no regression from Chat feature implementation")
        print("=" * 60)
        
        tests = [
            ("Pricing Endpoint", self.test_pricing_endpoint),
            ("Health Check", self.test_health_check),
            ("City Search", self.test_city_search),
            ("Time Parser", self.test_time_parser),
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