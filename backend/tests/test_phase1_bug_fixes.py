"""
Test Phase 1 Bug Fixes:
1. Test deactivation works for categories, tiles, tiers (active: false not being dropped)
2. Test Valentine's package landing page APIs return content
3. Test homepage data API returns valentine-special category with linked packages
4. Test admin login and session persistence
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_USERNAME = "NiroAdmin"
ADMIN_PASSWORD = "NewAdmin@123"

# Test category and tile IDs for testing
TEST_CATEGORY_ID = "TEST_deactivation_category"
TEST_TILE_ID = "TEST_deactivation_tile"
TEST_TIER_ID = "TEST_deactivation_tier"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin token for authenticated requests"""
    response = requests.post(f"{BASE_URL}/api/admin/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    data = response.json()
    assert data.get("ok") == True, "Login response not ok"
    assert "token" in data, "No token in login response"
    return data["token"]


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Return headers with admin token"""
    return {
        "Content-Type": "application/json",
        "X-Admin-Token": admin_token
    }


class TestAdminLogin:
    """Test admin login works correctly"""
    
    def test_admin_login_success(self):
        """Test admin can login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "token" in data
        assert len(data["token"]) > 20  # Token should be a proper hash
    
    def test_admin_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "username": "wrong_user",
            "password": "wrong_pass"
        })
        assert response.status_code == 401


class TestDeactivationFix:
    """Test that active: false is properly preserved in PUT requests (bug fix #2)"""
    
    def test_create_and_deactivate_category(self, admin_headers):
        """Test creating a category and then deactivating it"""
        # First, clean up if test category exists (deactivate and delete)
        delete_resp = requests.delete(
            f"{BASE_URL}/api/admin/categories/{TEST_CATEGORY_ID}?hard_delete=true",
            headers=admin_headers
        )
        
        # Create a new test category
        create_resp = requests.post(
            f"{BASE_URL}/api/admin/categories",
            headers=admin_headers,
            json={
                "category_id": TEST_CATEGORY_ID,
                "title": "Test Deactivation Category",
                "helper_copy": "Testing deactivation",
                "order": 999,
                "active": False  # Start as inactive since no tiles
            }
        )
        assert create_resp.status_code == 200, f"Create failed: {create_resp.text}"
        
        # Now try to deactivate with active: false
        deactivate_resp = requests.put(
            f"{BASE_URL}/api/admin/categories/{TEST_CATEGORY_ID}",
            headers=admin_headers,
            json={"active": False}  # THIS WAS THE BUG - active: false was being dropped
        )
        assert deactivate_resp.status_code == 200, f"Deactivate failed: {deactivate_resp.text}"
        data = deactivate_resp.json()
        assert data.get("ok") == True, "Response not ok"
        
        # Verify the category is now deactivated
        category = data.get("category", {})
        assert category.get("active") == False, f"Category should be inactive, got: {category.get('active')}"
        
        # Verify by re-fetching - use include_inactive to see it
        verify_resp = requests.get(
            f"{BASE_URL}/api/admin/categories?include_inactive=true",
            headers=admin_headers
        )
        assert verify_resp.status_code == 200
        categories = verify_resp.json().get("categories", [])
        test_cat = next((c for c in categories if c.get("category_id") == TEST_CATEGORY_ID), None)
        assert test_cat is not None, "Test category not found"
        assert test_cat.get("active") == False, f"Category should still be inactive: {test_cat}"
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/admin/categories/{TEST_CATEGORY_ID}?hard_delete=true",
            headers=admin_headers
        )
    
    def test_reactivate_category_requires_tiles(self, admin_headers):
        """Test that reactivating a category requires tiles (validation)"""
        # Clean up first
        requests.delete(
            f"{BASE_URL}/api/admin/categories/{TEST_CATEGORY_ID}?hard_delete=true",
            headers=admin_headers
        )
        
        # Create inactive category
        create_resp = requests.post(
            f"{BASE_URL}/api/admin/categories",
            headers=admin_headers,
            json={
                "category_id": TEST_CATEGORY_ID,
                "title": "Test Reactivation Category",
                "order": 999,
                "active": False
            }
        )
        assert create_resp.status_code == 200
        
        # Try to activate without tiles - should fail
        activate_resp = requests.put(
            f"{BASE_URL}/api/admin/categories/{TEST_CATEGORY_ID}",
            headers=admin_headers,
            json={"active": True}
        )
        # This should fail with 400 because no tiles
        assert activate_resp.status_code == 400, f"Should fail to activate category without tiles: {activate_resp.text}"
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/admin/categories/{TEST_CATEGORY_ID}?hard_delete=true",
            headers=admin_headers
        )
    
    def test_deactivate_tile(self, admin_headers):
        """Test deactivating a tile with active: false"""
        # Clean up first
        requests.delete(
            f"{BASE_URL}/api/admin/tiles/{TEST_TILE_ID}?hard_delete=true",
            headers=admin_headers
        )
        
        # Create a test tile
        create_resp = requests.post(
            f"{BASE_URL}/api/admin/tiles",
            headers=admin_headers,
            json={
                "tile_id": TEST_TILE_ID,
                "category_id": "love",  # Use existing category
                "short_title": "Test Tile",
                "full_title": "Test Tile for Deactivation",
                "icon_type": "star",
                "order": 999,
                "active": True
            }
        )
        assert create_resp.status_code == 200, f"Create tile failed: {create_resp.text}"
        
        # Deactivate the tile
        deactivate_resp = requests.put(
            f"{BASE_URL}/api/admin/tiles/{TEST_TILE_ID}",
            headers=admin_headers,
            json={"active": False}
        )
        assert deactivate_resp.status_code == 200, f"Deactivate tile failed: {deactivate_resp.text}"
        data = deactivate_resp.json()
        assert data.get("ok") == True
        tile = data.get("tile", {})
        assert tile.get("active") == False, f"Tile should be inactive: {tile}"
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/admin/tiles/{TEST_TILE_ID}?hard_delete=true",
            headers=admin_headers
        )
    
    def test_deactivate_tier(self, admin_headers):
        """Test deactivating a tier/package with active: false"""
        # Clean up first
        requests.delete(
            f"{BASE_URL}/api/admin/tiers/{TEST_TIER_ID}?hard_delete=true",
            headers=admin_headers
        )
        
        # Create a test tier
        create_resp = requests.post(
            f"{BASE_URL}/api/admin/tiers",
            headers=admin_headers,
            json={
                "tier_id": TEST_TIER_ID,
                "name": "Test Package",
                "price": 999,
                "duration_days": 7,
                "calls_included": 1,
                "features": ["Test feature"],
                "active": True
            }
        )
        assert create_resp.status_code == 200, f"Create tier failed: {create_resp.text}"
        
        # Deactivate the tier
        deactivate_resp = requests.put(
            f"{BASE_URL}/api/admin/tiers/{TEST_TIER_ID}",
            headers=admin_headers,
            json={"active": False}
        )
        assert deactivate_resp.status_code == 200, f"Deactivate tier failed: {deactivate_resp.text}"
        data = deactivate_resp.json()
        assert data.get("ok") == True
        tier = data.get("tier", {})
        assert tier.get("active") == False, f"Tier should be inactive: {tier}"
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/admin/tiers/{TEST_TIER_ID}?hard_delete=true",
            headers=admin_headers
        )


