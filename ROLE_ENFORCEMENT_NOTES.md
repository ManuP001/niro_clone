# ROLE_ENFORCEMENT_NOTES.md

## Signal Role Enforcement System

This document describes the role-based signal selection pipeline implemented to fix repetitive readings (same Venus/Jupiter + same "Why this answer").

---

## 1. Role Definitions

Every candidate signal is assigned one of these roles **BEFORE scoring**:

| Role | Description | Purpose |
|------|-------------|---------|
| `TOPIC_DRIVER` | Signal directly relevant to query topic | Primary drivers for the answer |
| `TIME_DRIVER` | Signal relevant to time direction (dasha/transit) | Timing context |
| `BASELINE_CONTEXT` | Lagna lord/Moon baseline traits | Emotional/contextual tone |
| `CONTRAST_SIGNAL` | Opposing indicator (future use) | Balance perspective |
| `NOISE` | Everything else | Excluded from drivers |

---

## 2. Role Assignment Rules

### A. TOPIC_DRIVER
Assigned when **any** of these are true:
- Signal ties to **topic houses** (from topic→house mapping)
- Signal **planet matches topic karakas** (e.g., Venus for relationships)
- Signal is a **planet placement in relevant houses**

**Topic → House Mapping:**
| Topic | Houses |
|-------|--------|
| Career | 10, 6, 2 |
| Relationships | 7, 5, 11 |
| Finance/Money | 2, 11, 8 |
| Health | 1, 6, 8, 12 |
| Family | 4, 2, 5 |
| Education | 4, 5, 9 |
| Travel | 3, 9, 12 |
| Spirituality | 9, 12, 5 |

**Topic → Karaka Planets:**
| Topic | Primary Karakas |
|-------|-----------------|
| Career | Sun, Saturn, Mercury, Jupiter |
| Relationships | Venus, Moon, Jupiter |
| Finance | Mercury, Jupiter, Venus, Saturn |
| Health | Sun, Mars, Saturn, Moon |
| Family | Moon, Venus, Jupiter |
| Education | Mercury, Jupiter, Moon |

### B. TIME_DRIVER
Assigned when:
- Signal is **dasha-related** for the relevant time_direction:
  - `past`: Allow dasha only if NOT "current/ongoing"
  - `present/timeless`: Allow current dasha
  - `future`: Allow upcoming dasha transitions
- Signal is **transit-related** AND time_direction is `present/future`
  - Skip transit if time_direction=`past` (no historical transit data)

### C. BASELINE_CONTEXT
Assigned when:
- Lagna lord / Moon / baseline traits
- NOT directly topic-linked (otherwise would be TOPIC_DRIVER)
- Mahadasha lord when not matching topic planets

### D. CONTRAST_SIGNAL
Assigned when:
- Signal conflicts with top candidates (opposing indicator)
- Currently not implemented (placeholder for future)

### E. NOISE
Everything else, including:
- `planet="Unknown"` unless clearly topic-linked
- Signals with no relevance to topic or time

---

## 3. Role Quota Enforcement

**Required Quota:**
```
TOPIC_DRIVER:     2 (prefer different planets)
TIME_DRIVER:      1
BASELINE_CONTEXT: 1 (optional, only if adds context)
```

**Constraints:**
- **Max 2 signals from same planet** in final drivers
- **Exclude NOISE** from kept signals unless minimum can't be filled
- **Past questions**: No "current ongoing" dasha/transit as TIME_DRIVER

**Fallback Logic:**
1. If TOPIC_DRIVER shortfall → fill from BASELINE_CONTEXT
2. If TIME_DRIVER shortfall → fill from remaining TOPIC_DRIVER
3. If still short → pull from NOISE as last resort

---

## 4. Scoring Within Role Buckets

Signals are scored **within their role bucket**, not across all candidates.

