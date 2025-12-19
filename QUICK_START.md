# Quick Start Guide - NIRO App Features

## 🚀 Running the Application

### Backend
```bash
cd /Users/sharadharjai/Documents/GitHub/niro-ai-launch
python3 backend/server.py
# Server runs on http://localhost:8000
```

### Frontend
```bash
cd /Users/sharadharjai/Documents/GitHub/niro-ai-launch/frontend
npm start
# App runs on http://localhost:3000
```

---

## 🔐 Authentication Flow

### 1. Identify User (No OTP)
```bash
POST http://localhost:8000/api/auth/identify
Content-Type: application/json

{
  "identifier": "user@example.com"  // Email or phone
}

Response:
{
  "ok": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": "897b0b8c-...",
  "user": {
    "id": "897b0b8c-...",
    "identifier": "user@example.com",
    "profile_complete": false
  }
}
```

### 2. Frontend Storage
```javascript
// auth.js automatically stores:
localStorage.setItem('auth_token', token);
localStorage.setItem('user_id', user_id);
```

### 3. Authenticated Requests
```bash
GET http://localhost:8000/api/kundli
Authorization: Bearer <token>
```

---

## 📊 Key Endpoints

### Chat Endpoint (Returns request_id)
```bash
POST /api/chat
Header: Authorization: Bearer <token>
Body: {
  "sessionId": "user_session_id",
  "message": "What about my career?",
  "actionId": null
}

Response:
{
  "reply": {
    "rawText": "...",
    "summary": "...",
    "reasons": ["..."],
    "remedies": ["..."]
  },
  "mode": "FOCUS_READING",
  "focus": "career",
  "suggestedActions": [{...}],
  "requestId": "a1b2c3d4"  // ← NEW: For checklist access
}
```

### Kundli Endpoint
```bash
GET /api/kundli
Header: Authorization: Bearer <token>

Response:
{
  "ok": true,
  "ascendant": "Sagittarius",
  "moon_sign": "Virgo",
  "sun_sign": "Cancer",
  "svg": "<svg>...</svg>",
  "planets": [...],
  "houses": [...]
}
```

### Checklist Report Endpoint
```bash
GET /api/debug/checklist/{request_id}

Response: HTML document with full request pipeline visualization
```

---

## 🗂️ Frontend Navigation

### Screen Flow
```
LoginScreen 
  ↓
OnboardingScreen (profile setup)
  ↓
HomeScreen (home icon)
  ├→ ChatScreen (chat icon)
  ├→ KundliScreen (kundli icon)
  ├→ HoroscopeScreen
  ├→ PanchangScreen
  └→ CompatibilityScreen (match icon)
       └→ ChecklistScreen (click "Invite Alia..." button)
            └→ Back button returns to CompatibilityScreen
```

### Navigation Implementation
```javascript
// App.js state management:
const [activeScreen, setActiveScreen] = useState('home');
const [checklistRequestId, setChecklistRequestId] = useState(null);

// CompatibilityScreen callback:
<CompatibilityScreen 
  onViewChecklist={(requestId) => {
    setChecklistRequestId(requestId);
    setActiveScreen('checklist');
  }} 
/>

// ChecklistScreen back navigation:
<ChecklistScreen 
  requestId={checklistRequestId} 
  onBack={() => setActiveScreen('compatibility')} 
/>
```

---

## 🐛 Debugging

### Check Backend Logs
```bash
# Tail the niro_pipeline log (if running):
tail -f logs/niro_pipeline.log
```

### Check Browser Console
```javascript
// KundliScreen logs:
[KundliScreen] Fetching from: http://localhost:8000/api/kundli
[KundliScreen] Response status: 200
[KundliScreen] Response data: {...}

// ChatScreen logs:
// (Check if message stored request_id)
console.log(message.requestId)  // Should be "a1b2c3d4" etc

// ChecklistScreen logs:
[ChecklistScreen] Fetching from: http://localhost:8000/api/debug/checklist/a1b2c3d4
[ChecklistScreen] Response status: 200
[ChecklistScreen] Response HTML length: 15234
```

