# NIRO - AI Astrology Companion

## Original Problem Statement
Build a comprehensive astrology consultation platform with:
- Google OAuth authentication
- Package-based consultations with experts
- Razorpay payment integration
- Kundli/birth chart generation via Vedic API
- AI-powered chat (Mira)
- Admin dashboard for business monitoring with hierarchical content management
- Dynamic homepage that reflects admin changes in real-time
- Live preview of homepage changes before they go live

## User Personas
1. **Seekers** - Users looking for astrological guidance
2. **Paying Customers** - Users who purchase consultation packages
3. **Admins** - Business owners managing catalog and monitoring revenue

---

## Current Redesign Project (Feb 2026)
Major UI/UX redesign based on `niro-final-marquee_1.html` to:
- Adopt new teal/peach/cream color scheme with Lexend font
- Remove phone-frame layout for true responsive design
- Implement new navigation (desktop header + mobile bottom nav)
- Add testimonials marquee, footer, and social links

### Redesign 5-Phase Plan Status:

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Foundation & Theme Swap | ✅ COMPLETE |
| 2 | Navigation Overhaul | ✅ COMPLETE (via Landing Page) |
| 3 | Layout & Grid Transformation | ✅ COMPLETE |
| 4 | Component Refactoring & CTA Mapping | ✅ COMPLETE |
| 5 | Backlog & Polish | 🔲 PENDING |

---

## What's Been Implemented

### Phase 1-5: Core Platform (Previous Sessions)
- Google OAuth, birth details, Kundli, AI chat (Mira)
- Payment flow with Razorpay
- Admin dashboard with hierarchical CRUD
- Dynamic homepage from DB
- Live homepage preview modal

### Phase 6: Admin Dashboard Bug Fixes (Feb 12, 2026)
- Fixed Users/Orders page crashes, deactivation logic, checkout DB lookup, error messages

### Phase 7: Bottom Nav Restructure (Feb 12, 2026)
- New users: Home, Consult, Remedies, Astro (4 tabs)
- Returning users: Home, Consult, Remedies, My Pack, Astro (5 tabs)

### Phase 8: Bulk Upload Flow (Feb 12, 2026)
- POST /api/admin/bulk-upload + template download + admin UI

### Phase 9: P0 Bug Fixes (Feb 16, 2026)
1. Export CSV fix — Authenticated fetch + blob download
2. Checkout back button fix — Preserves/restores previous screen context
3. Expert visibility fix — Public endpoints merge DB + catalog experts

### Phase 10: Expert Tag System & Image Upload (Feb 16, 2026)
1. 3-Type Expert Tag System: life_situation (58), method (10), remedy_support (10)
2. Expert Image Upload: POST /api/admin/upload/image + admin form

### Phase 11: P2 UI Cleanup & Bulk CRUD (Feb 16, 2026)
1. Removed DevToggle (New/Returning/Reset) from homepage
2. Removed "What you'll get" duplicate section from checkout
3. Removed RefundBadge ("No questions asked" & "100% satisfaction") from checkout
4. Bulk CRUD: Multi-select checkboxes + bulk Deactivate/Delete in all admin tables

### Phase 12: Redesign - Foundation & Theme Swap (Feb 18, 2026)
1. **Lexend Font Integration** - Updated index.html and index.css with Lexend as primary font
2. **New CSS Variables** - Created design tokens (--niro-teal, --niro-peach, --niro-cream)
3. **Theme.js Overhaul** - Updated colors, shadows, typography for new design system
4. **Phone Frame Removal** - Removed lg:max-w-md constraint from App.js
5. **Responsive Container** - SimplifiedApp now uses max-w-7xl mx-auto for full-width
6. **LoginScreen Update** - New teal-cream gradient, pill-shaped button, Lexend font
7. **HomeScreen Update** - New hero section with teal gradient, peach CTA button
8. **BottomNav Update** - Added md:hidden for mobile-only display
9. **Responsive Tiles Grid** - 3 cols mobile, 6 cols desktop (grid-cols-3 md:grid-cols-6)

