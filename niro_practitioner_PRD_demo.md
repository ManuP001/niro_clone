# Niro Practitioner Platform — PRD (Demo Build)
**Version:** 3.2-DEMO | **Date:** March 2026 | **URL:** `pro.getniro.ai`  
**Build Mode:** DEMO — Clone repository. No database. No real payments. No real video. All UI clickable with mock data.

---

## 0. Demo Build Rules

This is a **demo/prototype build** on a clone repository. These rules override everything else:

```
✅ Build all UI exactly as specced
✅ All navigation and routing must work
✅ All forms must be interactive (typeable, selectable, validatable)
✅ All buttons must respond and transition to the next state
✅ Use localStorage for any form state that needs to persist across screens
✅ Use mock data (defined in lib/mock-data.ts) for all lists, leads, sessions, earnings
❌ No Supabase — no database calls of any kind
❌ No Razorpay — no payment processing (simulate with a 1.5s delay + success state)
❌ No Daily.co — replace with a simulated video UI
❌ No Claude API — replace text cleanup with a simulated 1s delay + fake diff
❌ No email/WhatsApp sending — show the message in a copy-ready panel
❌ No auth middleware — use a simple mock session in localStorage
❌ No backend API routes — all data comes from lib/mock-data.ts
```

---

## 1. Project Overview

### 1.1 Goal
Build a fully clickable demo of `pro.getniro.ai` — the practitioner dashboard for Niro Astrology. Every screen must be navigable, every form fillable, every button functional. No real integrations — simulate all async operations with realistic delays and success states.

### 1.2 Tech Stack
```
Framework:    Next.js 14 (App Router), TypeScript, Tailwind CSS
State:        React useState + localStorage (no external state library needed)
Mock Data:    lib/mock-data.ts (single source of truth for all demo data)
Forms:        react-hook-form + zod
Icons:        lucide-react
Deployment:   Vercel (optional — runs locally with npm run dev)
```

### 1.3 No Environment Variables Needed
This demo build requires no .env file. All data is mocked.

---

## 2. Mock Data (replaces database)

Create `lib/mock-data.ts` as the single source of all data in the demo.

