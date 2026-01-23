# NIRO Product Requirements Document

## Overview
NIRO is an AI-powered Vedic astrology platform providing personalized guidance across Love, Career, and Health topics. The app is on V4 with V6 premium UI upgrades.

## Current Status (January 2025)
- **Active Version:** V4 with V6 Premium UI Upgrades
- **Completed Sprints:** Landing Page + Home Screen V6 Revamp
- **Status:** ✅ Complete and tested (15/15 features verified)

---

## V6 Home Screen Design

### Key Features
- **Gradient background** - Linear gradient matching onboarding screens
- **Animated Niro logo** - Larger constellation ring animation (20s spin)
- **Premium CTA area** - "Talk to Expert" (primary/teal), "Chat with Mira (AI)" (secondary/white)
- **Trust microcopy** - "Private • No spam • Verified experts"
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
1. **Header** - Back button + Topic title
2. **Topic Explainer** - 1-line context at top (from V6 source)
3. **Hero** - "Hi {userName}, here are the paths you can choose for your journey"
4. **Tier Selector Tabs** - Focussed/Supported/Comprehensive (Recommended badge ONLY here)
5. **Tier Summary Card** - 2x2 grid (Duration, Consultation, Follow-ups, Chat)
6. **Refund Guarantee** - "No questions asked — 7 day full refund guarantee" (ONLY after summary)
7. **Outcomes** - Grouped by Clarity/Timeline/Support
8. **How will your journey unfold** - 4-step timeline
9. **Optional Add-ons** - "Coming soon" pill (NO CTA)
10. **Why Niro** - Trust bullets
11. **FAQs** - Expandable
12. **Sticky CTA Bar** - ONLY Price + "Start my journey" (simplified)

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
- Topic explainer 1-liners
- Tier pricing (Focussed/Supported/Comprehensive)
- Duration, consultations, follow-ups, chat type
- Expert mix per tier
- Outcomes (Clarity/Timeline/Support)
- Journey steps
- Why Niro bullets
- FAQs
- Optional remedies

---

## Key Files

### Frontend (V6)
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx` - V6 premium home
- `/app/frontend/src/components/screens/simplified/TopicLandingPage.jsx` - V6 landing page
- `/app/frontend/src/components/screens/simplified/v6Data/landingPageContentV6.js` - V6 content source
- `/app/frontend/src/components/screens/simplified/icons.jsx` - Minimalist icons

### Backend
- `/app/backend/niro_simplified/catalog.py` - Tier pricing and configuration
- `/app/backend/niro_simplified/routes.py` - Simplified API routes

---

## Payments
- **Provider:** Razorpay (INR)
- **Test mode:** Enabled with test keys in backend/.env

---

## Upcoming Tasks (P1)
1. Update Mira Chat welcome message
2. Implement post-purchase home screen experience

## Future Tasks (P2)
1. Onboarding flow refinements (8-screen flow, skip birth time)
2. Global design system application
3. Full Remedies implementation

## Technical Debt
- Remove unused V5 files (`SimplifiedAppV5.jsx`, `v5Screens/`, `v5Data/`)
