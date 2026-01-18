# NIRO Astrology App - Complete Development Summary

## Project Overview

**NIRO** is an astrology-based expert consultation platform where users can get unlimited access to experts across 12 life topics through tiered subscription packs.

**Tech Stack:** React (Frontend) + FastAPI (Backend) + MongoDB (Database)

---

## Evolution Timeline

| Version | Focus | Status |
|---------|-------|--------|
| V1 (Simplified) | Core product structure, 12 topics, expert catalog, payment flow | ✅ Complete |
| V1.5 | UI redesign (gold theme), bottom nav, Ask Mira, no-blur experts | ✅ Complete |
| V2 | DEV toggle, rotating placeholders, expert profiles, profile screen | ✅ Complete |

---

## Feature Summary

### 1. Authentication & Onboarding
- **Login:** Phone/email only (simplified)
- **No birth details required** for V1+ (skip traditional astrology onboarding)
- **Splash Screen:** Branded with gold color scheme and constellation animation

### 2. Navigation System
**Bottom Navigation (5 tabs):**
| Tab | Icon | Description |
|-----|------|-------------|
| Home | 🏠 | Topic tiles + Ask Mira input |
| Experts | 👥 | Browse all experts by modality |
| Ask Mira | ✨ | AI guide chat |
| Profile | 👤 | Account info + DEV options |
| My Pack | 📦 | Plan dashboard (conditional) |

**My Pack Visibility Rules:**
- Hidden for new users
- Shows when user has active plan OR in "Returning" DEV mode

### 3. 12 Life Topics
| Topic | Icon | Experts |
|-------|------|---------|
| Career & Work | 💼 | 8 |
| Money & Finance | 💰 | 3 |
| Health & Wellness | 🏥 | 3 |
| Marriage & Family | 💑 | 2 |
| Children & Education | 👶 | Shared |
| Love & Relationships | ❤️ | 3 |
| Business | 🚀 | Shared |
| Travel & Relocation | ✈️ | 1 |
| Property & Vastu | 🏠 | Shared |
| Mental Health | 🧠 | Shared |
| Spiritual Growth | 🙏 | 2 |
| Legal Matters | ⚖️ | 1 |

**Total Experts:** 23 across 14 modalities

### 4. Expert System

**Expert Modalities:**
- Vedic Astrologer
- Western Astrologer
- Career Coach
- Life Coach
- Numerologist
- Tarot Reader
- Palmist
- Psychic
- Healer
- Spiritual Guide
- Relationship Counselor
- Marriage Counselor
- Financial Advisor
- Legal Advisor

**Expert Card Display:**
- Full photo (no blur)
- Name, modality, rating
- Languages spoken
- Best-for tags
- Short bio
- Topic tags

**Gating (Pre-purchase):**
- Photos visible
- Details visible
- Actions locked: "🔓 Unlock to talk"
- Routes to topic landing → checkout

### 5. Subscription Packs

| Attribute | Starter | Plus ⭐ | Pro |
|-----------|---------|---------|-----|
| Price | ₹2,999 | ₹4,999 | ₹7,999 |
| Validity | 4 weeks | 8 weeks | 12 weeks |
| Chat SLA | 24 hours | 24 hours | 24 hours |
| Calls/month | ❌ | 2 (60 min) | 4 (60 min) |
| Expert Threads | 1 | 3 | Unlimited |
| Free Tools | ❌ | ✅ | ✅ |

**Unlimited Access Conditions:**
1. Unlimited chat with 24hr response SLA
2. Video calls per expert availability (Plus/Pro only)
3. Single topic focus (add more via Topic Pass ₹2,000)

### 6. Ask Mira (AI Guide)

**Purpose:** Help users with topics, packs, experts, and FAQs

**Features:**
- Full-screen chat interface
- Rotating placeholder examples (12 prompts)
- Topic detection and navigation suggestions
- Quick reply chips
- Connected to backend chat API

**From Home:**
- Text input below topics
- Submit → Navigate to Ask Mira with message sent
- Placeholder rotates every 3 seconds

### 7. Payment Integration (Razorpay)

**Flow:**
1. Select tier on topic landing page
2. Proceed to checkout
3. Create order via `/api/simplified/checkout/create-order`
4. Razorpay modal opens
5. Payment success → Verify via `/api/simplified/checkout/verify`
6. Plan created → Navigate to dashboard

**Error Handling:**
- Order creation failure
- Payment cancelled
- Payment failed
- Verification failed

### 8. DEV Toggle (V2)

**Location:** Top-left corner

**Modes:**
- **New:** 4 tabs, no My Pack
- **Returning:** 5 tabs, shows My Pack + Active Pack card

**Persistence:** localStorage key `niro_user_state`

---

## UI Design System

### Color Palette (from Visual Moodboard)

| Element | Color | Hex |
|---------|-------|-----|
| Primary Background | Warm Gold | #d7b870 |
| Logo/Text | Off-white/Cream | #f0e9d1 |
| Accent Lines | Rich Gold | #e5d188 |
| Button/Dark Text | Dark Gray | #5c5c5c |
| Muted Text | Muted Gold | #9a8a6a |
| Light Background | Cream | #f5f0e3 |

