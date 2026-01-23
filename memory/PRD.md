# NIRO Product Requirements Document

## Overview
NIRO is an AI-powered Vedic astrology platform providing personalized guidance across Love, Career, and Health topics. The app is currently on V4 with incremental improvements being made.

## Current Status (December 2024)
- **Active Version:** V4 (default)
- **Last Sprint:** Landing Page Redesign (Frame 27 wireframe implementation)
- **Status:** ✅ Complete and tested

---

## Landing Page Structure (Frame 27 Implementation)

### Section Order (11 Sections)
1. **Header** - Back button + Sub-topic title
2. **Hero** - Category label, headline, promise, refund guarantee
3. **Tier Selector Tabs** - Focussed / Supported (Recommended) / Comprehensive
4. **Tier Summary Card** - Price, duration, sessions, follow-ups, chat status
5. **Outcomes Section** - "What will this journey help you with?"
6. **How It Unfolds** - Expert type, consultations, async chat, response SLA
7. **Paid Remedies Slider** - Optional add-ons (horizontal scroll)
8. **Sticky CTA Bar** - Fixed bottom with price, tier, "Start my journey" button
9. **After Purchase Steps** - 4-step timeline
10. **Why Niro Trust Section** - 5 trust bullets including "Unlimited follow-ups till clarity"
11. **FAQ Accordion** - Sub-topic specific FAQs

### Tier Configuration
| Tier | Sessions | Follow-ups | Chat | Price Range |
|------|----------|------------|------|-------------|
| Focussed | 1 session | 1 included | 7 days | ₹2,999 - ₹7,999 |
| Supported (Recommended) | 3 sessions | 2 included | Unlimited | ₹4,999 - ₹9,999 |
| Comprehensive | 5 sessions | 3+ included | Unlimited (priority) | ₹6,999 - ₹11,999 |

### Key Requirements Met
- ✅ Supported tier shows "Recommended" badge on tab, card, and CTA
- ✅ Tier switching updates content on same page (no navigation)
- ✅ Sticky CTA always visible with trust microtext
- ✅ Uses V4 color theme (Teal/Gold: #3E827A, #EFE1A9)
- ✅ Content from landingPageContent.js (18 sub-topics)
- ✅ Remedies section hidden if no remedies available

---

## 18 Sub-Topics Structure

### Love (6)
- Relationship Healing (₹6,999-₹10,999)
- Family Relationships (₹5,999-₹9,999)
- Dating & Compatibility (₹4,999-₹8,999)
- Marriage Planning (₹7,999-₹11,999)
- Communication & Trust (₹5,999-₹9,999)
- Breakup & Closure (₹4,999-₹8,999)

### Career (6)
- Career Clarity (₹4,999-₹8,999)
- Job Transition (₹7,999-₹11,999)
- Money Stability (₹2,999-₹6,999)
- Work Stress (₹4,999-₹8,999)
- Office Politics (₹4,999-₹8,999)
- Big Decision Timing (₹2,999-₹6,999)

### Health (6)
- Healing Journey (₹4,999-₹8,999)
- Stress Management (₹7,999-₹11,999)
- Energy & Balance (₹4,999-₹8,999)
- Sleep Reset (₹4,999-₹8,999)
- Emotional Recovery (₹4,999-₹8,999)
- Women's Wellness (₹4,999-₹8,999)

---

## V4 Design System
- **Primary Color:** Teal (#3E827A)
- **Accent Color:** Gold (#EFE1A9)
- **Typography:** Inter (body), Kumbh Sans (logo)
- **Background:** Linear gradient from teal to cream

---

## Key Files Reference

### Frontend
- `TopicLandingPage.jsx` - Main landing page component (Frame 27 layout)
- `v5Data/landingPageContent.js` - Content for all 18 sub-topics
- `TileCard.jsx` - Home screen tiles with data-testid
- `SimplifiedApp.jsx` - App navigation and state management
- `CheckoutScreen.jsx` - Razorpay checkout flow
- `theme.js` - V4 color system and design tokens

### Backend
- `niro_simplified/catalog.py` - Tier pricing for all 54 combinations
- `niro_simplified/routes.py` - API endpoints

---

## Completed Work

### December 2024 - Landing Page Sprint
- ✅ Redesigned TopicLandingPage.jsx with Frame 27 layout
- ✅ Implemented 11-section structure
- ✅ Tier selector with instant content updates
- ✅ "Recommended" badge for Supported tier
- ✅ Sticky CTA bar with trust microtext
- ✅ Added PhoneIcon to icons.jsx
- ✅ Added getSubtopicBySlug/getAllSubtopics helpers
- ✅ Added data-testid to TileCard for testing
- ✅ Testing: 100% pass rate (14/14 features)

---

## Upcoming/Future Tasks

### P1 - Onboarding Flow
- Implement 8-screen onboarding (Splash → Birth → Topic → Sub-topic → Trust → Pack → Checkout → Home)
- "Skip birth time" functionality (birth_time: null)

### P2 - Home Screen Enhancements
- Post-purchase home screen with topic rows
- Horizontal scrolling tiles
- "View All" links
- Unique icons per tile

### P3 - Chat & Remedies
- Update Mira chat welcome message
- Remedies as "done-for-you" services

---

## Testing Notes
- Test URL: localhost:3000
- Login: Any email (no password required)
- Skip onboarding: Set localStorage 'niro_onboarding_completed'='true'
- Key test selectors: tile-{id}, tier-tab-{tier}, start-journey-btn, landing-back-btn
