#!/bin/bash

# Test the chat fixes using curl commands

echo "Testing NIRO Chat Fixes with curl..."

# Step 1: Register user
echo "1. Registering user..."
AUTH_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/auth/identify" \
  -H "Content-Type: application/json" \
  -d '{"identifier": "chatfix-test@example.com"}')

echo "Auth response: $AUTH_RESPONSE"

# Extract token
TOKEN=$(echo $AUTH_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "Token: $TOKEN"

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token"
  exit 1
fi

# Step 2: Create profile
echo "2. Creating profile..."
PROFILE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/profile/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Test User",
    "dob": "1990-05-15",
    "tob": "14:30",
    "location": "Mumbai",
    "birth_place_lat": 19.08,
    "birth_place_lon": 72.88,
    "birth_place_tz": 5.5
  }')

echo "Profile response: $PROFILE_RESPONSE"

# Step 3: Test welcome endpoint
echo "3. Testing welcome endpoint..."
WELCOME_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/profile/welcome" \
  -H "Authorization: Bearer $TOKEN" \
  --max-time 30)

echo "Welcome response: $WELCOME_RESPONSE"

# Step 4: Test chat endpoint
echo "4. Testing chat endpoint..."
CHAT_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "sessionId": "chatfix_test_123",
    "message": "should I start a business or a job?",
    "actionId": null
  }' \
  --max-time 30)

echo "Chat response: $CHAT_RESPONSE"

echo "Testing complete!"