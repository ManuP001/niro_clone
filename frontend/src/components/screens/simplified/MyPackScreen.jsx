import React, { useState, useEffect } from 'react';
import { colors, shadows } from './theme';
import { apiSimplified, formatPrice, trackEvent } from './utils';
import { 
  CalendarIcon, 
  ChatIcon, 
  PhoneIcon, 
  ClockIcon,
  ChevronRightIcon,
  CheckIcon,
  GiftIcon
} from './icons';
import ResponsiveHeader from './ResponsiveHeader';

/**
 * MyPackScreen V2 - Dashboard for paying customers with responsive layout
 * Shows: Package details, days left, deliverables, schedule calls, suggested remedies
 */

// Suggested remedies based on common needs
const SUGGESTED_REMEDIES = [
  {
    id: 'chakra_balance',
    title: 'Chakra Balance Program',
    subtitle: '3 Guided Sessions',
    description: 'Feel calmer, clearer, and more grounded',
    price: 3500,
    image: '🧘',
    tag: 'Popular',
  },
  {
    id: 'stress_sleep_kit',
    title: 'Stress & Sleep Kit',
    description: 'Natural remedies for better rest',
    price: 899,
    image: '😴',
    tag: 'Quick Relief',
  },
  {
    id: 'prosperity_kit',
    title: 'Prosperity Kit',
    description: 'Attract abundance and success',
    price: 999,
    image: '✨',
    tag: 'Best Seller',
  },
];

