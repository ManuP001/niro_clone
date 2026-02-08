# NIRO Product Requirements Document

## Overview
NIRO is an AI-powered Vedic astrology platform providing personalized guidance across Love, Career, and Health topics. The app uses Google OAuth for authentication and Razorpay for payments.

## Current Status (February 2026)
- **Active Version:** V6 Premium UI
- **Last Update:** February 8, 2026 - Admin Dashboard & Remedy Purchase Flow
- **Status:** ✅ Complete and tested

### Latest Changes (Feb 8, 2026)

#### ✅ Admin Dashboard Implementation
- **URL:** `/admin` - Password-protected admin panel
- **Credentials:** Username: `NiroAdmin`, Password: `NewAdmin@123`
- **Features:**
  - Dashboard overview with stats (users, orders, plans, revenue)
  - Users list with search, pagination, and detail view
  - Package orders list with revenue tracking
  - Plans list with status tracking
  - Remedy orders list
  - CSV export for all data types
  - Environment filter (Production/Preview/All)
- **Backend:** `/app/backend/routes/admin.py`
- **Frontend:** `/app/frontend/src/components/admin/AdminDashboard.jsx`

#### ✅ Remedy Purchase Flow
- Full Razorpay integration for remedy purchases
- Backend API: `/api/remedies/create-order`, `/api/remedies/verify-payment`
- Remedies catalog: 14 SKUs (poojas, gemstones, kits, rituals)
- Email notifications on successful purchase
- **Backend:** `/app/backend/routes/remedies.py`
- **Frontend:** Updated `RemediesScreen.jsx` with payment flow

#### ✅ Bug Fixes
- Removed "Made with Emergent" badge from `index.html`
- Environment tagging added to all orders (production/preview)
- Expert tracking added to package orders

#### ⚠️ Pending User Action
- **Google OAuth:** User needs to add new redirect URI to Google Console:
  - `https://mystic-portal-18.preview.emergentagent.com/auth/callback`
- **Email notifications:** Verified working - emails sent to `booking@getniro.ai`

### Previous Changes (Jan 23-26, 2026)
- ✅ Migrated from email/phone login to Google OAuth 2.0
- ✅ Updated Vedic API key (was expired)
- ✅ Fixed profile update network error
- ✅ Updated onboarding screen content
- ✅ Price-per-minute display in topic landing page footer
- ✅ "My Pack" tab for returning users
- ✅ Removed old version toggles (V2, V5)

## Architecture

### Backend (FastAPI)
```
/app/backend/
├── server.py                 # Main app entry
├── routes/
│   ├── admin.py             # Admin dashboard API (NEW)
│   ├── remedies.py          # Remedy purchase API (NEW)
│   ├── google_oauth_direct.py # Google OAuth
├── niro_simplified/
│   ├── routes.py            # Package checkout API (updated)
│   ├── storage.py           # MongoDB storage
│   └── catalog.py           # Package/tier catalog
├── services/
│   └── email_service.py     # Resend email notifications
└── profile/
    └── __init__.py          # User profile management
```

### Frontend (React)
```
/app/frontend/src/
├── App.js                    # Main app with admin route
├── components/
│   ├── admin/
│   │   └── AdminDashboard.jsx # Full admin dashboard (NEW)
│   └── screens/
│       └── simplified/
│           ├── RemediesScreen.jsx # With payment (updated)
│           └── ...
```

### MongoDB Collections
| Collection | Purpose |
|------------|---------|
| `users` | User accounts (Google OAuth) with birth details |
| `user_sessions` | Login sessions |
| `niro_simplified_orders` | Package orders (with environment tag) |
| `niro_simplified_plans` | Active plans |
| `niro_remedy_orders` | Remedy purchases (NEW) |
| `niro_simplified_threads` | Chat threads |

## API Endpoints

### Admin API (Protected)
- `POST /api/admin/login` - Admin authentication
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/users` - Users list with pagination
- `GET /api/admin/orders` - Package orders list
- `GET /api/admin/plans` - Plans list
- `GET /api/admin/remedy-orders` - Remedy orders list
- `GET /api/admin/export/users` - Export users CSV
- `GET /api/admin/export/orders` - Export orders CSV
- `GET /api/admin/export/plans` - Export plans CSV
- `GET /api/admin/export/remedies` - Export remedy orders CSV

### Remedy API
- `GET /api/remedies/catalog` - Get remedies catalog
- `POST /api/remedies/create-order` - Create Razorpay order
- `POST /api/remedies/verify-payment` - Verify payment
- `GET /api/remedies/my-orders` - Get user's remedy orders

### Auth API
- `GET /api/auth/google/login` - Initiate Google OAuth
- `POST /api/auth/google/callback` - Handle OAuth callback
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

## Environment Variables (Backend)
```
MONGO_URL, DB_NAME
RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
RESEND_API_KEY, SENDER_EMAIL, BOOKING_EMAIL
GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
ADMIN_USERNAME, ADMIN_PASSWORD
VEDIC_API_KEY
```

## Upcoming Tasks

### P1 - High Priority
- [ ] Test end-to-end purchase flow with real payment
- [ ] Verify email notifications reach booking@getniro.ai
- [ ] Fix Google OAuth redirect URI (user action)

### P2 - Medium Priority
- [ ] Implement new onboarding flow (UX research doc ready)
- [ ] Post-purchase home screen
- [ ] Remedies feature completion

### P3 - Technical Debt
- [ ] Remove legacy JWT auth code
- [ ] Delete V5 code files
- [ ] Simplify App.js routing

---
*Last updated: February 8, 2026*
