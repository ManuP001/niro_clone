"""
Bug Fix Tests - Iteration 14

Tests for 3 P0 bug fixes:
1. Export CSV buttons (users & orders) - now use fetch with X-Admin-Token instead of window.open()
2. Checkout back button - preserves previous screen context
3. New admin experts visibility - public API merges admin_experts DB collection

Admin credentials: NiroAdmin / NewAdmin@123
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_USERNAME = "NiroAdmin"
ADMIN_PASSWORD = "NewAdmin@123"


class TestAdminAuth:
    """Test admin authentication for export tests"""
    
    def test_admin_login(self):
        """Login to admin and get token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert data.get("ok") == True
        assert "token" in data
        print(f"✅ Admin login successful, token: {data['token'][:20]}...")
        return data["token"]


class TestExportCSVFix:
    """Bug Fix 1: Export CSV buttons should work with X-Admin-Token header"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_export_users_csv_with_token(self, admin_token):
        """Test /api/admin/export/users with X-Admin-Token header"""
        response = requests.get(
            f"{BASE_URL}/api/admin/export/users",
            headers={"X-Admin-Token": admin_token}
        )
        assert response.status_code == 200, f"Export users failed: {response.status_code} - {response.text}"
        
        # Verify it's a CSV response
        content_type = response.headers.get("content-type", "")
        assert "text/csv" in content_type, f"Expected CSV, got {content_type}"
        
        # Verify it has content-disposition for download
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp, f"Missing attachment header: {content_disp}"
        assert "niro_users_" in content_disp, f"Missing filename: {content_disp}"
        
        # Verify CSV has data
        csv_content = response.text
        assert "user_id" in csv_content, "CSV missing user_id header"
        assert "email" in csv_content, "CSV missing email header"
        
        lines = csv_content.strip().split("\n")
        print(f"✅ Export users CSV working - {len(lines)} rows (including header)")
    
    def test_export_users_csv_without_token(self):
        """Test /api/admin/export/users without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/admin/export/users")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Export users without token correctly returns 401")
    
    def test_export_orders_csv_with_token(self, admin_token):
        """Test /api/admin/export/orders with X-Admin-Token header"""
        response = requests.get(
            f"{BASE_URL}/api/admin/export/orders",
            headers={"X-Admin-Token": admin_token}
        )
        assert response.status_code == 200, f"Export orders failed: {response.status_code} - {response.text}"
        
        # Verify it's a CSV response
        content_type = response.headers.get("content-type", "")
        assert "text/csv" in content_type, f"Expected CSV, got {content_type}"
        
        # Verify it has content-disposition for download
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp, f"Missing attachment header: {content_disp}"
        assert "niro_orders_" in content_disp, f"Missing filename: {content_disp}"
        
        # Verify CSV has data
        csv_content = response.text
        assert "order_id" in csv_content, "CSV missing order_id header"
        
        lines = csv_content.strip().split("\n")
        print(f"✅ Export orders CSV working - {len(lines)} rows (including header)")
    
    def test_export_orders_csv_without_token(self):
        """Test /api/admin/export/orders without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/admin/export/orders")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Export orders without token correctly returns 401")


class TestAdminExpertsVisibility:
    """Bug Fix 3: New admin experts should be visible in public /api/simplified/experts/all"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token for tests"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        return response.json()["token"]
    
    def test_create_admin_expert_and_verify_public_visibility(self, admin_token):
        """Create expert via admin, verify it appears in public /api/simplified/experts/all"""
        # Generate unique expert ID for this test
        test_expert_id = f"test_expert_{uuid.uuid4().hex[:8]}"
        
        # Step 1: Create new expert via admin API
        expert_data = {
            "expert_id": test_expert_id,
            "name": "Test Expert " + test_expert_id[-8:],
            "modality": "Vedic",
            "modality_label": "Vedic Astrology",
            "bio": "A test expert created via admin dashboard",
            "languages": "Hindi, English, Tamil",
            "years_experience": 10,
            "rating": 4.8,
            "total_consults": 150,
            "topics": ["love", "career"],
            "photo_url": "https://example.com/photo.jpg",
            "tags": ["love", "relationships", "career growth"],
            "active": True
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/admin/experts",
            json=expert_data,
            headers={"X-Admin-Token": admin_token}
        )
        assert create_response.status_code == 200, f"Create expert failed: {create_response.text}"
        created = create_response.json()
        assert created.get("ok") == True
        print(f"✅ Created admin expert: {test_expert_id}")
        
        # Step 2: Verify expert appears in public /api/simplified/experts/all
        public_response = requests.get(f"{BASE_URL}/api/simplified/experts/all")
        assert public_response.status_code == 200, f"Public API failed: {public_response.text}"
        
        public_data = public_response.json()
        assert public_data.get("ok") == True
        
        experts_list = public_data.get("experts", [])
        
        # Find our test expert
        test_expert = None
        for exp in experts_list:
            if exp.get("expert_id") == test_expert_id:
                test_expert = exp
                break
        
        assert test_expert is not None, f"Test expert {test_expert_id} not found in public API response. Total experts: {len(experts_list)}"
        
        # Step 3: Verify field normalization (_normalize_db_expert)
        # DB stores: bio -> should be short_bio in response
        # DB stores: languages (string) -> should be languages (array) in response
        # DB stores: tags -> should be best_for_tags in response
        # DB stores: years_experience -> should be experience_years in response
        # DB stores: total_consults -> should be total_consultations in response
        
        # Check languages is array (not string)
        languages = test_expert.get("languages", [])
        assert isinstance(languages, list), f"Expected languages array, got {type(languages)}: {languages}"
        assert "Hindi" in languages, f"Expected 'Hindi' in languages: {languages}"
        
        # Check best_for_tags is mapped from tags
        best_for_tags = test_expert.get("best_for_tags", [])
        assert isinstance(best_for_tags, list), f"Expected best_for_tags array, got {type(best_for_tags)}"
        
        # Check short_bio is mapped from bio
        short_bio = test_expert.get("short_bio", "")
        assert "test expert" in short_bio.lower(), f"Expected bio content in short_bio: {short_bio}"
        
        # Check experience_years is mapped from years_experience
        experience_years = test_expert.get("experience_years", 0)
        assert experience_years == 10, f"Expected experience_years=10, got {experience_years}"
        
        # Check total_consultations is mapped from total_consults
        total_consultations = test_expert.get("total_consultations", 0)
        assert total_consultations == 150 or test_expert.get("consultations", 0) == 150, \
            f"Expected total_consultations=150, got total_consultations={total_consultations}, consultations={test_expert.get('consultations')}"
        
        print(f"✅ Test expert {test_expert_id} visible in public API with correct field normalization")
        print(f"   - languages: {languages} (array)")
        print(f"   - best_for_tags: {best_for_tags}")
        print(f"   - short_bio: {short_bio[:50]}...")
        print(f"   - experience_years: {experience_years}")
        
        # Step 4: Cleanup - delete test expert
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/experts/{test_expert_id}?hard_delete=true",
            headers={"X-Admin-Token": admin_token}
        )
        assert delete_response.status_code == 200
        print(f"✅ Cleaned up test expert: {test_expert_id}")
    
    def test_experts_endpoint_also_includes_db_experts(self, admin_token):
        """Test /api/simplified/experts also queries admin_experts collection"""
        # Create a test expert
        test_expert_id = f"test_exp_{uuid.uuid4().hex[:8]}"
        
        expert_data = {
            "expert_id": test_expert_id,
            "name": "Test Filtered Expert",
            "modality": "Tarot",
            "modality_label": "Tarot Reading",
            "bio": "Test expert for filtering",
            "languages": "English",
            "years_experience": 5,
            "rating": 4.5,
            "total_consults": 50,
            "topics": ["love"],
            "tags": [],
            "active": True
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/admin/experts",
            json=expert_data,
            headers={"X-Admin-Token": admin_token}
        )
        assert create_response.status_code == 200
        
        # Check /api/simplified/experts (without /all)
        response = requests.get(f"{BASE_URL}/api/simplified/experts")
        assert response.status_code == 200
        
        data = response.json()
        experts = data.get("experts", [])
        
        found = any(e.get("expert_id") == test_expert_id for e in experts)
        assert found, f"Test expert {test_expert_id} not found in /api/simplified/experts"
        
        print(f"✅ /api/simplified/experts includes admin_experts DB (found {test_expert_id})")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/admin/experts/{test_expert_id}?hard_delete=true",
            headers={"X-Admin-Token": admin_token}
        )


class TestPublicAPIHealth:
    """Basic health checks for public APIs used in the app"""
    
    def test_homepage_data(self):
        """Test public homepage data endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print(f"✅ Homepage data API working - {len(data.get('data', []))} categories")
    
    def test_topics_endpoint(self):
        """Test topics endpoint"""
        response = requests.get(f"{BASE_URL}/api/simplified/topics")
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        print(f"✅ Topics API working - {len(data.get('topics', []))} topics")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
