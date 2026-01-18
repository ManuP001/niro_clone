import React from 'react';
import { BACKEND_URL } from '../../../config';

// API helper for V2 endpoints
export const apiV2 = {
  baseUrl: `${BACKEND_URL}/api/v2`,
  
  async get(endpoint, token) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
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
      throw new Error(`API Error: ${response.status}`);
    }
    return response.json();
  },
};

// Topic configuration
export const TOPICS = {
  career: { label: 'Career & Work', icon: '💼', color: 'blue' },
  relationships: { label: 'Love & Relationships', icon: '💕', color: 'pink' },
  money: { label: 'Money & Finance', icon: '💰', color: 'yellow' },
  health: { label: 'Health & Wellbeing', icon: '⚕️', color: 'green' },
  family: { label: 'Family & Home', icon: '🏠', color: 'purple' },
  children: { label: 'Children & Education', icon: '🧒', color: 'orange' },
};

// Urgency configuration
export const URGENCY_LEVELS = {
  low: { label: 'Just exploring options', description: 'No rush, looking for insights' },
  medium: { label: 'Need clarity soon', description: 'Within the next few weeks' },
  high: { label: 'Urgent — affecting me now', description: 'Need guidance immediately' },
};

// Decision ownership configuration
export const DECISION_OWNERSHIP = {
  me: { label: 'Me alone', description: 'I make this decision' },
  family: { label: 'Family/others involved', description: 'Others have a say' },
  both: { label: 'Both me and family', description: 'Joint decision' },
};

// Format price
export const formatPrice = (priceInr) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(priceInr);
};

// Get branch label
export const getBranchLabel = (branch) => {
  const labels = {
    remedies_only: 'Self-Guided',
    consult_only: 'Consultation Only',
    combined: 'Full Package',
  };
  return labels[branch] || branch;
};

// Get remedy category label
export const getRemedyCategoryLabel = (category) => {
  const labels = {
    astrological: 'Astrological',
    spiritual: 'Spiritual',
    healing: 'Healing',
  };
  return labels[category] || category;
};

// Get remedy category icon
export const getRemedyCategoryIcon = (category) => {
  const icons = {
    astrological: '🪐',
    spiritual: '🙏',
    healing: '💫',
  };
  return icons[category] || '✨';
};
