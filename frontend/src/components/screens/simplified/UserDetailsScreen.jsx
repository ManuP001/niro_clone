import React, { useState } from 'react';
import { colors, shadows } from './theme';
import { BACKEND_URL } from '../../../config';

/**
 * UserDetailsScreen - Collect user birth details for Kundli
 * Shown after login for new users only
 */
export default function UserDetailsScreen({ token, onComplete }) {
  const [formData, setFormData] = useState({
    name: '',
    gender: '',
    birthDate: '',
    birthTime: '',
    birthPlace: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.gender) newErrors.gender = 'Please select your gender';
    if (!formData.birthDate) newErrors.birthDate = 'Birth date is required';
    if (!formData.birthPlace.trim()) newErrors.birthPlace = 'Birth place is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    
    setIsLoading(true);
    try {
      // Save profile data - Backend expects specific field names
      const response = await fetch(`${BACKEND_URL}/api/profile/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: formData.name,
          gender: formData.gender,
          dob: formData.birthDate,  // Backend expects 'dob' in YYYY-MM-DD format
          tob: formData.birthTime || '12:00',  // Backend expects 'tob', default to noon if not provided
          location: formData.birthPlace,  // Backend expects 'location'
        }),
      });

      if (response.ok) {
        onComplete();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setErrors({ submit: errorData.detail || 'Failed to save. Please try again.' });
      }
    } catch (err) {
      console.error('Failed to save profile:', err);
      setErrors({ submit: 'Something went wrong. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ 
        background: colors.background.gradient,
        paddingTop: 'env(safe-area-inset-top)',
        paddingBottom: 'env(safe-area-inset-bottom)',
      }}
    >
      {/* Constellation Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <svg className="absolute w-full h-full opacity-15" viewBox="0 0 400 800">
          <g stroke="#ffffff" strokeWidth="0.5" fill="none">
            <line x1="80" y1="100" x2="150" y2="160" />
            <line x1="150" y1="160" x2="220" y2="120" />
            <line x1="50" y1="350" x2="120" y2="400" />
            <line x1="280" y1="320" x2="360" y2="380" />
          </g>
          <g fill="#ffffff">
            <circle cx="80" cy="100" r="2" />
            <circle cx="150" cy="160" r="3" />
            <circle cx="220" cy="120" r="2" />
            <circle cx="50" cy="350" r="2" />
            <circle cx="120" cy="400" r="3" />
            <circle cx="280" cy="320" r="2" />
            <circle cx="360" cy="380" r="2" />
          </g>
        </svg>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col px-6 pt-12 pb-6 relative z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 
            className="text-2xl font-bold mb-2"
            style={{ color: colors.text.primary }}
          >
            Tell us about yourself
          </h1>
          <p 
            className="text-sm"
            style={{ color: 'rgba(255,255,255,0.8)' }}
          >
            This helps us create your personalized Kundli
          </p>
        </div>

        {/* Form Card */}
        <div 
          className="rounded-2xl p-5 flex-1"
          style={{ 
            backgroundColor: 'rgba(255,255,255,0.95)',
            boxShadow: shadows.lg,
          }}
        >
          {/* Name */}
          <div className="mb-4">
            <label 
              className="block text-sm font-medium mb-1.5"
              style={{ color: colors.text.secondary }}
            >
              Your Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Enter your full name"
              className="w-full px-4 py-3 rounded-xl text-base focus:outline-none focus:ring-2 transition-all"
              style={{ 
                backgroundColor: colors.gold.cream,
                border: `1px solid ${errors.name ? '#ef4444' : colors.ui.borderDark}`,
                color: colors.text.dark,
              }}
            />
            {errors.name && <p className="text-xs text-red-500 mt-1">{errors.name}</p>}
          </div>

          {/* Gender */}
          <div className="mb-4">
            <label 
              className="block text-sm font-medium mb-1.5"
              style={{ color: colors.text.secondary }}
            >
              Gender *
            </label>
            <div className="flex gap-2">
              {['male', 'female', 'other'].map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => handleChange('gender', g)}
                  className="flex-1 py-3 rounded-xl text-sm font-medium capitalize transition-all"
                  style={{ 
                    backgroundColor: formData.gender === g ? colors.teal.primary : colors.gold.cream,
                    color: formData.gender === g ? '#ffffff' : colors.text.dark,
                    border: `1px solid ${errors.gender && !formData.gender ? '#ef4444' : colors.ui.borderDark}`,
                  }}
                >
                  {g}
                </button>
              ))}
            </div>
            {errors.gender && <p className="text-xs text-red-500 mt-1">{errors.gender}</p>}
          </div>

          {/* Birth Date */}
          <div className="mb-4">
            <label 
              className="block text-sm font-medium mb-1.5"
              style={{ color: colors.text.secondary }}
            >
              Date of Birth *
            </label>
            <input
              type="date"
              value={formData.birthDate}
              onChange={(e) => handleChange('birthDate', e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-base focus:outline-none focus:ring-2 transition-all"
              style={{ 
                backgroundColor: colors.gold.cream,
                border: `1px solid ${errors.birthDate ? '#ef4444' : colors.ui.borderDark}`,
                color: colors.text.dark,
              }}
            />
            {errors.birthDate && <p className="text-xs text-red-500 mt-1">{errors.birthDate}</p>}
          </div>

          {/* Birth Time (Optional) */}
          <div className="mb-4">
            <label 
              className="block text-sm font-medium mb-1.5"
              style={{ color: colors.text.secondary }}
            >
              Time of Birth <span className="text-xs font-normal">(Optional)</span>
            </label>
            <input
              type="time"
              value={formData.birthTime}
              onChange={(e) => handleChange('birthTime', e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-base focus:outline-none focus:ring-2 transition-all"
              style={{ 
                backgroundColor: colors.gold.cream,
                border: `1px solid ${colors.ui.borderDark}`,
                color: colors.text.dark,
              }}
            />
            <p className="text-xs mt-1" style={{ color: colors.text.mutedDark }}>
              If unknown, we&apos;ll use sunrise time
            </p>
          </div>

          {/* Birth Place */}
          <div className="mb-6">
            <label 
              className="block text-sm font-medium mb-1.5"
              style={{ color: colors.text.secondary }}
            >
              Place of Birth *
            </label>
            <input
              type="text"
              value={formData.birthPlace}
              onChange={(e) => handleChange('birthPlace', e.target.value)}
              placeholder="City, Country"
              className="w-full px-4 py-3 rounded-xl text-base focus:outline-none focus:ring-2 transition-all"
              style={{ 
                backgroundColor: colors.gold.cream,
                border: `1px solid ${errors.birthPlace ? '#ef4444' : colors.ui.borderDark}`,
                color: colors.text.dark,
              }}
            />
            {errors.birthPlace && <p className="text-xs text-red-500 mt-1">{errors.birthPlace}</p>}
          </div>

          {/* Submit Error */}
          {errors.submit && (
            <p className="text-sm text-red-500 text-center mb-4">{errors.submit}</p>
          )}

          {/* Continue Button */}
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="w-full py-4 rounded-xl font-semibold text-base transition-all hover:shadow-lg active:scale-[0.98] disabled:opacity-60"
            style={{ 
              backgroundColor: colors.gold.primary,
              color: colors.text.dark,
              boxShadow: shadows.md,
            }}
            data-testid="user-details-continue"
          >
            {isLoading ? 'Saving...' : 'Continue'}
          </button>
        </div>
      </div>
    </div>
  );
}
