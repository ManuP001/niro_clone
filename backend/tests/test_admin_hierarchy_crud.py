"""
Test Admin Dashboard Hierarchical CRUD - Categories and Tiles
Tests for the admin dashboard refactor with Categories (3 main groupings) and Tiles (18 homepage tiles)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://responsive-dashboard-14.preview.emergentagent.com').rstrip('/')

# Admin credentials
ADMIN_USERNAME = "NiroAdmin"
ADMIN_PASSWORD = "NewAdmin@123"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    data = response.json()
    assert data.get("ok") is True
    assert "token" in data
    return data["token"]


@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin token"""
    return {
        "Content-Type": "application/json",
        "X-Admin-Token": admin_token
    }


class TestAdminLogin:
    """Test admin authentication"""
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "token" in data
        assert data["message"] == "Login successful"
    
    def test_admin_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"username": "wrong", "password": "wrong"}
        )
        assert response.status_code == 401
    
    def test_admin_verify_session(self, admin_headers):
        """Test session verification"""
        response = requests.get(
            f"{BASE_URL}/api/admin/verify",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True


class TestCategoriesCRUD:
    """Test Categories CRUD operations"""
    
    def test_list_categories(self, admin_headers):
        """Test listing all categories - should have 3 (love, career, health)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/categories",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "categories" in data
        assert data["count"] >= 3
        
        # Verify the 3 main categories exist
        category_ids = [c["category_id"] for c in data["categories"]]
        assert "love" in category_ids
        assert "career" in category_ids
        assert "health" in category_ids
    
    def test_category_structure(self, admin_headers):
        """Test category data structure"""
        response = requests.get(
            f"{BASE_URL}/api/admin/categories",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        for category in data["categories"]:
            assert "category_id" in category
            assert "title" in category
            assert "helper_copy" in category
            assert "order" in category
            assert "active" in category
    
    def test_create_category(self, admin_headers):
        """Test creating a new category"""
        new_category = {
            "category_id": "TEST_finance",
            "title": "Finance & Wealth",
            "helper_copy": "Investment, savings, financial planning",
            "order": 10,
            "active": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/categories",
            headers=admin_headers,
            json=new_category
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["category"]["category_id"] == "TEST_finance"
        assert data["category"]["title"] == "Finance & Wealth"
    
    def test_update_category(self, admin_headers):
        """Test updating a category"""
        update_data = {
            "title": "Finance & Wealth Updated",
            "helper_copy": "Investment, savings, financial planning, budgeting"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/admin/categories/TEST_finance",
            headers=admin_headers,
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["category"]["title"] == "Finance & Wealth Updated"
        
        # Verify update persisted
        get_response = requests.get(
            f"{BASE_URL}/api/admin/categories?include_inactive=true",
            headers=admin_headers
        )
        categories = get_response.json()["categories"]
        test_cat = next((c for c in categories if c["category_id"] == "TEST_finance"), None)
        assert test_cat is not None
        assert test_cat["title"] == "Finance & Wealth Updated"
    
    def test_soft_delete_category(self, admin_headers):
        """Test soft deleting a category"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/categories/TEST_finance",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "deactivated" in data["message"]
        
        # Verify soft delete - should be inactive
        get_response = requests.get(
            f"{BASE_URL}/api/admin/categories?include_inactive=true",
            headers=admin_headers
        )
        categories = get_response.json()["categories"]
        test_cat = next((c for c in categories if c["category_id"] == "TEST_finance"), None)
        assert test_cat is not None
        assert test_cat["active"] is False
    
    def test_hard_delete_category(self, admin_headers):
        """Test hard deleting a category"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/categories/TEST_finance?hard_delete=true",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "deleted" in data["message"]
        
        # Verify hard delete - should be gone
        get_response = requests.get(
            f"{BASE_URL}/api/admin/categories?include_inactive=true",
            headers=admin_headers
        )
        categories = get_response.json()["categories"]
        test_cat = next((c for c in categories if c["category_id"] == "TEST_finance"), None)
        assert test_cat is None
    
    def test_create_duplicate_category_fails(self, admin_headers):
        """Test that creating duplicate category fails"""
        response = requests.post(
            f"{BASE_URL}/api/admin/categories",
            headers=admin_headers,
            json={"category_id": "love", "title": "Duplicate Love", "order": 99}
        )
        assert response.status_code == 400


class TestTilesCRUD:
    """Test Tiles CRUD operations"""
    
    def test_list_tiles(self, admin_headers):
        """Test listing all tiles - should have 18 tiles"""
        response = requests.get(
            f"{BASE_URL}/api/admin/tiles",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "tiles" in data
        assert data["count"] >= 18
    
    def test_tiles_grouped_by_category(self, admin_headers):
        """Test that tiles are properly grouped by category"""
        response = requests.get(
            f"{BASE_URL}/api/admin/tiles",
            headers=admin_headers
        )
        data = response.json()
        
        # Count tiles per category
        love_tiles = [t for t in data["tiles"] if t["category_id"] == "love"]
        career_tiles = [t for t in data["tiles"] if t["category_id"] == "career"]
        health_tiles = [t for t in data["tiles"] if t["category_id"] == "health"]
        
        assert len(love_tiles) >= 6, f"Expected 6 love tiles, got {len(love_tiles)}"
        assert len(career_tiles) >= 6, f"Expected 6 career tiles, got {len(career_tiles)}"
        assert len(health_tiles) >= 6, f"Expected 6 health tiles, got {len(health_tiles)}"
    
    def test_filter_tiles_by_category(self, admin_headers):
        """Test filtering tiles by category"""
        response = requests.get(
            f"{BASE_URL}/api/admin/tiles?category_id=love",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        for tile in data["tiles"]:
            assert tile["category_id"] == "love"
    
    def test_tile_structure(self, admin_headers):
        """Test tile data structure"""
        response = requests.get(
            f"{BASE_URL}/api/admin/tiles",
            headers=admin_headers
        )
        data = response.json()
        
        for tile in data["tiles"]:
            assert "tile_id" in tile
            assert "category_id" in tile
            assert "short_title" in tile
            assert "full_title" in tile
            assert "icon_type" in tile
            assert "order" in tile
            assert "active" in tile
    
    def test_create_tile(self, admin_headers):
        """Test creating a new tile"""
        new_tile = {
            "tile_id": "TEST_yoga",
            "category_id": "health",
            "short_title": "Yoga",
            "full_title": "Yoga & Flexibility",
            "icon_type": "yoga",
            "order": 10,
            "active": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/tiles",
            headers=admin_headers,
            json=new_tile
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["tile"]["tile_id"] == "TEST_yoga"
        assert data["tile"]["category_id"] == "health"
    
    def test_update_tile(self, admin_headers):
        """Test updating a tile"""
        update_data = {
            "short_title": "Yoga Updated",
            "full_title": "Yoga & Flexibility Practice"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/admin/tiles/TEST_yoga",
            headers=admin_headers,
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["tile"]["short_title"] == "Yoga Updated"
        
        # Verify update persisted
        get_response = requests.get(
            f"{BASE_URL}/api/admin/tiles?include_inactive=true",
            headers=admin_headers
        )
        tiles = get_response.json()["tiles"]
        test_tile = next((t for t in tiles if t["tile_id"] == "TEST_yoga"), None)
        assert test_tile is not None
        assert test_tile["short_title"] == "Yoga Updated"
    
    def test_soft_delete_tile(self, admin_headers):
        """Test soft deleting a tile"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/tiles/TEST_yoga",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "deactivated" in data["message"]
        
        # Verify soft delete
        get_response = requests.get(
            f"{BASE_URL}/api/admin/tiles?include_inactive=true",
            headers=admin_headers
        )
        tiles = get_response.json()["tiles"]
        test_tile = next((t for t in tiles if t["tile_id"] == "TEST_yoga"), None)
        assert test_tile is not None
        assert test_tile["active"] is False
    
    def test_hard_delete_tile(self, admin_headers):
        """Test hard deleting a tile"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/tiles/TEST_yoga?hard_delete=true",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        # Verify hard delete
        get_response = requests.get(
            f"{BASE_URL}/api/admin/tiles?include_inactive=true",
            headers=admin_headers
        )
        tiles = get_response.json()["tiles"]
        test_tile = next((t for t in tiles if t["tile_id"] == "TEST_yoga"), None)
        assert test_tile is None
    
    def test_create_duplicate_tile_fails(self, admin_headers):
        """Test that creating duplicate tile fails"""
        response = requests.post(
            f"{BASE_URL}/api/admin/tiles",
            headers=admin_headers,
            json={"tile_id": "career_clarity", "category_id": "career", "short_title": "Duplicate", "order": 99}
        )
        assert response.status_code == 400


class TestSeedCatalog:
    """Test seed catalog endpoint"""
    
    def test_seed_catalog_detects_existing_data(self, admin_headers):
        """Test that seed catalog detects existing data"""
        response = requests.post(
            f"{BASE_URL}/api/admin/seed-catalog",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should indicate data exists
        assert data["ok"] is False
        assert "already exists" in data["message"]
        assert "existing" in data
        assert data["existing"]["categories"] >= 3
        assert data["existing"]["tiles"] >= 18


class TestUnauthorizedAccess:
    """Test unauthorized access is blocked"""
    
    def test_categories_without_token(self):
        """Test categories endpoint without token"""
        response = requests.get(f"{BASE_URL}/api/admin/categories")
        assert response.status_code == 401
    
    def test_tiles_without_token(self):
        """Test tiles endpoint without token"""
        response = requests.get(f"{BASE_URL}/api/admin/tiles")
        assert response.status_code == 401
    
    def test_create_category_without_token(self):
        """Test creating category without token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/categories",
            json={"category_id": "test", "title": "Test"}
        )
        assert response.status_code == 401
    
    def test_create_tile_without_token(self):
        """Test creating tile without token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/tiles",
            json={"tile_id": "test", "category_id": "love", "short_title": "Test"}
        )
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
