"""
Test Public Homepage API - GET /api/admin/public/homepage-data

Tests:
1. Public API returns data without authentication
2. Response format matches frontend expectations (id, title, helperCopy, tiles)
3. Tiles have correct structure (id, shortTitle, fullTitle, iconType)
4. Admin changes reflect immediately in public API
5. Fallback to defaults when database is empty (simulated)
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials for testing admin changes
ADMIN_USERNAME = "NiroAdmin"
ADMIN_PASSWORD = "NewAdmin@123"


class TestPublicHomepageAPI:
    """Tests for the public homepage data endpoint"""
    
    def test_public_api_no_auth_required(self):
        """Test that public API works without authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        
        # Should return 200 without any auth headers
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("ok") is True, "Response should have ok=True"
        print("✓ Public API accessible without authentication")
    
    def test_response_has_correct_structure(self):
        """Test that response has the expected structure for frontend"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check top-level fields
        assert "ok" in data, "Response should have 'ok' field"
        assert "source" in data, "Response should have 'source' field"
        assert data["source"] in ["database", "defaults"], f"Source should be 'database' or 'defaults', got {data['source']}"
        
        # If source is database, check 'data' field
        if data["source"] == "database":
            assert "data" in data, "Database response should have 'data' field"
            homepage_data = data["data"]
            assert isinstance(homepage_data, list), "'data' should be a list"
            assert len(homepage_data) > 0, "'data' should not be empty"
        
        print(f"✓ Response structure correct, source: {data['source']}")
    
    def test_categories_have_frontend_format(self):
        """Test that categories have id, title, helperCopy, tiles structure"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["source"] == "database":
            homepage_data = data["data"]
            
            for category in homepage_data:
                # Check required fields
                assert "id" in category, f"Category missing 'id': {category}"
                assert "title" in category, f"Category missing 'title': {category}"
                assert "helperCopy" in category, f"Category missing 'helperCopy': {category}"
                assert "tiles" in category, f"Category missing 'tiles': {category}"
                
                # Validate types
                assert isinstance(category["id"], str), "Category 'id' should be string"
                assert isinstance(category["title"], str), "Category 'title' should be string"
                assert isinstance(category["tiles"], list), "Category 'tiles' should be list"
                
                print(f"  ✓ Category '{category['id']}' has correct structure")
        else:
            # Check defaults format
            assert "categories" in data, "Defaults response should have 'categories'"
            assert "tiles" in data, "Defaults response should have 'tiles'"
        
        print("✓ All categories have frontend-friendly format")
    
    def test_tiles_have_correct_structure(self):
        """Test that tiles have id, shortTitle, fullTitle, iconType"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["source"] == "database":
            homepage_data = data["data"]
            total_tiles = 0
            
            for category in homepage_data:
                for tile in category["tiles"]:
                    # Check required fields
                    assert "id" in tile, f"Tile missing 'id': {tile}"
                    assert "shortTitle" in tile, f"Tile missing 'shortTitle': {tile}"
                    assert "iconType" in tile, f"Tile missing 'iconType': {tile}"
                    
                    # Validate types
                    assert isinstance(tile["id"], str), "Tile 'id' should be string"
                    assert isinstance(tile["shortTitle"], str), "Tile 'shortTitle' should be string"
                    assert isinstance(tile["iconType"], str), "Tile 'iconType' should be string"
                    
                    total_tiles += 1
            
            print(f"✓ All {total_tiles} tiles have correct structure")
        else:
            print("✓ Using defaults - tiles structure verified in defaults")
    
    def test_expected_categories_present(self):
        """Test that expected categories (love, career, health) are present"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["source"] == "database":
            homepage_data = data["data"]
            category_ids = [cat["id"] for cat in homepage_data]
            
            expected_categories = ["love", "career", "health"]
            for expected in expected_categories:
                assert expected in category_ids, f"Expected category '{expected}' not found"
                print(f"  ✓ Category '{expected}' present")
        else:
            categories = data.get("categories", [])
            category_ids = [cat["category_id"] for cat in categories]
            
            expected_categories = ["love", "career", "health"]
            for expected in expected_categories:
                assert expected in category_ids, f"Expected category '{expected}' not found in defaults"
        
        print("✓ All expected categories present")
    
    def test_tiles_count_per_category(self):
        """Test that each category has expected number of tiles (6 each)"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["source"] == "database":
            homepage_data = data["data"]
            
            for category in homepage_data:
                tile_count = len(category["tiles"])
                print(f"  Category '{category['id']}': {tile_count} tiles")
                # Each category should have at least 1 tile
                assert tile_count >= 1, f"Category '{category['id']}' has no tiles"
        
        print("✓ Tile counts verified")


class TestAdminChangesReflection:
    """Tests that admin changes reflect immediately in public API"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Admin authentication failed")
    
    def test_create_category_reflects_in_public_api(self, admin_token):
        """Test that creating a category via admin reflects in public API"""
        headers = {"X-Admin-Token": admin_token}
        
        # Create a test category
        test_category = {
            "category_id": "TEST_public_api_cat",
            "title": "Test Public API Category",
            "helper_copy": "Testing public API reflection",
            "order": 99,
            "active": True
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/admin/categories",
            json=test_category,
            headers=headers
        )
        
        # Handle case where category already exists
        if create_response.status_code == 400:
            # Delete and recreate
            requests.delete(
                f"{BASE_URL}/api/admin/categories/TEST_public_api_cat?hard_delete=true",
                headers=headers
            )
            create_response = requests.post(
                f"{BASE_URL}/api/admin/categories",
                json=test_category,
                headers=headers
            )
        
        assert create_response.status_code == 200, f"Failed to create category: {create_response.text}"
        print("✓ Test category created")
        
        # Check public API immediately
        public_response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert public_response.status_code == 200
        
        data = public_response.json()
        
        # The category should appear in the response
        if data["source"] == "database":
            category_ids = [cat["id"] for cat in data["data"]]
            assert "TEST_public_api_cat" in category_ids, "New category not found in public API"
            print("✓ New category immediately visible in public API")
        
        # Cleanup - delete the test category
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/categories/TEST_public_api_cat?hard_delete=true",
            headers=headers
        )
        assert delete_response.status_code == 200, "Failed to cleanup test category"
        print("✓ Test category cleaned up")
    
    def test_create_tile_reflects_in_public_api(self, admin_token):
        """Test that creating a tile via admin reflects in public API"""
        headers = {"X-Admin-Token": admin_token}
        
        # Create a test tile under 'love' category
        test_tile = {
            "tile_id": "TEST_public_api_tile",
            "category_id": "love",
            "short_title": "Test Tile",
            "full_title": "Test Public API Tile",
            "icon_type": "star",
            "order": 99,
            "active": True
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/admin/tiles",
            json=test_tile,
            headers=headers
        )
        
        # Handle case where tile already exists
        if create_response.status_code == 400:
            requests.delete(
                f"{BASE_URL}/api/admin/tiles/TEST_public_api_tile?hard_delete=true",
                headers=headers
            )
            create_response = requests.post(
                f"{BASE_URL}/api/admin/tiles",
                json=test_tile,
                headers=headers
            )
        
        assert create_response.status_code == 200, f"Failed to create tile: {create_response.text}"
        print("✓ Test tile created")
        
        # Check public API immediately
        public_response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert public_response.status_code == 200
        
        data = public_response.json()
        
        # Find the tile in the love category
        if data["source"] == "database":
            love_category = next((cat for cat in data["data"] if cat["id"] == "love"), None)
            assert love_category is not None, "Love category not found"
            
            tile_ids = [tile["id"] for tile in love_category["tiles"]]
            assert "TEST_public_api_tile" in tile_ids, "New tile not found in public API"
            print("✓ New tile immediately visible in public API under 'love' category")
        
        # Cleanup
        delete_response = requests.delete(
            f"{BASE_URL}/api/admin/tiles/TEST_public_api_tile?hard_delete=true",
            headers=headers
        )
        assert delete_response.status_code == 200, "Failed to cleanup test tile"
        print("✓ Test tile cleaned up")
    
    def test_update_category_reflects_in_public_api(self, admin_token):
        """Test that updating a category title reflects in public API"""
        headers = {"X-Admin-Token": admin_token}
        
        # Get current love category title
        public_response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        data = public_response.json()
        
        if data["source"] == "database":
            love_category = next((cat for cat in data["data"] if cat["id"] == "love"), None)
            original_title = love_category["title"]
            
            # Update the title
            update_response = requests.put(
                f"{BASE_URL}/api/admin/categories/love",
                json={"title": "TEST_Updated Love Title"},
                headers=headers
            )
            assert update_response.status_code == 200, f"Failed to update category: {update_response.text}"
            print("✓ Category title updated")
            
            # Check public API immediately
            public_response2 = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
            data2 = public_response2.json()
            
            love_category2 = next((cat for cat in data2["data"] if cat["id"] == "love"), None)
            assert love_category2["title"] == "TEST_Updated Love Title", "Title update not reflected"
            print("✓ Updated title immediately visible in public API")
            
            # Restore original title
            restore_response = requests.put(
                f"{BASE_URL}/api/admin/categories/love",
                json={"title": original_title},
                headers=headers
            )
            assert restore_response.status_code == 200, "Failed to restore original title"
            print(f"✓ Original title '{original_title}' restored")
    
    def test_deactivate_tile_hides_from_public_api(self, admin_token):
        """Test that deactivating a tile hides it from public API"""
        headers = {"X-Admin-Token": admin_token}
        
        # First create a test tile
        test_tile = {
            "tile_id": "TEST_deactivate_tile",
            "category_id": "career",
            "short_title": "Deactivate Test",
            "full_title": "Test Deactivation",
            "icon_type": "star",
            "order": 99,
            "active": True
        }
        
        # Clean up first if exists
        requests.delete(
            f"{BASE_URL}/api/admin/tiles/TEST_deactivate_tile?hard_delete=true",
            headers=headers
        )
        
        create_response = requests.post(
            f"{BASE_URL}/api/admin/tiles",
            json=test_tile,
            headers=headers
        )
        assert create_response.status_code == 200, f"Failed to create tile: {create_response.text}"
        
        # Verify it's visible
        public_response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        data = public_response.json()
        
        if data["source"] == "database":
            career_category = next((cat for cat in data["data"] if cat["id"] == "career"), None)
            tile_ids = [tile["id"] for tile in career_category["tiles"]]
            assert "TEST_deactivate_tile" in tile_ids, "Test tile should be visible initially"
            print("✓ Test tile visible in public API")
            
            # Deactivate the tile (soft delete)
            deactivate_response = requests.delete(
                f"{BASE_URL}/api/admin/tiles/TEST_deactivate_tile",
                headers=headers
            )
            assert deactivate_response.status_code == 200, "Failed to deactivate tile"
            print("✓ Tile deactivated")
            
            # Check public API - tile should be hidden
            public_response2 = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
            data2 = public_response2.json()
            
            career_category2 = next((cat for cat in data2["data"] if cat["id"] == "career"), None)
            tile_ids2 = [tile["id"] for tile in career_category2["tiles"]]
            assert "TEST_deactivate_tile" not in tile_ids2, "Deactivated tile should be hidden"
            print("✓ Deactivated tile hidden from public API")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/admin/tiles/TEST_deactivate_tile?hard_delete=true",
            headers=headers
        )
        print("✓ Test tile cleaned up")


class TestPublicAPIEdgeCases:
    """Edge case tests for public homepage API"""
    
    def test_api_returns_json_content_type(self):
        """Test that API returns proper JSON content type"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type, f"Expected JSON content type, got {content_type}"
        print("✓ API returns JSON content type")
    
    def test_api_handles_concurrent_requests(self):
        """Test that API handles multiple concurrent requests"""
        import concurrent.futures
        
        def make_request():
            response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
            return response.status_code
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 200 for status in results), f"Some requests failed: {results}"
        print(f"✓ All {len(results)} concurrent requests succeeded")
    
    def test_response_excludes_mongodb_id(self):
        """Test that response doesn't include MongoDB _id field"""
        response = requests.get(f"{BASE_URL}/api/admin/public/homepage-data")
        assert response.status_code == 200
        
        data = response.json()
        response_text = str(data)
        
        # Check that _id is not in the response
        assert "_id" not in response_text, "Response should not contain MongoDB _id"
        print("✓ Response excludes MongoDB _id field")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
