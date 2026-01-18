# NIRO Simplified V2 Implementation

## Overview

V2 builds on V1.5 with key UX improvements for a more "real" and usable experience:
- DEV toggle for New/Returning user simulation
- Updated bottom navigation with Profile tab
- Ask Mira section moved below topics with rotating placeholders
- Expert profile pages
- Full expert photos without blur
- Payment flow working end-to-end

---

## What Changed in V2

### 1. DEV Toggle (New/Returning User)
**Location:** Top-left corner of the app

- **New User mode:** 
  - Bottom nav shows: Home, Experts, Ask Mira, Profile (NO My Pack)
  - Home shows topics + Ask Mira input
  
- **Returning User mode:**
  - Bottom nav shows: Home, Experts, Ask Mira, Profile, My Pack
  - Home shows Active Pack card + topics + Ask Mira
  
- Persisted in `localStorage` with key `niro_user_state`
- Values: `NEW` or `RETURNING`

### 2. Bottom Navigation V2
**Tabs (in order):**
1. Home (🏠)
2. Experts (👥)
3. Ask Mira (✨)
4. Profile (👤)
5. My Pack (📦) - *Only shown in Returning mode or with active plan*

### 3. Home Screen: Ask Mira Placement
**Changes:**
- Ask Mira section now appears **AFTER** Life Topics
- Header: **"Share what's on your mind."**
- Removed "Your personal guide" subtitle

**Rotating Placeholders:**
- Changes every 3 seconds
- Stops when input is focused or user starts typing
- Resumes when cleared/unfocused
- Example prompts:
  - "How do I manage my anger?"
  - "When will I get married?"
  - "Should I switch jobs now?"
  - And 9 more...

### 4. Expert Profile Page
**New Screen: `ExpertProfileScreen.jsx`**

Shows full expert details:
- Large photo (no blur)
- Name, modality, rating
- Best-for tags
- Topics covered
- Languages
- Bio
- Social proof stats (rating, sessions, years)

**Gating:**
- Pre-purchase: "🔓 Unlock to talk" button
- Post-purchase: "💬 Start Chat" button

### 5. Experts Screen Updates
- Added search functionality
- Click on expert card → Opens Expert Profile page
- "Tap to unlock" indicator on cards

### 6. Profile Screen
**New Screen: `ProfileScreen.jsx`**

Shows:
- Profile avatar
- Name, email/phone, DOB (if available)
- Location, gender (if available)
- "Edit Profile" button (stub)
- **DEV Options:** Reset Demo State button

### 7. Desktop Scrolling Fix
- Fixed `lg:overflow-hidden` → `lg:overflow-auto` in App.js
- Scrolling now works on desktop

---

## Files Changed

### New Files
- `/app/frontend/src/components/screens/simplified/ProfileScreen.jsx`
- `/app/frontend/src/components/screens/simplified/ExpertProfileScreen.jsx`

### Modified Files
- `/app/frontend/src/App.js` - Fixed desktop scrolling
- `/app/frontend/src/components/screens/simplified/SimplifiedApp.jsx` - DEV toggle, navigation
- `/app/frontend/src/components/screens/simplified/BottomNav.jsx` - Added Profile tab
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx` - Rotating placeholders, Ask Mira below topics
- `/app/frontend/src/components/screens/simplified/ExpertsScreen.jsx` - Expert profile navigation, search
- `/app/frontend/src/components/screens/simplified/PlanDashboard.jsx` - Demo mode support
- `/app/frontend/src/components/screens/simplified/utils.js` - flow_version: simplified_v2
- `/app/frontend/src/components/screens/simplified/index.js` - New exports

---

## Telemetry Events (≤12)

All events include `flow_version: "simplified_v2"`

| Event | When |
|-------|------|
| `splash_viewed` | App loads, includes dev_mode |
| `home_viewed` | Home screen loads, variant: new/returning |
| `nav_tab_clicked` | User switches bottom nav tab |
| `mira_input_submitted` | User submits Ask Mira from home |
| `mira_message_sent` | User sends message in Ask Mira |
| `experts_tab_viewed` | User opens Experts tab |
| `expert_profile_viewed` | User opens expert profile |
| `topic_viewed` | User opens topic landing page |
| `tier_selected` | User selects a tier |
| `checkout_started` | User starts checkout |
| `purchase_completed` | Payment successful |
| `dashboard_viewed` | User views plan dashboard |

---

## Testing Guide

### New User Flow
1. Login → Splash → Home
2. DEV toggle shows "New" selected (top-left)
3. Bottom nav has 4 tabs (no My Pack)
4. Topics displayed first
5. Ask Mira section below topics with rotating placeholder
6. Type message → Navigate to Ask Mira tab with message sent
7. Click topic → Topic landing page
8. Select tier → Checkout
9. Complete payment → Plan created
10. DEV toggle auto-switches to "Returning"
11. My Pack tab now visible

### Returning User Flow
1. Click "Returning" in DEV toggle
2. Bottom nav shows My Pack tab
3. Home shows Active Pack card (demo or real)
4. Click "Continue" → Plan dashboard
5. Can start expert threads (real plan) or see demo message

### Experts Tab Flow
1. Click Experts tab
2. Browse all experts with search
3. Filter by modality
4. Click expert card → Expert Profile page
5. See full details, photos, tags
6. Click "Unlock to talk" → Topic landing page
7. (With access) Click "Start Chat" → Thread creation

### Ask Mira Flow
1. From home, type in rotating placeholder input
2. Submit → Opens Ask Mira tab with message sent
3. Or click Ask Mira tab directly
4. Chat with Mira, get topic suggestions

### Profile Flow
1. Click Profile tab
2. View account information
3. Click "Reset Demo State" (DEV) to clear localStorage

---

## Environment Variables

No new environment variables required. Uses existing:
- `REACT_APP_BACKEND_URL` (frontend)
- `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` (backend)

---

## Known Limitations

1. **Profile Edit:** Stub only, not functional
2. **Thread View:** Basic implementation
3. **Call Booking:** UI exists but not functional
4. **Push Notifications:** Not implemented

---

## Next Steps (V3+)

- Full thread chat UI
- Call booking integration
- Push notifications
- Expert-side dashboard
- Analytics dashboard