export default function MyPackScreen({ token, userState, onNavigate, hasBottomNav, onTabChange }) {
  const [loading, setLoading] = useState(false);
  const [planDetails, setPlanDetails] = useState(null);
  const [error, setError] = useState(null);

  const activePlan = userState?.active_plans?.[0];

  useEffect(() => {
    if (activePlan?.plan_id) {
      loadPlanDetails();
    }
    trackEvent('mypack_viewed', { has_active_plan: !!activePlan }, token);
  }, [activePlan, token]);

  const loadPlanDetails = async () => {
    if (!activePlan?.plan_id) return;
    
    setLoading(true);
    try {
      const response = await apiSimplified.get(`/plans/${activePlan.plan_id}`, token);
      setPlanDetails(response);
    } catch (err) {
      console.error('Failed to load plan details:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Calculate days remaining
  const getDaysRemaining = () => {
    if (!activePlan?.expires_at) return 0;
    const expiresAt = new Date(activePlan.expires_at);
    const now = new Date();
    const diffTime = expiresAt - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(0, diffDays);
  };

  const daysRemaining = getDaysRemaining();

  // No active plan state
  if (!activePlan) {
    return (
      <div 
        className={`min-h-screen ${hasBottomNav ? 'pb-24' : 'pb-6'}`}
        style={{ background: 'linear-gradient(180deg, #E8F5F3 0%, #F5FBF9 50%, #FFFEF5 100%)' }}
      >
        <div className="px-5 pt-8 pb-6">
          <h1 
            className="text-2xl font-bold mb-2"
            style={{ color: colors.text.dark }}
          >
            My Pack
          </h1>
          <p className="text-sm" style={{ color: colors.text.secondary }}>
            Your purchased consultations will appear here
          </p>
        </div>

        <div className="px-5">
          <div 
            className="rounded-2xl p-8 text-center"
            style={{ backgroundColor: 'rgba(255,255,255,0.9)', border: '1px solid rgba(0,0,0,0.06)' }}
          >
            <div 
              className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center"
              style={{ backgroundColor: `${colors.teal.primary}10` }}
            >
              <GiftIcon className="w-8 h-8" style={{ color: colors.teal.primary }} />
            </div>
            <h2 className="text-lg font-semibold mb-2" style={{ color: colors.text.dark }}>
              No active pack yet
            </h2>
            <p className="text-sm mb-6" style={{ color: colors.text.secondary }}>
              Explore our consultation packages to get started with personalized guidance
            </p>
            <button
              onClick={() => onNavigate('home')}
              className="px-6 py-3 rounded-xl font-semibold"
              style={{ backgroundColor: colors.teal.primary, color: '#fff' }}
            >
              Browse Consultations
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-24' : 'pb-6'}`}
      style={{ background: 'linear-gradient(180deg, #E8F5F3 0%, #F5FBF9 50%, #FFFEF5 100%)' }}
    >
      {/* Header */}
      <div className="px-5 pt-8 pb-4">
        <h1 
          className="text-2xl font-bold mb-1"
          style={{ color: colors.text.dark }}
        >
          My Pack
        </h1>
        <p className="text-sm" style={{ color: colors.text.secondary }}>
          Manage your active consultation
        </p>
      </div>

      {/* Active Pack Card */}
      <div className="px-5 mb-6">
        <div 
          className="rounded-2xl overflow-hidden"
          style={{ 
            background: `linear-gradient(135deg, ${colors.teal.primary} 0%, ${colors.teal.dark} 100%)`,
            boxShadow: '0 4px 20px rgba(62, 130, 122, 0.3)',
          }}
        >
          {/* Pack Header */}
          <div className="p-5 pb-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs uppercase tracking-wide text-white/70 mb-1">Active Pack</p>
                <h2 className="text-xl font-bold text-white">
                  {activePlan.tier_name || 'Consultation Pack'}
                </h2>
                <p className="text-sm text-white/80 mt-1">
                  {activePlan.topic_label || 'Your Journey'}
                </p>
              </div>
              <div 
                className="px-3 py-1.5 rounded-full"
                style={{ backgroundColor: 'rgba(255,255,255,0.2)' }}
              >
                <span className="text-sm font-semibold text-white">
                  {daysRemaining} days left
                </span>
              </div>
            </div>
          </div>

          {/* Deliverables Grid */}
          <div 
            className="grid grid-cols-2 gap-px"
            style={{ backgroundColor: 'rgba(255,255,255,0.1)' }}
          >
            <div className="bg-white/10 p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
                <PhoneIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-white/70">Calls</p>
                <p className="text-sm font-semibold text-white">
                  {planDetails?.calls_remaining || activePlan.calls_remaining || 0} remaining
                </p>
              </div>
            </div>
            <div className="bg-white/10 p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
                <ChatIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-white/70">Chat</p>
                <p className="text-sm font-semibold text-white">Unlimited</p>
              </div>
            </div>
            <div className="bg-white/10 p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
                <CalendarIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-white/70">Duration</p>
                <p className="text-sm font-semibold text-white">
                  {activePlan.validity_weeks || 8} weeks
                </p>
              </div>
            </div>
            <div className="bg-white/10 p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center">
                <ClockIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-white/70">Experts</p>
                <p className="text-sm font-semibold text-white">
                  {planDetails?.threads?.length || 0} active
                </p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="p-4 flex gap-3">
            <button
              onClick={() => onNavigate('planDashboard', { planId: activePlan.plan_id })}
              className="flex-1 py-3 rounded-xl font-semibold text-sm transition-all active:scale-[0.98]"
              style={{ backgroundColor: 'rgba(255,255,255,0.2)', color: '#fff' }}
            >
              View Details
            </button>
            <button
              onClick={() => onNavigate('scheduleCall', { planId: activePlan.plan_id })}
              className="flex-1 py-3 rounded-xl font-semibold text-sm transition-all active:scale-[0.98]"
              style={{ backgroundColor: colors.gold.primary, color: colors.text.dark }}
            >
              Schedule Call
            </button>
          </div>
        </div>
      </div>

      {/* Continue Your Journey */}
      {planDetails?.threads?.length > 0 && (
        <div className="px-5 mb-6">
          <h3 className="text-base font-semibold mb-3" style={{ color: colors.text.dark }}>
            Continue Your Journey
          </h3>
          <div className="space-y-3">
            {planDetails.threads.slice(0, 2).map((thread) => (
              <button
                key={thread.thread_id}
                onClick={() => onNavigate('thread', { threadId: thread.thread_id, planId: activePlan.plan_id })}
                className="w-full p-4 rounded-xl flex items-center gap-4 transition-all active:scale-[0.99]"
                style={{ backgroundColor: 'rgba(255,255,255,0.9)', border: '1px solid rgba(0,0,0,0.06)' }}
              >
                <div 
                  className="w-12 h-12 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: `${colors.teal.primary}15` }}
                >
                  <span className="text-xl">👤</span>
                </div>
                <div className="flex-1 text-left">
                  <p className="font-medium" style={{ color: colors.text.dark }}>
                    {thread.expert?.name || 'Expert'}
                  </p>
                  <p className="text-sm" style={{ color: colors.text.secondary }}>
                    {thread.message_count || 0} messages
                  </p>
                </div>
                <ChevronRightIcon className="w-5 h-5" style={{ color: colors.text.mutedDark }} />
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Suggested Remedies */}
      <div className="px-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-base font-semibold" style={{ color: colors.text.dark }}>
            Suggested For You
          </h3>
          <button 
            onClick={() => onNavigate('remedies')}
            className="text-sm font-medium"
            style={{ color: colors.teal.primary }}
          >
            View all
          </button>
        </div>
        
        <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
          {SUGGESTED_REMEDIES.map((remedy) => (
            <div
              key={remedy.id}
              onClick={() => onNavigate('remedyDetail', { remedyId: remedy.id })}
              className="flex-shrink-0 w-40 rounded-xl p-4 cursor-pointer transition-all active:scale-[0.98]"
              style={{ backgroundColor: 'rgba(255,255,255,0.9)', border: '1px solid rgba(0,0,0,0.06)' }}
            >
              {remedy.tag && (
                <span 
                  className="text-[10px] px-2 py-0.5 rounded-full font-medium"
                  style={{ backgroundColor: `${colors.teal.primary}15`, color: colors.teal.primary }}
                >
                  {remedy.tag}
                </span>
              )}
              <div className="text-3xl my-3">{remedy.image}</div>
              <h4 className="font-medium text-sm mb-1" style={{ color: colors.text.dark }}>
                {remedy.title}
              </h4>
              <p className="text-xs mb-2" style={{ color: colors.text.secondary }}>
                {remedy.description}
              </p>
              <p className="font-semibold text-sm" style={{ color: colors.teal.primary }}>
                {formatPrice(remedy.price)}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="px-5 mb-6">
        <h3 className="text-base font-semibold mb-3" style={{ color: colors.text.dark }}>
          Quick Actions
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => onNavigate('mira')}
            className="p-4 rounded-xl flex flex-col items-center text-center transition-all active:scale-[0.98]"
            style={{ backgroundColor: 'rgba(255,255,255,0.9)', border: '1px solid rgba(0,0,0,0.06)' }}
          >
            <div 
              className="w-10 h-10 rounded-full mb-2 flex items-center justify-center"
              style={{ backgroundColor: `${colors.teal.primary}15` }}
            >
              <ChatIcon className="w-5 h-5" style={{ color: colors.teal.primary }} />
            </div>
            <span className="text-sm font-medium" style={{ color: colors.text.dark }}>Ask Mira</span>
            <span className="text-xs" style={{ color: colors.text.secondary }}>Free AI Chat</span>
          </button>
          
          <button
            onClick={() => onNavigate('kundli')}
            className="p-4 rounded-xl flex flex-col items-center text-center transition-all active:scale-[0.98]"
            style={{ backgroundColor: 'rgba(255,255,255,0.9)', border: '1px solid rgba(0,0,0,0.06)' }}
          >
            <div 
              className="w-10 h-10 rounded-full mb-2 flex items-center justify-center"
              style={{ backgroundColor: `${colors.teal.primary}15` }}
            >
              <span className="text-lg">🌟</span>
            </div>
            <span className="text-sm font-medium" style={{ color: colors.text.dark }}>Your Kundli</span>
            <span className="text-xs" style={{ color: colors.text.secondary }}>Birth Chart</span>
          </button>
        </div>
      </div>

      {/* Support */}
      <div className="px-5 mb-6">
        <div 
          className="rounded-xl p-4 flex items-center gap-4"
          style={{ backgroundColor: `${colors.teal.primary}08`, border: `1px solid ${colors.teal.primary}20` }}
        >
          <div 
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ backgroundColor: `${colors.teal.primary}15` }}
          >
            <span className="text-lg">💬</span>
          </div>
          <div className="flex-1">
            <p className="font-medium text-sm" style={{ color: colors.text.dark }}>
              Need help with your pack?
            </p>
            <p className="text-xs" style={{ color: colors.text.secondary }}>
              Our support team is here 24/7
            </p>
          </div>
          <button
            className="px-4 py-2 rounded-lg text-sm font-medium"
            style={{ backgroundColor: colors.teal.primary, color: '#fff' }}
          >
            Contact
          </button>
        </div>
      </div>
    </div>
  );
}
