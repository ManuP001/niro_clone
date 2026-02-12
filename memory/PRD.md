# NIRO - AI Astrology Companion

## Original Problem Statement
Build a comprehensive astrology consultation platform with:
- Google OAuth authentication
- Package-based consultations with experts
- Razorpay payment integration
- Kundli/birth chart generation via Vedic API
- AI-powered chat (Mira)
- Admin dashboard for business monitoring with hierarchical content management
- **Dynamic homepage** that reflects admin changes in real-time
- **Live preview** of homepage changes before they go live

## User Personas
1. **Seekers** - Users looking for astrological guidance
2. **Paying Customers** - Users who purchase consultation packages
3. **Admins** - Business owners managing catalog and monitoring revenue

## Core Requirements
- Secure Google OAuth login
- Birth details collection for Kundli
- Topic-based consultation packages (Career, Relationships, etc.)
- Expert chat threads
- Razorpay payment processing
- Admin dashboard with full CRUD for hierarchical catalog management
- **Homepage dynamically renders admin-managed categories and tiles**
- **Live preview modal to see changes before deployment**

---

## What's Been Implemented

### Phase 1-5: Core Platform (Previous Sessions)
- Google OAuth, birth details, Kundli, AI chat (Mira)
- Payment flow with Razorpay
- Admin dashboard with hierarchical CRUD
- Dynamic homepage from DB
- Live homepage preview modal
- Valentine's Special category + 3 packages

### Phase 6: Admin Dashboard Bug Fixes (Feb 12, 2026)
1. **Fixed BACKEND_URL crash** — Users & Orders pages crashed due to undefined `BACKEND_URL`. Replaced with `getBackendUrl()`.
2. **Fixed deactivation broken** — All entity update endpoints used `model_dump()` with `if v is not None` which dropped `false`/`0` values. Changed to `model_dump(exclude_unset=True)`.
3. **Fixed Valentine's content display** — `PackageLandingPage` now falls back to basic package fields (name, features, description) when rich `content` object is empty.
4. **Fixed checkout DB lookup** — `niro_simplified/routes.py` now uses `request.app.state.db` as primary DB source instead of unreliable storage singleton.
5. **Improved error messages** — `CatalogManager` maps technical errors to user-friendly messages.

### Phase 7: Bottom Nav Restructure (Feb 12, 2026)
- Removed **Mira** from bottom navigation (still accessible from homepage CTA)
- **New users** (no active plan): Home, Consult, Remedies, Astro (4 tabs)
- **Returning users** (active plan): Home, Consult, Remedies, My Pack, Astro (5 tabs)

### Phase 8: Bulk Upload Flow (Feb 12, 2026)
- **Backend**: `POST /api/admin/bulk-upload` — creates category + tiles + packages in one request (upserts)
- **Backend**: `GET /api/admin/bulk-upload/template` — downloadable JSON template
- **Frontend**: Bulk Upload page in admin sidebar under "Tools" section
- File upload + JSON paste + preview before upload + success/error reporting

---

## Technical Architecture

### Frontend
- React with Tailwind CSS
- Runtime backend URL via `getBackendUrl()`
- Admin dashboard with hierarchical CRUD + Bulk Upload
- Homepage dynamically fetches from public API

### Backend
- FastAPI on port 8001
- MongoDB collections for catalog data
- Session token + JWT authentication
- Public API for homepage data (no auth)

### Key Files
- `/app/frontend/src/components/admin/AdminDashboard.jsx` - Admin UI (CRUD + Bulk Upload + Preview)
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx` - Dynamic homepage
- `/app/frontend/src/components/screens/simplified/BottomNav.jsx` - Restructured bottom nav
- `/app/frontend/src/components/screens/simplified/PackageLandingPage.jsx` - Package landing with fallback
- `/app/backend/routes/admin.py` - Admin API (CRUD + Bulk Upload + Public endpoints)
- `/app/backend/niro_simplified/routes.py` - Checkout with fixed DB lookup
- `/app/backend/niro_simplified/catalog.py` - Hardcoded tiers including Valentine's

### Database Collections
- `admin_categories` - Homepage categories (4)
- `admin_tiles` - Homepage tiles (21)
- `admin_topics` - Topics (14)
- `admin_experts` - Expert profiles (31)
- `admin_remedies` - Remedies catalog (15)
- `admin_tiers` - Package tiers (118)
- `admin_sessions` - Admin login sessions

---

## Credentials
- **Admin Dashboard:** NiroAdmin / NewAdmin@123
- **Preview URL:** https://heart-payment-test.preview.emergentagent.com/admin

---

## Prioritized Backlog

### P0 - Deploy Required
- [x] All Phase 1-8 changes complete and tested

### P1 - Deferred UX (To-Do)
- [ ] Issue #5: Expand tile icons from 16 to full Lucide set
- [ ] Issue #7: Dynamic sidebar counts (replace hardcoded "Categories (3)", "Tiles (18)")
- [ ] Issue #9: Show feedback when categories are force-created as inactive

### P2 - Enhancements
- [ ] Expert Chat Selection — Allow customers to choose specific astrologer
- [ ] Countdown Timer — Valentine's Special category banner

### P3 - Tech Debt
- [ ] Remove obsolete JWT auth code
- [ ] Data migration script for existing data
- [ ] Cache catalog data for performance

---

## Test Reports
- `/app/test_reports/iteration_12.json` - Phase 1 bug fixes (18/18 pass)
- `/app/test_reports/iteration_13.json` - Phase 1-3 comprehensive (all pass)
- `/app/backend/tests/test_phase1_bug_fixes.py` - Backend regression tests
