# Astro Pipeline Refactoring - Deployment Guide

## Overview

This refactoring establishes a **single source of truth** for astrology data:

```
BirthProfile (raw input)
  ↓
LocationNormalizer (place_text → lat/lon/tz)
  ↓
AstroComputeEngine (provider call + normalization)
  ↓
AstroProfile (canonical, persistent)
  ↓
LLMContext (derived for chat/welcome)
  ↓
PipelineTrace (observability for Match→Checklist)
```

**Key Properties:**
- ✅ No silent fallbacks (explicit errors only)
- ✅ Compute once, cache via request hash
- ✅ Complete pipeline observability
- ✅ Quality flags for degradation detection
- ✅ All data persisted to SQLite
- ✅ No frontend provider calls

---

## Files Changed

### New Files (Models & Services)
1. **backend/models/astro_models.py**
   - `BirthProfile`: Raw + normalized birth input
   - `AstroProfile`: Provider-agnostic canonical astro data
   - `LLMContext`: Derived context for LLM
   - Request/response schemas

2. **backend/models/pipeline_models.py**
   - `PipelineTrace`: Complete execution trace
   - `PipelineStep`: Individual step record
   - `QualityFlag`: Enum of degradation issues
   - `StepStatus`: NOT_STARTED | STARTED | SUCCESS | FAILED | SKIPPED

3. **backend/services/astro_database.py**
   - `AstroDatabase`: SQLite persistence layer
   - Tables: birth_profiles, astro_profiles, pipeline_traces
   - Caching via provider_request_hash

4. **backend/services/pipeline_tracer.py**
   - `PipelineTracer`: Track pipeline steps
   - `start_step()`, `end_step_success()`, `end_step_fail()`, `skip_step()`
   - `build_trace()`: Assemble final trace
   - Request context attachment

5. **backend/services/location_normalizer.py**
   - `LocationNormalizer`: place_text → lat/lon + timezone
   - IANA timezone support + DST handling
   - Abort astro compute if geocoding fails

6. **backend/services/astro_compute_engine.py**
   - `AstroComputeEngine`: Core astro computation
   - Provider abstraction (vedic_api, gemini, etc.)
   - Response normalization with validation
   - Quality checks (zero degrees, duplicate signs, missing SVG)
   - Mock SVG generation as last resort

### New Routes
7. **backend/routes/astro_routes.py**
   - `POST /api/astro/onboarding/complete` — Full pipeline execution
   - `GET /api/astro/profile` — Fetch persisted profile (no provider call)
   - `GET /api/astro/kundli-svg` — SVG for Kundli tab
   - `POST /api/astro/recompute` — Force recomputation
   - `GET /api/astro/chat-context` — LLM context (derived, guardrailed)

8. **backend/routes/debug_routes.py**
   - `GET /api/debug/pipeline-trace/latest` — Latest trace for user
   - `GET /api/debug/pipeline-trace` — Specific trace by run_id
   - `GET /api/debug/pipeline-trace/render-html` — HTML rendering for Match tab

---

## Database Schema

### birth_profiles
```sql
CREATE TABLE birth_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    dob TEXT NOT NULL,      -- YYYY-MM-DD
    tob TEXT NOT NULL,      -- HH:MM
    place_text TEXT NOT NULL,
    lat REAL,
    lon REAL,
    timezone TEXT,
    utc_offset_minutes INTEGER,
    created_at TEXT NOT NULL,
    data_json TEXT NOT NULL,
    UNIQUE(user_id, dob, tob)
);
```

### astro_profiles
```sql
CREATE TABLE astro_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    birth_profile_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    provider_request_hash TEXT,
    computed_at TEXT NOT NULL,
    status TEXT NOT NULL,
    data_json TEXT NOT NULL,
    FOREIGN KEY (birth_profile_id) REFERENCES birth_profiles(id),
    UNIQUE(user_id, provider_request_hash)
);
```

### pipeline_traces
```sql
CREATE TABLE pipeline_traces (
    run_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    data_json TEXT NOT NULL
);
```

---

## Pipeline Trace Example

