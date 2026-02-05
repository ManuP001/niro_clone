# Niro Onboarding UX Research & Recommendations

## Executive Summary

Based on comprehensive research of 10+ astrology apps across India (Astrotalk, Astroyogi, InstaAstro, Bodhi) and the US (Sanctuary, Nebula, Kasamba, Keen, Purple Garden, Co-Star, The Pattern), this document outlines the optimal onboarding flow for Niro's evolved positioning as a **premium, outcome-led life-guidance platform**.

---

## Part 1: Competitive Analysis Summary

### 🇮🇳 India Market Apps

| App | Onboarding Style | Pricing Model | Key Strengths | Key Weaknesses |
|-----|-----------------|---------------|---------------|----------------|
| **Astrotalk** | Quick phone signup → Wallet recharge → Browse astrologers | Per-minute (₹10+/min) | 450K daily users, Uber-style ratings, 13K+ astrologers | Marketplace feel, no outcome focus |
| **Astroyogi** | Optional signup for free content → 5-min free trial | Per-minute (₹10+/min) | 30+ crore users, free Kundli tools, 5K+ experts | Cluttered UI, generic marketplace |
| **InstaAstro** | OTP signup → ₹1 first consultation → Wallet-based | Per-minute with wallet | ₹1 trial hook, simple flow | Fear of meter running |
| **Bodhi** | Birth details → AI horoscopes → Escalate to human | Hybrid (free AI + paid human) | AI-first engagement, trusted entry | Less premium positioning |

### 🇺🇸 US Market Apps

| App | Onboarding Style | Pricing Model | Key Strengths | Key Weaknesses |
|-----|-----------------|---------------|---------------|----------------|
| **Sanctuary** | Birth chart setup → Free content → Premium readings | Freemium + $14.99/mo subscription | "Talkspace for astrology" positioning, human experts | iOS-focused, limited scale |
| **Nebula** | Birth details → Free horoscope → Psychic chat | Per-minute + subscription | Clean UX, 1000+ psychics | Billing complaints, upsell-heavy |
| **Kasamba** | Quick signup → 3 free min × 3 advisors | Per-minute (9 free min total) | Strong trial hook, 3M+ users | Marketplace, not specialists |
| **Keen** | Best Match Quiz → Advisor browse | Per-minute | Quiz-based matching, 24/7 access | Generic advisor pool |
| **Purple Garden** | Video intro previews → Credit-based booking | Credit packages ($30 free first) | Video-first, 91.5% accuracy claim | Credit system confusion |
| **Co-Star** | NASA-powered birth chart → Daily notifications | Free + Premium | Viral social features, Gen Z appeal | AI-only, no human connection |
| **The Pattern** | Birth details → Personality audio → Bonds | Freemium | Deep personalization, compatibility | No consultations |

---

## Part 2: Key Insights & Patterns

### What Works Well (Adopt)

1. **Immediate Value Delivery**
   - Co-Star/The Pattern: Generate birth chart instantly after birth details
   - Bodhi: Free AI horoscopes before asking for payment
   - **Niro Implication**: Deliver a personalized insight within 30 seconds of entering birth details

2. **Low-Friction Trial Experiences**
   - InstaAstro: ₹1 first consultation removes price anxiety
   - Kasamba: 3 free minutes × 3 advisors = 9 min total trial
   - Sanctuary: Free birth chart + content before premium
   - **Niro Implication**: Offer meaningful free value, not just teasers

3. **Expert Discovery UX**
   - Astrotalk: Uber-style ratings + years of experience + reviews
   - Purple Garden: Video intro previews before booking
   - Keen: Quiz-based matching algorithm
   - **Niro Implication**: Match users to specialists based on their situation, not generic browsing

4. **Trust Signals That Convert**
   - Verified expert badges
   - Specific accuracy claims (Purple Garden: 91.5%)
   - Real reviews with specific outcomes
   - **Niro Implication**: Lead with expert vetting and outcome stories

