// Mock data for Niro Mobile App

export const userData = {
  name: 'Ananya',
  zodiacSign: 'Leo',
  birthDate: 'August 15, 1995',
  birthTime: '10:30 AM',
  birthPlace: 'Bengaluru, India',
  avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
};

export const todayInsights = {
  date: 'July 11, 2025',
  luckyColor: 'Red',
  luckyNumber: '7',
  mood: ['happy', 'calm', 'energetic'],
  overallScore: 78,
  message: "Looks like your day is going to be great! The stars align in your favor today.",
};

export const panchangData = {
  date: '16 Mar 2425',
  location: 'Bengaluru, IN',
  tithi: 'Shukla Paksha Dashami',
  nakshatra: 'Swati',
  yoga: 'Shubha',
  karana: 'Bava',
  sunrise: '06:00:00 AM',
  sunset: '06:24:06 PM',
  moonrise: '02:45 PM',
  sunSign: 'Pisces',
  moonSign: 'Libra',
  rahuKaal: '04:30 PM - 06:00 PM',
  masar: {
    inSagittarius: '5/45 - 18:30',
    inCancer: '09:45 - 11:05',
  },
  ascendant: {
    inSagittarius: '5/45 - 18:30',
    inCancer: '09:45 - 11:05',
  },
  auspiciousTimes: [
    'Shakti Patha (Moon ascending)',
    'Purnimasay, Ashadha',
    'Amanta: Ashadha',
  ],
  inauspiciousTimes: [
    'Rahu Kaal: 04:30 PM - 06:00 PM',
    'Yamagandam: 12:00 PM - 01:30 PM',
  ],
  festivals: ['Maha Christmas and New Year'],
};

export const horoscopeCategories = [
  {
    id: 'career',
    title: 'Career',
    icon: 'briefcase',
    content: 'This is a favorable time for career growth. New opportunities may arise that align with your long-term goals. Stay focused and maintain a positive attitude.',
    score: 85,
  },
  {
    id: 'health',
    title: 'Health',
    icon: 'heart',
    content: 'Your energy levels are high today. This is a good time to start a new fitness routine or focus on your mental well-being through meditation.',
    score: 72,
  },
  {
    id: 'love',
    title: 'Love',
    icon: 'heart',
    content: 'Venus gracing your life from the harmonious realm of Libra, your relationship is touched by a delicate balance of grace and understanding. Your ability to both give and receive love is heightened.',
    score: 90,
  },
  {
    id: 'relationship',
    title: 'Relationship',
    icon: 'users',
    content: 'Communication with loved ones will be smooth. Express your feelings openly and you will strengthen your bonds.',
    score: 88,
  },
  {
    id: 'finance',
    title: 'Finance',
    icon: 'wallet',
    content: 'Be cautious with investments today. It is a good time to save rather than spend on luxury items.',
    score: 65,
  },
];

export const compatibilityData = {
  user: {
    name: 'You',
    avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
    zodiac: 'Leo',
  },
  partner: {
    name: 'Alia',
    avatar: 'https://randomuser.me/api/portraits/women/68.jpg',
    zodiac: 'Sagittarius',
  },
  overallMatch: 95,
  parameters: [
    { name: 'Gund & kaal daya', score: 8, maxScore: 8 },
    { name: 'Remedies', score: 7, maxScore: 8 },
    { name: 'Puja', score: 6, maxScore: 8 },
  ],
  detailedScores: [
    { category: 'Emotional', score: 92 },
    { category: 'Mental', score: 88 },
    { category: 'Physical', score: 95 },
    { category: 'Spiritual', score: 90 },
  ],
};

export const chatMessages = [
  {
    id: 1,
    type: 'user',
    message: 'How can I improve my finances?',
    timestamp: '10:30 AM',
  },
  {
    id: 2,
    type: 'ai',
    message: 'Venus is currently where Mercury was when you were born. That angle brings complexity and transformation. Based on your chart, this is a good period for long-term investments rather than quick gains. Consider diversifying your portfolio and avoid impulsive purchases.',
    timestamp: '10:31 AM',
  },
  {
    id: 3,
    type: 'user',
    message: 'When will I get married?',
    timestamp: '10:35 AM',
  },
  {
    id: 4,
    type: 'ai',
    message: 'Based on your Dasha periods and Venus placement, the most favorable time for marriage appears to be between late 2025 and early 2026. Jupiter\'s transit through your 7th house during this period creates auspicious conditions for committed relationships.',
    timestamp: '10:36 AM',
  },
];