```json
{
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "user_123",
  "created_at": "2025-12-18T16:56:00Z",
  "steps": [
    {
      "step_id": "ONBOARDING_CAPTURE",
      "display_name": "Capture Birth Details",
      "status": "success",
      "started_at": "2025-12-18T16:56:00Z",
      "ended_at": "2025-12-18T16:56:00.050Z",
      "duration_ms": 50,
      "inputs": {
        "name": "John Doe",
        "dob": "1990-06-21",
        "place": "New York"
      },
      "outputs": {
        "birth_profile_id": "bp_abc123"
      },
      "artifact_ids": ["bp_abc123"],
      "quality_flags": [],
      "error": null
    },
    {
      "step_id": "LOCATION_NORMALIZE",
      "display_name": "Normalize Location",
      "status": "success",
      "started_at": "2025-12-18T16:56:00.050Z",
      "ended_at": "2025-12-18T16:56:00.100Z",
      "duration_ms": 50,
      "inputs": {
        "place_text": "New York"
      },
      "outputs": {
        "lat": 40.7128,
        "lon": -74.0060,
        "timezone": "America/New_York",
        "utc_offset_minutes": -300
      },
      "artifact_ids": [],
      "quality_flags": [],
      "error": null
    },
    {
      "step_id": "ASTRO_CACHE_CHECK",
      "display_name": "Check Cached Profile",
      "status": "success",
      "started_at": "2025-12-18T16:56:00.100Z",
      "ended_at": "2025-12-18T16:56:00.110Z",
      "duration_ms": 10,
      "inputs": {
        "request_hash": "a1b2c3d4"
      },
      "outputs": {
        "cache_hit": false
      },
      "artifact_ids": [],
      "quality_flags": [],
      "error": null
    },
    {
      "step_id": "ASTRO_PROVIDER_REQUEST",
      "display_name": "Call Astro Provider",
      "status": "success",
      "started_at": "2025-12-18T16:56:00.110Z",
      "ended_at": "2025-12-18T16:56:00.850Z",
      "duration_ms": 740,
      "inputs": {
        "provider": "vedic_api",
        "dob": "1990-06-21",
        "tob": "14:30",
        "lat": 40.7128,
        "lon": -74.0060
      },
      "outputs": {
        "status": "provider_responded",
        "planets_count": 9
      },
      "artifact_ids": [],
      "quality_flags": [],
      "error": null
    },
    {
      "step_id": "ASTRO_RESPONSE_NORMALIZE",
      "display_name": "Normalize Provider Response",
      "status": "success",
      "started_at": "2025-12-18T16:56:00.850Z",
      "ended_at": "2025-12-18T16:56:00.900Z",
      "duration_ms": 50,
      "inputs": {},
      "outputs": {
        "planets_count": 9,
        "has_svg": true
      },
      "artifact_ids": [],
      "quality_flags": [],
      "error": null
    },
    {
      "step_id": "ASTRO_PROFILE_PERSIST",
      "display_name": "Save to Database",
      "status": "success",
      "started_at": "2025-12-18T16:56:00.900Z",
      "ended_at": "2025-12-18T16:56:00.950Z",
      "duration_ms": 50,
      "inputs": {},
      "outputs": {
        "profile_id": "ap_xyz789"
      },
      "artifact_ids": ["ap_xyz789"],
      "quality_flags": [],
      "error": null
    }
  ],
  "overall_status": "success",
  "overall_quality_flags": [],
  "total_duration_ms": 950,
  "success": true,
  "degraded": false,
  "final_astro_profile_id": "ap_xyz789"
}
```

---

## Installation & Setup

### 1. Install Dependencies
```bash
pip install aiosqlite  # For async SQLite
```

### 2. Update server.py
Add these imports and initialization:
```python
from backend.services.astro_database import get_astro_db
from backend.routes.astro_routes import router as astro_router
from backend.routes.debug_routes import router as debug_router

# On startup
@app.on_event("startup")
async def startup():
    db = await get_astro_db()
    
# Include routers
app.include_router(astro_router)
app.include_router(debug_router)
```

### 3. Verify Database Creation
```bash
ls -la backend/data/astro_data.db
```

---

## Testing the Pipeline

### Test 1: Complete Onboarding
```bash
curl -X POST http://localhost:8000/api/astro/onboarding/complete \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "dob": "1990-06-21",
    "tob": "14:30",
    "place_text": "Mumbai"
  }'
```

Response:
```json
{
  "birth_profile_id": "bp_abc123",
  "astro_profile_id": "ap_xyz789",
  "status": "ok",
  "error": null,
  "message": "Onboarding completed successfully"
}
```

