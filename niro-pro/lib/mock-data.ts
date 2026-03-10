import { Practitioner, Package, Lead, Session, EarningsRow, Notification, TopicKey } from "./types";

export const MOCK_PRACTITIONER: Practitioner = {
  id: "prac_001",
  full_name: "Kavita Sharma",
  primary_tradition: "Vedic Astrology",
  languages: ["Hindi", "English"],
  years_of_practice: 12,
  credential_education: "Jyotish Visharad, Bharatiya Vidya Bhavan, 2012",
  city: "Mumbai",
  philosophy: "I believe astrology is not about predictions — it is about patterns that help us make more conscious choices. My work focuses on timing: when to act, when to wait, and how to align your decisions with the larger rhythms of your life. Every chart tells a story that is already unfolding. I help you read it clearly.",
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
  photo_url: null,
};

export const MOCK_PACKAGES: Package[] = [
  {
    id: "pkg_001",
    name: "Intro Clarity Call",
    who_its_for: "Someone exploring astrology for the first time",
    topic: "career",
    outcomes: [
      "A clear answer to your most pressing question",
      "One key timing window for the next 90 days",
      "A simple next step you can take immediately",
    ],
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
    outcomes: [
      "A written chart summary for your career zone",
      "Timing windows for the next 3 months",
      "A 2-step action plan aligned with your chart",
    ],
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
    outcomes: [
      "Compatibility insights from your Navamsa chart",
      "Current Venus and 7th house transit analysis",
      "Timing guidance for the next 60 days",
    ],
    duration_days: 30,
    sessions_included: 2,
    price_inr: 2500,
    is_intro_template: false,
  },
];

export const MOCK_LEADS: Lead[] = [
  {
    id: "lead_001",
    client_name: "Priya",
    life_area: "career",
    question: "Should I quit my job and start my own business this year? I've been at my current company for 6 years and feel completely stuck.",
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
      { rule: "MAHADASHA_JUPITER", summary: "Expansion period — favourable for new ventures" },
    ],
    flat_fee_inr: 99,
    expires_in_seconds: 847,
    status: "pending",
  },
  {
    id: "lead_002",
    client_name: "Rahul",
    life_area: "money",
    question: "I want to invest in a new business partnership. Will this be financially good for me in the next year?",
    niro_ai_context: "Client is evaluating a significant financial commitment with a business partner. Needs timing clarity.",
    chart: null,
    top_transits: [],
    focus_factors: [],
    flat_fee_inr: 99,
    expires_in_seconds: 492,
    status: "pending",
  },
];

export const MOCK_SESSION: Session = {
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
};

export const MOCK_EARNINGS: EarningsRow[] = [
  { date: "Mar 8, 2026", client: "Priya", package: "Career Clarity Session", gross_inr: 1500, fee_inr: 99, net_inr: 1401 },
  { date: "Mar 6, 2026", client: "Amit", package: "Intro Clarity Call", gross_inr: 499, fee_inr: 99, net_inr: 400 },
  { date: "Mar 4, 2026", client: "Sunita", package: "Career Clarity Session", gross_inr: 1500, fee_inr: 99, net_inr: 1401 },
  { date: "Mar 1, 2026", client: "Ravi", package: "Relationship Clarity Package", gross_inr: 2500, fee_inr: 99, net_inr: 2401 },
  { date: "Feb 28, 2026", client: "Meera", package: "Intro Clarity Call", gross_inr: 499, fee_inr: 99, net_inr: 400 },
];

