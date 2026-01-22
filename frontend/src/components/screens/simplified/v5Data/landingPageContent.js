/**
 * NIRO V5 Landing Page Content
 * All content from:
 * - niro_landing_pages_v5.json (10 sub-topics)
 * - Niro_Landing_Pages_V5_Remaining_8_Subtopics_Content.xlsx (8 sub-topics)
 * 
 * Total: 18 sub-topics organized under 3 main topics (Love, Career, Health)
 * Each topic has 6 sub-topics
 */

// ==========================================
// LOVE / RELATIONSHIP SUB-TOPICS (6)
// ==========================================

export const LOVE_SUBTOPICS = {
  'relationship-healing': {
    slug: 'relationship-healing',
    category: 'Love',
    subTopic: 'Relationship Healing',
    headline: 'Relationship Healing Guidance',
    subHeadline: 'Navigate relationship challenges with clarity and confidence.',
    heroPromise: 'Trusted guidance for relationship healing — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Feeling stuck in recurring arguments',
      'Lack of communication and understanding',
      'Doubts about the future of the relationship',
      'Emotional distress and conflict'
    ],
    journeyOutcomes: [
      'Gain a deeper understanding of relationship dynamics.',
      'Develop effective communication strategies.',
      'Resolve conflicts constructively.',
      'Feel more secure and connected in your relationship.'
    ],
    tierCards: {
      Focussed: { priceInr: 6999, durationWeeks: 8 },
      Supported: { priceInr: 8999, durationWeeks: 8 },
      Comprehensive: { priceInr: 10999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 x 60-min video call',
        asyncChat: '7 days',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'What is driving it right now (key planets/houses)',
          'What outcome is most likely if nothing changes',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One good window + one avoid window (high-level)',
          'One clear next step to reduce confusion immediately',
          '1 follow-up check-in (async) to clarify doubts'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions (1x60-min, 2x30-min follow-ups)',
        asyncChat: '8 weeks',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          'Two likely paths + trade-offs (no hype)',
          'How your tendencies affect decisions in this area',
          '8–12 week timeline with key turning points',
          'Best time to act + best time to wait (with reason)',
          'Unlimited chat with astrologer for the full pack duration',
          '2 follow-ups to refine guidance as things unfold'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '5 sessions (2x60-min, 3x30-min follow-ups)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'What aligns vs what will drain you (decision confidence)',
          'What needs to change internally for outcomes to improve',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Multiple action windows (primary + backup) with risk notes',
          'Unlimited chat + priority response in critical moments',
          'More follow-ups so guidance stays relevant as reality changes'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Relationship harmony pooja', description: 'Booking + coordination', type: 'pooja' },
      { name: 'Stress + sleep kit', description: 'Delivered to your door', type: 'kit' },
      { name: '1:1 healing session', description: 'Sound/energy healer booking', type: 'session' }
    ],
    faqs: [
      { q: 'Is Mira free to use?', a: 'Yes. Mira is free and available anytime. Packages add human astrologer support and done-for-you remedies.' },
      { q: 'How fast will I get responses?', a: 'Within 24 hours for Supported and Comprehensive. Focussed includes a short follow-up window.' },
      { q: 'Is there a refund?', a: 'Yes — no questions asked 7-day full refund guarantee.' }
    ]
  },

  'family-relationships': {
    slug: 'family-relationships',
    category: 'Love',
    subTopic: 'Family Relationships',
    headline: 'Family Relationship Guidance',
    subHeadline: 'Foster harmony and understanding in your family dynamics.',
    heroPromise: 'Trusted guidance for family relationships — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Intergenerational conflicts',
      'Communication breakdowns within the family',
      'Navigating difficult family members',
      'Desire for stronger family bonds'
    ],
    journeyOutcomes: [
      'Improve communication with family members.',
      'Resolve family disputes effectively.',
      'Create a more peaceful and supportive home environment.',
      'Strengthen your connection with loved ones.'
    ],
    tierCards: {
      Focussed: { priceInr: 5999, durationWeeks: 8 },
      Supported: { priceInr: 7999, durationWeeks: 8 },
      Comprehensive: { priceInr: 9999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 x 60-min video call',
        asyncChat: '7 days',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'What is driving it right now (key planets/houses)',
          'What outcome is most likely if nothing changes',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One good window + one avoid window (high-level)',
          'One clear next step to reduce confusion immediately',
          '1 follow-up check-in (async) to clarify doubts'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions (1x60-min, 2x30-min follow-ups)',
        asyncChat: '8 weeks',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          'Two likely paths + trade-offs (no hype)',
          'How your tendencies affect decisions in this area',
          '8–12 week timeline with key turning points',
          'Best time to act + best time to wait (with reason)',
          'Unlimited chat with astrologer for the full pack duration',
          '2 follow-ups to refine guidance as things unfold'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '5 sessions (2x60-min, 3x30-min follow-ups)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'What aligns vs what will drain you (decision confidence)',
          'What needs to change internally for outcomes to improve',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Multiple action windows (primary + backup) with risk notes',
          'Unlimited chat + priority response in critical moments',
          'More follow-ups so guidance stays relevant as reality changes'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Home harmony pooja', description: 'Booking + coordination', type: 'pooja' },
      { name: 'Protection kit', description: 'Reduce negativity/conflict', type: 'kit' },
      { name: 'Gemstone sourcing', description: 'Calm/communication support', type: 'gemstone' }
    ],
    faqs: [
      { q: 'Is Mira free to use?', a: 'Yes. Mira is free and available anytime. Packages add human astrologer support and done-for-you remedies.' },
      { q: 'How fast will I get responses?', a: 'Within 24 hours for Supported and Comprehensive. Focussed includes a short follow-up window.' },
      { q: 'Is there a refund?', a: 'Yes — no questions asked 7-day full refund guarantee.' }
    ]
  },

  'dating-compatibility': {
    slug: 'dating-compatibility',
    category: 'Love',
    subTopic: 'Dating & Compatibility',
    headline: 'Dating & Compatibility Insights',
    subHeadline: 'Understand your compatibility and make informed dating choices.',
    heroPromise: 'Trusted guidance for dating & compatibility — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Uncertainty about potential partners',
      'Difficulty finding the right match',
      'Concerns about long-term compatibility',
      'Repeating negative dating patterns'
    ],
    journeyOutcomes: [
      'Gain clarity on your relationship needs and preferences.',
      'Understand compatibility with potential partners.',
      'Navigate the dating world with more confidence.',
      'Build healthier and more fulfilling relationships.'
    ],
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 x 60-min video call',
        asyncChat: '7 days',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'What is driving it right now (key planets/houses)',
          'What outcome is most likely if nothing changes',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One good window + one avoid window (high-level)',
          'One clear next step to reduce confusion immediately',
          '1 follow-up check-in (async) to clarify doubts'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions (1x60-min, 2x30-min follow-ups)',
        asyncChat: '8 weeks',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          'Two likely paths + trade-offs (no hype)',
          'How your tendencies affect decisions in this area',
          '8–12 week timeline with key turning points',
          'Best time to act + best time to wait (with reason)',
          'Unlimited chat with astrologer for the full pack duration',
          '2 follow-ups to refine guidance as things unfold'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '5 sessions (2x60-min, 3x30-min follow-ups)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'What aligns vs what will drain you (decision confidence)',
          'What needs to change internally for outcomes to improve',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Multiple action windows (primary + backup) with risk notes',
          'Unlimited chat + priority response in critical moments',
          'More follow-ups so guidance stays relevant as reality changes'
        ]
      }
    },
    toolsIncluded: ['Kundli Matching Snapshot (8 points + real-life fit lens)'],
    optionalRemedies: [
      { name: 'Confidence gemstone', description: 'Sourcing + delivery (attraction support)', type: 'gemstone' },
      { name: 'Personal protection kit', description: 'Evil-eye/calm protection', type: 'kit' },
      { name: '1:1 tarot clarity session', description: 'Mini-session booking (add-on)', type: 'session' }
    ],
    faqs: [
      { q: 'Is Mira free to use?', a: 'Yes. Mira is free and available anytime. Packages add human astrologer support and done-for-you remedies.' },
      { q: 'How fast will I get responses?', a: 'Within 24 hours for Supported and Comprehensive. Focussed includes a short follow-up window.' },
      { q: 'Is there a refund?', a: 'Yes — no questions asked 7-day full refund guarantee.' }
    ]
  },

  'marriage-planning': {
    slug: 'marriage-planning',
    category: 'Love',
    subTopic: 'Marriage Planning',
    headline: 'Marriage Planning Guidance',
    subHeadline: 'Ensure a harmonious and auspicious start to your married life.',
    heroPromise: 'Trusted guidance for marriage planning — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Concerns about astrological compatibility for marriage',
      'Finding the right wedding date (muhurat)',
      'Pre-marital stress and anxieties',
      'Navigating family expectations'
    ],
    journeyOutcomes: [
      'Gain confidence in your marriage compatibility.',
      'Secure auspicious wedding dates.',
      'Reduce pre-marital stress and anxiety.',
      'Build a strong foundation for a lasting marriage.'
    ],
    tierCards: {
      Focussed: { priceInr: 7999, durationWeeks: 12 },
      Supported: { priceInr: 9999, durationWeeks: 12 },
      Comprehensive: { priceInr: 11999, durationWeeks: 12 }
    },
    featuresByTier: {
      Focussed: {
        duration: '12 weeks',
        consultations: '1 x 60-min video call',
        asyncChat: '7 days',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'What is driving it right now (key planets/houses)',
          'What outcome is most likely if nothing changes',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One good window + one avoid window (high-level)',
          'One clear next step to reduce confusion immediately',
          '1 follow-up check-in (async) to clarify doubts'
        ]
      },
      Supported: {
        duration: '12 weeks',
        consultations: '3 sessions (1x60-min, 2x30-min follow-ups)',
        asyncChat: '12 weeks',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          'Two likely paths + trade-offs (no hype)',
          'How your tendencies affect decisions in this area',
          '8–12 week timeline with key turning points',
          'Best time to act + best time to wait (with reason)',
          'Unlimited chat with astrologer for the full pack duration',
          '2 follow-ups to refine guidance as things unfold'
        ]
      },
      Comprehensive: {
        duration: '12 weeks',
        consultations: '5 sessions (2x60-min, 3x30-min follow-ups)',
        asyncChat: '12 weeks (priority)',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'What aligns vs what will drain you (decision confidence)',
          'What needs to change internally for outcomes to improve',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Multiple action windows (primary + backup) with risk notes',
          'Unlimited chat + priority response in critical moments',
          'More follow-ups so guidance stays relevant as reality changes'
        ]
      }
    },
    toolsIncluded: ['Kundli Matching Snapshot (8 points + real-life fit lens)'],
    optionalRemedies: [
      { name: 'Vivah Shanti Pooja', description: 'Booking + end-to-end coordination', type: 'pooja' },
      { name: 'Gemstone sourcing', description: 'Stability/compatibility focus', type: 'gemstone' },
      { name: 'Couple harmony ritual set', description: 'Delivered (optional)', type: 'kit' }
    ],
    faqs: [
      { q: 'Is Mira free to use?', a: 'Yes. Mira is free and available anytime. Packages add human astrologer support and done-for-you remedies.' },
      { q: 'How fast will I get responses?', a: 'Within 24 hours for Supported and Comprehensive. Focussed includes a short follow-up window.' },
      { q: 'Is there a refund?', a: 'Yes — no questions asked 7-day full refund guarantee.' }
    ]
  },

  'communication-trust': {
    slug: 'communication-trust',
    category: 'Love',
    subTopic: 'Communication & Trust',
    headline: 'Communication & Trust',
    subHeadline: 'Get clear, grounded guidance to rebuild trust, reduce overthinking, and communicate without spiraling. Talk to a verified astrologer on call + chat until you feel steady and sure about where this relationship is headed.',
    heroPromise: 'Trusted guidance for communication & trust — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Understand why trust feels shaky right now',
      'Know what is a phase vs a pattern',
      'Identify the next 2–3 weeks\' emotional climate'
    ],
    journeyOutcomes: [
      'Clear timeline for stability vs volatility',
      'What conversations to have now vs later',
      'Confidence on whether to repair, pause, or redefine',
      'Two-perspective clarity (logic + intuition)',
      'Root cause behind repeated triggers',
      'Strongest confidence on long-term viability'
    ],
    tierCards: {
      Focussed: { priceInr: 5999, durationWeeks: 8 },
      Supported: { priceInr: 7999, durationWeeks: 8 },
      Comprehensive: { priceInr: 9999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call + 3 follow-up chats (48h response) + 1 final clarity note',
        asyncChat: '48h response',
        outcomes: [
          'Understand why trust feels shaky right now',
          'Know what is a phase vs a pattern',
          'Identify the next 2–3 weeks\' emotional climate'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls + unlimited chat with astrologer (priority response)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Clear timeline for stability vs volatility',
          'What conversations to have now vs later',
          'Confidence on whether to repair, pause, or redefine'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '2 expert calls (Vedic + Tarot) + 3 follow-up calls + unlimited chat + cross-verified reading',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Two-perspective clarity (logic + intuition)',
          'Root cause behind repeated triggers',
          'Strongest confidence on long-term viability'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Relationship harmony gemstone', description: 'Delivered to your door', type: 'gemstone' },
      { name: 'Personal protection charm/bracelet', description: 'Delivered', type: 'kit' },
      { name: 'Shanti pooja for peace & stability', description: 'Booked + supported', type: 'pooja' },
      { name: 'Calming wellness kit', description: 'Sleep + anxiety support (delivered)', type: 'kit' }
    ],
    faqs: [
      { q: 'Will you tell me if this relationship will last?', a: 'We provide clarity on patterns and timing, not guarantees. You make the final call.' },
      { q: 'Can I ask unlimited follow-ups?', a: 'Supported and Comprehensive include unlimited chat. Focussed has structured follow-ups.' },
      { q: 'What if I\'m not sure what to ask?', a: 'Your astrologer will guide you through the right questions.' },
      { q: 'What if my partner\'s birth details aren\'t available?', a: 'We can still provide insights based on your chart alone.' },
      { q: 'Is this therapy?', a: 'No, this is astrological guidance. For clinical issues, please consult a therapist.' },
      { q: 'How fast do I get responses?', a: 'Within 24-48 hours depending on your pack.' },
      { q: 'What if I want a second opinion?', a: 'Comprehensive includes two expert perspectives.' },
      { q: 'How does the 7-day refund work?', a: 'Full refund if you\'re not satisfied, no questions asked.' }
    ]
  },

  'breakup-closure': {
    slug: 'breakup-closure',
    category: 'Love',
    subTopic: 'Breakup & Closure',
    headline: 'Breakup & Closure',
    subHeadline: 'Move from confusion to closure — with clear timelines, emotional grounding, and the confidence to let go or reconnect wisely. Get astrological guidance for what ended, what\'s next, and how to protect your peace while you heal.',
    heroPromise: 'Trusted guidance for breakup & closure — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'What this breakup was meant to teach',
      'How long the heavy phase may last',
      'Whether reconnection is likely or not'
    ],
    journeyOutcomes: [
      'Clear \'no-contact vs conversation\' timing',
      'Emotional stability plan for the next month',
      'Confidence to stop looping on "what if"',
      'Cross-verified clarity on reconnection vs closure',
      'Why you attract similar patterns',
      'Strongest confidence on your next relationship chapter'
    ],
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call + 3 follow-up chats + 1 closure summary',
        asyncChat: '48h response',
        outcomes: [
          'What this breakup was meant to teach',
          'How long the heavy phase may last',
          'Whether reconnection is likely or not'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls + unlimited chat (priority)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Clear \'no-contact vs conversation\' timing',
          'Emotional stability plan for the next month',
          'Confidence to stop looping on "what if"'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '2 expert calls (Vedic + Tarot) + 3 follow-up calls + unlimited chat + pattern decoding',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Cross-verified clarity on reconnection vs closure',
          'Why you attract similar patterns',
          'Strongest confidence on your next relationship chapter'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Heart-healing gemstone', description: 'Delivered to your door', type: 'gemstone' },
      { name: 'Emotional protection bracelet', description: 'Delivered', type: 'kit' },
      { name: 'Shanti/closure pooja', description: 'Booked + supported', type: 'pooja' },
      { name: 'Mood & sleep wellness kit', description: 'Delivered', type: 'kit' }
    ],
    faqs: [
      { q: 'Will you predict if they\'ll come back?', a: 'We provide timing insights and probabilities, not guarantees.' },
      { q: 'Can you guide me if I\'m still talking to them?', a: 'Yes, we help you navigate ongoing communication.' },
      { q: 'How do follow-ups work?', a: 'Chat or call-based depending on your pack.' },
      { q: 'Can I do this without birth time?', a: 'Yes, we can work with approximate time or date only.' },
      { q: 'What if I feel triggered again?', a: 'You can reach out through chat anytime during your pack.' },
      { q: 'Is Tarot included?', a: 'Comprehensive includes both Vedic and Tarot perspectives.' },
      { q: 'What if I want privacy?', a: 'All conversations are confidential and encrypted.' },
      { q: 'Refund policy?', a: '7-day full refund, no questions asked.' }
    ]
  }
};

