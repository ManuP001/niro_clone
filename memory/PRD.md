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

### Feb 2026 - Session 2 (Current)
- **FIXED:** Payment "Authentication required" error
  - Root cause: Session tokens from Google OAuth weren't being validated
  - Solution: Added async session token validation in `get_user_id_from_token_async()`
  - Affected file: `/app/backend/niro_simplified/routes.py`
  
- **IDENTIFIED:** Google OAuth redirect_uri_mismatch on production
  - Requires adding `https://getniro.ai/auth/callback` to Google Cloud Console

---

## Prioritized Backlog

### P0 - Critical (Blocking Users)
- [ ] Add production redirect URI to Google Cloud Console
- [ ] Redeploy to production

### P1 - High Priority (Phase 2)
- [ ] Implement "My Pack" tab for paying customers
- [ ] Remove per-minute pricing from landing pages
- [ ] Fix "Buy Now" bar visibility on Remedy page

### P2 - Medium Priority (Phase 3)
- [ ] Admin Dashboard CRUD for Plans, Remedies, Experts, Topics
- [ ] Admin dashboard revenue fix verification on production

### P3 - Low Priority (Tech Debt)
- [ ] Remove obsolete JWT authentication code
- [ ] Remove legacy V5 UI components
- [ ] Data migration to unified schema

---

## Technical Architecture

### Frontend
- React with Tailwind CSS
- Shadcn/UI components
- Google OAuth via redirect flow

### Backend
- FastAPI on port 8001
- MongoDB for data storage
- Razorpay SDK for payments
- Vedic API for astrology calculations

### Key Files
- `/app/backend/niro_simplified/routes.py` - Main API routes with auth fix
- `/app/backend/routes/google_oauth_direct.py` - OAuth flow
- `/app/frontend/src/components/screens/simplified/` - Main UI

### Database Collections
- `users` - User accounts
- `user_sessions` - OAuth session tokens
- `niro_simplified_orders` - Purchase orders
- `niro_simplified_plans` - Active subscriptions

---

## Credentials (Preview Environment)
- **Admin Dashboard:** NiroAdmin / NewAdmin@123
- **Vedic API Key:** In `/app/backend/.env`
- **Razorpay:** Live keys in `.env`
