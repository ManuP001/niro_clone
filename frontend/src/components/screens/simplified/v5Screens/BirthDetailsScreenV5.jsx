/**
 * NIRO V5 Birth Details Screen
 * Step 2 in the 8-step onboarding flow
 * 
 * Features:
 * - V5 themed styling
 * - Skip birth time option (sends null to API)
 * - Preserves existing logic
 */

import React, { useState, useCallback } from 'react';
import { colors, typography, borderRadius, shadows } from '../theme';

// Simple date picker component
const DateInput = ({ value, onChange, placeholder }) => {
  return (
    <input
      type="date"
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full px-4 py-3 rounded-xl text-base transition-all focus:outline-none focus:ring-2"
      style={{
        background: colors.background.card,
        border: `1px solid ${colors.ui.borderDark}`,
        color: colors.text.dark,
        borderRadius: borderRadius.md
      }}
      data-testid="birth-date-input"
    />
  );
};

// Time picker component
const TimeInput = ({ value, onChange, disabled, placeholder }) => {
  return (
    <input
      type="time"
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      placeholder={placeholder}
      className={`w-full px-4 py-3 rounded-xl text-base transition-all focus:outline-none focus:ring-2 ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      style={{
        background: disabled ? `${colors.background.card}80` : colors.background.card,
        border: `1px solid ${colors.ui.borderDark}`,
        color: colors.text.dark,
        borderRadius: borderRadius.md
      }}
      data-testid="birth-time-input"
    />
  );
};

export default function BirthDetailsScreenV5({ 
  initialData = {}, 
  onComplete, 
  onBack 
}) {
  const [name, setName] = useState(initialData.name || '');
  const [dateOfBirth, setDateOfBirth] = useState(initialData.dateOfBirth || '');
  const [timeOfBirth, setTimeOfBirth] = useState(initialData.timeOfBirth || '');
  const [placeOfBirth, setPlaceOfBirth] = useState(initialData.placeOfBirth || '');
  const [skipTime, setSkipTime] = useState(initialData.skipBirthTime || false);
  const [errors, setErrors] = useState({});

  const validateForm = useCallback(() => {
    const newErrors = {};
    
    if (!name.trim()) {
      newErrors.name = 'Please enter your name';
    }
    
    if (!dateOfBirth) {
      newErrors.dateOfBirth = 'Please enter your date of birth';
    }
    
    if (!placeOfBirth.trim()) {
      newErrors.placeOfBirth = 'Please enter your place of birth';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [name, dateOfBirth, placeOfBirth]);

  const handleSubmit = useCallback(() => {
    if (!validateForm()) return;
    
    onComplete({
      name: name.trim(),
      dateOfBirth,
      timeOfBirth: skipTime ? null : timeOfBirth,
      placeOfBirth: placeOfBirth.trim(),
      skipBirthTime: skipTime
    });
  }, [name, dateOfBirth, timeOfBirth, placeOfBirth, skipTime, validateForm, onComplete]);

  const handleSkipTimeToggle = () => {
    setSkipTime(!skipTime);
    if (!skipTime) {
      setTimeOfBirth('');
    }
  };

  const isFormValid = name.trim() && dateOfBirth && placeOfBirth.trim();

  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ background: colors.background.gradient }}
    >
      {/* Header */}
      <div className="px-5 pt-12 pb-6">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-medium mb-6 transition-opacity hover:opacity-70"
          style={{ color: colors.gold.primary }}
          data-testid="birth-details-back-btn"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        
        <h1 
          className="text-2xl font-bold mb-2"
          style={{ color: colors.text.primary }}
        >
          Tell us about yourself
        </h1>
        <p 
          className="text-sm"
          style={{ color: colors.text.muted }}
        >
          This helps us create your personalized astrology profile
        </p>
      </div>

      {/* Form Card */}
      <div 
        className="flex-1 px-5 pb-safe"
        style={{ paddingBottom: 'calc(env(safe-area-inset-bottom) + 100px)' }}
      >
        <div 
          className="rounded-2xl p-5 space-y-5"
          style={{ 
            background: `rgba(255, 255, 255, 0.95)`,
            boxShadow: shadows.lg
          }}
        >
          {/* Name Input */}
          <div>
            <label 
              className="block text-sm font-medium mb-2"
              style={{ color: colors.text.dark }}
            >
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your full name"
              className="w-full px-4 py-3 rounded-xl text-base transition-all focus:outline-none focus:ring-2"
              style={{
                background: colors.background.card,
                border: `1px solid ${errors.name ? colors.ui.error : colors.ui.borderDark}`,
                color: colors.text.dark,
                borderRadius: borderRadius.md
              }}
              data-testid="birth-name-input"
            />
            {errors.name && (
              <p className="text-xs mt-1" style={{ color: colors.ui.error }}>{errors.name}</p>
            )}
          </div>

          {/* Date of Birth */}
          <div>
            <label 
              className="block text-sm font-medium mb-2"
              style={{ color: colors.text.dark }}
            >
              Date of Birth
            </label>
            <DateInput
              value={dateOfBirth}
              onChange={setDateOfBirth}
              placeholder="Select date"
            />
            {errors.dateOfBirth && (
              <p className="text-xs mt-1" style={{ color: colors.ui.error }}>{errors.dateOfBirth}</p>
            )}
          </div>

          {/* Time of Birth */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label 
                className="text-sm font-medium"
                style={{ color: colors.text.dark }}
              >
                Time of Birth
              </label>
              <button
                onClick={handleSkipTimeToggle}
                className="text-xs font-medium transition-colors"
                style={{ color: skipTime ? colors.ui.success : colors.teal.primary }}
                data-testid="skip-birth-time-btn"
              >
                {skipTime ? '✓ Skipped' : "I don't know"}
              </button>
            </div>
            <TimeInput
              value={timeOfBirth}
              onChange={setTimeOfBirth}
              disabled={skipTime}
              placeholder="Select time"
            />
            {skipTime && (
              <p 
                className="text-xs mt-2 flex items-center gap-1"
                style={{ color: colors.text.secondary }}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                No worries! We can still provide guidance without exact time
              </p>
            )}
          </div>

          {/* Place of Birth */}
          <div>
            <label 
              className="block text-sm font-medium mb-2"
              style={{ color: colors.text.dark }}
            >
              Place of Birth
            </label>
            <input
              type="text"
              value={placeOfBirth}
              onChange={(e) => setPlaceOfBirth(e.target.value)}
              placeholder="City, State, Country"
              className="w-full px-4 py-3 rounded-xl text-base transition-all focus:outline-none focus:ring-2"
              style={{
                background: colors.background.card,
                border: `1px solid ${errors.placeOfBirth ? colors.ui.error : colors.ui.borderDark}`,
                color: colors.text.dark,
                borderRadius: borderRadius.md
              }}
              data-testid="birth-place-input"
            />
            {errors.placeOfBirth && (
              <p className="text-xs mt-1" style={{ color: colors.ui.error }}>{errors.placeOfBirth}</p>
            )}
          </div>
        </div>

        {/* Privacy note */}
        <p 
          className="text-xs text-center mt-4 px-6"
          style={{ color: colors.text.muted }}
        >
          🔒 Your information is secure and never shared
        </p>
      </div>

      {/* Fixed CTA */}
      <div 
        className="fixed bottom-0 left-0 right-0 p-5 border-t"
        style={{ 
          background: `linear-gradient(to top, ${colors.teal.dark} 0%, ${colors.teal.primary} 100%)`,
          borderColor: colors.ui.border,
          paddingBottom: 'calc(env(safe-area-inset-bottom) + 20px)'
        }}
      >
        <button
          onClick={handleSubmit}
          disabled={!isFormValid}
          className="w-full py-4 rounded-xl font-semibold text-base transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: isFormValid ? colors.gold.primary : `${colors.gold.primary}80`,
            color: colors.text.dark,
            boxShadow: isFormValid ? shadows.md : 'none'
          }}
          data-testid="birth-details-continue-btn"
        >
          Continue
        </button>
      </div>
    </div>
  );
}
