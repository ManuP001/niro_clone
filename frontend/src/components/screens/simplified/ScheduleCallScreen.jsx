import React from 'react';
import { colors, shadows } from './theme';

/**
 * ScheduleCallScreen - Google Calendar booking page
 * Shown after user completes birth details (for free 10-min call flow)
 */

const GOOGLE_CALENDAR_LINK = 'https://calendar.app.google/cm7fCPK7iHWPXvTY6';

export default function ScheduleCallScreen({ onBack, onComplete, userName }) {
  const handleOpenCalendar = () => {
    window.open(GOOGLE_CALENDAR_LINK, '_blank');
  };

  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Header */}
      <header className="sticky top-0 z-40 px-4 py-4 flex items-center gap-4" style={{ backgroundColor: colors.background.primary }}>
        <button
          onClick={onBack}
          className="w-10 h-10 rounded-full flex items-center justify-center transition-all hover:bg-gray-100"
          style={{ backgroundColor: '#FFFFFF', boxShadow: shadows.card }}
          data-testid="schedule-back-btn"
        >
          <svg className="w-5 h-5" style={{ color: colors.text.dark }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 className="text-lg font-semibold" style={{ color: colors.text.dark }}>
          Schedule Your Free Call
        </h1>
      </header>

      {/* Content */}
      <div className="flex-1 px-4 py-8">
        <div className="max-w-lg mx-auto">
          {/* Success Icon */}
          <div className="text-center mb-8">
            <div 
              className="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center"
              style={{ backgroundColor: `${colors.teal.primary}15` }}
            >
              <svg className="w-10 h-10" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold mb-2" style={{ color: colors.text.dark }}>
              Great, {userName || 'you\'re all set'}!
            </h2>
            <p className="text-base" style={{ color: colors.text.secondary }}>
              Your birth details have been saved. Now let's schedule your free 10-minute consultation.
            </p>
          </div>

          {/* What to Expect */}
          <div 
            className="rounded-2xl p-6 mb-6"
            style={{ backgroundColor: '#FFFFFF', boxShadow: shadows.card }}
          >
            <h3 className="font-semibold mb-4" style={{ color: colors.text.dark }}>
              What to expect in your free call:
            </h3>
            <ul className="space-y-3">
              {[
                'Quick review of your birth chart',
                'Identify your primary concern area',
                'Get initial insights and guidance',
                'Learn about personalized consultation options',
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3">
                  <div 
                    className="w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center mt-0.5"
                    style={{ backgroundColor: colors.teal.primary }}
                  >
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-sm" style={{ color: colors.text.secondary }}>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Astrologer Info */}
          <div 
            className="rounded-2xl p-6 mb-8"
            style={{ backgroundColor: colors.cream.warm }}
          >
            <div className="flex items-center gap-4">
              <div 
                className="w-14 h-14 rounded-full flex items-center justify-center"
                style={{ backgroundColor: colors.teal.primary }}
              >
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <p className="font-semibold" style={{ color: colors.text.dark }}>Niro Expert Team</p>
                <p className="text-sm" style={{ color: colors.text.muted }}>
                  One of our verified Vedic astrologers will connect with you
                </p>
              </div>
            </div>
          </div>

          {/* CTA Button */}
          <button
            onClick={handleOpenCalendar}
            className="w-full py-4 rounded-full font-semibold text-base transition-all hover:shadow-lg hover:-translate-y-0.5 flex items-center justify-center gap-2"
            style={{
              backgroundColor: colors.peach.primary,
              color: colors.text.dark,
              boxShadow: shadows.peach,
            }}
            data-testid="open-calendar-btn"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Pick a Time Slot
          </button>

          <p className="text-center text-xs mt-4" style={{ color: colors.text.muted }}>
            You'll be redirected to Google Calendar to select your preferred time
          </p>
        </div>
      </div>

      {/* Trust Footer */}
      <div className="px-4 py-6 text-center" style={{ backgroundColor: colors.cream.warm }}>
        <div className="flex items-center justify-center gap-6 text-xs" style={{ color: colors.text.muted }}>
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            100% Confidential
          </span>
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            Verified Experts
          </span>
          <span className="flex items-center gap-1">
            <svg className="w-4 h-4" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            10 mins, No pressure
          </span>
        </div>
      </div>
    </div>
  );
}
