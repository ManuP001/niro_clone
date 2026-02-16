"""
Phase 2 Testing: Expert Tags and Image Upload Features

Tests:
1. POST /api/admin/upload/image - Upload image file and verify serving
2. GET /api/admin/tag-options - Returns all tag options by type
3. POST /api/admin/experts - Create expert with new tag fields
4. GET /api/simplified/experts/all - Verify best_for_tags composition
"""

import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_USERNAME = 'NiroAdmin'
ADMIN_PASSWORD = 'NewAdmin@123'

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope='module')
def admin_token():
    """Get admin authentication token"""
    response = requests.post(f'{BASE_URL}/api/admin/login', json={
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f'Admin login failed: {response.text}')
    data = response.json()
    return data.get('token')

@pytest.fixture
def admin_headers(admin_token):
    """Headers with admin token"""
    return {
        'X-Admin-Token': admin_token,
        'Content-Type': 'application/json'
    }

# ============================================================================
# Feature 1: Image Upload Endpoint
# ============================================================================

class TestImageUpload:
    """Test POST /api/admin/upload/image and GET /api/admin/uploads/{filename}"""
    
    def test_upload_image_success(self, admin_token):
        """Upload an image file and verify it returns a URL"""
        # Create a simple test image (1x1 PNG)
        import base64
        # Minimal valid PNG
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        
        files = {
            'file': ('test_image.png', io.BytesIO(png_data), 'image/png')
        }
        
        response = requests.post(
            f'{BASE_URL}/api/admin/upload/image',
            files=files,
            headers={'X-Admin-Token': admin_token}
        )
        
        assert response.status_code == 200, f'Upload failed: {response.text}'
        data = response.json()
        assert data.get('ok') == True
        assert 'url' in data, 'Response should contain URL'
        assert 'filename' in data, 'Response should contain filename'
        assert data['url'].startswith('/api/admin/uploads/'), f'URL should be /api/admin/uploads/... got {data["url"]}'
        
        # Store for next test
        TestImageUpload.uploaded_url = data['url']
        TestImageUpload.uploaded_filename = data['filename']
        print(f'Uploaded image URL: {data["url"]}')
    
    def test_serve_uploaded_image(self):
        """Verify the uploaded image can be retrieved via GET"""
        if not hasattr(TestImageUpload, 'uploaded_url'):
            pytest.skip('No uploaded image from previous test')
        
        url = f'{BASE_URL}{TestImageUpload.uploaded_url}'
        response = requests.get(url)
        
        assert response.status_code == 200, f'Failed to serve image: {response.status_code}'
        assert response.headers.get('content-type') in ['image/png', 'application/octet-stream'], \
            f'Unexpected content-type: {response.headers.get("content-type")}'
        print(f'Image served successfully from {url}')
    
    def test_upload_without_auth_fails(self):
        """Upload without auth token should fail"""
        import base64
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        
        files = {
            'file': ('test_image.png', io.BytesIO(png_data), 'image/png')
        }
        
        response = requests.post(f'{BASE_URL}/api/admin/upload/image', files=files)
        assert response.status_code == 401, 'Should require auth'
    
    def test_upload_invalid_file_type_fails(self, admin_token):
        """Upload non-image file should fail"""
        files = {
            'file': ('test.txt', io.BytesIO(b'not an image'), 'text/plain')
        }
        
        response = requests.post(
            f'{BASE_URL}/api/admin/upload/image',
            files=files,
            headers={'X-Admin-Token': admin_token}
        )
        
        assert response.status_code == 400, f'Should reject non-image: {response.text}'


# ============================================================================
# Feature 2: Tag Options Endpoint
# ============================================================================

class TestTagOptions:
    """Test GET /api/admin/tag-options"""
    
    def test_get_tag_options(self, admin_headers):
        """Get all tag options grouped by type"""
        response = requests.get(f'{BASE_URL}/api/admin/tag-options', headers=admin_headers)
        
        assert response.status_code == 200, f'Failed: {response.text}'
        data = response.json()
        assert data.get('ok') == True
        assert 'tag_options' in data
        
        tag_options = data['tag_options']
        
        # Verify 3 tag types exist
        assert 'life_situation' in tag_options, 'Missing life_situation tags'
        assert 'method' in tag_options, 'Missing method tags'
        assert 'remedy_support' in tag_options, 'Missing remedy_support tags'
        
        print(f'Tag types returned: {list(tag_options.keys())}')
    
    def test_life_situation_has_categories(self, admin_headers):
        """life_situation should be grouped by category"""
        response = requests.get(f'{BASE_URL}/api/admin/tag-options', headers=admin_headers)
        data = response.json()
        
        life_situation = data['tag_options']['life_situation']
        assert isinstance(life_situation, dict), 'life_situation should be dict of categories'
        
        # Verify expected categories exist
        expected_categories = ['Career & Work', 'Business & Finance', 'Relationships', 'Marriage']
        for cat in expected_categories:
            assert cat in life_situation, f'Missing category: {cat}'
        
        # Count total tags
        total_tags = sum(len(tags) for tags in life_situation.values())
        print(f'life_situation: {len(life_situation)} categories, {total_tags} total tags')
        assert total_tags >= 50, f'Expected ~58 life_situation tags, got {total_tags}'
    
    def test_method_is_flat_array(self, admin_headers):
        """method tags should be flat array"""
        response = requests.get(f'{BASE_URL}/api/admin/tag-options', headers=admin_headers)
        data = response.json()
        
        method = data['tag_options']['method']
        assert isinstance(method, list), 'method should be a list'
        assert len(method) == 10, f'Expected 10 method tags, got {len(method)}'
        print(f'method tags: {method[:3]}...')
    
    def test_remedy_support_is_flat_array(self, admin_headers):
        """remedy_support tags should be flat array"""
        response = requests.get(f'{BASE_URL}/api/admin/tag-options', headers=admin_headers)
        data = response.json()
        
        remedy = data['tag_options']['remedy_support']
        assert isinstance(remedy, list), 'remedy_support should be a list'
        assert len(remedy) == 10, f'Expected 10 remedy tags, got {len(remedy)}'
        print(f'remedy_support tags: {remedy[:3]}...')


# ============================================================================
# Feature 3: Expert Creation with New Tag Fields
# ============================================================================

class TestExpertWithTags:
    """Test POST/PUT /api/admin/experts with new tag fields"""
    
    TEST_EXPERT_ID = 'TEST_phase2_expert_tags'
    
    def test_create_expert_with_tags(self, admin_headers):
        """Create expert with life_situation_tags, method_tags, remedy_tags"""
        # First delete if exists
        requests.delete(
            f'{BASE_URL}/api/admin/experts/{self.TEST_EXPERT_ID}?hard_delete=true',
            headers=admin_headers
        )
        
        expert_data = {
            'expert_id': self.TEST_EXPERT_ID,
            'name': 'Phase 2 Test Expert',
            'modality': 'vedic_astrologer',
            'modality_label': 'Vedic Astrologer',
            'bio': 'Testing Phase 2 tags',
            'languages': 'Hindi, English',
            'years_experience': 10,
            'rating': 4.7,
            'total_consults': 200,
            'topics': ['love', 'career'],
            'life_situation_tags': ['Career direction clarity', 'Job switch decision (stay vs leave)', 'Relationship clarity (where is this going?)'],
            'method_tags': ['Dasha analysis', 'Transit guidance'],
            'remedy_tags': ['Mantra guidance (basic)', 'Pooja guidance'],
            'active': True
        }
        
        response = requests.post(
            f'{BASE_URL}/api/admin/experts',
            json=expert_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200, f'Create failed: {response.text}'
        data = response.json()
        assert data.get('ok') == True
        
        expert = data.get('expert', {})
        assert expert.get('life_situation_tags') == expert_data['life_situation_tags']
        assert expert.get('method_tags') == expert_data['method_tags']
        assert expert.get('remedy_tags') == expert_data['remedy_tags']
        print('Expert created with all 3 tag types')
    
    def test_get_created_expert_has_tags(self, admin_headers):
        """Verify created expert has tag fields persisted"""
        response = requests.get(
            f'{BASE_URL}/api/admin/experts?include_inactive=true',
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        experts = data.get('experts', [])
        test_expert = next((e for e in experts if e.get('expert_id') == self.TEST_EXPERT_ID), None)
        
        assert test_expert is not None, f'Test expert not found in list'
        assert 'life_situation_tags' in test_expert
        assert 'method_tags' in test_expert
        assert 'remedy_tags' in test_expert
        assert len(test_expert['life_situation_tags']) == 3
        assert len(test_expert['method_tags']) == 2
        assert len(test_expert['remedy_tags']) == 2
        print(f'Expert persisted with tags: life={len(test_expert["life_situation_tags"])}, method={len(test_expert["method_tags"])}, remedy={len(test_expert["remedy_tags"])}')
    
    def test_cleanup_test_expert(self, admin_headers):
        """Cleanup test data"""
        response = requests.delete(
            f'{BASE_URL}/api/admin/experts/{self.TEST_EXPERT_ID}?hard_delete=true',
            headers=admin_headers
        )
        assert response.status_code in [200, 404]
        print('Test expert cleaned up')


# ============================================================================
# Feature 4: Public Experts Endpoint - best_for_tags Composition
# ============================================================================

class TestPublicExpertsBestForTags:
    """Test GET /api/simplified/experts/all - best_for_tags composition"""
    
    TEST_EXPERT_ID = 'TEST_phase2_public_visibility'
    
    def test_create_expert_for_public_test(self, admin_headers):
        """Create expert with tags to test public visibility"""
        requests.delete(
            f'{BASE_URL}/api/admin/experts/{self.TEST_EXPERT_ID}?hard_delete=true',
            headers=admin_headers
        )
        
        expert_data = {
            'expert_id': self.TEST_EXPERT_ID,
            'name': 'Public Visibility Test',
            'modality': 'tarot',
            'modality_label': 'Tarot Reader',
            'bio': 'Testing public endpoint tags',
            'languages': 'Hindi, English',
            'years_experience': 5,
            'rating': 4.5,
            'total_consults': 100,
            'topics': ['love'],
            'life_situation_tags': ['Breakup recovery', 'Trust issues / cheating suspicion'],
            'method_tags': ['Good vs caution periods (phase guidance)'],
            'remedy_tags': ['Energy healing session'],
            'active': True
        }
        
        response = requests.post(
            f'{BASE_URL}/api/admin/experts',
            json=expert_data,
            headers=admin_headers
        )
        assert response.status_code == 200, f'Create failed: {response.text}'
        print('Test expert created for public visibility test')
    
    def test_public_experts_includes_best_for_tags(self):
        """Public /api/simplified/experts/all should include computed best_for_tags"""
        response = requests.get(f'{BASE_URL}/api/simplified/experts/all')
        
        assert response.status_code == 200, f'Public endpoint failed: {response.text}'
        data = response.json()
        assert data.get('ok') == True
        
        experts = data.get('experts', [])
        test_expert = next((e for e in experts if e.get('expert_id') == self.TEST_EXPERT_ID), None)
        
        assert test_expert is not None, f'Test expert not found in public API. Total experts: {len(experts)}'
        
        # Verify best_for_tags is composed correctly
        assert 'best_for_tags' in test_expert, 'Missing best_for_tags field'
        best_for = test_expert['best_for_tags']
        
        # Should contain life_situation_tags + first method tag
        assert 'Breakup recovery' in best_for, 'Missing life_situation tag in best_for_tags'
        assert 'Trust issues / cheating suspicion' in best_for, 'Missing second life_situation tag'
        assert 'Good vs caution periods (phase guidance)' in best_for, 'Missing method tag in best_for_tags'
        
        # Verify other tag fields are also returned
        assert 'life_situation_tags' in test_expert
        assert 'method_tags' in test_expert
        assert 'remedy_tags' in test_expert
        
        print(f'best_for_tags correctly composed: {best_for}')
        print(f'life_situation_tags: {test_expert.get("life_situation_tags")}')
        print(f'method_tags: {test_expert.get("method_tags")}')
        print(f'remedy_tags: {test_expert.get("remedy_tags")}')
    
    def test_best_for_tags_composition_logic(self):
        """Verify best_for_tags = life_situation + first_method"""
        response = requests.get(f'{BASE_URL}/api/simplified/experts/all')
        data = response.json()
        
        test_expert = next((e for e in data.get('experts', []) if e.get('expert_id') == self.TEST_EXPERT_ID), None)
        if not test_expert:
            pytest.skip('Test expert not found')
        
        # Expected: 2 life_situation tags + 1 method tag = 3 tags
        best_for = test_expert.get('best_for_tags', [])
        life_tags = test_expert.get('life_situation_tags', [])
        method_tags = test_expert.get('method_tags', [])
        
        expected_best_for = list(life_tags)
        if method_tags:
            expected_best_for.append(method_tags[0])
        
        assert best_for == expected_best_for, f'best_for_tags composition mismatch. Got {best_for}, expected {expected_best_for}'
        print('best_for_tags composition logic verified')
    
    def test_cleanup_public_test_expert(self, admin_headers):
        """Cleanup test data"""
        response = requests.delete(
            f'{BASE_URL}/api/admin/experts/{self.TEST_EXPERT_ID}?hard_delete=true',
            headers=admin_headers
        )
        assert response.status_code in [200, 404]
        print('Public visibility test expert cleaned up')


# ============================================================================
# Feature 5 & 6: Admin UI tests will be done via Playwright
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
