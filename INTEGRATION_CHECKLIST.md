# Integration Checklist & Verification

## Pre-Integration Setup

- [ ] Python 3.9+ running
- [ ] Backend server running on port 8000
- [ ] Frontend running on port 3000
- [ ] aiosqlite installed: `pip install aiosqlite`

---

## Step 1: Update server.py

**File:** `backend/server.py`

**Add imports** (after existing imports):
```python
from backend.services.astro_database import get_astro_db
from backend.routes.astro_routes import router as astro_router
from backend.routes.debug_routes import router as debug_router
```

**Add startup hook** (after existing startup/shutdown):
```python
@app.on_event("startup")
async def init_astro_db():
    """Initialize astro database on startup."""
    db = await get_astro_db()
    logger.info("✓ Astro database initialized")
```

**Include routers** (after other router includes):
```python
app.include_router(astro_router)
app.include_router(debug_router)
```

**Verify:** Run `python3 -m py_compile backend/server.py` (should have no output)

---

## Step 2: Verify Database Creation

After restarting backend, check:
```bash
ls -la backend/data/astro_data.db
sqlite3 backend/data/astro_data.db ".tables"
```

Should show:
```
astro_profiles  birth_profiles  pipeline_traces
```

---

## Step 3: Test API Endpoints

### Test 3a: Onboarding Complete
```bash
curl -X POST http://localhost:8000/api/astro/onboarding/complete \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "dob": "1990-06-21",
    "tob": "14:30",
    "place_text": "Mumbai"
  }' | jq .
```

**Expected Response:**
```json
{
  "birth_profile_id": "uuid",
  "astro_profile_id": "uuid",
  "status": "ok",
  "error": null,
  "message": "Onboarding completed successfully"
}
```

**Verification Checklist:**
- [ ] HTTP 200 response
- [ ] `status` is "ok"
- [ ] `error` is null
- [ ] Both profile IDs present (non-empty UUIDs)
- [ ] Check database: `sqlite3 backend/data/astro_data.db "SELECT COUNT(*) FROM birth_profiles;"`

---

### Test 3b: Fetch Astro Profile
```bash
curl http://localhost:8000/api/astro/profile \
  -H "Authorization: Bearer test_token" | jq .
```

**Expected Response:**
```json
{
  "data": {
    "user_id": "test_user",
    "provider": "vedic_api",
    "status": "ok",
    "ascendant": {
      "sign": "Leo",
      "degree": 15.5,
      "house": 1
    },
    "planets": [
      {
        "name": "Sun",
        "sign": "Gemini",
        "degree": 28.3,
        "house": 10,
        "retrograde": false
      },
      ...
    ],
    "houses": [
      {"house": 1, "sign": "Leo", "degree": 15.5},
      ...
    ],
    "kundli_svg": "<svg>...</svg>",
    "error": null
  },
  "cached": false,
  "served_at": "2025-12-18T..."
}
```

**Verification Checklist:**
- [ ] HTTP 200 response
- [ ] `data.status` is "ok"
- [ ] `data.ascendant.degree` is NOT 0.0
- [ ] `data.planets` has at least 7 planets
- [ ] Each planet has non-zero degree
- [ ] `data.houses` has exactly 12 houses
- [ ] `data.kundli_svg` is a non-empty string

---

### Test 3c: Get Kundli SVG
```bash
curl http://localhost:8000/api/astro/kundli-svg \
  -H "Authorization: Bearer test_token" | jq .
```

**Expected Response:**
```json
{
  "svg": "<svg viewBox=\"0 0 400 400\"...></svg>",
  "provider": "vedic_api",
  "computed_at": "2025-12-18T..."
}
```

**Verification Checklist:**
- [ ] HTTP 200 response
- [ ] `svg` starts with `<svg`
- [ ] `svg` ends with `</svg>`
- [ ] `provider` is set

---

### Test 3d: Get Chat Context
```bash
curl http://localhost:8000/api/astro/chat-context \
  -H "Authorization: Bearer test_token" | jq .
```

