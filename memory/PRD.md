# NIRO V5 Product Requirements Document

## Overview
NIRO is an AI-powered Vedic astrology platform providing personalized guidance across Love, Career, and Health topics. V5 introduces a complete redesign of the onboarding flow and landing pages with a new visual theme.

## V5 Design System
- **Colors:** Teal/Gold palette (#3E827A primary, #EFE1A9 gold accents)
- **Typography:** Inter (body), Kumbh Sans (logo)
- **Background:** Linear gradient from teal to cream

## 8-Step Onboarding Flow

1. **Splash Screen** - Brand intro with "Get Started" CTA
2. **Birth Details** - Name, DOB, Time (skippable), Place
3. **Pick Topic** - Love, Career, or Health
4. **Pick Sub-topic** - 6 specific services per topic
5. **Trust Screen** - "Why NIRO?" section
6. **Choose Pack** - 3-tier selection (Focussed/Supported/Comprehensive)
7. **Checkout** - Razorpay payment integration
8. **Home** - Post-purchase dashboard

## 18 Sub-Topics Structure

### Love (6)
- Relationship Healing
- Family Relationships
- Dating & Compatibility
- Marriage Planning
- Communication & Trust
- Breakup & Closure

### Career (6)
- Career Clarity
- Job Transition
- Money Stability
- Work Stress
- Office Politics
- Big Decision Timing

### Health (6)
- Healing Journey
- Stress Management
- Energy & Balance
- Sleep Reset
- Emotional Recovery
- Women's Wellness

## Tier Structure
Each sub-topic has 3 tiers:
- **Focussed** - Entry level, 1 call, 7 days chat
- **Supported** ⭐ (Recommended) - 3 calls, unlimited chat
- **Comprehensive** - 5 calls, priority support

## Technical Implementation

### Frontend Files Created (2026-01-22)
```
/app/frontend/src/components/screens/simplified/
├── v5Screens/
│   ├── SplashScreenV5.jsx
│   ├── BirthDetailsScreenV5.jsx
│   ├── TopicSelectionScreen.jsx
│   ├── SubtopicSelectionScreen.jsx
│   ├── TrustScreenV5.jsx
│   ├── PackSelectionScreen.jsx
│   ├── CheckoutScreenV5.jsx
│   ├── HomeScreenV5.jsx
│   ├── LandingPageV5.jsx
│   └── index.js
├── v5Data/
│   ├── landingPageContent.js  (all 18 sub-topic content)
│   └── useOnboardingState.js  (state management hook)
└── SimplifiedAppV5.jsx  (main orchestrator)
```

### Backend Updates
- `/app/backend/niro_simplified/catalog.py` - Added 54 new tiers (18 × 3)

### Key Features
- ✅ "Skip birth time" option (sends null to API)
- ✅ "Recommended" badge always on Supported tier
- ✅ Razorpay payment integration preserved
- ✅ All content from provided JSON/Excel files
- ✅ Landing page follows Frame 27 wireframe structure

## Testing Status
- Backend: 25/25 tests passed (all tier APIs verified)
- Frontend: All V5 screens verified working

## Completed Work (2026-01-22)
- [x] V5 Design System (theme.js)
- [x] All 8 onboarding screens
- [x] Landing page component
- [x] 18 sub-topic content data file
- [x] Onboarding state management hook
- [x] Backend tier catalog (54 tiers)
- [x] App.js integration with V5 toggle

## Backlog
- [ ] Post-purchase home screen interactions
- [ ] Landing page e2e payment flow testing
- [ ] Profile screen integration
- [ ] Push notifications for follow-ups
