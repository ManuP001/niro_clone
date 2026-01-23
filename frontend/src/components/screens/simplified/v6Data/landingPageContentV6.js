/**
 * NIRO V6 Landing Page Content - Source of Truth
 * All content from: Niro_Subtopic_Naming_SourceOfTruth_V6_FilledTemplate.xlsx
 * 
 * Total: 18 sub-topics organized under 3 main topics (Love, Career, Health)
 * Each topic has 6 sub-topics
 */

// ==========================================
// V6 TIER CONFIGURATION
// ==========================================
export const V6_TIER_CONFIG = {
  Focussed: { 
    label: 'Quick clarity',
    badge: null,
  },
  Supported: { 
    label: 'Full support',
    badge: 'Recommended',
  },
  Comprehensive: { 
    label: 'Deep confidence',
    badge: null,
  },
};

// ==========================================
// LOVE / RELATIONSHIP SUB-TOPICS (6)
// ==========================================
export const V6_LOVE_SUBTOPICS = {
  'relationship-healing': {
    slug: 'relationship-healing',
    category: 'Love & Relationships',
    subTopic: 'Relationship Healing',
    topicExplainerOneLiner: 'Closure, emotional stability, and what changes next.',
    heroPromise: 'Talk to a trusted astrologer on chat + calls until your relationship decision feels clear.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 8999, durationWeeks: 8 },
      Supported: { priceInr: 10999, durationWeeks: 8 },
      Comprehensive: { priceInr: 12999, durationWeeks: 12 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 session',
        followUps: 'chat: 7 days',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One clear next step to reduce confusion immediately'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions',
        followUps: 'Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          '8–12 week timeline with key turning points',
          'Unlimited chat with astrologer for the full pack duration'
        ]
      },
      Comprehensive: {
        duration: '12 weeks',
        consultations: '5 sessions',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer + Tarot Reader',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Unlimited chat + priority response in critical moments'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this for me if I\'m confused and overthinking?', a: 'Yes. These packs are built for uncertainty — you\'ll get clear answers, timing, and follow-ups until things feel settled.' },
      { q: 'Do I need exact birth time?', a: 'No. If you don\'t know it, you can skip it. We\'ll still guide you using the details you have.' },
      { q: 'How fast do I get to talk to an astrologer?', a: 'Typically within 24–48 hours for the first call. Chat opens immediately after purchase.' },
      { q: 'Can I ask follow-up questions?', a: 'Yes. Supported and Comprehensive include Unlimited chat follow-ups with your astrologer.' },
      { q: 'Will I get a written summary?', a: 'Yes. After your session, you\'ll receive a concise summary of the key insights and what to expect next.' },
      { q: 'Are remedies compulsory?', a: 'No. Remedies are optional add-ons. If you choose one, we handle booking, coordination, and delivery.' },
      { q: 'Can I switch experts if I don\'t vibe?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
      { q: 'What if I don\'t find value?', a: 'You\'re covered by our no questions asked — 7-day full refund guarantee.' }
    ],
    optionalRemedies: [
      { name: 'Relationship harmony pooja', description: 'Booking + coordination (optional)', type: 'pooja' },
      { name: 'Stress + sleep kit', description: 'Delivered to your door', type: 'kit' },
      { name: '1:1 healing session', description: 'Sound/energy healer booking', type: 'session' }
    ]
  },

  'dating-compatibility': {
    slug: 'dating-compatibility',
    category: 'Love & Relationships',
    subTopic: 'Dating & Compatibility',
    topicExplainerOneLiner: 'Compatibility, patterns, and whether to invest emotionally.',
    heroPromise: 'Talk to a trusted astrologer on chat + calls until your relationship decision feels clear.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 6999, durationWeeks: 8 },
      Supported: { priceInr: 8999, durationWeeks: 8 },
      Comprehensive: { priceInr: 11999, durationWeeks: 12 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 session',
        followUps: 'chat: 7 days',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One clear next step to reduce confusion immediately'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions',
        followUps: 'Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          '8–12 week timeline with key turning points',
          'Unlimited chat with astrologer for the full pack duration'
        ]
      },
      Comprehensive: {
        duration: '12 weeks',
        consultations: '5 sessions',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer + Tarot Reader',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Unlimited chat + priority response in critical moments'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this for me if I\'m confused and overthinking?', a: 'Yes. These packs are built for uncertainty — you\'ll get clear answers, timing, and follow-ups until things feel settled.' },
      { q: 'Do I need exact birth time?', a: 'No. If you don\'t know it, you can skip it. We\'ll still guide you using the details you have.' },
      { q: 'How fast do I get to talk to an astrologer?', a: 'Typically within 24–48 hours for the first call. Chat opens immediately after purchase.' },
      { q: 'Can I ask follow-up questions?', a: 'Yes. Supported and Comprehensive include Unlimited chat follow-ups with your astrologer.' },
      { q: 'Will I get a written summary?', a: 'Yes. After your session, you\'ll receive a concise summary of the key insights and what to expect next.' },
      { q: 'Are remedies compulsory?', a: 'No. Remedies are optional add-ons. If you choose one, we handle booking, coordination, and delivery.' },
      { q: 'Can I switch experts if I don\'t vibe?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
      { q: 'What if I don\'t find value?', a: 'You\'re covered by our no questions asked — 7-day full refund guarantee.' }
    ],
    optionalRemedies: [
      { name: 'Gemstone sourcing', description: 'Confidence/attraction support', type: 'gemstone' },
      { name: 'Personal protection kit', description: 'Evil-eye/calm protection', type: 'kit' },
      { name: '1:1 tarot clarity session', description: 'Mini-session booking (add-on)', type: 'session' }
    ]
  },

  'marriage-planning': {
    slug: 'marriage-planning',
    category: 'Love & Relationships',
    subTopic: 'Marriage Planning',
    topicExplainerOneLiner: 'Timelines, commitment clarity, and family alignment.',
    heroPromise: 'Talk to a trusted astrologer on chat + calls until your relationship decision feels clear.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 8999, durationWeeks: 8 },
      Supported: { priceInr: 10999, durationWeeks: 12 },
      Comprehensive: { priceInr: 11999, durationWeeks: 12 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 session',
        followUps: 'chat: 7 days',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One clear next step to reduce confusion immediately'
        ]
      },
      Supported: {
        duration: '12 weeks',
        consultations: '3 sessions',
        followUps: 'Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          '8–12 week timeline with key turning points',
          'Unlimited chat with astrologer for the full pack duration'
        ]
      },
      Comprehensive: {
        duration: '12 weeks',
        consultations: '5 sessions',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer + Tarot Reader',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Unlimited chat + priority response in critical moments'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this for me if I\'m confused and overthinking?', a: 'Yes. These packs are built for uncertainty — you\'ll get clear answers, timing, and follow-ups until things feel settled.' },
      { q: 'Do I need exact birth time?', a: 'No. If you don\'t know it, you can skip it. We\'ll still guide you using the details you have.' },
      { q: 'How fast do I get to talk to an astrologer?', a: 'Typically within 24–48 hours for the first call. Chat opens immediately after purchase.' },
      { q: 'Can I ask follow-up questions?', a: 'Yes. Supported and Comprehensive include Unlimited chat follow-ups with your astrologer.' },
      { q: 'Will I get a written summary?', a: 'Yes. After your session, you\'ll receive a concise summary of the key insights and what to expect next.' },
      { q: 'Are remedies compulsory?', a: 'No. Remedies are optional add-ons. If you choose one, we handle booking, coordination, and delivery.' },
      { q: 'Can I switch experts if I don\'t vibe?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
      { q: 'What if I don\'t find value?', a: 'You\'re covered by our no questions asked — 7-day full refund guarantee.' }
    ],
    optionalRemedies: [
      { name: 'Vivah Shanti Pooja', description: 'Booking + end-to-end coordination', type: 'pooja' },
      { name: 'Gemstone sourcing', description: 'Stability/compatibility focus', type: 'gemstone' },
      { name: 'Couple harmony ritual set', description: 'Delivered (optional)', type: 'kit' }
    ]
  },

  'communication-trust': {
    slug: 'communication-trust',
    category: 'Love & Relationships',
    subTopic: 'Communication & Trust',
    topicExplainerOneLiner: 'Get clear, grounded guidance to rebuild trust, reduce overthinking, and communicate without spiraling.',
    heroPromise: 'Talk to a verified astrologer on call + chat until you feel steady and sure about where this relationship is headed.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 5999, durationWeeks: 8 },
      Supported: { priceInr: 7999, durationWeeks: 8 },
      Comprehensive: { priceInr: 9999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1x 45-min astrologer call',
        followUps: '3 follow-up chats (48h response)',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'Understand why trust feels shaky right now',
          'Know what is a phase vs a pattern',
          'Identify the next 2–3 weeks\' emotional climate'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1x 45-min call + 2x 25-min follow-up calls',
        followUps: 'Unlimited chat (priority response)',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Clear timeline for stability vs volatility',
          'What conversations to have now vs later',
          'Confidence on whether to repair, pause, or redefine'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '2 expert calls (Vedic + Tarot)',
        followUps: '3 follow-up calls + Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer, Tarot Reader',
        outcomes: [
          'Two-perspective clarity (logic + intuition)',
          'Root cause behind repeated triggers',
          'Strongest confidence on long-term viability'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Will you tell me if this relationship will last?', a: 'We provide clarity on patterns and timing, not guarantees. You make the final call.' },
      { q: 'Can I ask unlimited follow-ups?', a: 'Supported and Comprehensive include Unlimited chat. Focussed has structured follow-ups.' },
      { q: 'What if I\'m not sure what to ask?', a: 'Your astrologer will guide you through the right questions.' },
      { q: 'What if my partner\'s birth details aren\'t available?', a: 'We can still provide insights based on your chart alone.' },
      { q: 'Is this therapy?', a: 'No, this is astrological guidance. For clinical issues, please consult a therapist.' },
      { q: 'How fast do I get responses?', a: 'Within 24-48 hours depending on your pack.' },
      { q: 'What if I want a second opinion?', a: 'Comprehensive includes two expert perspectives.' },
      { q: 'How does the 7-day refund work?', a: 'Full refund if you\'re not satisfied, no questions asked.' }
    ],
    optionalRemedies: [
      { name: 'Relationship harmony gemstone', description: 'Delivered to your door', type: 'gemstone' },
      { name: 'Personal protection charm/bracelet', description: 'Delivered', type: 'kit' },
      { name: 'Shanti pooja for peace & stability', description: 'Booked + supported', type: 'pooja' },
      { name: 'Calming wellness kit', description: 'Sleep + anxiety support (delivered)', type: 'kit' }
    ]
  },

  'family-relationships': {
    slug: 'family-relationships',
    category: 'Love & Relationships',
    subTopic: 'Family Dynamics',
    topicExplainerOneLiner: 'Peace, boundaries, and smoother dynamics at home.',
    heroPromise: 'Talk to a trusted astrologer on chat + calls until your relationship decision feels clear.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 7999, durationWeeks: 8 },
      Supported: { priceInr: 9999, durationWeeks: 8 },
      Comprehensive: { priceInr: 11999, durationWeeks: 12 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 session',
        followUps: 'chat: 7 days',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One clear next step to reduce confusion immediately'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions',
        followUps: 'Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          '8–12 week timeline with key turning points',
          'Unlimited chat with astrologer for the full pack duration'
        ]
      },
      Comprehensive: {
        duration: '12 weeks',
        consultations: '5 sessions',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer + Tarot Reader',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Unlimited chat + priority response in critical moments'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this for me if I\'m confused and overthinking?', a: 'Yes. These packs are built for uncertainty — you\'ll get clear answers, timing, and follow-ups until things feel settled.' },
      { q: 'Do I need exact birth time?', a: 'No. If you don\'t know it, you can skip it. We\'ll still guide you using the details you have.' },
      { q: 'How fast do I get to talk to an astrologer?', a: 'Typically within 24–48 hours for the first call. Chat opens immediately after purchase.' },
      { q: 'Can I ask follow-up questions?', a: 'Yes. Supported and Comprehensive include Unlimited chat follow-ups with your astrologer.' },
      { q: 'Will I get a written summary?', a: 'Yes. After your session, you\'ll receive a concise summary of the key insights and what to expect next.' },
      { q: 'Are remedies compulsory?', a: 'No. Remedies are optional add-ons. If you choose one, we handle booking, coordination, and delivery.' },
      { q: 'Can I switch experts if I don\'t vibe?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
      { q: 'What if I don\'t find value?', a: 'You\'re covered by our no questions asked — 7-day full refund guarantee.' }
    ],
    optionalRemedies: [
      { name: 'Home harmony pooja', description: 'Booking + coordination', type: 'pooja' },
      { name: 'Protection kit', description: 'Reduce negativity/conflict', type: 'kit' },
      { name: 'Gemstone sourcing', description: 'Calm/communication support', type: 'gemstone' }
    ]
  },

  'breakup-closure': {
    slug: 'breakup-closure',
    category: 'Love & Relationships',
    subTopic: 'Breakup & Closure',
    topicExplainerOneLiner: 'Move from confusion to closure — with clear timelines, emotional grounding, and the confidence to let go or reconnect wisely.',
    heroPromise: 'Get astrological guidance for what ended, what\'s next, and how to protect your peace while you heal.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1x 45-min astrologer call',
        followUps: '3 follow-up chats',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What this breakup was meant to teach',
          'How long the heavy phase may last',
          'Whether reconnection is likely or not'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1x 45-min call + 2x 25-min follow-up calls',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Clear \'no-contact vs conversation\' timing',
          'Emotional stability plan for the next month',
          'Confidence to stop looping on "what if"'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '2 expert calls (Vedic + Tarot)',
        followUps: '3 follow-up calls + Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer, Tarot Reader',
        outcomes: [
          'Cross-verified clarity on reconnection vs closure',
          'Why you attract similar patterns',
          'Strongest confidence on your next relationship chapter'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
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
    ],
    optionalRemedies: [
      { name: 'Heart-healing gemstone', description: 'Delivered to your door', type: 'gemstone' },
      { name: 'Emotional protection bracelet', description: 'Delivered', type: 'kit' },
      { name: 'Shanti/closure pooja', description: 'Booked + supported', type: 'pooja' },
      { name: 'Mood & sleep wellness kit', description: 'Delivered', type: 'kit' }
    ]
  }
};

