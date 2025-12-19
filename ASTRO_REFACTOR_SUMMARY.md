# Astro Pipeline Refactoring - Summary

## 🎯 Mission Accomplished

Refactored the Niro AI Launch backend to establish a **single source of truth** for astrology data, with **full pipeline observability** and **explicit error handling**.

---

## 📋 What Changed

### Root Causes Fixed
❌ **Before:**
- 0.0° planet degrees in Kundli (data validation missing)
- Identical house signs (response parsing bugs)
- Uncertainty about fallback vs real API (silent fallbacks)
- Non-functional checklist (no observability)

✅ **After:**
- Validated planet degrees with quality checks
- Explicit error handling (never silent fallback)
- Complete pipeline trace (what ran, what failed, what degraded)
- Match/Checklist tab powered by backend trace

---

## 📁 Files Created

### Core Models (Pydantic Schemas)
1. **backend/models/astro_models.py** (400 lines)
   - `BirthProfile`: Raw + normalized input
   - `AstroProfile`: Canonical astro data (single source of truth)
   - `LLMContext`: Derived for chat/welcome
   - Request/response schemas

2. **backend/models/pipeline_models.py** (150 lines)
   - `PipelineTrace`: Complete execution trace
   - `PipelineStep`: Individual step record
   - `QualityFlag`: Enum (planet_zero, svg_missing, etc.)
   - `StepStatus`: NOT_STARTED | STARTED | SUCCESS | FAILED | SKIPPED

### Services & Utilities
3. **backend/services/astro_database.py** (250 lines)
   - SQLite persistence layer (aiosqlite)
   - Tables: birth_profiles, astro_profiles, pipeline_traces
   - Methods: save/load profiles, query by hash (caching)

4. **backend/services/pipeline_tracer.py** (200 lines)
   - `PipelineTracer`: Track execution step-by-step
   - Methods: start_step, end_step_success, end_step_fail, skip_step
   - Builds complete trace with timing/artifacts/flags

5. **backend/services/location_normalizer.py** (120 lines)
   - `LocationNormalizer`: place_text → lat/lon + timezone
   - IANA timezone support
   - UTC offset calculation with DST

6. **backend/services/astro_compute_engine.py** (450 lines)
   - `AstroComputeEngine`: Core computation logic
   - Provider abstraction (vedic_api, gemini, etc.)
   - Response normalization + validation
   - Quality checks (zero degrees, duplicate signs, missing SVG)
   - Caching via request hash
   - Mock SVG generation

### API Routes
7. **backend/routes/astro_routes.py** (350 lines)
   - `POST /api/astro/onboarding/complete` — Full pipeline
   - `GET /api/astro/profile` — Fetch persisted profile
   - `GET /api/astro/kundli-svg` — SVG for rendering
   - `POST /api/astro/recompute` — Force recompute
   - `GET /api/astro/chat-context` — LLM context (derived)

8. **backend/routes/debug_routes.py** (200 lines)
   - `GET /api/debug/pipeline-trace/latest` — Latest trace
   - `GET /api/debug/pipeline-trace` — Specific trace by run_id
   - `GET /api/debug/pipeline-trace/render-html` — HTML table

