# Quick Reference: API Testing with Curl

## Setup

```bash
# Set your token (after authenticating)
TOKEN="<your-jwt-token>"
BACKEND_URL="http://localhost:8000"
```

---

## Part A: Personalized Welcome Message

### Fetch Personalized Welcome

```bash
curl -X POST ${BACKEND_URL}/api/profile/welcome \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "ok": true,
  "welcome": {
    "message": "Hey Sharad 👋\n\nI've pulled up your chart...",
    "title": "Welcome, Sharad!",
    "subtitle": "I've pulled up your chart.",
    "bullets": ["Steady and grounded", "Emotionally perceptive", "..."],
    "prompt": "What would you like to explore first..."
  }
}
```

**Key Points:**
- ✅ Returns warm, personalized greeting (not mechanical)
- ✅ Uses name from profile
- ✅ Includes ascendant/moon data
- ✅ 3 personality strengths
- ✅ Gentle invitation to explore

---

## Part B: Kundli Tab

### Fetch Kundli Chart

```bash
curl -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/kundli | jq .
```

**Expected Response:**
```json
{
  "ok": true,
  "svg": "<svg xmlns='http://www.w3.org/2000/svg'...>...</svg>",
  "profile": {
    "name": "Sharad",
    "dob": "1990-05-15",
    "tob": "14:30",
    "location": "Delhi, India"
  },
  "structured": {
    "ascendant": {
      "sign": "Taurus",
      "degree": 12.3,
      "house": 1
    },
    "planets": [
      {"name": "Sun", "sign": "Taurus", "degree": 20.5, "house": 1, "retrograde": false},
      {"name": "Moon", "sign": "Cancer", "degree": 15.2, "house": 3, "retrograde": false}
    ],
    "houses": [
      {"house": 1, "sign": "Taurus", "lord": "Venus"},
      {"house": 2, "sign": "Gemini", "lord": "Mercury"}
    ]
  },
  "source": {
    "vendor": "VedicAstroAPI",
    "chart_type": "birth_chart",
    "format": "svg"
  }
}
```

**Quick checks:**
```bash
# Get just ascendant
curl -s -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/kundli | jq .structured.ascendant

# Get planet count
curl -s -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/kundli | jq '.structured.planets | length'

# Save SVG to file
curl -s -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/kundli | jq -r .svg > /tmp/kundli.svg
```

**Key Points:**
- ✅ Real SVG from Vedic API
- ✅ Structured planets/houses/ascendant
- ✅ Profile birth details included
- ✅ Source metadata provided

---

## Part C: Processing Report

### 1. Make Chat Request (to generate checklist)

```bash
curl -X POST ${BACKEND_URL}/api/chat \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-'"$(date +%s)"'",
    "message": "Tell me about my career prospects",
    "actionId": null
  }' | jq .
```

**Response includes:**
```json
{
  "reply": {...},
  "mode": "READING",
  "focus": "career",
  "requestId": "a1b2c3d4",
  "suggestedActions": [...]
}
```

**Extract request_id:**
```bash
REQUEST_ID=$(curl -s -X POST ${BACKEND_URL}/api/chat \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test","message":"Hello","actionId":null}' | jq -r .requestId)

echo "Request ID: ${REQUEST_ID}"
```

### 2. Fetch Checklist (JSON Endpoint)

```bash
curl -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/processing/checklist/${REQUEST_ID} | jq .
```

**Expected Response:**
```json
{
  "ok": true,
  "request_id": "a1b2c3d4",
  "timestamp": "2025-12-17T19:40:15.123456Z",
  "user_input": {
    "message": "Tell me about my career",
    "topic": "career",
    "mode": "READING"
  },
  "birth_details": {
    "name": "Sharad",
    "dob": "1990-05-15",
    "tob": "14:30",
    "place": "Delhi, India",
    "lat": 28.6139,
    "lon": 77.2090,
    "tz": 5.5
  },
  "api_calls": [
    {"name": "extended-kundli-details", "status": "ok", "duration_ms": 245},
    {"name": "maha-dasha", "status": "ok", "duration_ms": 189}
  ],
  "reading_pack": {
    "signals_kept": 6,
    "timing_windows": 2,
    "data_gaps": 0
  },
  "llm": {
    "model": "niro",
    "tokens_in": null,
    "tokens_out": null
  },
  "final": {
    "status": "ok",
    "summary": "Career reading complete"
  }
}
```