// ==========================================
// CAREER SUB-TOPICS (6)
// ==========================================
export const V6_CAREER_SUBTOPICS = {
  'career-clarity': {
    slug: 'career-clarity',
    category: 'Career & Money',
    subTopic: 'Career Clarity',
    topicExplainerOneLiner: 'Direction, strengths, and the right next step.',
    heroPromise: 'Get clear timing and confidence for your next career move — with trusted astrologers on chat + calls.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 8999, durationWeeks: 8 },
      Supported: { priceInr: 10999, durationWeeks: 8 },
      Comprehensive: { priceInr: 12999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 session',
        followUps: 'chat: 7 days',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One clear next step to reduce confusion immediately'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions',
        followUps: 'Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          '8–12 week timeline with key turning points',
          'Unlimited chat with astrologer for the full pack duration'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '5 sessions',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer + Numerologist',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Unlimited chat + priority response in critical moments'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this for me if I\'m confused and overthinking?', a: 'Yes. These packs are built for uncertainty — you\'ll get clear answers, timing, and follow-ups until things feel settled.' },
      { q: 'Do I need exact birth time?', a: 'No. If you don\'t know it, you can skip it. We\'ll still guide you using the details you have.' },
      { q: 'How fast do I get to talk to an astrologer?', a: 'Typically within 24–48 hours for the first call. Chat opens immediately after purchase.' },
      { q: 'Can I ask follow-up questions?', a: 'Yes. Supported and Comprehensive include Unlimited chat follow-ups with your astrologer.' },
      { q: 'Will I get a written summary?', a: 'Yes. After your session, you\'ll receive a concise summary of the key insights and what to expect next.' },
      { q: 'Are remedies compulsory?', a: 'No. Remedies are optional add-ons. If you choose one, we handle booking, coordination, and delivery.' },
      { q: 'Can I switch experts if I don\'t vibe?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
      { q: 'What if I don\'t find value?', a: 'You\'re covered by our no questions asked — 7-day full refund guarantee.' }
    ],
    optionalRemedies: [
      { name: 'Gemstone sourcing', description: 'Confidence/authority stone + delivery', type: 'gemstone' },
      { name: '1:1 tarot clarity session', description: 'Decision focus mini-session', type: 'session' },
      { name: 'Prosperity + focus kit', description: 'Delivered', type: 'kit' }
    ]
  },

  'job-transition': {
    slug: 'job-transition',
    category: 'Career & Money',
    subTopic: 'Job Change',
    topicExplainerOneLiner: 'Switch timing, decision confidence, and stability.',
    heroPromise: 'Get clear timing and confidence for your next career move — with trusted astrologers on chat + calls.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 8999, durationWeeks: 8 },
      Supported: { priceInr: 10999, durationWeeks: 12 },
      Comprehensive: { priceInr: 11999, durationWeeks: 12 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 session',
        followUps: 'chat: 7 days',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One clear next step to reduce confusion immediately'
        ]
      },
      Supported: {
        duration: '12 weeks',
        consultations: '3 sessions',
        followUps: 'Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          '8–12 week timeline with key turning points',
          'Unlimited chat with astrologer for the full pack duration'
        ]
      },
      Comprehensive: {
        duration: '12 weeks',
        consultations: '5 sessions',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer + Numerologist',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Unlimited chat + priority response in critical moments'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this for me if I\'m confused and overthinking?', a: 'Yes. These packs are built for uncertainty — you\'ll get clear answers, timing, and follow-ups until things feel settled.' },
      { q: 'Do I need exact birth time?', a: 'No. If you don\'t know it, you can skip it. We\'ll still guide you using the details you have.' },
      { q: 'How fast do I get to talk to an astrologer?', a: 'Typically within 24–48 hours for the first call. Chat opens immediately after purchase.' },
      { q: 'Can I ask follow-up questions?', a: 'Yes. Supported and Comprehensive include Unlimited chat follow-ups with your astrologer.' },
      { q: 'Will I get a written summary?', a: 'Yes. After your session, you\'ll receive a concise summary of the key insights and what to expect next.' },
      { q: 'Are remedies compulsory?', a: 'No. Remedies are optional add-ons. If you choose one, we handle booking, coordination, and delivery.' },
      { q: 'Can I switch experts if I don\'t vibe?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
      { q: 'What if I don\'t find value?', a: 'You\'re covered by our no questions asked — 7-day full refund guarantee.' }
    ],
    optionalRemedies: [
      { name: 'Obstacle-removal pooja', description: 'Booking + coordination (optional)', type: 'pooja' },
      { name: 'Gemstone sourcing', description: 'Stability/confidence stone + delivery', type: 'gemstone' },
      { name: 'Interview confidence kit', description: 'Delivered', type: 'kit' }
    ]
  },

  'money-stability': {
    slug: 'money-stability',
    category: 'Career & Money',
    subTopic: 'Money Stability',
    topicExplainerOneLiner: 'Patterns, savings, and timing for financial decisions.',
    heroPromise: 'Get clear timing and confidence for your next career move — with trusted astrologers on chat + calls.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 6999, durationWeeks: 8 },
      Supported: { priceInr: 8999, durationWeeks: 8 },
      Comprehensive: { priceInr: 10999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 session',
        followUps: 'chat: 7 days',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One clear next step to reduce confusion immediately'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions',
        followUps: 'Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          '8–12 week timeline with key turning points',
          'Unlimited chat with astrologer for the full pack duration'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '5 sessions',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer + Numerologist',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Unlimited chat + priority response in critical moments'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this for me if I\'m confused and overthinking?', a: 'Yes. These packs are built for uncertainty — you\'ll get clear answers, timing, and follow-ups until things feel settled.' },
      { q: 'Do I need exact birth time?', a: 'No. If you don\'t know it, you can skip it. We\'ll still guide you using the details you have.' },
      { q: 'How fast do I get to talk to an astrologer?', a: 'Typically within 24–48 hours for the first call. Chat opens immediately after purchase.' },
      { q: 'Can I ask follow-up questions?', a: 'Yes. Supported and Comprehensive include Unlimited chat follow-ups with your astrologer.' },
      { q: 'Will I get a written summary?', a: 'Yes. After your session, you\'ll receive a concise summary of the key insights and what to expect next.' },
      { q: 'Are remedies compulsory?', a: 'No. Remedies are optional add-ons. If you choose one, we handle booking, coordination, and delivery.' },
      { q: 'Can I switch experts if I don\'t vibe?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
      { q: 'What if I don\'t find value?', a: 'You\'re covered by our no questions asked — 7-day full refund guarantee.' }
    ],
    optionalRemedies: [
      { name: 'Prosperity kit', description: 'Wallet/home items delivered', type: 'kit' },
      { name: 'Gemstone sourcing', description: 'Abundance/protection stone + delivery', type: 'gemstone' },
      { name: 'Lakshmi ritual service', description: 'Simple booking (optional)', type: 'pooja' }
    ]
  },

  'big-decision-timing': {
    slug: 'big-decision-timing',
    category: 'Career & Money',
    subTopic: 'Big Decision Timing',
    topicExplainerOneLiner: 'Know when to accept an offer, make a big move, or pause — based on chart-backed timing.',
    heroPromise: 'Get clear timing and confidence for your next career move — with trusted astrologers on chat + calls.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 2999, durationWeeks: 4 },
      Supported: { priceInr: 4999, durationWeeks: 4 },
      Comprehensive: { priceInr: 6999, durationWeeks: 4 }
    },
    featuresByTier: {
      Focussed: {
        duration: '4 weeks',
        consultations: '1× 30-min astrologer call',
        followUps: '2 follow-up chats + 1 timing note',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'Identify your next action window',
          'Know which weeks to avoid',
          'Feel confident about timing, not impulse'
        ]
      },
      Supported: {
        duration: '4 weeks',
        consultations: '1× 45-min call + 1× 20-min follow-up call',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Clear sequencing: what to do first vs later',
          'Confidence on acceptance/exit decisions',
          'Reduced anxiety around "wrong timing"'
        ]
      },
      Comprehensive: {
        duration: '4 weeks',
        consultations: '2 expert calls (Vedic + Numerology)',
        followUps: '2 follow-up calls + Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer, Numerologist',
        outcomes: [
          'Cross-verified timing window',
          'Why you\'re stuck in indecision',
          'Strongest confidence on big moves'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Will you guarantee success?', a: 'We provide clarity on timing, not outcome guarantees.' },
      { q: 'Can you help choose between 2 options?', a: 'Yes, we help you see the timing and trade-offs for each.' },
      { q: 'Unlimited chat included?', a: 'Supported and Comprehensive include Unlimited chat.' },
      { q: 'What if dates change?', a: 'We can provide updated timing guidance.' },
      { q: 'Can I do this without birth time?', a: 'Yes, we can work with approximate time.' },
      { q: 'What if I\'m still unsure?', a: 'We work with you until you feel clear.' },
      { q: 'Refund?', a: '7-day full refund, no questions asked.' },
      { q: 'How fast is the turnaround?', a: 'Expert matching within 24 hours.' }
    ],
    optionalRemedies: [
      { name: 'Confidence gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Prosperity charm', description: 'Delivered', type: 'kit' },
      { name: 'Obstacle-removal pooja', description: 'Booked + supported', type: 'pooja' }
    ]
  },

  'work-stress': {
    slug: 'work-stress',
    category: 'Career & Money',
    subTopic: 'Work Stress',
    topicExplainerOneLiner: 'Get calm clarity on what\'s draining you at work — and how long this pressure phase is likely to last.',
    heroPromise: 'Understand your current career cycle, stress triggers, and the best timing to push, pause, or change lanes.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call',
        followUps: '3 follow-up chats + 1 stress-phase summary',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'Identify chart-based stress triggers',
          'Know if this is temporary or structural',
          'Understand the next 4–6 weeks\' intensity'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Clear \'survive vs switch\' timing window',
          'What to avoid to reduce conflict',
          'Confidence on boundaries + next step'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '2 expert calls (Vedic + Numerology)',
        followUps: '3 follow-up calls + Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer, Numerologist',
        outcomes: [
          'Cross-verified timeline for peak stress → relief',
          'Root pattern behind work pressure',
          'Strongest confidence on change vs stay decision'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
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
    ],
    optionalRemedies: [
      { name: 'Focus & grounding gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Work-stability protection charm', description: 'Delivered', type: 'kit' },
      { name: 'Obstacle-removal pooja', description: 'Booked + supported', type: 'pooja' },
      { name: 'Sleep + recovery wellness kit', description: 'Delivered', type: 'kit' }
    ]
  },

  'office-politics': {
    slug: 'office-politics',
    category: 'Career & Money',
    subTopic: 'Office Dynamics',
    topicExplainerOneLiner: 'Understand hidden dynamics, protect your reputation, and time your moves wisely.',
    heroPromise: 'Get chart-based clarity on power dynamics, conflict cycles, and the safest way forward in your workplace.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call',
        followUps: '3 follow-up chats + 1 clarity summary',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'Know what to ignore vs address',
          'Identify high-risk days/weeks for conflict',
          'Understand who to trust (and how much)'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Clear timing for asking, negotiating, escalating',
          'Confidence on how to respond (not react)',
          'Stronger protection for reputation + role stability'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '2 expert calls (Vedic + Tarot)',
        followUps: '3 follow-up calls + Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Vedic Astrologer, Tarot Reader',
        outcomes: [
          'Two-perspective view on intent + outcome',
          'Root pattern behind recurring conflict',
          'Strongest confidence on stay/exit timeline'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
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
    ],
    optionalRemedies: [
      { name: 'Protection + grounding gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Workplace shield kit', description: 'Delivered', type: 'kit' },
      { name: 'Shanti pooja for peace', description: 'Booked + supported', type: 'pooja' }
    ]
  }
};

