#!/usr/bin/env python3
"""
Test script for onboarding changes:
1. City autocomplete
2. Always-on user context in chat
3. Personalized welcome message

Run with: VEDIC_API_KEY="..." python3 test_onboarding_enhancements.py
"""

import sys
import requests
import json
from datetime import datetime

sys.path.insert(0, '/Users/sharadharjai/Documents/GitHub/niro-ai-launch')

BACKEND_URL = "http://localhost:8000"

class OnboardingEnhancementsTest:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.results = []
    
    def log_result(self, test_name, success, message):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.results.append({"test": test_name, "success": success, "message": message})
        return success
    
    def test_1_city_autocomplete(self):
        """Test Goal 1: City autocomplete API returns results"""
        test_name = "Goal 1: City Autocomplete"
        try:
            # Test autocomplete endpoint
            response = requests.get(f"{BACKEND_URL}/api/places/search?q=Rohtak")
            
            if response.status_code != 200:
                return self.log_result(test_name, False, f"HTTP {response.status_code}")
            
            data = response.json()
            places = data.get('places', [])
            
            if not places:
                return self.log_result(test_name, False, "No places returned")
            
            place = places[0]
            required_fields = ['label', 'place_id', 'lat', 'lon', 'tz']
            if not all(field in place for field in required_fields):
                return self.log_result(test_name, False, f"Missing fields: {required_fields}")
            
            return self.log_result(
                test_name, 
                True, 
                f"✓ Autocomplete works. Found: {place['label']} ({place['lat']}, {place['lon']})"
            )
        except Exception as e:
            return self.log_result(test_name, False, str(e))
    
    def test_2_profile_with_coordinates(self):
        """Test Goal 2: Profile saves with lat/lon/tz"""
        test_name = "Goal 2: Profile with Coordinates"
        try:
            # Step 1: Auth
            from backend.auth.auth_service import get_auth_service
            from backend.auth.otp_manager import get_otp_manager
            
            auth_service = get_auth_service()
            test_identifier = "onboard_test@example.com"
            
            auth_service.request_otp(test_identifier)
            otp_manager = get_otp_manager()
            otp = otp_manager.otps[test_identifier]['otp']
            
            result = auth_service.verify_otp(test_identifier, otp)
            if not result:
                return self.log_result(test_name, False, "OTP verification failed")
            
            token, user_id = result
            self.token = token
            self.user_id = user_id
            
            # Step 2: Save profile with coordinates
            profile_data = {
                'name': 'Test User',
                'dob': '1990-05-15',
                'tob': '14:30',
                'location': 'Rohtak, Haryana, India',
                'birth_place_lat': 28.8955,
                'birth_place_lon': 76.5660,
                'birth_place_tz': 5.5,
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/profile/",
                headers={'Authorization': f'Bearer {token}'},
                json=profile_data
            )
            
            if response.status_code != 200:
                return self.log_result(test_name, False, f"Profile save failed: {response.text}")
            
            # Verify profile was saved with coordinates
            profile = auth_service.get_profile(user_id)
            if not profile:
                return self.log_result(test_name, False, "Profile not retrievable")
            
            if profile.get('birth_place_lat') != 28.8955:
                return self.log_result(test_name, False, f"Latitude not saved: {profile}")
            
            return self.log_result(test_name, True, f"✓ Profile saved with lat/lon/tz")
        except Exception as e:
            return self.log_result(test_name, False, str(e))
    
    def test_3_welcome_message_personalized(self):
        """Test Goal 3: Welcome message uses saved profile"""
        test_name = "Goal 3: Personalized Welcome Message"
        try:
            if not self.token:
                return self.log_result(test_name, False, "No token from previous test")
            
            # Get welcome message
            response = requests.post(
                f"{BACKEND_URL}/api/profile/welcome",
                headers={'Authorization': f'Bearer {self.token}'}
            )
            
            if response.status_code != 200:
                return self.log_result(test_name, False, f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            if not data.get('ok'):
                return self.log_result(test_name, False, "Response not OK")
            
            welcome = data.get('welcome', {})
            required_fields = ['title', 'subtitle', 'bullets', 'prompt']
            if not all(field in welcome for field in required_fields):
                return self.log_result(test_name, False, f"Missing fields: {required_fields}")
            
            # Verify it has name and 3 strengths
            title = welcome.get('title', '')
            bullets = welcome.get('bullets', [])
            
            if 'Test User' not in title:
                return self.log_result(test_name, False, f"Name not in title: {title}")
            
            if len(bullets) != 3:
                return self.log_result(test_name, False, f"Expected 3 bullets, got {len(bullets)}")
            
            return self.log_result(
                test_name,
                True,
                f"✓ Welcome personalized. Title: '{title[:50]}...', Strengths: {bullets}"
            )
        except Exception as e:
            return self.log_result(test_name, False, str(e))
    
    def test_4_chat_uses_profile_context(self):
        """Test Goal 2: Chat doesn't ask for birth details when profile exists"""
        test_name = "Goal 2: Chat Uses Profile Context"
        try:
            if not self.token:
                return self.log_result(test_name, False, "No token from previous test")
            
            # Send chat message with profile context
            chat_payload = {
                "sessionId": f"test-session-{datetime.now().timestamp()}",
                "message": "Tell me about my career",
                "actionId": None
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/chat",
                headers={'Authorization': f'Bearer {self.token}'},
                json=chat_payload
            )
            
            if response.status_code != 200:
                return self.log_result(test_name, False, f"HTTP {response.status_code}: {response.text}")
            
            data = response.json()
            
            # Verify response has required fields
            if 'reply' not in data or 'mode' not in data:
                return self.log_result(test_name, False, f"Missing fields in response: {data}")
            
            # Check that mode is not NEED_BIRTH_DETAILS (since we have a complete profile)
            mode = data.get('mode', '')
            if mode == 'NEED_BIRTH_DETAILS':
                return self.log_result(
                    test_name, 
                    False, 
                    "Chat still asking for birth details even though profile is complete"
                )
            
            return self.log_result(
                test_name,
                True,
                f"✓ Chat proceeded to {mode} mode without asking for birth details"
            )
        except Exception as e:
            return self.log_result(test_name, False, str(e))
    
    def test_5_integration_flow(self):
        """Test full integration: Onboarding → Welcome → Chat"""
        test_name = "Integration: Onboarding → Welcome → Chat"
        try:
            # This combines all previous tests in sequence
            # If all previous tests passed, this should pass too
            
            all_passed = all(r['success'] for r in self.results)
            if not all_passed:
                failed = [r['test'] for r in self.results if not r['success']]
                return self.log_result(test_name, False, f"Some tests failed: {failed}")
            
            return self.log_result(test_name, True, "✓ Full integration working end-to-end")
        except Exception as e:
            return self.log_result(test_name, False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("ONBOARDING ENHANCEMENTS TEST SUITE")
        print("=" * 80)
        print()
        
        self.test_1_city_autocomplete()
        self.test_2_profile_with_coordinates()
        self.test_3_welcome_message_personalized()
        self.test_4_chat_uses_profile_context()
        self.test_5_integration_flow()
        
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for r in self.results if r['success'])
        total = len(self.results)
        
        print(f"Passed: {passed}/{total}")
        
        if passed == total:
            print("✅ All tests PASSED!")
        else:
            print("\n❌ Failed tests:")
            for r in self.results:
                if not r['success']:
                    print(f"  - {r['test']}: {r['message']}")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = OnboardingEnhancementsTest()
    tester.run_all_tests()
