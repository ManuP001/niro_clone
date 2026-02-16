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

### Phase 6: Admin Dashboard Bug Fixes (Feb 12, 2026)
1. Fixed BACKEND_URL crash on Users & Orders pages
2. Fixed deactivation broken (model_dump exclude_unset)
3. Fixed Valentine's content display fallback
4. Fixed checkout DB lookup
5. Improved error messages

### Phase 7: Bottom Nav Restructure (Feb 12, 2026)
- New users: Home, Consult, Remedies, Astro (4 tabs)
- Returning users: Home, Consult, Remedies, My Pack, Astro (5 tabs)

### Phase 8: Bulk Upload Flow (Feb 12, 2026)
- POST /api/admin/bulk-upload
- GET /api/admin/bulk-upload/template
- Admin UI with file upload + JSON paste + preview

### Phase 9: P0 Bug Fixes (Feb 16, 2026)
1. **Export CSV fix** — Authenticated fetch + blob download
2. **Checkout back button fix** — Preserves/restores previous screen context
3. **Expert visibility fix** — Public endpoints merge DB + catalog experts

### Phase 10: Expert Tag System & Image Upload (Feb 16, 2026)
1. **3-Type Expert Tag System:**
   - **Life-situation tags** (A): 58 tags across 7 categories (Career & Work, Business & Finance, Relationships, Marriage, Health & Wellness, Spiritual, Other) — shown as "Best For" on profile
   - **Method tags** (B): 10 tags (Dasha analysis, Transit guidance, etc.)
   - **Remedy/Support tags** (C): 10 tags (Breathwork, Chakra meditation, etc.)
   - Profile display: life-situation tags + optionally 1 method tag
   - Backend: `GET /api/admin/tag-options`, updated ExpertCreate/ExpertUpdate models
   - Frontend: TagMultiSelect component with grouped categories, max limits (5/3/2)
2. **Expert Image Upload:**
   - Backend: `POST /api/admin/upload/image` (saves to /assets/uploads/, max 5MB)
   - Backend: `GET /api/admin/uploads/{filename}` (serves uploaded files)
   - Frontend: Image upload field with file chooser + URL paste option

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
- `/app/frontend/src/components/admin/AdminDashboard.jsx` - Admin UI (CRUD + Tags + Upload)
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx` - Dynamic homepage
- `/app/frontend/src/components/screens/simplified/BottomNav.jsx` - Bottom nav
- `/app/frontend/src/components/screens/simplified/SimplifiedApp.jsx` - Main app container
- `/app/frontend/src/components/screens/simplified/ExpertsScreen.jsx` - Expert listing with tag display
- `/app/backend/routes/admin.py` - Admin API (CRUD + Tags + Upload)
- `/app/backend/niro_simplified/routes.py` - Public API (experts, tiers, checkout)

### Database Collections
- `admin_categories` - Homepage categories
- `admin_tiles` - Homepage tiles
- `admin_topics` - Topics
- `admin_experts` - Expert profiles (with life_situation_tags, method_tags, remedy_tags)
- `admin_remedies` - Remedies catalog
- `admin_tiers` - Package tiers
- `admin_sessions` - Admin login sessions

---

## Credentials
- **Admin Dashboard:** NiroAdmin / NewAdmin@123

---

## Prioritized Backlog

### P2 - UI Cleanup
- [ ] Remove "New/Returning/Reset" tag from homepage
- [ ] Remove duplicate package summary from checkout
- [ ] Remove "No questions asked" & "100% satisfaction" from checkout
- [ ] Bulk CRUD (multi-select + bulk edit/delete in admin)

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
- `/app/test_reports/iteration_12.json` - Phase 1 bug fixes
- `/app/test_reports/iteration_13.json` - Phase 1-3 comprehensive
- `/app/test_reports/iteration_14.json` - Phase 9 P0 bug fixes (9/9 pass)
- `/app/test_reports/iteration_15.json` - Phase 10 Tags & Upload (15/15 pass + UI verified)
