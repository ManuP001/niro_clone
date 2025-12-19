#!/usr/bin/env python3
"""
Onboarding Flow Test
Tests the complete onboarding flow: OTP auth -> Profile creation -> Profile retrieval
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, '/Users/sharadharjai/Documents/GitHub/niro-ai-launch')

from backend.auth.auth_service import get_auth_service
from backend.auth.store import get_user_store_instance, get_profile_store_instance


class OnboardingFlowTester:
    def __init__(self):
        self.test_results = []
        self.auth_service = get_auth_service()
        self.user_store = get_user_store_instance()
        self.profile_store = get_profile_store_instance()
        
    def log_result(self, test_name, success, message):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status} {test_name}")
        print(f"   {message}")
        return success
    
    def test_1_complete_otp_flow(self):
        """Test 1: Complete OTP authentication flow"""
        test_name = "Test 1: Complete OTP Auth Flow"
        try:
            test_identifier = "onboarding_test_1@example.com"
            
            # Request OTP
            success, expires_in = self.auth_service.request_otp(test_identifier)
            if not success:
                return self.log_result(test_name, False, "Failed to request OTP")
            
            # Get OTP from manager
            from backend.auth.otp_manager import get_otp_manager
            otp_manager = get_otp_manager()
            otp = otp_manager.otps[test_identifier]['otp']
            
            # Verify OTP
            result = self.auth_service.verify_otp(test_identifier, otp)
            if not result:
                return self.log_result(test_name, False, "Failed to verify OTP")
            
            token, user_id = result
            return self.log_result(
                test_name,
                True,
                f"OTP auth complete. User ID: {user_id}, Token: {token[:20]}..."
            )
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_2_save_profile_with_all_fields(self):
        """Test 2: Save user profile with all required fields"""
        test_name = "Test 2: Save Profile with All Fields"
        try:
            test_identifier = "onboarding_test_2@example.com"
            
            # Step 1: Auth
            success, _ = self.auth_service.request_otp(test_identifier)
            if not success:
                return self.log_result(test_name, False, "Failed to request OTP")
            
            from backend.auth.otp_manager import get_otp_manager
            otp_manager = get_otp_manager()
            otp = otp_manager.otps[test_identifier]['otp']
            
            result = self.auth_service.verify_otp(test_identifier, otp)
            if not result:
                return self.log_result(test_name, False, "Failed to verify OTP")
            
            token, user_id = result
            
            # Step 2: Save profile
            profile_data = {
                'name': 'John Doe',
                'dob': '1990-05-15',
                'tob': '14:30',
                'location': 'New York, USA'
            }
            
            success = self.auth_service.save_profile(user_id, profile_data)
            if not success:
                return self.log_result(test_name, False, "Failed to save profile")
            
            return self.log_result(
                test_name,
                True,
                f"Profile saved. Name: {profile_data['name']}, DOB: {profile_data['dob']}"
            )
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_3_retrieve_saved_profile(self):
        """Test 3: Retrieve previously saved profile"""
        test_name = "Test 3: Retrieve Saved Profile"
        try:
            test_identifier = "onboarding_test_3@example.com"
            
            # Auth
            self.auth_service.request_otp(test_identifier)
            from backend.auth.otp_manager import get_otp_manager
            otp_manager = get_otp_manager()
            otp = otp_manager.otps[test_identifier]['otp']
            result = self.auth_service.verify_otp(test_identifier, otp)
            token, user_id = result
            
            # Save profile
            profile_data = {
                'name': 'Jane Smith',
                'dob': '1992-03-20',
                'tob': '09:45',
                'location': 'San Francisco, California'
            }
            
            self.auth_service.save_profile(user_id, profile_data)
            
            # Retrieve profile
            retrieved_profile = self.auth_service.get_profile(user_id)
            
            if not retrieved_profile:
                return self.log_result(test_name, False, "Failed to retrieve profile")
            
            # Validate all fields
            for field in ['name', 'dob', 'tob', 'location']:
                if retrieved_profile.get(field) != profile_data[field]:
                    return self.log_result(
                        test_name, False,
                        f"Profile mismatch: {field} = {retrieved_profile.get(field)} != {profile_data[field]}"
                    )
            
            return self.log_result(
                test_name,
                True,
                f"Profile retrieved successfully. Name: {retrieved_profile['name']}"
            )
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_4_profile_missing_fields(self):
        """Test 4: Reject profile with missing fields"""
        test_name = "Test 4: Reject Profile with Missing Fields"
        try:
            test_identifier = "onboarding_test_4@example.com"
            
            # Auth
            self.auth_service.request_otp(test_identifier)
            from backend.auth.otp_manager import get_otp_manager
            otp_manager = get_otp_manager()
            otp = otp_manager.otps[test_identifier]['otp']
            result = self.auth_service.verify_otp(test_identifier, otp)
            token, user_id = result
            
            # Try to save profile with missing 'tob' field
            incomplete_profile = {
                'name': 'Bob Johnson',
                'dob': '1988-07-10',
                'location': 'London, UK'
                # Missing 'tob'
            }
            
            success = self.auth_service.save_profile(user_id, incomplete_profile)
            
            if success:
                return self.log_result(test_name, False, "Should reject profile with missing fields")
            
            return self.log_result(test_name, True, "Correctly rejected incomplete profile")
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_5_profile_date_formats(self):
        """Test 5: Profile with various date formats"""
        test_name = "Test 5: Profile Date Format Handling"
        try:
            test_identifier = "onboarding_test_5@example.com"
            
            # Auth
            self.auth_service.request_otp(test_identifier)
            from backend.auth.otp_manager import get_otp_manager
            otp_manager = get_otp_manager()
            otp = otp_manager.otps[test_identifier]['otp']
            result = self.auth_service.verify_otp(test_identifier, otp)
            token, user_id = result
            
            # Save profile with standard ISO format
            profile_data = {
                'name': 'Alice Cooper',
                'dob': '1985-12-25',  # YYYY-MM-DD format
                'tob': '18:30',       # HH:MM format
                'location': 'Sydney, Australia'
            }
            
            success = self.auth_service.save_profile(user_id, profile_data)
            
            if not success:
                return self.log_result(test_name, False, "Failed to save profile with ISO dates")
            
            # Retrieve and verify
            retrieved = self.auth_service.get_profile(user_id)
            if retrieved['dob'] != '1985-12-25':
                return self.log_result(test_name, False, f"DOB format issue: {retrieved['dob']}")
            
            if retrieved['tob'] != '18:30':
                return self.log_result(test_name, False, f"TOB format issue: {retrieved['tob']}")
            
            return self.log_result(test_name, True, "Date formats handled correctly")
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_6_end_to_end_onboarding(self):
        """Test 6: Complete end-to-end onboarding flow"""
        test_name = "Test 6: End-to-End Onboarding"
        try:
            test_identifier = "onboarding_test_6@example.com"
            
            # Step 1: Request OTP
            success, expires_in = self.auth_service.request_otp(test_identifier)
            if not success or expires_in <= 0:
                return self.log_result(test_name, False, "OTP request failed")
            
            # Step 2: Verify OTP and get token
            from backend.auth.otp_manager import get_otp_manager
            otp_manager = get_otp_manager()
            otp = otp_manager.otps[test_identifier]['otp']
            
            result = self.auth_service.verify_otp(test_identifier, otp)
            if not result:
                return self.log_result(test_name, False, "OTP verification failed")
            
            token, user_id = result
            
            # Step 3: Complete profile
            profile_data = {
                'name': 'Sharad Arjai',
                'dob': '1986-01-24',
                'tob': '06:32',
                'location': 'Rohtak, Haryana'
            }
            
            success = self.auth_service.save_profile(user_id, profile_data)
            if not success:
                return self.log_result(test_name, False, "Profile save failed")
            
            # Step 4: Verify token is valid
            payload = self.auth_service.verify_token(token)
            if not payload or payload.get('user_id') != user_id:
                return self.log_result(test_name, False, "Token verification failed")
            
            # Step 5: Verify profile is retrievable
            profile = self.auth_service.get_profile(user_id)
            if not profile:
                return self.log_result(test_name, False, "Profile retrieval failed")
            
            return self.log_result(
                test_name,
                True,
                f"✅ E2E Complete: {profile_data['name']}, DOB: {profile_data['dob']}, Location: {profile_data['location']}"
            )
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("ONBOARDING FLOW TEST SUITE")
        print("="*70)
        
        tests = [
            self.test_1_complete_otp_flow,
            self.test_2_save_profile_with_all_fields,
            self.test_3_retrieve_saved_profile,
            self.test_4_profile_missing_fields,
            self.test_5_profile_date_formats,
            self.test_6_end_to_end_onboarding,
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                logger.error(f"Test {test_func.__name__} crashed: {e}")
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {total - passed} ❌")
        
        if total - passed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "="*70)
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("✅ ALL TESTS PASSED - ONBOARDING FLOW IS WORKING!")
        else:
            print("❌ SOME TESTS FAILED - CHECK ONBOARDING FLOW")
        
        print("="*70 + "\n")
        
        return passed == total


if __name__ == "__main__":
    tester = OnboardingFlowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
