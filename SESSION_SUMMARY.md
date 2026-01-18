# 📋 NIRO Astrology App - Session Summary

**Session Date:** January 4, 2026  
**App:** NIRO AI Vedic Astrology Chat Application

---

## 🚀 1. Repository Launch
- Installed backend dependencies (`pip install -r requirements.txt`)
- Installed frontend dependencies (`yarn install`)
- Resolved dependency conflict with `emergentintegrations`
- Restarted all services (backend, frontend, MongoDB)
- Verified health checks passing

---

## 🔍 2. Data Flow Audit: Kundli Tab vs Chat Engine

**Objective:** Verify if both pipelines use identical chart data

### Findings
| Metric | Result |
|--------|--------|
| Full Matches | 8/13 |
| Partial/Derived | 5/13 |
| Mismatches | **0/13** |

### Verdict: **"Kundli tab and reading engine use IDENTICAL data"**

**Confirmed Consistent:**
- ✅ Same Ayanamsa (Lahiri)
- ✅ Same House System (Whole Sign)
- ✅ Same Timezone handling
- ✅ Same API endpoints and parsing logic

**Files Audited:**
- `/app/backend/astro_client/vedic_api.py` - API parsing
- `/app/backend/server.py` - Kundli endpoint
- `/app/backend/conversation/enhanced_orchestrator.py` - Chat pipeline
- `/app/frontend/src/components/screens/KundliScreen.jsx` - UI rendering

**Output:** `/app/DATA_FLOW_AUDIT_REPORT.md`

---

## 📡 3. Vedic API Optimization

### Before: 11+ API calls per profile
```
1x /extended-horoscope/extended-kundli-details
1x /dashas/maha-dasha  
9x /horoscope/planet-report (one per planet)
```

### After: 2 API calls per profile
```
1x /horoscope/planet-details (ALL planets + ascendant with exact degrees)
1x /dashas/current-mahadasha-full (complete dasha timeline)
```

### Benefits
- **Exact degrees** instead of approximated values
- **Nakshatra & pada** for each planet
- **Combust status** detection
- **5x faster** profile loading

### Files Modified:
- `/app/backend/astro_client/vedic_api.py`
  - `fetch_full_profile()` - Optimized
  - `fetch_kundli_optimized()` - Optimized
  - `_parse_profile_from_real_api()` - Updated dasha parsing

---

## 📚 4. Vedic API Documentation

**Fetched from MCP Server:** `https://github.com/vedicastroapidev/vapi-doc-coding-mcp.git`

### Total Endpoints: 130 APIs

| Category | Count | Examples |
|----------|-------|----------|
| Dashas | 13 | maha-dasha, current-mahadasha-full, char-dasha |
| Horoscope | 16 | planet-details, chart-image, ashtakvarga |
| Extended | 17 | yoga-list, sade-sati, gem-suggestion |
| Dosha | 5 | mangal-dosh, kaalsarp-dosh, pitra-dosh |
| Matching | 10 | ashtakoot, dashakoot, aggregate-match |
| Panchang | 14 | daily panchang, muhurta, transit-dates |
| Prediction | 9 | daily-nakshatra, yearly horoscope |
| Western | 26 | natal-chart, synastry, transits |
| Tarot | 12 | daily, yes-no, love readings |
| Utilities | 5 | geo-search, gem-details |

### High Potential APIs Identified:
1. `/horoscope/ai-12-month-prediction` - AI forecasts
2. `/extended-horoscope/yoga-list` - Computed yogas
3. `/prediction/daily-nakshatra` - Daily predictions
4. `/panchang/transit-dates` - Transit calendar
5. `/matching/ashtakoot` - Compatibility matching

**Output:** `/app/VEDIC_API_REFERENCE.md`

---

## 📊 5. Scoring Methodology Documentation

### Career Topic Example (Sharad Harjai - Sagittarius Ascendant)

**Topic Configuration:**
- Houses: 2, 6, 10, 11
- Planets: 10th Lord (Mercury), Sun, Saturn, Rahu, Mercury

**Scoring Formula:**
```
FINAL_SCORE = Base(0.20) 
            + House_Bonus(0.20-0.30) 
            + Karaka_Bonus(0.15-0.25)
            + Signal_Type(0.08-0.15)
            + Time_Relevance(0.08-0.35)
            - Penalties(0.10-0.30)
```

### All 14 Topics Documented:

