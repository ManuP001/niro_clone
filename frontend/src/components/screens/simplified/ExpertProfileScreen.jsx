import React, { useState, useEffect } from 'react';
import { apiSimplified, trackEvent } from './utils';

/**
 * ExpertProfileScreen - Full expert profile page
 * V2: Shows full expert details with gated actions
 */
export default function ExpertProfileScreen({ token, expertId, userState, onNavigate, onBack, hasBottomNav }) {
  const [expert, setExpert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showTopicSelector, setShowTopicSelector] = useState(false);

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

  const handleAction = () => {
    if (!expert) return;
    
    // Check if user has access to any of the expert's topics
    const accessibleTopic = expert.topics?.find(t => activePlanTopics.includes(t));
    
    if (accessibleTopic) {
      // User has access - navigate to plan to start thread
      const plan = userState?.active_plans?.find(p => p.topic_id === accessibleTopic);
      if (plan) {
        onNavigate('plan', { planId: plan.plan_id, preSelectExpert: expert.expert_id });
      }
    } else {
      // User doesn't have access - show topic selector or go to topic landing
      if (expert.topics?.length === 1) {
        onNavigate('topic', { topicId: expert.topics[0] });
      } else {
        setShowTopicSelector(true);
      }
    }
  };

  const hasAccess = expert?.topics?.some(t => activePlanTopics.includes(t));

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${hasBottomNav ? 'pb-20' : ''}`} style={{ backgroundColor: '#f5f0e3' }}>
        <div className="text-center">
          <div 
            className="w-12 h-12 border-4 rounded-full animate-spin mx-auto mb-4"
            style={{ borderColor: 'rgba(215,184,112,0.3)', borderTopColor: '#d7b870' }}
          />
          <p style={{ color: '#9a8a6a' }}>Loading expert...</p>
        </div>
      </div>
    );
  }

  if (!expert) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${hasBottomNav ? 'pb-20' : ''}`} style={{ backgroundColor: '#f5f0e3' }}>
        <div className="text-center">
          <p style={{ color: '#5c5c5c' }}>Expert not found</p>
          <button onClick={onBack} className="mt-4 font-medium" style={{ color: '#d7b870' }}>Go back</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${hasBottomNav ? 'pb-24' : 'pb-6'}`} style={{ backgroundColor: '#f5f0e3' }}>
      {/* Header with Photo */}
      <div 
        className="relative px-6 pt-12 pb-20"
        style={{ background: 'linear-gradient(135deg, #d7b870 0%, #c9a85a 100%)' }}
      >
        <button 
          onClick={onBack} 
          className="mb-4 flex items-center transition-colors"
          style={{ color: 'rgba(240,233,209,0.8)' }}
        >
          <span className="mr-2">←</span> Back
        </button>
        
        {/* Expert Photo - Centered, overlapping bottom */}
        <div className="absolute left-1/2 -translate-x-1/2 -bottom-16">
          <div 
            className="w-32 h-32 rounded-full overflow-hidden border-4 shadow-lg"
            style={{ borderColor: '#f5f0e3' }}
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
                style={{ background: 'linear-gradient(135deg, rgba(215,184,112,0.5) 0%, rgba(229,209,136,0.5) 100%)' }}
              >
                👤
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-6 pt-20">
        {/* Name & Modality */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold" style={{ color: '#5c5c5c' }}>{expert.name}</h1>
          <p className="font-medium mt-1" style={{ color: '#d7b870' }}>{expert.modality_label}</p>
          
          {/* Rating */}
          <div className="flex items-center justify-center mt-2">
            <span style={{ color: '#d7b870' }}>★</span>
            <span className="ml-1 font-medium" style={{ color: '#5c5c5c' }}>{expert.rating}</span>
            <span className="mx-2" style={{ color: '#e5d188' }}>|</span>
            <span style={{ color: '#9a8a6a' }}>{expert.total_consultations || '500+'}+ consultations</span>
          </div>
        </div>

        {/* Best For Tags */}
        {expert.best_for_tags?.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold mb-2" style={{ color: '#5c5c5c' }}>Best for</h3>
            <div className="flex flex-wrap gap-2">
              {expert.best_for_tags.map((tag, idx) => (
                <span 
                  key={idx} 
                  className="px-3 py-1 rounded-full text-sm"
                  style={{ backgroundColor: 'rgba(215,184,112,0.2)', color: '#7a6a4a' }}
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
            <h3 className="font-semibold mb-2" style={{ color: '#5c5c5c' }}>Topics</h3>
            <div className="flex flex-wrap gap-2">
              {expert.topics.map((topicId) => (
                <span 
                  key={topicId} 
                  className="px-3 py-1 rounded-full text-sm"
                  style={{ backgroundColor: 'rgba(215,184,112,0.3)', color: '#5c5c5c' }}
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
            <h3 className="font-semibold mb-2" style={{ color: '#5c5c5c' }}>Languages</h3>
            <p style={{ color: '#7a6a4a' }}>🗣️ {expert.languages.join(', ')}</p>
          </div>
        )}

        {/* Bio */}
        <div className="mb-6">
          <h3 className="font-semibold mb-2" style={{ color: '#5c5c5c' }}>About</h3>
          <p style={{ color: '#7a6a4a' }}>
            {expert.short_bio}
          </p>
          <p className="mt-2" style={{ color: '#9a8a6a' }}>
            💼 {expert.experience_years || 10}+ years of experience
          </p>
        </div>

        {/* Social Proof Placeholders */}
        <div 
          className="rounded-xl p-4 mb-6"
          style={{ backgroundColor: 'rgba(215,184,112,0.1)', border: '1px solid #e5d188' }}
        >
          <div className="flex items-center justify-around text-center">
            <div>
              <p className="font-bold text-lg" style={{ color: '#5c5c5c' }}>{expert.rating}★</p>
              <p className="text-xs" style={{ color: '#9a8a6a' }}>Rating</p>
            </div>
            <div className="w-px h-8" style={{ backgroundColor: '#e5d188' }} />
            <div>
              <p className="font-bold text-lg" style={{ color: '#5c5c5c' }}>{expert.total_consultations || '500'}+</p>
              <p className="text-xs" style={{ color: '#9a8a6a' }}>Sessions</p>
            </div>
            <div className="w-px h-8" style={{ backgroundColor: '#e5d188' }} />
            <div>
              <p className="font-bold text-lg" style={{ color: '#5c5c5c' }}>{expert.experience_years || 10}+</p>
              <p className="text-xs" style={{ color: '#9a8a6a' }}>Years</p>
            </div>
          </div>
        </div>
      </div>

      {/* Sticky CTA */}
      <div 
        className="fixed bottom-16 left-0 right-0 p-4 z-40"
        style={{ backgroundColor: '#f5f0e3', borderTop: '1px solid #e5d188' }}
      >
        <button
          onClick={handleAction}
          className="w-full font-semibold py-4 rounded-xl transition-all"
          style={hasAccess 
            ? { background: 'linear-gradient(135deg, #d7b870 0%, #c9a85a 100%)', color: '#f0e9d1' }
            : { backgroundColor: 'rgba(215,184,112,0.2)', color: '#5c5c5c', border: '1px solid #e5d188' }
          }
        >
          {hasAccess ? '💬 Start Chat' : '🔓 Unlock to talk'}
        </button>
      </div>

      {/* Topic Selector Modal */}
      {showTopicSelector && (
        <div className="fixed inset-0 bg-black/50 flex items-end z-50">
          <div className="bg-white w-full rounded-t-3xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold" style={{ color: '#5c5c5c' }}>Which topic is this about?</h2>
              <button 
                onClick={() => setShowTopicSelector(false)}
                className="text-2xl" style={{ color: '#9a8a6a' }}
              >
                ×
              </button>
            </div>
            <p className="text-sm mb-4" style={{ color: '#9a8a6a' }}>
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
                  className="w-full rounded-xl p-4 text-left transition-all"
                  style={{ backgroundColor: '#f5f0e3', border: '1px solid #e5d188' }}
                >
                  <span className="font-medium" style={{ color: '#5c5c5c' }}>
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
