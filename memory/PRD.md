# NIRO Product Requirements Document

## Overview
NIRO is an AI-powered Vedic astrology platform providing personalized guidance across Love, Career, and Health topics. The app is on V4 with incremental improvements.

## Current Status (January 2025)
- **Active Version:** V4 (default)
- **Last Sprint:** Landing Page UI Improvements (Premium Minimal Design)
- **Status:** ✅ Complete and tested (17/17 features verified)

---

## Landing Page Design (V4 - Premium Minimal)

### Design Philosophy
- **ONE base background** - #FAFAFA across entire page (no rainbow sections)
- **TWO container styles** - Standard card (#FFFFFF) + Highlighted card (subtle border/shadow)
- **Section differentiation** via spacing, dividers, typography (not colors)

### Section Order (Top to Bottom)

1. **Header** - Back button + Sub-topic title
2. **Hero** - "Hi {userName}, here are the paths you can choose for your journey"
3. **Tier Selector Tabs**
   - Focussed (Quick clarity)
   - Supported (Full support) + Recommended badge
   - Comprehensive (Deep confidence)
4. **Tier Summary Card** (highlighted)
   - Name + Recommended badge
   - Price
   - 2x2 Grid: Duration | Consultation | Follow-ups | Chat
5. **Refund Guarantee Strip** - "No questions asked — 7 day full refund guarantee"
6. **Outcomes Section** (no colored backgrounds)
   - CLARITY (3 bullets)
   - TIMELINE (2 bullets)
   - SUPPORT (2 bullets)
7. **"How will your journey unfold?"** - 4-step timeline
   1. Choose your pack
   2. Get matched with an expert
   3. Calls + follow-ups + unlimited chat
   4. Optional add-ons (Coming soon - grayed)
8. **Optional Add-ons** - "Coming soon" pill, NO CTA button
9. **Why Niro** - Trust bullets including "Unlimited follow-ups till clarity"
10. **FAQs** - 6 objection-killer questions only
11. **Sticky CTA** - Price (left) + "Start my journey" (right) - NOTHING else

### Sticky CTA Requirements
- ✅ Shows: Price + CTA button only
- ❌ Does NOT show: Recommended tag, weeks, package name, secure payments, refund text

### Tier Configuration
| Tier | Micro-label | Sessions | Follow-ups | Chat |
|------|-------------|----------|------------|------|
| Focussed | Quick clarity | 1 call | 1 follow-up | 7 days |
| Supported | Full support | 3 calls | 2 follow-ups | Unlimited |
| Comprehensive | Deep confidence | 5 calls | 3+ follow-ups | Unlimited |

### FAQs (Objection-killers only)
1. When will my first consult happen?
2. Is chat really unlimited?
3. What happens after I pay?
4. What if I don't feel it helped?
5. How does the 7-day refund work?
6. Are experts verified?

---

## 18 Sub-Topics

### Love (6)
- Relationship Healing, Family Relationships, Dating & Compatibility
- Marriage Planning, Communication & Trust, Breakup & Closure

### Career (6)
- Career Clarity, Job Transition, Money Stability
- Work Stress, Office Politics, Big Decision Timing

### Health (6)
- Healing Journey, Stress Management, Energy & Balance
- Sleep Reset, Emotional Recovery, Women's Wellness

---

## Key Files Reference

### Frontend
- `TopicLandingPage.jsx` - Premium minimal landing page
- `SimplifiedApp.jsx` - Passes userName prop to landing page
- `v5Data/landingPageContent.js` - Content for all 18 sub-topics
- `theme.js` - V4 color system

### Backend
- `niro_simplified/catalog.py` - Tier pricing
- `niro_simplified/routes.py` - API endpoints

---

## Completed Work (January 2025)

### Landing Page UI Improvements Sprint ✅
- ✅ ONE base background (#FAFAFA)
- ✅ Premium minimal card styling
- ✅ Personalized hero: "Hi {userName}, here are the paths..."
- ✅ Tier tabs with micro-labels
- ✅ 2x2 package summary grid
- ✅ "Unlimited chat" (not "Async chat")
- ✅ Refund guarantee after summary section
- ✅ Outcomes grouped by Clarity/Timeline/Support (no colors)
- ✅ "How will your journey unfold?" 4-step timeline
- ✅ Add-ons with "Coming soon" pill (no CTA)
- ✅ Sticky CTA simplified (price + button only)
- ✅ "Unlimited follow-ups till clarity" in Why Niro
- ✅ Objection-killer FAQs
- ✅ Razorpay checkout works

---

## Testing Results
- **Iteration 3:** 100% pass rate (17/17 features)
- **Bug Fixed:** Duration "8 weeks weeks" → "8 weeks"

---

## Upcoming/Future Tasks

### P1 - Onboarding Flow
- Implement 8-screen onboarding with "skip birth time" feature
- Birth details screen: Full name, DOB, Time (skippable), Place

### P2 - Home Screen Enhancements
- Post-purchase home screen with topic rows
- Horizontal scrolling tiles
- "View All" links

### P3 - Chat & Other
- Update Mira chat welcome message
