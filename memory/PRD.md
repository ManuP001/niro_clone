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
- **Public homepage endpoint: `GET /api/admin/public/homepage-data` (no auth required)**

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

### Phase 4: Dynamic Homepage ✅
**Frontend (`/app/frontend/src/components/screens/simplified/HomeScreen.jsx`):**
- Fetches categories and tiles from `/api/admin/public/homepage-data`
- Falls back to hardcoded defaults if API fails
- Changes in admin dashboard reflect immediately on homepage
- No frontend redeployment needed for content changes

### Phase 5: Live Homepage Preview ✅ (NEW)
**Frontend (`/app/frontend/src/components/admin/AdminDashboard.jsx`):**
- Added `HomepagePreview` modal component
- "Preview Homepage" button in admin header
- Mobile phone frame showing exact homepage layout
- Shows all 3 categories with their tiles and icons
- Real-time data from database with refresh capability
- "Live data from database" indicator

**New MongoDB Collections:**
- `admin_categories` - Homepage categories (3)
- `admin_tiles` - Homepage tiles (18)
- `admin_topics` - Topics configuration (14)
- `admin_experts` - Expert profiles (31)
- `admin_remedies` - Remedies catalog (15)
- `admin_tiers` - Package tiers (112+)

---

## How Homepage Management Works

### For Admins:
1. Login to `/admin` with NiroAdmin credentials
2. Click **"Preview Homepage"** button in header to see current state
3. Click "Categories (3)" to manage the 3 main sections
4. Click "Tiles (18)" to manage the 18 tiles under each category
5. Click **"Preview Homepage"** again to see your changes
6. Changes are **immediately** visible on the user-facing homepage

### Data Flow:
```
Admin Dashboard → MongoDB → Public API → Homepage
     ↓                          ↓
 CRUD Operations          No Auth Required
     ↓
Preview Modal (Live Data)
```

### Example Admin Actions:
- **Rename category:** "Love & Relationships" → "Relationships & Love"
- **Reorder tiles:** Change "Healing" from order 1 to order 3
- **Add new tile:** Create "Astrology Reports" tile under Career
- **Hide tile:** Deactivate "Office Politics" tile (hidden from users)
- **Preview changes:** Click "Preview Homepage" to see how it looks

---

## Admin Dashboard Features

### Homepage Preview
- Click "Preview Homepage" button in top-right header
- Shows mobile phone frame with exact homepage layout
- Displays all categories and tiles with icons
- Shows "Live data from database" indicator
- Refresh button to reload latest changes
- Close button to dismiss

### Hierarchical Structure
**Categories (4)**
- Love & Relationships: Dating, commitment, healing, family dynamics
- **Valentine's Special**: NOT OFFICIAL YET, READY FOR MARRIAGE?, MOVE ON OR STAY?
- Career & Money: Work direction, stability, timing, growth
- Health & Wellness: Stress, recovery, energy, emotional balance

**Tiles (21 total)**
- Love: Healing, Dating, Marriage, Trust, Family, Closure (6)
- **Valentine's Special**: NOT OFFICIAL YET, READY FOR MARRIAGE?, MOVE ON OR STAY? (3) - NEW
- Career: Clarity, Job Change, Money, Timing, Work Stress, Office (6)
- Health: Stress, Sleep, Energy, Timing, Emotional, Recovery (6)

---

## Prioritized Backlog

### P0 - Deploy Required
- [x] All Phase 1-5 changes complete
- [x] Admin Dashboard hierarchical refactor complete
- [x] Homepage dynamic data integration complete
- [x] Live homepage preview modal complete
- [ ] Redeploy to production

### P1 - Enhancements
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
- **Homepage dynamically fetches from public API**
- **Live preview modal with mobile phone frame**

### Backend
- FastAPI on port 8001
- MongoDB collections for catalog data
- Session token + JWT authentication
- Persistent admin sessions in MongoDB
- **Public API for homepage data (no auth)**

### Key Files
- `/app/frontend/src/components/admin/AdminDashboard.jsx` - Admin UI with CRUD + **Preview Modal**
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx` - **Dynamic homepage**
- `/app/backend/routes/admin.py` - Admin API endpoints + **public homepage endpoint**
- `/app/frontend/src/config.js` - Backend URL configuration

### Database Collections (Catalog)
- `admin_categories` - Homepage categories (4 - added Valentine's Special)
- `admin_tiles` - Homepage tiles (21 - added 3 Valentine's tiles)
- `admin_topics` - Topics configuration (14)
- `admin_experts` - Expert profiles (31)
- `admin_remedies` - Remedies catalog (15)
- `admin_tiers` - Package tiers (112+)
- `admin_sessions` - Persistent admin login sessions

---

## API Reference

### Public Endpoints (No Auth)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/public/homepage-data` | GET | Get categories and tiles for homepage |

### Admin Endpoints (Requires X-Admin-Token)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/categories` | GET/POST | List/Create categories |
| `/api/admin/categories/{id}` | PUT/DELETE | Update/Delete category |
| `/api/admin/tiles` | GET/POST | List/Create tiles |
| `/api/admin/tiles/{id}` | PUT/DELETE | Update/Delete tile |
| `/api/admin/seed-catalog` | POST | Seed initial data |

---

## Credentials
- **Admin Dashboard:** NiroAdmin / NewAdmin@123
- **Vedic API Key:** `6792dc58-2dda-530b-82de-87777c7ecfe5`
- **Preview URL:** https://astro-admin-5.preview.emergentagent.com/admin

---

## Test Reports
- `/app/test_reports/iteration_10.json` - Admin hierarchy CRUD tests (100% pass)
- `/app/test_reports/iteration_11.json` - Public homepage API tests (100% pass)
- `/app/backend/tests/test_admin_hierarchy_crud.py` - Backend CRUD tests
- `/app/backend/tests/test_public_homepage_api.py` - Public API tests
