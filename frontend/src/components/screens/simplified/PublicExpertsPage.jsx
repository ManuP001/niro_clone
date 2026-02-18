import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { colors, shadows } from './theme';
import { StarIcon, ChevronRightIcon } from './icons';
import { getBackendUrl } from '../../../config';
import PublicNavHeader from './PublicNavHeader';

/**
 * PublicExpertsPage - Publicly accessible experts listing (no login required)
 * Shows all experts with ability to view profiles
 */

export default function PublicExpertsPage({ isAuthenticated, onLoginClick }) {
  const navigate = useNavigate();
  const [experts, setExperts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedModality, setSelectedModality] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const loadExperts = async () => {
      try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/api/simplified/experts/all`);
        if (response.ok) {
          const data = await response.json();
          setExperts(data.experts || []);
        }
      } catch (err) {
        console.error('Failed to load experts:', err);
      } finally {
        setLoading(false);
      }
    };
    loadExperts();
  }, []);

  // Group experts by modality
  const modalities = [...new Set(experts.map(e => e.modality))];
  const modalityLabels = {
    vedic_astrologer: 'Vedic Astrologer',
    western_astrologer: 'Western Astrologer',
    career_coach: 'Career Coach',
    life_coach: 'Life Coach',
    numerologist: 'Numerologist',
    tarot: 'Tarot Reader',
    palmist: 'Palmist',
    psychic: 'Psychic',
    healer: 'Healer',
    spiritual_guide: 'Spiritual Guide',
    relationship_counselor: 'Relationship Counselor',
    marriage_counselor: 'Marriage Counselor',
    financial_advisor: 'Financial Advisor',
    legal_advisor: 'Legal Advisor',
  };

  // Filter by modality and search
  let filteredExperts = selectedModality === 'all' 
    ? experts 
    : experts.filter(e => e.modality === selectedModality);
  
  if (searchQuery.trim()) {
    const query = searchQuery.toLowerCase();
    filteredExperts = filteredExperts.filter(e => 
      e.name.toLowerCase().includes(query) ||
      e.modality_label?.toLowerCase().includes(query) ||
      e.best_for_tags?.some(tag => tag.toLowerCase().includes(query)) ||
      e.life_situation_tags?.some(tag => tag.toLowerCase().includes(query)) ||
      e.method_tags?.some(tag => tag.toLowerCase().includes(query))
    );
  }

  // Group by modality for display
  const groupedExperts = filteredExperts.reduce((acc, expert) => {
    const modality = expert.modality;
    if (!acc[modality]) acc[modality] = [];
    acc[modality].push(expert);
    return acc;
  }, {});

  const handleExpertClick = (expert) => {
    navigate(`/experts/${expert.expert_id}`);
  };

  if (loading) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: colors.background.primary }}
      >
        <div className="text-center">
          <div 
            className="w-12 h-12 border-4 rounded-full animate-spin mx-auto mb-4"
            style={{ borderColor: 'rgba(74,155,142,0.3)', borderTopColor: colors.teal.primary }}
          />
          <p style={{ color: colors.text.muted }}>Loading experts...</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="min-h-screen"
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Header */}
      <header
        className="sticky top-0 z-50"
        style={{
          backgroundColor: 'rgba(251,248,243,0.95)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(0,0,0,0.06)',
        }}
      >
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="flex items-center justify-between h-16 md:h-20">
            {/* Left: Back + Logo */}
            <div className="flex items-center gap-3">
              <button
                onClick={handleBackToHome}
                className="p-2 -ml-2 rounded-full hover:bg-black/5 transition-colors"
                data-testid="back-to-home-btn"
              >
                <svg
                  className="w-5 h-5"
                  style={{ color: colors.text.dark }}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <a href="/" className="flex items-center" data-testid="header-logo">
                <span
                  className="text-3xl md:text-4xl font-bold tracking-tight"
                  style={{
                    fontFamily: "'Lexend', sans-serif",
                    color: colors.teal.dark,
                  }}
                >
                  niro
                </span>
              </a>
            </div>

            {/* Right: CTA */}
            <a
              href={isAuthenticated ? '/app/schedule' : '/login'}
              className="hidden md:flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium transition-all hover:shadow-md hover:-translate-y-0.5"
              style={{
                backgroundColor: colors.teal.primary,
                color: '#ffffff',
              }}
              data-testid="header-cta-btn"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
              </svg>
              Get a free 10 mins consultation
            </a>
          </div>
        </div>
      </header>

      {/* Content Container */}
      <div className="max-w-6xl mx-auto">
        {/* Header Section */}
        <div className="px-4 md:px-8 pt-6 pb-4">
          <h1 
            className="text-2xl md:text-3xl font-bold mb-1"
            style={{ color: colors.text.dark }}
          >
            Our Experts
          </h1>
          <p className="text-sm md:text-base mb-4" style={{ color: colors.text.muted }}>
            Browse our certified astrologers and specialists
          </p>
          
          {/* Search */}
          <div className="mb-4 max-w-md">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search experts..."
              className="w-full px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2"
              style={{ 
                backgroundColor: 'white', 
                border: `1px solid ${colors.ui.borderDark}`,
                color: colors.text.dark,
                '--tw-ring-color': colors.teal.primary,
              }}
              data-testid="experts-search-input"
            />
          </div>
          
          {/* Modality Filter Pills */}
          <div className="flex overflow-x-auto gap-2 pb-2 scrollbar-hide">
            <button
              onClick={() => setSelectedModality('all')}
              className="flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all"
              style={selectedModality === 'all'
                ? { backgroundColor: colors.teal.primary, color: '#ffffff' }
                : { backgroundColor: '#ffffff', color: colors.text.muted, border: `1px solid ${colors.ui.borderDark}` }
              }
              data-testid="filter-all"
            >
              All Experts
            </button>
            {modalities.map((modality) => (
              <button
                key={modality}
                onClick={() => setSelectedModality(modality)}
                className="flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all whitespace-nowrap"
                style={selectedModality === modality
                  ? { backgroundColor: colors.teal.primary, color: '#ffffff' }
                  : { backgroundColor: '#ffffff', color: colors.text.muted, border: `1px solid ${colors.ui.borderDark}` }
                }
                data-testid={`filter-${modality}`}
              >
                {modalityLabels[modality] || modality}
              </button>
            ))}
          </div>
        </div>

        {/* Expert Cards - Responsive Grid */}
        <div className="px-4 md:px-8 py-6">
          {selectedModality === 'all' ? (
            Object.entries(groupedExperts).map(([modality, modalityExperts]) => (
              <div key={modality} className="mb-8">
                <h2 className="text-lg md:text-xl font-semibold mb-4" style={{ color: colors.text.dark }}>
                  {modalityLabels[modality] || modality}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {modalityExperts.map((expert) => (
                    <ExpertCard
                      key={expert.expert_id}
                      expert={expert}
                      onClick={() => handleExpertClick(expert)}
                      modalityLabels={modalityLabels}
                    />
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredExperts.map((expert) => (
                <ExpertCard
                  key={expert.expert_id}
                  expert={expert}
                  onClick={() => handleExpertClick(expert)}
                  modalityLabels={modalityLabels}
                />
              ))}
            </div>
          )}
          
          {filteredExperts.length === 0 && (
            <div className="text-center py-12">
              <p className="text-lg" style={{ color: colors.text.muted }}>No experts found</p>
              <p className="text-sm mt-2" style={{ color: colors.text.muted }}>Try adjusting your search or filters</p>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer 
        className="py-8 px-6 text-center"
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

/**
 * ExpertCard - Expert card component
 */
function ExpertCard({ expert, onClick, modalityLabels }) {
  return (
    <div
      onClick={onClick}
      className="rounded-xl p-4 transition-all active:scale-[0.99] cursor-pointer hover:shadow-md"
      style={{ 
        backgroundColor: '#ffffff',
        border: `1px solid ${colors.ui.borderDark}`,
        boxShadow: shadows.sm,
      }}
      data-testid={`expert-card-${expert.expert_id}`}
    >
      <div className="flex gap-4">
        {/* Avatar */}
        <div 
          className="w-14 h-14 rounded-full flex-shrink-0 overflow-hidden"
          style={{ backgroundColor: colors.gold.cream }}
        >
          {expert.photo_url ? (
            <img 
              src={expert.photo_url} 
              alt={expert.name}
              className="w-full h-full object-cover"
              onError={(e) => { e.target.style.display = 'none'; }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-xl font-bold" style={{ color: colors.teal.primary }}>
              {expert.name?.charAt(0) || 'E'}
            </div>
          )}
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-semibold text-sm" style={{ color: colors.text.dark }}>
                {expert.name}
              </h3>
              <p className="text-xs mt-0.5" style={{ color: colors.teal.primary }}>
                {expert.modality_label || modalityLabels[expert.modality] || expert.modality}
              </p>
            </div>
            <ChevronRightIcon className="w-5 h-5 flex-shrink-0" style={{ color: colors.text.mutedDark }} />
          </div>
          
          <div className="flex items-center gap-3 mt-2">
            <div className="flex items-center gap-1">
              <StarIcon className="w-3.5 h-3.5" style={{ color: '#F59E0B' }} filled />
              <span className="text-xs font-medium" style={{ color: colors.text.dark }}>{expert.rating || '4.8'}</span>
            </div>
            <span className="text-xs" style={{ color: colors.text.mutedDark }}>
              {expert.consultations || '500'}+ consultations
            </span>
          </div>
          
          {expert.languages && (
            <p className="text-xs mt-1" style={{ color: colors.text.mutedDark }}>
              {expert.languages.join(', ')}
            </p>
          )}
        </div>
      </div>
      
      {/* Tags */}
      {(() => {
        const lifeTags = expert.life_situation_tags || [];
        const methodTags = expert.method_tags || [];
        const displayTags = lifeTags.length > 0
          ? [...lifeTags.slice(0, 3), ...(methodTags.length > 0 ? [methodTags[0]] : [])].slice(0, 4)
          : (expert.best_for_tags || []).slice(0, 3);
        return displayTags.length > 0 ? (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {displayTags.map((tag, idx) => (
              <span 
                key={idx}
                className="text-[10px] px-2 py-0.5 rounded-full"
                style={{ 
                  backgroundColor: idx >= (lifeTags.length > 0 ? lifeTags.slice(0, 3).length : 999) ? `${colors.gold.accent}20` : `${colors.teal.primary}10`,
                  color: idx >= (lifeTags.length > 0 ? lifeTags.slice(0, 3).length : 999) ? colors.gold.accent : colors.teal.primary
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        ) : null;
      })()}
    </div>
  );
}