**Expected Response:**
```json
{
  "user_id": "test_user",
  "user_name": "Test User",
  "birth_summary": "Born 1990-06-21 at 14:30 in Mumbai",
  "sun_sign": "Gemini",
  "moon_sign": "Virgo",
  "ascendant_sign": "Leo",
  "personality_highlights": [
    {
      "title": "Sun Sign Influence",
      "description": "...",
      "astrological_basis": "Sun in Gemini"
    },
    ...
  ],
  "guardrails": [
    "Do not invent astro data...",
    ...
  ]
}
```

**Verification Checklist:**
- [ ] HTTP 200 response
- [ ] `personality_highlights` has at least 3 items
- [ ] `guardrails` is non-empty
- [ ] `sun_sign`, `moon_sign`, `ascendant_sign` all set (not "Unknown")

---

### Test 3e: Get Pipeline Trace
```bash
curl "http://localhost:8000/api/debug/pipeline-trace/latest?user_id=test_user" \
  -H "Authorization: Bearer test_token" | jq .
```

**Expected Response:**
```json
{
  "trace": {
    "run_id": "uuid",
    "user_id": "test_user",
    "created_at": "2025-12-18T...",
    "steps": [
      {
        "step_id": "ONBOARDING_CAPTURE",
        "status": "success",
        "duration_ms": 50,
        "inputs": {...},
        "outputs": {...},
        "quality_flags": [],
        "error": null
      },
      {
        "step_id": "LOCATION_NORMALIZE",
        "status": "success",
        ...
      },
      {
        "step_id": "ASTRO_CACHE_CHECK",
        "status": "success",
        ...
      },
      {
        "step_id": "ASTRO_PROVIDER_REQUEST",
        "status": "success",
        ...
      },
      {
        "step_id": "ASTRO_RESPONSE_NORMALIZE",
        "status": "success",
        ...
      },
      {
        "step_id": "ASTRO_PROFILE_PERSIST",
        "status": "success",
        ...
      }
    ],
    "overall_status": "success",
    "success": true,
    "degraded": false,
    "total_duration_ms": 950
  },
  "rendered_at": "2025-12-18T..."
}
```

**Verification Checklist:**
- [ ] HTTP 200 response
- [ ] 6 steps present in correct order
- [ ] All steps have `status: "success"`
- [ ] `overall_status` is "success"
- [ ] `success` is true
- [ ] `degraded` is false
- [ ] `total_duration_ms` > 0
- [ ] Each step has `duration_ms` > 0

---

### Test 3f: HTML Rendering
```bash
curl "http://localhost:8000/api/debug/pipeline-trace/render-html?user_id=test_user" \
  -H "Authorization: Bearer test_token"
```

**Expected Response:** HTML table with pipeline steps, status colors, timing

**Verification Checklist:**
- [ ] HTTP 200 response
- [ ] Content-Type is text/html
- [ ] Table visible with 6 rows
- [ ] Status colors shown (green for success, red for fail)
- [ ] All columns visible (step, name, status, duration, flags, error)

---

## Step 4: Test Error Cases

### Test 4a: Invalid Location
```bash
curl -X POST http://localhost:8000/api/astro/onboarding/complete \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "dob": "1990-06-21",
    "tob": "14:30",
    "place_text": "XyZ_Invalid_City_123"
  }' | jq .
```

**Expected Response:**
```json
{
  "birth_profile_id": "uuid",
  "astro_profile_id": "",
  "status": "error",
  "error": {
    "code": "geocode_failed",
    "message": "Could not normalize location: 'XyZ_Invalid_City_123'",
    "details": "..."
  },
  "message": "Location normalization failed: ..."
}
```

**Verification Checklist:**
- [ ] HTTP 200 response (error is valid response)
- [ ] `status` is "error"
- [ ] `error.code` is "geocode_failed"
- [ ] `message` describes the failure
- [ ] Check database trace: `sqlite3 backend/data/astro_data.db "SELECT COUNT(*) FROM pipeline_traces WHERE user_id='test_user';"`
- [ ] Trace shows "LOCATION_NORMALIZE" as FAILED

---

### Test 4b: Missing Profile
```bash
curl http://localhost:8000/api/astro/kundli-svg \
  -H "Authorization: Bearer nonexistent_user_token"
```

**Expected Response:**
```json
{
  "detail": "No astro profile found"
}
```

**Verification Checklist:**
- [ ] HTTP 404 response
- [ ] Error message is clear

