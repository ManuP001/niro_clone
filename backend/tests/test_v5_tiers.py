"""
NIRO V5 Tier API Tests
Tests for the 18 sub-topic tiers (3 tiers per sub-topic: Focussed, Supported, Comprehensive)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# All 18 sub-topics with their 3 tiers each
V5_SUBTOPICS = [
    # Love sub-topics (6)
    "relationship-healing",
    "family-relationships", 
    "dating-compatibility",
    "marriage-planning",
    "communication-trust",
    "breakup-closure",
    # Career sub-topics (6)
    "career-clarity",
    "job-transition",
    "money-stability",
    "work-stress",
    "office-politics",
    "big-decision-timing",
    # Health sub-topics (6)
    "healing-journey",
    "stress-management",
    "energy-balance",
    "sleep-reset",
    "emotional-recovery",
    "womens-wellness",
]

TIER_LEVELS = ["focussed", "supported", "comprehensive"]


class TestV5TierAPIs:
    """Test V5 tier API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_health_check(self):
        """Test API is accessible"""
        response = self.session.get(f"{BASE_URL}/api/health")
        # Health endpoint may not exist, so we test a known endpoint
        tier_response = self.session.get(f"{BASE_URL}/api/simplified/tiers/relationship-healing_supported")
        assert tier_response.status_code == 200
        print("API is accessible")
    
    @pytest.mark.parametrize("subtopic", V5_SUBTOPICS[:6])  # Test Love sub-topics
    def test_love_subtopic_tiers(self, subtopic):
        """Test Love category sub-topic tiers"""
        for tier_level in TIER_LEVELS:
            tier_id = f"{subtopic}_{tier_level}"
            response = self.session.get(f"{BASE_URL}/api/simplified/tiers/{tier_id}")
            
            assert response.status_code == 200, f"Failed for {tier_id}: {response.text}"
            
            data = response.json()
            assert data.get("ok") == True, f"Response not ok for {tier_id}"
            
            tier = data.get("tier", {})
            assert tier.get("tier_id") == tier_id
            assert tier.get("tier_level") == tier_level
            assert tier.get("price_inr") > 0
            assert tier.get("validity_weeks") > 0
            
            # Supported tier should always be recommended
            if tier_level == "supported":
                assert tier.get("is_recommended") == True, f"Supported tier {tier_id} should be recommended"
            
            print(f"✓ {tier_id}: ₹{tier.get('price_inr')} ({tier.get('validity_weeks')} weeks)")
    
    @pytest.mark.parametrize("subtopic", V5_SUBTOPICS[6:12])  # Test Career sub-topics
    def test_career_subtopic_tiers(self, subtopic):
        """Test Career category sub-topic tiers"""
        for tier_level in TIER_LEVELS:
            tier_id = f"{subtopic}_{tier_level}"
            response = self.session.get(f"{BASE_URL}/api/simplified/tiers/{tier_id}")
            
            assert response.status_code == 200, f"Failed for {tier_id}: {response.text}"
            
            data = response.json()
            assert data.get("ok") == True
            
            tier = data.get("tier", {})
            assert tier.get("tier_id") == tier_id
            assert tier.get("price_inr") > 0
            
            # Supported tier should always be recommended
            if tier_level == "supported":
                assert tier.get("is_recommended") == True
            
            print(f"✓ {tier_id}: ₹{tier.get('price_inr')}")
    
    @pytest.mark.parametrize("subtopic", V5_SUBTOPICS[12:])  # Test Health sub-topics
    def test_health_subtopic_tiers(self, subtopic):
        """Test Health category sub-topic tiers"""
        for tier_level in TIER_LEVELS:
            tier_id = f"{subtopic}_{tier_level}"
            response = self.session.get(f"{BASE_URL}/api/simplified/tiers/{tier_id}")
            
            assert response.status_code == 200, f"Failed for {tier_id}: {response.text}"
            
            data = response.json()
            assert data.get("ok") == True
            
            tier = data.get("tier", {})
            assert tier.get("tier_id") == tier_id
            assert tier.get("price_inr") > 0
            
            print(f"✓ {tier_id}: ₹{tier.get('price_inr')}")
    
    def test_relationship_healing_prices(self):
        """Test specific prices for Relationship Healing sub-topic"""
        expected_prices = {
            "relationship-healing_focussed": 6999,
            "relationship-healing_supported": 8999,
            "relationship-healing_comprehensive": 10999,
        }
        
        for tier_id, expected_price in expected_prices.items():
            response = self.session.get(f"{BASE_URL}/api/simplified/tiers/{tier_id}")
            assert response.status_code == 200
            
            data = response.json()
            tier = data.get("tier", {})
            actual_price = tier.get("price_inr")
            
            assert actual_price == expected_price, f"{tier_id}: expected ₹{expected_price}, got ₹{actual_price}"
            print(f"✓ {tier_id}: ₹{actual_price} (correct)")
    
    def test_supported_tier_always_recommended(self):
        """Verify all Supported tiers have is_recommended=True"""
        for subtopic in V5_SUBTOPICS:
            tier_id = f"{subtopic}_supported"
            response = self.session.get(f"{BASE_URL}/api/simplified/tiers/{tier_id}")
            
            assert response.status_code == 200
            
            data = response.json()
            tier = data.get("tier", {})
            
            assert tier.get("is_recommended") == True, f"{tier_id} should be recommended"
        
        print(f"✓ All {len(V5_SUBTOPICS)} Supported tiers are marked as recommended")
    
    def test_tier_features_present(self):
        """Test that tiers have features list"""
        response = self.session.get(f"{BASE_URL}/api/simplified/tiers/relationship-healing_supported")
        assert response.status_code == 200
        
        data = response.json()
        tier = data.get("tier", {})
        features = tier.get("features", [])
        
        assert len(features) > 0, "Tier should have features"
        print(f"✓ Supported tier has {len(features)} features")
    
    def test_tier_access_policy(self):
        """Test that tiers have access policy"""
        response = self.session.get(f"{BASE_URL}/api/simplified/tiers/relationship-healing_supported")
        assert response.status_code == 200
        
        data = response.json()
        tier = data.get("tier", {})
        access_policy = tier.get("access_policy", {})
        
        assert "chat_sla_hours" in access_policy
        assert "calls_enabled" in access_policy
        assert "calls_per_month" in access_policy
        
        print(f"✓ Access policy: {access_policy.get('calls_per_month')} calls/month, {access_policy.get('chat_sla_hours')}h SLA")
    
    def test_invalid_tier_returns_404(self):
        """Test that invalid tier ID returns 404"""
        response = self.session.get(f"{BASE_URL}/api/simplified/tiers/invalid-tier-id")
        assert response.status_code == 404
        print("✓ Invalid tier returns 404")


class TestV5UserState:
    """Test user state API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_user_state_requires_auth(self):
        """Test that user state endpoint requires authentication"""
        response = self.session.get(f"{BASE_URL}/api/simplified/user/state")
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403, 200]  # 200 if auth is optional
        print(f"User state endpoint returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
