/**
 * NIRO V6 Landing Page Content - Source of Truth
 * Updated from: Niro_LandingPage_Content_Template_And_Content_V6_UpdatedKeyColumns.xlsx
 * 
 * Total: 18 topics organized under 3 main categories (Love, Career, Health)
 * Each topic has 3 tiers (Focussed, Supported, Comprehensive)
 */

// ==========================================
// V6 TIER CONFIGURATION
// ==========================================
export const V6_TIER_CONFIG = {
  Focussed: { 
    label: 'Focussed',
    badge: null,
    description: 'Quick clarity with one primary expert and fast follow-ups.',
  },
  Supported: { 
    label: 'Supported',
    badge: 'Recommended',
    description: 'Extended support with follow-ups for ongoing clarity.',
  },
  Comprehensive: { 
    label: 'Comprehensive',
    badge: null,
    description: 'High-stakes support with multiple experts, more sessions, and unlimited chat.',
  },
};

// ==========================================
// EXPERTS DATA (for Experts Widget)
// ==========================================
export const V6_EXPERTS = [
  { role: 'Senior Vedic Astrologer', badge: 'Verified • 10+ yrs', focus: 'Chart + timing clarity' },
  { role: 'Tarot Guide', badge: 'Verified • 6+ yrs', focus: 'Emotional clarity + patterns' },
  { role: 'Numerology Expert', badge: 'Verified • 8+ yrs', focus: 'Cycles + decision windows' },
];

// ==========================================
// COMMON SECTIONS
// ==========================================
const COMMON_WHY_NIRO = [
  'Real experts (not bots)',
  'Unlimited follow-ups till clarity',
  'Private & secure',
  'Built for modern life decisions (not predictions)',
  'Clear outcomes + timelines',
];