### Phase 13: Public Landing Page & Intent-Based Routing (Feb 18, 2026)
1. **PublicLandingPage.jsx** - New public entry point based on niro-final-marquee_1.html
   - Hero section with teal gradient, trust badges, peach CTA
   - Testimonials marquee with 6 customer reviews
   - "What We Offer" section with 5 feature cards
   - "Life Topics" section with 4 topic cards (Career, Health, Love, Fertility)
   - "How It Works" 4-step section
   - "Our Experts" horizontal scroll with 4 expert cards
   - Footer with logo, disclaimer, social icons (Instagram, X, LinkedIn, YouTube), and links
   - Sticky navigation with backdrop blur
   - Mobile hamburger menu
2. **ScheduleCallScreen.jsx** - Google Calendar booking integration (https://calendar.app.google/cm7fCPK7iHWPXvTY6)
3. **App.js Rewrite** - New routing flow:
   - Entry: PublicLandingPage (public, no auth required)
   - CTAs store intent in localStorage before login redirect
   - After login: Route based on intent + user type
4. **SimplifiedApp.jsx Updates** - Intent-based post-login routing:
   - free_call intent: New user → Birth Details → Schedule | Returning → Schedule
   - consultation:topicId: New user → Birth Details → Home | Returning → Home or MyPack
5. **Intent Storage System** - setUserIntent(), getUserIntent(), clearUserIntent() helpers

### Phase 14: Layout & Grid Transformation (Dec 2025)
1. **ResponsiveHeader.jsx** - New reusable header component for authenticated screens
   - Desktop navigation with Life topics, Experts, Remedies, Astro links
   - Mobile hamburger menu with same navigation items
   - CTA button "Get a Free 10 mins consultation" with phone icon
   - Profile button (desktop only)
   - Back button support for sub-pages
   - Sticky header with backdrop blur (md:sticky)
   - Max-width container (max-w-7xl)
   - All data-testid attributes for testing
2. **HomeScreen.jsx Updates** - V11 responsive layout
   - ResponsiveHeader integration
   - 3-column category grid on desktop (lg:grid-cols-3)
   - Stacked categories on mobile
   - Enhanced hero section with responsive typography
   - Floating decorative shapes on desktop
   - Mobile profile button in hero (md:hidden)
3. **ExpertsScreen.jsx Updates** - Responsive grid layout
   - ResponsiveHeader integration
   - 2-3 column expert cards grid (md:grid-cols-2 lg:grid-cols-3)
   - Centered max-w-6xl container
   - Responsive search and filters
4. **TopicLandingPage.jsx Updates** - Responsive layout
   - ResponsiveHeader with back button
   - Centered max-w-4xl container
   - 3-column outcomes grid on desktop
   - 2-column FAQs grid on desktop
   - Responsive typography throughout
5. **CheckoutScreen.jsx Updates** - Responsive layout
   - ResponsiveHeader with back button
   - Centered max-w-2xl container
   - Responsive typography and spacing

### Phase 15: Component Refactoring (Dec 2025)
1. **TileCard V2** - Refined tile component
   - Responsive sizing (w-28 md:w-32, h-24 md:h-28)
   - Hover effects (hover:shadow-lg hover:-translate-y-0.5)
   - Active scale animation (active:scale-[0.97])
   - Teal icon wrapper with cream background
   - 2-line title with ellipsis support
2. **ExpertProfileScreen V3** - Redesigned with new theme
   - ResponsiveHeader integration with back button
   - Teal gradient hero section
   - Centered photo with border overlay
   - Stats card with teal accent
   - Sticky CTA respects hasBottomNav
   - max-w-2xl centered container
3. **RemediesScreen V2** - Responsive layout update
   - ResponsiveHeader integration
   - 3-column grid on desktop (lg:grid-cols-3)
   - Teal theme for category pills and accents
   - Trust section with 3-column layout on desktop
   - max-w-6xl centered container
4. **MyPackScreen V2** - Responsive layout update
   - ResponsiveHeader integration
   - Active pack card with teal gradient
   - 2x2 deliverables grid
   - Responsive Quick Actions grid
   - Suggested Remedies carousel
   - max-w-4xl centered container
5. **ResponsiveHeader Logo Update** - Larger logo
   - Logo size: text-3xl md:text-4xl (up from text-2xl md:text-3xl)
   - Lexend font family maintained

### Phase 16: React Router Migration & Polish (Dec 2025)
1. **React Router v7 Migration** - Replaced state-machine navigation with URL-based routing
   - `/app/frontend/src/App.js` - BrowserRouter wrapper with AppRoutes
   - `/app/frontend/src/router/AppRoutes.jsx` - Public routes (/, /login, /auth/callback) and protected routes (/app/*)
   - `/app/frontend/src/router/AppLayout.jsx` - Authenticated layout with nested routes
   - Routes: /app, /app/topic/:topicId, /app/package/:packageId, /app/checkout, /app/plan/:planId, /app/mypack, /app/experts, /app/expert/:expertId, /app/mira, /app/profile, /app/astro, /app/remedies, /app/schedule, /app/categories
   - Protected route redirect: /app/* → /login for unauthenticated users
   - Browser back/forward navigation working
   - Deep-linking enabled
2. **Topics Search/Filter** - Search functionality for life topics on HomeScreen
   - Search input with icon and clear button
   - Real-time filtering of categories and tiles
   - Results count display
   - data-testid attributes for testing
3. **Scroll Reveal Animations** - IntersectionObserver-based animations
   - `/app/frontend/src/hooks/useScrollReveal.js` - Custom hook and ScrollReveal component
   - CSS animations: fadeInUp, fadeInLeft, fadeInRight, scaleIn
   - Staggered delays for category cards
   - Smooth transition effects

### Phase 17: Public Access & Navigation (Feb 2026)
1. **Public Experts Page** - /experts route accessible without login
   - PublicExpertsPage.jsx - Lists all 31 experts with search and filters
   - Fixed API endpoint to /api/simplified/experts/all
   - Back button navigates to home (/)
   - CTA button links to /login for unauthenticated users
   - Responsive grid layout with expert cards, photos, ratings
2. **Public Expert Profile Page** - /experts/:expertId route
   - PublicExpertProfilePage.jsx - Shows individual expert details
   - CTA to book consultation (redirects to login)
   - Responsive layout with stats and info sections
3. **Public Life Topics Page** - /topics route accessible without login
   - PublicTopicsPage.jsx - Shows all 22 life topic tiles across 4 categories
   - Includes new "Fertility & Family Planning" category with "Coming Soon" badge
   - Topics: Fertility Support, Baby Naming & Muhurat, Delivery Muhurat, Teenagers Mental Health
   - Search functionality for filtering topics
   - Back button navigates to home
4. **Landing Page Navigation Updates**
   - "See More Life Topics" button now navigates to /topics (no login required)
   - "View Profile" buttons navigate to /experts (no login required)
   - "View all certified experts" card navigates to /experts
5. **ResponsiveHeader Home Link** - Added "Home" nav item for logged-in users
   - NAV_ITEMS includes { id: 'home', label: 'Home', href: '/' }
   - Provides seamless navigation back to public landing page

### Phase 18: Landing Pages Redesign (Feb 2026)
1. **TopicLandingPage V7 Redesign** - Complete UI overhaul
   - ResponsiveHeader integration with back button and "📞 Get a free 10 mins consultation" CTA
   - Cream background (#FBF8F3) with white card sections (#FFFFFF)
   - Pill-shaped tier selector tabs (Focussed, Supported, Comprehensive) with "Recommended" badge
   - Tier summary card with 2x2 grid: Duration, Consultation, Follow-ups, Chat (with teal icons)
   - Outcomes section in 3-column grid: Clarity, Timeline, Support
   - "How will your journey unfold" section with numbered steps
   - Expert widget carousel with profile cards
   - "Why Niro?" trust section with checkmark bullets
   - Expandable FAQ section in 2-column grid
   - Sticky CTA bar with peach "Start my journey" button and price
2. **PackageLandingPage V2 Redesign** - Complete UI overhaul
   - ResponsiveHeader integration
   - Centered max-width container (max-w-3xl)
   - Trust badges with pill-shaped design
   - Package overview card with price and "What's included" grid
   - Expandable help sections and analysis sections
   - Deliverables section with peach-colored checkmarks
   - Trust & Privacy note section
   - Sticky CTA bar with peach "Start my journey" button

### Phase 19: Public Access & Navigation Improvements (Feb 2026)
1. **PublicNavHeader Component** - Shared navigation for all public pages
   - Life Topics, Experts, Remedies navigation links
   - Active link indicator with teal underline
   - CTA button: "📞 Get a free 10 mins consultation"
   - Mobile-responsive navigation bar
2. **Public Topic Landing Page** - Browse topics without login
   - /topic/:topicId route accessible without authentication
   - Full topic content: tier selector, pricing, outcomes, FAQs
   - "Start my journey" redirects to /login only when clicked (not on page load)
   - Login -> Birth details -> Checkout flow preserved
3. **Sticky CTA Bar Fix** - Fixed disappearing on fast scroll
   - Changed from CSS transform to opacity/visibility
   - Added requestAnimationFrame for smooth scroll handling
   - Passive scroll listener for performance
4. **Homepage Navigation Updates**
   - Nav links now point to /topics, /experts, /app/remedies
   - Mobile menu updated with same links
   - CTA button text updated: "📞 Get a free 10 mins consultation"

---

## Technical Architecture

### Key Files (Updated for Redesign)
- `/app/frontend/src/index.css` - CSS variables, Lexend font, scroll reveal animations
- `/app/frontend/src/App.js` - Main app with BrowserRouter and React Router v7
- `/app/frontend/src/router/AppRoutes.jsx` - Route definitions (public + protected)
- `/app/frontend/src/router/AppLayout.jsx` - Authenticated app layout with nested routes
- `/app/frontend/src/hooks/useScrollReveal.js` - IntersectionObserver scroll animation hook
- `/app/frontend/src/components/screens/simplified/theme.js` - V10 design tokens
- `/app/frontend/src/components/screens/simplified/ResponsiveHeader.jsx` - V11 reusable desktop header (text-3xl md:text-4xl logo)
- `/app/frontend/src/components/screens/simplified/TileCard.jsx` - V2 responsive tiles with hover effects
- `/app/frontend/src/components/screens/simplified/HomeScreen.jsx` - V11 hero + responsive 3-col grid + search/filter
- `/app/frontend/src/components/screens/simplified/ExpertsScreen.jsx` - V2 responsive 3-col grid
- `/app/frontend/src/components/screens/simplified/ExpertProfileScreen.jsx` - V3 with ResponsiveHeader
- `/app/frontend/src/components/screens/simplified/RemediesScreen.jsx` - V2 with ResponsiveHeader and 3-col grid
- `/app/frontend/src/components/screens/simplified/MyPackScreen.jsx` - V2 with ResponsiveHeader
- `/app/frontend/src/components/screens/simplified/TopicLandingPage.jsx` - Responsive centered layout
- `/app/frontend/src/components/screens/simplified/CheckoutScreen.jsx` - V2 responsive centered layout
- `/app/frontend/src/components/screens/simplified/SimplifiedApp.jsx` - Phone frame removed, onTabChange prop passing
- `/app/frontend/src/components/screens/simplified/BottomNav.jsx` - Mobile-only (md:hidden)
- `/app/frontend/src/components/screens/LoginScreen.jsx` - New login design
- `/app/frontend/src/App.js` - Removed phone frame wrapper

### Database Collections
- admin_categories, admin_tiles, admin_topics, admin_experts, admin_remedies, admin_tiers, admin_sessions

---

## Credentials
- **Admin Dashboard:** NiroAdmin / NewAdmin@123

---

## Prioritized Backlog

### Phase 1: Public Access & Navigation ✅ COMPLETE (Feb 2026)
- [x] Public /experts route - browse experts without login
- [x] Public /experts/:expertId route - view expert profile without login
- [x] Public /topics route - browse life topics without login
- [x] "Fertility & Family Planning" category with Coming Soon badge
- [x] Landing page navigation to public pages (no login required)
- [x] "Home" nav link in ResponsiveHeader for logged-in users
- [x] Fixed API endpoint for experts (/api/simplified/experts/all)

### Phase 2: Life Topics & Package Landing Pages Redesign ✅ COMPLETE (Feb 2026)
- [x] TopicLandingPage V7 redesign with cream/white card design
- [x] PackageLandingPage V2 redesign with ResponsiveHeader
- [x] Pill-shaped tier selector tabs
- [x] Sticky CTA bar with peach "Start my journey" button
- [x] Outcomes section in 3-column grid

### Phase 3 & 4: Public Navigation & Bug Fixes ✅ COMPLETE (Feb 2026)
- [x] Fixed sticky CTA bar disappearing on fast scroll
- [x] PublicNavHeader component with Life Topics, Experts, Remedies links
- [x] Public topic landing page (/topic/:topicId) - browse without login
- [x] Login only required before checkout (not on topic browse)
- [x] Homepage nav updated with proper links to /topics, /experts
- [x] Mobile menu updated with same links

### Phase 5: UI/UX Polish (P1 - NEXT)
- [ ] Redesign Birth details screen
- [ ] Audit all authenticated screens for profile icon visibility
- [ ] Site-wide check for consistent back buttons
- [ ] Add YouTube, Facebook, X links to footer

### Future Phase: UI Changes (P2)
- [ ] Change free call CTA text to: "Get a Free 10 mins consultation 📞"
- [ ] Update top-right nav button to same text and follow same path as hero CTA
- [ ] Increase Niro logo size further if needed

### P3 - Tile Sizing (deferred by user)
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
- `/app/test_reports/iteration_14.json` - Phase 9 P0 bug fixes (9/9 pass)
- `/app/test_reports/iteration_15.json` - Phase 10 Tags & Upload (15/15 pass)
- `/app/test_reports/iteration_16.json` - Phase 11 UI Cleanup & Bulk CRUD (100% frontend pass)
- `/app/test_reports/iteration_17.json` - Phase 12 Foundation & Theme Swap (100% pass, 13/13 features)
- `/app/test_reports/iteration_18.json` - Phase 13 Public Landing Page & Intent Routing (100% pass, 20/20 features)
- `/app/test_reports/iteration_19.json` - Phase 14 Layout & Grid Transformation (100% pass, 11/11 features)
- `/app/test_reports/iteration_20.json` - Phase 15 Component Refactoring (100% pass, 13/13 features)
- `/app/test_reports/iteration_21.json` - Phase 1 Navigation & Back Buttons (100% pass after CSS fix)
- `/app/test_reports/iteration_22.json` - Phase 2 CTAs & Conversion (100% pass, 17/17 tests)
- `/app/test_reports/iteration_23.json` - Phase 3 Polish & Advanced (100% pass, 7/7 tests)
- `/app/test_reports/iteration_24.json` - Phase 17 Public Access & Navigation (100% pass, 9/9 tests)
- `/app/test_reports/iteration_25.json` - Phase 18 Landing Pages Redesign (100% pass, code review + live tests)
- `/app/test_reports/iteration_26.json` - Phase 19 Public Access & Nav Improvements (100% pass)
