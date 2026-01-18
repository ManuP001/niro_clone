/**
 * NIRO V5 Tile Data Configuration
 * Updated with correct pricing and content from spreadsheet
 */

import { expertImages } from './theme';

// ==========================================
// HOME CATEGORIES WITH TILES
// ==========================================
export const HOME_CATEGORIES = [
  {
    id: 'relationship',
    title: 'Relationship Clarity & Commitment',
    tiles: [
      {
        id: 'relationship_healing',
        title: 'Relationship Healing',
        shortTitle: 'Healing',
        iconType: 'healing',
        outcomeStatement: 'Full astrology report about Love & Relationships',
        painPoints: 'Post-conflict/breakup risk; emotional confusion; trust issues',
        price: 6999,
        validity: 60,
        duration: '60 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 3×20 min follow-ups + Unlimited chat',
        whoFor: [
          'Post-conflict/breakup risk situations',
          'Emotional confusion about the relationship',
          'Trust issues that need to be addressed'
        ],
        includedTools: [
          { name: '30-Day Repair Plan', description: 'Weekly steps + check-ins to rebuild trust', cta: 'Open' },
          { name: 'Communication Script Pack', description: 'What to say/avoid in key moments', cta: 'Open' },
          { name: '+triggers identification', description: 'Why patterns repeat identified', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Moon-Mercury Calm Kit', description: 'Sleep/anxiety + communication routine', price: 899 },
          { name: 'Protection Kit', description: 'Evil-eye / calming kit', price: 799 },
          { name: 'Shanti/Graha Pooja', description: 'Optional: if astrologically relevant', price: 1999 }
        ]
      },
      {
        id: 'family_relationships',
        title: 'Family Relationships',
        shortTitle: 'Family',
        iconType: 'family',
        outcomeStatement: 'Full astrology report about Family Relationships',
        painPoints: 'Family conflicts/pressure; wants peace + direction',
        price: 5999,
        validity: 60,
        duration: '60 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 4×30 min follow-ups + Unlimited chat',
        whoFor: [
          'Family conflicts and pressure situations',
          'Looking for peace and direction',
          'Need help navigating family dynamics'
        ],
        includedTools: [
          { name: 'Family Harmony Toolkit', description: 'Strategies for peace at home', cta: 'Open' },
          { name: 'Relationship Pattern Analysis', description: 'Understanding family dynamics', cta: 'Open' },
          { name: 'Communication Guidelines', description: 'Effective family communication tips', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Mercury Focus Kit', description: 'Communication clarity ritual', price: 799 },
          { name: 'Protection Kit', description: 'Can mirror protection + shanti options', price: 799 },
          { name: 'Shanti Pooja', description: 'Family peace ritual', price: 1999 }
        ]
      },
      {
        id: 'dating_compatibility',
        title: 'Dating & Compatibility',
        shortTitle: 'Dating',
        iconType: 'heart',
        outcomeStatement: 'Full astrology report about Dating & Compatibility',
        painPoints: 'Dating confusion; wants to understand compatibility patterns',
        price: 4999,
        validity: 60,
        duration: '60 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 3×20 min follow-ups + Unlimited chat',
        whoFor: [
          'Navigating the dating scene with clarity',
          'Want to understand compatibility with a potential partner',
          'Need guidance on relationship patterns and timing'
        ],
        includedTools: [
          { name: 'Compatibility Checklist', description: 'Key factors that make a match work', cta: 'Open' },
          { name: 'Dating Timeline', description: 'Favorable periods for meeting someone', cta: 'Open' },
          { name: 'Red Flag Identifier', description: 'Patterns to watch for in new relationships', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Venus Harmony Kit', description: 'Attract love and connection ritual', price: 899 },
          { name: 'Protection Kit', description: 'Emotional protection during dating', price: 799 },
          { name: 'Relationship Pooja', description: 'Blessing for new love', price: 1999 }
        ]
      },
      {
        id: 'marriage_planning',
        title: 'Marriage Planning',
        shortTitle: 'Marriage',
        iconType: 'rings',
        outcomeStatement: 'Full astrology report about Marriage & Partnership',
        painPoints: 'Marriage timing anxiety; wants auspicious dates + partner clarity',
        price: 7999,
        validity: 90,
        duration: '90 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 5×20 min follow-ups + Unlimited chat',
        whoFor: [
          'Planning to get married and need timing guidance',
          'Want kundli matching with your partner',
          'Need auspicious muhurat for engagement or wedding'
        ],
        includedTools: [
          { name: 'Kundli Matching Report', description: 'Comprehensive compatibility analysis', cta: 'Open' },
          { name: 'Muhurat Calendar', description: 'Auspicious dates for engagement & wedding', cta: 'Open' },
          { name: 'Marriage Readiness Assessment', description: 'Timing and preparation checklist', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Venus Harmony Kit', description: 'Love and marriage blessing ritual', price: 899 },
          { name: 'Vivah Pooja', description: 'Marriage blessing ceremony', price: 2499 },
          { name: 'Gemstone Recommendation', description: 'Partnership harmony stone', price: 1499 }
        ]
      }
    ]
  },
  {
    id: 'career',
    title: 'Career Direction & Stability',
    tiles: [
      {
        id: 'career_clarity',
        title: 'Career Clarity',
        shortTitle: 'Clarity',
        iconType: 'compass',
        outcomeStatement: 'Full report about Career, Opportunities & Money',
        painPoints: 'Confused about direction; wants role/track clarity',
        price: 4999,
        validity: 60,
        duration: '60 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 3×20 min follow-ups + Unlimited chat',
        whoFor: [
          'Confused about career direction',
          'Need clarity on which role/track suits you',
          'Want a focused skill-building roadmap'
        ],
        includedTools: [
          { name: 'Role Fit Map', description: '3 tracks + why they suit you', cta: 'Open' },
          { name: 'Skill Focus Plan', description: '30-day plan: what to build + how', cta: 'Open' },
          { name: 'Decision Window', description: '90-day timing: when to explore vs commit', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Mercury Focus Kit', description: 'Gemstone recommendation + purchase', price: 1499 },
          { name: 'Saturday Saturn Discipline', description: 'Confidence/authority ritual guide', price: 799 },
          { name: 'Protection Kit', description: 'Grounding ritual', price: 799 }
        ]
      },
      {
        id: 'job_transition',
        title: 'Job Transition',
        shortTitle: 'Job Change',
        iconType: 'briefcase',
        outcomeStatement: 'Full report about Career, Opportunities & Money',
        painPoints: 'Switching jobs; interviews/offers; timing anxiety',
        price: 7999,
        validity: 90,
        duration: '90 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 5×15 min follow-ups + Unlimited chat',
        whoFor: [
          'Currently switching jobs or considering a change',
          'Have interviews/offers and need decision clarity',
          'Experiencing timing anxiety about the transition'
        ],
        includedTools: [
          { name: 'Timing Window', description: 'Apply/interview/negotiation optimal periods', cta: 'Open' },
          { name: 'Offer Decision Checklist', description: 'Role fit + risk assessment', cta: 'Open' },
          { name: 'Joining Date Shortlist', description: '2-3 auspicious options', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Gemstone Recommendation', description: 'Confidence/grounding stone + purchase', price: 1499 },
          { name: 'Mercury Focus Kit', description: 'Interview clarity ritual', price: 799 },
          { name: 'Protection Kit', description: 'Grounding support', price: 799 }
        ]
      },
      {
        id: 'money_stability',
        title: 'Money Stability',
        shortTitle: 'Money',
        iconType: 'wallet',
        outcomeStatement: 'Full report about Career, Opportunities & Money',
        painPoints: 'Money stress; inconsistent earnings; wants stability',
        price: 2999,
        validity: 30,
        duration: '30 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 2×15 min follow-ups + Unlimited chat',
        whoFor: [
          'Experiencing money stress or inconsistent income',
          'Want financial stability and a savings plan',
          'Need timing guidance for financial decisions'
        ],
        includedTools: [
          { name: 'Wealth Timeline', description: 'Income patterns and growth windows', cta: 'Open' },
          { name: 'Money Do/Don\'t Calendar', description: 'Spending and saving discipline guide', cta: 'Open' },
          { name: 'Savings Discipline Plan', description: 'Practical steps for stability', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Prosperity Kit', description: 'Abundance attraction kit', price: 999 },
          { name: 'Gemstone Recommendation', description: 'Wealth stone + purchase', price: 1499 },
          { name: 'Friday Lakshmi Routine', description: 'Weekly prosperity practice', price: 499 }
        ]
      }
    ]
  },
  {
    id: 'business_money',
    title: 'Business & Money',
    tiles: [
      {
        id: 'business_decision',
        title: 'Business Decisions',
        shortTitle: 'Start a Business?',
        iconType: 'chart',
        outcomeStatement: 'Full report about Business, Growth & Money',
        painPoints: 'Launch/contract decision; wants timing + risk clarity',
        price: 4999,
        validity: 60,
        duration: '60 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 3×20 min follow-ups + Unlimited chat',
        whoFor: [
          'Considering starting or scaling a business',
          'Need timing clarity for launches/contracts',
          'Want partnership compatibility assessment'
        ],
        includedTools: [
          { name: 'Business Muhurat Pack', description: 'Launch/contract/payment timing', cta: 'Open' },
          { name: 'Decision Risk Scan', description: 'Top 3 risks + mitigation strategies', cta: 'Open' },
          { name: 'Partnership Fit Check', description: 'Co-founder/partner compatibility', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Gemstone Recommendation', description: 'Stability/protection stone + purchase', price: 1499 },
          { name: 'Friday Lakshmi Routine', description: 'Weekly prosperity ritual', price: 499 },
          { name: 'Prosperity/Protection Kit', description: 'D2C business success kit', price: 999 }
        ]
      },
      {
        id: 'financial_growth',
        title: 'Financial Growth',
        shortTitle: 'Loss in Business?',
        iconType: 'trending',
        outcomeStatement: 'Full report about Business, Growth & Money',
        painPoints: 'Wants stable income/savings; money anxiety',
        price: 7999,
        validity: 90,
        duration: '90 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 5×15 min follow-ups + Unlimited chat',
        whoFor: [
          'Experiencing losses or money anxiety',
          'Want stable income and savings growth',
          'Need to identify and fix money leakages'
        ],
        includedTools: [
          { name: 'Wealth Leakage Scan', description: 'Patterns + fixes identified', cta: 'Open' },
          { name: 'Growth Window', description: '90-day growth opportunity periods', cta: 'Open' },
          { name: 'Savings Discipline Plan', description: 'Practical wealth building steps', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Gemstone Recommendation', description: 'Abundance/protection stone + purchase', price: 1499 },
          { name: 'Lakshmi Routine', description: 'Weekly prosperity practice', price: 499 },
          { name: 'Prosperity Kit', description: 'D2C wealth kit', price: 999 }
        ]
      },
      {
        id: 'timing_move',
        title: 'Timing Your Next Move',
        shortTitle: 'Partnership?',
        iconType: 'clock',
        outcomeStatement: 'Full report about Business, Growth & Money',
        painPoints: 'Multiple options; wants "when to do what"',
        price: 2999,
        validity: 30,
        duration: '30 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 2×15 min follow-ups + Unlimited chat',
        whoFor: [
          'Have multiple business options to consider',
          'Need clarity on "when to do what"',
          'Want an action calendar for key decisions'
        ],
        includedTools: [
          { name: 'Next 90/180 Day Timeline', description: 'Push/hold/avoid periods', cta: 'Open' },
          { name: 'Action Calendar', description: 'Key dates + what to do', cta: 'Open' },
          { name: '1-Page Decision Summary', description: 'Quick reference for clarity', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Gemstone Recommendation', description: 'Timing/clarity stone + purchase', price: 1499 },
          { name: 'Protection Kit', description: 'Obstacle protection kit', price: 799 },
          { name: 'Obstacle Removal Pooja', description: 'Optional: clear blockers', price: 1999 }
        ]
      }
    ]
  },
  {
    id: 'parenting',
    title: 'Family & Kids',
    tiles: [
      {
        id: 'fertility',
        title: 'Fertility Support',
        shortTitle: 'Fertility',
        iconType: 'baby',
        outcomeStatement: 'Full Astrology report about Parenthood',
        painPoints: 'Trying to conceive; planning windows; emotional uncertainty',
        price: null, // Price not specified in spreadsheet
        validity: 60,
        duration: '60 days',
        sessions: '8 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic Astrologer consultation + 3 Tarot Card Readings (5 questions each) + 3×20 min + 5×15 min follow up sessions + Unlimited Chat with the Astrologer',
        whoFor: [
          'Trying to conceive and need timing support',
          'Planning windows for conception',
          'Navigating emotional uncertainty around fertility'
        ],
        includedTools: [
          { name: 'Conception Timing Pack', description: '2-3 favorable windows + rationale', cta: 'Open' },
          { name: 'Medical-Support Friendly Checklist', description: 'Non-medical routine + stress tips', cta: 'Open' },
          { name: 'Mira Q&A List', description: '10 questions for guidance', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Santan / Fertility Pooja', description: 'Verified blessing for conception', price: 2499 },
          { name: 'Protection Kit', description: 'Calm + grounding support', price: 799 },
          { name: 'Gemstone Recommendation', description: 'Supportive framing only', price: 1499 }
        ]
      },
      {
        id: 'baby_naming',
        title: 'Baby Naming & Muhurat',
        shortTitle: 'Naming',
        iconType: 'star',
        outcomeStatement: "Child's Kundli, name options and life report",
        painPoints: 'Delivery + naming decisions; wants "done-for-me" clarity',
        price: null, // Shown as "—" in spreadsheet
        validity: 90,
        duration: '90 days',
        sessions: '9 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic Astrologer consultation + 3 Tarot Card Readings (5 questions each) + 3×20 min + 5×15 min follow up sessions + Unlimited Chat with the Astrologer',
        whoFor: [
          'Expecting a baby and need naming guidance',
          'Want kundli-based name suggestions',
          'Need childbirth muhurat timing'
        ],
        includedTools: [
          { name: 'Childbirth Muhurat Pack', description: 'Auspicious delivery timing', cta: 'Open' },
          { name: 'Baby Naming Pack', description: '20 options + meaning + initials', cta: 'Open' },
          { name: 'Name Shortlist Finalizer', description: 'Top 3 with rationale', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Naming Ceremony / Muhurat Service', description: 'Auspicious naming ceremony timing', price: 1999 },
          { name: 'Protection Kit', description: 'Evil-eye protection for baby', price: 799 },
          { name: 'Blessing/Comfort D2C Kit', description: 'Welcome baby blessing kit', price: 599 }
        ]
      },
      {
        id: 'child_development',
        title: 'Child Development',
        shortTitle: 'Kids',
        iconType: 'growth',
        outcomeStatement: "Child's Kundli and life report",
        painPoints: 'Parenting guidance; temperament/learning style; future anxiety',
        price: null, // Price not clearly visible
        validity: 60,
        duration: '60 days',
        sessions: '10 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic Astrologer consultation + 3 Tarot Card Readings (5 questions each) + 3×20 min + 5×15 min follow up sessions + Unlimited Chat with the Astrologer',
        whoFor: [
          'Want to understand your child better',
          'Need guidance on their learning style',
          'Concerned about their future development'
        ],
        includedTools: [
          { name: 'Kids Kundli Snapshot', description: 'Strengths + temperament analysis', cta: 'Open' },
          { name: 'Learning Style Guide', description: 'How they learn best', cta: 'Open' },
          { name: 'Annual "Kids Year Ahead"', description: 'Mini-report for the year', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Protection Kit', description: 'Child protection ritual', price: 799 },
          { name: 'Gemstone Recommendation', description: 'Only if parent asks', price: 1499 },
          { name: 'Child Protection/Shanti Pooja', description: 'Optional peace ritual', price: 1999 }
        ]
      }
    ]
  },
  {
    id: 'health_wellness',
    title: 'Health & Wellness',
    tiles: [
      {
        id: 'healing_journey',
        title: 'Healing Journey (Energy & Burnout)',
        shortTitle: 'Healing',
        iconType: 'heart_pulse',
        outcomeStatement: 'Full astrology report about Health',
        painPoints: 'Recovering emotionally/mentally; wants calmer phase',
        price: 4999,
        validity: 60,
        duration: '60 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 3×20 min follow-ups + Unlimited chat',
        whoFor: [
          'Recovering emotionally or mentally',
          'Want a calmer, more peaceful phase',
          'Need holistic recovery support'
        ],
        includedTools: [
          { name: 'Healing Window Timing', description: 'Next 60/90 days outlook', cta: 'Open' },
          { name: '14-Day Recovery Routine', description: 'Grounding plan + triggers', cta: 'Open' },
          { name: 'Trigger Map', description: 'Identify and manage stress triggers', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Stress & Sleep Kit', description: 'Moon-Saturn calming routine', price: 899 },
          { name: 'Gemstone Recommendation', description: 'Calm/grounding stone + purchase', price: 1499 },
          { name: 'Shanti Pooja', description: 'Healing support (optional)', price: 1999 }
        ]
      },
      {
        id: 'stress_management',
        title: 'Stress Management (Sleep, Stress & Balance)',
        shortTitle: 'Stress',
        iconType: 'mind',
        outcomeStatement: 'Full astrology report about Health',
        painPoints: 'High anxiety/overwhelm; sleep disruption',
        price: 7999,
        validity: 90,
        duration: '90 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 5×15 min follow-ups + Unlimited chat',
        whoFor: [
          'Dealing with high anxiety or overwhelm',
          'Sleep disruption affecting daily life',
          'Need boundary setting support'
        ],
        includedTools: [
          { name: 'Stress Driver Diagnosis', description: 'Chart-based stress analysis', cta: 'Open' },
          { name: 'Sleep Reset Plan', description: '14-day sleep improvement routine', cta: 'Open' },
          { name: 'Boundary Scripts', description: 'Work + relationship communication templates', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Stress & Sleep Kit', description: 'Calming routine kit', price: 899 },
          { name: 'Gemstone Recommendation', description: 'Calm/peace stone + purchase', price: 1499 },
          { name: 'Shanti/Mental Peace Pooja', description: 'Optional peace ritual', price: 1999 }
        ]
      },
      {
        id: 'energy_balance',
        title: 'Energy & Balance (Recovery Phase)',
        shortTitle: 'Energy',
        iconType: 'sun',
        outcomeStatement: 'Full astrology report about Health',
        painPoints: 'Low energy; inconsistent routine',
        price: 4999,
        validity: 60,
        duration: '60 days',
        sessions: '7 days / 3 messages per expert to find best fit',
        responseSLA: '24 hours',
        toolFeatures: '1 Vedic astrologer consultation + 1 Tarot reading (5 Qs) + 3×20 min follow-ups + Unlimited chat',
        whoFor: [
          'Experiencing low energy levels',
          'Inconsistent daily routine',
          'Need a practical vitality plan'
        ],
        includedTools: [
          { name: 'Energy Pattern Scan', description: 'Sun/Mars focus analysis', cta: 'Open' },
          { name: '14-Day Vitality Plan', description: 'Energy restoration routine', cta: 'Open' },
          { name: 'Daily Schedule Template', description: 'Optimal timing for activities', cta: 'Open' }
        ],
        paidRemedies: [
          { name: 'Vitality Kit', description: 'D2C energy wellness kit', price: 799 },
          { name: 'Gemstone Recommendation', description: 'Energy stone + purchase', price: 1499 },
          { name: 'Sun Support Ritual', description: 'Minimal daily practice guide', price: 399 }
        ]
      }
    ]
  }
];

// ==========================================
// HELPER FUNCTIONS
// ==========================================

// Get tile by ID
export const getTileById = (tileId) => {
  for (const category of HOME_CATEGORIES) {
    const tile = category.tiles.find(t => t.id === tileId);
    if (tile) {
      return { ...tile, categoryTitle: category.title, categoryId: category.id };
    }
  }
  return null;
};

// Get all tiles flat
export const getAllTiles = () => {
  const tiles = [];
  for (const category of HOME_CATEGORIES) {
    for (const tile of category.tiles) {
      tiles.push({ ...tile, categoryTitle: category.title, categoryId: category.id });
    }
  }
  return tiles;
};

// Get tiles by category
export const getTilesByCategory = (categoryId) => {
  const category = HOME_CATEGORIES.find(c => c.id === categoryId);
  return category ? category.tiles : [];
};

// Get category by ID
export const getCategoryById = (categoryId) => {
  return HOME_CATEGORIES.find(c => c.id === categoryId);
};

// Get tile tools
export const getTileTools = (tileId) => {
  const tile = getTileById(tileId);
  return tile?.includedTools || [];
};

// Get package structure for topic landing page
export const getPackageStructure = (tileId) => {
  const tile = getTileById(tileId);
  if (!tile) return null;
  
  return {
    whoIsThisFor: tile.whoFor || [],
    deliverables: [
      { icon: 'calendar', item: `${tile.validity} days of access` },
      { icon: 'chat', item: tile.sessions || 'Expert sessions included' },
      { icon: 'clock', item: `${tile.responseSLA} response time` },
      { icon: 'document', item: tile.outcomeStatement },
    ],
    howItWorks: [
      { step: 1, title: 'Buy Your Pack', description: 'Choose a pack and complete payment securely' },
      { step: 2, title: 'Get Matched', description: "We'll connect you with the right expert for your needs" },
      { step: 3, title: 'Start Chatting', description: 'Message your expert anytime, get responses within 24 hours' },
      { step: 4, title: 'Get Your Report', description: tile.outcomeStatement },
    ],
    whatsIncluded: [
      { icon: 'astro', title: 'Expert Guidance', description: tile.toolFeatures },
      { icon: 'chat', title: 'Unlimited Chat', description: 'Message your expert anytime during your plan' },
      { icon: 'document', title: 'Tools & Reports', description: 'Access to specialized tools and insights' },
      { icon: 'gift', title: 'Remedies (Optional)', description: 'Add verified remedies to enhance your journey' },
    ],
    faqs: [
      { q: 'How quickly will I get a response?', a: `Our experts respond within ${tile.responseSLA}. For urgent matters, you can book a video call.` },
      { q: 'Can I change my expert?', a: "Yes, you can request a different expert if you feel the match isn't right." },
      { q: 'What is the refund policy?', a: "We offer a 7-day no-questions-asked refund if you're not satisfied." },
      { q: 'Is my information private?', a: 'Absolutely. All conversations are encrypted and your data is never shared.' },
    ],
  };
};

// Format price
export const formatPrice = (price) => {
  if (price === null || price === undefined) {
    return 'Contact Us';
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
};

// ==========================================
// SAMPLE EXPERTS (for landing pages)
// ==========================================
export const SAMPLE_EXPERTS = [
  {
    expert_id: '1',
    name: 'Pandit Raj Sharma',
    modality_label: 'Vedic Astrologer',
    rating: 4.9,
    consultations: 2840,
    experience: '15 years',
    languages: ['Hindi', 'English'],
    photo_url: expertImages[0],
  },
  {
    expert_id: '2',
    name: 'Dr. Meera Rao',
    modality_label: 'Numerologist',
    rating: 4.8,
    consultations: 1950,
    experience: '12 years',
    languages: ['English', 'Kannada'],
    photo_url: expertImages[1],
  },
  {
    expert_id: '3',
    name: 'Acharya Ved Gupta',
    modality_label: 'Spiritual Guide',
    rating: 4.9,
    consultations: 3200,
    experience: '20 years',
    languages: ['Hindi', 'Sanskrit'],
    photo_url: expertImages[2],
  },
  {
    expert_id: '4',
    name: 'Priya Deshmukh',
    modality_label: 'Tarot Reader',
    rating: 4.7,
    consultations: 1680,
    experience: '8 years',
    languages: ['Marathi', 'Hindi', 'English'],
    photo_url: expertImages[3],
  },
  {
    expert_id: '5',
    name: 'Swami Anand',
    modality_label: 'Healer',
    rating: 4.9,
    consultations: 2100,
    experience: '18 years',
    languages: ['Hindi', 'English'],
    photo_url: expertImages[4],
  },
  {
    expert_id: '6',
    name: 'Kavitha Nair',
    modality_label: 'Life Coach',
    rating: 4.8,
    consultations: 1420,
    experience: '10 years',
    languages: ['Malayalam', 'English'],
    photo_url: expertImages[5],
  },
];
