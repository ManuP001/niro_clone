import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { colors, shadows } from './theme';
import { getBackendUrl } from '../../../config';
import PublicNavHeader from './PublicNavHeader';

/**
 * PublicTopicsPage - Publicly accessible life topics page (no login required)
 * Shows all life topic categories and tiles
 * Clicking a tile navigates to the public topic landing page (no login required)
 */

// Topics that have packages available (all others are "Coming Soon")
const TOPICS_WITH_PACKAGES = [
  'career_clarity',
  'marriage_planning', 
  'stress_management',
  'relationship_healing'
];

// Default fallback data with new Fertility category
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
  },
  {
    id: 'fertility',
    title: 'Fertility & Family Planning',
    helperCopy: 'Family planning, baby naming, delivery timing',
    comingSoon: true,
    tiles: [
      { id: 'fertility_support', shortTitle: 'Fertility Support', iconType: 'fertility', comingSoon: true },
      { id: 'baby_naming_muhurat', shortTitle: 'Baby Naming & Muhurat', iconType: 'baby', comingSoon: true },
      { id: 'delivery_muhurat', shortTitle: 'Delivery Muhurat', iconType: 'calendar', comingSoon: true },
      { id: 'teenagers_mental_health', shortTitle: 'Teenagers Mental Health', iconType: 'mental_health', comingSoon: true },
    ]
  }
];

// Minimalist Tile Icon Component
function MinimalistTileIcon({ type, comingSoon }) {
  const iconStyle = { 
    color: comingSoon ? colors.text.muted : colors.teal.primary,
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
    // Fertility & Family Planning
    fertility: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <circle cx="12" cy="8" r="5" />
        <path d="M12 13v8" />
        <path d="M9 18h6" />
      </svg>
    ),
    baby: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <circle cx="12" cy="10" r="6" />
        <path d="M12 16v4" />
        <path d="M8 20h8" />
        <circle cx="9" cy="9" r="1" fill="currentColor" />
        <circle cx="15" cy="9" r="1" fill="currentColor" />
        <path d="M10 12h4" />
      </svg>
    ),
    calendar: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
        <path d="M8 14h.01" />
        <path d="M12 14h.01" />
        <path d="M16 14h.01" />
        <path d="M8 18h.01" />
        <path d="M12 18h.01" />
      </svg>
    ),
    mental_health: (
      <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={iconStyle}>
        <path d="M12 2a8 8 0 0 0-8 8c0 3 2 5 4 6v4a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-4c2-1 4-3 4-6a8 8 0 0 0-8-8z" />
        <path d="M12 8v4" />
        <path d="M10 10h4" />
      </svg>
    ),
  };

  return icons[type] || icons.heart;
}

// Minimalist Tile Component
function MinimalistTile({ tile, onClick, comingSoon }) {
  return (
    <button
      onClick={() => !comingSoon && onClick(tile.id, tile)}
      disabled={comingSoon}
      data-testid={`tile-${tile.id}`}
      className={`flex flex-col items-center justify-center w-full aspect-[1.1] rounded-xl transition-all duration-300 ${
        comingSoon 
          ? 'cursor-not-allowed opacity-60' 
          : 'hover:shadow-md hover:-translate-y-1 active:scale-[0.96]'
      }`}
      style={{ 
        backgroundColor: '#FFFFFF',
        border: '1px solid rgba(74, 155, 142, 0.1)',
        boxShadow: shadows.card,
      }}
    >
      <div className="mb-1 relative">
        <MinimalistTileIcon type={tile.iconType} comingSoon={comingSoon} />
      </div>
      <span 
        className="text-[11px] font-medium text-center px-1 leading-tight"
        style={{ color: comingSoon ? colors.text.muted : colors.text.dark }}
      >
        {tile.shortTitle}
      </span>
      {comingSoon && (
        <span 
          className="text-[8px] mt-1 px-2 py-0.5 rounded-full"
          style={{ 
            backgroundColor: colors.peach.soft, 
            color: colors.text.secondary 
          }}
        >
          Coming Soon
        </span>
      )}
    </button>
  );
}