// ==========================================
// CAREER SUB-TOPICS (6)
// ==========================================

export const CAREER_SUBTOPICS = {
  'career-clarity': {
    slug: 'career-clarity',
    category: 'Career',
    subTopic: 'Career Clarity',
    headline: 'Career Clarity Guidance',
    subHeadline: 'Discover your ideal career path and unlock your professional potential.',
    heroPromise: 'Trusted guidance for career clarity — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Feeling unfulfilled in your current job',
      'Uncertainty about career choices',
      'Lack of direction in your professional life',
      'Desire for a more meaningful career'
    ],
    journeyOutcomes: [
      'Identify your strengths and passions for career alignment.',
      'Gain clarity on potential career paths.',
      'Make confident decisions about your professional future.',
      'Find greater satisfaction and purpose in your work.'
    ],
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 x 60-min video call',
        asyncChat: '7 days',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'What is driving it right now (key planets/houses)',
          'What outcome is most likely if nothing changes',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One good window + one avoid window (high-level)',
          'One clear next step to reduce confusion immediately',
          '1 follow-up check-in (async) to clarify doubts'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions (1x60-min, 2x30-min follow-ups)',
        asyncChat: '8 weeks',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          'Two likely paths + trade-offs (no hype)',
          'How your tendencies affect decisions in this area',
          '8–12 week timeline with key turning points',
          'Best time to act + best time to wait (with reason)',
          'Unlimited chat with astrologer for the full pack duration',
          '2 follow-ups to refine guidance as things unfold'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '5 sessions (2x60-min, 3x30-min follow-ups)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'What aligns vs what will drain you (decision confidence)',
          'What needs to change internally for outcomes to improve',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Multiple action windows (primary + backup) with risk notes',
          'Unlimited chat + priority response in critical moments',
          'More follow-ups so guidance stays relevant as reality changes'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Gemstone sourcing', description: 'Confidence/authority stone + delivery', type: 'gemstone' },
      { name: '1:1 tarot clarity session', description: 'Decision focus mini-session', type: 'session' },
      { name: 'Prosperity + focus kit', description: 'Delivered', type: 'kit' }
    ],
    faqs: [
      { q: 'Is Mira free to use?', a: 'Yes. Mira is free and available anytime. Packages add human astrologer support and done-for-you remedies.' },
      { q: 'How fast will I get responses?', a: 'Within 24 hours for Supported and Comprehensive. Focussed includes a short follow-up window.' },
      { q: 'Is there a refund?', a: 'Yes — no questions asked 7-day full refund guarantee.' }
    ]
  },

  'job-transition': {
    slug: 'job-transition',
    category: 'Career',
    subTopic: 'Job Transition',
    headline: 'Job Transition Support',
    subHeadline: 'Navigate your career change with confidence and strategic planning.',
    heroPromise: 'Trusted guidance for job transition — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Anxiety about leaving a current job',
      'Uncertainty about the job search process',
      'Fear of making the wrong career move',
      'Difficulty finding a suitable new role'
    ],
    journeyOutcomes: [
      'Identify the best timing for a job transition.',
      'Develop a strategic approach to your job search.',
      'Gain confidence in your career move.',
      'Secure a fulfilling new role that aligns with your goals.'
    ],
    tierCards: {
      Focussed: { priceInr: 7999, durationWeeks: 12 },
      Supported: { priceInr: 9999, durationWeeks: 12 },
      Comprehensive: { priceInr: 11999, durationWeeks: 12 }
    },
    featuresByTier: {
      Focussed: {
        duration: '12 weeks',
        consultations: '1 x 60-min video call',
        asyncChat: '7 days',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'What is driving it right now (key planets/houses)',
          'What outcome is most likely if nothing changes',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One good window + one avoid window (high-level)',
          'One clear next step to reduce confusion immediately',
          '1 follow-up check-in (async) to clarify doubts'
        ]
      },
      Supported: {
        duration: '12 weeks',
        consultations: '3 sessions (1x60-min, 2x30-min follow-ups)',
        asyncChat: '12 weeks',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          'Two likely paths + trade-offs (no hype)',
          'How your tendencies affect decisions in this area',
          '8–12 week timeline with key turning points',
          'Best time to act + best time to wait (with reason)',
          'Unlimited chat with astrologer for the full pack duration',
          '2 follow-ups to refine guidance as things unfold'
        ]
      },
      Comprehensive: {
        duration: '12 weeks',
        consultations: '5 sessions (2x60-min, 3x30-min follow-ups)',
        asyncChat: '12 weeks (priority)',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'What aligns vs what will drain you (decision confidence)',
          'What needs to change internally for outcomes to improve',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Multiple action windows (primary + backup) with risk notes',
          'Unlimited chat + priority response in critical moments',
          'More follow-ups so guidance stays relevant as reality changes'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Obstacle-removal pooja', description: 'Booking + coordination (optional)', type: 'pooja' },
      { name: 'Gemstone sourcing', description: 'Stability/confidence stone + delivery', type: 'gemstone' },
      { name: 'Interview confidence kit', description: 'Delivered', type: 'kit' }
    ],
    faqs: [
      { q: 'Is Mira free to use?', a: 'Yes. Mira is free and available anytime. Packages add human astrologer support and done-for-you remedies.' },
      { q: 'How fast will I get responses?', a: 'Within 24 hours for Supported and Comprehensive. Focussed includes a short follow-up window.' },
      { q: 'Is there a refund?', a: 'Yes — no questions asked 7-day full refund guarantee.' }
    ]
  },

  'money-stability': {
    slug: 'money-stability',
    category: 'Career',
    subTopic: 'Money Stability',
    headline: 'Financial Stability Guidance',
    subHeadline: 'Achieve greater financial security and abundance.',
    heroPromise: 'Trusted guidance for money stability — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Financial instability and debt',
      'Struggles with income generation',
      'Anxiety about future financial security',
      'Difficulty in managing finances effectively'
    ],
    journeyOutcomes: [
      'Identify patterns affecting your financial well-being.',
      'Develop strategies for income growth and stability.',
      'Reduce financial anxiety and build confidence.',
      'Create a path towards long-term financial abundance.'
    ],
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 4 },
      Comprehensive: { priceInr: 6999, durationWeeks: 4 }
    },
    featuresByTier: {
      Focussed: {
        duration: '4 weeks',
        consultations: '1 x 60-min video call',
        asyncChat: '7 days',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'What is driving it right now (key planets/houses)',
          'What outcome is most likely if nothing changes',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One good window + one avoid window (high-level)',
          'One clear next step to reduce confusion immediately',
          '1 follow-up check-in (async) to clarify doubts'
        ]
      },
      Supported: {
        duration: '4 weeks',
        consultations: '3 sessions (1x60-min, 2x30-min follow-ups)',
        asyncChat: '4 weeks',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          'Two likely paths + trade-offs (no hype)',
          'How your tendencies affect decisions in this area',
          '8–12 week timeline with key turning points',
          'Best time to act + best time to wait (with reason)',
          'Unlimited chat with astrologer for the full pack duration',
          '2 follow-ups to refine guidance as things unfold'
        ]
      },
      Comprehensive: {
        duration: '4 weeks',
        consultations: '5 sessions (2x60-min, 3x30-min follow-ups)',
        asyncChat: '4 weeks (priority)',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'What aligns vs what will drain you (decision confidence)',
          'What needs to change internally for outcomes to improve',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Multiple action windows (primary + backup) with risk notes',
          'Unlimited chat + priority response in critical moments',
          'More follow-ups so guidance stays relevant as reality changes'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Prosperity kit', description: 'Wallet/home items delivered', type: 'kit' },
      { name: 'Gemstone sourcing', description: 'Abundance/protection stone + delivery', type: 'gemstone' },
      { name: 'Lakshmi ritual service', description: 'Simple booking (optional)', type: 'pooja' }
    ],
    faqs: [
      { q: 'Is Mira free to use?', a: 'Yes. Mira is free and available anytime. Packages add human astrologer support and done-for-you remedies.' },
      { q: 'How fast will I get responses?', a: 'Within 24 hours for Supported and Comprehensive. Focussed includes a short follow-up window.' },
      { q: 'Is there a refund?', a: 'Yes — no questions asked 7-day full refund guarantee.' }
    ]
  },

  'work-stress': {
    slug: 'work-stress',
    category: 'Career',
    subTopic: 'Work Stress',
    headline: 'Work Stress',
    subHeadline: 'Get calm clarity on what\'s draining you at work — and how long this pressure phase is likely to last. Understand your current career cycle, stress triggers, and the best timing to push, pause, or change lanes.',
    heroPromise: 'Trusted guidance for work stress — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Identify chart-based stress triggers',
      'Know if this is temporary or structural',
      'Understand the next 4–6 weeks\' intensity'
    ],
    journeyOutcomes: [
      'Clear \'survive vs switch\' timing window',
      'What to avoid to reduce conflict',
      'Confidence on boundaries + next step',
      'Cross-verified timeline for peak stress → relief',
      'Root pattern behind work pressure',
      'Strongest confidence on change vs stay decision'
    ],
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call + 3 follow-up chats + 1 stress-phase summary',
        asyncChat: '48h response',
        outcomes: [
          'Identify chart-based stress triggers',
          'Know if this is temporary or structural',
          'Understand the next 4–6 weeks\' intensity'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls + unlimited chat (priority)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Clear \'survive vs switch\' timing window',
          'What to avoid to reduce conflict',
          'Confidence on boundaries + next step'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '2 expert calls (Vedic + Numerology) + 3 follow-up calls + unlimited chat + burnout timeline check',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Cross-verified timeline for peak stress → relief',
          'Root pattern behind work pressure',
          'Strongest confidence on change vs stay decision'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Focus & grounding gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Work-stability protection charm', description: 'Delivered', type: 'kit' },
      { name: 'Obstacle-removal pooja', description: 'Booked + supported', type: 'pooja' },
      { name: 'Sleep + recovery wellness kit', description: 'Delivered', type: 'kit' }
    ],
    faqs: [
      { q: 'Is this medical advice?', a: 'No, this is astrological guidance. Please consult a doctor for medical issues.' },
      { q: 'Can astrology really help stress?', a: 'It helps identify timing patterns and root causes, which brings clarity.' },
      { q: 'How fast do responses come?', a: 'Within 24-48 hours depending on your pack.' },
      { q: 'Can you guide job switch timing?', a: 'Yes, timing guidance is a core part of what we provide.' },
      { q: 'What if I can\'t share workplace details?', a: 'We work with what you\'re comfortable sharing.' },
      { q: 'Is Numerology included?', a: 'Comprehensive includes multiple expert perspectives.' },
      { q: 'Refund?', a: '7-day full refund, no questions asked.' },
      { q: 'What happens after purchase?', a: 'You\'ll get matched with an expert within 24 hours.' }
    ]
  },

  'office-politics': {
    slug: 'office-politics',
    category: 'Career',
    subTopic: 'Office Politics',
    headline: 'Office Politics',
    subHeadline: 'Understand hidden dynamics, protect your reputation, and time your moves wisely — without overreacting. Get chart-based clarity on power dynamics, conflict cycles, and the safest way forward in your workplace.',
    heroPromise: 'Trusted guidance for office politics — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Know what to ignore vs address',
      'Identify high-risk days/weeks for conflict',
      'Understand who to trust (and how much)'
    ],
    journeyOutcomes: [
      'Clear timing for asking, negotiating, escalating',
      'Confidence on how to respond (not react)',
      'Stronger protection for reputation + role stability',
      'Two-perspective view on intent + outcome',
      'Root pattern behind recurring conflict',
      'Strongest confidence on stay/exit timeline'
    ],
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call + 3 follow-up chats + 1 clarity summary',
        asyncChat: '48h response',
        outcomes: [
          'Know what to ignore vs address',
          'Identify high-risk days/weeks for conflict',
          'Understand who to trust (and how much)'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls + unlimited chat (priority)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Clear timing for asking, negotiating, escalating',
          'Confidence on how to respond (not react)',
          'Stronger protection for reputation + role stability'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '2 expert calls (Vedic + Tarot) + 3 follow-up calls + unlimited chat + cross-verified dynamics reading',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Two-perspective view on intent + outcome',
          'Root pattern behind recurring conflict',
          'Strongest confidence on stay/exit timeline'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Protection + grounding gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Workplace shield kit', description: 'Delivered', type: 'kit' },
      { name: 'Shanti pooja for peace', description: 'Booked + supported', type: 'pooja' }
    ],
    faqs: [
      { q: 'Will you take sides?', a: 'No, we provide objective clarity on dynamics and timing.' },
      { q: 'Can you tell me who\'s against me?', a: 'We help you understand patterns, not point fingers.' },
      { q: 'Is this confidential?', a: 'Yes, all conversations are private and encrypted.' },
      { q: 'How do follow-ups work?', a: 'Chat or call-based depending on your pack.' },
      { q: 'What if things escalate?', a: 'You can reach out anytime during your pack period.' },
      { q: 'Is Tarot included?', a: 'Comprehensive includes multiple expert perspectives.' },
      { q: 'Refund?', a: '7-day full refund, no questions asked.' },
      { q: 'Response time?', a: 'Within 24-48 hours depending on your pack.' }
    ]
  },

  'big-decision-timing': {
    slug: 'big-decision-timing',
    category: 'Career',
    subTopic: 'Big Decision Timing',
    headline: 'Big Decision Timing',
    subHeadline: 'Know when to accept an offer, make a big move, or pause — based on chart-backed timing, not just gut feel. Best for people stuck between options, waiting for the "right time," or afraid of missing a window.',
    heroPromise: 'Trusted guidance for big decision timing — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Identify your next action window',
      'Know which weeks to avoid',
      'Feel confident about timing, not impulse'
    ],
    journeyOutcomes: [
      'Clear sequencing: what to do first vs later',
      'Confidence on acceptance/exit decisions',
      'Reduced anxiety around "wrong timing"',
      'Cross-verified timing window',
      'Why you\'re stuck in indecision',
      'Strongest confidence on big moves'
    ],
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 4 },
      Comprehensive: { priceInr: 6999, durationWeeks: 4 }
    },
    featuresByTier: {
      Focussed: {
        duration: '4 weeks',
        consultations: '1× 30-min astrologer call + 2 follow-up chats + 1 timing note',
        asyncChat: '48h response',
        outcomes: [
          'Identify your next action window',
          'Know which weeks to avoid',
          'Feel confident about timing, not impulse'
        ]
      },
      Supported: {
        duration: '4 weeks',
        consultations: '1× 45-min call + 1× 20-min follow-up call + unlimited chat (priority)',
        asyncChat: '4 weeks (priority)',
        outcomes: [
          'Clear sequencing: what to do first vs later',
          'Confidence on acceptance/exit decisions',
          'Reduced anxiety around "wrong timing"'
        ]
      },
      Comprehensive: {
        duration: '4 weeks',
        consultations: '2 expert calls (Vedic + Numerology) + 2 follow-up calls + unlimited chat',
        asyncChat: '4 weeks (priority)',
        outcomes: [
          'Cross-verified timing window',
          'Why you\'re stuck in indecision',
          'Strongest confidence on big moves'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Confidence gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Prosperity charm', description: 'Delivered', type: 'kit' },
      { name: 'Obstacle-removal pooja', description: 'Booked + supported', type: 'pooja' }
    ],
    faqs: [
      { q: 'Will you guarantee success?', a: 'We provide clarity on timing, not outcome guarantees.' },
      { q: 'Can you help choose between 2 options?', a: 'Yes, we help you see the timing and trade-offs for each.' },
      { q: 'Unlimited chat included?', a: 'Supported and Comprehensive include unlimited chat.' },
      { q: 'What if dates change?', a: 'We can provide updated timing guidance.' },
      { q: 'Can I do this without birth time?', a: 'Yes, we can work with approximate time.' },
      { q: 'What if I\'m still unsure?', a: 'We work with you until you feel clear.' },
      { q: 'Refund?', a: '7-day full refund, no questions asked.' },
      { q: 'How fast is the turnaround?', a: 'Expert matching within 24 hours.' }
    ]
  }
};