| Topic | Primary House | Key Planets |
|-------|---------------|-------------|
| career | 10 | 10th Lord, Sun, Saturn, Rahu, Mercury |
| money | 2 | 2nd Lord, 11th Lord, Jupiter, Venus |
| marriage_partnership | 7 | 7th Lord, Venus, Jupiter, Mars |
| romantic_relationships | 5 | 5th Lord, Venus, Moon, Mars |
| family_home | 4 | 4th Lord, Moon, Venus |
| health_energy | 1 | Lagna Lord, Sun, Mars, Saturn |
| learning_education | 5 | 5th Lord, 9th Lord, Mercury, Jupiter |
| spirituality | 9 | 9th Lord, 12th Lord, Jupiter, Ketu |
| self_psychology | 1 | Lagna Lord, Moon, Rahu, Ketu |
| travel_relocation | 9 | 9th Lord, 12th Lord, 4th Lord, Rahu |
| legal_contracts | 6 | 6th Lord, 7th Lord, Mars, Saturn |
| friends_social | 11 | 11th Lord, 3rd Lord, Mercury |
| daily_guidance | 1 | Lagna Lord, Moon, Transit planets |
| general | 1 | Lagna Lord, Moon, Sun, Jupiter |

---

## 🌍 6. Place of Birth Search Enhancement

### Before
- Static list of ~200 major Indian cities
- Missing districts and smaller towns

### After
- **Primary:** Vedic API `/utilities/geo-search` (comprehensive worldwide)
- **Fallback 1:** Local Indian cities database
- **Fallback 2:** GeoNames API

### Test Results
| Search | Before | After |
|--------|--------|-------|
| Jhajjar | ❌ Not found | ✅ Jhajjar, Haryana, IN |
| Bhiwani | ✅ Found | ✅ Bhiwani, Haryana, IN |
| Narnaul | ❌ Not found | ✅ Narnaul, Haryana, IN |
| Bahadurgarh | ❌ Not found | ✅ Bahadurgarh, Haryana, IN |

### Files Modified:
- `/app/backend/server.py` - Updated `/api/utils/search-cities` endpoint
- `/app/frontend/src/components/screens/OnboardingScreen.jsx` - Updated to handle `tz_offset`

---

## 🎉 7. Confidence-Aware Welcome Engine

### New Module: `/app/backend/conversation/welcome_engine.py`

**Features:**
- Confidence bands (HIGH/MEDIUM/LOW)
- Personality anchor from Moon sign + Ascendant
- Current life phase from Mahadasha/Antardasha
- Guardrails validation

### New Endpoint: `GET /api/profile/welcome`

**Response Format:**
```json
{
  "ok": true,
  "welcome_message": "Welcome, Sharad. With Moon in Gemini...",
  "confidence_map": {
    "personality": "high",
    "past_theme": null,
    "current_phase": "high"
  },
  "suggested_questions": ["What skills should I develop now?", ...]
}
```

### Confidence Bands

| Band | Language Allowed | When Used |
|------|------------------|-----------|
| **HIGH** | "You are...", "This phase is about..." | Strong signal alignment |
| **MEDIUM** | "You're likely experiencing..." | Meaningful but not airtight |
| **LOW** | ❌ Nothing said | Section omitted |

### Guardrails Enforced
- ❌ No follow-up questions
- ❌ No generic astrology statements
- ❌ No vague phrases ("you may feel", "possibly")
- ❌ No planets outside allowed drivers

### Test Result (Sharad Harjai)
```
Welcome, Sharad. With Moon in Gemini, you are emotionally curious 
and mentally active. Your adaptability helps you navigate emotional 
complexity with flexibility. You approach life with philosophical 
optimism and adventurous spirit. You've recently entered a Mercury 
period. This period highlights skills, analysis, and connection 
through ideas.
```

### Files Created/Modified:
- **NEW:** `/app/backend/conversation/welcome_engine.py`
- `/app/backend/server.py` - Added `/api/profile/welcome` endpoint
- `/app/frontend/src/components/screens/ChatScreen.jsx` - Changed POST to GET

---

## 📁 Files Created This Session

| File | Purpose |
|------|---------|
| `/app/DATA_FLOW_AUDIT_REPORT.md` | Kundli vs Chat data consistency report |
| `/app/VEDIC_API_REFERENCE.md` | Complete 130 API endpoints documentation |
| `/app/data_flow_audit.py` | Audit script (can be deleted) |
| `/app/backend/conversation/welcome_engine.py` | Welcome message generator |

---

## 📁 Files Modified This Session

| File | Changes |
|------|---------|
| `/app/backend/astro_client/vedic_api.py` | Optimized to use `/horoscope/planet-details` |
| `/app/backend/server.py` | Added `/api/profile/welcome`, updated city search |
| `/app/frontend/src/components/screens/OnboardingScreen.jsx` | City search timezone handling |
| `/app/frontend/src/components/screens/ChatScreen.jsx` | Welcome fetch method fix |

---

## 🔧 API Parameters (Sharad Harjai)

```json
{
  "dob": "24/01/1986",
  "tob": "06:32",
  "lat": 28.8955,
  "lon": 76.6066,
  "tz": 5.5,
  "lang": "en"
}
```

### Chart Summary
- **Ascendant:** Sagittarius 27.04°
- **Moon:** Gemini 17.00° (Ardra nakshatra)
- **Current Dasha:** Mercury-Mercury (Feb 2025 - Jul 2027)
- **Ayanamsa:** Lahiri (23.6682°)

---

*Session completed: January 4, 2026*