// ==========================================
// HEALTH SUB-TOPICS (6)
// ==========================================
export const V6_HEALTH_SUBTOPICS = {
  'stress-management': {
    slug: 'stress-management',
    category: 'Health & Wellness',
    subTopic: 'Stress Management',
    topicExplainerOneLiner: 'Nervous-system calm, better sleep, and lighter days.',
    heroPromise: 'Get calm clarity on your current phase and what improves next — guided by trusted astrologers.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 6999, durationWeeks: 12 },
      Supported: { priceInr: 8999, durationWeeks: 12 },
      Comprehensive: { priceInr: 9999, durationWeeks: 12 }
    },
    featuresByTier: {
      Focussed: {
        duration: '12 weeks',
        consultations: '1 session',
        followUps: 'chat: 7 days',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One clear next step to reduce confusion immediately'
        ]
      },
      Supported: {
        duration: '12 weeks',
        consultations: '3 sessions',
        followUps: 'Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          '8–12 week timeline with key turning points',
          'Unlimited chat with astrologer for the full pack duration'
        ]
      },
      Comprehensive: {
        duration: '12 weeks',
        consultations: '5 sessions',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Astrologer + Natural Wellness Expert',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Unlimited chat + priority response in critical moments'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this for me if I\'m confused and overthinking?', a: 'Yes. These packs are built for uncertainty — you\'ll get clear answers, timing, and follow-ups until things feel settled.' },
      { q: 'Do I need exact birth time?', a: 'No. If you don\'t know it, you can skip it. We\'ll still guide you using the details you have.' },
      { q: 'How fast do I get to talk to an astrologer?', a: 'Typically within 24–48 hours for the first call. Chat opens immediately after purchase.' },
      { q: 'Can I ask follow-up questions?', a: 'Yes. Supported and Comprehensive include Unlimited chat follow-ups with your astrologer.' },
      { q: 'Will I get a written summary?', a: 'Yes. After your session, you\'ll receive a concise summary of the key insights and what to expect next.' },
      { q: 'Are remedies compulsory?', a: 'No. Remedies are optional add-ons. If you choose one, we handle booking, coordination, and delivery.' },
      { q: 'Can I switch experts if I don\'t vibe?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
      { q: 'What if I don\'t find value?', a: 'You\'re covered by our no questions asked — 7-day full refund guarantee.' }
    ],
    optionalRemedies: [
      { name: 'Deep sleep kit', description: 'Premium kit delivered', type: 'kit' },
      { name: 'Natural wellness consult', description: 'Booking', type: 'session' },
      { name: 'Mental peace pooja', description: 'Booking + coordination (optional)', type: 'pooja' }
    ]
  },

  'sleep-reset': {
    slug: 'sleep-reset',
    category: 'Health & Wellness',
    subTopic: 'Sleep Reset',
    topicExplainerOneLiner: 'Understand why sleep is off right now — and when your system is likely to stabilize again.',
    heroPromise: 'Astrology helps you see cycles of stress, overstimulation, and recovery — so you can stop feeling stuck.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call',
        followUps: '3 follow-up chats',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'Identify why sleep is disrupted now',
          'Know how long the unstable phase may last',
          'Understand recovery windows in the next month'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Clear timing for improvement vs dips',
          'Reduced anxiety through pattern clarity',
          'Confidence in what to change first (small wins)'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '1 astrologer call + 1 natural wellness expert call',
        followUps: '3 follow-up calls + Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer, Natural Wellness Expert',
        outcomes: [
          'Astrological + wellness perspective combined',
          'Strongest confidence on recovery trajectory',
          'Clearest understanding of root triggers + relief'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this medical advice?', a: 'No, this is astrological guidance. Please consult a doctor for medical issues.' },
      { q: 'Can astrology improve sleep?', a: 'It helps identify timing and root causes, which brings clarity and peace.' },
      { q: 'Do you replace doctors?', a: 'No, we complement medical care with timing and emotional clarity.' },
      { q: 'What is the wellness expert?', a: 'A natural health practitioner (Ayurveda/Naturopathy) for holistic support.' },
      { q: 'Unlimited chat?', a: 'Supported and Comprehensive include Unlimited chat.' },
      { q: 'Response time?', a: 'Within 24-48 hours depending on your pack.' },
      { q: 'Can I do this without birth time?', a: 'Yes, we can work with approximate time.' },
      { q: 'Refund?', a: '7-day full refund, no questions asked.' }
    ],
    optionalRemedies: [
      { name: 'Sleep support wellness kit', description: 'Delivered', type: 'kit' },
      { name: 'Calming gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Shanti pooja for mental peace', description: 'Booked + supported', type: 'pooja' },
      { name: 'Wellness retreat recommendation', description: 'Booking support', type: 'session' }
    ]
  },

  'energy-balance': {
    slug: 'energy-balance',
    category: 'Health & Wellness',
    subTopic: 'Energy & Balance',
    topicExplainerOneLiner: 'Routine stability, vitality, and momentum.',
    heroPromise: 'Get calm clarity on your current phase and what improves next — guided by trusted astrologers.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 8999, durationWeeks: 8 },
      Supported: { priceInr: 10999, durationWeeks: 8 },
      Comprehensive: { priceInr: 11999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 session',
        followUps: 'chat: 7 days',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One clear next step to reduce confusion immediately'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions',
        followUps: 'Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          '8–12 week timeline with key turning points',
          'Unlimited chat with astrologer for the full pack duration'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '5 sessions',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Astrologer + Natural Wellness Expert',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Unlimited chat + priority response in critical moments'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this for me if I\'m confused and overthinking?', a: 'Yes. These packs are built for uncertainty — you\'ll get clear answers, timing, and follow-ups until things feel settled.' },
      { q: 'Do I need exact birth time?', a: 'No. If you don\'t know it, you can skip it. We\'ll still guide you using the details you have.' },
      { q: 'How fast do I get to talk to an astrologer?', a: 'Typically within 24–48 hours for the first call. Chat opens immediately after purchase.' },
      { q: 'Can I ask follow-up questions?', a: 'Yes. Supported and Comprehensive include Unlimited chat follow-ups with your astrologer.' },
      { q: 'Will I get a written summary?', a: 'Yes. After your session, you\'ll receive a concise summary of the key insights and what to expect next.' },
      { q: 'Are remedies compulsory?', a: 'No. Remedies are optional add-ons. If you choose one, we handle booking, coordination, and delivery.' },
      { q: 'Can I switch experts if I don\'t vibe?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
      { q: 'What if I don\'t find value?', a: 'You\'re covered by our no questions asked — 7-day full refund guarantee.' }
    ],
    optionalRemedies: [
      { name: 'Vitality kit', description: 'D2C energy wellness kit delivered', type: 'kit' },
      { name: 'Natural wellness consult', description: 'Booking', type: 'session' },
      { name: 'Gemstone sourcing', description: 'Energy/confidence stone + delivery', type: 'gemstone' }
    ]
  },

  'healing-journey': {
    slug: 'healing-journey',
    category: 'Health & Wellness',
    subTopic: 'Healing Journey',
    topicExplainerOneLiner: 'Closure, emotional stability, and what changes next.',
    heroPromise: 'Get calm clarity on your current phase and what improves next — guided by trusted astrologers.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 8999, durationWeeks: 8 },
      Supported: { priceInr: 10999, durationWeeks: 8 },
      Comprehensive: { priceInr: 11999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1 session',
        followUps: 'chat: 7 days',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'What your chart says about this situation (no jargon)',
          'Near-term direction (next 4–8 weeks): what improves vs stays stuck',
          'One clear next step to reduce confusion immediately'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '3 sessions',
        followUps: 'Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Root pattern in the chart (why this repeats)',
          '8–12 week timeline with key turning points',
          'Unlimited chat with astrologer for the full pack duration'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '5 sessions',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Astrologer + Natural Wellness Expert',
        outcomes: [
          'Deep-dive reading: situation + your longer life pattern',
          'Full 3–6 month map: pressure, relief, and momentum phases',
          'Unlimited chat + priority response in critical moments'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this for me if I\'m confused and overthinking?', a: 'Yes. These packs are built for uncertainty — you\'ll get clear answers, timing, and follow-ups until things feel settled.' },
      { q: 'Do I need exact birth time?', a: 'No. If you don\'t know it, you can skip it. We\'ll still guide you using the details you have.' },
      { q: 'How fast do I get to talk to an astrologer?', a: 'Typically within 24–48 hours for the first call. Chat opens immediately after purchase.' },
      { q: 'Can I ask follow-up questions?', a: 'Yes. Supported and Comprehensive include Unlimited chat follow-ups with your astrologer.' },
      { q: 'Will I get a written summary?', a: 'Yes. After your session, you\'ll receive a concise summary of the key insights and what to expect next.' },
      { q: 'Are remedies compulsory?', a: 'No. Remedies are optional add-ons. If you choose one, we handle booking, coordination, and delivery.' },
      { q: 'Can I switch experts if I don\'t vibe?', a: 'Yes. We\'ll help you switch to another expert if the match doesn\'t feel right.' },
      { q: 'What if I don\'t find value?', a: 'You\'re covered by our no questions asked — 7-day full refund guarantee.' }
    ],
    optionalRemedies: [
      { name: 'Stress + sleep kit', description: 'Delivered', type: 'kit' },
      { name: 'Natural wellness consult', description: 'Ayurveda/Naturopathy booking', type: 'session' },
      { name: 'Shanti pooja', description: 'Booking + coordination (optional)', type: 'pooja' }
    ]
  },

  'emotional-recovery': {
    slug: 'emotional-recovery',
    category: 'Health & Wellness',
    subTopic: 'Emotional Recovery',
    topicExplainerOneLiner: 'Feel grounded again — with clear timelines, emotional clarity, and supportive guidance through a heavy phase.',
    heroPromise: 'Best for grief, emotional burnout, low mood, or feeling stuck after a big life event.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call',
        followUps: '3 follow-up chats + 1 recovery-phase summary',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'Understand what you\'re moving through',
          'Know when it\'s likely to feel lighter',
          'Stop blaming yourself for the "slow recovery"'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Clear timeline for emotional easing',
          'Confidence on what to do when triggers hit',
          'Stronger sense of control and steadiness'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '1 astrologer call + 1 Tarot/healing-style expert call',
        followUps: '3 follow-up calls + Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer, Tarot/Healing Expert',
        outcomes: [
          'Cross-verified clarity (mind + emotion)',
          'Strongest confidence on healing trajectory',
          'Deeper understanding of patterns + release'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this therapy?', a: 'No, this is astrological guidance. For clinical support, please see a therapist.' },
      { q: 'What if I feel worse suddenly?', a: 'You can reach out through chat anytime during your pack.' },
      { q: 'Unlimited chat?', a: 'Supported and Comprehensive include Unlimited chat.' },
      { q: 'Can I get a second opinion?', a: 'Comprehensive includes multiple expert perspectives.' },
      { q: 'Is Tarot included?', a: 'Comprehensive includes both Vedic and Tarot/healing perspectives.' },
      { q: 'Can I skip birth time?', a: 'Yes, we can work with approximate time or date only.' },
      { q: 'Refund?', a: '7-day full refund, no questions asked.' },
      { q: 'How private is this?', a: 'All conversations are confidential and encrypted.' }
    ],
    optionalRemedies: [
      { name: 'Calming gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Emotional grounding bracelet', description: 'Delivered', type: 'kit' },
      { name: 'Shanti pooja', description: 'Booked + supported', type: 'pooja' },
      { name: 'Wellness kit for calm + sleep', description: 'Delivered', type: 'kit' }
    ]
  },

  'womens-wellness': {
    slug: 'womens-wellness',
    category: 'Health & Wellness',
    subTopic: 'Women\'s Wellness',
    topicExplainerOneLiner: 'Get cycle-aware guidance, stress clarity, and supportive timing insights for your body and mood shifts.',
    heroPromise: 'Best for hormonal fluctuations, low energy phases, or recurring mood dips that feel hard to explain.',
    refundGuarantee: 'No questions asked — 7-day full refund guarantee.',
    tierCards: {
      Focussed: { priceInr: 4999, durationWeeks: 8 },
      Supported: { priceInr: 6999, durationWeeks: 8 },
      Comprehensive: { priceInr: 8999, durationWeeks: 8 }
    },
    featuresByTier: {
      Focussed: {
        duration: '8 weeks',
        consultations: '1× 45-min astrologer call',
        followUps: '3 follow-up chats',
        unlimitedChat: false,
        expertMix: 'Astrologer',
        outcomes: [
          'Understand your current body-mood phase',
          'Know when energy is likely to rise again',
          'Identify timing patterns that repeat monthly'
        ]
      },
      Supported: {
        duration: '8 weeks',
        consultations: '1× 45-min call + 2× 25-min follow-up calls',
        followUps: 'Unlimited chat (priority)',
        unlimitedChat: true,
        expertMix: 'Astrologer',
        outcomes: [
          'Clear timeline for stable windows',
          'Confidence in what to prioritize (rest vs action)',
          'Reduced fear around "what\'s wrong with me"'
        ]
      },
      Comprehensive: {
        duration: '8 weeks',
        consultations: '1 astrologer call + 1 natural wellness expert call',
        followUps: '3 follow-up calls + Unlimited chat',
        unlimitedChat: true,
        expertMix: 'Astrologer, Natural Wellness Expert',
        outcomes: [
          'Astrology + wellness view combined',
          'Strongest clarity on recurring patterns',
          'Clearest confidence on recovery + balance trajectory'
        ]
      }
    },
    journeySteps: [
      { step: 1, title: 'Choose your pack', desc: 'Select the tier that fits your needs' },
      { step: 2, title: 'Get matched with an expert', desc: 'Within 24 hours of purchase' },
      { step: 3, title: 'Calls + follow-ups + Unlimited chat', desc: 'Ongoing support till you have clarity' },
      { step: 4, title: 'Optional add-ons', desc: 'Coming soon' }
    ],
    afterPurchaseSteps: [
      'You get instant access to your pack + your astrologer chat',
      'We schedule your first call within 24–48 hours',
      'After the call, you can ask follow-ups and get clarity until you feel confident',
      'If you choose any optional remedies, we coordinate and deliver them end-to-end'
    ],
    whyNiroBullets: [
      'Real astrologers (not generic reports) — across Vedic, Tarot, Numerology & more',
      'Unlimited follow-ups in Supported & Comprehensive packs',
      'Clear outcomes: patterns, timing, and what to expect next (no jargon)',
      'Private, secure, and designed for a judgement-free experience',
      'No questions asked — 7-day full refund guarantee.'
    ],
    faqs: [
      { q: 'Is this medical advice?', a: 'No, this is astrological guidance. Please consult a doctor for medical issues.' },
      { q: 'Can you help with PCOS/thyroid?', a: 'We provide timing and stress insights, not medical treatment.' },
      { q: 'What is the wellness expert?', a: 'A natural health practitioner (Ayurveda/Naturopathy) for holistic support.' },
      { q: 'Unlimited chat?', a: 'Supported and Comprehensive include Unlimited chat.' },
      { q: 'Can I do this without birth time?', a: 'Yes, we can work with approximate time.' },
      { q: 'Privacy?', a: 'All conversations are confidential and encrypted.' },
      { q: 'Refund?', a: '7-day full refund, no questions asked.' },
      { q: 'Response time?', a: 'Within 24-48 hours depending on your pack.' }
    ],
    optionalRemedies: [
      { name: 'Women\'s wellness support kit', description: 'Delivered', type: 'kit' },
      { name: 'Calming/grounding gemstone', description: 'Delivered', type: 'gemstone' },
      { name: 'Shanti pooja for peace', description: 'Booked + supported', type: 'pooja' },
      { name: 'Wellness retreat recommendation', description: 'Booking support', type: 'session' }
    ]
  }
};

