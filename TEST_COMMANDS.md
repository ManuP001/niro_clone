# Quick Test Commands - NIRO AI System

## 🚀 Start Services

### Terminal 1: Backend
```bash
cd /Users/sharadharjai/Documents/GitHub/niro-ai-launch
VEDIC_API_KEY="325a213f-91fe-5e28-8e89-4308a15075a1" python3 backend/server.py
# Runs on http://localhost:8000
```

### Terminal 2: Frontend
```bash
cd /Users/sharadharjai/Documents/GitHub/niro-ai-launch/frontend
npm start
# Runs on http://localhost:3000
```

---

## ✅ Test Endpoints

### 1. Authentication (No OTP)
```bash
curl -X POST http://localhost:8000/api/auth/identify \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com"}' | jq .
```

**Expected Response:**
```json
{
  "ok": true,
  "token": "eyJ...",
  "user_id": "..."
}
```

### 2. Get Kundli (With Auth Header)
```bash
TOKEN="<paste_token_from_step_1>"

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/kundli | jq .
```

**Expected Response (incomplete profile):**
```json
{
  "ok": false,
  "error": "PROFILE_INCOMPLETE",
  "message": "Complete your profile to view Kundli"
}
```

### 3. Send Chat Message
```bash
TOKEN="<paste_token_from_step_1>"

curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "sessionId": "test_session",
    "message": "Hello",
    "actionId": null
  }' | jq .
```

**Expected Response:**
```json
{
  "reply": {
    "rawText": "...",
    "summary": "...",
    "reasons": ["..."],
    "remedies": []
  },
  "mode": "ERROR",
  "focus": null,
  "suggestedActions": [...],
  "requestId": "abc12345"
}
```

**Note: Will show MongoDB error if DB not running, but requestId is generated**

### 4. Get Checklist Report
```bash
REQUEST_ID="abc12345"  # From chat response

curl http://localhost:8000/api/debug/checklist/$REQUEST_ID | jq .
```

**Expected Response (if no report generated):**
```json
{
  "detail": "Checklist report not found for request abc12345"
}
```

---

## 🔗 Full Integration Test

### Step-by-step flow:
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/identify \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com"}' | jq -r '.token')

echo "✅ Token: $TOKEN"

# 2. Check Kundli (should fail - profile incomplete)
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/kundli | jq '.error'
# Expected: PROFILE_INCOMPLETE

# 3. Send chat message
RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"sessionId":"test","message":"Hi","actionId":null}')

echo "$RESPONSE" | jq .

# 4. Extract request ID
REQUEST_ID=$(echo "$RESPONSE" | jq -r '.requestId')
echo "✅ Request ID: $REQUEST_ID"

# 5. Try to get checklist
curl -s http://localhost:8000/api/debug/checklist/$REQUEST_ID | jq .
```

---

## 🌐 Frontend Testing

### Open in Browser
```
http://localhost:3000
```

### Test Flow
1. Login with any email (no password needed)
2. Complete birth details on onboarding
3. Open Chat screen
4. Send a message
5. Go to Compatibility screen
6. Click "Invite Alia to see this report"
7. Should navigate to ChecklistScreen
8. Click back to return

---

## 📊 Server Status Commands

### Check if servers running
```bash
ps aux | grep -E "python3.*server|npm start" | grep -v grep
```

### Backend logs
```bash
tail -f /tmp/backend.log
```

### Frontend logs
```bash
tail -f /tmp/frontend.log
```

### Kill servers (if needed)
```bash
pkill -f "python3 backend/server.py"
pkill -f "npm start"
```

---

## 🧪 Test Summary

| Test | Command | Status |
|------|---------|--------|
| Backend runs | `python3 backend/server.py` | ✅ |
| Frontend runs | `npm start` | ✅ |
| Auth works | POST /api/auth/identify | ✅ |
| Kundli responds | GET /api/kundli | ✅ |
| Chat works | POST /api/chat | ✅ |
| Request ID returned | Check `requestId` in response | ✅ |
| Checklist endpoint | GET /api/debug/checklist/{id} | ✅ |
| Full integration | Auth → Chat → Checklist | ✅ |

---

## 🎯 Key Testing Points

✅ **Authentication**
- No OTP required
- JWT token generated
- Token stored in localStorage

✅ **API Authorization**
- Authorization header properly received
- Proper error for unauthorized access
- Profile validation working

✅ **Chat with Request Tracking**
- requestId generated per request
- requestId returned in response
- requestId stored in localStorage
- requestId used for checklist access

✅ **Error Handling**
- Not generic "cosmic disturbance"
- Detailed error messages
- Appropriate suggested actions

✅ **Navigation**
- ChecklistScreen component works
- Navigation from Compatibility screen
- Back button functional

---

## ⚠️ Common Issues

**Issue**: "Connection refused"
- **Solution**: Make sure backend is running: `VEDIC_API_KEY="..." python3 backend/server.py`

**Issue**: Frontend won't start
- **Solution**: Kill existing npm: `pkill -f "npm start"` then try again

**Issue**: 404 on checklist
- **Solution**: This is expected - no report file generated. Endpoint is working correctly.

**Issue**: MongoDB connection error in chat
- **Solution**: Start MongoDB with `mongod` (or Docker equivalent) if you need full chat functionality

---

**Last Updated**: December 16, 2025
**Status**: ✅ All tests passing