// Category Module Component
function CategoryModule({ situation, onTileClick }) {
  const isComingSoon = situation.comingSoon;
  
  return (
    <div 
      className="rounded-2xl p-4 transition-all duration-300 h-full"
      style={{ 
        backgroundColor: '#FFFFFF',
        border: isComingSoon ? `2px dashed ${colors.peach.primary}` : '1px solid rgba(74, 155, 142, 0.08)',
        boxShadow: shadows.card,
      }}
    >
      {/* Section Title */}
      <div className="mb-3 flex items-center justify-between">
        <div>
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
        {isComingSoon && (
          <span 
            className="text-xs px-3 py-1 rounded-full font-medium"
            style={{ 
              backgroundColor: colors.peach.primary, 
              color: colors.text.dark 
            }}
          >
            Coming Soon
          </span>
        )}
      </div>
      
      {/* Grid of Tiles */}
      <div className="grid gap-2 grid-cols-3 md:grid-cols-4">
        {situation.tiles.map((tile) => (
          <MinimalistTile 
            key={tile.id}
            tile={tile}
            onClick={onTileClick}
            comingSoon={isComingSoon || tile.comingSoon}
          />
        ))}
      </div>
    </div>
  );
}

export default function PublicTopicsPage({ isAuthenticated }) {
  const navigate = useNavigate();
  const [lifeSituations, setLifeSituations] = useState(DEFAULT_LIFE_SITUATIONS);
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
            // Merge API data with default fertility category
            const apiData = result.data;
            const hasFertility = apiData.some(s => s.id === 'fertility');
            if (!hasFertility) {
              apiData.push(DEFAULT_LIFE_SITUATIONS.find(s => s.id === 'fertility'));
            }
            setLifeSituations(apiData);
            setFilteredSituations(apiData);
          }
        }
      } catch (error) {
        console.log('Using default homepage data:', error.message);
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
      const categoryMatches = situation.title.toLowerCase().includes(query) ||
                             (situation.helperCopy && situation.helperCopy.toLowerCase().includes(query));
      
      const matchingTiles = situation.tiles.filter(tile => 
        tile.shortTitle?.toLowerCase().includes(query) ||
        tile.id?.toLowerCase().includes(query)
      );

      if (categoryMatches) {
        return situation;
      } else if (matchingTiles.length > 0) {
        return { ...situation, tiles: matchingTiles };
      }
      return null;
    }).filter(Boolean);

    setFilteredSituations(filtered);
  }, [searchQuery, lifeSituations]);

  const handleTileClick = (tileId, tileData) => {
    // Navigate to public topic landing page (no login required)
    // Login is only required before checkout
    navigate(`/topic/${tileId}`);
  };

  return (
    <div 
      className="min-h-screen"
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Header with Navigation */}
      <PublicNavHeader isAuthenticated={isAuthenticated} />

      {/* Content */}
      <div className="max-w-5xl mx-auto px-4 md:px-8 py-8">
        {/* Page Title */}
        <div className="text-center mb-8">
          <h1 
            className="text-2xl md:text-3xl lg:text-4xl font-bold mb-2"
            style={{ color: colors.text.dark }}
          >
            Life Topics
          </h1>
          <p 
            className="text-sm md:text-base max-w-2xl mx-auto"
            style={{ color: colors.text.secondary }}
          >
            Choose the area of life you need clarity <span style={{ fontStyle: 'italic' }}>on today.</span>
          </p>
        </div>

        {/* Search */}
        <div className="relative max-w-md mx-auto mb-8">
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
            className="text-center text-sm mb-6"
            style={{ color: colors.text.muted }}
            data-testid="search-results-count"
          >
            {filteredSituations.length === 0 
              ? 'No topics found. Try a different search term.'
              : `Found ${filteredSituations.reduce((acc, s) => acc + s.tiles.length, 0)} topics in ${filteredSituations.length} categories`
            }
          </p>
        )}

        {/* Categories Grid */}
        <div className="grid md:grid-cols-2 gap-4 lg:gap-6">
          {filteredSituations.map((situation) => (
            <CategoryModule 
              key={situation.id}
              situation={situation}
              onTileClick={handleTileClick}
            />
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer 
        className="py-8 px-6 text-center mt-8"
        style={{ 
          backgroundColor: colors.background.secondary,
          borderTop: `1px solid ${colors.ui.borderDark}`,
        }}
      >
        <a 
          href="/"
          className="text-2xl font-bold"
          style={{ 
            fontFamily: "'Lexend', sans-serif",
            color: colors.teal.dark,
          }}
        >
          niro
        </a>
        <p 
          className="text-xs mt-4 max-w-md mx-auto"
          style={{ color: colors.text.mutedDark }}
        >
          Niro provides astrology-based guidance across Vedic astrology and healing modalities. 
          Our guidance is not a substitute for medical, legal, or financial advice.
        </p>
      </footer>
    </div>
  );
}