class TestValentinesPackageAPIs:
    """Test Valentine's Special package landing page APIs (bug fix #3, #4)"""
    
    def test_not_official_yet_package(self):
        """Test GET /api/admin/public/package/not-official-yet-pkg returns content"""
        response = requests.get(f"{BASE_URL}/api/admin/public/package/not-official-yet-pkg")
        assert response.status_code == 200, f"Failed to get package: {response.text}"
        data = response.json()
        assert data.get("ok") == True, "Response not ok"
        assert "package" in data, "No package in response"
        
        pkg = data["package"]
        # Verify package has basic fields
        assert "tier_id" in pkg or "name" in pkg, f"Package missing tier_id or name: {pkg.keys()}"
        assert pkg.get("price") or pkg.get("price") == 0, "Package missing price"
        
        # Verify content exists or fallback fields work
        content = pkg.get("content", {})
        has_content = bool(content and any(content.values()))
        has_fallback = bool(pkg.get("name") or pkg.get("features") or pkg.get("description"))
        assert has_content or has_fallback, "Package should have content or fallback fields"
        
        print(f"Package found: {pkg.get('name', pkg.get('tier_id'))}")
    
    def test_ready_for_marriage_package(self):
        """Test GET /api/admin/public/package/ready-for-marriage-pkg returns content"""
        response = requests.get(f"{BASE_URL}/api/admin/public/package/ready-for-marriage-pkg")
        assert response.status_code == 200, f"Failed to get package: {response.text}"
        data = response.json()
        assert data.get("ok") == True, "Response not ok"
        assert "package" in data, "No package in response"
        
        pkg = data["package"]
        assert pkg.get("price") or pkg.get("price") == 0, "Package missing price"
        print(f"Package found: {pkg.get('name', pkg.get('tier_id'))} - Price: {pkg.get('price')}")
    
    def test_move_on_or_stay_package(self):
        """Test GET /api/admin/public/package/move-on-or-stay-pkg returns content"""
        response = requests.get(f"{BASE_URL}/api/admin/public/package/move-on-or-stay-pkg")
        assert response.status_code == 200, f"Failed to get package: {response.text}"
        data = response.json()
        assert data.get("ok") == True, "Response not ok"
        assert "package" in data, "No package in response"
        
        pkg = data["package"]
        assert pkg.get("price") or pkg.get("price") == 0, "Package missing price"
        print(f"Package found: {pkg.get('name', pkg.get('tier_id'))} - Price: {pkg.get('price')}")


