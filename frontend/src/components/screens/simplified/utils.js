import { BACKEND_URL } from '../../../config';

// API helper for Simplified endpoints
export const apiSimplified = {
  baseUrl: `${BACKEND_URL}/api/simplified`,
  
  async get(endpoint, token, { signal } = {}) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      },
      signal,
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }
    return response.json();
  },
  
  async post(endpoint, data, token) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }
    return response.json();
  },
};

// Format price in INR
export const formatPrice = (priceInr) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(priceInr);
};

// Tier colors
export const TIER_COLORS = {
  starter: {
    bg: 'bg-slate-50',
    border: 'border-slate-200',
    accent: 'text-slate-600',
    button: 'bg-slate-600 hover:bg-slate-700',
  },
  plus: {
    bg: 'bg-emerald-50',
    border: 'border-emerald-300',
    accent: 'text-emerald-600',
    button: 'bg-emerald-600 hover:bg-emerald-700',
  },
  pro: {
    bg: 'bg-purple-50',
    border: 'border-purple-300',
    accent: 'text-purple-600',
    button: 'bg-purple-600 hover:bg-purple-700',
  },
};

// Tier labels
export const TIER_LABELS = {
  starter: 'Starter',
  plus: 'Plus',
  pro: 'Pro',
};

// Topic icons (fallback) - V2: Added meditation and counseling
export const TOPIC_ICONS = {
  career: '💼',
  money: '💰',
  health: '🏥',
  marriage: '💑',
  children: '👶',
  love: '💕',
  business: '🚀',
  travel: '✈️',
  property: '🏠',
  mental_health: '🧠',
  spiritual: '🙏',
  legal: '⚖️',
  meditation: '🧘',
  counseling: '💬',
};

// Telemetry helper - V2: Always includes flow_version
export const trackEvent = async (eventName, properties = {}, token = null) => {
  try {
    await apiSimplified.post('/telemetry', {
      event_name: eventName,
      properties: {
        ...properties,
        flow_version: properties.flow_version || 'simplified_v2',
      },
    }, token);
  } catch (e) {
    console.warn('Telemetry failed:', e);
  }
};

// Modality labels for display - V2: Astro/spiritual/healing only
export const MODALITY_LABELS = {
  vedic_astrologer: 'Vedic Astrologer',
  western_astrologer: 'Western Astrologer',
  numerologist: 'Numerologist',
  tarot: 'Tarot Reader',
  palmist: 'Palmist',
  psychic: 'Psychic',
  healer: 'Healer',
  spiritual_guide: 'Spiritual Guide',
  meditation_guru: 'Meditation Guru',
  life_coach: 'Life Coach',
  relationship_counselor: 'Relationship Counselor',
  marriage_counselor: 'Marriage Counselor',
  wellness_counselor: 'Wellness Counselor',
  career_counselor: 'Career Counselor',
};
