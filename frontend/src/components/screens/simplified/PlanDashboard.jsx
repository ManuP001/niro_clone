import React, { useState, useEffect } from 'react';
import { apiSimplified, formatPrice, trackEvent } from './utils';

/**
 * PlanDashboard - Post-purchase view with experts, threads, tools
 * V2: Works with bottom nav, enhanced expert selection, demo mode support
 */
export default function PlanDashboard({ token, planId, onNavigate, onBack, hasBottomNav, isDemoMode }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [showExpertSelector, setShowExpertSelector] = useState(false);
  const [creatingThread, setCreatingThread] = useState(false);

  useEffect(() => {
    const loadPlanData = async () => {
      // Demo mode - show mock data
      if (isDemoMode) {
        setData(getDemoData());
        setLoading(false);
        return;
      }
      
      if (!planId) {
        setError('No plan ID provided');
        setLoading(false);
        return;
      }
      try {
        const response = await apiSimplified.get(`/plans/${planId}`, token);
        setData(response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadPlanData();
    trackEvent('dashboard_viewed', { plan_id: planId, is_demo: isDemoMode, flow_version: 'simplified_v2' }, token);
  }, [planId, token, isDemoMode]);

  const handleStartThread = async (expertId) => {
    if (creatingThread || isDemoMode) {
      if (isDemoMode) {
        alert('This is demo mode. Purchase a real pack to chat with experts!');
      }
      return;
    }
    
    setCreatingThread(true);
    try {
      const response = await apiSimplified.post('/threads', {
        plan_id: planId,
        expert_id: expertId,
      }, token);
      
      trackEvent('expert_thread_started', { 
        plan_id: planId, 
        expert_id: expertId,
        flow_version: 'simplified_v2'
      }, token);
      
      setShowExpertSelector(false);
      onNavigate('thread', { threadId: response.thread_id, planId });
    } catch (err) {
      alert(err.message || 'Failed to start conversation');
    } finally {
      setCreatingThread(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-emerald-200 border-t-emerald-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error || 'Failed to load plan'}</p>
          <button onClick={onBack} className="text-emerald-600 font-medium">Go back</button>
        </div>
      </div>
    );
  }

  const { plan, tier, topic, threads, experts, tools, calls_remaining, can_create_thread } = data;
  const weeksRemaining = plan.expires_at 
    ? Math.max(0, Math.ceil((new Date(plan.expires_at) - new Date()) / (7 * 24 * 60 * 60 * 1000)))
    : tier?.validity_weeks || 0;

  return (
    <div className={`min-h-screen bg-slate-50 ${hasBottomNav ? 'pb-20' : 'pb-6'}`}>
      {/* Header */}
      <div className="bg-gradient-to-br from-emerald-500 to-teal-600 text-white px-6 pt-10 pb-8">
        <div className="flex items-center justify-between mb-2">
          <div>
            <p className="text-emerald-100 text-sm uppercase tracking-wide">Your Active Pack</p>
            <h1 className="text-2xl font-bold">{tier?.name || 'Your Plan'}</h1>
          </div>
          <div className="bg-white/20 px-3 py-1 rounded-full">
            <span className="text-sm font-medium">{weeksRemaining}w left</span>
          </div>
        </div>
        
        <p className="text-emerald-100 flex items-center">
          <span className="mr-2">{topic?.icon}</span>
          {topic?.label}
        </p>
        
        {tier?.access_policy?.calls_enabled && (
          <div className="mt-4 bg-white/10 rounded-xl p-3">
            <p className="text-sm">
              <span className="mr-2">📞</span>
              {calls_remaining} calls remaining this month
            </p>
          </div>
        )}
      </div>

      {/* Expert Conversations */}
      <div className="px-6 py-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-800">Your Expert Conversations</h2>
        </div>
        
        {/* Start New Thread Button */}
        {can_create_thread && (
          <button
            onClick={() => setShowExpertSelector(true)}
            className="w-full bg-white border-2 border-dashed border-emerald-300 rounded-xl p-4 text-center hover:bg-emerald-50 transition-all mb-4"
          >
            <span className="text-emerald-600 font-medium">+ Start new conversation with an expert</span>
          </button>
        )}
        
        {!can_create_thread && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
            <p className="text-amber-700 text-sm">
              ⚠️ Thread limit reached for your plan. Upgrade to add more experts.
            </p>
          </div>
        )}
        
        {/* Active Threads */}
        {threads.length > 0 ? (
          <div className="space-y-3">
            {threads.map((thread) => (
              <button
                key={thread.thread_id}
                onClick={() => onNavigate('thread', { threadId: thread.thread_id, planId })}
                className="w-full bg-white border border-slate-200 rounded-xl p-4 text-left hover:border-emerald-300 transition-all"
              >
                <div className="flex items-center">
                  <div className="w-12 h-12 rounded-full overflow-hidden bg-gradient-to-br from-emerald-100 to-teal-100 flex-shrink-0">
                    {thread.expert?.photo_url ? (
                      <img 
                        src={thread.expert.photo_url} 
                        alt={thread.expert?.name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-xl">
                        👤
                      </div>
                    )}
                  </div>
                  <div className="flex-1 ml-4">
                    <p className="font-medium text-slate-800">{thread.expert?.name || 'Expert'}</p>
                    <p className="text-slate-500 text-sm">{thread.expert?.modality_label || 'Consultant'}</p>
                    <p className="text-slate-400 text-xs mt-1">
                      {thread.message_count || 0} messages
                    </p>
                  </div>
                  <span className="text-emerald-500 font-medium">→</span>
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="bg-slate-100 rounded-xl p-6 text-center">
            <span className="text-4xl mb-3 block">💬</span>
            <p className="text-slate-600 font-medium">No conversations yet</p>
            <p className="text-slate-500 text-sm mt-1">Start one with an expert above!</p>
          </div>
        )}
      </div>

      {/* Call Booking (Plus/Pro) */}
      {tier?.access_policy?.calls_enabled && (
        <div className="px-6 py-4">
          <div className="bg-white border border-slate-200 rounded-xl p-4">
            <h3 className="font-semibold text-slate-800 mb-2">📞 Schedule a Call</h3>
            <p className="text-slate-600 text-sm mb-3">
              You have {calls_remaining} calls remaining this month (60 min each)
            </p>
            <button className="w-full bg-slate-100 text-slate-700 font-medium py-3 rounded-xl hover:bg-slate-200 transition-all">
              Book a Call with Expert
            </button>
          </div>
        </div>
      )}

      {/* Free Tools (Plus/Pro) */}
      {tools.length > 0 && (
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Free Services</h2>
          <div className="grid grid-cols-2 gap-3">
            {tools.map((tool) => (
              <button
                key={tool.tool_id}
                onClick={() => trackEvent('free_tool_opened', { 
                  tool_id: tool.tool_id, 
                  topic_id: topic?.topic_id,
                  flow_version: 'simplified_v1_5' 
                }, token)}
                className="bg-white border border-slate-200 rounded-xl p-4 text-left hover:border-emerald-300 transition-all"
              >
                <span className="text-xl">
                  {tool.tool_type === 'quiz' ? '🎯' : 
                   tool.tool_type === 'checklist' ? '✅' :
                   tool.tool_type === 'framework' ? '📊' : '📝'}
                </span>
                <p className="font-medium text-slate-800 text-sm mt-2">{tool.title}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Add Topic Pass */}
      <div className="px-6 py-4">
        <div className="bg-slate-100 border border-slate-200 rounded-xl p-4">
          <h3 className="font-semibold text-slate-800 mb-1">Need to discuss another topic?</h3>
          <p className="text-slate-600 text-sm mb-3">
            Your pack covers {topic?.label} only. Add another topic:
          </p>
          <button 
            onClick={() => onNavigate('addTopic', { parentPlanId: planId })}
            className="w-full bg-white border border-slate-300 text-slate-700 font-medium py-3 rounded-xl hover:bg-slate-50 transition-all"
          >
            + Add Topic Pass — {formatPrice(2000)}
          </button>
        </div>
      </div>

      {/* Expert Selector Modal */}
      {showExpertSelector && (
        <div className="fixed inset-0 bg-black/50 flex items-end z-50">
          <div className="bg-white w-full rounded-t-3xl p-6 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-slate-800">Choose an Expert</h2>
              <button 
                onClick={() => setShowExpertSelector(false)}
                className="text-slate-400 text-2xl hover:text-slate-600"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-3">
              {experts.map((expert) => (
                <button
                  key={expert.expert_id}
                  onClick={() => handleStartThread(expert.expert_id)}
                  disabled={creatingThread}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 text-left hover:border-emerald-300 transition-all disabled:opacity-50"
                >
                  <div className="flex items-center">
                    <div className="w-14 h-14 rounded-full overflow-hidden bg-gradient-to-br from-emerald-100 to-teal-100 flex-shrink-0">
                      {expert.photo_url ? (
                        <img 
                          src={expert.photo_url} 
                          alt={expert.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-2xl">
                          👤
                        </div>
                      )}
                    </div>
                    <div className="flex-1 ml-4">
                      <p className="font-medium text-slate-800">{expert.name}</p>
                      <p className="text-emerald-600 text-sm">{expert.modality_label}</p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {expert.best_for_tags?.slice(0, 2).map((tag, idx) => (
                          <span key={idx} className="bg-slate-200 text-slate-600 text-xs px-2 py-0.5 rounded-full">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center text-yellow-500">
                        <span>★</span>
                        <span className="text-slate-600 text-sm ml-1">{expert.rating}</span>
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Demo data for returning user mode without real plan
function getDemoData() {
  return {
    plan: {
      plan_id: 'demo_plan',
      status: 'active',
      expires_at: new Date(Date.now() + 42 * 24 * 60 * 60 * 1000).toISOString(), // 6 weeks
    },
    tier: {
      tier_id: 'demo_plus',
      name: 'Plus Pack (Demo)',
      tier_level: 'plus',
      validity_weeks: 8,
      access_policy: {
        calls_enabled: true,
        calls_per_month: 2,
        max_active_expert_threads: 3,
        free_tools_access: true,
      },
      features: [
        'Unlimited chat with experts',
        '3 expert threads',
        '2 video calls/month',
        'Free tools access',
      ],
    },
    topic: {
      topic_id: 'career',
      label: 'Career & Work',
      icon: '💼',
    },
    threads: [],
    experts: [
      {
        expert_id: 'demo_exp_1',
        name: 'Pandit Rajesh (Demo)',
        modality_label: 'Vedic Astrologer',
        photo_url: 'https://randomuser.me/api/portraits/men/32.jpg',
        best_for_tags: ['Career timing', 'Job changes'],
        rating: 4.9,
      },
      {
        expert_id: 'demo_exp_2',
        name: 'Dr. Ananya (Demo)',
        modality_label: 'Career Coach',
        photo_url: 'https://randomuser.me/api/portraits/women/44.jpg',
        best_for_tags: ['Career transitions', 'Leadership'],
        rating: 4.8,
      },
    ],
    tools: [
      { tool_id: 'demo_tool_1', title: 'Career Assessment', tool_type: 'quiz' },
      { tool_id: 'demo_tool_2', title: 'Goal Tracker', tool_type: 'checklist' },
    ],
    calls_remaining: 2,
    can_create_thread: true,
  };
}

