# INSTRUMENTATION_RUNTIME_GUIDE.md

## NIRO Pipeline Observability Guide

This document explains how to use the new exhaustive observability system for debugging the NIRO astrology chat pipeline.

---

## Quick Start

### 1. Enable Debug Logging
```bash
export NIRO_DEBUG_LOGS=1
```

This forces snapshot files to be written for **every** request, regardless of whether data is missing.

Without this flag, snapshots are only written when:
- Data is missing (coverage check fails)
- Parse errors occur  
- LLM output contains "missing data" phrases
- QUALITY_ALERT is triggered

### 2. Tail the Pipeline Log
```bash
tail -f /app/logs/niro_pipeline.log
```

Each line is a stage tag with structured data:
```
[STAGE_NAME] session=SESSION_ID request_id=REQUEST_ID key=value key=value ...
```

### 3. Find Snapshots
```bash
# All snapshots for a session
ls -lt /app/logs/*_SESSION_ID_*

# All snapshots of a certain type
ls -lt /app/logs/api_profile_response_*

# Find by request ID
ls -lt /app/logs/*_REQUEST_ID_*
```

---

## Log Stages (A-I)

Each request generates logs at these stages in order:

### Stage A: START
Logged at pipeline entry.
```
[START] session=abc123 request_id=12ab34 user_message="..." time_context=future action_id=null
```

**Fields:**
- `user_message`: First 300 chars of user input
- `time_context`: "past" | "present" | "future" | "unknown"
- `action_id`: Action being performed (if any)

### Stage B: BIRTH_EXTRACTION
After attempting to extract birth details from message/subjectData.
```
[BIRTH_EXTRACTION] session=abc123 request_id=12ab34 extracted=true extraction_method=regex dob=2000-01-15 tob=10:30 location="NYC" confidence=N/A
```

**Fields:**
- `extracted`: true/false
- `extraction_method`: "regex" | "llm" | "subjectData" | "previous_state" | "none"
- `dob`, `tob`, `location`: Birth details (if extracted)
- `confidence`: Confidence score (if available)

### Stage C: ROUTING / TOPIC
After mode routing and topic classification.
```
[ROUTING] session=abc123 request_id=12ab34 mode=NORMAL_READING topic=CAREER time_context=future
```

**Fields:**
- `mode`: Conversation mode
- `topic`: Selected topic/category
- `time_context`: Inferred time context

### Stage D: API_PROFILE_REQ
Before calling Vedic API for profile.
```
[API_PROFILE_REQ] session=abc123 request_id=12ab34 dob=2000-01-15 tob=10:30 location=NYC timezone=5.5
```

### Stage D (cont): API_PROFILE_RES
After Vedic API returns profile, with coverage validation.
```
[API_PROFILE_RES] session=abc123 request_id=12ab34 ok=14 missing=0 missing_count=0 missing_keys="[]" present_keys="['birth_details', 'ascendant', ...]"
```

**Fields:**
- `ok`: Number of required fields present
- `missing`: Number of required fields missing
- `missing_count`: Count of missing fields
- `missing_keys`: List of missing field paths (first 5)
- `present_keys`: Sample of present top-level keys

### Stage E: API_TRANSITS_REQ
Before calling Vedic API for transits.
```
[API_TRANSITS_REQ] session=abc123 request_id=12ab34 date_range=2025-12-13
```

### Stage E (cont): API_TRANSITS_RES
After Vedic API returns transits, with coverage validation.
```
[API_TRANSITS_RES] session=abc123 request_id=12ab34 ok=4 missing=0 event_count=12
```

**Fields:**
- `ok`: Number of required transit fields present
- `missing`: Number of required transit fields missing
- `event_count`: Number of transit events returned

### Stage F: FEATURES
After building astro_features for LLM.
```
[FEATURES] session=abc123 request_id=12ab34 ok=9 missing=0 focus_factors_count=5 transits_count=3 key_rules_count=2
```

**Fields:**
- `ok`: Number of required feature fields present
- `missing`: Number of required feature fields missing
- `focus_factors_count`: Number of astrological focus factors
- `transits_count`: Number of filtered transits
- `key_rules_count`: Number of key rules firing

### Stage G: LLM_PROMPT
Before calling the LLM model.
```
[LLM_PROMPT] session=abc123 request_id=12ab34 model=niro_llm payload_size=1523 topic=CAREER mode=NORMAL_READING
```

**Fields:**
- `model`: LLM model name
- `payload_size`: Size of JSON payload in bytes
- `topic`: Topic being analyzed
- `mode`: Conversation mode

### Stage H: LLM_OUTPUT
After LLM returns response.
```
[LLM_OUTPUT] session=abc123 request_id=12ab34 output_length=842 parse_success=true contains_missing_phrase=false
```