---

## Step 5: Database Verification

```bash
# Count records
sqlite3 backend/data/astro_data.db "SELECT COUNT(*) as birth_profiles FROM birth_profiles;"
sqlite3 backend/data/astro_data.db "SELECT COUNT(*) as astro_profiles FROM astro_profiles;"
sqlite3 backend/data/astro_data.db "SELECT COUNT(*) as pipeline_traces FROM pipeline_traces;"

# View latest trace
sqlite3 backend/data/astro_data.db "SELECT run_id, user_id, created_at FROM pipeline_traces ORDER BY created_at DESC LIMIT 1;"

# View astro profile status
sqlite3 backend/data/astro_data.db "SELECT user_id, provider, status FROM astro_profiles ORDER BY computed_at DESC LIMIT 1;"
```

---

## Step 6: Frontend Integration

### Update Kundli Tab
**File:** `frontend/src/components/screens/KundliScreen.jsx`

Replace profile fetch with:
```javascript
const fetchProfile = async () => {
  const response = await fetch('/api/astro/profile', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (!response.ok) {
    setError('Failed to load profile');
    return;
  }
  
  const { data } = await response.json();
  
  if (data.status === 'error') {
    setError(data.error.message);
    return;
  }
  
  // Render SVG
  setSvgContent(data.kundli_svg);
  setProfile(data);
};
```

### Update Chat/Welcome Tab
**File:** `frontend/src/components/screens/ChatScreen.jsx`

Replace context fetch with:
```javascript
const fetchContext = async () => {
  const response = await fetch('/api/astro/chat-context', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const context = await response.json();
  
  // Use in LLM prompt
  const systemPrompt = `
    User: ${context.user_name}
    Birth: ${context.birth_summary}
    Sun: ${context.sun_sign}
    Moon: ${context.moon_sign}
    Ascendant: ${context.ascendant_sign}
    
    Guardrails:
    ${context.guardrails.join('\n')}
  `;
  
  return systemPrompt;
};
```

### Update Match/Checklist Tab
**File:** `frontend/src/components/screens/MatchScreen.jsx` (or ChecklistScreen)

Replace with:
```javascript
const fetchTrace = async () => {
  const response = await fetch('/api/debug/pipeline-trace/latest', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const { trace } = await response.json();
  
  return (
    <div className="pipeline-trace">
      <h3>Astro Pipeline Execution</h3>
      <p>Status: {trace.overall_status} | Duration: {trace.total_duration_ms}ms</p>
      <table>
        <thead>
          <tr>
            <th>Step</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Quality Flags</th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody>
          {trace.steps.map((step) => (
            <tr key={step.step_id}>
              <td>{step.display_name}</td>
              <td>{step.status}</td>
              <td>{step.duration_ms}ms</td>
              <td>{step.quality_flags.join(', ') || '-'}</td>
              <td>{step.error?.message || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

---

## Final Verification Checklist

- [ ] server.py compiles without errors
- [ ] Backend starts without errors
- [ ] Database created at `backend/data/astro_data.db`
- [ ] All 6 API endpoints respond (200 or 404 as appropriate)
- [ ] Onboarding creates birth + astro profile
- [ ] Pipeline trace has 6 steps
- [ ] Kundli tab shows real planet degrees (not 0.0)
- [ ] Kundli shows 12 unique houses
- [ ] Chat context has personality highlights
- [ ] Match/Checklist shows pipeline trace
- [ ] Error case returns proper error codes
- [ ] Database has records after test

---

## Rollback Plan

If issues occur:

1. **Remove routers from server.py** (undo step 1)
2. **Delete database:** `rm backend/data/astro_data.db`
3. **Restart backend:** `pkill -9 -f "python3 -m uvicorn"`
4. Previous endpoints will work (old code)

---

## Success Criteria

✅ All API endpoints responding
✅ Pipeline trace complete with 6 steps
✅ Kundli shows real degrees, 12 houses
✅ No 0.0° degrees anywhere
✅ Error cases explicit (not silent fallback)
✅ Match/Checklist shows execution trace
✅ Chat uses derived context (same source of truth)

---

**Status:** Ready for integration testing
**Last Updated:** 2025-12-18