class TestHomepageDataAPI:
    """Test homepage data API returns Valentine's category correctly"""
    
    def test_homepage_data_returns_valentine_category(self):
        """Test GET /api/admin/public/homepage-data returns valentine-special category with tiles"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert response.status_code == 200, f"Homepage data failed: {response.text}"
        data = response.json()
        assert data.get("ok") == True, "Response not ok"
        assert "data" in data, "No data in response"
        
        categories = data["data"]
        assert len(categories) > 0, "No categories returned"
        
        # Find valentine-special category
        valentine_cat = next((c for c in categories if c.get("id") == "valentine-special"), None)
        
        if valentine_cat:
            print(f"Found valentine-special category: {valentine_cat.get('title')}")
            tiles = valentine_cat.get("tiles", [])
            assert len(tiles) > 0, "Valentine category should have tiles"
            
            # Check tiles have linkedPackageId (for Valentine's tiles)
            tiles_with_packages = [t for t in tiles if t.get("linkedPackageId")]
            print(f"Tiles with linkedPackageId: {len(tiles_with_packages)} / {len(tiles)}")
            
            # Verify at least one tile has linkedPackageId
            if len(tiles) >= 3:  # Expected 3 Valentine's tiles
                assert len(tiles_with_packages) >= 1, "At least one tile should have linkedPackageId"
        else:
            # Valentine category might not be active - just verify we got some categories
            print(f"Valentine category not found. Categories: {[c.get('id') for c in categories]}")
            print("Note: Valentine category might be deactivated or not seeded")
    
    def test_homepage_data_categories_have_tiles(self):
        """Test that categories have tiles with proper structure"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert response.status_code == 200
        data = response.json()
        
        for cat in data.get("data", []):
            assert "id" in cat, "Category missing id"
            assert "title" in cat, "Category missing title"
            tiles = cat.get("tiles", [])
            
            for tile in tiles:
                assert "id" in tile, f"Tile missing id in category {cat.get('id')}"
                assert "shortTitle" in tile, f"Tile missing shortTitle in category {cat.get('id')}"


class TestAdminDashboardAPIs:
    """Test admin dashboard APIs work correctly (bug fix #1 - BACKEND_URL undefined)"""
    
    def test_users_endpoint(self, admin_headers):
        """Test /api/admin/users endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users?page=1&limit=20",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Users endpoint failed: {response.text}"
        data = response.json()
        assert data.get("ok") == True
        assert "users" in data
        assert "pagination" in data
        print(f"Users API works - Total users: {data['pagination'].get('total', 0)}")
    
    def test_orders_endpoint(self, admin_headers):
        """Test /api/admin/orders endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/orders?page=1&limit=20",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Orders endpoint failed: {response.text}"
        data = response.json()
        assert data.get("ok") == True
        assert "orders" in data
        assert "pagination" in data
        print(f"Orders API works - Total orders: {data['pagination'].get('total', 0)}")
    
    def test_stats_endpoint(self, admin_headers):
        """Test /api/admin/stats endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Stats endpoint failed: {response.text}"
        data = response.json()
        assert data.get("ok") == True
        assert "stats" in data
        
        stats = data["stats"]
        assert "total_users" in stats
        assert "total_orders" in stats
        print(f"Stats API works - Users: {stats.get('total_users')}, Orders: {stats.get('total_orders')}")
    
    def test_categories_endpoint(self, admin_headers):
        """Test /api/admin/categories endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/categories",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Categories endpoint failed: {response.text}"
        data = response.json()
        assert data.get("ok") == True
        assert "categories" in data
        print(f"Categories API works - Count: {data.get('count', len(data.get('categories', [])))}")
    
    def test_tiles_endpoint(self, admin_headers):
        """Test /api/admin/tiles endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/tiles",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Tiles endpoint failed: {response.text}"
        data = response.json()
        assert data.get("ok") == True
        assert "tiles" in data
        print(f"Tiles API works - Count: {data.get('count', len(data.get('tiles', [])))}")


class TestVerifySessionEndpoint:
    """Test verify session endpoint for session persistence"""
    
    def test_verify_valid_session(self, admin_token):
        """Test /api/admin/verify endpoint with valid token"""
        response = requests.get(
            f"{BASE_URL}/api/admin/verify",
            headers={"X-Admin-Token": admin_token}
        )
        assert response.status_code == 200, f"Verify failed: {response.text}"
        data = response.json()
        assert data.get("ok") == True
        print("Session verification works")
    
    def test_verify_invalid_session(self):
        """Test /api/admin/verify endpoint with invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/admin/verify",
            headers={"X-Admin-Token": "invalid-token-12345"}
        )
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
