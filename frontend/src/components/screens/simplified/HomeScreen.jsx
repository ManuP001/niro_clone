import React, { useEffect, useState } from 'react';
import { colors, shadows, borderRadius } from './theme';
import { SparklesIcon, PhoneIcon, ConsultIcon, ShieldIcon } from './icons';
import { trackEvent } from './utils';
import { getBackendUrl } from '../../../config';
import ResponsiveHeader from './ResponsiveHeader';

/**
 * HomeScreen V11 - Phase 3 Responsive Layout
 * 
 * Changes from V10:
 * - Added ResponsiveHeader with desktop navigation
 * - Multi-column grid layouts for desktop
 * - Centered content with max-width containers
 * - Enhanced hero section for larger screens
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

// Category Module Component - Updated for responsive layout
function CategoryModule({ situation, onTileClick, isDesktop = false }) {
  return (
    <div 
      className={`rounded-2xl p-4 ${isDesktop ? '' : 'mb-4'} transition-all duration-300 h-full`}
      style={{ 
        backgroundColor: '#FFFFFF',
        border: '1px solid rgba(74, 155, 142, 0.08)',
        boxShadow: shadows.card,
      }}
    >
      {/* Section Title */}
      <div className="mb-3">
        <h3 
          className="text-base md:text-lg font-semibold"
          style={{ color: colors.text.dark }}
        >
          {situation.title}
        </h3>
        {situation.helperCopy && (
          <p 
            className="text-xs md:text-sm mt-0.5"
            style={{ color: colors.text.muted }}
          >
            {situation.helperCopy}
          </p>
        )}
      </div>
      
      {/* Grid of Tiles - Responsive: 3 cols mobile, different layout on desktop */}
      <div className={`grid gap-2 ${isDesktop ? 'grid-cols-3' : 'grid-cols-3 md:grid-cols-6'}`}>
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
  onTabChange,
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
    trackEvent('home_viewed', { flow_version: 'v10_redesign', data_source: dataSource }, token);
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
      className={`min-h-screen ${hasBottomNav ? 'pb-20 md:pb-0' : ''}`}
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Responsive Header - Desktop Navigation */}
      <ResponsiveHeader
        onNavigate={onNavigate}
        onOpenProfile={onOpenProfile}
        onTabChange={onTabChange}
        ctaText="Get a Free 10 mins consultation"
        onCtaClick={onTalkToHuman}
      />

      {/* Hero Section - Enhanced for Desktop */}
      <header 
        className="relative pt-8 pb-10 md:pt-12 md:pb-16 lg:pt-16 lg:pb-20 px-4 md:px-8 lg:px-12"
        style={{ 
          background: `linear-gradient(180deg, ${colors.teal.primary} 0%, ${colors.teal.soft} 100%)`,
        }}
      >
        {/* Floating shapes for desktop - decorative */}
        <div className="hidden lg:block absolute top-20 left-[10%] w-24 h-24 rounded-full opacity-20 animate-float" 
          style={{ background: `linear-gradient(135deg, ${colors.peach.soft}, ${colors.teal.soft})` }} 
        />
        <div className="hidden lg:block absolute top-32 right-[12%] w-16 h-16 rounded-full opacity-20 animate-float-delayed" 
          style={{ background: `linear-gradient(135deg, ${colors.teal.soft}, ${colors.peach.soft})` }} 
        />
        
        {/* Hero Content - Centered, max-width */}
        <div className="text-center max-w-3xl mx-auto relative z-10">
          <h1 
            className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold mb-4 md:mb-6 leading-tight"
            style={{ color: '#FFFFFF' }}
          >
            Expert astrology guidance,{' '}
            <span style={{ fontStyle: 'italic', fontWeight: 400 }}>
              for as long as you need it.
            </span>
          </h1>
          <p 
            className="text-sm sm:text-base md:text-lg mb-6 md:mb-8 max-w-2xl mx-auto"
            style={{ color: 'rgba(255,255,255,0.9)' }}
          >
            Experienced Vedic astrologers for your most important life decisions — with full support from first understanding to complete clarity.
          </p>
          
          {/* Primary CTA - Larger on desktop */}
          <button
            onClick={onTalkToHuman}
            className="inline-flex items-center gap-2 px-6 md:px-8 py-3 md:py-4 rounded-full font-semibold text-sm md:text-base transition-all hover:shadow-lg hover:-translate-y-0.5 active:scale-[0.98]"
            style={{ 
              backgroundColor: colors.peach.primary,
              color: colors.text.dark,
              boxShadow: shadows.peach,
            }}
            data-testid="hero-cta-btn"
          >
            <svg className="w-4 h-4 md:w-5 md:h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
            </svg>
            Get Your Free 10-Min Call
          </button>
          
          {/* Trust Badges - Responsive layout */}
          <div className="flex flex-wrap items-center justify-center gap-3 md:gap-6 mt-6 md:mt-8 text-xs md:text-sm" style={{ color: 'rgba(255,255,255,0.85)' }}>
            <span className="flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              Only 4.5+ rated astrologers
            </span>
            <span className="flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Unlimited chat with experts
            </span>
            <span className="flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Remedies execution support
            </span>
          </div>
        </div>

        {/* Mobile Profile Button - Only on small screens */}
        <button
          onClick={onOpenProfile}
          className="md:hidden absolute top-4 right-4 w-10 h-10 rounded-full flex items-center justify-center transition-all active:scale-95"
          style={{ 
            backgroundColor: 'rgba(255,255,255,0.2)',
            border: '1px solid rgba(255,255,255,0.3)',
          }}
          data-testid="mobile-profile-button"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </button>
      </header>

      {/* Secondary Actions - Chat with Mira */}
      <div className="px-4 md:px-8 lg:px-12 -mt-4 md:-mt-6 mb-6 md:mb-8">
        <div className="max-w-3xl mx-auto">
          <button
            onClick={onChatWithMira}
            className="w-full flex items-center justify-center gap-2 py-3 md:py-4 rounded-xl font-medium text-sm md:text-base transition-all hover:shadow-md active:scale-[0.98]"
            style={{ 
              backgroundColor: '#FFFFFF',
              color: colors.text.dark,
              boxShadow: shadows.card,
              border: `1px solid ${colors.ui.borderDark}`,
            }}
            data-testid="chat-with-mira-btn"
          >
            <SparklesIcon className="w-4 h-4 md:w-5 md:h-5" style={{ color: colors.teal.primary }} />
            Or chat with Mira (AI Astrology Assistant)
          </button>
        </div>
      </div>

      {/* Life Topics Section Header */}
      <div className="px-4 md:px-8 lg:px-12 mb-4 md:mb-6" id="topics-section">
        <div className="max-w-5xl mx-auto">
          <h2 
            className="text-lg sm:text-xl md:text-2xl font-semibold text-center"
            style={{ color: colors.text.dark }}
          >
            Choose the area of life you need clarity <span style={{ fontStyle: 'italic' }}>on today.</span>
          </h2>
        </div>
      </div>

      {/* Life Situations - Category Cards with Responsive Grid */}
      <div className="px-4 md:px-8 lg:px-12 pb-8 md:pb-12">
        <div className="max-w-5xl mx-auto">
          {/* Desktop: Show all categories in a grid layout */}
          <div className="hidden md:grid md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
            {lifeSituations.map((situation) => (
              <CategoryModule 
                key={situation.id}
                situation={situation}
                onTileClick={handleTileClick}
                isDesktop={true}
              />
            ))}
          </div>
          
          {/* Mobile: Stack categories vertically */}
          <div className="md:hidden space-y-4">
            {lifeSituations.map((situation) => (
              <CategoryModule 
                key={situation.id}
                situation={situation}
                onTileClick={handleTileClick}
                isDesktop={false}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
