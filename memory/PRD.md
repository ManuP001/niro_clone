# NIRO Product Requirements Document

## Overview
NIRO is an AI-powered Vedic astrology platform providing personalized guidance across Love, Career, and Health topics. The app is on V4 with V6 premium UI upgrades.

## Current Status (January 2025)
- **Active Version:** V4 with V6 Premium UI Upgrades
- **Last Update:** January 23, 2026 - User Details screen and onboarding flow fix
- **Completed Sprints:** Landing Page + Home Screen V6 Revamp + Onboarding Flow V6
- **Status:** ✅ Complete and tested (14/14 backend tests passed)

### Latest Changes (Jan 23, 2026)
- ✅ Fixed P0 blocker: UserDetailsScreen now saves profile via `/api/profile/` endpoint
- ✅ Field mapping corrected: birthDate→dob, birthTime→tob, birthPlace→location
- ✅ Onboarding flow: Login → User Details → How Niro Works → Trust & Safety → Home
- ✅ HomeScreen: Reduced tile size, removed category subtitles, added profile button
- ✅ Landing Page: 2x2 grid for package details, topic explainer moved after tier selector
- ✅ Reused existing BirthDetailsModal for onboarding (city autocomplete with lat/lon)
- ✅ Fixed Health tiles: Corrected IDs (health_timing, emotional_wellbeing, recovery_support)
- ✅ Deleted redundant UserDetailsScreen.jsx - using BirthDetailsModal instead

---

## V6 Home Screen Design

### Key Features
- **Gradient background** - Linear gradient matching onboarding screens
- **Animated Niro logo** - Larger constellation ring animation (20s spin)
- **Premium CTA area** - "Talk to Expert" (primary/teal), "Chat with Mira (AI)" (secondary/white)
- **Category modules** - Soft card containers with helper copy
- **Reduced whitespace** - Bottom padding reduced by 60%+

### Tile Order (V6 - Premium + Highest Intent First)

**Love & Relationships** - "Dating, commitment, healing, family dynamics"
1. Healing
2. Dating
3. Marriage
4. Trust
5. Family
6. Closure

**Career & Money** - "Work direction, stability, timing, growth"
1. Clarity
2. Job Change
3. Money
4. Timing
5. Work Stress
6. Office

**Health & Wellness** - "Stress, recovery, energy, emotional balance"
1. Stress
2. Sleep
3. Energy
4. Healing
5. Emotional
6. Wellness

---

## V6 Landing Page Design (Frame 27 Layout)

### Design Philosophy
- **Gradient background** - Same as home/onboarding (not plain white)
- **Subtle highlights** - Boxes, dividers, shade differences (no rainbow blocks)
- **Frame 27 structure** from wireframe reference

### Section Order
1. **Header** - Back button + Topic title (headerTitle from content)
2. **Hero Promise** - One-line promise (heroOneLinePromise from Excel)
3. **Personalized Greeting** - "Hi {userName}, here are the paths you can choose for your journey"
4. **Tier Selector Tabs** - Focussed/Supported/Comprehensive (Recommended badge ONLY on Supported)
5. **Tier Summary Card** - Details from tierSummaryDetails (Duration, Consultations, Follow-ups, Support)
6. **Refund Guarantee** - "No questions asked — 7 day full refund guarantee" (ONLY after summary)
7. **Outcomes** - Grouped by Clarity/Timeline/Support (from outcomesByTier)
8. **How will your journey unfold** - Bullets from howUnfoldsByTier
9. **Experts Widget** - "Meet your experts" with horizontal scroll cards (3 experts)
10. **Optional Add-ons** - "Coming soon" section
11. **Why Niro** - Trust bullets
12. **FAQs** - Expandable
13. **Sticky CTA Bar** - ONLY Price + "Start my journey" (simplified)

### Strict Rules
- ✅ "Unlimited chat" exact wording (not "async chat")
- ✅ "How will your journey unfold" (not "How will it unfold?")
- ✅ Recommended badge ONLY on tier selector tabs
- ✅ Remedies CTA = "Coming soon"
- ✅ Sticky bar = Price + CTA only (no badge, no weeks, no package name)
- ✅ Refund appears ONLY after tier summary

---

## V6 Content Source

All 18 subtopic content from: `v6Data/landingPageContentV6.js`
Source Excel: `Niro_LandingPage_Content_Template_And_Content_V6_UpdatedKeyColumns.xlsx`

### Content Structure per Topic:
- **heroOneLinePromise** - Main promise text
- **topicExplainerOneLiner** - Personalized greeting template
- **heroSubtitle** - Additional context
- **tierCards** - Price and duration per tier (Focussed/Supported/Comprehensive)
- **tierSummaryDetails** - Formatted summary string per tier
- **outcomesByTier** - Clarity, Timeline, Support bullets per tier
- **howUnfoldsByTier** - Journey steps per tier
- **expertsWidgetTitle/Subtitle** - Experts section content
- **whyNiroBullets** - Trust reasons
- **faqs** - FAQ Q&A pairs

### Categories:
- **V6_LOVE_SUBTOPICS** (6): relationship-healing, dating-compatibility, breakup-closure, communication-trust, family-relationships, marriage-planning
- **V6_CAREER_SUBTOPICS** (6): career-clarity, job-transition, money-stability, big-decision-timing, work-stress, office-politics
- **V6_HEALTH_SUBTOPICS** (6): stress-management, sleep-reset, energy-balance, health-timing, emotional-wellbeing, recovery-support

---

## Key Files

### Frontend (V6)
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx` - V6 premium home with profile button
- `/app/frontend/src/components/screens/simplified/TopicLandingPage.jsx` - V6 landing page with 2x2 grid
- `/app/frontend/src/components/screens/simplified/UserDetailsScreen.jsx` - NEW: Birth details collection screen
- `/app/frontend/src/components/screens/simplified/SimplifiedApp.jsx` - Main app container with onboarding flow
- `/app/frontend/src/components/screens/simplified/v6Data/landingPageContentV6.js` - V6 content source
- `/app/frontend/src/components/screens/simplified/icons.jsx` - Minimalist icons

### Backend
- `/app/backend/profile/__init__.py` - Profile endpoints (POST/GET /api/profile/)
- `/app/backend/auth/routes.py` - Auth endpoints (POST /api/auth/identify)
- `/app/backend/niro_simplified/catalog.py` - Tier pricing and configuration
- `/app/backend/niro_simplified/routes.py` - Simplified API routes

---

## Payments
- **Provider:** Razorpay (INR)
- **Test mode:** Enabled with test keys in backend/.env

---

## Upcoming Tasks (P1)
1. Verify Kundli visibility and dynamic updates on HomeScreen
2. Cleanup duplicate LoginScreen.jsx (two files exist)
3. Update Mira Chat welcome message
4. Implement post-purchase home screen experience

## Future Tasks (P2)
1. Onboarding flow refinements (8-screen flow, skip birth time)
2. Global design system application (Teal/Gold theme)
3. Full Remedies implementation (currently "Coming soon")

## Technical Debt
- Remove unused V5 files (`SimplifiedAppV5.jsx`, `v5Screens/`, `v5Data/`)
- Consolidate duplicate LoginScreen.jsx files (`screens/` and `screens/simplified/`)
