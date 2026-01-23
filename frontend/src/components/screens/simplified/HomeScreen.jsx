import React, { useEffect } from 'react';
import { colors } from './theme';
import { SparklesIcon, ConsultIcon } from './icons';
import { trackEvent } from './utils';
import TileCard from './TileCard';

/**
 * HomeScreen V4 - Revamped with animated logo, 3 life situations, 18 tiles
 * - Fixed header with animated Niro logo
 * - Only tiles scroll
 * - Premium minimal design matching other screens
 */

// Base styling constants (same as landing page)
const BASE_BG = '#FAFAFA';

// 3 Life Situations with 6 subtopics each = 18 tiles
const LIFE_SITUATIONS = [
  {
    id: 'love',
    title: 'Love & Relationships',
    tiles: [
      { id: 'relationship_healing', shortTitle: 'Healing', iconType: 'healing' },
      { id: 'family_relationships', shortTitle: 'Family', iconType: 'family' },
      { id: 'dating_compatibility', shortTitle: 'Dating', iconType: 'heart' },
      { id: 'marriage_planning', shortTitle: 'Marriage', iconType: 'rings' },
      { id: 'communication_trust', shortTitle: 'Trust', iconType: 'chat' },
      { id: 'breakup_closure', shortTitle: 'Closure', iconType: 'breakup' },
    ]
  },
  {
    id: 'career',
    title: 'Career & Money',
    tiles: [
      { id: 'career_clarity', shortTitle: 'Clarity', iconType: 'compass' },
      { id: 'job_transition', shortTitle: 'Job Change', iconType: 'briefcase' },
      { id: 'money_stability', shortTitle: 'Money', iconType: 'wallet' },
      { id: 'work_stress', shortTitle: 'Work Stress', iconType: 'stress' },
      { id: 'office_politics', shortTitle: 'Office', iconType: 'office' },
      { id: 'big_decision_timing', shortTitle: 'Timing', iconType: 'clock' },
    ]
  },
  {
    id: 'health',
    title: 'Health & Wellness',
    tiles: [
      { id: 'healing_journey', shortTitle: 'Healing', iconType: 'healing' },
      { id: 'stress_management', shortTitle: 'Stress', iconType: 'stress' },
      { id: 'energy_balance', shortTitle: 'Energy', iconType: 'energy' },
      { id: 'sleep_reset', shortTitle: 'Sleep', iconType: 'sleep' },
      { id: 'emotional_recovery', shortTitle: 'Emotional', iconType: 'emotional' },
      { id: 'womens_wellness', shortTitle: 'Wellness', iconType: 'wellness' },
    ]
  }
];

// Animated Logo Component (from Splash Screen)
function AnimatedLogo() {
  return (
    <div className="relative w-24 h-24 mx-auto">
      {/* Animated Ring */}
      <svg 
        className="absolute inset-0 w-full h-full animate-spin-slow" 
        viewBox="0 0 160 160"
        style={{ animationDuration: '20s' }}
      >
        <g stroke="rgba(62,130,122,0.3)" strokeWidth="1" fill="none">
          <polygon points="80,8 100,25 120,25 112,48 120,72 100,72 80,88 60,72 40,72 48,48 40,25 60,25" />
        </g>
        <g fill="rgba(62,130,122,0.5)">
          <circle cx="80" cy="8" r="2.5" />
          <circle cx="100" cy="25" r="1.5" />
          <circle cx="120" cy="25" r="2" />
          <circle cx="112" cy="48" r="1.5" />
          <circle cx="120" cy="72" r="2" />
          <circle cx="100" cy="72" r="1.5" />
          <circle cx="80" cy="88" r="2.5" />
          <circle cx="60" cy="72" r="1.5" />
          <circle cx="40" cy="72" r="2" />
          <circle cx="48" cy="48" r="1.5" />
          <circle cx="40" cy="25" r="2" />
          <circle cx="60" cy="25" r="1.5" />
        </g>
      </svg>
      
      {/* Inner Glow */}
      <div 
        className="absolute inset-4 rounded-full"
        style={{ 
          background: 'radial-gradient(circle, rgba(62,130,122,0.1) 0%, transparent 100%)',
        }}
      />
      
      {/* Logo Text */}
      <div className="absolute inset-0 flex items-center justify-center">
        <span 
          className="text-3xl font-bold tracking-wide"
          style={{ 
            fontFamily: "'Kumbh Sans', 'Inter', sans-serif",
            background: colors.logo.gradient,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          niro
        </span>
      </div>
    </div>
  );
}

// Minimalist Tile Icon Component
function MinimalistTileIcon({ type }) {
  const iconStyle = { 
    color: colors.teal.primary,
    strokeWidth: 1.5,
  };

  const icons = {
    // Love
    healing: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <path d="M19.5 13.5L12 21l-7.5-7.5a5.5 5.5 0 0 1 7.5-8 5.5 5.5 0 0 1 7.5 8z" />
        <path d="M12 13l2-3 2 4 2-3" />
      </svg>
    ),
    family: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <circle cx="9" cy="7" r="3" />
        <circle cx="17" cy="7" r="2" />
        <path d="M5 21v-2a4 4 0 0 1 4-4h2" />
        <path d="M15 21v-2a3 3 0 0 1 3-3" />
        <circle cx="12" cy="17" r="2" />
      </svg>
    ),
    heart: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
      </svg>
    ),
    rings: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <circle cx="9" cy="12" r="5" />
        <circle cx="15" cy="12" r="5" />
      </svg>
    ),
    chat: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        <line x1="9" y1="10" x2="15" y2="10" />
      </svg>
    ),
    breakup: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M12 22V12" />
        <path d="M8 9l8 6" />
      </svg>
    ),
    // Career
    compass: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <circle cx="12" cy="12" r="10" />
        <polygon points="16.24,7.76 14.12,14.12 7.76,16.24 9.88,9.88" />
      </svg>
    ),
    briefcase: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
      </svg>
    ),
    wallet: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4" />
        <path d="M3 5v14a2 2 0 0 0 2 2h16v-5" />
        <path d="M18 12a2 2 0 0 0 0 4h4v-4h-4z" />
      </svg>
    ),
    stress: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <circle cx="12" cy="12" r="10" />
        <path d="M8 15s1.5 2 4 2 4-2 4-2" />
        <line x1="9" y1="9" x2="9.01" y2="9" />
        <line x1="15" y1="9" x2="15.01" y2="9" />
      </svg>
    ),
    office: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <rect x="4" y="2" width="16" height="20" rx="2" />
        <line x1="9" y1="6" x2="15" y2="6" />
        <line x1="9" y1="10" x2="15" y2="10" />
        <line x1="9" y1="14" x2="12" y2="14" />
      </svg>
    ),
    clock: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <circle cx="12" cy="12" r="10" />
        <polyline points="12,6 12,12 16,14" />
      </svg>
    ),
    // Health
    energy: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <polygon points="13,2 3,14 12,14 11,22 21,10 12,10" />
      </svg>
    ),
    sleep: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
      </svg>
    ),
    emotional: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5" />
        <path d="M8.5 8.5v.01" />
        <path d="M16 15.5a3.5 3.5 0 0 1-8 0" />
      </svg>
    ),
    wellness: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <path d="M12 2a4 4 0 0 0-4 4c0 2.5 4 6 4 6s4-3.5 4-6a4 4 0 0 0-4-4z" />
        <path d="M12 12v10" />
        <path d="M8 17c-2 1-4 0-4-2s2-3 4-2" />
        <path d="M16 17c2 1 4 0 4-2s-2-3-4-2" />
      </svg>
    ),
  };

  return icons[type] || icons.heart;
}

