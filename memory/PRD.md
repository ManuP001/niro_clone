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
3. **Admins** - Business owners monitoring revenue and users

## Core Requirements
- Secure Google OAuth login
- Birth details collection for Kundli
- Topic-based consultation packages (Career, Relationships, etc.)
- Expert chat threads
- Razorpay payment processing
- Admin dashboard with revenue metrics

---

## What's Been Implemented

### Dec 2025 - Initial Build
- Full-stack app with React frontend + FastAPI backend
- Google OAuth 2.0 authentication flow
- Razorpay payment integration
- Vedic API integration for Kundli calculations
- MongoDB database with multiple collections

### Feb 2026 - Session 1
- Admin Dashboard at `/admin` with authentication
- Data aggregation from legacy + new collections
- Remedy purchase flow
- Environment tagging for orders

### Feb 2026 - Session 2
- **FIXED:** Payment "Authentication required" error (session token validation)
- **FIXED:** Google OAuth double login issue (router order fix)
- **FIXED:** OAuth loop in production (runtime URL resolution)
- **FIXED:** Vedic API key updated to correct key
- **ADDED:** Chakra Healing remedy (₹3,500, 3 sessions)

### Feb 2026 - Session 3 (Current) - Phase 2 Complete
- **IMPLEMENTED:** "My Pack" tab for paying customers
  - New `MyPackScreen.jsx` component
  - Shows package details, days remaining, deliverables
  - Schedule call option
  - Suggested remedies section
  - Quick actions (Mira, Kundli)
  - Support contact
  - File: `/app/frontend/src/components/screens/simplified/MyPackScreen.jsx`

- **IMPLEMENTED:** Removed per-minute pricing from landing pages
  - Updated `TopicLandingPage.jsx` sticky CTA bar
  - Now shows total package price instead of ₹/min
  - File: `/app/frontend/src/components/screens/simplified/TopicLandingPage.jsx`

- **FIXED:** "Buy Now" bar visibility on Remedy page
  - Changed modal z-index from z-50 to z-[60]
  - File: `/app/frontend/src/components/screens/simplified/RemediesScreen.jsx`

---

## Prioritized Backlog

### P0 - Critical (Deploy Required)
- [x] Phase 1 bug fixes complete
- [x] Phase 2 UI refinements complete
- [ ] Redeploy to production to apply all changes

### P1 - High Priority (Phase 3)
- [ ] Admin Dashboard CRUD for Plans
- [ ] Admin Dashboard CRUD for Remedies
- [ ] Admin Dashboard CRUD for Experts
- [ ] Admin Dashboard CRUD for Topics

### P2 - Medium Priority
- [ ] Admin dashboard revenue fix verification on production
- [ ] Schedule call integration (currently placeholder)

### P3 - Low Priority (Tech Debt)
- [ ] Remove obsolete JWT authentication code (`/app/backend/auth/`)
- [ ] Remove legacy V5 UI components
- [ ] Data migration to unified schema

---

## Technical Architecture

### Frontend
- React with Tailwind CSS
- Shadcn/UI components
- Google OAuth via redirect flow
- Runtime backend URL resolution via `getBackendUrl()`

### Backend
- FastAPI on port 8001
- MongoDB for data storage
- Razorpay SDK for payments
- Vedic API for astrology calculations
- Session token + JWT dual authentication support

### Key Files
- `/app/frontend/src/config.js` - Backend URL configuration with `getBackendUrl()`
- `/app/frontend/src/components/screens/simplified/MyPackScreen.jsx` - New My Pack screen
- `/app/frontend/src/components/screens/simplified/TopicLandingPage.jsx` - Landing page (pricing updated)
- `/app/frontend/src/components/screens/simplified/RemediesScreen.jsx` - Remedies with z-index fix
- `/app/frontend/src/components/screens/simplified/BottomNav.jsx` - Navigation with My Pack tab
- `/app/backend/niro_simplified/routes.py` - Main API routes with session token auth
- `/app/backend/routes/google_oauth_direct.py` - OAuth flow
- `/app/backend/server.py` - Router order (Google auth before legacy JWT)

### Database Collections
- `users` - User accounts
- `user_sessions` - OAuth session tokens
- `niro_simplified_orders` - Purchase orders
- `niro_simplified_plans` - Active subscriptions

---

## Credentials (Preview Environment)
- **Admin Dashboard:** NiroAdmin / NewAdmin@123
- **Vedic API Key:** `6792dc58-2dda-530b-82de-87777c7ecfe5` (in `/app/backend/.env`)
- **Razorpay:** Live keys in `.env`
