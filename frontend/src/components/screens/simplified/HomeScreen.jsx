import React, { useEffect, useState } from 'react';
import { colors, shadows, borderRadius } from './theme';
import { SparklesIcon, PhoneIcon, ConsultIcon, ShieldIcon } from './icons';
import { trackEvent } from './utils';
import { getBackendUrl } from '../../../config';

/**
 * HomeScreen V10 - Redesigned for niro-final-marquee
 * 
 * Changes from V6:
 * - New Lexend font and teal/peach/cream color scheme
 * - Responsive layout (mobile-first, desktop-enhanced)
 * - Removed phone-frame constraint
 * - Updated CTAs and styling to match new design
 */

// Default fallback data
const DEFAULT_LIFE_SITUATIONS = [
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
      { id: 'health_timing', shortTitle: 'Timing', iconType: 'healing' },
      { id: 'emotional_wellbeing', shortTitle: 'Emotional', iconType: 'emotional' },
      { id: 'recovery_support', shortTitle: 'Recovery', iconType: 'wellness' },
    ]
  }
];

// Niro Logo Component (new design)
function NiroLogo({ size = 'md' }) {
  const sizes = {
    sm: 'text-2xl',
    md: 'text-3xl',
    lg: 'text-4xl',
  };
  
  return (
    <span 
      className={`font-bold tracking-tight ${sizes[size]}`}
      style={{ 
        fontFamily: "'Lexend', sans-serif",
        color: colors.teal.dark,
      }}
    >
      niro
    </span>
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

// Minimalist Tile Component - Updated for new design
function MinimalistTile({ tile, onClick }) {
  return (
    <button
      onClick={() => onClick(tile.id, tile)}
      data-testid={`tile-${tile.id}`}
      className="flex flex-col items-center justify-center w-full aspect-[1.1] rounded-xl transition-all duration-300 hover:shadow-md hover:-translate-y-1 active:scale-[0.96]"
      style={{ 
        backgroundColor: '#FFFFFF',
        border: '1px solid rgba(74, 155, 142, 0.1)',
        boxShadow: shadows.card,
      }}
    >
      <div className="mb-1">
        <MinimalistTileIcon type={tile.iconType} />
      </div>
      <span 
        className="text-[11px] font-medium text-center px-1 leading-tight"
        style={{ color: colors.text.dark }}
      >
        {tile.shortTitle}
      </span>
    </button>
  );
}

// Category Module Component - Updated for new design
function CategoryModule({ situation, onTileClick }) {
  return (
    <div 
      className="rounded-2xl p-4 mb-4 transition-all duration-300"
      style={{ 
        backgroundColor: '#FFFFFF',
        border: '1px solid rgba(74, 155, 142, 0.08)',
        boxShadow: shadows.card,
      }}
    >
      {/* Section Title */}
      <div className="mb-3">
        <h3 
          className="text-base font-semibold"
          style={{ color: colors.text.dark }}
        >
          {situation.title}
        </h3>
        {situation.helperCopy && (
          <p 
            className="text-xs mt-0.5"
            style={{ color: colors.text.muted }}
          >
            {situation.helperCopy}
          </p>
        )}
      </div>
      
      {/* Grid of Tiles - Responsive: 3 cols mobile, 6 cols desktop */}
      <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
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
  onOpenProfile,
}) {
  // State for dynamic homepage data
  const [lifeSituations, setLifeSituations] = useState(DEFAULT_LIFE_SITUATIONS);
  const [dataSource, setDataSource] = useState('defaults');

  // Fetch homepage data from API
  useEffect(() => {
    const fetchHomepageData = async () => {
      try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/api/admin/public/homepage-data`);
        if (response.ok) {
          const result = await response.json();
          if (result.ok && result.data && result.data.length > 0) {
            setLifeSituations(result.data);
            setDataSource(result.source || 'database');
          }
        }
      } catch (error) {
        console.log('Using default homepage data:', error.message);
        // Keep using defaults on error
      }
    };
    
    fetchHomepageData();
  }, []);

  useEffect(() => {
    trackEvent('home_viewed', { flow_version: 'v6_premium', data_source: dataSource }, token);
  }, [token, dataSource]);

  const handleTileClick = (tileId, tileData) => {
    trackEvent('tile_clicked', { tile_id: tileId, has_linked_package: !!tileData?.linkedPackageId }, token);
    // If tile has a linked package, navigate to package landing page
    if (tileData?.linkedPackageId) {
      onNavigate('packageLanding', { packageId: tileData.linkedPackageId, tileData });
    } else {
      onNavigate('topic', { topicId: tileId });
    }
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
          background: 'linear-gradient(180deg, #3E827A 0%, #4A8F87 100%)',
        }}
      >
        {/* Profile Button - Top Right */}
        <div className="absolute top-4 right-4 z-50">
          <button
            onClick={onOpenProfile}
            className="w-9 h-9 rounded-full flex items-center justify-center transition-all active:scale-95"
            style={{ 
              backgroundColor: 'rgba(255,255,255,0.2)',
              border: '1px solid rgba(255,255,255,0.3)',
            }}
            data-testid="profile-button"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </button>
        </div>

        {/* Animated Logo */}
        <AnimatedLogo />
        
        {/* Premium CTA Area */}
        <div className="mt-4">
          {/* CTAs - Talk to Expert is Primary */}
          <div className="flex gap-2">
            <button
              onClick={onTalkToHuman}
              className="flex-1 flex items-center justify-center gap-1.5 py-3 rounded-xl font-medium text-sm transition-all active:scale-[0.98]"
              style={{ 
                backgroundColor: '#EFE1A9',
                color: colors.text.dark,
              }}
              data-testid="talk-to-expert-btn"
            >
              <PhoneIcon className="w-4 h-4" />
              Talk to Expert
            </button>

            <button
              onClick={onChatWithMira}
              className="flex-1 flex items-center justify-center gap-1.5 py-3 rounded-xl font-medium text-sm transition-all active:scale-[0.98]"
              style={{ 
                backgroundColor: 'rgba(255,255,255,0.95)',
                color: colors.text.dark,
              }}
              data-testid="chat-with-mira-btn"
            >
              <SparklesIcon className="w-4 h-4" />
              Chat with Mira (AI)
            </button>
          </div>
          
        </div>

        {/* Section Title - Now inside header for consistent background */}
        <div className="mt-4">
          <p 
            className="text-sm font-medium text-center"
            style={{ color: 'rgba(255,255,255,0.9)' }}
          >
            Choose a life topic that feels the most uncertain right now
          </p>
        </div>
      </header>

      {/* Scrollable Tiles Section - Reduced Bottom Padding */}
      <div className="px-4 pt-3" style={{ paddingBottom: '12px' }}>

        {/* Life Situations - Premium Module Cards - Now Dynamic */}
        {lifeSituations.map((situation) => (
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