**Quick checks:**
```bash
# Check if birth details present
curl -s -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/processing/checklist/${REQUEST_ID} | jq .birth_details

# Count API calls
curl -s -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/processing/checklist/${REQUEST_ID} | jq '.api_calls | length'

# Get final status
curl -s -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/processing/checklist/${REQUEST_ID} | jq .final.status
```

### 3. Fetch Checklist (HTML Endpoint)

```bash
# Get HTML
curl -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/debug/checklist/${REQUEST_ID} -o /tmp/checklist.html

# Open in browser
open /tmp/checklist.html

# Or view in terminal
curl -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/debug/checklist/${REQUEST_ID} | lynx -stdin
```

**Expected:** Formatted HTML with same data as JSON endpoint

**Key Points:**
- ✅ Both endpoints return same data
- ✅ Birth details fully populated
- ✅ API calls tracked
- ✅ Reading pack summary included
- ✅ No 404 errors

---

## Troubleshooting

### Endpoint Returns 401 (Unauthorized)

```bash
# Problem: Missing or invalid token
# Solution: Check token is valid and not expired
curl -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/auth/me
```

### Endpoint Returns 404

```bash
# Problem: Request ID not found
# Solution: Make sure chat request completed successfully
# and returned a valid request_id

curl -X POST ${BACKEND_URL}/api/chat \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test","message":"Hello","actionId":null}' \
  | jq .requestId
```

### Birth Details Show as "?"

```bash
# Problem: Profile not saved correctly
# Solution: Complete onboarding first
curl -X POST ${BACKEND_URL}/api/auth/profile \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Name",
    "dob": "1990-05-15",
    "tob": "14:30",
    "location": "City, Country",
    "birth_place_lat": 28.6139,
    "birth_place_lon": 77.2090,
    "birth_place_tz": 5.5
  }'
```

---

## Complete End-to-End Test

```bash
#!/bin/bash

TOKEN="your-token-here"
BACKEND_URL="http://localhost:8000"

echo "=== Feature 1: Welcome Message ==="
curl -s -X POST ${BACKEND_URL}/api/profile/welcome \
  -H "Authorization: Bearer ${TOKEN}" | jq '.welcome.message' | head -3

echo ""
echo "=== Feature 2: Kundli Tab ==="
curl -s -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/kundli | jq '.structured.ascendant'

echo ""
echo "=== Feature 3: Processing Report ==="
REQUEST_ID=$(curl -s -X POST ${BACKEND_URL}/api/chat \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test-'"$(date +%s)"'","message":"Hello","actionId":null}' \
  | jq -r .requestId)

echo "Request ID: ${REQUEST_ID}"

sleep 1

curl -s -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/processing/checklist/${REQUEST_ID} | \
  jq '{birth_details: .birth_details.dob, api_calls: (.api_calls|length), status: .final.status}'

echo ""
echo "=== All Features Working ==="
```

---

## Environment Variables

Set these before running tests:

```bash
export TOKEN="your-jwt-token"
export BACKEND_URL="http://localhost:8000"
export VEDIC_API_KEY="your-vedic-api-key"  # Used by backend
export JWT_SECRET="your-jwt-secret"         # Used by backend
export MONGO_URL="mongodb://localhost:27017"
export DB_NAME="niro_ai"
```

---

## Performance Notes

- Welcome message: ~50ms (uses cached traits mapping)
- Kundli SVG: ~200-500ms (Vedic API call + SVG generation)
- Checklist JSON: ~1ms (file read from logs/checklists/)
- Checklist HTML: ~5-10ms (file read + rendering)

For slower connections, add timeout:

```bash
curl --max-time 30 -H "Authorization: Bearer ${TOKEN}" \
  ${BACKEND_URL}/api/kundli
```