```typescript
// lib/mock-data.ts

export const MOCK_PRACTITIONER = {
  id: "prac_001",
  full_name: "Kavita Sharma",
  primary_tradition: "Vedic Astrology",
  languages: ["Hindi", "English"],
  years_of_practice: 12,
  credential_education: "Jyotish Visharad, Bharatiya Vidya Bhavan, 2012",
  city: "Mumbai",
  philosophy: "I believe astrology is not about predictions — it is about patterns that help us make more conscious choices. My work focuses on timing: when to act, when to wait, and how to align your decisions with the larger rhythms of your life.",
  short_bio: "Vedic astrologer with 12 years of practice, specialising in career transitions and relationship timing. Based in Mumbai.",
  primary_topic: "career",
  secondary_topics: ["romantic_relationships", "money"],
  typical_availability: "Weekday evenings 7–10pm, Weekend mornings",
  max_sessions_per_week: 8,
  status: "approved",
  conversion_rate: 28,
  total_revenue_inr: 12500,
  average_rating: 4.8,
  total_sessions: 12,
  photo_url: null, // will use avatar placeholder
};

export const MOCK_PACKAGES = [
  {
    id: "pkg_001",
    name: "Intro Clarity Call",
    who_its_for: "Someone exploring astrology for the first time",
    topic: "career",
    outcomes: ["A clear answer to your most pressing question", "One key timing window for the next 90 days", "A simple next step you can take immediately"],
    duration_days: 15,
    sessions_included: 1,
    price_inr: 499,
    is_intro_template: true,
  },
  {
    id: "pkg_002",
    name: "Career Clarity Session",
    who_its_for: "People facing job change or career transition decisions",
    topic: "career",
    outcomes: ["A written chart summary for your career zone", "Timing windows for the next 3 months", "A 2-step action plan aligned with your chart"],
    duration_days: 30,
    sessions_included: 1,
    price_inr: 1500,
    is_intro_template: false,
  },
  {
    id: "pkg_003",
    name: "Relationship Clarity Package",
    who_its_for: "People navigating relationship decisions or marriage timing",
    topic: "romantic_relationships",
    outcomes: ["Compatibility insights from your Navamsa chart", "Current Venus and 7th house transit analysis", "Timing guidance for next 60 days"],
    duration_days: 30,
    sessions_included: 2,
    price_inr: 2500,
    is_intro_template: false,
  },
];

export const MOCK_LEADS = [
  {
    id: "lead_001",
    client_name: "Priya",
    life_area: "career",
    question: "Should I quit my job and start my own business this year? I've been at my current company for 6 years and feel stuck.",
    niro_ai_context: "Client is weighing a major career shift. High urgency — has a business idea ready. Open to timing guidance.",
    chart: {
      ascendant: "Virgo",
      moon_sign: "Taurus",
      current_mahadasha: "Jupiter",
      mahadasha_end: "2034",
    },
    top_transits: [
      "Saturn transiting 6th house — pressure on work environment",
      "Jupiter aspects 10th house — favourable for career moves",
    ],
    focus_factors: [
      { rule: "MAHADASHA_JUPITER", summary: "Expansion period — favourable for new ventures" }
    ],
    flat_fee_inr: 99,
    expires_in_seconds: 847, // ~14 minutes
    status: "pending",
  },
  {
    id: "lead_002",
    client_name: "Rahul",
    life_area: "money",
    question: "I want to invest in a new business partnership. Will this be financially good for me in the next year?",
    niro_ai_context: "Client is evaluating a significant financial commitment with a business partner. Needs timing clarity.",
    chart: null, // no birth details provided
    top_transits: [],
    focus_factors: [],
    flat_fee_inr: 99,
    expires_in_seconds: 492, // ~8 minutes
    status: "pending",
  },
];

export const MOCK_SESSIONS = [
  {
    id: "sess_001",
    lead_id: "lead_001",
    client_name: "Priya",
    life_area: "career",
    question: "Should I quit my job and start my own business this year?",
    niro_ai_context: "Client is weighing a major career shift. High urgency.",
    chart: MOCK_LEADS[0].chart,
    top_transits: MOCK_LEADS[0].top_transits,
    focus_factors: MOCK_LEADS[0].focus_factors,
    status: "scheduled",
  },
];

export const MOCK_EARNINGS = [
  { date: "Mar 8, 2026", client: "Priya", package: "Career Clarity Session", gross_inr: 1500, fee_inr: 99, net_inr: 1401 },
  { date: "Mar 6, 2026", client: "Amit", package: "Intro Clarity Call", gross_inr: 499, fee_inr: 99, net_inr: 400 },
  { date: "Mar 4, 2026", client: "Sunita", package: "Career Clarity Session", gross_inr: 1500, fee_inr: 99, net_inr: 1401 },
  { date: "Mar 1, 2026", client: "Ravi", package: "Relationship Clarity Package", gross_inr: 2500, fee_inr: 99, net_inr: 2401 },
  { date: "Feb 28, 2026", client: "Meera", package: "Intro Clarity Call", gross_inr: 499, fee_inr: 99, net_inr: 400 },
];

export const SESSION_CARDS = {
  vedic_astrology: {
    phase01: {
      title: "Open + Past Observation",
      guide: "Speak in feelings and archetypes — never signs, degrees, or house numbers.",
      opening: '"You carry a strong sense of purpose — built to lead. That same drive can make you feel isolated at times."',
      past_obs: '"A big commitment in your late 20s came apart. That wasn\'t failure — your chart was clearing the path."',
    },
    phase02: {
      title: "Answer Their Question",
      guide: "Read their question back verbatim. Give a resonant answer. End with a resonance check.",
      script: '"What your chart shows is a period of internal restructuring. The ground is ready — the challenge is clarity on what you\'re moving toward."',
      resonance_check: '"Does that resonate?" or "Does that feel true?"',
    },
    phase03: {
      title: "Invite Deeper — No Pressure",
      guide: "Name ONE thread you couldn't explore. Offer your package once — as a door, not a close.",
      script: '"There\'s a pattern in your chart around [this area] I couldn\'t get to. A 30-minute session would let us map the full picture. No rush — but there\'s a lot more here for you."',
      never: "Never say 'Would you like to book?' — offer, don't sell.",
    },
  },
  numerology: {
    phase01: {
      title: "Open + Past Observation",
      guide: "Speak in life themes and numbers — never say 'your life path number is X' first.",
      opening: '"There is a 5 at the heart of your chart — restless, freedom-seeking. You thrive in motion and suffocate when trapped."',
      past_obs: '"There was a period of deep questioning where you had to rediscover yourself outside of others."',
    },
    phase02: {
      title: "Answer Their Question",
      guide: "Use personal year cycle to give a direct, actionable answer.",
      script: '"You are in a 1 Personal Year — the start of a new nine-year cycle. Numerologically, one of the best windows in nearly a decade to begin something new."',
      resonance_check: '"Does that feel true?"',
    },
    phase03: {
      title: "Invite Deeper — No Pressure",
      guide: "Name a specific gap in what was covered.",
      script: '"Your core numbers reveal something about the gap between how you show up publicly and who you are privately. A full session takes us through your complete profile."',
      never: "Don't give away the full reading in 5 minutes — leave them curious.",
    },
  },
  tarot: {
    phase01: {
      title: "Open + Past Observation",
      guide: "Speak in energy and themes — never name a card or number.",
      opening: '"The energy around you is one of transition. Something is ending so something more aligned can begin."',
      past_obs: '"The cards reflect you\'ve already been through the hardest part of what you are asking about."',
    },
    phase02: {
      title: "Answer Their Question",
      guide: "Speak to the emotional truth first, then the practical guidance.",
      script: '"The energy I see is readiness mixed with fear — and that fear is not a stop sign. It is your nervous system catching up with a decision part of you has already made."',
      resonance_check: '"Does that land?"',
    },
    phase03: {
      title: "Invite Deeper — No Pressure",
      guide: "Point to one unexplored thread that genuinely needs more time.",
      script: '"There was a second layer I kept seeing — around what you truly want versus what you\'ve been told you should want. A longer reading gives us the space to really sit with what\'s coming up."',
      never: "Don't offer the package multiple times — once, as a door.",
    },
  },
  kp_astrology: {
    phase01: {
      title: "Open + Past Observation",
      guide: "Use KP principles but speak in plain language — never mention cuspal sub lords.",
      opening: '"Your chart shows a person who thinks deeply before acting — which means when you do move, you move with precision."',
      past_obs: '"Around 3–4 years ago there was a significant shift in your professional environment — something you didn\'t fully choose but had to navigate."',
    },
    phase02: {
      title: "Answer Their Question",
      guide: "Give a clear directional answer using sublord principles without the jargon.",
      script: '"The indicators I\'m seeing point toward a window of clarity opening in the next 4–6 months. The question is what you do with it now to prepare."',
      resonance_check: '"Does that align with what you\'ve been sensing?"',
    },
    phase03: {
      title: "Invite Deeper — No Pressure",
      guide: "Offer to go deeper on timing — KP's strength.",
      script: '"KP astrology is particularly strong on timing — month and week level precision. A full session would let me map the exact windows for your specific question."',
      never: "Don't give specific dates in the 5-min session — save that for the paid reading.",
    },
  },
  vastu: {
    phase01: {
      title: "Open + Space Observation",
      guide: "Connect to how their space might be affecting the life area they're asking about.",
      opening: '"The direction your main entrance faces has a direct relationship with the kind of energy that flows into your career and finances."',
      past_obs: '"Many of the challenges you\'ve faced in [life area] often have a spatial dimension that goes unaddressed."',
    },
    phase02: {
      title: "Answer Their Question",
      guide: "Give one specific vastu insight that directly addresses their question.",
      script: '"Based on what you\'ve described, the northwest zone of your home or workspace is where I\'d focus first. That\'s the direction associated with movement and new opportunities."',
      resonance_check: '"Does that direction feel significant in your space?"',
    },
    phase03: {
      title: "Invite Deeper — No Pressure",
      guide: "Offer a proper vastu audit as the next step.",
      script: '"A proper vastu consultation involves looking at all 8 directions in relation to your specific question. I\'d love to do a proper assessment — it usually takes 60–90 minutes and gives you a clear action list."',
      never: "Don't promise dramatic results — speak to the process and what you'll uncover.",
    },
  },
};

export const TOPICS = [
  { value: "career", label: "Career" },
  { value: "romantic_relationships", label: "Relationships" },
  { value: "marriage_partnership", label: "Marriage" },
  { value: "money", label: "Money" },
  { value: "health_energy", label: "Health" },
  { value: "family_home", label: "Family" },
  { value: "spirituality", label: "Spiritual" },
  { value: "self_psychology", label: "Personal Growth" },
  { value: "friends_social", label: "Social" },
  { value: "learning_education", label: "Learning" },
  { value: "travel_relocation", label: "Travel" },
  { value: "legal_contracts", label: "Legal" },
  { value: "daily_guidance", label: "Daily Guidance" },
  { value: "general", label: "General" },
];

export const TRADITIONS = [
  "Vedic Astrology", "KP Astrology", "Numerology", "Tarot", "Vastu", "Palmistry", "Other"
];

export const LANGUAGES = [
  "Hindi", "English", "Tamil", "Telugu", "Marathi", "Bengali", "Kannada", "Other"
];
```

