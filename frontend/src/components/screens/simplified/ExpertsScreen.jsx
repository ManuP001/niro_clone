import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { colors, shadows } from './theme';
import { apiSimplified, trackEvent } from './utils';
import { StarIcon, ChevronRightIcon } from './icons';
import { getBackendUrl } from '../../../config';

const resolvePhotoUrl = (url) => {
  if (!url) return null;
  if (url.startsWith('/')) return `${getBackendUrl()}${url}`;
  return url;
};
import ResponsiveHeader from './ResponsiveHeader';

/**
 * ExpertsScreen V2 - Responsive Layout with Desktop Header
 * - Multi-column grid on desktop
 * - Centered max-width container
 * - Desktop navigation header
 */
export default function ExpertsScreen({ token, userState, onNavigate, onTabChange, hasBottomNav = true, topicId: topicIdProp, maxResults, onExpertSelect, onBookFreeCall, isAuthenticated, onLoginClick }) {
  const [searchParams] = useSearchParams();
  // topicId can come from parent prop (wizard mode) or URL search param (direct navigation)
  const topicId = topicIdProp || searchParams.get('topicId') || null;

  const [experts, setExperts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedModality, setSelectedModality] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Get active plan topics for entitlement checking
  const activePlanTopics = userState?.active_plans?.map(p => p.topic_id) || [];

  useEffect(() => {
    const loadExperts = async () => {
      try {
        const response = await apiSimplified.get('/experts/all', token);
        let allExperts = response.experts || [];

        if (topicId) {
          const topicFiltered = allExperts.filter(e => e.topics?.includes(topicId));
          // If none tagged with this topic, show all active experts so wizard is never empty
          allExperts = topicFiltered.length > 0 ? topicFiltered : allExperts;
          allExperts.sort((a, b) => (parseFloat(b.rating) || 0) - (parseFloat(a.rating) || 0));
          if (maxResults) allExperts = allExperts.slice(0, maxResults);
        }

        setExperts(allExperts);
        trackEvent('experts_tab_viewed', { flow_version: 'simplified_v5' }, token);
      } catch (err) {
        console.error('Failed to load experts:', err);
      } finally {
        setLoading(false);
      }
    };
    loadExperts();
  }, [token, topicId, maxResults]);

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
    // In wizard mode with onBookFreeCall, cards are display-only
    if (onBookFreeCall) return;
    if (onExpertSelect) {
      onExpertSelect(expert.expert_id, expert.name);
    } else {
      onNavigate('expertProfile', { expertId: expert.expert_id, topicId });
    }
  };

  if (loading) {
    return (
      <div 
        className={`min-h-screen ${hasBottomNav ? 'pb-20 md:pb-0' : ''} flex items-center justify-center`}
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
      className={`${!topicId ? 'min-h-screen' : ''} ${hasBottomNav && !topicId ? 'pb-20 md:pb-0' : ''} ${onBookFreeCall ? 'pb-24' : ''}`}
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Responsive Header (hidden in wizard mode) */}
      {!topicId && (
        <ResponsiveHeader
          title="Experts"
          showBackButton={false}
          onNavigate={onNavigate}
          onTabChange={onTabChange}
        />
      )}

      {/* Content Container */}
      <div className={topicId ? '' : 'max-w-6xl mx-auto'}>
        {/* Header Section */}
        <div className={`px-4 ${topicId ? 'pt-4 pb-2' : 'md:px-8 pt-6 pb-4'}`}>
          {topicId ? (
            <h2
              className="text-lg font-semibold mb-4"
              style={{ color: colors.text.dark }}
            >
              Astrologers for your topic
            </h2>
          ) : (
            <>
              <h1
                className="text-2xl md:text-3xl font-bold mb-1"
                style={{ color: colors.text.dark }}
              >
                Our Experts
              </h1>
              <p className="text-sm md:text-base mb-4" style={{ color: colors.text.muted }}>
                Browse by expertise, unlock to start chatting
              </p>
            </>
          )}

          {/* Search (hidden in wizard mode) */}
          {!topicId && (
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
          )}

          {/* Modality Filter Pills (hidden in wizard mode) */}
          {!topicId && (
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
          )}
        </div>

        {/* Free Call CTA Banner — shown on topic-filtered listing (not in wizard/onBookFreeCall mode) */}
        {topicId && !onExpertSelect && !onBookFreeCall && (
          <div className="px-4 md:px-8 mb-2">
            <div
              className="rounded-2xl p-5 flex items-center gap-4"
              style={{
                background: `linear-gradient(135deg, ${colors.teal.primary} 0%, ${colors.teal.dark || '#2d6b63'} 100%)`,
                boxShadow: '0 4px 16px rgba(62,130,122,0.25)',
              }}
            >
              <div className="flex-1">
                <p className="font-bold text-base text-white mb-0.5">
                  Not sure which expert to pick?
                </p>
                <p className="text-sm text-white/80">
                  Book a free 5-min intro call — we'll match you with the right astrologer.
                </p>
              </div>
              <button
                onClick={() => {
                  if (!isAuthenticated) { onLoginClick?.(); return; }
                  onNavigate?.('schedule', {});
                }}
                className="flex-shrink-0 px-4 py-2.5 rounded-xl font-semibold text-sm transition-all active:scale-[0.97] hover:shadow-md"
                style={{ backgroundColor: '#FFFFFF', color: colors.teal.primary }}
              >
                Book free call
              </button>
            </div>
          </div>
        )}

        {/* Expert Cards - Responsive Grid */}
        <div className="px-4 md:px-8 py-6">
          {selectedModality === 'all' ? (
            // Show grouped view with multi-column grid
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
                      hasAccess={expert.topics?.some(t => activePlanTopics.includes(t))}
                      onClick={() => handleExpertClick(expert)}
                      topicId={topicId}
                    />
                  ))}
                </div>
              </div>
            ))
          ) : (
            // Show flat list for filtered view with grid
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredExperts.map((expert) => (
                <ExpertCard
                  key={expert.expert_id}
                  expert={expert}
                  hasAccess={expert.topics?.some(t => activePlanTopics.includes(t))}
                  onClick={() => handleExpertClick(expert)}
                  topicId={topicId}
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

      {/* Sticky footer CTA — wizard mode only */}
      {onBookFreeCall && (
        <div
          className="fixed bottom-0 left-0 right-0 z-40 px-4 py-4"
          style={{ backgroundColor: colors.background.primary, borderTop: `1px solid ${colors.ui.borderDark}` }}
        >
          <div className="max-w-lg mx-auto">
            <button
              onClick={onBookFreeCall}
              className="w-full py-4 rounded-full font-semibold text-base transition-all hover:shadow-lg active:scale-[0.99]"
              style={{ backgroundColor: colors.teal.primary, color: '#ffffff' }}
            >
              Book your free 5 min call →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * ExpertCard - Expert card with consistent styling
 */
function ExpertCard({ expert, hasAccess, onClick, topicId }) {
  return (
    <div
      onClick={onClick}
      className="rounded-xl p-4 transition-all active:scale-[0.99] cursor-pointer"
      style={{ 
        backgroundColor: '#ffffff',
        border: `1px solid ${colors.ui.borderDark}`,
        boxShadow: shadows.sm,
      }}
    >
      <div className="flex gap-4">
        {/* Avatar */}
        <div 
          className="w-14 h-14 rounded-full flex-shrink-0 overflow-hidden"
          style={{ backgroundColor: colors.gold.cream }}
        >
          {expert.photo_url ? (
            <img
              src={resolvePhotoUrl(expert.photo_url)}
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
                {expert.modality_label}
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
      
      {/* Tags - show life-situation tags + optionally 1 method tag */}
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

      {/* Free call available badge — shown only in wizard mode */}
      {topicId && expert.offers_free_call && (
        <div className="mt-2">
          <span
            className="text-[10px] px-2 py-0.5 rounded-full font-medium"
            style={{ backgroundColor: `${colors.teal.primary}15`, color: colors.teal.primary }}
          >
            Free call available
          </span>
        </div>
      )}
    </div>
  );
}
