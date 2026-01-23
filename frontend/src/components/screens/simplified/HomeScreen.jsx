import React, { useEffect } from 'react';
import { colors } from './theme';
import { SparklesIcon, PhoneIcon, ConsultIcon, ShieldIcon } from './icons';
import { trackEvent } from './utils';

/**
 * HomeScreen V6 - Premium UI Upgrade
 * 
 * Changes from V4:
 * - Reordered 18 tiles (premium + highest intent first)
 * - Reduced bottom whitespace by 60%+
 * - Gradient background (same as onboarding)
 * - Category modules with premium card containers
 * - Premium CTA area with "Talk to Expert" as primary
 * - Trust microcopy under CTAs
 */

// V6 Tile Order - Premium + Highest Intent First
const V6_LIFE_SITUATIONS = [
  {
    id: 'love',
    title: 'Love & Relationships',
    helperCopy: 'Dating, commitment, healing, family dynamics',
    tiles: [
      { id: 'relationship_healing', shortTitle: 'Healing', iconType: 'healing' },
      { id: 'dating_compatibility', shortTitle: 'Dating', iconType: 'heart' },
      { id: 'marriage_planning', shortTitle: 'Marriage', iconType: 'rings' },
      { id: 'communication_trust', shortTitle: 'Trust', iconType: 'chat' },
      { id: 'family_relationships', shortTitle: 'Family', iconType: 'family' },
      { id: 'breakup_closure', shortTitle: 'Closure', iconType: 'breakup' },
    ]
  },
  {
    id: 'career',
    title: 'Career & Money',
    helperCopy: 'Work direction, stability, timing, growth',
    tiles: [
      { id: 'career_clarity', shortTitle: 'Clarity', iconType: 'compass' },
      { id: 'job_transition', shortTitle: 'Job Change', iconType: 'briefcase' },
      { id: 'money_stability', shortTitle: 'Money', iconType: 'wallet' },
      { id: 'big_decision_timing', shortTitle: 'Timing', iconType: 'clock' },
      { id: 'work_stress', shortTitle: 'Work Stress', iconType: 'stress' },
      { id: 'office_politics', shortTitle: 'Office', iconType: 'office' },
    ]
  },
  {
    id: 'health',
    title: 'Health & Wellness',
    helperCopy: 'Stress, recovery, energy, emotional balance',
    tiles: [
      { id: 'stress_management', shortTitle: 'Stress', iconType: 'stress' },
      { id: 'sleep_reset', shortTitle: 'Sleep', iconType: 'sleep' },
      { id: 'energy_balance', shortTitle: 'Energy', iconType: 'energy' },
      { id: 'healing_journey', shortTitle: 'Healing', iconType: 'healing' },
      { id: 'emotional_recovery', shortTitle: 'Emotional', iconType: 'emotional' },
      { id: 'womens_wellness', shortTitle: 'Wellness', iconType: 'wellness' },
    ]
  }
];

// Premium Gradient Background (same as onboarding)
const GRADIENT_BG = 'linear-gradient(180deg, #F8FAF9 0%, #F0F5F3 50%, #E8F0ED 100%)';
const MODULE_BG = 'rgba(255, 255, 255, 0.7)';

// Animated Logo Component (from Splash Screen)
function AnimatedLogo() {
  return (
    <div className="relative w-28 h-28 mx-auto">
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
          className="text-4xl font-bold tracking-wide"
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
      className="flex flex-col items-center justify-center w-full aspect-square rounded-2xl transition-all active:scale-[0.96] hover:shadow-md"
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

// Category Module Component - Premium Card Container
function CategoryModule({ situation, onTileClick }) {
  return (
    <div 
      className="rounded-2xl p-4 mb-4"
      style={{ 
        backgroundColor: MODULE_BG,
        backdropFilter: 'blur(8px)',
        border: '1px solid rgba(255,255,255,0.8)',
        boxShadow: '0 2px 12px rgba(0,0,0,0.03)',
      }}
    >
      {/* Section Title + Helper */}
      <div className="mb-3">
        <h3 
          className="text-sm font-semibold"
          style={{ color: colors.text.dark }}
        >
          {situation.title}
        </h3>
        <p 
          className="text-xs mt-0.5"
          style={{ color: colors.text.secondary }}
        >
          {situation.helperCopy}
        </p>
      </div>
      
      {/* 3x2 Grid of Tiles */}
      <div className="grid grid-cols-3 gap-2.5">
        {situation.tiles.map((tile) => (
          <MinimalistTile 
            key={tile.id}
            tile={tile}
            onClick={onTileClick}
          />
        ))}
      </div>
    </div>
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
    trackEvent('home_viewed', { flow_version: 'v6_premium' }, token);
  }, [token]);

  const handleTileClick = (tileId) => {
    trackEvent('tile_clicked', { tile_id: tileId }, token);
    onNavigate('topic', { topicId: tileId });
  };

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-16' : ''}`}
      style={{ background: GRADIENT_BG }}
    >
      {/* Fixed Header with Animated Logo */}
      <header 
        className="sticky top-0 z-40 pt-6 pb-4 px-5"
        style={{ 
          background: 'linear-gradient(180deg, #F8FAF9 0%, rgba(248,250,249,0.95) 100%)',
        }}
      >
        {/* Animated Logo (Larger) */}
        <AnimatedLogo />
        
        {/* Premium CTA Area */}
        <div className="mt-4">
          {/* CTAs - Talk to Expert is Primary */}
          <div className="flex gap-2">
            <button
              onClick={onTalkToHuman}
              className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl font-medium text-xs transition-all active:scale-[0.98]"
              style={{ 
                backgroundColor: colors.teal.primary,
                color: '#ffffff',
              }}
              data-testid="talk-to-expert-btn"
            >
              <PhoneIcon className="w-3.5 h-3.5" />
              Talk to Expert
            </button>

            <button
              onClick={onChatWithMira}
              className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl font-medium text-xs transition-all active:scale-[0.98]"
              style={{ 
                backgroundColor: 'rgba(255,255,255,0.9)',
                color: colors.text.dark,
                border: '1px solid rgba(0,0,0,0.08)',
              }}
              data-testid="chat-with-mira-btn"
            >
              <SparklesIcon className="w-3.5 h-3.5" />
              Chat with Mira (AI)
            </button>
          </div>
          
        </div>
      </header>

      {/* Scrollable Tiles Section - Reduced Bottom Padding */}
      <div className="px-4 pt-2" style={{ paddingBottom: '12px' }}>
        {/* Section Title */}
        <div className="mb-4">
          <p 
            className="text-sm font-medium text-center"
            style={{ color: colors.text.dark }}
          >
            Choose a life topic that feels the most uncertain right now
          </p>
        </div>

        {/* Life Situations - Premium Module Cards */}
        {V6_LIFE_SITUATIONS.map((situation) => (
          <CategoryModule 
            key={situation.id}
            situation={situation}
            onTileClick={handleTileClick}
          />
        ))}
      </div>
    </div>
  );
}
