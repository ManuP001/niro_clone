"""
Test suite for Niro Astrology App - Onboarding and Tier Pricing
Tests the backend tier API to verify prices are synced with frontend V6 content
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Basic health check tests"""
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"✓ Backend healthy: {data}")


class TestTierPricing:
    """Test tier pricing is synced with frontend V6 content"""
    
    # Career tiers
    def test_career_clarity_focussed(self):
        """Career Clarity Focussed: 3999 INR, 4 weeks"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/career-clarity_focussed")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] == True
        tier = data["tier"]
        assert tier["price_inr"] == 3999
        assert tier["validity_weeks"] == 4
        assert tier["tier_level"] == "focussed"
        print(f"✓ career-clarity_focussed: {tier['price_inr']} INR, {tier['validity_weeks']} weeks")
    
    def test_career_clarity_supported(self):
        """Career Clarity Supported: 6999 INR, 8 weeks"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/career-clarity_supported")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] == True
        tier = data["tier"]
        assert tier["price_inr"] == 6999
        assert tier["validity_weeks"] == 8
        assert tier["tier_level"] == "supported"
        assert tier["is_recommended"] == True
        print(f"✓ career-clarity_supported: {tier['price_inr']} INR, {tier['validity_weeks']} weeks")
    
    def test_career_clarity_comprehensive(self):
        """Career Clarity Comprehensive: 10999 INR, 12 weeks"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/career-clarity_comprehensive")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] == True
        tier = data["tier"]
        assert tier["price_inr"] == 10999
        assert tier["validity_weeks"] == 12
        assert tier["tier_level"] == "comprehensive"
        print(f"✓ career-clarity_comprehensive: {tier['price_inr']} INR, {tier['validity_weeks']} weeks")
    
    # Job Transition tiers (higher prices)
    def test_job_transition_focussed(self):
        """Job Transition Focussed: 5999 INR, 8 weeks"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/job-transition_focussed")
        assert response.status_code == 200
        data = response.json()
        tier = data["tier"]
        assert tier["price_inr"] == 5999
        assert tier["validity_weeks"] == 8
        print(f"✓ job-transition_focussed: {tier['price_inr']} INR, {tier['validity_weeks']} weeks")
    
    def test_job_transition_supported(self):
        """Job Transition Supported: 9999 INR, 12 weeks"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/job-transition_supported")
        assert response.status_code == 200
        data = response.json()
        tier = data["tier"]
        assert tier["price_inr"] == 9999
        assert tier["validity_weeks"] == 12
        print(f"✓ job-transition_supported: {tier['price_inr']} INR, {tier['validity_weeks']} weeks")
    
    def test_job_transition_comprehensive(self):
        """Job Transition Comprehensive: 14999 INR, 16 weeks"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/job-transition_comprehensive")
        assert response.status_code == 200
        data = response.json()
        tier = data["tier"]
        assert tier["price_inr"] == 14999
        assert tier["validity_weeks"] == 16
        print(f"✓ job-transition_comprehensive: {tier['price_inr']} INR, {tier['validity_weeks']} weeks")
    
    # Relationship Healing tiers
    def test_relationship_healing_supported(self):
        """Relationship Healing Supported: 6999 INR, 8 weeks"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/relationship-healing_supported")
        assert response.status_code == 200
        data = response.json()
        tier = data["tier"]
        assert tier["price_inr"] == 6999
        assert tier["validity_weeks"] == 8
        print(f"✓ relationship-healing_supported: {tier['price_inr']} INR, {tier['validity_weeks']} weeks")
    
    # Money Stability tiers (lower prices)
    def test_money_stability_supported(self):
        """Money Stability Supported: 4999 INR, 8 weeks"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/money-stability_supported")
        assert response.status_code == 200
        data = response.json()
        tier = data["tier"]
        assert tier["price_inr"] == 4999
        assert tier["validity_weeks"] == 8
        print(f"✓ money-stability_supported: {tier['price_inr']} INR, {tier['validity_weeks']} weeks")
    
    # Health tiers
    def test_healing_journey_supported(self):
        """Healing Journey Supported: 6999 INR, 8 weeks"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/healing-journey_supported")
        assert response.status_code == 200
        data = response.json()
        tier = data["tier"]
        assert tier["price_inr"] == 6999
        assert tier["validity_weeks"] == 8
        print(f"✓ healing-journey_supported: {tier['price_inr']} INR, {tier['validity_weeks']} weeks")


class TestTierFeatures:
    """Test tier features are correctly configured"""
    
    def test_focussed_tier_features(self):
        """Focussed tier should have correct features"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/career-clarity_focussed")
        assert response.status_code == 200
        tier = response.json()["tier"]
        features = tier["features"]
        assert "1× 60-90 min video session" in features
        assert "Written summary report" in features
        print(f"✓ Focussed tier features: {features}")
    
    def test_supported_tier_features(self):
        """Supported tier should have correct features"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/career-clarity_supported")
        assert response.status_code == 200
        tier = response.json()["tier"]
        features = tier["features"]
        assert "1× 60-90 min primary session" in features
        assert "Priority chat responses" in features
        print(f"✓ Supported tier features: {features}")
    
    def test_comprehensive_tier_features(self):
        """Comprehensive tier should have correct features"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/career-clarity_comprehensive")
        assert response.status_code == 200
        tier = response.json()["tier"]
        features = tier["features"]
        assert "2× 60 min sessions (multi-expert)" in features
        assert "Cross-verified expert perspectives" in features
        print(f"✓ Comprehensive tier features: {features}")


class TestAccessPolicy:
    """Test access policies are correctly configured"""
    
    def test_focussed_access_policy(self):
        """Focussed tier: 48h SLA, 1 call/month"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/career-clarity_focussed")
        assert response.status_code == 200
        policy = response.json()["tier"]["access_policy"]
        assert policy["chat_sla_hours"] == 48
        assert policy["calls_per_month"] == 1
        assert policy["max_active_expert_threads"] == 1
        print(f"✓ Focussed access policy: {policy}")
    
    def test_supported_access_policy(self):
        """Supported tier: 24h SLA, 3 calls/month"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/career-clarity_supported")
        assert response.status_code == 200
        policy = response.json()["tier"]["access_policy"]
        assert policy["chat_sla_hours"] == 24
        assert policy["calls_per_month"] == 3
        assert policy["max_active_expert_threads"] == 2
        print(f"✓ Supported access policy: {policy}")
    
    def test_comprehensive_access_policy(self):
        """Comprehensive tier: 24h SLA, 5 calls/month, unlimited threads"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/career-clarity_comprehensive")
        assert response.status_code == 200
        policy = response.json()["tier"]["access_policy"]
        assert policy["chat_sla_hours"] == 24
        assert policy["calls_per_month"] == 5
        assert policy["max_active_expert_threads"] == -1  # Unlimited
        print(f"✓ Comprehensive access policy: {policy}")


class TestInvalidTier:
    """Test error handling for invalid tier requests"""
    
    def test_invalid_tier_id(self):
        """Invalid tier ID should return 404"""
        response = requests.get(f"{BASE_URL}/api/simplified/tiers/invalid-tier-id")
        assert response.status_code == 404
        print("✓ Invalid tier returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