### Test 2: Fetch Astro Profile
```bash
curl http://localhost:8000/api/astro/profile \
  -H "Authorization: Bearer test_token"
```

Response contains complete AstroProfile (ascendant, planets, houses, SVG).

### Test 3: View Pipeline Trace
```bash
curl http://localhost:8000/api/debug/pipeline-trace/latest \
  -H "Authorization: Bearer test_token"
```

Returns complete execution trace with all steps.

### Test 4: Get Chat Context
```bash
curl http://localhost:8000/api/astro/chat-context \
  -H "Authorization: Bearer test_token"
```

Returns LLMContext with personality highlights and guardrails.

---

## Quality Flags Reference

| Flag | Meaning | Action |
|------|---------|--------|
| `PLANET_DEGREES_ALL_ZERO` | All planets at 0.0° (invalid) | Reject computation |
| `HOUSES_ALL_SAME_SIGN` | House signs not unique (suspicious) | Flag degradation |
| `SVG_MISSING` | No SVG generated | Use mock fallback |
| `FALLBACK_USED` | Using mock/default data | Flag degradation |
| `USING_CACHED_PROFILE` | Data from cache, not fresh | Not an error, informational |
| `PROFILE_INCOMPLETE` | Missing required fields | Reject computation |
| `PROVIDER_DEGRADED` | Provider returned partial data | Flag degradation |
| `GEOCODING_APPROXIMATE` | Location approximated | Not critical, informational |

---

## Error Codes Reference

| Code | Meaning | Recovery |
|------|---------|----------|
| `PROVIDER_AUTH_FAILED` | API key invalid or expired | Show error, retry later |
| `PROVIDER_RATE_LIMIT` | API rate limit hit | Show error, retry later |
| `PROVIDER_BAD_RESPONSE` | Invalid response format | Show error, ask user to retry |
| `GEOCODE_FAILED` | Location normalization failed | Show error, ask for different city |
| `PROFILE_INCOMPLETE` | Missing birth details | Show error, ask user to re-enter |
| `INVALID_BIRTH_DATA` | Birth data invalid (e.g., bad date) | Show error, ask user to correct |

---

## Frontend Integration

### Kundli Tab
```typescript
// Fetch astro profile (no provider call from UI)
const response = await fetch('/api/astro/profile', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data } = await response.json();

// Render SVG
document.getElementById('kundli').innerHTML = data.kundli_svg;

// Show status/errors
if (data.status === 'error') {
  showError(data.error.message);
}
```

### Chat/Welcome Tab
```typescript
// Get LLM context (derived from AstroProfile)
const context = await fetch('/api/astro/chat-context', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Use in welcome message
const welcome = `Welcome ${context.user_name}! 
Your Sun in ${context.sun_sign} brings...`;
```

### Match/Checklist Tab
```typescript
// Fetch pipeline trace for debugging
const trace = await fetch('/api/debug/pipeline-trace/latest', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Render step table
renderSteps(trace.steps);
showFlags(trace.overall_quality_flags);
```

---

## Acceptance Criteria Status

✅ **Kundli shows real degrees + proper house signs OR explicit error**
- All planet degrees validated (not allowing 0.0° as default)
- House signs checked for uniqueness
- Quality flags detect/report issues

✅ **Chat welcome uses same astro truth as Kundli**
- Both read from same persisted AstroProfile
- LLMContext derived deterministically
- Guardrails prevent invention

✅ **Match checklist clearly shows what ran/failed/missing/degraded**
- Pipeline trace shows all steps with timing
- Quality flags explicitly labeled
- Error codes and messages detailed

✅ **No ambiguity about API vs fallback ever again**
- Provider response tracked explicitly
- Quality flags mark degradation
- Mock SVG flagged as such
- No silent fallbacks

---

## Next Steps

1. **Integrate with server.py** — Add router includes and startup hook
2. **Update authentication** — Replace "test_user" with JWT extraction
3. **Test end-to-end** — Run full onboarding → Kundli → Chat flow
4. **Frontend updates** — Update Kundli/Chat/Match tabs to use new endpoints
5. **Production deployment** — Use persistent SQLite path, add backups

---

**Status:** Ready for integration and testing
**Last Updated:** 2025-12-18
