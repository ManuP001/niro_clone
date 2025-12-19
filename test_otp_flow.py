#!/usr/bin/env python3
"""
OTP Login Flow Test
Tests the complete OTP authentication flow: request OTP -> verify OTP -> get token
"""

import sys
import logging
from datetime import datetime

# Configure logging to show debug info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, '/Users/sharadharjai/Documents/GitHub/niro-ai-launch')

from backend.auth.otp_manager import get_otp_manager
from backend.auth.auth_service import get_auth_service
from backend.auth.store import get_user_store_instance, get_profile_store_instance


class OTPFlowTester:
    def __init__(self):
        self.test_results = []
        self.otp_manager = get_otp_manager()
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
    
    def test_1_request_otp(self):
        """Test 1: Request OTP for an identifier"""
        test_name = "Test 1: Request OTP"
        try:
            test_identifier = "test_user@example.com"
            success, expires_in = self.auth_service.request_otp(test_identifier)
            
            if not success:
                return self.log_result(test_name, False, "request_otp returned False")
            
            if expires_in <= 0:
                return self.log_result(test_name, False, f"Invalid expires_in value: {expires_in}")
            
            # Verify user was created
            user = self.user_store.get_user_by_identifier(test_identifier)
            if not user:
                return self.log_result(test_name, False, "User was not created in store")
            
            # Verify OTP was generated in manager
            if test_identifier not in self.otp_manager.otps:
                return self.log_result(test_name, False, "OTP was not stored in manager")
            
            return self.log_result(
                test_name, 
                True, 
                f"OTP requested successfully. Expires in: {expires_in}s, User ID: {user['id']}"
            )
            
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_2_verify_otp_success(self):
        """Test 2: Verify OTP with correct code"""
        test_name = "Test 2: Verify OTP - Success Case"
        try:
            test_identifier = "test_user2@example.com"
            
            # Step 1: Request OTP
            success, _ = self.auth_service.request_otp(test_identifier)
            if not success:
                return self.log_result(test_name, False, "Failed to request OTP")
            
            # Step 2: Get the OTP from manager (simulating reading from logs/email)
            otp_record = self.otp_manager.otps.get(test_identifier)
            if not otp_record:
                return self.log_result(test_name, False, "OTP not found in manager")
            
            actual_otp = otp_record['otp']
            
            # Step 3: Verify OTP
            result = self.auth_service.verify_otp(test_identifier, actual_otp)
            if not result:
                return self.log_result(test_name, False, "verify_otp returned None")
            
            token, user_id = result
            
            if not token:
                return self.log_result(test_name, False, "No JWT token returned")
            
            if not user_id:
                return self.log_result(test_name, False, "No user_id returned")
            
            # Step 4: Verify token is valid
            auth_payload = self.auth_service.verify_token(token)
            if not auth_payload:
                return self.log_result(test_name, False, "JWT token verification failed")
            
            if auth_payload.get('user_id') != user_id:
                return self.log_result(test_name, False, "user_id mismatch in token payload")
            
            return self.log_result(
                test_name,
                True,
                f"OTP verified successfully. User ID: {user_id}, Token: {token[:20]}..."
            )
            
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_3_verify_otp_failure_wrong_code(self):
        """Test 3: Verify OTP with incorrect code"""
        test_name = "Test 3: Verify OTP - Wrong Code"
        try:
            test_identifier = "test_user3@example.com"
            
            # Request OTP
            success, _ = self.auth_service.request_otp(test_identifier)
            if not success:
                return self.log_result(test_name, False, "Failed to request OTP")
            
            # Try with wrong OTP
            result = self.auth_service.verify_otp(test_identifier, "000000")
            
            if result is not None:
                return self.log_result(test_name, False, "verify_otp should return None for wrong OTP")
            
            return self.log_result(test_name, True, "Correctly rejected wrong OTP")
            
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_4_verify_otp_failure_expired(self):
        """Test 4: Verify OTP after expiration"""
        test_name = "Test 4: Verify OTP - Expired OTP"
        try:
            test_identifier = "test_user4@example.com"
            
            # Request OTP
            success, _ = self.auth_service.request_otp(test_identifier)
            if not success:
                return self.log_result(test_name, False, "Failed to request OTP")
            
            # Get OTP and manually expire it
            otp_record = self.otp_manager.otps[test_identifier]
            original_created_at = otp_record['created_at']
            
            # Set created_at to far in the past (2 hours ago)
            from datetime import timedelta
            otp_record['created_at'] = original_created_at - timedelta(hours=2)
            
            # Try to verify expired OTP
            result = self.auth_service.verify_otp(test_identifier, otp_record['otp'])
            
            if result is not None:
                return self.log_result(test_name, False, "verify_otp should return None for expired OTP")
            
            return self.log_result(test_name, True, "Correctly rejected expired OTP")
            
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_5_otp_cleared_after_verification(self):
        """Test 5: Verify OTP is cleared after successful verification"""
        test_name = "Test 5: OTP Cleared After Verification"
        try:
            test_identifier = "test_user5@example.com"
            
            # Request and verify OTP
            self.auth_service.request_otp(test_identifier)
            otp = self.otp_manager.otps[test_identifier]['otp']
            
            # Verify
            result = self.auth_service.verify_otp(test_identifier, otp)
            if not result:
                return self.log_result(test_name, False, "OTP verification failed")
            
            # Check if OTP was cleared
            if test_identifier in self.otp_manager.otps:
                return self.log_result(test_name, False, "OTP was not cleared after verification")
            
            return self.log_result(test_name, True, "OTP correctly cleared after verification")
            
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_6_max_attempts(self):
        """Test 6: Max attempts limit"""
        test_name = "Test 6: Max Attempts Limit"
        try:
            test_identifier = "test_user6@example.com"
            
            # Request OTP
            self.auth_service.request_otp(test_identifier)
            
            # Try to verify with wrong OTP 5 times
            for i in range(5):
                wrong_otp = "999999"
                result = self.auth_service.verify_otp(test_identifier, wrong_otp)
                if result is not None:
                    return self.log_result(test_name, False, f"Wrong OTP {i+1} should fail")
            
            # Verify the OTP is now cleared
            if test_identifier in self.otp_manager.otps:
                return self.log_result(test_name, False, "OTP not cleared after max attempts")
            
            return self.log_result(test_name, True, "Correctly locked OTP after max attempts")
            
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def test_7_same_user_multiple_otps(self):
        """Test 7: Requesting OTP multiple times creates a new OTP"""
        test_name = "Test 7: Multiple OTP Requests"
        try:
            test_identifier = "test_user7@example.com"
            
            # Request OTP first time
            self.auth_service.request_otp(test_identifier)
            first_otp = self.otp_manager.otps[test_identifier]['otp']
            
            # Request OTP second time (should generate new OTP)
            self.auth_service.request_otp(test_identifier)
            second_otp = self.otp_manager.otps[test_identifier]['otp']
            
            # OTPs might be same by chance, but attempts should reset
            # Try with first OTP - should fail if second was generated
            self.otp_manager.otps[test_identifier]['attempts'] = 0  # Reset for clean test
            result = self.auth_service.verify_otp(test_identifier, first_otp)
            
            # If first_otp != second_otp, verify_otp should fail
            if first_otp != second_otp and result is not None:
                return self.log_result(test_name, False, "First OTP should fail if different OTP was generated")
            
            return self.log_result(test_name, True, f"Multiple OTP requests handled. First: {first_otp}, Second: {second_otp}")
            
        except Exception as e:
            return self.log_result(test_name, False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("OTP LOGIN FLOW TEST SUITE")
        print("="*60)
        
        tests = [
            self.test_1_request_otp,
            self.test_2_verify_otp_success,
            self.test_3_verify_otp_failure_wrong_code,
            self.test_4_verify_otp_failure_expired,
            self.test_5_otp_cleared_after_verification,
            self.test_6_max_attempts,
            self.test_7_same_user_multiple_otps,
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                logger.error(f"Test {test_func.__name__} crashed: {e}")
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
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
        
        print("\n" + "="*60)
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("✅ ALL TESTS PASSED - OTP LOGIN FLOW IS WORKING!")
        else:
            print("❌ SOME TESTS FAILED - OTP LOGIN FLOW HAS ISSUES")
        
        print("="*60 + "\n")
        
        return passed == total


if __name__ == "__main__":
    tester = OTPFlowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