// ==========================================
// HEALTH SUB-TOPICS (6)
// ==========================================

export const HEALTH_SUBTOPICS = {
  'healing-journey': {
    slug: 'healing-journey',
    category: 'Health',
    subTopic: 'Healing Journey',
    headline: 'Healing Journey Support',
    subHeadline: 'Embark on a healing path with astrological insights and support.',
    heroPromise: 'Trusted guidance for healing journey — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Struggling with physical or emotional ailments',
      'Feeling overwhelmed by health challenges',
      'Seeking complementary support for healing',
      'Desire for improved well-being'
    ],
    journeyOutcomes: [
      'Understand astrological influences on your health.',
      'Identify optimal timings for healing practices.',
      'Receive guidance to support your recovery.',
      'Empower your healing journey with clarity and positivity.'
    ],
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 x 60-min video call',
        asyncChat: '7 days',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'What is driving it right now (key planets/houses)',
          'What outcome is most likely if nothing changes',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One good window + one avoid window (high-level)',
          'One clear next step to reduce confusion immediately',
          '1 follow-up check-in (async) to clarify doubts'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions (1x60-min, 2x30-min follow-ups)',
        asyncChat: '8 weeks',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          'Two likely paths + trade-offs (no hype)',
          'How your tendencies affect decisions in this area',
          '8–12 week timeline with key turning points',
          'Best time to act + best time to wait (with reason)',
          'Unlimited chat with astrologer for the full pack duration',
          '2 follow-ups to refine guidance as things unfold'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '5 sessions (2x60-min, 3x30-min follow-ups)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'What aligns vs what will drain you (decision confidence)',
          'What needs to change internally for outcomes to improve',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Multiple action windows (primary + backup) with risk notes',
          'Unlimited chat + priority response in critical moments',
          'More follow-ups so guidance stays relevant as reality changes'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Stress + sleep kit', description: 'Delivered', type: 'kit' },
      { name: 'Natural wellness consult', description: 'Ayurveda/Naturopathy booking', type: 'session' },
      { name: 'Shanti pooja', description: 'Booking + coordination (optional)', type: 'pooja' }
    ],
    faqs: [
      { q: 'Is Mira free to use?', a: 'Yes. Mira is free and available anytime. Packages add human astrologer support and done-for-you remedies.' },
      { q: 'How fast will I get responses?', a: 'Within 24 hours for Supported and Comprehensive. Focussed includes a short follow-up window.' },
      { q: 'Is there a refund?', a: 'Yes — no questions asked 7-day full refund guarantee.' }
    ]
  },

  'stress-management': {
    slug: 'stress-management',
    category: 'Health',
    subTopic: 'Stress Management',
    headline: 'Stress Management Guidance',
    subHeadline: 'Find balance and peace with personalized stress management strategies.',
    heroPromise: 'Trusted guidance for stress management — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Feeling overwhelmed by daily stress',
      'Difficulty sleeping or relaxing',
      'Impact of stress on physical and mental health',
      'Desire for greater inner calm'
    ],
    journeyOutcomes: [
      'Understand the astrological roots of your stress.',
      'Develop effective coping mechanisms for stress.',
      'Improve sleep quality and relaxation.',
      'Cultivate a sense of inner peace and balance.'
    ],
    tierCards: {
      Focussed: { priceInr: 7999, durationWeeks: 12 },
      Supported: { priceInr: 9999, durationWeeks: 12 },
      Comprehensive: { priceInr: 11999, durationWeeks: 12 }
    },
    featuresByTier: {
      Focussed: {
        duration: '12 weeks',
        consultations: '1 x 60-min video call',
        asyncChat: '7 days',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'What is driving it right now (key planets/houses)',
          'What outcome is most likely if nothing changes',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One good window + one avoid window (high-level)',
          'One clear next step to reduce confusion immediately',
          '1 follow-up check-in (async) to clarify doubts'
        ]
      },
      Supported: {
        duration: '12 weeks',
        consultations: '3 sessions (1x60-min, 2x30-min follow-ups)',
        asyncChat: '12 weeks',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          'Two likely paths + trade-offs (no hype)',
          'How your tendencies affect decisions in this area',
          '8–12 week timeline with key turning points',
          'Best time to act + best time to wait (with reason)',
          'Unlimited chat with astrologer for the full pack duration',
          '2 follow-ups to refine guidance as things unfold'
        ]
      },
      Comprehensive: {
        duration: '12 weeks',
        consultations: '5 sessions (2x60-min, 3x30-min follow-ups)',
        asyncChat: '12 weeks (priority)',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'What aligns vs what will drain you (decision confidence)',
          'What needs to change internally for outcomes to improve',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Multiple action windows (primary + backup) with risk notes',
          'Unlimited chat + priority response in critical moments',
          'More follow-ups so guidance stays relevant as reality changes'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Deep sleep kit', description: 'Premium kit delivered', type: 'kit' },
      { name: 'Natural wellness consult', description: 'Booking', type: 'session' },
      { name: 'Mental peace pooja', description: 'Booking + coordination (optional)', type: 'pooja' }
    ],
    faqs: [
      { q: 'Is Mira free to use?', a: 'Yes. Mira is free and available anytime. Packages add human astrologer support and done-for-you remedies.' },
      { q: 'How fast will I get responses?', a: 'Within 24 hours for Supported and Comprehensive. Focussed includes a short follow-up window.' },
      { q: 'Is there a refund?', a: 'Yes — no questions asked 7-day full refund guarantee.' }
    ]
  },

  'energy-balance': {
    slug: 'energy-balance',
    category: 'Health',
    subTopic: 'Energy & Balance',
    headline: 'Energy & Balance Guidance',
    subHeadline: 'Restore your vitality and achieve a harmonious state of being.',
    heroPromise: 'Trusted guidance for energy & balance — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Low energy levels and fatigue',
      'Feeling unbalanced and out of sync',
      'Difficulty maintaining physical and mental equilibrium',
      'Desire for renewed vitality'
    ],
    journeyOutcomes: [
      'Understand astrological influences on your energy levels.',
      'Identify practices to restore balance and vitality.',
      'Develop strategies for sustained energy and well-being.',
      'Feel more vibrant, centered, and harmonious.'
    ],
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 x 60-min video call',
        asyncChat: '7 days',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'What is driving it right now (key planets/houses)',
          'What outcome is most likely if nothing changes',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One good window + one avoid window (high-level)',
          'One clear next step to reduce confusion immediately',
          '1 follow-up check-in (async) to clarify doubts'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions (1x60-min, 2x30-min follow-ups)',
        asyncChat: '8 weeks',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          'Two likely paths + trade-offs (no hype)',
          'How your tendencies affect decisions in this area',
          '8–12 week timeline with key turning points',
          'Best time to act + best time to wait (with reason)',
          'Unlimited chat with astrologer for the full pack duration',
          '2 follow-ups to refine guidance as things unfold'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '5 sessions (2x60-min, 3x30-min follow-ups)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'What aligns vs what will drain you (decision confidence)',
          'What needs to change internally for outcomes to improve',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Multiple action windows (primary + backup) with risk notes',
          'Unlimited chat + priority response in critical moments',
          'More follow-ups so guidance stays relevant as reality changes'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Vitality kit', description: 'D2C energy wellness kit delivered', type: 'kit' },
      { name: 'Natural wellness consult', description: 'Booking', type: 'session' },
      { name: 'Gemstone sourcing', description: 'Energy/confidence stone + delivery', type: 'gemstone' }
    ],
    faqs: [
      { q: 'Is Mira free to use?', a: 'Yes. Mira is free and available anytime. Packages add human astrologer support and done-for-you remedies.' },
      { q: 'How fast will I get responses?', a: 'Within 24 hours for Supported and Comprehensive. Focussed includes a short follow-up window.' },
      { q: 'Is there a refund?', a: 'Yes — no questions asked 7-day full refund guarantee.' }
    ]
  },

  'sleep-reset': {
    slug: 'sleep-reset',
    category: 'Health',
    subTopic: 'Sleep Reset',
    headline: 'Sleep Reset',
    subHeadline: 'Understand why sleep is off right now — and when your system is likely to stabilize again. Astrology helps you see cycles of stress, overstimulation, and recovery — so you can stop feeling stuck.',
    heroPromise: 'Trusted guidance for sleep reset — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Identify why sleep is disrupted now',
      'Know how long the unstable phase may last',
      'Understand recovery windows in the next month'
    ],
    journeyOutcomes: [
      'Clear timing for improvement vs dips',
      'Reduced anxiety through pattern clarity',
      'Confidence in what to change first (small wins)',
      'Astrological + wellness perspective combined',
      'Strongest confidence on recovery trajectory',
      'Clearest understanding of root triggers + relief'
    ],
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call + 3 follow-up chats + 1 sleep-phase summary',
        asyncChat: '48h response',
        outcomes: [
          'Identify why sleep is disrupted now',
          'Know how long the unstable phase may last',
          'Understand recovery windows in the next month'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls + unlimited chat (priority)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Clear timing for improvement vs dips',
          'Reduced anxiety through pattern clarity',
          'Confidence in what to change first (small wins)'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '1 astrologer call + 1 natural wellness expert call + 3 follow-up calls + unlimited chat',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Astrological + wellness perspective combined',
          'Strongest confidence on recovery trajectory',
          'Clearest understanding of root triggers + relief'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Sleep support wellness kit', description: 'Delivered', type: 'kit' },
      { name: 'Calming gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Shanti pooja for mental peace', description: 'Booked + supported', type: 'pooja' },
      { name: 'Wellness retreat recommendation', description: 'Booking support', type: 'session' }
    ],
    faqs: [
      { q: 'Is this medical advice?', a: 'No, this is astrological guidance. Please consult a doctor for medical issues.' },
      { q: 'Can astrology improve sleep?', a: 'It helps identify timing and root causes, which brings clarity and peace.' },
      { q: 'Do you replace doctors?', a: 'No, we complement medical care with timing and emotional clarity.' },
      { q: 'What is the wellness expert?', a: 'A natural health practitioner (Ayurveda/Naturopathy) for holistic support.' },
      { q: 'Unlimited chat?', a: 'Supported and Comprehensive include unlimited chat.' },
      { q: 'Response time?', a: 'Within 24-48 hours depending on your pack.' },
      { q: 'Can I do this without birth time?', a: 'Yes, we can work with approximate time.' },
      { q: 'Refund?', a: '7-day full refund, no questions asked.' }
    ]
  },

  'emotional-recovery': {
    slug: 'emotional-recovery',
    category: 'Health',
    subTopic: 'Emotional Recovery',
    headline: 'Emotional Recovery',
    subHeadline: 'Feel grounded again — with clear timelines, emotional clarity, and supportive guidance through a heavy phase. Best for grief, emotional burnout, low mood, or feeling stuck after a big life event.',
    heroPromise: 'Trusted guidance for emotional recovery — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Understand what you\'re moving through',
      'Know when it\'s likely to feel lighter',
      'Stop blaming yourself for the "slow recovery"'
    ],
    journeyOutcomes: [
      'Clear timeline for emotional easing',
      'Confidence on what to do when triggers hit',
      'Stronger sense of control and steadiness',
      'Cross-verified clarity (mind + emotion)',
      'Strongest confidence on healing trajectory',
      'Deeper understanding of patterns + release'
    ],
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call + 3 follow-up chats + 1 recovery-phase summary',
        asyncChat: '48h response',
        outcomes: [
          'Understand what you\'re moving through',
          'Know when it\'s likely to feel lighter',
          'Stop blaming yourself for the "slow recovery"'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls + unlimited chat (priority)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Clear timeline for emotional easing',
          'Confidence on what to do when triggers hit',
          'Stronger sense of control and steadiness'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '1 astrologer call + 1 Tarot/healing-style expert call + 3 follow-up calls + unlimited chat',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Cross-verified clarity (mind + emotion)',
          'Strongest confidence on healing trajectory',
          'Deeper understanding of patterns + release'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Calming gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Emotional grounding bracelet', description: 'Delivered', type: 'kit' },
      { name: 'Shanti pooja', description: 'Booked + supported', type: 'pooja' },
      { name: 'Wellness kit for calm + sleep', description: 'Delivered', type: 'kit' }
    ],
    faqs: [
      { q: 'Is this therapy?', a: 'No, this is astrological guidance. For clinical support, please see a therapist.' },
      { q: 'What if I feel worse suddenly?', a: 'You can reach out through chat anytime during your pack.' },
      { q: 'Unlimited chat?', a: 'Supported and Comprehensive include unlimited chat.' },
      { q: 'Can I get a second opinion?', a: 'Comprehensive includes multiple expert perspectives.' },
      { q: 'Is Tarot included?', a: 'Comprehensive includes both Vedic and Tarot/healing perspectives.' },
      { q: 'Can I skip birth time?', a: 'Yes, we can work with approximate time or date only.' },
      { q: 'Refund?', a: '7-day full refund, no questions asked.' },
      { q: 'How private is this?', a: 'All conversations are confidential and encrypted.' }
    ]
  },

  'womens-wellness': {
    slug: 'womens-wellness',
    category: 'Health',
    subTopic: 'Women\'s Wellness',
    headline: 'Women\'s Wellness',
    subHeadline: 'Get cycle-aware guidance, stress clarity, and supportive timing insights for your body and mood shifts. Best for hormonal fluctuations, low energy phases, or recurring mood dips that feel hard to explain.',
    heroPromise: 'Trusted guidance for women\'s wellness — through chat + calls — until it feels clear.',
    refundGuarantee: 'No questions asked — 7 day full refund guarantee.',
    painPoints: [
      'Understand your current body-mood phase',
      'Know when energy is likely to rise again',
      'Identify timing patterns that repeat monthly'
    ],
    journeyOutcomes: [
      'Clear timeline for stable windows',
      'Confidence in what to prioritize (rest vs action)',
      'Reduced fear around "what\'s wrong with me"',
      'Astrology + wellness view combined',
      'Strongest clarity on recurring patterns',
      'Clearest confidence on recovery + balance trajectory'
    ],
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call + 3 follow-up chats + 1 wellness-phase summary',
        asyncChat: '48h response',
        outcomes: [
          'Understand your current body-mood phase',
          'Know when energy is likely to rise again',
          'Identify timing patterns that repeat monthly'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls + unlimited chat (priority)',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Clear timeline for stable windows',
          'Confidence in what to prioritize (rest vs action)',
          'Reduced fear around "what\'s wrong with me"'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '1 astrologer call + 1 natural wellness expert call + 3 follow-up calls + unlimited chat',
        asyncChat: '8 weeks (priority)',
        outcomes: [
          'Astrology + wellness view combined',
          'Strongest clarity on recurring patterns',
          'Clearest confidence on recovery + balance trajectory'
        ]
      }
    },
    optionalRemedies: [
      { name: 'Women\'s wellness support kit', description: 'Delivered', type: 'kit' },
      { name: 'Calming/grounding gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Shanti pooja for peace', description: 'Booked + supported', type: 'pooja' },
      { name: 'Wellness retreat recommendation', description: 'Booking support', type: 'session' }
    ],
    faqs: [
      { q: 'Is this medical advice?', a: 'No, this is astrological and wellness guidance. Please consult a doctor for medical issues.' },
      { q: 'Can you help with PCOS/thyroid?', a: 'We provide timing clarity, not medical treatment. Consult your doctor.' },
      { q: 'What is the wellness expert?', a: 'A natural health practitioner for holistic support.' },
      { q: 'Unlimited chat?', a: 'Supported and Comprehensive include unlimited chat.' },
      { q: 'Can I do this without birth time?', a: 'Yes, we can work with approximate time.' },
      { q: 'Privacy?', a: 'All conversations are confidential and encrypted.' },
      { q: 'Refund?', a: '7-day full refund, no questions asked.' },
      { q: 'Response time?', a: 'Within 24-48 hours depending on your pack.' }
    ]
  }
};