export const quickQuestions = [
  'When will I get married?',
  'Will I study abroad?',
  'Should I start my own business?',
  'How is my health looking?',
  'What about my career growth?',
];

export const navItems = [
  { id: 'home', label: 'Home', icon: 'home' },
  { id: 'chat', label: 'Chat', icon: 'message-circle' },
  { id: 'kundli', label: 'Kundli', icon: 'star' },
  { id: 'horoscope', label: 'Horoscope', icon: 'star' },
  { id: 'panchang', label: 'Panchang', icon: 'calendar' },
  { id: 'compatibility', label: 'Match', icon: 'heart' },
];

export const niroFeatures = [
  {
    id: 1,
    icon: 'zap',
    title: 'Instant Insights',
    description: 'Get real-time astrological guidance powered by AI',
  },
  {
    id: 2,
    icon: 'shield',
    title: 'Privacy First',
    description: 'Your data is encrypted and never shared',
  },
  {
    id: 3,
    icon: 'user',
    title: 'Personalized',
    description: 'Tailored predictions based on your birth chart',
  },
  {
    id: 4,
    icon: 'clock',
    title: '24/7 Support',
    description: 'Get guidance anytime, anywhere',
  },
];

export const sampleQuestions = [
  {
    question: 'Will I get promoted this year?',
    avatar: 'https://randomuser.me/api/portraits/women/1.jpg',
  },
  {
    question: 'When will I meet my soulmate?',
    avatar: 'https://randomuser.me/api/portraits/women/2.jpg',
  },
  {
    question: 'Is this a good time to start a business?',
    avatar: 'https://randomuser.me/api/portraits/women/3.jpg',
  },
  {
    question: 'What are my financial prospects?',
    avatar: 'https://randomuser.me/api/portraits/women/4.jpg',
  },
];

export const blogArticles = [
  {
    id: 1,
    title: 'Understanding Your Birth Chart',
    image: 'https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=600&h=400&fit=crop',
    excerpt: 'Learn how to read and interpret your natal chart...',
  },
  {
    id: 2,
    title: 'Mercury Retrograde: Myths vs Reality',
    image: 'https://images.unsplash.com/photo-1444080748397-f442aa95c3e5?w=600&h=400&fit=crop',
    excerpt: 'Discover the truth about this misunderstood phenomenon...',
  },
  {
    id: 3,
    title: 'Daily Rituals for Cosmic Alignment',
    image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop',
    excerpt: 'Simple practices to align with your cosmic energy...',
  },
];

export const features = [
  {
    icon: 'star',
    label: 'Daily Horoscope',
  },
  {
    icon: 'heart',
    label: 'Compatibility',
  },
  {
    icon: 'calendar',
    label: 'Panchang',
  },
  {
    icon: 'zap',
    label: 'AI Chat',
  },
];

export const testimonials = [
  {
    name: 'Sarah',
    role: 'Software Engineer',
    content: 'Niro has transformed how I approach life decisions. Highly recommend!',
    rating: 5,
    avatar: 'https://randomuser.me/api/portraits/women/5.jpg',
  },
  {
    name: 'Priya',
    role: 'Designer',
    content: 'The accuracy is impressive. It feels like having a personal astrologer!',
    rating: 5,
    avatar: 'https://randomuser.me/api/portraits/women/6.jpg',
  },
  {
    name: 'Anita',
    role: 'Marketing Manager',
    content: "Best astrology app I've used. Simple, elegant, and insightful.",
    rating: 5,
    avatar: 'https://randomuser.me/api/portraits/women/7.jpg',
  },
];

export const faqs = [
  {
    id: 1,
    question: 'How accurate is Niro?',
    answer: 'Niro uses Vedic astrology principles combined with AI analysis for highly accurate insights.',
  },
  {
    id: 2,
    question: 'Is my data secure?',
    answer: 'Yes, all your data is encrypted and never shared with third parties.',
  },
  {
    id: 3,
    question: 'Can I use Niro offline?',
    answer: 'Currently, Niro requires an internet connection for AI-powered insights.',
  },
  {
    id: 4,
    question: 'Do I need my exact birth time?',
    answer: 'Yes, for accurate moon sign and house calculations, your birth time is important.',
  },
];