const COMMON_FAQS_CAREER = [
  { q: 'What\'s included in this package?', a: 'Your package includes expert consultations, follow-ups, and unlimited chat support based on your tier.' },
  { q: 'How do calls and follow-ups work?', a: 'After purchase, you\'ll schedule your first call within 24-48 hours. Follow-ups are scheduled based on your journey needs.' },
  { q: 'Can I chat anytime during the package window?', a: 'Yes. Supported and Comprehensive tiers include unlimited chat throughout your package duration.' },
  { q: 'What if I\'m not satisfied—do you offer refunds?', a: 'Yes. No questions asked — 7-day full refund guarantee.' },
  { q: 'Can I switch experts if I don\'t feel a match?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
  { q: 'Will this tell me if I should quit or switch?', a: 'We provide clarity on timing and direction, but the decision is always yours.' },
  { q: 'Is my information private and secure?', a: 'Absolutely. All consultations are private and your data is protected.' },
  { q: 'Do you offer remedies?', a: 'Remedies are optional add-ons. Coming soon.' },
];

const COMMON_FAQS_LOVE = [
  { q: 'What\'s included in this package?', a: 'Your package includes expert consultations, follow-ups, and unlimited chat support based on your tier.' },
  { q: 'How do calls and follow-ups work?', a: 'After purchase, you\'ll schedule your first call within 24-48 hours. Follow-ups are scheduled based on your journey needs.' },
  { q: 'Can I chat anytime during the package window?', a: 'Yes. Supported and Comprehensive tiers include unlimited chat throughout your package duration.' },
  { q: 'What if I\'m not satisfied—do you offer refunds?', a: 'Yes. No questions asked — 7-day full refund guarantee.' },
  { q: 'Can I switch experts if I don\'t feel a match?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
  { q: 'Will this tell me whether we will end up together?', a: 'We provide clarity on compatibility and timing, but outcomes depend on both partners.' },
  { q: 'Is my information private and secure?', a: 'Absolutely. All consultations are private and your data is protected.' },
  { q: 'Do you offer remedies?', a: 'Remedies are optional add-ons. Coming soon.' },
];

const COMMON_FAQS_HEALTH = [
  { q: 'What\'s included in this package?', a: 'Your package includes expert consultations, follow-ups, and unlimited chat support based on your tier.' },
  { q: 'How do calls and follow-ups work?', a: 'After purchase, you\'ll schedule your first call within 24-48 hours. Follow-ups are scheduled based on your journey needs.' },
  { q: 'Can I chat anytime during the package window?', a: 'Yes. Supported and Comprehensive tiers include unlimited chat throughout your package duration.' },
  { q: 'What if I\'m not satisfied—do you offer refunds?', a: 'Yes. No questions asked — 7-day full refund guarantee.' },
  { q: 'Can I switch experts if I don\'t feel a match?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
  { q: 'Is this medical advice?', a: 'No. This is holistic guidance. Please consult medical professionals for health issues.' },
  { q: 'Is my information private and secure?', a: 'Absolutely. All consultations are private and your data is protected.' },
  { q: 'Do you offer remedies?', a: 'Remedies are optional add-ons. Coming soon.' },
];

// ==========================================
// CAREER TOPICS (6)
// ==========================================
export const V6_CAREER_SUBTOPICS = {
  'career-clarity': {
    slug: 'career-clarity',
    category: 'Career & Money',
    topicKey: 'Career Clarity',
    headerTitle: 'Career Clarity',
    heroOneLinePromise: 'Decode what your chart says about your strengths and direction so you can choose your next move with clarity.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Find direction in your career—what fits you, and what\'s next. Get a clear reading of your work phase, ideal roles, and timing to act.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 3999, durationWeeks: 4 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 10999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Your current career phase: what\'s working and what\'s blocked',
          'What kind of work will feel \'right\' for you in this phase',
          'What to avoid in the next decision to prevent regret'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Your current career phase: what\'s working and what\'s blocked',
          'What kind of work will feel \'right\' for you in this phase',
          'What to avoid in the next decision to prevent regret'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Your current career phase: what\'s working and what\'s blocked',
          'What kind of work will feel \'right\' for you in this phase',
          'What to avoid in the next decision to prevent regret'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_CAREER,
  },

  'job-transition': {
    slug: 'job-transition',
    category: 'Career & Money',
    topicKey: 'Job Transition',
    headerTitle: 'Job Transition',
    heroOneLinePromise: 'Plan the right timing for switching roles and reduce risk in interviews, offers, and decisions.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Switch jobs with confidence—timing, risks, and the best next move. Know when to resign, interview, negotiate, or wait—with support through the transition.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 5999, durationWeeks: 8 },
      Supported: { priceInr: 9999, durationWeeks: 12 },
      Comprehensive: { priceInr: 14999, durationWeeks: 16 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 12 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 16 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Whether a job switch is supported right now (and why)',
          'What to prioritise in the next role to feel stable',
          'Key risks to avoid during the switch (timing + people)'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Whether a job switch is supported right now (and why)',
          'What to prioritise in the next role to feel stable',
          'Key risks to avoid during the switch (timing + people)'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Whether a job switch is supported right now (and why)',
          'What to prioritise in the next role to feel stable',
          'Key risks to avoid during the switch (timing + people)'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_CAREER,
  },

  'money-stability': {
    slug: 'money-stability',
    category: 'Career & Money',
    topicKey: 'Money Stability',
    headerTitle: 'Money Stability',
    heroOneLinePromise: 'Understand your money cycles and build steady financial momentum with better timing and fewer setbacks.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Bring stability to money matters—income, expenses, and financial stress. Understand what\'s causing the volatility and what the next few weeks look like.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 8 },
      Comprehensive: { priceInr: 7999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Why money feels unstable right now (chart timing)',
          'Where to be cautious vs where to lean in',
          'What will stabilise finances fastest in your phase'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Why money feels unstable right now (chart timing)',
          'Where to be cautious vs where to lean in',
          'What will stabilise finances fastest in your phase'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Why money feels unstable right now (chart timing)',
          'Where to be cautious vs where to lean in',
          'What will stabilise finances fastest in your phase'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_CAREER,
  },

  'big-decision-timing': {
    slug: 'big-decision-timing',
    category: 'Career & Money',
    topicKey: 'Big Decision Timing',
    headerTitle: 'Big Decision Timing',
    heroOneLinePromise: 'Get a clear "act now vs wait" verdict for a major decision you\'re facing—based on your chart\'s timing.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Time a big decision—business, purchase, or life move. Get clarity on whether now is the right window to act, wait, or pivot.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 3999, durationWeeks: 4 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 10999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Is this the right time to act on your decision?',
          'What factors support or block the decision now',
          'What risks you need to watch'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Is this the right time to act on your decision?',
          'What factors support or block the decision now',
          'What risks you need to watch'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Is this the right time to act on your decision?',
          'What factors support or block the decision now',
          'What risks you need to watch'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_CAREER,
  },

  'work-stress': {
    slug: 'work-stress',
    category: 'Career & Money',
    topicKey: 'Work Stress',
    headerTitle: 'Work Stress',
    heroOneLinePromise: 'See what\'s behind the pressure right now—and when relief is coming—so you can manage it better.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Handle work stress—burnout, pressure, and uncertainty. Get clarity on why this phase feels heavy and when it will lighten up.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 8 },
      Comprehensive: { priceInr: 7999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Why work pressure is peaking right now',
          'What boundaries to set vs what to endure temporarily',
          'How to protect your energy without burning out'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Why work pressure is peaking right now',
          'What boundaries to set vs what to endure temporarily',
          'How to protect your energy without burning out'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Why work pressure is peaking right now',
          'What boundaries to set vs what to endure temporarily',
          'How to protect your energy without burning out'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_CAREER,
  },

  'office-politics': {
    slug: 'office-politics',
    category: 'Career & Money',
    topicKey: 'Office Politics',
    headerTitle: 'Office Politics',
    heroOneLinePromise: 'Navigate workplace dynamics and conflicts without losing momentum or peace of mind.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Deal with office politics—conflict, misunderstanding, or unfair treatment. Know what to prioritize and when to step back or push forward.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 8 },
      Comprehensive: { priceInr: 7999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Why this conflict is surfacing now',
          'Who to trust / distance from in this phase',
          'Whether to speak up or hold back (and when)'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Why this conflict is surfacing now',
          'Who to trust / distance from in this phase',
          'Whether to speak up or hold back (and when)'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Why this conflict is surfacing now',
          'Who to trust / distance from in this phase',
          'Whether to speak up or hold back (and when)'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_CAREER,
  },
};

// ==========================================
// LOVE & RELATIONSHIPS TOPICS (6)
// ==========================================
export const V6_LOVE_SUBTOPICS = {
  'relationship-healing': {
    slug: 'relationship-healing',
    category: 'Love & Relationships',
    topicKey: 'Relationship Healing',
    headerTitle: 'Relationship Healing',
    heroOneLinePromise: 'Work through recurring relationship patterns and feel emotionally steady again — without overthinking every move.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Heal a relationship—rebuilding connection, stability, and peace. Understand what\'s breaking the bond and how to repair it with support.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 3999, durationWeeks: 4 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 10999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'What your chart says about this connection right now',
          'Root cause of distance/instability (from your chart patterns)',
          'What repair looks like—and the conditions needed for it'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'What your chart says about this connection right now',
          'Root cause of distance/instability (from your chart patterns)',
          'What repair looks like—and the conditions needed for it'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'What your chart says about this connection right now',
          'Root cause of distance/instability (from your chart patterns)',
          'What repair looks like—and the conditions needed for it'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_LOVE,
  },

  'dating-compatibility': {
    slug: 'dating-compatibility',
    category: 'Love & Relationships',
    topicKey: 'Dating & Compatibility',
    headerTitle: 'Dating & Compatibility',
    heroOneLinePromise: 'Understand if a new connection has potential — and what you should watch out for before investing emotionally.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Navigate dating—compatibility, patterns, and next steps. Know whether to invest emotionally and what to expect in the coming weeks.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 8 },
      Comprehensive: { priceInr: 7999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'What your chart says about this connection right now',
          'Early red/green flags based on your compatibility indicators',
          'What to prioritize before committing further'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'What your chart says about this connection right now',
          'Early red/green flags based on your compatibility indicators',
          'What to prioritize before committing further'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'What your chart says about this connection right now',
          'Early red/green flags based on your compatibility indicators',
          'What to prioritize before committing further'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_LOVE,
  },

  'breakup-closure': {
    slug: 'breakup-closure',
    category: 'Love & Relationships',
    topicKey: 'Breakup & Closure',
    headerTitle: 'Breakup & Closure',
    heroOneLinePromise: 'Get emotional clarity after a breakup so you can move forward without carrying the weight of confusion.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Find closure after a breakup—peace, clarity, and next steps. Understand what led here and how to rebuild emotional stability.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 3999, durationWeeks: 4 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 10999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'What your chart says about this connection right now',
          'Why it ended (or needed to) from a patterns perspective',
          'What closure looks like for you—and whether reconnection is possible'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'What your chart says about this connection right now',
          'Why it ended (or needed to) from a patterns perspective',
          'What closure looks like for you—and whether reconnection is possible'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'What your chart says about this connection right now',
          'Why it ended (or needed to) from a patterns perspective',
          'What closure looks like for you—and whether reconnection is possible'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_LOVE,
  },

  'communication-trust': {
    slug: 'communication-trust',
    category: 'Love & Relationships',
    topicKey: 'Communication & Trust',
    headerTitle: 'Communication & Trust',
    heroOneLinePromise: 'Improve communication and rebuild trust with your partner — step by step, with guidance on what to address first.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Strengthen communication—rebuilding trust, honesty, and connection. Get clarity on the blocks and how to repair them effectively.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 8 },
      Comprehensive: { priceInr: 7999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'What your chart says about this connection right now',
          'What\'s creating friction or misunderstanding',
          'What you can do to shift the dynamic'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'What your chart says about this connection right now',
          'What\'s creating friction or misunderstanding',
          'What you can do to shift the dynamic'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'What your chart says about this connection right now',
          'What\'s creating friction or misunderstanding',
          'What you can do to shift the dynamic'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_LOVE,
  },

  'family-relationships': {
    slug: 'family-relationships',
    category: 'Love & Relationships',
    topicKey: 'Family Relationships',
    headerTitle: 'Family Relationships',
    heroOneLinePromise: 'Navigate family expectations, conflicts, and boundaries while protecting your peace and relationships.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Handle family relationships—conflict, boundaries, and emotional strain. Get clarity on dynamics and the best way to reduce friction.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 3999, durationWeeks: 4 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 10999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'What your chart says about this connection right now',
          'Why friction keeps happening (roles, expectations, boundaries)',
          'What to say/do to reduce conflict without over-explaining'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'What your chart says about this connection right now',
          'Why friction keeps happening (roles, expectations, boundaries)',
          'What to say/do to reduce conflict without over-explaining'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'What your chart says about this connection right now',
          'Why friction keeps happening (roles, expectations, boundaries)',
          'What to say/do to reduce conflict without over-explaining'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_LOVE,
  },

  'marriage-planning': {
    slug: 'marriage-planning',
    category: 'Love & Relationships',
    topicKey: 'Marriage Planning',
    headerTitle: 'Marriage Planning',
    heroOneLinePromise: 'Get clarity on timing, partner alignment, and family dynamics so you can move toward marriage with conviction.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Plan marriage with confidence—timing, compatibility, and next steps. Know when marriage is supported and what to prioritise before committing.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 5999, durationWeeks: 8 },
      Supported: { priceInr: 9999, durationWeeks: 12 },
      Comprehensive: { priceInr: 14999, durationWeeks: 16 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 12 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 16 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'What your chart says about this connection right now',
          'Readiness + compatibility indicators for long-term marriage',
          'What to prioritise before you commit (non-negotiables)'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'What your chart says about this connection right now',
          'Readiness + compatibility indicators for long-term marriage',
          'What to prioritise before you commit (non-negotiables)'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'What your chart says about this connection right now',
          'Readiness + compatibility indicators for long-term marriage',
          'What to prioritise before you commit (non-negotiables)'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_LOVE,
  },
};

// ==========================================
// HEALTH & WELLNESS TOPICS (6)
// ==========================================
export const V6_HEALTH_SUBTOPICS = {
  'stress-management': {
    slug: 'stress-management',
    category: 'Health & Wellness',
    topicKey: 'Stress & Anxiety',
    headerTitle: 'Stress & Anxiety',
    heroOneLinePromise: 'Understand why this phase feels overwhelming—and when the pressure will ease—so you can cope better.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Manage stress and anxiety—understand the root cause and when relief comes. Get clarity on what\'s driving the overwhelm and how to regain stability.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 8 },
      Comprehensive: { priceInr: 7999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Why this phase feels heavier than usual',
          'What\'s triggering the stress (chart patterns)',
          'What to do immediately to reduce pressure'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Why this phase feels heavier than usual',
          'What\'s triggering the stress (chart patterns)',
          'What to do immediately to reduce pressure'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Why this phase feels heavier than usual',
          'What\'s triggering the stress (chart patterns)',
          'What to do immediately to reduce pressure'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_HEALTH,
  },

  'sleep-reset': {
    slug: 'sleep-reset',
    category: 'Health & Wellness',
    topicKey: 'Sleep & Rest',
    headerTitle: 'Sleep & Rest',
    heroOneLinePromise: 'Find out what\'s disrupting your sleep and when the restless phase will improve — so you can plan around it.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Reset your sleep—understand the disruption and when it eases. Know what\'s off in your cycle and what will help you rest better.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 8 },
      Comprehensive: { priceInr: 7999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Why sleep is disrupted right now (chart timing)',
          'What\'s creating mental unrest at night',
          'Small changes to try during this phase'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Why sleep is disrupted right now (chart timing)',
          'What\'s creating mental unrest at night',
          'Small changes to try during this phase'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Why sleep is disrupted right now (chart timing)',
          'What\'s creating mental unrest at night',
          'Small changes to try during this phase'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_HEALTH,
  },

  'energy-balance': {
    slug: 'energy-balance',
    category: 'Health & Wellness',
    topicKey: 'Energy & Vitality',
    headerTitle: 'Energy & Vitality',
    heroOneLinePromise: 'Understand why your energy feels off—and what the next few weeks look like for recovery and momentum.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Balance your energy—low motivation, fatigue, or feeling stuck. Get clarity on the root cause and when momentum returns.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 8 },
      Comprehensive: { priceInr: 7999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Why energy is low in this phase',
          'What\'s draining you vs what will restore you',
          'What small actions will have the biggest impact now'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Why energy is low in this phase',
          'What\'s draining you vs what will restore you',
          'What small actions will have the biggest impact now'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Why energy is low in this phase',
          'What\'s draining you vs what will restore you',
          'What small actions will have the biggest impact now'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_HEALTH,
  },

  'health-timing': {
    slug: 'health-timing',
    category: 'Health & Wellness',
    topicKey: 'Health Timing',
    headerTitle: 'Health Timing',
    heroOneLinePromise: 'Know when to push, when to rest, and when to prioritize health moves—based on your chart\'s timing.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Time health decisions—surgery, treatment, or lifestyle changes. Know when your chart supports action and when to wait.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 3999, durationWeeks: 4 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 10999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Is this a good time for the health action you\'re considering?',
          'What to watch out for in this phase',
          'What will support recovery vs slow it down'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Is this a good time for the health action you\'re considering?',
          'What to watch out for in this phase',
          'What will support recovery vs slow it down'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Is this a good time for the health action you\'re considering?',
          'What to watch out for in this phase',
          'What will support recovery vs slow it down'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_HEALTH,
  },

  'emotional-wellbeing': {
    slug: 'emotional-wellbeing',
    category: 'Health & Wellness',
    topicKey: 'Emotional Wellbeing',
    headerTitle: 'Emotional Wellbeing',
    heroOneLinePromise: 'Get clarity on why emotions feel unstable—and what the next few weeks hold for inner peace.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Stabilize emotional wellbeing—mood swings, sadness, or feeling lost. Understand what\'s happening and when things will feel lighter.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 3999, durationWeeks: 4 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 10999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'Why emotions feel heavy or unstable right now',
          'What\'s driving the inner turbulence',
          'What will help you stabilize fastest'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'Why emotions feel heavy or unstable right now',
          'What\'s driving the inner turbulence',
          'What will help you stabilize fastest'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'Why emotions feel heavy or unstable right now',
          'What\'s driving the inner turbulence',
          'What will help you stabilize fastest'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_HEALTH,
  },

  'recovery-support': {
    slug: 'recovery-support',
    category: 'Health & Wellness',
    topicKey: 'Recovery Support',
    headerTitle: 'Recovery Support',
    heroOneLinePromise: 'Understand your recovery timeline and what will speed up or slow down your healing process.',
    topicExplainerOneLiner: 'Hi <UserName>, here are the paths you can choose for your journey.',
    heroSubtitle: 'Support recovery—from illness, surgery, or setback. Know when your chart supports healing and how to optimize the journey.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 3999, durationWeeks: 4 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 10999, durationWeeks: 12 }
    },
    tierSummaryDetails: {
      Focussed: '• Duration: 4 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 1 follow-up\n• Support: Unlimited chat',
      Supported: '• Duration: 8 weeks\n• Consultations: 1 deep session (Vedic Astrologer)\n• Follow-ups: 2 follow-ups\n• Support: Unlimited chat',
      Comprehensive: '• Duration: 12 weeks\n• Consultations: 2 expert sessions (Vedic Astrologer + Tarot Reader / Numerologist)\n• Follow-ups: 3 follow-ups\n• Support: Unlimited chat'
    },
    outcomesByTier: {
      Focussed: {
        clarity: [
          'What your chart says about recovery timing',
          'What\'s supporting vs blocking healing right now',
          'What actions will help recovery most in this phase'
        ],
        timeline: [
          'How long this phase is likely to last',
          'Your next best 2–4 week window to act (or wait)'
        ],
        support: [
          'Unlimited chat to ask follow-up questions during the package',
          'A clear written summary so you don\'t forget what matters'
        ]
      },
      Supported: {
        clarity: [
          'What your chart says about recovery timing',
          'What\'s supporting vs blocking healing right now',
          'What actions will help recovery most in this phase'
        ],
        timeline: [
          'Clear \'now vs later\' timing across the next 8–12 weeks',
          'Key dates/windows to watch (decision + emotional stability)'
        ],
        support: [
          'Unlimited chat for ongoing doubts and quick reassurance',
          'Follow-up calls to refine decisions as things evolve'
        ]
      },
      Comprehensive: {
        clarity: [
          'What your chart says about recovery timing',
          'What\'s supporting vs blocking healing right now',
          'What actions will help recovery most in this phase'
        ],
        timeline: [
          'Cross-verified timing windows (2 expert perspectives)',
          'A clear 12–16 week view of what improves and when'
        ],
        support: [
          'Unlimited chat + more follow-ups for high-stakes decisions',
          'Second expert opinion to reduce confusion and build confidence'
        ]
      }
    },
    howUnfoldsByTier: {
      Focussed: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '1 structured follow-up in Week 2 (20 min) if needed',
        'Share your context in-app before the call for a sharper reading'
      ],
      Supported: [
        'Primary 60–90 min session with Vedic Astrologer',
        'Unlimited chat for the full package duration',
        '2 follow-up calls (20 min) to track progress + adjust guidance',
        'Priority responses on chat during peak uncertainty'
      ],
      Comprehensive: [
        '2 expert perspectives: Vedic Astrologer + Tarot Reader / Numerologist',
        '2 deep sessions (60 min each) to cross-verify clarity + timing',
        '3 follow-up calls (20 min) across the journey',
        'Unlimited chat for the full package duration'
      ]
    },
    expertsWidgetTitle: 'Meet your experts',
    expertsWidgetSubtitle: 'Verified specialists for this journey. Choose one to start — you can switch later.',
    remediesTitle: 'Optional add-ons (Coming soon)',
    whyNiroBullets: COMMON_WHY_NIRO,
    faqs: COMMON_FAQS_HEALTH,
  },
};

// ==========================================
// TILE ID TO SUBTOPIC SLUG MAPPING
// ==========================================
export const V6_TILE_TO_SUBTOPIC_MAP = {
  // Love tiles
  'relationship_healing': 'relationship-healing',
  'dating_compatibility': 'dating-compatibility',
  'breakup_closure': 'breakup-closure',
  'communication_trust': 'communication-trust',
  'family_relationships': 'family-relationships',
  'marriage_planning': 'marriage-planning',
  // Career tiles  
  'career_clarity': 'career-clarity',
  'job_transition': 'job-transition',
  'money_stability': 'money-stability',
  'big_decision_timing': 'big-decision-timing',
  'work_stress': 'work-stress',
  'office_politics': 'office-politics',
  // Health tiles
  'stress_management': 'stress-management',
  'sleep_reset': 'sleep-reset',
  'energy_balance': 'energy-balance',
  'health_timing': 'health-timing',
  'emotional_wellbeing': 'emotional-wellbeing',
  'recovery_support': 'recovery-support',
};

// ==========================================
// HELPER FUNCTIONS
// ==========================================

/**
 * Get subtopic data by slug
 */
export function getV6SubtopicBySlug(slug) {
  // Check all category objects
  const allSubtopics = {
    ...V6_LOVE_SUBTOPICS,
    ...V6_CAREER_SUBTOPICS,
    ...V6_HEALTH_SUBTOPICS,
  };
  return allSubtopics[slug] || null;
}

/**
 * Get all subtopics for a category
 */
export function getV6SubtopicsByCategory(category) {
  switch (category) {
    case 'love':
      return Object.values(V6_LOVE_SUBTOPICS);
    case 'career':
      return Object.values(V6_CAREER_SUBTOPICS);
    case 'health':
      return Object.values(V6_HEALTH_SUBTOPICS);
    default:
      return [];
  }
}

/**
 * Get all V6 subtopics
 */
export function getAllV6Subtopics() {
  return [
    ...Object.values(V6_LOVE_SUBTOPICS),
    ...Object.values(V6_CAREER_SUBTOPICS),
    ...Object.values(V6_HEALTH_SUBTOPICS),
  ];
}
