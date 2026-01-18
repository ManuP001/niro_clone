# NIRO Simplified V1.5 Implementation

## Overview

V1.5 builds on the existing Simplified V1 foundation with key UX improvements:
- Bottom navigation for easier app navigation
- Dedicated Ask Mira screen (renamed from Niro Guide)
- Improved expert discovery without blur
- Fixed Razorpay payment flow
- Enhanced error handling
- **NEW: Gold color scheme from Visual Moodboard**
- **NEW: Skip birth details onboarding (login only)**
- **NEW: Branded splash screen with constellation pattern**

---

## Color Scheme (from Visual Moodboard)

| Element | Color Code | Name |
|---------|-----------|------|
| Primary Background | #d7b870 | Warm Gold |
| Logo/Text | #f0e9d1 | Off-white/Cream |
| Accent Lines | #e5d188 | Rich Gold |
| Button/Dark Text | #5c5c5c | Dark Gray |
| Muted Text | #9a8a6a | Muted Gold |
| Light Background | #f5f0e3 | Cream |

---

## What Changed in V1.5

### 1. Bottom Navigation (`BottomNav.jsx`)
**New Component**

A sticky bottom navigation bar with 3-4 tabs:
- **Home** (🏠) - Landing screen
- **Experts** (👥) - Browse all experts
- **Ask Mira** (💬) - AI guide chat
- **My Pack** (📦) - Only shown when user has active plan

**Rules:**
- My Pack tab appears immediately after successful purchase (no restart needed)
- Bottom nav hidden during checkout flow
- Sticky to bottom of screen

### 2. Ask Mira Screen (`AskMiraScreen.jsx`)
**New Component**

Full-screen chat interface replacing the overlay-only guide:
- Mira avatar and branding (purple theme)
- Connected to existing chat backend
- Quick reply chips for common questions
- Topic suggestions based on conversation
- Navigate to topics directly from chat

### 3. Experts Tab (`ExpertsScreen.jsx`)
**New Component**

Browse all 23+ experts grouped by modality:
- Filter by modality (Vedic, Tarot, Coach, etc.)
- Full expert cards with photos, bio, languages
- **Pre-purchase**: "Unlock to chat" routes to topic landing
- **Post-purchase**: "Chat now" starts thread directly
- Topic selector for multi-topic experts

### 4. Home Screen Updates
**Modified: `HomeScreen.jsx`**

- Replaced "Ask Niro" button with **text input box**
- Type message → Navigate to Ask Mira with message pre-filled
- Expanded layout to fill whitespace
- Better social proof display

### 5. Topic Landing Page Expert Cards
**Modified: `TopicLandingPage.jsx`**

- **Removed blur/lock overlay** from expert photos
- Full expert cards visible pre-purchase
- Only action buttons are locked ("Unlock to chat")
- Sticky CTA respects bottom nav spacing

### 6. Checkout Screen Improvements
**Modified: `CheckoutScreen.jsx`**

- Better error handling with error types
- Retry support for failed payments
- Clear messaging for verification failures
- Payment method indicators

### 7. Plan Dashboard Updates
**Modified: `PlanDashboard.jsx`**

- Works with bottom nav spacing
- Expert photos display correctly
- Improved thread creation flow

### 8. Backend Updates

**New Endpoint: `GET /api/simplified/experts/all`**
```json
{
  "ok": true,
  "experts": [...],
  "grouped_by_modality": {...},
  "modalities": ["vedic_astrologer", ...],
  "total_count": 23
}
```

**Updated Expert Data:**
- 23 experts across 14 modalities
- Real placeholder photos from randomuser.me
- Languages field populated
- Multiple topics per expert where appropriate

---

## Environment Variables Required

### Backend (.env)
```
RAZORPAY_KEY_ID=rzp_live_S2xl6qTVUYtJoq
RAZORPAY_KEY_SECRET=<your_secret>
```

### Frontend
No additional env vars needed - uses existing REACT_APP_BACKEND_URL

---

## Testing Guide

### Happy Path - New User
1. Open app → See splash screen → Home screen loads
2. Bottom nav shows 3 tabs: Home, Experts, Ask Mira
3. Type in "Ask Mira" input on home → Navigate to Mira screen
4. Click topic tile → Topic landing page loads
5. Expert cards show full photos (no blur)
6. Select tier → Checkout screen
7. Complete payment → Plan created
8. Bottom nav now shows 4 tabs (My Pack added)
9. Navigate to My Pack → See plan dashboard

### Happy Path - Returning User with Plan
1. Open app → Home shows active pack card
2. Bottom nav shows 4 tabs
3. Click My Pack → Plan dashboard
4. Start conversation with expert

### Experts Tab Flow
1. Click Experts tab
2. Browse all experts grouped by modality
3. Filter by modality using pills
4. Click "Unlock to chat" → Routes to topic landing
5. (Post-purchase) Click "Chat now" → Starts thread

### Ask Mira Flow
1. Click Ask Mira tab (or type in home input)
2. Ask questions about topics, packs, experts
3. Get suggestions with navigate buttons
4. Click "Explore Career" → Routes to Career topic

### Payment Failure Paths
1. **Order creation failure**: Shows error, allows retry
2. **Payment cancelled**: Dismisses modal, can retry
3. **Payment failed**: Shows reason, retry option
4. **Verification failed**: Shows support contact info

---

## Telemetry Events (V1.5)

All events include `flow_version: "simplified_v1_5"`

| Event | When |
|-------|------|
| `nav_tab_clicked` | User switches bottom nav tab |
| `mira_message_sent` | User sends message in Ask Mira |
| `experts_tab_viewed` | User opens Experts tab |
| `mira_screen_opened` | User opens Ask Mira screen |
| `purchase_cancelled` | User dismisses payment modal |
| `purchase_failed` | Payment fails (with reason) |
| `purchase_completed` | Payment successful |

---

## File Changes Summary

### New Files
- `/app/frontend/src/components/screens/simplified/BottomNav.jsx`
- `/app/frontend/src/components/screens/simplified/ExpertsScreen.jsx`
- `/app/frontend/src/components/screens/simplified/AskMiraScreen.jsx`

### Modified Files
- `/app/frontend/src/components/screens/simplified/SimplifiedApp.jsx` - Navigation rewrite
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx` - Ask Mira input
- `/app/frontend/src/components/screens/simplified/TopicLandingPage.jsx` - No blur experts
- `/app/frontend/src/components/screens/simplified/PlanDashboard.jsx` - Bottom nav support
- `/app/frontend/src/components/screens/simplified/CheckoutScreen.jsx` - Error handling
- `/app/frontend/src/components/screens/simplified/utils.js` - New telemetry
- `/app/frontend/src/components/screens/simplified/index.js` - New exports
- `/app/backend/niro_simplified/routes.py` - New experts endpoint
- `/app/backend/niro_simplified/catalog.py` - More experts with photos

---

## Known Limitations

1. **Thread View**: Basic implementation, needs full chat UI
2. **Call Booking**: UI exists but not functional
3. **Topic Pass Purchase**: Order creation exists, verification pending
4. **Expert Availability**: All show "available" (no real-time status)

---

## Next Steps (V1.6+)

- Full expert chat thread UI
- Call booking integration
- Push notifications
- Expert-side dashboard
- Analytics dashboard
