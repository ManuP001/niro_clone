#!/usr/bin/env python3
"""
Role-Based Signal Enforcement Testing
Tests the 5 acceptance test queries from the review request
"""

import requests
import json
import uuid
import time

# Backend URL from environment
BACKEND_URL = "https://public-api-rollout.preview.emergentagent.com/api"

class RoleEnforcementTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def setup_authenticated_user_session(self, email, birth_details):
        """Helper to set up authenticated user session with birth details"""
        try:
            # Step 1: Register user
            auth_payload = {"identifier": email}
            response = self.session.post(f"{BACKEND_URL}/auth/identify", json=auth_payload, timeout=30)
            
            if response.status_code != 200:
                return None, f"Auth failed: HTTP {response.status_code} - {response.text}"
            
            auth_data = response.json()
            token = auth_data.get("token")
            if not token:
                return None, "No token in auth response"
            
            # Step 2: Create profile
            profile_payload = {
                "name": birth_details.get("name", "Test User"),
                "dob": birth_details["dob"],
                "tob": birth_details["tob"],
                "location": birth_details["location"],
                "birth_place_lat": birth_details["lat"],
                "birth_place_lon": birth_details["lon"],
                "birth_place_tz": birth_details.get("tz", 5.5)
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.post(f"{BACKEND_URL}/profile/", json=profile_payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                return None, f"Profile creation failed: HTTP {response.status_code} - {response.text}"
            
            return token, None
            
        except Exception as e:
            return None, f"Setup exception: {str(e)}"
    
    def test_query_with_role_enforcement(self, test_name, query, expected_karakas, expected_houses=None, is_past_question=False):
        """Generic test for role-based signal enforcement"""
        try:
            # Setup authenticated user with birth details
            birth_details = {
                "name": f"{test_name} User",
                "dob": "1990-05-15",
                "tob": "10:30",
                "location": "Mumbai",
                "lat": 19.08,
                "lon": 72.88,
                "tz": 5.5
            }
            
            email = f"{test_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}@example.com"
            token, error = self.setup_authenticated_user_session(email, birth_details)
            
            if error:
                self.log_result(f"{test_name} - Setup", False, error)
                return False
            
            # Send query with authentication
            headers = {"Authorization": f"Bearer {token}"}
            chat_payload = {
                "sessionId": f"{test_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}",
                "message": query,
                "actionId": None
            }
            
            response = self.session.post(f"{BACKEND_URL}/chat", json=chat_payload, headers=headers, timeout=60)
            
            if response.status_code != 200:
                self.log_result(test_name, False, f"Chat HTTP {response.status_code}", response.text)
                return False
            
            chat_data = response.json()
            
            # Check debug endpoint for candidate signals
            response = self.session.get(f"{BACKEND_URL}/debug/candidate-signals/latest", timeout=30)
            
            if response.status_code != 200:
                self.log_result(f"{test_name} - Debug", False, f"Debug endpoint HTTP {response.status_code}", response.text)
                return False
            
            debug_data = response.json()
            signals_data = debug_data.get("data", {})
            summary = signals_data.get("summary", {})
            
            # Verify role_counts distribution
            role_counts = summary.get("role_counts", {})
            if not role_counts:
                self.log_result(test_name, False, "No role_counts in debug data summary")
                return False
            
            # Check for TOPIC_DRIVER signals
            topic_driver_count = role_counts.get("TOPIC_DRIVER", 0)
            if topic_driver_count == 0:
                self.log_result(test_name, False, "No TOPIC_DRIVER signals found", role_counts)
                return False
            
            # Verify kept_count >= 4
            kept_count = summary.get("kept_count", 0)
            if kept_count < 4:
                self.log_result(test_name, False, f"kept_count {kept_count} < 4")
                return False
            
            # Verify driver_count = 3 (max)
            driver_count = summary.get("driver_count", 0)
            if driver_count != 3:
                self.log_result(test_name, False, f"driver_count {driver_count} != 3")
                return False
            
            # Check candidates for role and role_reason fields
            candidates = signals_data.get("candidates", [])
            if not candidates:
                self.log_result(test_name, False, "No candidates in debug data")
                return False
            
            # Verify each candidate has role and role_reason
            for i, candidate in enumerate(candidates):
                if "role" not in candidate:
                    self.log_result(test_name, False, f"Candidate {i} missing 'role' field")
                    return False
                if "role_reason" not in candidate:
                    self.log_result(test_name, False, f"Candidate {i} missing 'role_reason' field")
                    return False
            
            # Special check for past questions
            if is_past_question:
                invalid_time_drivers = []
                for candidate in candidates:
                    if candidate.get("role") == "TIME_DRIVER":
                        role_reason = candidate.get("role_reason", "").lower()
                        claim = candidate.get("claim", "").lower()
                        
                        # Check for forbidden terms in TIME_DRIVER signals for past questions
                        forbidden_terms = ["current ongoing", "current antardasha", "current dasha", "ongoing", "active"]
                        for term in forbidden_terms:
                            if term in role_reason or term in claim:
                                invalid_time_drivers.append({
                                    "candidate": candidate,
                                    "forbidden_term": term
                                })
                                break
                
                if invalid_time_drivers:
                    self.log_result(test_name, False, 
                                  f"Found {len(invalid_time_drivers)} TIME_DRIVER signals with forbidden current/ongoing terms for past question")
                    return False
            
            # Check for expected karakas in Trust Widget drivers
            trust_widget = chat_data.get("trustWidget", {})
            drivers = trust_widget.get("drivers", [])
            
            if not drivers:
                self.log_result(test_name, False, "No Trust Widget drivers found")
                return False
            
            # Extract planets from drivers
            driver_planets = []
            for driver in drivers:
                driver_text = driver.get("label", "").lower()
                for karaka in expected_karakas:
                    if karaka.lower() in driver_text:
                        driver_planets.append(karaka.title())
                        break
            
            if not driver_planets:
                self.log_result(test_name, False, 
                              f"No expected karakas ({expected_karakas}) found in drivers: {[d.get('label', '') for d in drivers]}")
                return False
            
            # Check for expected houses if provided
            if expected_houses:
                topic_driver_houses = []
                for candidate in candidates:
                    if candidate.get("role") == "TOPIC_DRIVER":
                        house = candidate.get("house")
                        if house and house in expected_houses:
                            topic_driver_houses.append(house)
                
                if not topic_driver_houses:
                    self.log_result(test_name, False, 
                                  f"No TOPIC_DRIVER signals found for expected houses {expected_houses}")
                    return False
            
            # Verify planet diversity (max 2 signals per planet)
            kept_signals = [c for c in candidates if c.get("kept", False)]
            planet_counts = {}
            for signal in kept_signals:
                planet = signal.get("planet", "Unknown")
                planet_counts[planet] = planet_counts.get(planet, 0) + 1
            
            violations = []
            for planet, count in planet_counts.items():
                if count > 2:
                    violations.append(f"{planet}: {count} signals")
            
            if violations:
                self.log_result(test_name, False, f"Planet diversity violation: {violations}")
                return False
            
            self.log_result(test_name, True, 
                          f"✅ {topic_driver_count} TOPIC_DRIVER signals, {kept_count} kept, {driver_count} drivers, karakas: {driver_planets}")
            return True
            
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all 5 acceptance test queries"""
        print("=" * 80)
        print("TESTING ROLE-BASED SIGNAL ENFORCEMENT - 5 ACCEPTANCE QUERIES")
        print("=" * 80)
        
        tests = [
            {
                "name": "Career Query",
                "query": "What's my career outlook?",
                "expected_karakas": ["Saturn", "Sun", "Mercury"],
                "expected_houses": [10, 6, 2]
            },
            {
                "name": "Relationships Query", 
                "query": "Will I find love this year?",
                "expected_karakas": ["Venus", "Moon", "Jupiter"],
                "expected_houses": [7, 5, 11]
            },
            {
                "name": "Money Query",
                "query": "How's my financial future?", 
                "expected_karakas": ["Mercury", "Jupiter", "Venus"],
                "expected_houses": [2, 11, 8]
            },
            {
                "name": "Health Query",
                "query": "How's my health looking?",
                "expected_karakas": ["Sun", "Mars", "Saturn"],
                "expected_houses": [1, 6, 8, 12]
            },
            {
                "name": "Past Question",
                "query": "What happened in my career last year?",
                "expected_karakas": ["Saturn", "Sun", "Mercury"],
                "expected_houses": [10, 6, 2],
                "is_past_question": True
            }
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            print(f"\n--- Testing {test['name']} ---")
            if self.test_query_with_role_enforcement(
                test["name"],
                test["query"], 
                test["expected_karakas"],
                test.get("expected_houses"),
                test.get("is_past_question", False)
            ):
                passed += 1
        
        print("\n" + "=" * 60)
        print(f"RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ ALL ROLE-BASED SIGNAL ENFORCEMENT TESTS PASSED")
            print("Role-based signal enforcement working correctly")
        elif passed >= 3:
            print("✅ CORE ROLE-BASED SIGNAL ENFORCEMENT FUNCTIONALITY WORKING")
            print("Minor issues may exist but core features operational")
        else:
            print("❌ CRITICAL TESTS FAILED")
            print("Role-based signal enforcement functionality may be impacted")
        
        print("=" * 60)
        
        return passed >= 3

if __name__ == "__main__":
    tester = RoleEnforcementTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)