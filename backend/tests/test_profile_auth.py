"""
Backend API Tests for Profile and Auth Endpoints
Tests the V6 onboarding flow: Auth -> Profile creation/retrieval
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthEndpoint:
    """Health check endpoint tests - run first"""
    
    def test_health_check(self):
        """Verify backend is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
        print(f"✓ Health check passed: {data}")


class TestAuthIdentify:
    """POST /api/auth/identify - User authentication/creation"""
    
    def test_identify_new_user(self):
        """Should create new user and return JWT token"""
        test_email = f"TEST_newuser_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(
            f"{BASE_URL}/api/auth/identify",
            json={"identifier": test_email},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data.get('ok') == True
        assert 'token' in data
        assert 'user_id' in data
        assert isinstance(data['token'], str)
        assert len(data['token']) > 0
        print(f"✓ New user created: {test_email}, user_id={data['user_id']}")
    
    def test_identify_existing_user(self):
        """Should return same user_id for existing user"""
        test_email = f"TEST_existing_{uuid.uuid4().hex[:8]}@example.com"
        
        # First call - create user
        response1 = requests.post(
            f"{BASE_URL}/api/auth/identify",
            json={"identifier": test_email},
            headers={"Content-Type": "application/json"}
        )
        assert response1.status_code == 200
        user_id_1 = response1.json()['user_id']
        
        # Second call - should return same user
        response2 = requests.post(
            f"{BASE_URL}/api/auth/identify",
            json={"identifier": test_email},
            headers={"Content-Type": "application/json"}
        )
        assert response2.status_code == 200
        user_id_2 = response2.json()['user_id']
        
        assert user_id_1 == user_id_2
        print(f"✓ Existing user returned same user_id: {user_id_1}")
    
    def test_identify_missing_identifier(self):
        """Should return 422 for missing identifier"""
        response = requests.post(
            f"{BASE_URL}/api/auth/identify",
            json={},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        print("✓ Missing identifier returns 422")


class TestProfileEndpoints:
    """Profile CRUD tests - POST and GET /api/profile/"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for profile tests"""
        test_email = f"TEST_profile_{uuid.uuid4().hex[:8]}@example.com"
        response = requests.post(
            f"{BASE_URL}/api/auth/identify",
            json={"identifier": test_email},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        return response.json()['token']
    
    def test_create_profile_success(self, auth_token):
        """POST /api/profile/ - Should save user profile with all fields"""
        profile_data = {
            "name": "TEST_User Profile",
            "dob": "1990-05-15",
            "tob": "10:30",
            "location": "Mumbai, India",
            "gender": "male"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/profile/",
            json=profile_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        assert data.get('profile_complete') == True
        print(f"✓ Profile created successfully")
    
    def test_get_profile_after_create(self, auth_token):
        """GET /api/profile/ - Should retrieve saved profile"""
        # First create profile
        profile_data = {
            "name": "TEST_Get Profile User",
            "dob": "1985-12-25",
            "tob": "06:00",
            "location": "Delhi, India",
            "gender": "female"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/profile/",
            json=profile_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        assert create_response.status_code == 200
        
        # Now retrieve profile
        get_response = requests.get(
            f"{BASE_URL}/api/profile/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data.get('ok') == True
        assert 'profile' in data
        
        profile = data['profile']
        assert profile['name'] == "TEST_Get Profile User"
        assert profile['dob'] == "1985-12-25"
        assert profile['tob'] == "06:00"
        assert profile['location'] == "Delhi, India"
        print(f"✓ Profile retrieved successfully: {profile['name']}")
    
    def test_create_profile_without_auth(self):
        """POST /api/profile/ - Should return 401 without auth token"""
        response = requests.post(
            f"{BASE_URL}/api/profile/",
            json={"name": "Test", "dob": "1990-01-01", "tob": "12:00", "location": "Test"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401
        print("✓ Profile creation without auth returns 401")
    
    def test_get_profile_without_auth(self):
        """GET /api/profile/ - Should return 401 without auth token"""
        response = requests.get(f"{BASE_URL}/api/profile/")
        assert response.status_code == 401
        print("✓ Profile retrieval without auth returns 401")
    
    def test_create_profile_invalid_date_format(self, auth_token):
        """POST /api/profile/ - Should return 400 for invalid date format"""
        profile_data = {
            "name": "TEST_Invalid Date",
            "dob": "invalid-date",
            "tob": "10:30",
            "location": "Mumbai, India"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/profile/",
            json=profile_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        print("✓ Invalid date format returns 400")
    
    def test_create_profile_invalid_time_format(self, auth_token):
        """POST /api/profile/ - Should return 400 for invalid time format"""
        profile_data = {
            "name": "TEST_Invalid Time",
            "dob": "1990-05-15",
            "tob": "invalid-time",
            "location": "Mumbai, India"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/profile/",
            json=profile_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        print("✓ Invalid time format returns 400")
    
    def test_update_profile(self, auth_token):
        """POST /api/profile/ - Should update existing profile"""
        # Create initial profile
        initial_data = {
            "name": "TEST_Initial Name",
            "dob": "1990-01-01",
            "tob": "12:00",
            "location": "Initial City"
        }
        
        requests.post(
            f"{BASE_URL}/api/profile/",
            json=initial_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        # Update profile
        updated_data = {
            "name": "TEST_Updated Name",
            "dob": "1990-01-01",
            "tob": "12:00",
            "location": "Updated City"
        }
        
        update_response = requests.post(
            f"{BASE_URL}/api/profile/",
            json=updated_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        assert update_response.status_code == 200
        
        # Verify update persisted
        get_response = requests.get(
            f"{BASE_URL}/api/profile/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        profile = get_response.json()['profile']
        assert profile['name'] == "TEST_Updated Name"
        assert profile['location'] == "Updated City"
        print("✓ Profile update persisted correctly")


class TestAuthMe:
    """GET /api/auth/me - Current user info"""
    
    def test_get_current_user(self):
        """Should return current user info with valid token"""
        # First get a token
        test_email = f"TEST_me_{uuid.uuid4().hex[:8]}@example.com"
        auth_response = requests.post(
            f"{BASE_URL}/api/auth/identify",
            json={"identifier": test_email},
            headers={"Content-Type": "application/json"}
        )
        token = auth_response.json()['token']
        user_id = auth_response.json()['user_id']
        
        # Get current user
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('ok') == True
        assert 'user' in data
        assert data['user']['id'] == user_id
        print(f"✓ Current user retrieved: {data['user']['id']}")
    
    def test_get_current_user_without_auth(self):
        """Should return 401 without auth token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ Get current user without auth returns 401")
    
    def test_get_current_user_invalid_token(self):
        """Should return 401 with invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401
        print("✓ Get current user with invalid token returns 401")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