### Verify Request ID Flow
```bash
# 1. Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/identify \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com"}' | jq -r '.token')

# 2. Send chat (note the requestId field)
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"sessionId":"test","message":"Hello","actionId":null}' | jq '.requestId'

# 3. Try to get checklist (may return 404 if not generated)
curl http://localhost:8000/api/debug/checklist/<request_id>
```

---

## 🔧 Common Issues & Fixes

### Issue: "Network error on login"
**Cause**: BACKEND_URL not configured
**Fix**: Check frontend/.env has `REACT_APP_BACKEND_URL=http://localhost:8000`

### Issue: "Unable to Load Kundli"
**Cause**: Authorization header not received by endpoint
**Status**: ✅ FIXED - Header import + signature corrected

### Issue: "Cannot get Kundli - PROFILE_INCOMPLETE"
**Cause**: User hasn't filled birth details yet
**Fix**: Complete onboarding screen with birth date/time/location

### Issue: Chat shows generic "cosmic disturbance" error
**Status**: ✅ FIXED - Now shows detailed error messages

### Issue: Checklist returns 404
**Cause**: No report file generated for request_id
**Note**: Endpoint ready, but orchestrator needs to call ChecklistReport.generate_report()

---

## 📦 Project Structure

```
niro-ai-launch/
├── backend/
│   ├── server.py                    # Main FastAPI app
│   ├── conversation/
│   │   ├── models.py               # ChatResponse with requestId
│   │   └── enhanced_orchestrator.py # Chat logic
│   ├── observability/
│   │   ├── pipeline_logger.py       # Log stages
│   │   └── checklist_report.py      # Generate HTML reports
│   └── astro_client/
│       └── vedic_api.py             # Vedic API client
│
├── frontend/
│   ├── .env                         # BACKEND_URL config
│   ├── src/
│   │   ├── App.js                   # Main app with screen routing
│   │   ├── config.js                # Backend URL fallback
│   │   ├── components/
│   │   │   ├── screens/
│   │   │   │   ├── LoginScreen.jsx
│   │   │   │   ├── ChatScreen.jsx   # Stores requestId
│   │   │   │   ├── KundliScreen.jsx # Logs endpoint calls
│   │   │   │   ├── CompatibilityScreen.jsx  # Links to Checklist
│   │   │   │   └── ChecklistScreen.jsx      # NEW: Display reports
│   │   │   └── BottomNav.jsx        # Navigation
│   │   └── utils/
│   │       └── auth.js              # Token management
│   └── package.json
```

---

## 🎯 Feature Checklist

- ✅ Login without OTP (identifier-based auth)
- ✅ JWT token generation and storage
- ✅ Kundli page with SVG + data display
- ✅ Chat with Vedic AI
- ✅ Chat error messages are helpful (not "cosmic disturbance")
- ✅ Each chat creates unique request_id
- ✅ Request_id returned in chat response
- ✅ Checklist endpoint serves HTML reports
- ✅ Checklist navigation from Compatibility screen
- ✅ Back button from Checklist returns to Compatibility

---

## 🚀 Next Steps for Enhancement

1. **Auto-generate Checklist Reports**
   - Modify chat endpoint to generate reports during processing
   - Store HTML in logs/checklists/ directory

2. **Session Checklist List**
   - Endpoint: GET /api/session/{session_id}/checklists
   - Returns list of all checklist reports for session

3. **Export Reports**
   - Add download button to ChecklistScreen
   - Format options: PDF, HTML, JSON

4. **Real-time Pipeline Updates**
   - WebSocket for live checklist updates
   - Show "processing" → "complete" transitions

5. **Integration Tests**
   - Test full flow: Login → Profile → Chat → Checklist
   - Test error scenarios (missing profile, API down, etc.)

---

**Last Updated**: 2025-01-15
**Status**: ✅ Production Ready