**Fields:**
- `output_length`: Length of LLM output text
- `parse_success`: Whether output parsed correctly
- `contains_missing_phrase`: true if output mentions "missing data"

### Stage I: END
Pipeline completion.
```
[END] session=abc123 request_id=12ab34 elapsed_ms=1523 mode=NORMAL_READING topic=CAREER response_length=842 profile_fetched=true transits_fetched=true
```

**Fields:**
- `elapsed_ms`: Total time in milliseconds
- `mode`: Final mode
- `topic`: Final topic
- `response_length`: Length of response text
- `profile_fetched`: Whether API profile was fetched
- `transits_fetched`: Whether API transits were fetched

---

## Special: QUALITY_ALERT

A special stage that triggers when data is complete but LLM claims it's missing.

```
[QUALITY_ALERT] session=abc123 request_id=12ab34 reason=LLM_claims_missing_but_features_complete features_ok=9 features_missing=0
```

This indicates a potential issue with:
- The LLM prompt template
- How features are being passed to the LLM
- The LLM model's behavior

When this fires, a detailed snapshot is automatically written to:
```
/app/logs/quality_alert_missing_data_SESSION_ID_REQUEST_ID_TIMESTAMP.txt
```

---

## Snapshot Files

Snapshot files are written to `/app/logs/` in the following scenarios:

### Automatic Snapshots (Always)
- When data coverage validation finds missing fields
- When QUALITY_ALERT is triggered
- When NIRO_DEBUG_LOGS=1

### Snapshot Types

| Kind | Trigger | Contents |
|------|---------|----------|
| `input_payload_*.json` | Debug mode | User message, action ID, subject data, time context |
| `birth_extraction_*.json` | Extraction failed OR debug | Extraction method, regex result, final birth details |
| `routing_*.json` | Debug | Routing inputs/outputs, topic classification |
| `api_profile_response_*.json` | Missing data OR error | Coverage report, sample planets/houses, core signs |
| `api_transits_response_*.json` | Missing data OR error | Coverage report, sample transit events |
| `astro_features_*.json` | Missing data OR error | Coverage report, sample focus factors, transits, key rules |
| `llm_prompt_*.txt` | Missing features OR debug | Full LLM payload with features |
| `llm_output_*.txt` | Missing features OR debug | Full LLM response text |
| `quality_alert_missing_data_*.txt` | QUALITY_ALERT triggered | Alert message, LLM output, features, prompt |

### Snapshot Naming

```
{kind}_{session_id}_{request_id}_{timestamp}.{json|txt}
```

Example:
```
api_profile_response_test-session-001_a1b2c3d4_2025-12-13T14-30-22.json
```

### Snapshot Content (Minimized)

All snapshots are **minimized** to avoid massive log files:
- No full raw API payloads
- No secrets or auth tokens
- Top-level keys only
- First 2-3 items of arrays (planets, houses, events, etc.)
- Truncated long strings (max 200 chars)

Example snapshot structure:
```json
{
  "stage": "api_profile_response",
  "session_id": "test-session",
  "request_id": "a1b2c3d4",
  "timestamp": "2025-12-13T14:30:22.123Z",
  "coverage": {
    "ok": 12,
    "missing": 2,
    "missing_keys": ["planets", "current_antardasha.end_date"]
  },
  "birth_details": {
    "dob": "2000-01-15",
    "tob": "10:30",
    "location": "NYC"
  },
  "core_signs": {
    "ascendant": "Aries",
    "moon_sign": "Taurus",
    "sun_sign": "Capricorn"
  },
  "sample_planets": [
    {"planet": "Sun", "sign": "Capricorn"},
    {"planet": "Moon", "sign": "Taurus"}
  ],
  "sample_houses": [
    {"house": 1, "sign": "Aries"},
    {"house": 2, "sign": "Taurus"}
  ]
}
```

---

## Grep Recipes

### Filter by Stage
```bash
# All START stages
grep "\[START\]" /app/logs/niro_pipeline.log

# All API failures
grep -E "\[API_PROFILE_RES\].*missing=[1-9]" /app/logs/niro_pipeline.log

# All quality alerts
grep "\[QUALITY_ALERT\]" /app/logs/niro_pipeline.log
```

### Filter by Session
```bash
# All logs for one session
grep "session=test-session-001" /app/logs/niro_pipeline.log
```

### Filter by Request ID
```bash
# All logs for one request
grep "request_id=a1b2c3d4" /app/logs/niro_pipeline.log
```

### Find Timing Issues
```bash
# Requests taking more than 2 seconds
grep -E "\[END\].*elapsed_ms=[0-9]{4,}" /app/logs/niro_pipeline.log
```

