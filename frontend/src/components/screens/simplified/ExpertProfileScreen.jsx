import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { apiSimplified, trackEvent } from './utils';
import { getBackendUrl } from '../../../config';
import { colors, shadows } from './theme';
import ResponsiveHeader from './ResponsiveHeader';

const resolvePhotoUrl = (url) => {
  if (!url) return null;
  if (url.startsWith('/')) return `${getBackendUrl()}${url}`;
  return url;
};


/**
 * ExpertProfileScreen V3 - Full expert profile with new design
 * Updated for responsive layout and teal/cream theme
 */
export default function ExpertProfileScreen({ token, expertId: propExpertId, userState, onNavigate, onBack, hasBottomNav, onTabChange, isAuthenticated, user, onLoginClick, wizardMode = false, wizardTopicId, onBookFreeCall, onBuyPackage }) {
  // Get expertId from URL params or props
  const params = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const expertId = propExpertId || params.expertId;
  // topicId filters packages shown — comes from wizard prop or URL search param
  const topicId = wizardTopicId || searchParams.get('topicId') || null;

  const [expert, setExpert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showTopicSelector, setShowTopicSelector] = useState(false);
  const [expertRemedies, setExpertRemedies] = useState([]);
  const packagesRef = useRef(null);

  // Fetch remedies offered by this expert
  useEffect(() => {
    if (!expertId) return;
    apiSimplified.get(`/experts/${expertId}/remedies`, token)
      .then(res => setExpertRemedies(res.remedies || []))
      .catch(() => setExpertRemedies([]));
  }, [expertId, token]);

  // Handle back navigation
  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate(-1);
    }
  };

  // Get active plan topics for entitlement checking
  const activePlanTopics = userState?.active_plans?.map(p => p.topic_id) || [];

  useEffect(() => {
    const loadExpert = async () => {
      try {
        // Get all experts and find the one we need
        const response = await apiSimplified.get('/experts/all', token);
        const foundExpert = response.experts?.find(e => e.expert_id === expertId);
        setExpert(foundExpert);
        
        trackEvent('expert_profile_viewed', { 
          expert_id: expertId,
          flow_version: 'simplified_v2' 
        }, token);
      } catch (err) {
        console.error('Failed to load expert:', err);
      } finally {
        setLoading(false);
      }
    };
    loadExpert();
  }, [expertId, token]);

  const topicLabels = {
    career: 'Career & Work',
    money: 'Money & Finance',
    health: 'Health & Wellness',
    marriage: 'Marriage & Family',
    children: 'Children & Education',
    love: 'Love & Relationships',
    business: 'Business',
    travel: 'Travel & Relocation',
    property: 'Property & Vastu',
    mental_health: 'Mental Health',
    spiritual: 'Spiritual Growth',
    legal: 'Legal Matters',
  };

  const handleFreeCall = () => {
    if (!expert) return;
    if (wizardMode && onBookFreeCall) {
      onBookFreeCall();
      return;
    }
    if (!isAuthenticated) { onLoginClick?.(); return; }
    onNavigate?.('schedule', { expertId: expert.expert_id, expertName: expert.name });
  };

  const handleExplorePackages = () => {
    if (!expert) return;
    onNavigate?.('expertPackages', { expertId: expert.expert_id });
  };

  const hasAccess = expert?.topics?.some(t => activePlanTopics.includes(t));

  if (loading) {
    return (
      <div 
        className={`min-h-screen flex items-center justify-center ${hasBottomNav ? 'pb-20 md:pb-0' : ''}`} 
        style={{ backgroundColor: colors.background.primary }}
      >
        <div className="text-center">
          <div 
            className="w-12 h-12 border-4 rounded-full animate-spin mx-auto mb-4"
            style={{ borderColor: `${colors.teal.primary}30`, borderTopColor: colors.teal.primary }}
          />
          <p style={{ color: colors.text.muted }}>Loading expert...</p>
        </div>
      </div>
    );
  }

  if (!expert) {
    return (
      <div 
        className={`min-h-screen flex items-center justify-center ${hasBottomNav ? 'pb-20 md:pb-0' : ''}`} 
        style={{ backgroundColor: colors.background.primary }}
      >
        <div className="text-center">
          <p style={{ color: colors.text.dark }}>Expert not found</p>
          <button onClick={handleBack} className="mt-4 font-medium" style={{ color: colors.teal.primary }}>Go back</button>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-28 md:pb-24' : 'pb-24'}`} 
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Responsive Header */}
      <ResponsiveHeader
        title={expert.name}
        showBackButton={true}
        onBack={handleBack}
        onNavigate={onNavigate}
        onTabChange={onTabChange}
      />

      {/* Hero Section with Expert Photo */}
      <div 
        className="relative px-6 pt-8 pb-20 md:pb-24"
        style={{ background: `linear-gradient(135deg, ${colors.teal.primary} 0%, ${colors.teal.dark} 100%)` }}
      >
        {/* Expert Photo - Centered, overlapping bottom */}
        <div className="absolute left-1/2 -translate-x-1/2 -bottom-16">
          <div 
            className="w-32 h-32 md:w-36 md:h-36 rounded-full overflow-hidden border-4 shadow-lg"
            style={{ borderColor: colors.background.primary }}
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
                className="w-full h-full flex items-center justify-center text-5xl"
                style={{ backgroundColor: `${colors.teal.soft}` }}
              >
                <span style={{ color: colors.teal.primary }}>
                  {expert.name?.charAt(0) || '👤'}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Content Container - Centered */}
      <div className="max-w-2xl mx-auto px-6 pt-20">
        {/* Name & Modality */}
        <div className="text-center mb-6">
          <h1 className="text-2xl md:text-3xl font-bold" style={{ color: colors.text.dark }}>{expert.name}</h1>
          <p className="font-medium mt-1 text-base md:text-lg" style={{ color: colors.teal.primary }}>{expert.modality_label}</p>
          
          {/* Rating */}
          <div className="flex items-center justify-center mt-2 text-sm md:text-base">
            <span style={{ color: colors.peach.primary }}>★</span>
            <span className="ml-1 font-medium" style={{ color: colors.text.dark }}>{expert.rating}</span>
            <span className="mx-2" style={{ color: colors.ui.borderDark }}>|</span>
            <span style={{ color: colors.text.muted }}>{expert.total_consultations || '500+'}+ consultations</span>
          </div>
        </div>

        {/* Best For Tags */}
        {expert.best_for_tags?.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-2 text-sm md:text-base" style={{ color: colors.text.dark }}>Best for</h3>
            <div className="flex flex-wrap gap-2">
              {expert.best_for_tags.map((tag, idx) => (
                <span 
                  key={idx} 
                  className="px-3 py-1.5 rounded-full text-sm"
                  style={{ backgroundColor: `${colors.teal.primary}15`, color: colors.teal.dark }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Topics */}
        {expert.topics?.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-2 text-sm md:text-base" style={{ color: colors.text.dark }}>Topics</h3>
            <div className="flex flex-wrap gap-2">
              {expert.topics.map((topicId) => (
                <span 
                  key={topicId} 
                  className="px-3 py-1.5 rounded-full text-sm"
                  style={{ backgroundColor: `${colors.peach.soft}`, color: colors.text.dark }}
                >
                  {topicLabels[topicId] || topicId}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Languages */}
        {expert.languages?.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-2 text-sm md:text-base" style={{ color: colors.text.dark }}>Languages</h3>
            <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>🗣️ {expert.languages.join(', ')}</p>
          </div>
        )}

        {/* Bio */}
        <div className="mb-6">
          <h3 className="font-semibold mb-2 text-sm md:text-base" style={{ color: colors.text.dark }}>About</h3>
          <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>
            {expert.short_bio}
          </p>
          <p className="mt-2 text-sm md:text-base" style={{ color: colors.text.muted }}>
            💼 {expert.experience_years || 10}+ years of experience
          </p>
        </div>

        {/* Stats Card */}
        <div
          className="rounded-xl p-4 mb-6"
          style={{ backgroundColor: `${colors.teal.primary}08`, border: `1px solid ${colors.teal.primary}20` }}
        >
          <div className="flex items-center justify-around text-center">
            <div>
              <p className="font-bold text-lg md:text-xl" style={{ color: colors.text.dark }}>{expert.rating}★</p>
              <p className="text-xs md:text-sm" style={{ color: colors.text.muted }}>Rating</p>
            </div>
            <div className="w-px h-8" style={{ backgroundColor: colors.ui.borderDark }} />
            <div>
              <p className="font-bold text-lg md:text-xl" style={{ color: colors.text.dark }}>{expert.total_consultations || '500'}+</p>
              <p className="text-xs md:text-sm" style={{ color: colors.text.muted }}>Sessions</p>
            </div>
            <div className="w-px h-8" style={{ backgroundColor: colors.ui.borderDark }} />
            <div>
              <p className="font-bold text-lg md:text-xl" style={{ color: colors.text.dark }}>{expert.experience_years || 10}+</p>
              <p className="text-xs md:text-sm" style={{ color: colors.text.muted }}>Years</p>
            </div>
          </div>
        </div>

        {/* Consultation Options */}
        {(expert.consultations || []).length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-3 text-sm md:text-base" style={{ color: colors.text.dark }}>
              Book a consultation
            </h3>
            <div className="space-y-3">
              {expert.consultations.map((c, i) => (
                <button
                  key={i}
                  onClick={() => {
                    if (!isAuthenticated) { onLoginClick?.(); return; }
                    onNavigate?.('schedule', { expertId: expert.expert_id, expertName: expert.name, consultation: c });
                  }}
                  className="w-full text-left rounded-xl p-4 transition-all active:scale-[0.99] hover:shadow-sm"
                  style={{ backgroundColor: colors.peach.soft, border: `1px solid ${colors.ui.borderDark}` }}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span
                          className="text-[11px] font-semibold px-2 py-0.5 rounded-full"
                          style={{ backgroundColor: colors.teal.primary + '20', color: colors.teal.primary }}
                        >
                          {c.duration_mins} mins
                        </span>
                        {c.title && (
                          <p className="font-semibold text-sm" style={{ color: colors.text.dark }}>{c.title}</p>
                        )}
                      </div>
                      {c.what_you_get && (
                        <p className="text-xs mt-1 line-clamp-2" style={{ color: colors.text.secondary }}>
                          {c.what_you_get}
                        </p>
                      )}
                    </div>
                    <div className="flex-shrink-0 text-right">
                      <p className="font-bold text-base" style={{ color: colors.teal.primary }}>
                        ₹{c.price_inr?.toLocaleString('en-IN')}
                      </p>
                      <p className="text-xs" style={{ color: colors.text.muted }}>Book →</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Remedies offered by this expert */}
        {expertRemedies.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-3 text-sm md:text-base" style={{ color: colors.text.dark }}>
              Remedies &amp; rituals
            </h3>
            <div className="space-y-3">
              {expertRemedies.map((remedy) => (
                <button
                  key={remedy.remedy_id}
                  onClick={() => onNavigate?.('remedies')}
                  className="w-full text-left rounded-xl p-4 transition-all active:scale-[0.99] hover:shadow-sm"
                  style={{ backgroundColor: '#FFF8F0', border: `1px solid ${colors.ui.borderDark}` }}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <span className="text-2xl flex-shrink-0">{remedy.image}</span>
                      <div className="min-w-0">
                        <p className="font-semibold text-sm" style={{ color: colors.text.dark }}>{remedy.title}</p>
                        {remedy.subtitle && (
                          <p className="text-xs mt-0.5 line-clamp-1" style={{ color: colors.text.secondary }}>
                            {remedy.subtitle}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0 text-right">
                      <p className="font-bold text-base" style={{ color: colors.gold.accent || '#B45309' }}>
                        ₹{remedy.price?.toLocaleString('en-IN')}
                      </p>
                      <p className="text-xs" style={{ color: colors.text.muted }}>View →</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Sticky CTA - two stacked buttons */}
      <div
        className={`fixed ${hasBottomNav ? 'bottom-16 md:bottom-0' : 'bottom-0'} left-0 right-0 p-4 z-40`}
        style={{
          backgroundColor: colors.background.primary,
          borderTop: `1px solid ${colors.ui.borderDark}`,
          backdropFilter: 'blur(12px)',
        }}
      >
        <div className="max-w-2xl mx-auto">
          <button
            onClick={() => {
              if (!isAuthenticated) { onLoginClick?.(); return; }
              onNavigate?.('schedule', { expertId: expert?.expert_id, expertName: expert?.name });
            }}
            className="w-full font-semibold py-4 rounded-xl transition-all active:scale-[0.99] hover:shadow-md"
            style={{ backgroundColor: colors.teal.primary, color: '#ffffff' }}
            data-testid="expert-book-btn"
          >
            Book a consultation
          </button>
        </div>
      </div>

      {/* Topic Selector Modal (hidden in wizard mode — topic already selected) */}
      {!wizardMode && showTopicSelector && (
        <div className="fixed inset-0 bg-black/50 flex items-end z-50">
          <div 
            className="w-full rounded-t-3xl p-6 max-w-lg mx-auto"
            style={{ backgroundColor: '#ffffff' }}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold" style={{ color: colors.text.dark }}>Which topic is this about?</h2>
              <button 
                onClick={() => setShowTopicSelector(false)}
                className="text-2xl" style={{ color: colors.text.muted }}
              >
                ×
              </button>
            </div>
            <p className="text-sm mb-4" style={{ color: colors.text.secondary }}>
              {expert.name} can help with multiple topics. Choose one to continue:
            </p>
            <div className="space-y-2">
              {expert.topics?.map((topicId) => (
                <button
                  key={topicId}
                  onClick={() => {
                    setShowTopicSelector(false);
                    onNavigate('topic', { topicId });
                  }}
                  className="w-full rounded-xl p-4 text-left transition-all hover:shadow-md"
                  style={{ backgroundColor: colors.background.secondary, border: `1px solid ${colors.ui.borderDark}` }}
                >
                  <span className="font-medium" style={{ color: colors.text.dark }}>
                    {topicLabels[topicId] || topicId}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