// ==========================================
// COMBINED EXPORTS
// ==========================================

// All landing pages indexed by slug
export const ALL_LANDING_PAGES = {
  ...LOVE_SUBTOPICS,
  ...CAREER_SUBTOPICS,
  ...HEALTH_SUBTOPICS
};

// Get landing page content by slug
export const getLandingPageContent = (slug) => {
  return ALL_LANDING_PAGES[slug] || null;
};

// Get all slugs for a category
export const getSlugsByCategory = (category) => {
  const categoryMap = {
    'Love': LOVE_SUBTOPICS,
    'Career': CAREER_SUBTOPICS,
    'Health': HEALTH_SUBTOPICS
  };
  return Object.keys(categoryMap[category] || {});
};

// Main topics definition
export const V5_TOPICS = [
  {
    id: 'love',
    label: 'Love',
    icon: 'heart',
    tagline: 'Relationships & Connection',
    color: '#E91E63',
    subtopics: Object.values(LOVE_SUBTOPICS).map(s => ({
      slug: s.slug,
      label: s.subTopic,
      headline: s.headline
    }))
  },
  {
    id: 'career',
    label: 'Career',
    icon: 'briefcase',
    tagline: 'Work & Money',
    color: '#2196F3',
    subtopics: Object.values(CAREER_SUBTOPICS).map(s => ({
      slug: s.slug,
      label: s.subTopic,
      headline: s.headline
    }))
  },
  {
    id: 'health',
    label: 'Health',
    icon: 'heart_pulse',
    tagline: 'Wellness & Recovery',
    color: '#4CAF50',
    subtopics: Object.values(HEALTH_SUBTOPICS).map(s => ({
      slug: s.slug,
      label: s.subTopic,
      headline: s.headline
    }))
  }
];

// Format price helper
export const formatPriceInr = (price) => {
  if (price === null || price === undefined) return 'Contact Us';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price);
};

export default {
  LOVE_SUBTOPICS,
  CAREER_SUBTOPICS,
  HEALTH_SUBTOPICS,
  ALL_LANDING_PAGES,
  V5_TOPICS,
  getLandingPageContent,
  getSlugsByCategory,
  formatPriceInr
};
