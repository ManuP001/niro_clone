"""
Test Booking API Endpoints

Tests:
- POST /api/bookings/schedule - Create a booking (requires auth)
- GET /api/bookings/my-bookings - Get user's bookings (requires auth)
- GET /api/bookings/upcoming - Get upcoming bookings (requires auth)
- PUT /api/bookings/{booking_id}/cancel - Cancel a booking (requires auth)
"""
import pytest
import requests
import jwt
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://embedded-booking.preview.emergentagent.com').rstrip('/')
JWT_SECRET = "dev-secret-key-change-in-prod"  # From backend/.env


def generate_test_token(user_id="test_user_123", email="test@example.com", name="Test User"):
    """Generate a valid JWT token for testing"""
    payload = {
        "user_id": user_id,
        "email": email,
        "name": name,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


class TestHealthCheck:
    """Health check to ensure backend is running"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"✓ Backend is healthy: {data}")


class TestBookingSchedule:
    """Test booking schedule endpoint"""
    
    def test_schedule_without_auth(self):
        """Should return 401 when no auth token provided"""
        future_date = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
        booking_data = {
            "scheduled_date": future_date,
            "duration_minutes": 10,
            "call_type": "free_consultation",
            "user_name": "Test User",
            "user_email": "test@example.com",
            "notes": "Test booking"
        }
        response = requests.post(f"{BASE_URL}/api/bookings/schedule", json=booking_data)
        # 401 or 422 depending on auth check order
        assert response.status_code in [401, 422]
        print(f"✓ Schedule without auth returns {response.status_code}")
    
    def test_schedule_with_auth(self):
        """Should create booking when valid auth token provided"""
        token = generate_test_token()
        future_date = (datetime.utcnow() + timedelta(days=1, hours=10)).isoformat() + "Z"
        booking_data = {
            "scheduled_date": future_date,
            "duration_minutes": 10,
            "call_type": "free_consultation",
            "user_name": "Test User",
            "user_email": "test@example.com",
            "notes": "Test booking from pytest"
        }
        response = requests.post(
            f"{BASE_URL}/api/bookings/schedule",
            json=booking_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["ok"] == True
        assert "booking_id" in data
        assert data["booking_id"].startswith("booking_")
        print(f"✓ Booking created successfully: {data['booking_id']}")
        return data["booking_id"]
    
    def test_schedule_past_date(self):
        """Should reject booking for past date"""
        token = generate_test_token()
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
        booking_data = {
            "scheduled_date": past_date,
            "duration_minutes": 10,
            "call_type": "free_consultation",
        }
        response = requests.post(
            f"{BASE_URL}/api/bookings/schedule",
            json=booking_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200  # API returns 200 with ok=False
        data = response.json()
        assert data["ok"] == False
        assert "past" in data["message"].lower()
        print(f"✓ Past date booking rejected: {data['message']}")


class TestMyBookings:
    """Test my-bookings endpoint"""
    
    def test_my_bookings_without_auth(self):
        """Should return 401 when no auth token provided"""
        response = requests.get(f"{BASE_URL}/api/bookings/my-bookings")
        assert response.status_code == 401
        print(f"✓ My bookings without auth returns 401")
    
    def test_my_bookings_with_auth(self):
        """Should return user's bookings when authenticated"""
        token = generate_test_token()
        response = requests.get(
            f"{BASE_URL}/api/bookings/my-bookings",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] == True
        assert "bookings" in data
        assert isinstance(data["bookings"], list)
        assert "total" in data
        print(f"✓ My bookings returned {data['total']} bookings")


class TestUpcomingBookings:
    """Test upcoming bookings endpoint"""
    
    def test_upcoming_without_auth(self):
        """Should return 401 when no auth token provided"""
        response = requests.get(f"{BASE_URL}/api/bookings/upcoming")
        assert response.status_code == 401
        print(f"✓ Upcoming bookings without auth returns 401")
    
    def test_upcoming_with_auth(self):
        """Should return upcoming bookings when authenticated"""
        token = generate_test_token()
        response = requests.get(
            f"{BASE_URL}/api/bookings/upcoming",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] == True
        assert "bookings" in data
        print(f"✓ Upcoming bookings returned {len(data['bookings'])} bookings")


class TestCancelBooking:
    """Test booking cancellation"""
    
    def test_cancel_nonexistent_booking(self):
        """Should handle non-existent booking gracefully"""
        token = generate_test_token()
        response = requests.put(
            f"{BASE_URL}/api/bookings/nonexistent_booking/cancel",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] == False
        print(f"✓ Cancel non-existent booking handled: {data['message']}")


class TestBookingIntegration:
    """End-to-end booking flow test"""
    
    def test_full_booking_flow(self):
        """Test create -> get -> cancel flow"""
        token = generate_test_token(user_id="integration_test_user")
        
        # 1. Create a booking
        future_date = (datetime.utcnow() + timedelta(days=2, hours=14)).isoformat() + "Z"
        booking_data = {
            "scheduled_date": future_date,
            "duration_minutes": 10,
            "call_type": "free_consultation",
            "user_name": "Integration Test",
            "user_email": "integration@test.com",
            "notes": "Integration test booking"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/bookings/schedule",
            json=booking_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert create_response.status_code == 200
        create_data = create_response.json()
        assert create_data["ok"] == True
        booking_id = create_data["booking_id"]
        print(f"✓ Step 1: Created booking {booking_id}")
        
        # 2. Verify booking appears in my-bookings
        get_response = requests.get(
            f"{BASE_URL}/api/bookings/my-bookings",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["ok"] == True
        
        # Find our booking
        found = any(b["booking_id"] == booking_id for b in get_data["bookings"])
        assert found, f"Booking {booking_id} not found in my-bookings"
        print(f"✓ Step 2: Verified booking appears in my-bookings")
        
        # 3. Cancel the booking
        cancel_response = requests.put(
            f"{BASE_URL}/api/bookings/{booking_id}/cancel",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert cancel_response.status_code == 200
        cancel_data = cancel_response.json()
        assert cancel_data["ok"] == True
        print(f"✓ Step 3: Cancelled booking successfully")
        
        print(f"✓ Full booking flow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