### Visual Elements
- Constellation pattern on splash screen
- Rotating star animation
- Gold gradients throughout
- Rounded corners (xl/2xl)
- Shadow effects on cards

---

## API Endpoints

### Topics & Experts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/simplified/topics` | List all 12 topics |
| GET | `/api/simplified/topics/{id}` | Topic landing page data |
| GET | `/api/simplified/experts` | Experts by topic |
| GET | `/api/simplified/experts/all` | All experts grouped by modality |
| GET | `/api/simplified/tiers/{id}` | Tier details |

### User & Plans
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/simplified/user/state` | New vs returning detection |
| GET | `/api/simplified/plans` | User's plans |
| GET | `/api/simplified/plans/{id}` | Plan with threads |

### Checkout
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/simplified/checkout/create-order` | Create Razorpay order |
| POST | `/api/simplified/checkout/verify` | Verify payment |

### Threads & Telemetry
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/simplified/threads` | Create expert thread |
| GET | `/api/simplified/threads/{id}` | Thread with messages |
| POST | `/api/simplified/threads/{id}/messages` | Send message |
| POST | `/api/simplified/telemetry` | Log event |

---

## File Structure

### Frontend (`/app/frontend/src/components/screens/simplified/`)
```
├── SimplifiedApp.jsx      # Main container, navigation, DEV toggle
├── SplashScreen.jsx       # Branded splash with constellation
├── HomeScreen.jsx         # New/Returning variants, rotating placeholders
├── TopicLandingPage.jsx   # 5-section template, tier selection
├── CheckoutScreen.jsx     # Razorpay integration
├── PlanDashboard.jsx      # Post-purchase view, demo mode
├── ExpertsScreen.jsx      # Expert directory with search
├── ExpertProfileScreen.jsx # Full expert profile page
├── AskMiraScreen.jsx      # AI guide chat
├── ProfileScreen.jsx      # Account info, DEV reset
├── BottomNav.jsx          # 5-tab navigation
├── NiroGuideChat.jsx      # Legacy guide overlay
├── utils.js               # API helpers, telemetry
└── index.js               # Exports
```

### Backend (`/app/backend/niro_simplified/`)
```
├── __init__.py            # Module exports
├── models.py              # 15+ Pydantic models
├── catalog.py             # Seeded data (topics, experts, tiers, tools)
├── storage.py             # MongoDB storage layer
└── routes.py              # 20+ API endpoints
```

---

## Telemetry Events (12 max)

| Event | Description |
|-------|-------------|
| `splash_viewed` | App loads |
| `home_viewed` | Home screen (variant: new/returning) |
| `nav_tab_clicked` | Bottom nav tab switch |
| `mira_input_submitted` | Ask Mira from home |
| `mira_message_sent` | Message in Ask Mira |
| `experts_tab_viewed` | Experts tab opened |
| `expert_profile_viewed` | Expert profile opened |
| `topic_viewed` | Topic landing page |
| `tier_selected` | Tier selection |
| `checkout_started` | Checkout begun |
| `purchase_completed` | Payment successful |
| `dashboard_viewed` | Plan dashboard |

All events include `flow_version: "simplified_v2"`

---

## Environment Variables

### Backend (`.env`)
```
MONGO_URL=<mongodb_connection_string>
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=<secret>
GEMINI_API_KEY=<for_chat>
```

### Frontend (`.env`)
```
REACT_APP_BACKEND_URL=<backend_url>
```

---

## Lines of Code Summary

| Category | Lines |
|----------|-------|
| Backend Python | ~2,200 |
| Frontend JSX/JS | ~3,500 |
| Documentation | ~800 |
| **Total** | **~6,500** |

---

## What's Working ✅

1. ✅ Login (phone/email only)
2. ✅ Splash screen with branding
3. ✅ Home screen (new/returning variants)
4. ✅ 12 topic tiles with icons
5. ✅ Topic landing pages
6. ✅ 23 experts with real photos
7. ✅ Expert profile pages
8. ✅ Tier selection (Starter/Plus/Pro)
9. ✅ Razorpay payment flow
10. ✅ Plan dashboard
11. ✅ Ask Mira chat
12. ✅ Bottom navigation
13. ✅ DEV toggle (New/Returning)
14. ✅ Profile screen
15. ✅ Desktop scrolling

---

## Known Limitations / Future Work

| Feature | Status |
|---------|--------|
| Thread chat UI | Basic |
| Call booking | UI only |
| Push notifications | Not implemented |
| Expert-side dashboard | Not implemented |
| Profile editing | Stub only |
| Topic Pass purchase | Partial |

---

## Quick Start

1. **Login:** Enter any email (e.g., `test@example.com`)
2. **Explore:** Click on a topic (e.g., Career)
3. **Purchase:** Select Plus tier → Checkout → Complete payment
4. **Chat:** Navigate to My Pack → Start expert thread

**DEV Testing:**
- Use top-left toggle to switch New/Returning modes
- Profile → Reset Demo State to clear localStorage

---

*Last Updated: V2 Implementation - January 2025*
