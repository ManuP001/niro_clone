# NIRO Product Requirements Document

## Overview
NIRO is an AI-powered Vedic astrology platform providing personalized guidance across Love, Career, and Health topics. The app is on V4 with incremental improvements.

## Current Status (January 2025)
- **Active Version:** V4 (default)
- **Completed Sprints:** Landing Page UI + Home Screen Revamp
- **Status:** ✅ Complete and tested

---

## Home Screen Design (V4 Revamp)

### Key Features
- **Animated Niro logo** - Constellation ring animation (20s spin)
- **Sticky header** - Logo + CTA buttons stay fixed when scrolling
- **3 Life Situations** with 6 tiles each = **18 tiles total**
- **Minimalist icons** - Clean stroke-based SVG icons
- **Same background** (#FAFAFA) as other screens

### Structure
1. **Fixed Header**
   - Animated Niro logo (bigger, with constellation ring)
   - Two smaller CTA buttons:
     - "Chat with Mira (AI Astrologer)"
     - "Talk to Expert"

2. **Scrollable Tiles Section**
   - Title: "Choose a life topic that feels the most uncertain right now"
   - **Love & Relationships** (6 tiles): Healing, Family, Dating, Marriage, Trust, Closure
   - **Career & Money** (6 tiles): Clarity, Job Change, Money, Work Stress, Office, Timing
   - **Health & Wellness** (6 tiles): Healing, Stress, Energy, Sleep, Emotional, Wellness

### Removed
- Old tagline "Not predictions. Not generic advice..."
- White layer over background
- Old horizontal carousel layout (replaced with 3x2 grids)

---

## Landing Page Design (Premium Minimal)

### Design Philosophy
- **ONE base background** (#FAFAFA)
- **TWO container styles** - Standard card + Highlighted card
- Section differentiation via spacing, dividers, typography

### Section Order
1. Header - Back + Title
2. Hero - "Hi {userName}, here are the paths..."
3. Tier Selector Tabs (Focussed/Supported/Comprehensive with micro-labels)
4. Tier Summary Card (2x2 grid: Duration, Consultation, Follow-ups, Unlimited chat)
5. Refund Guarantee Strip
6. Outcomes Section (Clarity/Timeline/Support groups)
7. "How will your journey unfold?" (4-step timeline)
8. Optional Add-ons ("Coming soon" pill, no CTA)
9. Why Niro (includes "Unlimited follow-ups till clarity")
10. FAQs (6 objection-killer questions)
11. Sticky CTA (Price + "Start my journey" only)

---

## 18 Sub-Topics

### Love & Relationships
| ID | Title | Icon |
|----|-------|------|
| relationship_healing | Healing | healing |
| family_relationships | Family | family |
| dating_compatibility | Dating | heart |
| marriage_planning | Marriage | rings |
| communication_trust | Trust | chat |
| breakup_closure | Closure | breakup |

### Career & Money
| ID | Title | Icon |
|----|-------|------|
| career_clarity | Clarity | compass |
| job_transition | Job Change | briefcase |
| money_stability | Money | wallet |
| work_stress | Work Stress | stress |
| office_politics | Office | office |
| big_decision_timing | Timing | clock |

### Health & Wellness
| ID | Title | Icon |
|----|-------|------|
| healing_journey | Healing | healing |
| stress_management | Stress | stress |
| energy_balance | Energy | energy |
| sleep_reset | Sleep | sleep |
| emotional_recovery | Emotional | emotional |
| womens_wellness | Wellness | wellness |

---

## Key Files

### Frontend
- `HomeScreen.jsx` - Revamped with animated logo, 3 situations, 18 tiles
- `TopicLandingPage.jsx` - Premium minimal landing page
- `v5Data/landingPageContent.js` - Content for all 18 sub-topics

### Backend
- `niro_simplified/catalog.py` - Tier pricing
- `niro_simplified/routes.py` - API endpoints

---

## Testing Results
- **Iteration 3:** Landing Page - 100% (17/17)
- **Iteration 4:** Home Screen - 100% (11/11)

---

## Upcoming/Future Tasks

### P1 - Onboarding Flow
- 8-screen onboarding with "skip birth time" feature

### P2 - Additional Features
- Mira chat welcome message update
- Post-purchase experience
