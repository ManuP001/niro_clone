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

---

## Technical Architecture

### Key Files
- `/app/frontend/src/components/admin/AdminDashboard.jsx` - Admin UI (CRUD + Tags + Upload + Bulk)
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx` - Dynamic homepage
- `/app/frontend/src/components/screens/simplified/SimplifiedApp.jsx` - Main app container
- `/app/frontend/src/components/screens/simplified/ExpertsScreen.jsx` - Expert listing
- `/app/frontend/src/components/screens/simplified/CheckoutScreen.jsx` - Checkout flow
- `/app/backend/routes/admin.py` - Admin API (CRUD + Tags + Upload)
- `/app/backend/niro_simplified/routes.py` - Public API (experts, tiers, checkout)

### Database Collections
- admin_categories, admin_tiles, admin_topics, admin_experts, admin_remedies, admin_tiers, admin_sessions

---

## Credentials
- **Admin Dashboard:** NiroAdmin / NewAdmin@123

---

## Prioritized Backlog

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
