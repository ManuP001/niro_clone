# NIRO - AI Astrology Companion

## Original Problem Statement
Build a comprehensive astrology consultation platform with:
- Google OAuth authentication
- Package-based consultations with experts
- Razorpay payment integration
- Kundli/birth chart generation via Vedic API
- AI-powered chat (Mira)
- Admin dashboard for business monitoring

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
- Admin dashboard with full CRUD for catalog management

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
- Topics CRUD: `GET/POST/PUT/DELETE /api/admin/topics`
- Experts CRUD: `GET/POST/PUT/DELETE /api/admin/experts`
- Remedies CRUD: `GET/POST/PUT/DELETE /api/admin/remedies-catalog`
- Tiers CRUD: `GET/POST/PUT/DELETE /api/admin/tiers`
- Seed endpoint: `POST /api/admin/seed-catalog`

**Frontend Admin UI** (`/app/frontend/src/components/admin/AdminDashboard.jsx`):
- Generic `CatalogManager` component for all CRUD operations
- `TopicsManager` - Manage topics shown on home screen
- `ExpertsManager` - Manage expert profiles
- `RemediesCatalogManager` - Manage remedies catalog
- `TiersManager` - Manage consultation packages/tiers

**New MongoDB Collections:**
- `admin_topics` - Dynamic topics configuration
- `admin_experts` - Expert profiles
- `admin_remedies` - Remedies catalog
- `admin_tiers` - Consultation packages

---

## Admin Dashboard Features

### What Admins Can Do:
1. **Topics Management**
   - Add new topics (appears as tile on home screen)
   - Edit topic name, icon, tagline, color, order
   - Assign modalities (expert types) to topics
   - Activate/deactivate topics

2. **Experts Management**
   - Add new expert profiles
   - Edit name, bio, modality, languages, experience
   - Assign experts to topics
   - Set rating and total consults
   - Add photo URL

3. **Remedies Management**
   - Add new remedies (appears in Remedies section)
   - Edit price, description, benefits
   - Categorize: healing, pooja, gemstone, kit, ritual
   - Mark as featured
   - Activate/deactivate

4. **Packages/Tiers Management**
   - Create tiers for each topic
   - Set price, duration, calls included
   - Define features list
   - Mark as popular
   - Link to specific topics

---

## Prioritized Backlog

### P0 - Deploy Required
- [x] All Phase 1-3 changes complete
- [ ] Redeploy to production

### P1 - Enhancements
- [ ] Connect Topics/Tiers from admin DB to frontend display
- [ ] Expert photo upload functionality
- [ ] Schedule call integration

### P2 - Tech Debt
- [ ] Remove obsolete JWT auth code
- [ ] Data migration script for existing data
- [ ] Cache catalog data for performance

---

## Technical Architecture

### Frontend
- React with Tailwind CSS
- Runtime backend URL via `getBackendUrl()`
- Admin dashboard with CRUD components

### Backend
- FastAPI on port 8001
- MongoDB collections for catalog data
- Session token + JWT authentication

### Key Files
- `/app/frontend/src/components/admin/AdminDashboard.jsx` - Admin UI with CRUD
- `/app/backend/routes/admin.py` - Admin API endpoints
- `/app/frontend/src/components/screens/simplified/MyPackScreen.jsx` - My Pack tab
- `/app/frontend/src/config.js` - Backend URL configuration

### Database Collections (Catalog)
- `admin_topics` - Topics configuration
- `admin_experts` - Expert profiles  
- `admin_remedies` - Remedies catalog
- `admin_tiers` - Package tiers

---

## Credentials
- **Admin Dashboard:** NiroAdmin / NewAdmin@123
- **Vedic API Key:** `6792dc58-2dda-530b-82de-87777c7ecfe5`
- **Preview URL:** https://hierarchy-crud.preview.emergentagent.com/admin
