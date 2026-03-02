import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { colors, shadows } from './theme';
import { getBackendUrl } from '../../../config';

/**
 * PublicExpertProfilePage - Publicly accessible expert profile (no login required)
 * Shows expert details with CTA to book consultation
 */

export default function PublicExpertProfilePage({ isAuthenticated, onLoginClick }) {
  const { expertId } = useParams();
  const navigate = useNavigate();
  const [expert, setExpert] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadExpert = async () => {
      try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/api/simplified/experts/all`);
        if (response.ok) {
          const data = await response.json();
          const foundExpert = data.experts?.find(e => e.expert_id === expertId);
          setExpert(foundExpert);
        }
      } catch (err) {
        console.error('Failed to load expert:', err);
      } finally {
        setLoading(false);
      }
    };
    loadExpert();
  }, [expertId]);

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

  const handleBackToExperts = () => {
    navigate('/experts');
  };

  const handleConsultClick = () => {
    if (isAuthenticated) {
      // If logged in, go directly to schedule a call
      navigate('/app/schedule');
    } else {
      // Store intent to schedule and redirect to login
      localStorage.setItem('niro_user_intent', JSON.stringify({ 
        type: 'free_call',
        expertId: expertId,
        returnTo: '/app/schedule'
      }));
      navigate('/login');
    }
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
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: colors.background.primary }}
      >
        <div className="text-center">
          <p style={{ color: colors.text.dark }}>Expert not found</p>
          <button 
            onClick={handleBackToExperts} 
            className="mt-4 font-medium" 
            style={{ color: colors.teal.primary }}
          >
            Back to Experts
          </button>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="min-h-screen pb-24"
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
                onClick={handleBackToExperts}
                className="p-2 -ml-2 rounded-full hover:bg-black/5 transition-colors"
                data-testid="back-btn"
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
              <a href="/" className="hidden md:flex items-center" data-testid="header-logo">
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
              <h1
                className="text-lg font-semibold truncate md:hidden"
                style={{ color: colors.text.dark }}
              >
                {expert.name}
              </h1>
            </div>

            {/* Right: CTA */}
            <button
              onClick={handleConsultClick}
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
              Get a free 5 mins consultation
            </button>
          </div>
        </div>
      </header>

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
                src={expert.photo_url} 
                alt={expert.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div 
                className="w-full h-full flex items-center justify-center text-5xl"
                style={{ backgroundColor: `${colors.teal.soft}` }}
              >
                <span style={{ color: colors.teal.primary }}>
                  {expert.name?.charAt(0) || '?'}
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
      </div>

      {/* Sticky CTA */}
      <div 
        className="fixed bottom-0 left-0 right-0 p-4 z-40"
        style={{ 
          backgroundColor: colors.background.primary, 
          borderTop: `1px solid ${colors.ui.borderDark}`,
          backdropFilter: 'blur(12px)',
        }}
      >
        <div className="max-w-2xl mx-auto">
          <button
            onClick={handleConsultClick}
            className="w-full font-semibold py-4 rounded-xl transition-all active:scale-[0.99] hover:shadow-md"
            style={{ 
              backgroundColor: colors.peach.primary, 
              color: colors.text.dark 
            }}
            data-testid="consult-btn"
          >
            📞 Get a free 5 mins consultation
          </button>
        </div>
      </div>
    </div>
  );
}
