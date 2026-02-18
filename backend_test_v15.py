#!/usr/bin/env python3
"""
Backend API Testing for NIRO Simplified V1.5
Tests NIRO Simplified V1.5 backend APIs according to review request
"""

import requests
import json
import time
import uuid
import re
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://responsive-refactor-2.preview.emergentagent.com/api"

class NiroSimplifiedV15Tester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.test_user_email = "v15test@example.com"
        self.test_user_token = None
        
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
    
    def test_simplified_topics_list(self):
        """Test GET /api/simplified/topics - Should return 12 topics"""
        try:
            response = self.session.get(f"{BACKEND_URL}/simplified/topics", timeout=10)
            
            if response.status_code != 200:
                self.log_result("NIRO V1.5 Topics Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check response structure
            if not data.get("ok"):
                self.log_result("NIRO V1.5 Topics Endpoint", False, 
                              "Response ok field is not true", data)
                return False
            
            topics = data.get("topics", [])
            if len(topics) != 12:
                self.log_result("NIRO V1.5 Topics Endpoint", False, 
                              f"Expected 12 topics, got {len(topics)}", data)
                return False
            
            # Verify each topic has required fields
            required_fields = ["topic_id", "label", "icon", "tagline", "color_scheme"]
            for i, topic in enumerate(topics):
                missing_fields = [field for field in required_fields if field not in topic]
                if missing_fields:
                    self.log_result("NIRO V1.5 Topics Endpoint", False, 
                                  f"Topic {i} missing fields: {missing_fields}", topic)
                    return False
            
            # Check catalog version
            if not data.get("catalog_version"):
                self.log_result("NIRO V1.5 Topics Endpoint", False, 
                              "Missing catalog_version", data)
                return False
            
            self.log_result("NIRO V1.5 Topics Endpoint", True, 
                          f"Found {len(topics)} topics with all required fields")
            return True
            
        except Exception as e:
            self.log_result("NIRO V1.5 Topics Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_simplified_all_experts_endpoint(self):
        """Test GET /api/simplified/experts/all - Should return 23+ experts with real photo URLs and 14 modalities"""
        try:
            response = self.session.get(f"{BACKEND_URL}/simplified/experts/all", timeout=10)
            
            if response.status_code != 200:
                self.log_result("NIRO V1.5 All Experts Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check response structure
            if not data.get("ok"):
                self.log_result("NIRO V1.5 All Experts Endpoint", False, 
                              "Response ok field is not true", data)
                return False
            
            # Check experts array
            experts = data.get("experts", [])
            if len(experts) < 23:
                self.log_result("NIRO V1.5 All Experts Endpoint", False, 
                              f"Expected 23+ experts, got {len(experts)}", data)
                return False
            
            # Verify expert photo URLs are real (not placeholder paths)
            placeholder_count = 0
            real_url_count = 0
            for expert in experts:
                photo_url = expert.get("photo_url", "")
                if "/images/experts/" in photo_url:
                    placeholder_count += 1
                elif photo_url.startswith("https://randomuser.me/api/portraits/"):
                    real_url_count += 1
            
            if placeholder_count > 0:
                self.log_result("NIRO V1.5 All Experts Endpoint", False, 
                              f"Found {placeholder_count} experts with placeholder photo paths (/images/experts/*)", data)
                return False
            
            if real_url_count < 20:  # Most should have real URLs
                self.log_result("NIRO V1.5 All Experts Endpoint", False, 
                              f"Only {real_url_count} experts have real photo URLs (randomuser.me)", data)
                return False
            
            # Check grouped_by_modality object
            grouped_by_modality = data.get("grouped_by_modality", {})
            if not isinstance(grouped_by_modality, dict):
                self.log_result("NIRO V1.5 All Experts Endpoint", False, 
                              "grouped_by_modality is not an object", data)
                return False
            
            # Check modalities array
            modalities = data.get("modalities", [])
            if len(modalities) < 14:
                self.log_result("NIRO V1.5 All Experts Endpoint", False, 
                              f"Expected 14 modalities, got {len(modalities)}", data)
                return False
            
            # Verify modalities match grouped_by_modality keys
            grouped_keys = set(grouped_by_modality.keys())
            modalities_set = set(modalities)
            if grouped_keys != modalities_set:
                self.log_result("NIRO V1.5 All Experts Endpoint", False, 
                              f"Modalities array doesn't match grouped_by_modality keys", data)
                return False
            
            # Check total_count
            total_count = data.get("total_count", 0)
            if total_count != len(experts):
                self.log_result("NIRO V1.5 All Experts Endpoint", False, 
                              f"total_count {total_count} doesn't match experts array length {len(experts)}", data)
                return False
            
            self.log_result("NIRO V1.5 All Experts Endpoint", True, 
                          f"Found {len(experts)} experts with {real_url_count} real photo URLs, {len(modalities)} modalities")
            return True
            
        except Exception as e:
            self.log_result("NIRO V1.5 All Experts Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_simplified_topic_career_detail(self):
        """Test GET /api/simplified/topics/career - Should return career topic details with experts, scenarios, tiers, tools"""
        try:
            response = self.session.get(f"{BACKEND_URL}/simplified/topics/career", timeout=10)
            
            if response.status_code != 200:
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check response structure
            if not data.get("ok"):
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              "Response ok field is not true", data)
                return False
            
            # Check required top-level fields
            required_fields = ["topic", "experts", "scenarios", "tiers", "tools", "unlimited_conditions"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              f"Missing fields: {missing_fields}", data)
                return False
            
            # Verify topic details
            topic = data.get("topic")
            if not topic or topic.get("topic_id") != "career":
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              f"Invalid topic data: {topic}")
                return False
            
            # Verify experts array - check for real photo URLs
            experts = data.get("experts", [])
            if len(experts) == 0:
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              "No experts found for career topic", data)
                return False
            
            # Check expert photos are real URLs
            placeholder_photos = 0
            for expert in experts:
                photo_url = expert.get("photo_url", "")
                if "/images/experts/" in photo_url:
                    placeholder_photos += 1
            
            if placeholder_photos > 0:
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              f"Found {placeholder_photos} experts with placeholder photo paths", data)
                return False
            
            # Verify scenarios array
            scenarios = data.get("scenarios", [])
            if len(scenarios) == 0:
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              "No scenarios found for career topic", data)
                return False
            
            # Verify tiers array (should have starter, plus, pro)
            tiers = data.get("tiers", [])
            if len(tiers) != 3:
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              f"Expected 3 tiers, got {len(tiers)}", data)
                return False
            
            tier_levels = [tier.get("tier_level") for tier in tiers]
            expected_levels = ["starter", "plus", "pro"]
            if not all(level in tier_levels for level in expected_levels):
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              f"Missing tier levels. Expected {expected_levels}, got {tier_levels}", data)
                return False
            
            # Verify tools array
            tools = data.get("tools", [])
            if len(tools) == 0:
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              "No tools found for career topic", data)
                return False
            
            # Verify unlimited_conditions
            unlimited_conditions = data.get("unlimited_conditions")
            if not unlimited_conditions:
                self.log_result("NIRO V1.5 Career Topic Detail", False, 
                              "Missing unlimited_conditions", data)
                return False
            
            self.log_result("NIRO V1.5 Career Topic Detail", True, 
                          f"Career topic detail complete: {len(experts)} experts (no placeholder photos), {len(scenarios)} scenarios, {len(tiers)} tiers, {len(tools)} tools")
            return True
            
        except Exception as e:
            self.log_result("NIRO V1.5 Career Topic Detail", False, f"Exception: {str(e)}")
            return False
    
    def test_simplified_user_state_unauthenticated(self):
        """Test GET /api/simplified/user/state - Should return is_new_user: true for unauthenticated user"""
        try:
            response = self.session.get(f"{BACKEND_URL}/simplified/user/state", timeout=10)
            
            if response.status_code != 200:
                self.log_result("NIRO V1.5 User State (Unauthenticated)", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check response structure
            if not data.get("ok"):
                self.log_result("NIRO V1.5 User State (Unauthenticated)", False, 
                              "Response ok field is not true", data)
                return False
            
            user_state = data.get("user_state")
            if not user_state:
                self.log_result("NIRO V1.5 User State (Unauthenticated)", False, 
                              "No user_state in response", data)
                return False
            
            # Check required fields for new user
            required_fields = ["user_id", "is_new_user", "has_active_plan", "active_plans", "recent_expert_threads", "additional_topic_passes"]
            missing_fields = [field for field in required_fields if field not in user_state]
            if missing_fields:
                self.log_result("NIRO V1.5 User State (Unauthenticated)", False, 
                              f"Missing fields: {missing_fields}", user_state)
                return False
            
            # Verify new user state
            if not user_state.get("is_new_user"):
                self.log_result("NIRO V1.5 User State (Unauthenticated)", False, 
                              "Expected is_new_user to be true for unauthenticated user", user_state)
                return False
            
            if user_state.get("has_active_plan"):
                self.log_result("NIRO V1.5 User State (Unauthenticated)", False, 
                              "Expected has_active_plan to be false for new user", user_state)
                return False
            
            # Check arrays are empty for new user
            if len(user_state.get("active_plans", [])) > 0:
                self.log_result("NIRO V1.5 User State (Unauthenticated)", False, 
                              "Expected empty active_plans for new user", user_state)
                return False
            
            if len(user_state.get("recent_expert_threads", [])) > 0:
                self.log_result("NIRO V1.5 User State (Unauthenticated)", False, 
                              "Expected empty recent_expert_threads for new user", user_state)
                return False
            
            if len(user_state.get("additional_topic_passes", [])) > 0:
                self.log_result("NIRO V1.5 User State (Unauthenticated)", False, 
                              "Expected empty additional_topic_passes for new user", user_state)
                return False
            
            self.log_result("NIRO V1.5 User State (Unauthenticated)", True, 
                          f"New user state verified: user_id={user_state.get('user_id')}, is_new_user=true")
            return True
            
        except Exception as e:
            self.log_result("NIRO V1.5 User State (Unauthenticated)", False, f"Exception: {str(e)}")
            return False
    
    def test_create_test_user_and_order(self):
        """Test creating test user and order creation with tier_id=career_plus"""
        try:
            # Step 1: Create test user via POST /api/auth/identify
            user_payload = {
                "identifier": self.test_user_email
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/identify", json=user_payload, timeout=10)
            
            if response.status_code != 200:
                self.log_result("NIRO V1.5 Create Test User", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_result("NIRO V1.5 Create Test User", False, 
                              "Response ok field is not true", data)
                return False
            
            # Extract token
            token = data.get("token")
            if not token:
                self.log_result("NIRO V1.5 Create Test User", False, 
                              "No token in response", data)
                return False
            
            self.test_user_token = token
            
            self.log_result("NIRO V1.5 Create Test User", True, 
                          f"Test user created with email: {self.test_user_email}")
            
            # Step 2: Create order with tier_id="career_plus"
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            order_payload = {
                "tier_id": "career_plus",
                "scenario_ids": [],
                "intake_notes": "Test order for V1.5 testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/simplified/checkout/create-order", 
                                       json=order_payload, headers=headers, timeout=15)
            
            if response.status_code != 200:
                self.log_result("NIRO V1.5 Order Creation", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            if not data.get("ok"):
                self.log_result("NIRO V1.5 Order Creation", False, 
                              "Response ok field is not true", data)
                return False
            
            # Check razorpay_order_id
            razorpay_order_id = data.get("razorpay_order_id")
            if not razorpay_order_id:
                self.log_result("NIRO V1.5 Order Creation", False, 
                              "Missing razorpay_order_id", data)
                return False
            
            # Check key_id is returned correctly
            key_id = data.get("key_id")
            if not key_id:
                self.log_result("NIRO V1.5 Order Creation", False, 
                              "Missing key_id", data)
                return False
            
            # Verify key_id format (should start with rzp_live_ or rzp_test_)
            if not (key_id.startswith("rzp_live_") or key_id.startswith("rzp_test_")):
                self.log_result("NIRO V1.5 Order Creation", False, 
                              f"Invalid key_id format: {key_id}", data)
                return False
            
            # Check amount
            amount = data.get("amount")
            if not amount or amount <= 0:
                self.log_result("NIRO V1.5 Order Creation", False, 
                              f"Invalid amount: {amount}", data)
                return False
            
            # Check currency
            currency = data.get("currency")
            if currency != "INR":
                self.log_result("NIRO V1.5 Order Creation", False, 
                              f"Expected currency INR, got {currency}", data)
                return False
            
            self.log_result("NIRO V1.5 Order Creation", True, 
                          f"Order created successfully: razorpay_order_id={razorpay_order_id}, key_id={key_id}, amount=₹{amount/100}")
            return True
            
        except Exception as e:
            self.log_result("NIRO V1.5 Order Creation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all NIRO Simplified V1.5 tests in sequence"""
        print("🚀 Starting NIRO Simplified V1.5 Backend Testing...")
        print("=" * 60)
        
        tests = [
            self.test_simplified_topics_list,
            self.test_simplified_all_experts_endpoint,
            self.test_simplified_topic_career_detail,
            self.test_simplified_user_state_unauthenticated,
            self.test_create_test_user_and_order
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL {test.__name__}: Exception: {str(e)}")
                failed += 1
            
            time.sleep(0.5)  # Brief pause between tests
        
        print("=" * 60)
        print(f"🏁 NIRO Simplified V1.5 Testing Complete: {passed} passed, {failed} failed")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['message']}")
        
        return failed == 0


if __name__ == "__main__":
    tester = NiroSimplifiedV15Tester()
    success = tester.run_all_tests()
    exit(0 if success else 1)