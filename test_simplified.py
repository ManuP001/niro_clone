#!/usr/bin/env python3
"""
NIRO Simplified V1 API Testing
Tests the 5 specific endpoints mentioned in the review request
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://kundli-backend.preview.emergentagent.com/api"

class NiroSimplifiedTester:
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
    
    def test_simplified_topics_list(self):
        """Test GET /api/simplified/topics - Should return 12 topics"""
        try:
            response = self.session.get(f"{BACKEND_URL}/simplified/topics", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Simplified Topics List", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check response structure
            if not data.get("ok"):
                self.log_result("Simplified Topics List", False, 
                              "Response ok field is not true", data)
                return False
            
            topics = data.get("topics", [])
            if len(topics) != 12:
                self.log_result("Simplified Topics List", False, 
                              f"Expected 12 topics, got {len(topics)}", data)
                return False
            
            # Verify each topic has required fields
            required_fields = ["topic_id", "label", "icon", "tagline", "color_scheme"]
            for i, topic in enumerate(topics):
                missing_fields = [field for field in required_fields if field not in topic]
                if missing_fields:
                    self.log_result("Simplified Topics List", False, 
                                  f"Topic {i} missing fields: {missing_fields}", topic)
                    return False
            
            # Check catalog version
            if not data.get("catalog_version"):
                self.log_result("Simplified Topics List", False, 
                              "Missing catalog_version", data)
                return False
            
            self.log_result("Simplified Topics List", True, 
                          f"Found {len(topics)} topics with all required fields")
            return True
            
        except Exception as e:
            self.log_result("Simplified Topics List", False, f"Exception: {str(e)}")
            return False
    
    def test_simplified_topic_career_detail(self):
        """Test GET /api/simplified/topics/career - Should return career topic details with experts, scenarios, tiers, tools, and unlimited_conditions"""
        try:
            response = self.session.get(f"{BACKEND_URL}/simplified/topics/career", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Simplified Career Topic Detail", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check response structure
            if not data.get("ok"):
                self.log_result("Simplified Career Topic Detail", False, 
                              "Response ok field is not true", data)
                return False
            
            # Check required top-level fields
            required_fields = ["topic", "experts", "scenarios", "tiers", "tools", "unlimited_conditions"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_result("Simplified Career Topic Detail", False, 
                              f"Missing fields: {missing_fields}", data)
                return False
            
            # Verify topic details
            topic = data.get("topic")
            if not topic or topic.get("topic_id") != "career":
                self.log_result("Simplified Career Topic Detail", False, 
                              f"Invalid topic data: {topic}")
                return False
            
            # Verify experts array
            experts = data.get("experts", [])
            if len(experts) == 0:
                self.log_result("Simplified Career Topic Detail", False, 
                              "No experts found for career topic", data)
                return False
            
            # Verify scenarios array
            scenarios = data.get("scenarios", [])
            if len(scenarios) == 0:
                self.log_result("Simplified Career Topic Detail", False, 
                              "No scenarios found for career topic", data)
                return False
            
            # Verify tiers array (should have starter, plus, pro)
            tiers = data.get("tiers", [])
            if len(tiers) != 3:
                self.log_result("Simplified Career Topic Detail", False, 
                              f"Expected 3 tiers, got {len(tiers)}", data)
                return False
            
            tier_levels = [tier.get("tier_level") for tier in tiers]
            expected_levels = ["starter", "plus", "pro"]
            if not all(level in tier_levels for level in expected_levels):
                self.log_result("Simplified Career Topic Detail", False, 
                              f"Missing tier levels. Expected {expected_levels}, got {tier_levels}", data)
                return False
            
            # Verify tools array
            tools = data.get("tools", [])
            if len(tools) == 0:
                self.log_result("Simplified Career Topic Detail", False, 
                              "No tools found for career topic", data)
                return False
            
            # Verify unlimited_conditions
            unlimited_conditions = data.get("unlimited_conditions")
            if not unlimited_conditions:
                self.log_result("Simplified Career Topic Detail", False, 
                              "Missing unlimited_conditions", data)
                return False
            
            self.log_result("Simplified Career Topic Detail", True, 
                          f"Career topic detail complete: {len(experts)} experts, {len(scenarios)} scenarios, {len(tiers)} tiers, {len(tools)} tools")
            return True
            
        except Exception as e:
            self.log_result("Simplified Career Topic Detail", False, f"Exception: {str(e)}")
            return False
    
    def test_simplified_experts_career(self):
        """Test GET /api/simplified/experts?topic_id=career - Should return career experts"""
        try:
            response = self.session.get(f"{BACKEND_URL}/simplified/experts", 
                                      params={"topic_id": "career"}, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Simplified Career Experts", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check response structure
            if not data.get("ok"):
                self.log_result("Simplified Career Experts", False, 
                              "Response ok field is not true", data)
                return False
            
            experts = data.get("experts", [])
            if len(experts) == 0:
                self.log_result("Simplified Career Experts", False, 
                              "No experts found for career topic", data)
                return False
            
            # Verify each expert has required fields
            required_fields = ["expert_id", "name", "modality", "modality_label", "topics", "best_for_tags"]
            for i, expert in enumerate(experts):
                missing_fields = [field for field in required_fields if field not in expert]
                if missing_fields:
                    self.log_result("Simplified Career Experts", False, 
                                  f"Expert {i} missing fields: {missing_fields}", expert)
                    return False
                
                # Verify expert serves career topic
                if "career" not in expert.get("topics", []):
                    self.log_result("Simplified Career Experts", False, 
                                  f"Expert {expert.get('name')} does not serve career topic", expert)
                    return False
            
            # Check catalog version
            if not data.get("catalog_version"):
                self.log_result("Simplified Career Experts", False, 
                              "Missing catalog_version", data)
                return False
            
            self.log_result("Simplified Career Experts", True, 
                          f"Found {len(experts)} career experts with all required fields")
            return True
            
        except Exception as e:
            self.log_result("Simplified Career Experts", False, f"Exception: {str(e)}")
            return False
    
    def test_simplified_tier_career_plus(self):
        """Test GET /api/simplified/tiers/career_plus - Should return career Plus tier details"""
        try:
            response = self.session.get(f"{BACKEND_URL}/simplified/tiers/career_plus", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Simplified Career Plus Tier", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check response structure
            if not data.get("ok"):
                self.log_result("Simplified Career Plus Tier", False, 
                              "Response ok field is not true", data)
                return False
            
            tier = data.get("tier")
            if not tier:
                self.log_result("Simplified Career Plus Tier", False, 
                              "No tier in response", data)
                return False
            
            # Check tier ID
            if tier.get("tier_id") != "career_plus":
                self.log_result("Simplified Career Plus Tier", False, 
                              f"Wrong tier ID: {tier.get('tier_id')}", tier)
                return False
            
            # Check tier level
            if tier.get("tier_level") != "plus":
                self.log_result("Simplified Career Plus Tier", False, 
                              f"Wrong tier level: {tier.get('tier_level')}", tier)
                return False
            
            # Check topic ID
            if tier.get("topic_id") != "career":
                self.log_result("Simplified Career Plus Tier", False, 
                              f"Wrong topic ID: {tier.get('topic_id')}", tier)
                return False
            
            # Check required fields
            required_fields = ["name", "price_inr", "validity_weeks", "access_policy", "features"]
            missing_fields = [field for field in required_fields if field not in tier]
            if missing_fields:
                self.log_result("Simplified Career Plus Tier", False, 
                              f"Missing fields: {missing_fields}", tier)
                return False
            
            # Check access policy
            access_policy = tier.get("access_policy")
            if not access_policy:
                self.log_result("Simplified Career Plus Tier", False, 
                              "Missing access_policy", tier)
                return False
            
            # Verify Plus tier features (should have calls enabled)
            if not access_policy.get("calls_enabled"):
                self.log_result("Simplified Career Plus Tier", False, 
                              "Plus tier should have calls enabled", access_policy)
                return False
            
            if access_policy.get("calls_per_month", 0) <= 0:
                self.log_result("Simplified Career Plus Tier", False, 
                              "Plus tier should have calls per month > 0", access_policy)
                return False
            
            # Check catalog version
            if not data.get("catalog_version"):
                self.log_result("Simplified Career Plus Tier", False, 
                              "Missing catalog_version", data)
                return False
            
            self.log_result("Simplified Career Plus Tier", True, 
                          f"Career Plus tier verified: ₹{tier.get('price_inr')}, {tier.get('validity_weeks')} weeks, {access_policy.get('calls_per_month')} calls/month")
            return True
            
        except Exception as e:
            self.log_result("Simplified Career Plus Tier", False, f"Exception: {str(e)}")
            return False
    
    def test_simplified_user_state_new_user(self):
        """Test GET /api/simplified/user/state - Should return user state (new user without auth)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/simplified/user/state", timeout=10)
            
            if response.status_code != 200:
                self.log_result("Simplified User State (New User)", False, 
                              f"HTTP {response.status_code}", response.text)
                return False
            
            data = response.json()
            
            # Check response structure
            if not data.get("ok"):
                self.log_result("Simplified User State (New User)", False, 
                              "Response ok field is not true", data)
                return False
            
            user_state = data.get("user_state")
            if not user_state:
                self.log_result("Simplified User State (New User)", False, 
                              "No user_state in response", data)
                return False
            
            # Check required fields for new user
            required_fields = ["user_id", "is_new_user", "has_active_plan", "active_plans", "recent_expert_threads", "additional_topic_passes"]
            missing_fields = [field for field in required_fields if field not in user_state]
            if missing_fields:
                self.log_result("Simplified User State (New User)", False, 
                              f"Missing fields: {missing_fields}", user_state)
                return False
            
            # Verify new user state
            if not user_state.get("is_new_user"):
                self.log_result("Simplified User State (New User)", False, 
                              "Expected is_new_user to be true for unauthenticated user", user_state)
                return False
            
            if user_state.get("has_active_plan"):
                self.log_result("Simplified User State (New User)", False, 
                              "Expected has_active_plan to be false for new user", user_state)
                return False
            
            # Check arrays are empty for new user
            if len(user_state.get("active_plans", [])) > 0:
                self.log_result("Simplified User State (New User)", False, 
                              "Expected empty active_plans for new user", user_state)
                return False
            
            if len(user_state.get("recent_expert_threads", [])) > 0:
                self.log_result("Simplified User State (New User)", False, 
                              "Expected empty recent_expert_threads for new user", user_state)
                return False
            
            if len(user_state.get("additional_topic_passes", [])) > 0:
                self.log_result("Simplified User State (New User)", False, 
                              "Expected empty additional_topic_passes for new user", user_state)
                return False
            
            self.log_result("Simplified User State (New User)", True, 
                          f"New user state verified: user_id={user_state.get('user_id')}, is_new_user=true")
            return True
            
        except Exception as e:
            self.log_result("Simplified User State (New User)", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all NIRO Simplified V1 tests in sequence"""
        print("🚀 Starting NIRO Simplified V1 API Testing...")
        print("=" * 60)
        
        tests = [
            self.test_simplified_topics_list,
            self.test_simplified_topic_career_detail,
            self.test_simplified_experts_career,
            self.test_simplified_tier_career_plus,
            self.test_simplified_user_state_new_user
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
        print(f"🏁 NIRO Simplified V1 Testing Complete: {passed} passed, {failed} failed")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['message']}")
        
        return failed == 0


if __name__ == "__main__":
    tester = NiroSimplifiedTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All NIRO Simplified V1 tests passed!")
        exit(0)
    else:
        print("\n💥 Some NIRO Simplified V1 tests failed!")
        exit(1)