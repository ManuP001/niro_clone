#!/bin/bash

# Test the welcome endpoint fix

echo "Testing Welcome Endpoint Fix..."

# Step 1: Register user
echo "1. Registering user..."
AUTH_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/auth/identify" \
  -H "Content-Type: application/json" \
  -d '{"identifier": "welcome-fix-test@example.com"}')

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

# Step 3: Get profile to verify it was saved
echo "3. Getting profile..."
GET_PROFILE_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/profile/" \
  -H "Authorization: Bearer $TOKEN")

echo "Get profile response: $GET_PROFILE_RESPONSE"

# Step 4: Test welcome endpoint
echo "4. Testing welcome endpoint..."
START_TIME=$(date +%s%N)
WELCOME_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/profile/welcome" \
  -H "Authorization: Bearer $TOKEN" \
  --max-time 15)
END_TIME=$(date +%s%N)

DURATION_MS=$(( (END_TIME - START_TIME) / 1000000 ))

echo "Welcome response: $WELCOME_RESPONSE"
echo "Response time: ${DURATION_MS}ms"

# Check if response contains expected fields
if echo "$WELCOME_RESPONSE" | grep -q '"ok":true'; then
  echo "✅ Welcome endpoint working!"
  
  # Check for personalized message
  if echo "$WELCOME_RESPONSE" | grep -q '"welcome_message"'; then
    echo "✅ Welcome message field present"
    
    # Extract message length
    MESSAGE=$(echo $WELCOME_RESPONSE | grep -o '"welcome_message":"[^"]*"' | cut -d'"' -f4)
    MESSAGE_LENGTH=${#MESSAGE}
    echo "Message length: $MESSAGE_LENGTH characters"
    
    if [ $MESSAGE_LENGTH -gt 50 ]; then
      echo "✅ Message has sufficient content"
    else
      echo "⚠️ Message might be too short"
    fi
    
    # Check for astrological content
    if echo "$MESSAGE" | grep -qiE "(ascendant|moon|sun|sign|trait|chart)"; then
      echo "✅ Contains astrological content"
    else
      echo "⚠️ No obvious astrological content detected"
    fi
    
    # Check response time
    if [ $DURATION_MS -lt 10000 ]; then
      echo "✅ Fast response (${DURATION_MS}ms < 10s)"
    else
      echo "⚠️ Slow response (${DURATION_MS}ms)"
    fi
    
  else
    echo "❌ No welcome_message field"
  fi
else
  echo "❌ Welcome endpoint failed"
fi

echo "Testing complete!"