---

## 3. Page & Route Structure

```
pro.getniro.ai/ (or localhost:3000/)
├── /                         → redirect to /dashboard
├── /onboarding
│   ├── /welcome              → Step 0: Welcome
│   ├── /identity             → Step 1: Basic info
│   ├── /story                → Step 2: Philosophy + bio
│   ├── /specializations      → Step 3: Topics + availability
│   ├── /packages             → Step 4: Package builder
│   ├── /photos               → Step 5: Photo upload
│   └── /preview              → Step 6: Preview + submit
│
├── /dashboard                → Home: KPIs + leads + milestones
├── /leads
│   ├── /                     → Pending leads list
│   └── /[id]                 → Lead detail + accept/decline
│
├── /session/[id]
│   ├── /prep                 → Pre-session brief
│   └── /cockpit              → Live 5-min session cockpit
│
├── /packages
│   ├── /                     → List packages
│   ├── /new                  → Create package
│   └── /[id]/edit            → Edit package
│
├── /earnings                 → Earnings history
└── /settings                 → Profile edit
```

**No auth required** — all pages accessible directly for demo purposes. No login screen.

---

## 4. Simulated Async Behaviour

Replace all real API calls with these simulation helpers in `lib/simulate.ts`:

```typescript
// lib/simulate.ts

// Simulates a network delay with a success result
export async function simulateSuccess<T>(data: T, delayMs = 1200): Promise<T> {
  await new Promise(resolve => setTimeout(resolve, delayMs));
  return data;
}

// Simulates a payment flow: loading → processing → success
export async function simulatePayment(onStep: (step: string) => void): Promise<void> {
  onStep("Initiating payment...");
  await new Promise(r => setTimeout(r, 800));
  onStep("Processing ₹99 platform fee...");
  await new Promise(r => setTimeout(r, 1200));
  onStep("Payment confirmed ✓");
  await new Promise(r => setTimeout(r, 600));
}

// Simulates text cleanup: returns the input with a fake "correction" added
export async function simulateTextCleanup(text: string): Promise<{
  corrected: string;
  changes_made: boolean;
  changes: string[];
}> {
  await new Promise(r => setTimeout(r, 1000));
  // Make one tiny fake correction to show the feature working
  const corrected = text.replace("  ", " ").trim();
  return {
    corrected,
    changes_made: corrected !== text,
    changes: corrected !== text ? ["Removed extra whitespace"] : [],
  };
}

// Simulates offer being sent: shows WhatsApp template
export async function simulateOfferSend(offerDetails: {
  clientName: string;
  packageName: string;
  price: number;
  expiryHours: number;
}): Promise<{ whatsapp_template: string }> {
  await new Promise(r => setTimeout(r, 1000));
  return {
    whatsapp_template: `${offerDetails.clientName}, it was wonderful speaking with you today 🙏\n\nI've put together a special offer based on our conversation:\n\n✨ ${offerDetails.packageName}\n₹${offerDetails.price}\n\nThis offer is valid for ${offerDetails.expiryHours} hours.\nTo book: [Payment link]\n\nLooking forward to continuing this journey with you 🌙`,
  };
}
```

---

## 5. Module A — Onboarding

### Entry Point
For demo: `/onboarding/welcome` is the entry. No token validation needed.  
Show practitioner name as "Kavita" (hardcoded for demo — editable in first form field).

### Progress Bar
Persistent across all 6 steps. Steps: Welcome (0%) → Identity (20%) → Story (40%) → Specializations (60%) → Packages (80%) → Photos (90%) → Preview (100%).

### localStorage Keys
```
niro_onboarding_identity      → IdentityForm data
niro_onboarding_story         → StoryForm data
niro_onboarding_specializations → SpecializationsForm data
niro_onboarding_packages      → Package[] data
niro_onboarding_photos        → string[] (base64 previews)
```
All screens restore from localStorage on mount. Clear all keys after "submit" on preview screen.

### Screen 1 — Identity
Fields: full_name, primary_tradition (dropdown from TRADITIONS), languages (multi-checkbox from LANGUAGES), years_of_practice (number), credential_education (optional text), city (free text).  
Pre-fill with MOCK_PRACTITIONER values so demo shows real content immediately.

### Screen 2 — Story
Fields: philosophy (80–200 words, live counter), short_bio (50–300 chars, live counter).  
Pre-fill from MOCK_PRACTITIONER.

### Screen 3 — Specializations
Fields: primary_topic (single select from TOPICS), secondary_topics (multi-select, max 3), typical_availability (text), max_sessions_per_week (number 1–20).  
Pre-fill from MOCK_PRACTITIONER.

### Screen 4 — Package Builder
Min 1, max 4 packages. Show "Add Intro Session ₹499" template button if no package under ₹1,000.  
Pre-fill with MOCK_PACKAGES.  
Reference guide in collapsible sidebar (always show on desktop).

### Screen 5 — Photos
Accept image files. Preview as circles. No upload to server — store as base64 in localStorage.  
Show a placeholder avatar if no photo provided.

### Screen 6 — Preview + Submit
Render public profile card from localStorage data.  
On "Submit":
1. Call `simulateTextCleanup(philosophy)` — show 1s spinner
2. If changes_made: show diff panel (highlight changed text in yellow) with Accept/Keep Original
3. Show: "🎉 Profile submitted! Manu will review within 48 hours." (static success screen)
4. Clear localStorage
5. Show "Go to Dashboard →" button → `/dashboard`

---

## 6. Module B — Lead Management

### Lead List (`/leads`)
Show MOCK_LEADS as cards. Each card: life area badge (coloured), question preview (first 10 words + "..."), live countdown timer.  
Empty state: "No pending leads right now — we're finding the right clients for you 🔍"

### Lead Detail (`/leads/[id]`)
Pull lead from MOCK_LEADS by id.  
Show full layout from Section 6 of original PRD.

**Countdown Timer:** Start from `lead.expires_in_seconds` on mount. Update every second. Colour: green > 300s, amber 60–300s, red < 60s. At 0: replace page with "This lead has expired — no charge applied."

**Accept button:**
1. Show simulatePayment() steps inline (replace button with loading state showing each step)
2. On complete: toast "Lead accepted ✓" then navigate to `/session/[id]/prep`

**Decline button:** Confirm dialog → toast "Lead passed — no charge applied" → back to `/leads`

---

## 7. Module C — Session Cockpit

### Pre-Session Brief (`/session/[id]/prep`)
Pull data from MOCK_SESSIONS (or MOCK_LEADS) by id.  
Show all fields: client name, question (large), Niro AI context, chart snapshot (show "Birth details not provided" if chart is null), packages list with intro first.  
60-second countdown timer before button fully activates (but always clickable).  
"I'm Ready — Join Call →" → `/session/[id]/cockpit`

### Session Cockpit (`/session/[id]/cockpit`)

**Timer (CountdownTimer component):**  
- Props: startMinutes=5
- States: green > 1:30, amber 1:30–0:30, red < 0:30
- At 1:00: add a pulsing dot on Phase 02 tab
- At 3:30: add a pulsing dot on Phase 03 tab
- At 0:30: slide in the offer panel
- At 0:00: show "Time's up — your offer panel is ready" (do NOT navigate away)

**Simulated Video Call (NO Daily.co):**
```
Replace the video call with a simulated UI:
- Two rounded rectangles (16:9 ratio)
- Large one: "Priya" label, subtle pulse animation, grey gradient background
- Small one (bottom-right overlay): "You" label, same styling
- Mute button (clicking toggles a muted icon — no real audio)
- Camera button (clicking toggles a camera-off state)
- "Waiting for Priya to join..." text (shown for 3 seconds on mount, then changes to the active state)
```

**Left Panel (Client Brief):**  
Pull from MOCK_SESSIONS[0]. Verbatim question in 18px+ text. Chart snapshot if available.  
Private notes: textarea, saves to localStorage `niro_session_notes_[id]` on every keystroke.

**Right Panel (Session Card):**  
Pull tradition from MOCK_PRACTITIONER.primary_tradition. Map to SESSION_CARDS[tradition_key].  
3 tabs: Phase 01 / 02 / 03. Never/Always rules below tabs (always visible, not collapsible on desktop).

**Post-Call Offer Panel (slides in at 0:30):**
- Radio select: show MOCK_PACKAGES, intro package first with "Recommended" badge
- Custom offer toggle: price field + description + expiry (24h/48h/72h)
- Personal message (optional textarea)
- [Preview Offer] button: shows offer card preview inline
- [Send Offer] button:
  1. Call `simulateOfferSend()` — 1s delay
  2. Show WhatsApp template in a copy-ready panel with [Copy to WhatsApp] button (copies to clipboard)
  3. Show "Offer sent! Now complete your session notes." message

**Post-session debrief form:**  
Appears after offer is sent (or 2 min button in the cockpit).  
One question at a time wizard, 6 questions. On submit: navigate to `/dashboard` with toast "Debrief saved ✓".

---

## 8. Module D — Packages

### Package List (`/packages`)
Show MOCK_PACKAGES as cards. Each card: name, price, duration, sessions, topic tag, Edit button.  
"Add Package" button → `/packages/new`  
Floating banner if no package under ₹1,000: "Add an Intro Session — converts first-time clients better"

### Package Form (`/packages/new` and `/packages/[id]/edit`)
Same fields as onboarding Screen 4. Save to localStorage `niro_packages`. On save: toast "Package saved ✓" → back to `/packages`.  
Delete: confirmation dialog → toast "Package removed" → back to `/packages`.

---

## 9. Module E — Conversion Follow-Up

This module has no dedicated page in the demo. It is surfaced through:
- Dashboard notifications (bell icon, badge count)
- A notification panel that slides in when bell is clicked

### Mock Notifications (in MOCK_DATA or hardcoded in component)
```typescript
export const MOCK_NOTIFICATIONS = [
  {
    id: "notif_001",
    type: "follow_up_prompt",
    message: "Have you followed up with Priya yet? She seemed interested.",
    client_name: "Priya",
    suggested_package: "Intro Clarity Call",
    created_at: "2 hours ago",
    whatsapp_template: "Hi Priya! Just checking in — did you get a chance to look at the offer I sent? Happy to answer any questions 🙏",
  },
];
```
Clicking "Copy message" copies the whatsapp_template to clipboard. Clicking "Mark as done" removes the notification from the panel.

---

## 10. Module G — Earnings & Dashboard

### Dashboard Home (`/dashboard`)
Three KPI cards using MOCK_PRACTITIONER values:
- Conversion Rate: 28%
- Revenue this month: ₹12,500
- Rating: 4.8 ⭐

Pending leads section: pull from MOCK_LEADS with status="pending". Live countdown per lead.

Milestone tracker:
```
✅ Profile complete
✅ First package created
✅ First lead received
⬜ First session completed  ← current
⬜ First paid client
```

Notification bell (top right): badge showing count from MOCK_NOTIFICATIONS.

### Earnings Page (`/earnings`)
Table from MOCK_EARNINGS. Month filter (static — March 2026).  
Total: ₹12,500 | Fees: ₹495 (5 leads × ₹99)  
[Download Statement] button: generates and downloads a CSV of the table data (real browser download using Blob API — no server needed).

---

## 11. Settings Page (`/settings`)

Pre-filled with MOCK_PRACTITIONER data. All fields editable.  
Packages section: shows current packages, links to /packages.  
Photos section: upload area, shows current photos.  
"Save Changes" button: 1s simulate delay → toast "Profile updated ✓". Nothing actually saved to a server.

---

## 12. Design System

```
Primary dark:   #1E1B4B (deep navy/indigo)
Accent purple:  #7C3AED
Accent gold:    #D97706
Success green:  #059669
Warning amber:  #D97706
Error red:      #DC2626
Background:     #F9FAFB
Card bg:        #FFFFFF
Muted text:     #6B7280
Border:         #E5E7EB

Font: Inter (Google Fonts) or system-ui fallback
Rounded corners: rounded-xl for cards, rounded-lg for inputs
Shadows: shadow-sm for cards, shadow-md for modals/panels
```

Life area badge colours:
- career → blue (#DBEAFE / #1D4ED8)
- money → green (#D1FAE5 / #065F46)
- health_energy → red (#FEE2E2 / #991B1B)
- romantic_relationships → pink (#FCE7F3 / #9D174D)
- marriage_partnership → rose (#FFE4E6 / #BE123C)
- spirituality → purple (#EDE9FE / #5B21B6)
- general / other → grey (#F3F4F6 / #374151)

---

## 13. Out of Scope (Demo Build)

Everything below is confirmed CUT for this demo:
- All database / Supabase
- All real payment processing (Razorpay)
- Real video calls (Daily.co)
- Real AI text cleanup (Claude API)
- Real WhatsApp/email sending
- Auth middleware / login
- Studio/multi-practitioner accounts
- CRM (Client Relationship Management)
- Promo codes, countdown offers
- Digital products
- Broadcast messaging
- Badges and gamification
- Advanced analytics
- WhatsApp Business API

---

*PRD Version 3.2-DEMO — March 2026 — Clone repository only*