// Minimalist Tile Component
function MinimalistTile({ tile, onClick }) {
  return (
    <button
      onClick={() => onClick(tile.id)}
      data-testid={`tile-${tile.id}`}
      className="flex flex-col items-center justify-center w-24 h-24 rounded-2xl transition-all active:scale-[0.96] hover:shadow-md"
      style={{ 
        backgroundColor: '#FFFFFF',
        border: '1px solid rgba(0,0,0,0.06)',
      }}
    >
      <div className="mb-2">
        <MinimalistTileIcon type={tile.iconType} />
      </div>
      <span 
        className="text-xs font-medium text-center px-1 leading-tight"
        style={{ color: colors.text.dark }}
      >
        {tile.shortTitle}
      </span>
    </button>
  );
}

export default function HomeScreen({ 
  token, 
  hasBottomNav, 
  onNavigate, 
  onChatWithMira,
  onTalkToHuman,
}) {

  useEffect(() => {
    trackEvent('home_viewed', { flow_version: 'v4_revamp' }, token);
  }, [token]);

  const handleTileClick = (tileId) => {
    trackEvent('tile_clicked', { tile_id: tileId }, token);
    onNavigate('topic', { topicId: tileId });
  };

  return (
    <div 
      className={`min-h-screen flex flex-col ${hasBottomNav ? 'pb-20' : ''}`}
      style={{ backgroundColor: BASE_BG }}
    >
      {/* Fixed Header with Animated Logo */}
      <header className="flex-shrink-0 pt-6 pb-4 px-5">
        {/* Animated Logo */}
        <AnimatedLogo />
        
        {/* CTA Buttons - Smaller */}
        <div className="flex gap-2 mt-4">
          <button
            onClick={onChatWithMira}
            className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl font-medium text-xs transition-all active:scale-[0.98]"
            style={{ 
              backgroundColor: colors.gold.primary,
              color: colors.text.dark,
            }}
            data-testid="chat-with-mira-btn"
          >
            <SparklesIcon className="w-3.5 h-3.5" />
            Chat with Mira (AI Astrologer)
          </button>

          <button
            onClick={onTalkToHuman}
            className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl font-medium text-xs transition-all active:scale-[0.98]"
            style={{ 
              backgroundColor: '#FFFFFF',
              color: colors.text.dark,
              border: '1px solid rgba(0,0,0,0.1)',
            }}
            data-testid="talk-to-expert-btn"
          >
            <ConsultIcon className="w-3.5 h-3.5" />
            Talk to Expert
          </button>
        </div>
      </header>

      {/* Scrollable Tiles Section */}
      <div className="flex-1 overflow-y-auto px-5">
        {/* Section Title */}
        <div className="mb-5">
          <p 
            className="text-base font-medium text-center"
            style={{ color: colors.text.dark }}
          >
            Choose a life topic that feels the most uncertain right now
          </p>
        </div>

        {/* Life Situations */}
        {LIFE_SITUATIONS.map((situation) => (
          <div key={situation.id} className="mb-6">
            {/* Category Title */}
            <h3 
              className="text-sm font-semibold mb-3"
              style={{ color: colors.text.secondary }}
            >
              {situation.title}
            </h3>
            
            {/* 3x2 Grid of Tiles */}
            <div className="grid grid-cols-3 gap-3">
              {situation.tiles.map((tile) => (
                <MinimalistTile 
                  key={tile.id}
                  tile={tile}
                  onClick={handleTileClick}
                />
              ))}
            </div>
          </div>
        ))}

        {/* Extra scroll padding */}
        <div className="h-8" />
      </div>
    </div>
  );
}