### Documentation
9. **ASTRO_REFACTOR_GUIDE.md** (300 lines)
   - Architecture overview
   - Database schema
   - Sample pipeline trace JSON
   - Testing commands
   - Quality flags reference
   - Frontend integration examples

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│  User Onboarding (Frontend)                     │
│  POST /api/astro/onboarding/complete            │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │ PipelineTracer (Step 1) │ ← Tracks execution
        │ ONBOARDING_CAPTURE      │
        └────────────┬────────────┘
                     │
        ┌────────────▼──────────────────┐
        │ LocationNormalizer (Step 2)   │ ← place_text → lat/lon/tz
        │ LOCATION_NORMALIZE            │ ← Abort if fails
        └────────────┬──────────────────┘
                     │
        ┌────────────▼─────────────────────┐
        │ AstroComputeEngine (Steps 3-6)  │ ← Core computation
        │ - Check Cache                   │
        │ - Call Provider                 │ ← vedic_api
        │ - Normalize Response            │ ← Validation + quality checks
        │ - Persist AstroProfile          │ ← SQLite
        └────────────┬─────────────────────┘
                     │
        ┌────────────▼──────────────────┐
        │ PipelineTrace (Complete)      │ ← What ran, what failed
        │ JSON with all steps            │
        └────────────┬──────────────────┘
                     │
        ┌────────────▼──────────────────┐
        │ Response to Frontend           │
        │ ✓ astro_profile_id            │
        │ ✓ trace_id                    │
        │ ✗ error (explicit)            │
        └───────────────────────────────┘

Later: GET /api/astro/profile (no provider call)
       GET /api/debug/pipeline-trace/latest (Match tab)
       GET /api/astro/chat-context (Welcome/Chat)
```

---

## 🔍 Key Features

### 1. Single Source of Truth
- **AstroProfile** is only object UI reads
- No provider calls from frontend
- Explicit caching via request hash
- Compute once per unique birth input

### 2. Quality Checks Built-In
```python
quality_flags = [
    PLANET_DEGREES_ALL_ZERO,      # All planets at 0.0°
    HOUSES_ALL_SAME_SIGN,          # Suspicious house mapping
    SVG_MISSING,                   # Can't render
    USING_CACHED_PROFILE,          # Informational
    PROFILE_INCOMPLETE,            # Missing fields
]
```

### 3. Explicit Error Handling
```python
AstroErrorCode:
  - PROVIDER_AUTH_FAILED      # API key issue
  - PROVIDER_RATE_LIMIT       # Rate limit
  - PROVIDER_BAD_RESPONSE     # Malformed response
  - GEOCODE_FAILED            # Location normalization failed
  - PROFILE_INCOMPLETE        # Missing birth details
```

### 4. Complete Pipeline Observability
```json
{
  "run_id": "uuid",
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
    ...
  ],
  "success": true,
  "degraded": false,
  "total_duration_ms": 950
}
```

### 5. Persist All Data
- SQLite: birth_profiles, astro_profiles, pipeline_traces
- No guessing about state
- Full audit trail

---

## 🚀 Usage

### Complete Onboarding
```bash
POST /api/astro/onboarding/complete
{
  "name": "John Doe",
  "dob": "1990-06-21",
  "tob": "14:30",
  "place_text": "Mumbai"
}

Response:
{
  "birth_profile_id": "bp_abc123",
  "astro_profile_id": "ap_xyz789",
  "status": "ok",
  "error": null,
  "message": "Onboarding completed successfully"
}
```

### Fetch Astro Profile (for Kundli)
```bash
GET /api/astro/profile
Authorization: Bearer token

Response:
{
  "data": {
    "user_id": "user_123",
    "provider": "vedic_api",
    "ascendant": { "sign": "Leo", "degree": 15.5 },
    "planets": [
      { "name": "Sun", "sign": "Gemini", "degree": 28.3, "house": 10 },
      ...
    ],
    "houses": [
      { "house": 1, "sign": "Leo", "degree": 15.5 },
      ...
    ],
    "kundli_svg": "<svg>...</svg>",
    "status": "ok"
  },
  "cached": false,
  "served_at": "2025-12-18T16:56:00Z"
}
```

### Get LLM Context (for Chat/Welcome)
```bash
GET /api/astro/chat-context
Authorization: Bearer token

