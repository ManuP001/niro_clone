# NIRO Simplified V1 - Implementation Summary

## Overview

**Core Value Proposition:** "WELCOME to Niro. Get Unlimited access to experts."

NIRO Simplified V1 is a streamlined expert-access platform where users:
1. Browse 12 life topics
2. View expert galleries (locked pre-purchase)
3. Select scenario chips matching their situation
4. Choose from 3 pack tiers (Starter/Plus/Pro)
5. Complete checkout via Razorpay
6. Access unlimited expert chat post-purchase

---

## Implementation Completed (Phase 1)

### Backend Components (`/app/backend/niro_simplified/`)

| File | Purpose | Key Features |
|------|---------|--------------|
| `__init__.py` | Module exports | Router export |
| `models.py` | Data models | 15+ Pydantic models for topics, experts, tiers, plans, threads |
| `catalog.py` | Catalog service | 12 topics, 8+ experts (Career), 36 tiers, 24+ scenarios, 24+ tools |
| `storage.py` | MongoDB layer | Plans, threads, messages, topic passes, telemetry |
| `routes.py` | API endpoints | 20+ endpoints for topics, checkout, plans, threads |

### API Endpoints Created

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/simplified/topics` | List all 12 topics |
| GET | `/api/simplified/topics/{topic_id}` | Topic landing page data (experts, scenarios, tiers, tools, conditions) |
| GET | `/api/simplified/experts` | List experts (optionally by topic) |
| GET | `/api/simplified/tiers/{tier_id}` | Get tier details |
| GET | `/api/simplified/user/state` | User state for home screen routing (new vs returning) |
| POST | `/api/simplified/checkout/create-order` | Create Razorpay order |
| POST | `/api/simplified/checkout/verify` | Verify payment and create plan |
| GET | `/api/simplified/plans` | List user's plans |
| GET | `/api/simplified/plans/{plan_id}` | Plan details with threads |
| POST | `/api/simplified/threads` | Create expert thread |
| GET | `/api/simplified/threads/{thread_id}` | Thread with messages |
| POST | `/api/simplified/threads/{thread_id}/messages` | Send message |
| POST | `/api/simplified/telemetry` | Log telemetry event |
| POST | `/api/simplified/passes/create-order` | Create topic pass order (₹2000) |

### Frontend Components (`/app/frontend/src/components/screens/simplified/`)

| Component | Purpose | Status |
|-----------|---------|--------|
| `SimplifiedApp.jsx` | Main app container | ✅ Complete |
| `SplashScreen.jsx` | 2-3s branded splash | ✅ Complete |
| `HomeScreen.jsx` | New/Returning user variants | ✅ Complete |
| `TopicLandingPage.jsx` | Topic page template (5 sections) | ✅ Complete |
| `CheckoutScreen.jsx` | Razorpay payment flow | ✅ Complete |
| `PlanDashboard.jsx` | Post-purchase dashboard | ✅ Complete |
| `NiroGuideChat.jsx` | Persistent guide overlay | ✅ Complete |
| `utils.js` | API helpers, formatters | ✅ Complete |

---

## Data Seeded

### 12 Life Topics
1. Career & Work
2. Money & Financial Stability
3. Health & Wellbeing
4. Marriage & Family
5. Children & Education
6. Love & Relationships
7. Business & Entrepreneurship
8. Travel / Relocation / Foreign Settlement
9. Property & Home
10. Mental Health / Stress / Emotional Balance
11. Spiritual Growth / Purpose
12. Legal / Conflict / Disputes

### Pack Tiers (Per Topic)

| Tier | Price | Validity | Chat SLA | Calls | Expert Threads | Free Tools |
|------|-------|----------|----------|-------|----------------|------------|
| Starter | ₹2,999 | 4 weeks | 24hr | ❌ | 1 | ❌ |
| Plus | ₹4,999 | 8 weeks | 24hr | 2/month | 3 | ✅ |
| Pro | ₹7,999 | 12 weeks | 24hr | 4/month | Unlimited | ✅ |

### Experts (Career Topic - 8 experts)
- Pandit Rajesh Sharma (Vedic Astrologer)
- Dr. Ananya Mehta (Career Coach)
- Acharya Suresh Joshi (Numerologist)
- Priya Krishnamurthy (Life Coach)
- Guru Venkatesh Iyer (Vedic Astrologer)
- Meera Sundaram (Tarot Reader)
- Ramesh Kulkarni (Palmist)
- Dr. Shalini Rao (Western Astrologer)

### Scenarios (Career Topic - 8 scenarios)
- Job change (high urgency → Plus)
- Promotion stuck (medium → Plus)
- Career switch (high → Pro)
- Starting a business (high → Pro)
- Timing questions (medium → Plus)
- Work-life balance (low → Starter)
- Skill uncertainty (low → Starter)
- Layoff concerns (high → Plus)

### Free Tools (Career Topic - 3 tools)
- Career Decision Framework
- Timing Explainer
- Career Values Quiz

---

## Key Features Implemented

### 1. Splash Screen
- 2-3 second branded splash
- NIRO logo with gradient
- Loading animation
- Auto-transitions to Home

### 2. Home Screen (Two Variants)

**New User:**
- Welcome message
- 12 topic tiles (3x4 grid)
- "Ask Niro" guide CTA
- Social proof (10,000+ guided)

**Returning User:**
- Active plan card with weeks remaining
- Recent expert conversations
- Explore topics section
- Topic pass CTA (₹2,000)

### 3. Topic Landing Page (5 Sections)

**Section A - Scenarios:**
- Selectable chips matching user's situation
- "Tell us more" optional input

**Section B - Expert Gallery:**
- 6 experts displayed (locked with 🔒)
- Name, modality, rating
- Pre-purchase visibility

**Section C - Pack Tiers:**
- 3 tiers: Starter/Plus/Pro
- Recommended badge on Plus
- Feature comparison

**Section D - Free Services:**
- "Plus & Pro only" badge
- Tool cards with icons

**Section E - Unlimited Access Conditions:**
- Chat condition (24hr SLA)
- Call condition (Plus/Pro only, 60 min max)
- Topic condition (₹2,000 for additional topics)

**Sticky CTA:**
- "🔓 Unlock Unlimited Access — ₹X,XXX"

### 4. Checkout
- Order summary with features
- Razorpay integration
- Success → Plan Dashboard

### 5. Plan Dashboard
- Active pack status
- Expert conversations list
- Start new thread button
- Thread limits enforcement
- Call booking (Plus/Pro)
- Free tools access (Plus/Pro)
- Add topic pass CTA

### 6. Niro Guide Chat
- Floating button on all screens
- Rule-based topic suggestions
- Quick reply chips
- Navigation to topic pages

---

## Telemetry Events (12 Events)

| Event | Trigger |
|-------|---------|
| `splash_viewed` | Splash screen shown |
| `home_viewed` | Home screen loaded |
| `topic_viewed` | Topic page loaded |
| `scenario_selected` | User taps chip |
| `tier_selected` | User selects tier |
| `checkout_started` | Checkout opened |
| `purchase_completed` | Payment verified |
| `purchase_failed` | Payment failed |
| `expert_thread_started` | New thread created |
| `expert_message_sent` | Message sent |
| `guide_chat_opened` | Guide overlay opened |
| `free_tool_opened` | Tool accessed |

All events include: `flow_version: "simplified_v1"`, `user_id`, `session_id`, `timestamp`

---

## Access Controls

### Thread Limits
- Starter: 1 active thread
- Plus: 3 active threads
- Pro: Unlimited threads

### Free Tools
- Starter: ❌ No access
- Plus/Pro: ✅ Full access

### Video Calls
- Starter: ❌ Not included
- Plus: 2 calls/month (60 min)
- Pro: 4 calls/month (60 min)

---

## UI Toggle

Three versions available via toggle buttons (top-right):
- **V1** (Green): NIRO Simplified V1 (default)
- **V2** (Blue): NIRO V2 (previous version)
- **Old** (Purple): Legacy UI

---

## Testing

### Backend API Test
```bash
# Get all topics
curl http://localhost:8001/api/simplified/topics