### What Doesn't Work (Avoid)

1. **Per-Minute Billing Anxiety**
   - Nebula: Users report "meter running" stress, spending $50 in <5 minutes
   - Astrotalk/InstaAstro: Wallet model creates uncertainty
   - **Niro Implication**: Package-based pricing removes anxiety, increases trust

2. **Generic Marketplace Feel**
   - Astrotalk: 13K astrologers = paradox of choice
   - Kasamba: "Find an advisor" feels transactional
   - **Niro Implication**: Curated specialists, not an open marketplace

3. **Upsell-Heavy Flows**
   - Nebula: Sneaky subscriptions, cancellation complaints
   - Co-Star: Premium modals interrupt experience
   - **Niro Implication**: Transparent pricing, no hidden upsells

4. **AI-Only Limitations**
   - Co-Star/The Pattern: Popular but no human connection
   - **Niro Implication**: AI for engagement, humans for transformation

---

## Part 3: Recommended Niro Onboarding Flow

### Design Philosophy
Based on Niro's positioning as a **premium, outcome-led platform**, the onboarding should:
- **Qualify intent first** (what life situation, not just demographics)
- **Build trust through curation** (we match you, you don't browse)
- **Demonstrate value before asking for commitment**
- **Package-based pricing** (outcomes, not minutes)

---

### Proposed Screen Flow: 12 Screens

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: IDENTIFY INTENT (3 screens)                           │
├─────────────────────────────────────────────────────────────────┤
│  Screen 1: Welcome + Value Prop                                  │
│  Screen 2: Life Situation Selector                               │
│  Screen 3: Specific Concern Deepdive                             │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2: COLLECT DETAILS (2 screens)                           │
├─────────────────────────────────────────────────────────────────┤
│  Screen 4: Birth Details (with "why this matters")              │
│  Screen 5: Account Creation (Google OAuth)                       │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3: DELIVER VALUE (2 screens)                             │
├─────────────────────────────────────────────────────────────────┤
│  Screen 6: Personalized Insight Preview                          │
│  Screen 7: Your Matched Expert(s)                                │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 4: CONVERT (3 screens)                                   │
├─────────────────────────────────────────────────────────────────┤
│  Screen 8: Package Selection                                     │
│  Screen 9: Expert Profile Deep Dive                              │
│  Screen 10: Checkout                                             │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 5: ONBOARD TO JOURNEY (2 screens)                        │
├─────────────────────────────────────────────────────────────────┤
│  Screen 11: What to Expect + Journey Overview                    │
│  Screen 12: Schedule First Session                               │
└─────────────────────────────────────────────────────────────────┘
```

---

### Detailed Screen Wireframes

---

## SCREEN 1: Welcome + Value Prop
**Purpose**: Establish Niro's premium positioning, create curiosity

```
┌────────────────────────────────────┐
│                                    │
│           [Niro Logo]              │
│                                    │
│    "Clarity you can act on"        │
│                                    │
│   Premium life guidance from       │
│   vetted Vedic specialists         │
│                                    │
│   ┌──────────────────────────┐    │
│   │   [Illustration/Video]    │    │
│   │   Short loop showing      │    │
│   │   consultation in action  │    │
│   └──────────────────────────┘    │
│                                    │
│   ✓ Specialists, not generalists   │
│   ✓ Packaged outcomes, not minutes │
│   ✓ Follow-through until clarity   │
│                                    │
│   ┌──────────────────────────┐    │
│   │    Get Started →          │    │
│   └──────────────────────────┘    │
│                                    │
│   Already have an account? Login   │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Animated or video background showing real consultation
- 3 trust pillars as bullet points
- Single primary CTA

---

## SCREEN 2: Life Situation Selector
**Purpose**: Qualify user intent, route to relevant specialist track

```
┌────────────────────────────────────┐
│  ←                                 │
│                                    │
│   What's weighing on your mind?    │
│                                    │
│   (Select what feels most urgent)  │
│                                    │
│   ┌──────────────────────────┐    │
│   │ 💼 Career & Work         │    │
│   │    Job, growth, decisions │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │ ❤️ Relationships         │    │
│   │    Love, family, marriage │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │ 💰 Money & Business      │    │
│   │    Finances, ventures     │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │ 🏥 Health & Wellness     │    │
│   │    Physical, mental, energy│   │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │ 🌟 Life Direction        │    │
│   │    Purpose, timing, clarity│   │
│   └──────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Large, tappable cards with icons
- Emotional language, not clinical categories
- Each selection leads to personalized deepdive

---

## SCREEN 3: Specific Concern Deepdive
**Purpose**: Narrow to specific sub-topic for expert matching

```
┌────────────────────────────────────┐
│  ←                                 │
│                                    │
│   Career & Work                    │
│                                    │
│   What specifically is unclear?    │
│                                    │
│   ○ Should I change jobs?          │
│                                    │
│   ○ When is the right time to      │
│     make a career move?            │
│                                    │
│   ○ My workplace feels toxic,      │
│     what should I do?              │
│                                    │
│   ○ I'm stuck and don't know       │
│     my true calling                │
│                                    │
│   ○ Starting a business -          │
│     will it succeed?               │
│                                    │
│   ○ Something else...              │
│     [Text input if selected]       │
│                                    │
│   ┌──────────────────────────┐    │
│   │      Continue →           │    │
│   └──────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Radio button selection (single choice)
- Natural language questions, not categories
- "Something else" escape hatch with text input
- Selected option animates/highlights

---

## SCREEN 4: Birth Details
**Purpose**: Collect essential astrological data with context

```
┌────────────────────────────────────┐
│  ←                                 │
│                                    │
│   To match you with the right      │
│   specialist, we need your         │
│   birth details                    │
│                                    │
│   ┌──────────────────────────┐    │
│   │ 📅 Date of Birth         │    │
│   │    [DD / MM / YYYY]       │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │ ⏰ Time of Birth          │    │
│   │    [HH : MM] [AM/PM]      │    │
│   │                           │    │
│   │    ⓘ Don't know exact time?│   │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │ 📍 Place of Birth         │    │
│   │    [Search city...]       │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐    │
│   │  Why do we need this?     │    │
│   │  Your birth chart reveals │    │
│   │  your unique planetary    │    │
│   │  positions - essential    │    │
│   │  for accurate guidance    │    │
│   └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │      Continue →           │    │
│   └──────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Expandable info tooltip for "why this matters"
- "Don't know exact time?" links to guidance
- City search with autocomplete
- Pre-filled defaults to reduce friction

---

## SCREEN 5: Account Creation (Google OAuth)
**Purpose**: Create account with minimal friction

```
┌────────────────────────────────────┐
│  ←                                 │
│                                    │
│   Almost there!                    │
│                                    │
│   Create your account to save      │
│   your profile and get matched     │
│                                    │
│   ┌──────────────────────────┐    │
│   │  [G] Continue with Google │    │
│   └──────────────────────────┘    │
│                                    │
│                                    │
│   ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐    │
│   │                           │    │
│   │  🔒 Your data is private  │    │
│   │                           │    │
│   │  We never share your      │    │
│   │  birth details or         │    │
│   │  consultation history     │    │
│   │                           │    │
│   └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘    │
│                                    │
│                                    │
│   By continuing, you agree to our  │
│   Terms of Service and Privacy     │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Single Google OAuth button (as per Niro's direction)
- Privacy reassurance prominently displayed
- No phone/email alternative (cleaner flow)

---

## SCREEN 6: Personalized Insight Preview
**Purpose**: Deliver immediate value, build credibility

```
┌────────────────────────────────────┐
│                                    │
│   ✨ Your Snapshot                 │
│                                    │
│   Based on your birth chart:       │
│                                    │
│   ┌──────────────────────────┐    │
│   │                           │    │
│   │   [Mini Birth Chart       │    │
│   │    Visualization]         │    │
│   │                           │    │
│   │   Sun: Aquarius           │    │
│   │   Moon: Cancer            │    │
│   │   Rising: Libra           │    │
│   │                           │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │  📊 Career Timing         │    │
│   │                           │    │
│   │  You're currently in      │    │
│   │  Saturn Mahadasha, which  │    │
│   │  brings career challenges │    │
│   │  but also opportunities   │    │
│   │  for structured growth... │    │
│   │                           │    │
│   │  → See full analysis      │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │   Meet Your Expert →      │    │
│   └──────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Instant gratification with birth chart visual
- Teaser insight relevant to selected topic
- "See full analysis" creates desire for more
- Clear progression to expert matching

---

## SCREEN 7: Your Matched Expert(s)
**Purpose**: Introduce curated specialist(s) based on situation

```
┌────────────────────────────────────┐
│  ←                                 │
│                                    │
│   Your Career Specialist           │
│                                    │
│   Based on your chart and          │
│   situation, we recommend:         │
│                                    │
│   ┌──────────────────────────┐    │
│   │  [Expert Photo]           │    │
│   │                           │    │
│   │  Pandit Ramesh Kumar      │    │
│   │  ★ 4.9 (340 consultations)│    │
│   │                           │    │
│   │  Specializes in:          │    │
│   │  • Career transitions     │    │
│   │  • Saturn period guidance │    │
│   │  • Business timing        │    │
│   │                           │    │
│   │  15 years experience      │    │
│   │  Vedic + KP Astrology     │    │
│   │                           │    │
│   │  [▶ Watch Intro Video]    │    │
│   │                           │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐    │
│   │  See other experts (2)    │    │
│   └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │   View Packages →         │    │
│   └──────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Single recommended expert (not a marketplace)
- "Why this expert" relevance signals
- Video intro preview (Purple Garden pattern)
- Option to see alternatives without overwhelming

---

## SCREEN 8: Package Selection
**Purpose**: Present outcome-led packages, not per-minute pricing

```
┌────────────────────────────────────┐
│  ←                                 │
│                                    │
│   Choose Your Journey              │
│                                    │
│   All packages include follow-     │
│   through until you have clarity   │
│                                    │
│   ┌──────────────────────────┐    │
│   │  FOCUSSED        ₹3,999  │    │
│   │  ─────────────────────── │    │
│   │  • 1× 60-90 min session  │    │
│   │  • 1 follow-up call      │    │
│   │  • Chat support (4 weeks)│    │
│   │  • Written summary       │    │
│   │                          │    │
│   │  [Select]                │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │  SUPPORTED  ⭐   ₹6,999  │    │
│   │  ─────────────────────── │    │
│   │  MOST POPULAR            │    │
│   │  • 1× 60-90 min session  │    │
│   │  • 2 follow-up calls     │    │
│   │  • Priority chat (8 wks) │    │
│   │  • Remedy guidance       │    │
│   │                          │    │
│   │  [Select]                │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │  COMPREHENSIVE  ₹10,999  │    │
│   │  ─────────────────────── │    │
│   │  • 2× 60 min sessions    │    │
│   │  • 3 follow-up calls     │    │
│   │  • Unlimited chat (12 wks)│   │
│   │  • Multi-expert consult  │    │
│   │  • Remedy execution help │    │
│   │                          │    │
│   │  [Select]                │    │
│   └──────────────────────────┘    │
│                                    │
│   100% satisfaction guaranteed     │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- 3 clear tiers (pricing psychology)
- Middle tier highlighted as "Most Popular"
- Outcomes emphasized, not features
- No per-minute anxiety
- Satisfaction guarantee builds trust

---

## SCREEN 9: Expert Profile Deep Dive
**Purpose**: Build confidence before checkout

```
┌────────────────────────────────────┐
│  ←                                 │
│                                    │
│   [Expert Photo - Large]           │
│                                    │
│   Pandit Ramesh Kumar              │
│   ★ 4.9 • 340 consultations        │
│                                    │
│   ┌──────────────────────────┐    │
│   │  [▶ Watch Introduction]   │    │
│   │     2:30 min              │    │
│   └──────────────────────────┘    │
│                                    │
│   About                            │
│   15+ years practicing Vedic       │
│   astrology with specialization    │
│   in career guidance and timing... │
│                                    │
│   Expertise                        │
│   • Career & Business Timing       │
│   • Saturn Transit Guidance        │
│   • Profession Selection           │
│   • Muhurat for Ventures           │
│                                    │
│   Credentials                      │
│   ✓ Jyotish Acharya (ICAS)        │
│   ✓ 15 years experience            │
│   ✓ 340+ satisfied clients         │
│                                    │
│   ───────────────────────────────  │
│   Recent Reviews                   │
│                                    │
│   "He predicted exactly when my    │
│   promotion would come. Spot on."  │
│   - Verified Client, Oct 2025      │
│                                    │
│   ┌──────────────────────────┐    │
│   │  Continue to Checkout →   │    │
│   └──────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Video introduction (Purple Garden best practice)
- Credentials with verification badges
- Specific, outcome-focused reviews
- Clear CTA to proceed

---

## SCREEN 10: Checkout
**Purpose**: Secure payment with order summary

```
┌────────────────────────────────────┐
│  ←                                 │
│                                    │
│   Complete Your Booking            │
│                                    │
│   ┌──────────────────────────┐    │
│   │  Order Summary            │    │
│   │  ─────────────────────── │    │
│   │  Career Clarity Journey   │    │
│   │  SUPPORTED Package        │    │
│   │                           │    │
│   │  Expert: Pandit Ramesh    │    │
│   │  Duration: 8 weeks        │    │
│   │                           │    │
│   │  ─────────────────────── │    │
│   │  Total: ₹6,999            │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │  🔒 Secure Payment        │    │
│   │                           │    │
│   │  [Razorpay Payment Form]  │    │
│   │                           │    │
│   │  UPI • Cards • Wallets    │    │
│   │                           │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐    │
│   │                           │    │
│   │  ✓ No hidden charges      │    │
│   │  ✓ Satisfaction guaranteed│    │
│   │  ✓ Cancel anytime         │    │
│   │                           │    │
│   └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │    Pay ₹6,999 →           │    │
│   └──────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Clear order summary
- Trust signals (no hidden charges, guarantee)
- Multiple payment options via Razorpay
- Single prominent CTA

---

## SCREEN 11: What to Expect
**Purpose**: Post-purchase reassurance, set expectations

```
┌────────────────────────────────────┐
│                                    │
│   ✨ You're All Set!               │
│                                    │
│   Your Career Clarity Journey      │
│   begins now                       │
│                                    │
│   ┌──────────────────────────┐    │
│   │                           │    │
│   │  Your Journey Includes:   │    │
│   │                           │    │
│   │  ① First Session          │    │
│   │     60-90 min deep dive   │    │
│   │     with Pandit Ramesh    │    │
│   │                           │    │
│   │  ② Follow-Up Calls        │    │
│   │     2 check-ins as you    │    │
│   │     apply the guidance    │    │
│   │                           │    │
│   │  ③ Chat Support           │    │
│   │     8 weeks of priority   │    │
│   │     access for questions  │    │
│   │                           │    │
│   │  ④ Written Summary        │    │
│   │     Key insights and      │    │
│   │     action items          │    │
│   │                           │    │
│   └──────────────────────────┘    │
│                                    │
│   ┌──────────────────────────┐    │
│   │  Schedule First Session → │    │
│   └──────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Celebration moment (confetti animation)
- Clear journey timeline
- Numbered steps create structure
- Immediate action CTA

---

## SCREEN 12: Schedule First Session
**Purpose**: Book the first consultation

```
┌────────────────────────────────────┐
│  ←                                 │
│                                    │
│   Schedule Your First Session      │
│                                    │
│   with Pandit Ramesh Kumar         │
│                                    │
│   ┌──────────────────────────┐    │
│   │  Select Date              │    │
│   │                           │    │
│   │  ◀  January 2026  ▶       │    │
│   │                           │    │
│   │  M  T  W  T  F  S  S      │    │
│   │        1  2  3  4  5      │    │
│   │  6  7  8  9  10 11 12     │    │
│   │  13 14 15 ⬤  17 18 19     │    │
│   │  20 21 22 23 24 25 26     │    │
│   │                           │    │
│   └──────────────────────────┘    │
│                                    │
│   Available Times (IST)            │
│                                    │
│   ┌────┐ ┌────┐ ┌────┐ ┌────┐    │
│   │10AM│ │2PM │ │4PM │ │6PM │    │
│   └────┘ └────┘ └────┘ └────┘    │
│                                    │
│   Session: Video Call (Zoom)       │
│   Duration: ~90 minutes            │
│                                    │
│   ┌──────────────────────────┐    │
│   │  Confirm Booking →        │    │
│   └──────────────────────────┘    │
│                                    │
│   Need to prepare? We'll send      │
│   you a guide before your session  │
│                                    │
└────────────────────────────────────┘
```

**Key Elements**:
- Calendar date picker
- Time slot selection
- Session format reminder
- Preparation guidance note

---

## Part 4: Design Recommendations

### Visual Language

| Element | Recommendation |
|---------|----------------|
| **Primary Colors** | Teal (#3E827A) + Gold (#EFE1A9) - existing Niro palette |
| **Typography** | Kumbh Sans for headings, Inter for body |
| **Spacing** | Generous padding (24px+), breathable layout |
| **Cards** | Subtle shadows, rounded corners (12-16px) |
| **Icons** | Line style, consistent stroke width |
| **Illustrations** | Minimal, abstract cosmic elements |

### Interaction Patterns

1. **Progress Indicators**: Subtle dots or line showing position in flow
2. **Micro-animations**: Card selections, button states, transitions
3. **Loading States**: Cosmic-themed skeleton screens
4. **Error Handling**: Friendly messages, clear recovery paths

### Trust Signals to Include Throughout

- "Verified Expert" badges with tooltip explanation
- Real review snippets with outcomes
- "No hidden charges" repeated at key moments
- Privacy reassurance near data collection
- "X people consulted this week" social proof

---

## Part 5: Key Differentiators from Competition

| Competitor Pattern | Niro Difference |
|-------------------|-----------------|
| **Marketplace** (browse 1000s of astrologers) | **Curated matching** (we recommend the right expert) |
| **Per-minute billing** (anxiety, uncertainty) | **Package pricing** (clear outcomes, no meter) |
| **Generic categories** (Love, Career, Health) | **Situation-specific** (natural language questions) |
| **Transactional** (one reading, done) | **Journey-based** (follow-through until clarity) |
| **AI-only or Human-only** | **AI for engagement, Human for transformation** |
| **Upsells & hidden fees** | **Transparent, all-inclusive packages** |

---

## Part 6: Metrics to Track

### Onboarding Funnel
- Screen 1→2 conversion (Welcome → Topic selection)
- Screen 4 completion rate (Birth details submission)
- Screen 5 conversion (Account creation)
- Screen 8 selection rate (Package choice)
- Screen 10 completion (Payment)

### Quality Metrics
- Time to first session scheduled
- NPS after first consultation
- Package completion rate
- Return booking rate

---

## Next Steps

1. **Validate flow with users**: Quick interviews with 5-10 potential customers
2. **Create high-fidelity mockups**: Based on these wireframes
3. **Build prototype**: Interactive Figma/Framer prototype for testing
4. **A/B test key decisions**: Package pricing, expert matching display
5. **Implement incrementally**: Phase 1 (core flow), Phase 2 (optimizations)

---

*Document created: January 2026*
*Based on competitive analysis of 10+ astrology apps across India and US markets*
