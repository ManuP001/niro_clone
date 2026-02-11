# NIRO - AI Astrology Companion

## Original Problem Statement
Build a comprehensive astrology consultation platform with:
- Google OAuth authentication
- Package-based consultations with experts
- Razorpay payment integration
- Kundli/birth chart generation via Vedic API
- AI-powered chat (Mira)
- Admin dashboard for business monitoring with hierarchical content management

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

---

## What's Been Implemented

### Phase 1: Critical Bug Fixes ✅
- Fixed Payment "Authentication required" error (session token validation)
- Fixed Google OAuth double login issue (router order fix)
- Fixed OAuth loop in production (runtime URL resolution via `getBackendUrl()`)
- Updated Vedic API key
- Added Chakra Healing remedy (₹3,500, 3 sessions)

### Phase 2: UI & UX Refinements ✅
- Implemented "My Pack" tab for paying customers (`MyPackScreen.jsx`)
- Removed per-minute pricing from landing pages
- Fixed "Buy Now" bar visibility on Remedy page (z-index fix)

### Phase 3: Admin Dashboard CRUD ✅
**Backend APIs** (`/app/backend/routes/admin.py`):
- Categories CRUD: `GET/POST/PUT/DELETE /api/admin/categories`
- Tiles CRUD: `GET/POST/PUT/DELETE /api/admin/tiles`
- Topics CRUD: `GET/POST/PUT/DELETE /api/admin/topics`
- Experts CRUD: `GET/POST/PUT/DELETE /api/admin/experts`
- Remedies CRUD: `GET/POST/PUT/DELETE /api/admin/remedies-catalog`
- Tiers CRUD: `GET/POST/PUT/DELETE /api/admin/tiers`
- Seed endpoint: `POST /api/admin/seed-catalog`

**Frontend Admin UI** (`/app/frontend/src/components/admin/AdminDashboard.jsx`):
- Generic `CatalogManager` component for all CRUD operations
- **Homepage Section:**
  - `CategoriesManager` - Manage 3 homepage categories
  - `TilesManager` - Manage 18 homepage tiles
- **Catalog Section:**
  - `TopicsManager` - Manage topics
  - `ExpertsManager` - Manage expert profiles
  - `RemediesCatalogManager` - Manage remedies catalog
  - `TiersManager` - Manage consultation packages/tiers

**New MongoDB Collections:**
- `admin_categories` - 3 homepage category groupings
- `admin_tiles` - 18 homepage tiles (6 per category)
- `admin_topics` - Dynamic topics configuration
- `admin_experts` - Expert profiles (31 total)
- `admin_remedies` - Remedies catalog (15 total)
- `admin_tiers` - Consultation packages (112+ total)

---

## Admin Dashboard Features

### Hierarchical Structure (New!)
**Categories (3)**
- Love & Relationships: Dating, commitment, healing, family dynamics
- Career & Money: Work direction, stability, timing, growth
- Health & Wellness: Stress, recovery, energy, emotional balance

**Tiles (18 total, 6 per category)**
- Love: Healing, Dating, Marriage, Trust, Family, Closure
- Career: Clarity, Job Change, Money, Timing, Work Stress, Office
- Health: Stress, Sleep, Energy, Timing, Emotional, Recovery

### What Admins Can Do:
1. **Categories Management**
   - Add new homepage category groupings
   - Edit category title, helper copy, order
   - Activate/deactivate categories

2. **Tiles Management**
   - Add new homepage tiles
   - Assign tiles to categories
   - Edit short title, full title, icon, order
   - Activate/deactivate tiles

3. **Topics Management**
   - Add new topics (appears as tile on home screen)
   - Edit topic name, icon, tagline, color, order
   - Assign modalities (expert types) to topics
   - Activate/deactivate topics

4. **Experts Management**
   - Add new expert profiles
   - Edit name, bio, modality, languages, experience
   - Assign experts to topics
   - Set rating and total consults
   - Add photo URL

5. **Remedies Management**
   - Add new remedies (appears in Remedies section)
   - Edit price, description, benefits
   - Categorize: healing, pooja, gemstone, kit, ritual
   - Mark as featured
   - Activate/deactivate

6. **Packages/Tiers Management**
   - Create tiers for each topic
   - Set price, duration, calls included
   - Define features list
   - Mark as popular
   - Link to specific topics

---

## Prioritized Backlog

### P0 - Deploy Required
- [x] All Phase 1-3 changes complete
- [x] Admin Dashboard hierarchical refactor complete
- [ ] Redeploy to production

### P1 - Enhancements
- [ ] Connect Categories/Tiles from admin DB to frontend homepage display
- [ ] Expert photo upload functionality
- [ ] Schedule call integration
- [ ] Expert Chat Selection - Allow customers to choose specific astrologer

### P2 - Tech Debt
- [ ] Remove obsolete JWT auth code
- [ ] Data migration script for existing data
- [ ] Cache catalog data for performance

### P3 - Verification Pending
- [ ] Verify Google OAuth double login is fully resolved
- [ ] Verify Admin Dashboard revenue calculation accuracy

---

## Technical Architecture

### Frontend
- React with Tailwind CSS
- Runtime backend URL via `getBackendUrl()`
- Admin dashboard with hierarchical CRUD components

### Backend
- FastAPI on port 8001
- MongoDB collections for catalog data
- Session token + JWT authentication
- Persistent admin sessions in MongoDB

### Key Files
- `/app/frontend/src/components/admin/AdminDashboard.jsx` - Admin UI with CRUD
- `/app/backend/routes/admin.py` - Admin API endpoints
- `/app/frontend/src/components/screens/simplified/MyPackScreen.jsx` - My Pack tab
- `/app/frontend/src/config.js` - Backend URL configuration

### Database Collections (Catalog)
- `admin_categories` - Homepage categories (3)
- `admin_tiles` - Homepage tiles (18)
- `admin_topics` - Topics configuration (14)
- `admin_experts` - Expert profiles (31)
- `admin_remedies` - Remedies catalog (15)
- `admin_tiers` - Package tiers (112+)
- `admin_sessions` - Persistent admin login sessions

---

## Credentials
- **Admin Dashboard:** NiroAdmin / NewAdmin@123
- **Vedic API Key:** `6792dc58-2dda-530b-82de-87777c7ecfe5`
- **Preview URL:** https://hierarchy-crud.preview.emergentagent.com/admin

---

## Test Reports
- `/app/test_reports/iteration_10.json` - Admin hierarchy CRUD tests (100% pass rate)
- `/app/backend/tests/test_admin_hierarchy_crud.py` - Backend test file