# Get career topic details
curl http://localhost:8001/api/simplified/topics/career

# Get user state
curl -H "Authorization: Bearer <token>" http://localhost:8001/api/simplified/user/state
```

### Frontend Flow
1. Open app → See Splash (2-3s)
2. Land on Home (new user variant)
3. Tap topic tile → Topic Landing Page
4. Select scenarios → Choose tier
5. Tap "Unlock" → Checkout
6. Complete payment → Plan Dashboard
7. Start expert conversation

---

## Files Created/Modified

### New Files (Backend)
- `/app/backend/niro_simplified/__init__.py`
- `/app/backend/niro_simplified/models.py`
- `/app/backend/niro_simplified/catalog.py`
- `/app/backend/niro_simplified/storage.py`
- `/app/backend/niro_simplified/routes.py`

### New Files (Frontend)
- `/app/frontend/src/components/screens/simplified/index.js`
- `/app/frontend/src/components/screens/simplified/utils.js`
- `/app/frontend/src/components/screens/simplified/SimplifiedApp.jsx`
- `/app/frontend/src/components/screens/simplified/SplashScreen.jsx`
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx`
- `/app/frontend/src/components/screens/simplified/TopicLandingPage.jsx`
- `/app/frontend/src/components/screens/simplified/CheckoutScreen.jsx`
- `/app/frontend/src/components/screens/simplified/PlanDashboard.jsx`
- `/app/frontend/src/components/screens/simplified/NiroGuideChat.jsx`

### Modified Files
- `/app/backend/server.py` - Added simplified router and storage init
- `/app/frontend/src/App.js` - Added SimplifiedApp import and UI toggle

---

## Next Steps (Phase 2+)

1. **Scale Experts**: Add 6-10 experts per topic (72-120 total)
2. **Expert Chat Backend**: Real expert-side interface
3. **Call Booking**: Calendar integration for Plus/Pro
4. **Topic Pass Flow**: Complete purchase and activation
5. **Analytics Dashboard**: Funnel visualization
6. **Admin Panel**: Expert/tier management

---

## Summary

✅ **Completed:**
- Splash screen with branding
- New vs Returning user home variants
- Topic landing page template (5 sections)
- Tier system (Starter/Plus/Pro)
- "Unlimited Access Conditions" footer
- Checkout flow (Razorpay)
- Post-purchase dashboard
- Expert thread creation
- Niro Guide Chat overlay
- 12 telemetry events
- All 12 topics seeded
- Career experts (8) and scenarios (8) seeded

**Total: ~2,500 lines of code across 15 files**
