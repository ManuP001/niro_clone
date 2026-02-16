import React, { useState, useEffect } from 'react';
import { colors, shadows } from './theme';
import { apiSimplified, trackEvent } from './utils';
import { StarIcon, ChevronRightIcon } from './icons';

/**
 * ExpertsScreen - Browse all experts grouped by modality
 * V5: Updated with teal color scheme to match other tabs
 */
export default function ExpertsScreen({ token, userState, onNavigate }) {
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
        setExperts(response.experts || []);
        trackEvent('experts_tab_viewed', { flow_version: 'simplified_v5' }, token);
      } catch (err) {
        console.error('Failed to load experts:', err);
      } finally {
        setLoading(false);
      }
    };
    loadExperts();
  }, [token]);

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
    onNavigate('expertProfile', { expertId: expert.expert_id });
  };

  if (loading) {
    return (
      <div 
        className="min-h-screen pb-20 flex items-center justify-center" 
        style={{ background: colors.background.gradient }}
      >
        <div className="text-center">
          <div 
            className="w-12 h-12 border-4 rounded-full animate-spin mx-auto mb-4"
            style={{ borderColor: 'rgba(239,225,169,0.3)', borderTopColor: colors.gold.primary }}
          />
          <p style={{ color: colors.text.muted }}>Loading experts...</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="min-h-screen pb-20" 
      style={{ background: colors.background.gradient }}
    >
      {/* Header */}
      <div className="px-5 pt-6 pb-4">
        <h1 
          className="text-2xl font-bold mb-1"
          style={{ 
            fontFamily: "'Kumbh Sans', sans-serif",
            background: colors.logo.gradient,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          Experts
        </h1>
        <p className="text-sm mb-4" style={{ color: 'rgba(255,255,255,0.8)' }}>
          Browse by expertise, unlock to start chatting
        </p>
        
        {/* Search */}
        <div className="mb-4">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search experts..."
            className="w-full px-4 py-2.5 rounded-xl text-sm focus:outline-none"
            style={{ 
              backgroundColor: 'white', 
              border: `1px solid ${colors.ui.borderDark}`,
              color: colors.text.dark
            }}
          />
        </div>
        
        {/* Modality Filter Pills */}
        <div className="flex overflow-x-auto gap-2 pb-2 scrollbar-hide">
          <button
            onClick={() => setSelectedModality('all')}
            className="flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all"
            style={selectedModality === 'all'
              ? { backgroundColor: colors.gold.primary, color: colors.text.dark }
              : { backgroundColor: 'rgba(255,255,255,0.15)', color: colors.text.primary, border: `1px solid ${colors.ui.border}` }
            }
          >
            All Experts
          </button>
          {modalities.map((modality) => (
            <button
              key={modality}
              onClick={() => setSelectedModality(modality)}
              className="flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all whitespace-nowrap"
              style={selectedModality === modality
                ? { backgroundColor: colors.gold.primary, color: colors.text.dark }
                : { backgroundColor: 'rgba(255,255,255,0.15)', color: colors.text.primary, border: `1px solid ${colors.ui.border}` }
              }
            >
              {modalityLabels[modality] || modality}
            </button>
          ))}
        </div>
      </div>

      {/* Expert Cards */}
      <div 
        className="px-5 py-6 rounded-t-3xl -mt-2"
        style={{ backgroundColor: colors.background.card }}
      >
        {selectedModality === 'all' ? (
          // Show grouped view
          Object.entries(groupedExperts).map(([modality, modalityExperts]) => (
            <div key={modality} className="mb-6">
              <h2 className="text-lg font-semibold mb-3" style={{ color: colors.text.dark }}>
                {modalityLabels[modality] || modality}
              </h2>
              <div className="space-y-3">
                {modalityExperts.map((expert) => (
                  <ExpertCard
                    key={expert.expert_id}
                    expert={expert}
                    hasAccess={expert.topics?.some(t => activePlanTopics.includes(t))}
                    onClick={() => handleExpertClick(expert)}
                  />
                ))}
              </div>
            </div>
          ))
        ) : (
          // Show flat list for filtered view
          <div className="space-y-3">
            {filteredExperts.map((expert) => (
              <ExpertCard
                key={expert.expert_id}
                expert={expert}
                hasAccess={expert.topics?.some(t => activePlanTopics.includes(t))}
                onClick={() => handleExpertClick(expert)}
              />
            ))}
          </div>
        )}
        
        {filteredExperts.length === 0 && (
          <div className="text-center py-8">
            <p style={{ color: colors.text.mutedDark }}>No experts found</p>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * ExpertCard - Expert card with consistent styling
 */
function ExpertCard({ expert, hasAccess, onClick }) {
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
    </div>
  );
}
