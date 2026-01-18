import React, { useState, useEffect } from 'react';
import { apiV2, TOPICS, formatPrice } from './utils';

/**
 * HomeScreenV2 - Solution-led home screen for NIRO V2
 * 
 * Shows:
 * - Active plan (if any)
 * - Primary CTA to start conversation
 * - Topic tiles for quick access
 */
export default function HomeScreenV2({ token, userId, onNavigate }) {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async () => {
    try {
      // Load user's plans
      const plansResponse = await apiV2.get('/plans', token);
      if (plansResponse.ok) {
        setPlans(plansResponse.plans || []);
      }
    } catch (err) {
      console.error('Failed to load plans:', err);
    } finally {
      setLoading(false);
    }
  };

  const activePlan = plans.find(p => p.status === 'active');
  const currentHour = new Date().getHours();
  const greeting = currentHour < 12 ? 'Good morning' : currentHour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Header */}
      <div className="px-6 pt-12 pb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-500 text-sm">{greeting}</p>
            <h1 className="text-2xl font-semibold text-slate-900">Welcome to Niro</h1>
          </div>
          <button 
            onClick={() => onNavigate('profile')}
            className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center"
          >
            <span className="text-slate-600">👤</span>
          </button>
        </div>
      </div>

      {/* Active Plan Card */}
      {activePlan && (
        <div className="px-6 mb-6">
          <div 
            className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-5 text-white shadow-lg cursor-pointer"
            onClick={() => onNavigate('plan', { planId: activePlan.plan_id })}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <p className="text-emerald-100 text-xs font-medium uppercase tracking-wide">Your Active Plan</p>
                <h3 className="text-lg font-semibold mt-1">{activePlan.package?.name || 'Current Plan'}</h3>
              </div>
              <div className="text-right">
                <p className="text-emerald-100 text-xs">Week {activePlan.current_week || 1}</p>
              </div>
            </div>
            
            {/* Progress bar */}
            <div className="mb-3">
              <div className="h-2 bg-emerald-400/30 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-white rounded-full transition-all"
                  style={{ width: `${Math.min((activePlan.tasks_completed / activePlan.tasks_total) * 100, 100) || 0}%` }}
                />
              </div>
              <p className="text-emerald-100 text-xs mt-1">
                {activePlan.tasks_completed || 0} of {activePlan.tasks_total || 0} tasks completed
              </p>
            </div>
            
            <div className="flex items-center text-emerald-100 text-sm">
              <span>Continue your journey</span>
              <span className="ml-2">→</span>
            </div>
          </div>
        </div>
      )}

      {/* Primary CTA - Start Conversation */}
      <div className="px-6 mb-8">
        <h2 className="text-slate-800 font-semibold mb-3">What's on your mind?</h2>
        <button
          onClick={() => onNavigate('intake')}
          className="w-full bg-white border-2 border-slate-200 rounded-2xl p-5 text-left hover:border-emerald-300 hover:shadow-md transition-all group"
        >
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-xl flex items-center justify-center mr-4 group-hover:scale-105 transition-transform">
              <span className="text-2xl">💬</span>
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-slate-800 group-hover:text-emerald-700">Start a conversation</h3>
              <p className="text-slate-500 text-sm mt-0.5">
                Tell me what's going on — I'll guide you to the right solution
              </p>
            </div>
            <div className="text-slate-400 group-hover:text-emerald-600 transition-colors">
              →
            </div>
          </div>
        </button>
      </div>

      {/* Topic Tiles */}
      <div className="px-6 pb-24">
        <h2 className="text-slate-800 font-semibold mb-4">Explore by life area</h2>
        <div className="grid grid-cols-3 gap-3">
          {Object.entries(TOPICS).map(([key, topic]) => (
            <button
              key={key}
              onClick={() => onNavigate('intake', { topic: key })}
              className="bg-white border border-slate-100 rounded-xl p-4 text-center hover:border-emerald-200 hover:shadow-md transition-all group"
            >
              <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">
                {topic.icon}
              </div>
              <p className="text-xs font-medium text-slate-700 group-hover:text-emerald-700">
                {topic.label.split(' ')[0]}
              </p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
