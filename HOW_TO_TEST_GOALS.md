# How to Test All 4 Onboarding Goals

## Quick Start

Run the comprehensive test suite:
```bash
cd /Users/sharadharjai/Documents/GitHub/niro-ai-launch
python3 test_all_4_goals.py
```

Expected output: **✅ ALL TESTS PASSED!**

---

## Manual Testing Guide

### Goal 1: City Autocomplete

#### Via API
```bash
curl "http://localhost:8000/api/utils/search-cities?query=Rohtak&max_results=5"
```

Expected response:
```json
{
  "cities": [
    {
      "name": "Rohtak",
      "display_name": "Rohtak, Haryana, India",
      "lat": 28.8955,
      "lon": 76.6066,
      "timezone": "Asia/Kolkata",
      ...
    }
  ]
}
```

#### Via UI
1. Start frontend: `npm start` in `/frontend`
2. Go to Onboarding screen
3. Click "Place of birth" field
4. Type "Rohtak" (minimum 2 characters)
5. See dropdown suggestions appear
6. Click "Rohtak, Haryana, India"
7. Confirm location, coordinates, and timezone are populated

---

### Goal 2: Birth Context Always Used

#### Via API
```bash
# Step 1: Authenticate
TOKEN=$(curl -X POST http://localhost:8000/api/auth/identify \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com"}' | python3 -m json.tool | grep token | cut -d'"' -f4)

# Step 2: Save birth profile
curl -X POST http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "dob": "1990-05-15",
    "tob": "14:30",
    "location": "Rohtak, Haryana, India",
    "birth_place_lat": 28.8955,
    "birth_place_lon": 76.5660,
    "birth_place_tz": 5.5
  }'

# Step 3: Chat WITHOUT providing birth details
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-123",
    "message": "Tell me about my career",
    "subjectData": null
  }' | python3 -m json.tool | head -20
```

Expected behavior:
- Response `"mode"` is NOT `"BIRTH_COLLECTION"`
- Chat proceeds directly to processing message
- Chat does NOT ask for birth details

#### Via UI
1. Go through onboarding (save birth details)
2. Go to Chat screen
3. Type: "Tell me about my career prospects"
4. Chat should NOT ask for DOB/TOB/location
5. Chat should provide a reading

---

### Goal 3: Personalized Welcome

#### Via API
```bash
# Using TOKEN from Goal 2
curl -X POST http://localhost:8000/api/profile/welcome \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

Expected response:
```json
{
  "ok": true,
  "welcome": {
    "title": "🌟 Welcome to Niro.AI Chat, Test User!",
    "subtitle": "Based on your birth chart, here are 3 strengths you likely carry:",
    "bullets": [
      "Strength 1",
      "Strength 2",
      "Strength 3"
    ],
    "prompt": "Ask me anything—career, relationships, health, or timing..."
  }
}
```

Verify:
- Title includes user's name
- Exactly 3 bullets (strengths)
- NOT generic (doesn't ask for birth details)

#### Via UI
1. After onboarding, go to Chat screen
2. First message should be personalized welcome
3. Should show user's name
4. Should show 3 personality strengths
5. Should NOT be generic "Please tell me your birth details" message

---

### Goal 4: Request Checklist Shows Birth Details

#### Via API
```bash
# Get checklist using request_id from Goal 2 chat response
curl "http://localhost:8000/api/debug/checklist/{request_id}" \
  -H "Content-Type: text/html" > checklist.html

# Open in browser
open checklist.html
```

Expected content:
- DOB displayed (e.g., "1990-05-15")
- Location displayed (e.g., "Rohtak, Haryana, India")
- Timezone displayed (e.g., "5.5")
- Coordinates displayed (latitude, longitude)
- Mode displayed (e.g., "NORMAL_READING")

#### Via UI
1. Ask a chat question
2. Look for "View Details" / "Invite alia to see this report" button
3. Click to open checklist
4. Verify birth details are shown
5. Verify coordinates are present
6. Verify mode and request info are displayed

---

## Test Files

### Comprehensive Test Script
**File**: `test_all_4_goals.py`

Runs all 4 goals in sequence:
- Tests city search endpoint
- Tests profile saving with coordinates
- Tests chat with auth context
- Tests welcome endpoint
- Tests checklist retrieval and content

**Run**: 
```bash
python3 test_all_4_goals.py
```

### Debug Test Script
**File**: `debug_checklist.py`

Focused test for checklist debugging:
- Authenticates user
- Saves profile
- Makes chat request
- Fetches checklist HTML
- Checks if birth details are populated

**Run**:
```bash
python3 debug_checklist.py
```

---

## Troubleshooting

### City search returns empty
- Check that `/api/utils/search-cities` endpoint exists in server.py
- Verify `IndianCityService` is initialized
- Try searching for a known Indian city (Rohtak, Delhi, Mumbai)

### Birth details not showing in chat
- Verify token is valid (check JWT payload)
- Verify profile was saved (`profile_complete: true`)
- Check auth_service is using singleton pattern
- Verify birthDetails format in request.subjectData

### Welcome message is generic
- Verify token is being sent to `/api/profile/welcome`
- Check that profile exists for user
- Verify welcome_traits.py is imported and working
- Check for errors in backend logs

### Checklist missing birth details
- Verify birth_details_for_checklist is populated in server.py
- Check checklist_report.py HTML template includes all fields
- Verify request.subjectData.birthDetails is set before checklist generation

---

## Success Criteria - All Passing ✅

| Goal | Status | Evidence |
|------|--------|----------|
| 1. City Autocomplete | ✅ PASS | Search works, returns coordinates |
| 2. Birth Context | ✅ PASS | Chat doesn't ask for birth details |
| 3. Personalized Welcome | ✅ PASS | Shows name + 3 strengths |
| 4. Checklist Accurate | ✅ PASS | Shows DOB, location, timezone, mode |

---

## Summary of Changes

- **Frontend**: `OnboardingScreen.jsx` updated to use `/api/utils/search-cities`
- **Backend**: `server.py` enhanced to load user profile and inject birth context
- **Backend**: `checklist_report.py` updated to display coordinates and timezone
- **No new dependencies or database migrations required**
- **Production ready - can deploy immediately**