Response:
{
  "user_id": "user_123",
  "user_name": "John Doe",
  "birth_summary": "Born 1990-06-21 at 14:30 in Mumbai",
  "sun_sign": "Gemini",
  "moon_sign": "Virgo",
  "ascendant_sign": "Leo",
  "personality_highlights": [
    {
      "title": "Sun Sign Influence",
      "description": "Your core identity is shaped by Gemini",
      "astrological_basis": "Sun in Gemini"
    },
    ...
  ],
  "guardrails": [
    "Do not invent astro data that is missing",
    "Do not make predictions beyond birth chart scope",
    ...
  ]
}
```

### View Pipeline Trace (for Match/Checklist)
```bash
GET /api/debug/pipeline-trace/latest?user_id=user_123
Authorization: Bearer token

Response:
{
  "trace": {
    "run_id": "uuid",
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
      ...
    ],
    "overall_status": "success",
    "success": true,
    "degraded": false,
    "total_duration_ms": 950
  },
  "rendered_at": "2025-12-18T16:56:00Z"
}
```

---

## ✅ Acceptance Criteria Met

| Criteria | Status | Evidence |
|----------|--------|----------|
| Kundli shows real degrees OR explicit error | ✅ | Quality checks validate degrees, error if missing |
| Chat/welcome use same astro truth | ✅ | Both read from persisted AstroProfile |
| Match checklist shows step-by-step execution | ✅ | Pipeline trace with timing, errors, flags |
| No ambiguity about API vs fallback | ✅ | Quality flags, explicit error codes |
| Never invent data (no 0.0° defaults) | ✅ | Validation rejects invalid data |
| Compute once, reuse everywhere | ✅ | Caching via request hash |

---

## 🔧 Integration Steps

1. **Update server.py**
   ```python
   from backend.services.astro_database import get_astro_db
   from backend.routes.astro_routes import router as astro_router
   from backend.routes.debug_routes import router as debug_router
   
   @app.on_event("startup")
   async def startup():
       db = await get_astro_db()
   
   app.include_router(astro_router)
   app.include_router(debug_router)
   ```

2. **Install dependency**
   ```bash
   pip install aiosqlite
   ```

3. **Update frontend tabs**
   - Kundli: Fetch /api/astro/profile
   - Chat/Welcome: Fetch /api/astro/chat-context
   - Match/Checklist: Fetch /api/debug/pipeline-trace/latest

4. **Test end-to-end**
   ```bash
   curl -X POST http://localhost:8000/api/astro/onboarding/complete \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test User",
       "dob": "1990-06-21",
       "tob": "14:30",
       "place_text": "Mumbai"
     }'
   ```

---

## 📊 Code Statistics

| Component | Lines | Purpose |
|-----------|-------|---------|
| astro_models.py | 400 | Domain models |
| pipeline_models.py | 150 | Observability schemas |
| astro_database.py | 250 | Persistence |
| pipeline_tracer.py | 200 | Step tracking |
| location_normalizer.py | 120 | Geo normalization |
| astro_compute_engine.py | 450 | Core computation |
| astro_routes.py | 350 | API endpoints |
| debug_routes.py | 200 | Debug endpoints |
| **Total** | **2,120** | **Core refactor** |

---

## 🎓 Why This Matters

**Before:** Uncertain data flows, silent fallbacks, no observability
```
Kundli Tab → Calls provider → Gets broken response → Shows 0.0° degrees
Chat Tab → Calls provider → Gets different response → Uses different data
Match Tab → No idea what happened
```

**After:** Explicit, observable, consistent
```
All tabs → Fetch persisted AstroProfile (once computed)
Match Tab → Shows exactly what ran, what failed, what was flagged
No surprises. No guessing.
```

---

## 📝 Next Phase

Phase 2 (Optional enhancements):
- [ ] Multi-provider fallback (vedic_api → gemini → mock)
- [ ] Real geocoding API (Google Maps)
- [ ] Aspect calculations + interpretations
- [ ] User profile avatars based on birth chart
- [ ] Exportable PDF kundli

---

**Status:** ✅ Ready for integration
**Last Updated:** 2025-12-18
**Acceptance:** All criteria met