export const MOCK_NOTIFICATIONS: Notification[] = [
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

export const SESSION_CARDS: Record<string, {
  phase01: { title: string; guide: string; opening: string; past_obs: string };
  phase02: { title: string; guide: string; script: string; resonance_check: string };
  phase03: { title: string; guide: string; script: string; never: string };
}> = {
  "Vedic Astrology": {
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
      guide: "Name ONE unexplored thread. Offer your package once — as a door, not a close.",
      script: '"There\'s a pattern around this area I couldn\'t fully get to today. A 30-minute session would let us map the full picture. No rush — but there\'s a lot more here for you."',
      never: "Never say 'Would you like to book?' — offer, don't sell.",
    },
  },
  "KP Astrology": {
    phase01: {
      title: "Open + Past Observation",
      guide: "Use KP insights but speak in plain language — never mention cuspal sub lords.",
      opening: '"Your chart shows a person who thinks deeply before acting — when you do move, you move with precision."',
      past_obs: '"Around 3–4 years ago there was a significant shift in your professional environment — something you had to navigate rather than choose."',
    },
    phase02: {
      title: "Answer Their Question",
      guide: "Give a clear directional answer using sublord principles without the jargon.",
      script: '"The indicators I\'m seeing point toward a window of clarity opening in the next 4–6 months. The question is what you do now to prepare."',
      resonance_check: '"Does that align with what you\'ve been sensing?"',
    },
    phase03: {
      title: "Invite Deeper — No Pressure",
      guide: "Offer to go deeper on timing — KP\'s unique strength.",
      script: '"KP astrology is particularly strong on timing — month and week-level precision. A full session would let me map the exact windows for your question."',
      never: "Don't give specific dates in 5 minutes — that's the value of a full reading.",
    },
  },
  "Numerology": {
    phase01: {
      title: "Open + Past Observation",
      guide: "Speak in life themes — never open with 'your life path number is X'.",
      opening: '"There is a 5 at the heart of your chart — restless, freedom-seeking. You thrive in motion and suffocate when trapped."',
      past_obs: '"There was a period of deep questioning where you had to rediscover yourself outside of others\' definitions of you."',
    },
    phase02: {
      title: "Answer Their Question",
      guide: "Use personal year cycle to give a direct, actionable answer.",
      script: '"You are in a 1 Personal Year — the start of a new nine-year cycle. One of the best windows in nearly a decade to begin something new."',
      resonance_check: '"Does that feel true?"',
    },
    phase03: {
      title: "Invite Deeper — No Pressure",
      guide: "Name a specific gap in what was covered.",
      script: '"Your core numbers reveal something about the gap between how you show up publicly and who you are privately. A full session takes us through your complete profile."',
      never: "Don't give away the complete reading — leave them genuinely curious.",
    },
  },
  "Tarot": {
    phase01: {
      title: "Open + Energy Observation",
      guide: "Speak in energy and themes — never name a specific card.",
      opening: '"The energy around you right now is one of transition. Something is ending so something more aligned can begin."',
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
      script: '"There was a second layer I kept seeing — around what you truly want versus what you\'ve been told you should want. A longer reading gives us real space to sit with it."',
      never: "Don't offer the package multiple times — once, as a door, never a close.",
    },
  },
  "Vastu": {
    phase01: {
      title: "Open + Space Observation",
      guide: "Connect their question to how their space might be affecting that life area.",
      opening: '"The direction your main entrance faces has a direct relationship with the kind of energy that flows into your career and finances."',
      past_obs: '"Many of the challenges in this area often have a spatial dimension that goes completely unaddressed."',
    },
    phase02: {
      title: "Answer Their Question",
      guide: "Give one specific vastu insight that directly addresses their question.",
      script: '"Based on what you\'ve described, the northwest zone of your home or workspace is where I\'d focus first — that direction is associated with movement and new opportunities."',
      resonance_check: '"Does that direction feel significant in your space?"',
    },
    phase03: {
      title: "Invite Deeper — No Pressure",
      guide: "Offer a proper vastu audit as the natural next step.",
      script: '"A proper vastu consultation covers all 8 directions in relation to your specific question. I\'d love to do a full assessment — it usually takes 60–90 minutes and gives you a clear action list."',
      never: "Don't promise dramatic results — speak to the process and what you'll uncover.",
    },
  },
};

export const TOPICS: { value: TopicKey; label: string }[] = [
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
  "Vedic Astrology", "KP Astrology", "Numerology", "Tarot", "Vastu", "Palmistry", "Other",
];

export const LANGUAGES = [
  "Hindi", "English", "Tamil", "Telugu", "Marathi", "Bengali", "Kannada", "Other",
];

export const TOPIC_BADGE_COLOURS: Record<string, { bg: string; text: string }> = {
  career: { bg: "bg-blue-100", text: "text-blue-800" },
  money: { bg: "bg-green-100", text: "text-green-800" },
  health_energy: { bg: "bg-red-100", text: "text-red-800" },
  romantic_relationships: { bg: "bg-pink-100", text: "text-pink-800" },
  marriage_partnership: { bg: "bg-rose-100", text: "text-rose-800" },
  spirituality: { bg: "bg-purple-100", text: "text-purple-800" },
  family_home: { bg: "bg-amber-100", text: "text-amber-800" },
  self_psychology: { bg: "bg-indigo-100", text: "text-indigo-800" },
  friends_social: { bg: "bg-teal-100", text: "text-teal-800" },
  learning_education: { bg: "bg-cyan-100", text: "text-cyan-800" },
  travel_relocation: { bg: "bg-orange-100", text: "text-orange-800" },
  legal_contracts: { bg: "bg-slate-100", text: "text-slate-800" },
  daily_guidance: { bg: "bg-violet-100", text: "text-violet-800" },
  general: { bg: "bg-gray-100", text: "text-gray-700" },
};