### Base Scores by Role:
| Role | Base Score |
|------|------------|
| TOPIC_DRIVER | 0.50 |
| TIME_DRIVER | 0.45 |
| BASELINE_CONTEXT | 0.35 |
| NOISE | 0.10 |

### Bonuses (TOPIC_DRIVER):
- `+0.20` if in **primary topic house** (first in list)
- `+0.10` if in **secondary topic house**
- `+0.15` if **primary karaka planet**
- `+0.08` if **secondary karaka planet**

### Bonuses (TIME_DRIVER):
- `+0.15` if dasha matches present/timeless context
- `+0.12` if dasha for future context
- `+0.10` if transit for present/future context

### Bonuses (BASELINE_CONTEXT):
- `+0.10` if Moon (emotional significance)

### Universal Penalties:
- `-0.15` if time=past AND signal is "current/ongoing"
- `-0.10` repetition penalty if planet used in recent answers

---

## 5. Trust Widget Output

**Show only:**
- Signals with role `TOPIC_DRIVER` or `TIME_DRIVER`
- Optionally 1 `BASELINE_CONTEXT` if it adds emotional context

**Hide:**
- Any signal with `planet="Unknown"` or `"Mixed"`
- Any signal with `role="NOISE"`

---

## 6. Debug Output

The candidate signals debug endpoint includes:

```json
{
  "candidates": [
    {
      "signal_id": "C1",
      "planet": "Saturn",
      "house": 10,
      "role": "TOPIC_DRIVER",
      "role_reason": "planet=Saturn in topic house 10, karaka match",
      "score_final": 0.85,
      "scoring_breakdown": {
        "base": 0.50,
        "primary_house_bonus": 0.20,
        "primary_karaka_bonus": 0.15
      },
      "kept": true,
      "is_driver": true
    }
  ],
  "summary": {
    "total_candidates": 20,
    "kept_count": 4,
    "driver_count": 3,
    "role_counts": {
      "TOPIC_DRIVER": 8,
      "TIME_DRIVER": 3,
      "BASELINE_CONTEXT": 4,
      "NOISE": 5
    },
    "fallback_log": []
  }
}
```

---

## 7. Acceptance Criteria

✅ **Different planets per topic:**
- Career → Sun/Saturn/Mercury (not Venus/Jupiter)
- Relationships → Venus/Moon/Jupiter
- Health → Sun/Mars/Saturn
- Money → Mercury/Jupiter/Venus

✅ **Past questions:**
- Do NOT show "current antardasha ongoing" as driver
- TIME_DRIVER must be historical or natal-based

✅ **Signal counts:**
- `kept_count >= 4`
- Max 2 from same planet

✅ **Trust Widget:**
- Shows 2-3 drivers with different planets
- Roles visible: TOPIC_DRIVER, TIME_DRIVER, BASELINE_CONTEXT
- No Unknown planets

---

## Files Modified

| File | Changes |
|------|---------|
| `backend/astro_client/reading_pack.py` | Role assignment, quota enforcement, bucket scoring |
| `backend/conversation/ux_utils.py` | Trust widget role filtering |
| `backend/conversation/intent_router.py` | Intent classification (ASTRO vs non-ASTRO) |
| `backend/conversation/enhanced_orchestrator.py` | Pass drivers to trust widget |

---

## Testing

Run these 5 queries to verify:
1. **Career**: "What's my career outlook?" → Expect Saturn/Sun/Mercury drivers
2. **Relationships**: "Will I find love?" → Expect Venus/Moon/Jupiter drivers
3. **Money**: "How's my financial future?" → Expect Mercury/Jupiter/Venus drivers
4. **Health**: "How's my health?" → Expect Sun/Mars/Saturn drivers
5. **Generic**: "What does my chart say?" → Expect diverse planet mix

Check `/api/debug/candidate-signals/latest` for:
- `role_counts` showing distribution
- `kept_count >= 4`
- `driver_count = 3`
- Different planets across topics
