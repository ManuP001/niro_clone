import React, { useState, useEffect } from 'react';
import { apiV2 } from './utils';

/**
 * ProfileScreenV2 - User profile and journey history
 */
export default function ProfileScreenV2({ token, userId, onNavigate, onBack }) {
  const [loading, setLoading] = useState(true);
  const [plans, setPlans] = useState([]);
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const plansResponse = await apiV2.get('/plans', token);
      if (plansResponse.ok) {
        setPlans(plansResponse.plans || []);
      }
    } catch (err) {
      console.error('Failed to load profile data:', err);
    } finally {
      setLoading(false);
    }
  };

  const activePlans = plans.filter(p => p.status === 'active');
  const completedPlans = plans.filter(p => p.status === 'completed');

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-emerald-200 border-t-emerald-500 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 pb-24">
      {/* Header */}
      <div className="bg-white px-6 pt-12 pb-6 border-b border-slate-100">
        <button 
          onClick={onBack}
          className="text-slate-500 mb-4 flex items-center"
        >
          <span className="mr-2">←</span> Back
        </button>
        <h1 className="text-2xl font-semibold text-slate-900">My Profile</h1>
      </div>

      {/* Profile Card */}
      <div className="px-6 -mt-4">
        <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-3xl">N</span>
          </div>
          <h2 className="text-xl font-semibold text-slate-800">Niro User</h2>
          <p className="text-slate-500 text-sm mt-1">user@example.com</p>
          
          <button className="mt-4 text-emerald-600 text-sm font-medium">
            Edit Profile
          </button>
        </div>
      </div>

      <div className="px-6 mt-6 space-y-4">
        {/* My Journey */}
        <div className="bg-white rounded-2xl p-5 border border-slate-100">
          <h3 className="font-semibold text-slate-800 mb-4">My Journey</h3>
          
          {activePlans.length === 0 && completedPlans.length === 0 ? (
            <div className="text-center py-6">
              <span className="text-4xl mb-2 block">🌱</span>
              <p className="text-slate-600">No plans yet</p>
              <p className="text-slate-400 text-sm">Start a conversation to get personalized guidance</p>
            </div>
          ) : (
            <div className="space-y-3">
              {activePlans.map(plan => (
                <div 
                  key={plan.plan_id}
                  onClick={() => onNavigate('plan', { planId: plan.plan_id })}
                  className="flex items-center p-4 bg-emerald-50 border border-emerald-100 rounded-xl cursor-pointer hover:bg-emerald-100 transition-all"
                >
                  <span className="text-2xl mr-3">📁</span>
                  <div className="flex-1">
                    <p className="font-medium text-slate-800">{plan.package?.name || 'Active Plan'}</p>
                    <div className="flex items-center mt-1">
                      <span className="text-xs bg-emerald-200 text-emerald-700 px-2 py-0.5 rounded-full">Active</span>
                      <span className="text-slate-400 text-xs ml-2">Week {plan.current_week || 1}</span>
                    </div>
                  </div>
                  <span className="text-slate-400">→</span>
                </div>
              ))}
              
              {completedPlans.map(plan => (
                <div 
                  key={plan.plan_id}
                  className="flex items-center p-4 bg-slate-50 rounded-xl"
                >
                  <span className="text-2xl mr-3">📁</span>
                  <div className="flex-1">
                    <p className="font-medium text-slate-800">{plan.package?.name || 'Completed Plan'}</p>
                    <div className="flex items-center mt-1">
                      <span className="text-xs bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full">Completed ✓</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Settings Links */}
        <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden">
          {[
            { label: 'Notification Settings', icon: '🔔' },
            { label: 'Help & Support', icon: '❓' },
            { label: 'Terms & Privacy', icon: '📄' },
          ].map((item, idx) => (
            <button 
              key={idx}
              className="w-full flex items-center justify-between p-4 border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-all"
            >
              <div className="flex items-center">
                <span className="mr-3">{item.icon}</span>
                <span className="text-slate-700">{item.label}</span>
              </div>
              <span className="text-slate-400">→</span>
            </button>
          ))}
        </div>

        {/* Logout */}
        <button className="w-full text-center text-red-500 py-3 text-sm font-medium">
          Log Out
        </button>
      </div>
    </div>
  );
}
