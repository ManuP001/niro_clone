import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { colors, shadows } from './theme';
import { apiSimplified, trackEvent } from './utils';
import { ChevronRightIcon } from './icons';
import { getBackendUrl } from '../../../config';
import NiroCertifiedBadge from './NiroCertifiedBadge';
import ResponsiveHeader from './ResponsiveHeader';

const resolvePhotoUrl = (url) => {
  if (!url) return null;
  if (url.startsWith('/')) return `${getBackendUrl()}${url}`;
  return url;
};

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
  const [loadError, setLoadError] = useState(false);
  const [selectedModality, setSelectedModality] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Get active plan topics for entitlement checking
  const activePlanTopics = userState?.active_plans?.map(p => p.topic_id) || [];

  const loadExperts = async () => {
    setLoading(true);
    setLoadError(false);
    try {
      // 15-second timeout — prevents infinite spinner on Render cold starts
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 15000);
      const response = await apiSimplified.get('/experts/all', token, { signal: controller.signal });
      clearTimeout(timer);

      let allExperts = response.experts || [];
      if (topicId) {
        const topicFiltered = allExperts.filter(e => e.topics?.includes(topicId));
        allExperts = topicFiltered.length > 0 ? topicFiltered : allExperts;
        allExperts.sort((a, b) => (parseFloat(b.rating) || 0) - (parseFloat(a.rating) || 0));
        if (maxResults) allExperts = allExperts.slice(0, maxResults);
      }
      setExperts(allExperts);
      trackEvent('experts_tab_viewed', { flow_version: 'simplified_v5' }, token);
    } catch (err) {
      console.error('Failed to load experts:', err);
      setLoadError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExperts();
  }, [token, topicId, maxResults]); // eslint-disable-line

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
    if (onBookFreeCall) {
      // In wizard mode, clicking the card selects that expert and advances to booking
      onBookFreeCall(expert);
      return;
    }
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

  if (loadError) {
    return (
      <div
        className={`min-h-screen ${hasBottomNav ? 'pb-20 md:pb-0' : ''} flex items-center justify-center p-6`}
        style={{ backgroundColor: colors.background.primary }}
      >
        <div className="text-center">
          <p className="text-2xl mb-3">⏱️</p>
          <p className="font-semibold mb-1" style={{ color: colors.text.dark }}>Taking longer than usual</p>
          <p className="text-sm mb-4" style={{ color: colors.text.muted }}>The server may be waking up. Please try again.</p>
          <button
            onClick={loadExperts}
            className="px-5 py-2 rounded-lg font-medium text-white"
            style={{ backgroundColor: colors.teal.primary }}
          >
            Retry
          </button>
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

          {/* Search (hidden in wizard/topic mode) */}
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

          {/* Modality Filter Pills — always shown */}
          {modalities.length > 1 && (
            <div className="flex overflow-x-auto gap-2 pb-2 scrollbar-hide">
              <button
                onClick={() => setSelectedModality('all')}
                className="flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-all"
                style={selectedModality === 'all'
                  ? { backgroundColor: colors.teal.primary, color: '#ffffff' }
                  : { backgroundColor: '#ffffff', color: colors.text.muted, border: `1px solid ${colors.ui.borderDark}` }
                }
                data-testid="filter-all"
              >
                All
              </button>
              {modalities.map((modality) => (
                <button
                  key={modality}
                  onClick={() => setSelectedModality(modality)}
                  className="flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-all whitespace-nowrap"
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

        {/* Expert Cards - Flat vertical list */}
        <div className="px-4 md:px-8 py-4 space-y-3 max-w-2xl mx-auto">
          {filteredExperts.map((expert) => (
            <ExpertCard
              key={expert.expert_id}
              expert={expert}
              hasAccess={expert.topics?.some(t => activePlanTopics.includes(t))}
              onClick={() => handleExpertClick(expert)}
            />
          ))}

          {filteredExperts.length === 0 && (
            <div className="text-center py-12">
              <p className="text-lg" style={{ color: colors.text.muted }}>No experts found</p>
              <p className="text-sm mt-2" style={{ color: colors.text.muted }}>Try adjusting your filters</p>
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
 * ExpertCard — horizontal card matching Niro design mockups.
 * Shows: circular photo, name, modality, years of experience, Niro Certified badge, chevron.
 */
function ExpertCard({ expert, onClick }) {
  const years = expert.years_experience || expert.experience_years;
  return (
    <div
      onClick={onClick}
      className="flex items-center gap-4 rounded-2xl p-4 transition-all active:scale-[0.99] cursor-pointer hover:shadow-md"
      style={{
        backgroundColor: '#ffffff',
        border: `1px solid ${colors.ui.borderDark}`,
        boxShadow: shadows.card,
      }}
    >
      {/* Circular photo with gold ring */}
      <div
        className="w-16 h-16 rounded-full flex-shrink-0 overflow-hidden"
        style={{
          border: '2px solid #C9A84C',
          backgroundColor: colors.background.warm,
        }}
      >
        {expert.photo_url ? (
          <img
            src={resolvePhotoUrl(expert.photo_url)}
            alt={expert.name}
            className="w-full h-full object-cover"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
        ) : (
          <div
            className="w-full h-full flex items-center justify-center text-2xl font-bold"
            style={{ color: colors.teal.primary }}
          >
            {expert.name?.charAt(0) || 'E'}
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="font-bold text-base leading-tight" style={{ color: colors.text.dark }}>
          {expert.name}
        </p>
        <p className="text-sm mt-0.5" style={{ color: colors.text.secondary }}>
          {expert.modality_label}
        </p>
        {years ? (
          <p className="text-xs mt-0.5" style={{ color: colors.text.muted }}>
            {years}+ years of practice
          </p>
        ) : null}
        <div className="mt-1.5">
          <NiroCertifiedBadge size="sm" />
        </div>
      </div>

      {/* Chevron */}
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: colors.background.secondary }}
      >
        <ChevronRightIcon className="w-4 h-4" style={{ color: colors.text.muted }} />
      </div>
    </div>
  );
}