// ==========================================
// COMBINED EXPORT + HELPER FUNCTIONS
// ==========================================
export const V6_ALL_SUBTOPICS = {
  ...V6_LOVE_SUBTOPICS,
  ...V6_CAREER_SUBTOPICS,
  ...V6_HEALTH_SUBTOPICS
};

// Get subtopic by slug
export const getV6SubtopicBySlug = (slug) => {
  return V6_ALL_SUBTOPICS[slug] || null;
};

// Get all subtopics as array
export const getAllV6Subtopics = () => {
  return Object.values(V6_ALL_SUBTOPICS);
};

// Map old tile IDs to new V6 slugs
export const V6_TILE_TO_SUBTOPIC_MAP = {
  // Love
  'relationship_healing': 'relationship-healing',
  'dating_compatibility': 'dating-compatibility',
  'marriage_planning': 'marriage-planning',
  'communication_trust': 'communication-trust',
  'family_relationships': 'family-relationships',
  'breakup_closure': 'breakup-closure',
  // Career
  'career_clarity': 'career-clarity',
  'job_transition': 'job-transition',
  'money_stability': 'money-stability',
  'big_decision_timing': 'big-decision-timing',
  'work_stress': 'work-stress',
  'office_politics': 'office-politics',
  // Health
  'stress_management': 'stress-management',
  'sleep_reset': 'sleep-reset',
  'energy_balance': 'energy-balance',
  'healing_journey': 'healing-journey',
  'emotional_recovery': 'emotional-recovery',
  'womens_wellness': 'womens-wellness'
};

export default V6_ALL_SUBTOPICS;
