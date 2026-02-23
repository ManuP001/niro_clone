import React, { useEffect, useState } from 'react';
import { colors, shadows, borderRadius } from './theme';
import { SparklesIcon, PhoneIcon, ConsultIcon, ShieldIcon } from './icons';
import { trackEvent } from './utils';
import { getBackendUrl } from '../../../config';
import ResponsiveHeader from './ResponsiveHeader';
import AppFooter from './AppFooter';
import BannerCarousel from './BannerCarousel';
import { ScrollReveal } from '../../../hooks/useScrollReveal';

/**
 * HomeScreen V12 - Consolidated App Experience
 * 
 * Changes from V11:
 * - Replaced full-width hero with BannerCarousel
 * - Cleaner mobile-first layout
 * - Banner carousel with auto-scroll
 * - Ready for PWA usage
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
  isAuthenticated,
  user,
  onLoginClick,
  mode = 'full',
  onTopicSelect,
  enabledTopicIds,
}) {
  // Handle CTA click - schedule a free call
  const handleCtaClick = () => {
    if (onTalkToHuman) {
      onTalkToHuman();
    } else if (onNavigate) {
      onNavigate('schedule');
    }
  };
  
  // State for dynamic homepage data
  const [lifeSituations, setLifeSituations] = useState(DEFAULT_LIFE_SITUATIONS);
  const [dataSource, setDataSource] = useState('defaults');
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredSituations, setFilteredSituations] = useState(DEFAULT_LIFE_SITUATIONS);

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
            setFilteredSituations(result.data);
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

  // Filter topics based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredSituations(lifeSituations);
      return;
    }

    const query = searchQuery.toLowerCase().trim();
    const filtered = lifeSituations.map(situation => {
      // Check if category title matches
      const categoryMatches = situation.title.toLowerCase().includes(query) ||
                             (situation.helperCopy && situation.helperCopy.toLowerCase().includes(query));
      
      // Filter tiles within the category
      const matchingTiles = situation.tiles.filter(tile => 
        tile.shortTitle?.toLowerCase().includes(query) ||
        tile.id?.toLowerCase().includes(query)
      );

      // Include category if it matches or has matching tiles
      if (categoryMatches) {
        return situation; // Return full category if title matches
      } else if (matchingTiles.length > 0) {
        return { ...situation, tiles: matchingTiles };
      }
      return null;
    }).filter(Boolean);

    setFilteredSituations(filtered);
  }, [searchQuery, lifeSituations]);

  useEffect(() => {
    trackEvent('home_viewed', { flow_version: 'v10_redesign', data_source: dataSource }, token);
  }, [token, dataSource]);

  const handleTileClick = (tileId, tileData) => {
    trackEvent('tile_clicked', { tile_id: tileId, has_linked_package: !!tileData?.linkedPackageId }, token);
    if (mode === 'picker') {
      if (onTopicSelect) onTopicSelect(tileId);
      return;
    }
    // If tile has a linked package, navigate to package landing page
    if (tileData?.linkedPackageId) {
      onNavigate('packageLanding', { packageId: tileData.linkedPackageId, tileData });
    } else {
      onNavigate('topic', { topicId: tileId });
    }
  };

  // In picker mode, filter tiles to only those in the enabledTopicIds allowlist
  const displaySituations = (mode === 'picker' && enabledTopicIds)
    ? filteredSituations
        .map(s => ({ ...s, tiles: s.tiles.filter(t => enabledTopicIds.includes(t.id)) }))
        .filter(s => s.tiles.length > 0)
    : filteredSituations;

  return (
    <div
      className={`${mode !== 'picker' ? 'min-h-screen' : ''} ${hasBottomNav && mode !== 'picker' ? 'pb-20 md:pb-0' : ''}`}
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Responsive Header - Desktop Navigation (full mode only) */}
      {mode !== 'picker' && (
        <ResponsiveHeader
          onNavigate={onNavigate}
          onOpenProfile={onOpenProfile}
          onTabChange={onTabChange}
          ctaText="Get a Free 10 mins consultation"
          onCtaClick={handleCtaClick}
        />
      )}

      {/* Banner Carousel (full mode only) */}
      {mode !== 'picker' && (
        <BannerCarousel
          onBannerClick={(action) => {
            if (action === 'schedule') {
              onNavigate('schedule');
            } else if (action === 'experts') {
              onNavigate('experts');
            } else if (action === 'remedies') {
              onNavigate('remedies');
            }
          }}
        />
      )}

      {/* Life Topics Section Header with Search */}
      <div className="px-4 md:px-8 lg:px-12 pt-4 mb-4 md:mb-6" id="topics-section">
        <div className="max-w-5xl mx-auto">
          {mode === 'picker' ? (
            <h2
              className="text-lg sm:text-xl font-semibold text-center mb-4"
              style={{ color: colors.text.dark }}
            >
              What's on your mind?
            </h2>
          ) : (
          <h2
            className="text-lg sm:text-xl md:text-2xl font-semibold text-center mb-4 md:mb-6"
            style={{ color: colors.text.dark }}
          >
            Choose the area of life you need clarity <span style={{ fontStyle: 'italic' }}>on today.</span>
          </h2>
          )}
          
          {/* Search/Filter Input */}
          <div className="relative max-w-md mx-auto mb-6">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg 
                className="w-5 h-5" 
                style={{ color: colors.text.muted }}
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Search topics... (e.g., career, love, health)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-10 py-3 rounded-xl border text-sm md:text-base transition-all focus:outline-none focus:ring-2 focus:border-transparent"
              style={{
                backgroundColor: '#FFFFFF',
                borderColor: colors.ui.borderDark,
                color: colors.text.dark,
                '--tw-ring-color': colors.teal.primary,
              }}
              data-testid="topics-search-input"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute inset-y-0 right-0 pr-4 flex items-center"
                data-testid="clear-search-btn"
              >
                <svg 
                  className="w-5 h-5 hover:opacity-70 transition-opacity" 
                  style={{ color: colors.text.muted }}
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
          
          {/* Search Results Count */}
          {searchQuery && (
            <p 
              className="text-center text-sm mb-4"
              style={{ color: colors.text.muted }}
              data-testid="search-results-count"
            >
              {filteredSituations.length === 0 
                ? 'No topics found. Try a different search term.'
                : `Found ${filteredSituations.reduce((acc, s) => acc + s.tiles.length, 0)} topics in ${filteredSituations.length} categories`
              }
            </p>
          )}
        </div>
      </div>

      {/* Life Situations - Category Cards with Responsive Grid and Scroll Reveal */}
      <div className="px-4 md:px-8 lg:px-12 pb-8 md:pb-12">
        <div className="max-w-5xl mx-auto">
          {/* Desktop: Show all categories in a grid layout */}
          <div className="hidden md:grid md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
            {displaySituations.map((situation, index) => (
              <ScrollReveal
                key={situation.id}
                animation="up"
                delay={Math.min(index * 100, 400)}
              >
                <CategoryModule
                  situation={situation}
                  onTileClick={handleTileClick}
                  isDesktop={true}
                />
              </ScrollReveal>
            ))}
          </div>

          {/* Mobile: Stack categories vertically */}
          <div className="md:hidden space-y-4">
            {displaySituations.map((situation, index) => (
              <ScrollReveal
                key={situation.id}
                animation="up"
                delay={Math.min(index * 100, 300)}
              >
                <CategoryModule
                  situation={situation}
                  onTileClick={handleTileClick}
                  isDesktop={false}
                />
              </ScrollReveal>
            ))}
          </div>
        </div>
      </div>

      {/* Desktop Footer (full mode only) */}
      {mode !== 'picker' && <AppFooter onNavigate={onTabChange} />}
    </div>
  );
}
