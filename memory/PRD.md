# NIRO - AI Astrology Companion

## Original Problem Statement
Build a comprehensive astrology consultation platform with:
- Google OAuth authentication
- Package-based consultations with experts
- Razorpay payment integration
- Kundli/birth chart generation via Vedic API
- AI-powered chat (Mira)
- Admin dashboard for business monitoring with hierarchical content management
- Dynamic homepage that reflects admin changes in real-time
- Live preview of homepage changes before they go live

## User Personas
1. **Seekers** - Users looking for astrological guidance
2. **Paying Customers** - Users who purchase consultation packages
3. **Admins** - Business owners managing catalog and monitoring revenue

---

## Current Redesign Project (Feb 2026)
Major UI/UX redesign based on `niro-final-marquee_1.html` to:
- Adopt new teal/peach/cream color scheme with Lexend font
- Remove phone-frame layout for true responsive design
- Implement new navigation (desktop header + mobile bottom nav)
- Add testimonials marquee, footer, and social links

### Redesign 5-Phase Plan Status:

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Foundation & Theme Swap | ✅ COMPLETE |
| 2 | Navigation Overhaul | 🔲 PENDING |
| 3 | Layout & Grid Transformation | 🔲 PENDING |
| 4 | Component Refactoring & CTA Mapping | 🔲 PENDING |
| 5 | Backlog & Polish | 🔲 PENDING |

---

## What's Been Implemented

### Phase 1-5: Core Platform (Previous Sessions)
- Google OAuth, birth details, Kundli, AI chat (Mira)
- Payment flow with Razorpay
- Admin dashboard with hierarchical CRUD
- Dynamic homepage from DB
- Live homepage preview modal

### Phase 6: Admin Dashboard Bug Fixes (Feb 12, 2026)
- Fixed Users/Orders page crashes, deactivation logic, checkout DB lookup, error messages

### Phase 7: Bottom Nav Restructure (Feb 12, 2026)
- New users: Home, Consult, Remedies, Astro (4 tabs)
- Returning users: Home, Consult, Remedies, My Pack, Astro (5 tabs)

### Phase 8: Bulk Upload Flow (Feb 12, 2026)
- POST /api/admin/bulk-upload + template download + admin UI

### Phase 9: P0 Bug Fixes (Feb 16, 2026)
1. Export CSV fix — Authenticated fetch + blob download
2. Checkout back button fix — Preserves/restores previous screen context
3. Expert visibility fix — Public endpoints merge DB + catalog experts

### Phase 10: Expert Tag System & Image Upload (Feb 16, 2026)
1. 3-Type Expert Tag System: life_situation (58), method (10), remedy_support (10)
2. Expert Image Upload: POST /api/admin/upload/image + admin form

### Phase 11: P2 UI Cleanup & Bulk CRUD (Feb 16, 2026)
1. Removed DevToggle (New/Returning/Reset) from homepage
2. Removed "What you'll get" duplicate section from checkout
3. Removed RefundBadge ("No questions asked" & "100% satisfaction") from checkout
4. Bulk CRUD: Multi-select checkboxes + bulk Deactivate/Delete in all admin tables

### Phase 12: Redesign - Foundation & Theme Swap (Feb 18, 2026)
1. **Lexend Font Integration** - Updated index.html and index.css with Lexend as primary font
2. **New CSS Variables** - Created design tokens (--niro-teal, --niro-peach, --niro-cream)
3. **Theme.js Overhaul** - Updated colors, shadows, typography for new design system
4. **Phone Frame Removal** - Removed lg:max-w-md constraint from App.js
5. **Responsive Container** - SimplifiedApp now uses max-w-7xl mx-auto for full-width
6. **LoginScreen Update** - New teal-cream gradient, pill-shaped button, Lexend font
7. **HomeScreen Update** - New hero section with teal gradient, peach CTA button
8. **BottomNav Update** - Added md:hidden for mobile-only display
9. **Responsive Tiles Grid** - 3 cols mobile, 6 cols desktop (grid-cols-3 md:grid-cols-6)

### Phase 13: Public Landing Page & Intent-Based Routing (Feb 18, 2026)
1. **PublicLandingPage.jsx** - New public entry point based on niro-final-marquee_1.html
   - Hero section with teal gradient, trust badges, peach CTA
   - Testimonials marquee with 6 customer reviews
   - "What We Offer" section with 5 feature cards
   - "Life Topics" section with 4 topic cards (Career, Health, Love, Fertility)
   - "How It Works" 4-step section
   - "Our Experts" horizontal scroll with 4 expert cards
   - Footer with logo, disclaimer, social icons (Instagram, X, LinkedIn, YouTube), and links
   - Sticky navigation with backdrop blur
   - Mobile hamburger menu
2. **ScheduleCallScreen.jsx** - Google Calendar booking integration (https://calendar.app.google/cm7fCPK7iHWPXvTY6)
3. **App.js Rewrite** - New routing flow:
   - Entry: PublicLandingPage (public, no auth required)
   - CTAs store intent in localStorage before login redirect
   - After login: Route based on intent + user type
4. **SimplifiedApp.jsx Updates** - Intent-based post-login routing:
   - free_call intent: New user → Birth Details → Schedule | Returning → Schedule
   - consultation:topicId: New user → Birth Details → Home | Returning → Home or MyPack
5. **Intent Storage System** - setUserIntent(), getUserIntent(), clearUserIntent() helpers

---

## Technical Architecture

### Key Files (Updated for Redesign)
- `/app/frontend/src/index.css` - CSS variables and Lexend font
- `/app/frontend/src/components/screens/simplified/theme.js` - V10 design tokens
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx` - New hero + responsive layout
- `/app/frontend/src/components/screens/simplified/SimplifiedApp.jsx` - Phone frame removed
- `/app/frontend/src/components/screens/simplified/BottomNav.jsx` - Mobile-only (md:hidden)
- `/app/frontend/src/components/screens/LoginScreen.jsx` - New login design
- `/app/frontend/src/App.js` - Removed phone frame wrapper

### Database Collections
- admin_categories, admin_tiles, admin_topics, admin_experts, admin_remedies, admin_tiers, admin_sessions

---

## Credentials
- **Admin Dashboard:** NiroAdmin / NewAdmin@123

---

## Prioritized Backlog

### Redesign Phases 2-5 (P0 - Current Priority)
- [ ] Phase 2: Desktop nav, mobile hamburger, sticky header with blur
- [ ] Phase 3: Multi-column grids, centered containers for other screens
- [ ] Phase 4: Component refactoring, CTA sitemap implementation
- [ ] Phase 5: Footer, social icons, tile sizing fix, backlog items

### P2 - Tile Sizing (deferred by user)
- [ ] Fix tile sizing — make production tiles compact like admin preview

### P3 - Deferred UX
- [ ] Expand tile icon picker to full Lucide set
- [ ] Dynamic sidebar counts (Categories, Tiles)
- [ ] Show feedback on entity creation

### Tech Debt
- [ ] Remove obsolete JWT auth code
- [ ] Data migration script
- [ ] Cache catalog data for performance

---

## Test Reports
- `/app/test_reports/iteration_14.json` - Phase 9 P0 bug fixes (9/9 pass)
- `/app/test_reports/iteration_15.json` - Phase 10 Tags & Upload (15/15 pass)
- `/app/test_reports/iteration_16.json` - Phase 11 UI Cleanup & Bulk CRUD (100% frontend pass)
- `/app/test_reports/iteration_17.json` - Phase 12 Foundation & Theme Swap (100% pass, 13/13 features)