### Find Missing Data
```bash
# Requests with missing profile data
grep -E "\[API_PROFILE_RES\].*missing=[1-9]" /app/logs/niro_pipeline.log

# Requests with missing features
grep -E "\[FEATURES\].*missing=[1-9]" /app/logs/niro_pipeline.log
```

### Find Extraction Failures
```bash
# All failed extractions
grep "\[BIRTH_EXTRACTION\].*extracted=false" /app/logs/niro_pipeline.log
```

---

## Example Debugging Session

**Goal:** Find why a user says "the system says I don't have birth data" but you suspect we do.

### 1. Find the request
```bash
# User mentions session ID "user-abc-123"
grep "session=user-abc-123" /app/logs/niro_pipeline.log | head -20
```

Output:
```
2025-12-13 14:30:22 [START] session=user-abc-123 request_id=a1b2c3d4 user_message="Is this..." time_context=future
2025-12-13 14:30:22 [BIRTH_EXTRACTION] session=user-abc-123 request_id=a1b2c3d4 extracted=true extraction_method=subjectData
2025-12-13 14:30:23 [API_PROFILE_RES] session=user-abc-123 request_id=a1b2c3d4 ok=14 missing=0
2025-12-13 14:30:23 [FEATURES] session=user-abc-123 request_id=a1b2c3d4 ok=9 missing=0
2025-12-13 14:30:24 [QUALITY_ALERT] session=user-abc-123 request_id=a1b2c3d4 reason=LLM_claims_missing_but_features_complete
```

**Finding:** Features are complete (`missing=0`) but LLM says missing! This is a QUALITY_ALERT.

### 2. Check the alert snapshot
```bash
cat /app/logs/quality_alert_missing_data_user-abc-123_a1b2c3d4_*.txt
```

This shows exactly what the LLM received and why it said "missing data" despite having complete features.

### 3. Check what the LLM received
```bash
cat /app/logs/llm_prompt_user-abc-123_a1b2c3d4_*.txt
```

This reveals if the prompt is missing information or poorly formatted.

### 4. Check the actual response
```bash
cat /app/logs/llm_output_user-abc-123_a1b2c3d4_*.txt
```

This shows the exact LLM response and what it said.

---

## Environment Variables

### NIRO_DEBUG_LOGS
- **Default:** `false` (or unset)
- **Values:** `0`, `1`, `true`, `false`
- **Effect:** If set to `1` or `true`, write snapshot files for **every** request

Example:
```bash
# Enable debug logging
export NIRO_DEBUG_LOGS=1

# Run your app
python -m backend.server

# Disable debug logging
unset NIRO_DEBUG_LOGS
```

### NIRO_LOG_DIR
- **Default:** `/app/logs`
- **Effect:** Directory where all snapshots and niro_pipeline.log are written

Example:
```bash
# Use custom log directory
export NIRO_LOG_DIR=/tmp/niro_debug
mkdir -p /tmp/niro_debug
python -m backend.server
```

---

## Performance Considerations

- **Without debug:** Minimal overhead (~1-2ms per request for logging)
- **With debug (NIRO_DEBUG_LOGS=1):** ~10-50ms overhead from snapshot writing depending on data size
- **Snapshots are minimized:** Typically 5-50KB each, not full payloads
- **Log file rotation recommended:** niro_pipeline.log can grow rapidly in production

---

## Troubleshooting

### "Snapshots not being written"
Check:
```bash
# 1. Is debug enabled?
echo $NIRO_DEBUG_LOGS

# 2. Do you have write permission to log dir?
ls -la /app/logs/

# 3. Is there missing/error data?
grep -E "missing=[1-9]|ERROR" /app/logs/niro_pipeline.log
```

### "Log file is too large"
Solution:
```bash
# Set up log rotation
logrotate -f /etc/logrotate.d/niro

# Or manually archive
mv /app/logs/niro_pipeline.log /app/logs/niro_pipeline.log.$(date +%Y%m%d)
gzip /app/logs/niro_pipeline.log.*
```

### "Missing snapshot for a request"
Check if data was actually missing or if NIRO_DEBUG_LOGS is disabled:
```bash
# Check for missing data
grep "request_id=REQUEST_ID" /app/logs/niro_pipeline.log | grep "missing=[1-9]"

# Check for QUALITY_ALERT
grep "request_id=REQUEST_ID" /app/logs/niro_pipeline.log | grep "QUALITY_ALERT"

# If neither, debug mode must be off - enable it
export NIRO_DEBUG_LOGS=1
```

---

## Summary

The NIRO pipeline now logs:
1. **9 stages** (A-I) covering the entire flow
2. **Structured, grep-friendly** log lines
3. **Minimal snapshots** only when needed or in debug mode
4. **QUALITY_ALERT** detection for mismatches
5. **Request ID correlation** across all stages

Use this to debug why users see "missing data" messages despite having complete astrological data.
