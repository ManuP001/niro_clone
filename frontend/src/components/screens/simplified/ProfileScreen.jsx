import React, { useState, useEffect, useRef } from 'react';
import { BACKEND_URL } from '../../../config';
import { trackEvent } from './utils';
import { colors, shadows } from './theme';
import ResponsiveHeader from './ResponsiveHeader';

/**
 * ProfileScreen V3 - User profile with ResponsiveHeader and new theme
 */
export default function ProfileScreen({ token, userId, onResetDemo, hasBottomNav, onBack, onNavigate, onTabChange }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);

  const loadProfile = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/profile/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setProfile(data.profile || data);
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
    trackEvent('profile_viewed', { flow_version: 'simplified_v2' }, token);
  }, [token]);

  const handleEditComplete = () => {
    setShowEditModal(false);
    setLoading(true);
    loadProfile();
  };

  return (
    <div 
      className={`min-h-screen ${hasBottomNav ? 'pb-20' : ''}`}
      style={{ backgroundColor: '#f5f0e3' }}
    >
      {/* Header */}
      <div 
        className="px-6 pt-12 pb-8"
        style={{ background: 'linear-gradient(135deg, #d7b870 0%, #c9a85a 100%)' }}
      >
        <h1 className="text-2xl font-bold" style={{ color: '#f0e9d1' }}>Profile</h1>
        <p style={{ color: 'rgba(240,233,209,0.8)' }}>Manage your account</p>
      </div>

      <div className="px-6 py-6">
        {loading ? (
          <div className="text-center py-8">
            <div 
              className="w-12 h-12 border-4 rounded-full animate-spin mx-auto mb-4"
              style={{ borderColor: 'rgba(215,184,112,0.3)', borderTopColor: '#d7b870' }}
            />
            <p style={{ color: '#9a8a6a' }}>Loading profile...</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Profile Avatar */}
            <div className="flex items-center justify-center mb-6">
              <div 
                className="w-24 h-24 rounded-full flex items-center justify-center"
                style={{ background: 'linear-gradient(135deg, #d7b870 0%, #c9a85a 100%)' }}
              >
                <span className="text-4xl">👤</span>
              </div>
            </div>

            {/* Profile Info Card */}
            <div 
              className="rounded-xl p-4"
              style={{ backgroundColor: 'white', border: '1px solid #e5d188' }}
            >
              <h2 className="font-semibold mb-4" style={{ color: '#5c5c5c' }}>Account Information</h2>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: '#e5d188' }}>
                  <span style={{ color: '#9a8a6a' }}>Name</span>
                  <span style={{ color: '#5c5c5c' }}>{profile?.name || 'Not set'}</span>
                </div>
                
                <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: '#e5d188' }}>
                  <span style={{ color: '#9a8a6a' }}>Email/Phone</span>
                  <span style={{ color: '#5c5c5c' }}>{profile?.email || profile?.phone || userId || 'Not set'}</span>
                </div>
                
                {profile?.gender && (
                  <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: '#e5d188' }}>
                    <span style={{ color: '#9a8a6a' }}>Gender</span>
                    <span style={{ color: '#5c5c5c' }} className="capitalize">{profile.gender}</span>
                  </div>
                )}
                
                {profile?.marital_status && (
                  <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: '#e5d188' }}>
                    <span style={{ color: '#9a8a6a' }}>Marital Status</span>
                    <span style={{ color: '#5c5c5c' }} className="capitalize">{profile.marital_status}</span>
                  </div>
                )}
                
                {profile?.dob && (
                  <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: '#e5d188' }}>
                    <span style={{ color: '#9a8a6a' }}>Date of Birth</span>
                    <span style={{ color: '#5c5c5c' }}>{profile.dob}</span>
                  </div>
                )}
                
                {profile?.tob && (
                  <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: '#e5d188' }}>
                    <span style={{ color: '#9a8a6a' }}>Time of Birth</span>
                    <span style={{ color: '#5c5c5c' }}>{profile.tob}</span>
                  </div>
                )}
                
                {profile?.location && (
                  <div className="flex items-center justify-between py-2">
                    <span style={{ color: '#9a8a6a' }}>Place of Birth</span>
                    <span style={{ color: '#5c5c5c' }} className="text-right max-w-[60%] truncate">{profile.location}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Edit Profile Button */}
            <button 
              className="w-full py-3 rounded-xl font-medium transition-all hover:shadow-md"
              style={{ backgroundColor: '#d7b870', color: '#f0e9d1' }}
              onClick={() => setShowEditModal(true)}
            >
              Edit Profile
            </button>

            {/* DEV Section */}
            <div 
              className="rounded-xl p-4 mt-6"
              style={{ backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)' }}
            >
              <h3 className="font-semibold mb-2 text-red-600">DEV Options</h3>
              <p className="text-sm text-red-500 mb-3">For testing purposes only</p>
              
              <button 
                onClick={onResetDemo}
                className="w-full py-2 rounded-lg font-medium bg-red-500 text-white hover:bg-red-600 transition-all"
              >
                Reset Demo State
              </button>
              <p className="text-xs text-red-400 mt-2 text-center">
                This will clear localStorage and return to New User mode
              </p>
            </div>

            {/* App Info */}
            <div className="text-center pt-6">
              <p className="text-sm" style={{ color: '#9a8a6a' }}>NIRO Astrology v2.0</p>
              <p className="text-xs mt-1" style={{ color: '#baa87a' }}>Unlimited access to experts</p>
            </div>
          </div>
        )}
      </div>

      {/* Edit Profile Modal */}
      {showEditModal && (
        <EditProfileModal
          token={token}
          profile={profile}
          onClose={() => setShowEditModal(false)}
          onComplete={handleEditComplete}
        />
      )}
    </div>
  );
}

/**
 * EditProfileModal - Full edit profile form with NIRO V2 styling
 */
function EditProfileModal({ token, profile, onClose, onComplete }) {
  const [formData, setFormData] = useState({
    name: profile?.name || '',
    dob: profile?.dob || '',
    tob: profile?.tob || '12:00',
    location: profile?.location || '',
    birth_place_lat: profile?.birth_place_lat || null,
    birth_place_lon: profile?.birth_place_lon || null,
    birth_place_tz: profile?.birth_place_tz || 5.5,
    gender: profile?.gender || '',
    marital_status: profile?.marital_status || '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [placeSuggestions, setPlaceSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const suggestionsRef = useRef(null);

  // Handle location search
  const handleLocationSearch = async (value) => {
    setFormData((prev) => ({ ...prev, location: value }));

    if (value.length < 2) {
      setPlaceSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/utils/search-cities?query=${encodeURIComponent(value)}&max_results=15`);
      const data = await response.json();
      
      if (data.cities) {
        const suggestions = data.cities.map((city) => ({
          label: city.display_name || city.name,
          city: city.name,
          state: city.state,
          country: city.country,
          lat: city.lat,
          lon: city.lon,
          tz: city.tz_offset || (city.timezone === 'Asia/Kolkata' ? 5.5 : 0)
        }));
        setPlaceSuggestions(suggestions);
        setShowSuggestions(true);
      } else {
        setPlaceSuggestions([]);
      }
    } catch (err) {
      console.error('Place search error:', err);
      setPlaceSuggestions([]);
    }
  };

  const handleSelectPlace = (place) => {
    const displayName = `${place.city}${place.state ? ', ' + place.state : ''}${place.country ? ', ' + place.country : ''}`;
    setFormData((prev) => ({
      ...prev,
      location: displayName,
      birth_place_lat: place.lat,
      birth_place_lon: place.lon,
      birth_place_tz: place.tz,
    }));
    setShowSuggestions(false);
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!formData.name.trim()) {
      setError('Name is required');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/profile/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok || !data.ok) {
        setError(data.detail || 'Failed to save profile');
        setLoading(false);
        return;
      }

      setLoading(false);
      onComplete();
    } catch (err) {
      console.error('Profile save error:', err);
      setError('Network error. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div 
        className="w-full max-w-md rounded-2xl p-6 max-h-[90vh] overflow-y-auto"
        style={{ backgroundColor: '#f5f0e3' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold" style={{ color: '#5c5c5c' }}>Edit Profile</h2>
          <button onClick={onClose} className="text-2xl" style={{ color: '#9a8a6a' }}>×</button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Full Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Your full name"
              className="w-full px-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
              style={{ 
                backgroundColor: 'white', 
                borderColor: '#e5d188',
                color: '#5c5c5c'
              }}
              required
            />
          </div>

          {/* Gender */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Gender</label>
            <div className="flex gap-2">
              {['Male', 'Female', 'Other'].map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, gender: option.toLowerCase() }))}
                  className="flex-1 py-3 rounded-xl font-medium transition-all border"
                  style={{
                    backgroundColor: formData.gender === option.toLowerCase() ? '#d7b870' : 'white',
                    borderColor: '#e5d188',
                    color: formData.gender === option.toLowerCase() ? '#f0e9d1' : '#5c5c5c'
                  }}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>

          {/* Marital Status */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Marital Status</label>
            <div className="flex gap-2">
              {['Single', 'Married', 'Other'].map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, marital_status: option.toLowerCase() }))}
                  className="flex-1 py-3 rounded-xl font-medium transition-all border"
                  style={{
                    backgroundColor: formData.marital_status === option.toLowerCase() ? '#d7b870' : 'white',
                    borderColor: '#e5d188',
                    color: formData.marital_status === option.toLowerCase() ? '#f0e9d1' : '#5c5c5c'
                  }}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>

          {/* Date of Birth */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Date of Birth</label>
            <button
              type="button"
              onClick={() => setShowDatePicker(true)}
              className="w-full px-4 py-3 rounded-xl text-left border transition-all"
              style={{ 
                backgroundColor: 'white', 
                borderColor: '#e5d188',
                color: formData.dob ? '#5c5c5c' : '#9a8a6a'
              }}
            >
              {formData.dob || 'Select date'}
            </button>
          </div>

          {/* Time of Birth */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Time of Birth</label>
            <button
              type="button"
              onClick={() => setShowTimePicker(true)}
              className="w-full px-4 py-3 rounded-xl text-left border transition-all"
              style={{ 
                backgroundColor: 'white', 
                borderColor: '#e5d188',
                color: formData.tob ? '#5c5c5c' : '#9a8a6a'
              }}
            >
              {formData.tob || 'Select time'}
            </button>
          </div>

          {/* Location */}
          <div ref={suggestionsRef} className="relative">
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Place of Birth</label>
            <div className="relative">
              <span className="absolute left-3 top-3.5 text-lg">📍</span>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => handleLocationSearch(e.target.value)}
                onFocus={() => formData.location.length >= 2 && setShowSuggestions(true)}
                placeholder="Search city, state, country..."
                className="w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2"
                style={{ 
                  backgroundColor: 'white', 
                  borderColor: '#e5d188',
                  color: '#5c5c5c'
                }}
              />
            </div>

            {showSuggestions && placeSuggestions.length > 0 && (
              <div 
                className="absolute top-full left-0 right-0 mt-1 rounded-xl shadow-lg z-50 max-h-48 overflow-y-auto"
                style={{ backgroundColor: 'white', border: '1px solid #e5d188' }}
              >
                {placeSuggestions.map((place, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectPlace(place)}
                    className="w-full text-left px-4 py-2 hover:bg-amber-50 transition-colors border-b last:border-b-0"
                    style={{ borderColor: '#e5d188' }}
                  >
                    <div className="flex items-center gap-2">
                      <span style={{ color: '#d7b870' }}>📍</span>
                      <div>
                        <p className="text-sm font-medium" style={{ color: '#5c5c5c' }}>{place.label}</p>
                        <p className="text-xs" style={{ color: '#9a8a6a' }}>Lat: {place.lat.toFixed(2)}, Lon: {place.lon.toFixed(2)}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {formData.birth_place_lat && (
              <p className="text-xs mt-1" style={{ color: '#d7b870' }}>✓ Location confirmed</p>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="p-3 rounded-xl text-sm" style={{ backgroundColor: '#fee2e2', color: '#dc2626' }}>
              {error}
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 rounded-xl font-medium transition-all border"
              style={{ backgroundColor: 'white', borderColor: '#e5d188', color: '#5c5c5c' }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 rounded-xl font-medium transition-all"
              style={{ backgroundColor: '#d7b870', color: '#f0e9d1' }}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>

        {/* Date Picker Modal */}
        {showDatePicker && (
          <DatePickerModal
            currentValue={formData.dob}
            onSet={(val) => setFormData(prev => ({ ...prev, dob: val }))}
            onClose={() => setShowDatePicker(false)}
          />
        )}

        {/* Time Picker Modal */}
        {showTimePicker && (
          <TimePickerModal
            currentValue={formData.tob}
            onSet={(val) => setFormData(prev => ({ ...prev, tob: val }))}
            onClose={() => setShowTimePicker(false)}
          />
        )}
      </div>
    </div>
  );
}

// Date Picker Modal with NIRO styling
function DatePickerModal({ currentValue, onSet, onClose }) {
  const currentDate = currentValue ? new Date(currentValue) : new Date(1990, 0, 1);
  const [day, setDay] = useState(currentDate.getDate());
  const [month, setMonth] = useState(currentDate.getMonth());
  const [year, setYear] = useState(currentDate.getFullYear());

  const currentYear = new Date().getFullYear();
  const days = Array.from({ length: 31 }, (_, i) => i + 1);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const years = Array.from({ length: currentYear - 1900 + 1 }, (_, i) => currentYear - i).sort((a, b) => a - b);

  const handleSet = () => {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    onSet(dateStr);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-[60]">
      <div 
        className="w-full sm:w-96 rounded-t-2xl sm:rounded-2xl p-6"
        style={{ backgroundColor: '#f5f0e3' }}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold" style={{ color: '#5c5c5c' }}>Select Date of Birth</h2>
          <button onClick={onClose} style={{ color: '#9a8a6a' }}>✕</button>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Day</label>
            <select
              value={day}
              onChange={(e) => setDay(parseInt(e.target.value))}
              className="w-full px-3 py-2 rounded-xl border focus:outline-none"
              style={{ backgroundColor: 'white', borderColor: '#e5d188', color: '#5c5c5c' }}
            >
              {days.map((d) => <option key={d} value={d}>{String(d).padStart(2, '0')}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Month</label>
            <select
              value={month}
              onChange={(e) => setMonth(parseInt(e.target.value))}
              className="w-full px-3 py-2 rounded-xl border focus:outline-none"
              style={{ backgroundColor: 'white', borderColor: '#e5d188', color: '#5c5c5c' }}
            >
              {months.map((m, idx) => <option key={idx} value={idx}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Year</label>
            <select
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value))}
              className="w-full px-3 py-2 rounded-xl border focus:outline-none"
              style={{ backgroundColor: 'white', borderColor: '#e5d188', color: '#5c5c5c' }}
            >
              {years.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-xl font-medium border"
            style={{ backgroundColor: 'white', borderColor: '#e5d188', color: '#5c5c5c' }}
          >
            Cancel
          </button>
          <button
            onClick={handleSet}
            className="flex-1 py-3 rounded-xl font-medium"
            style={{ backgroundColor: '#d7b870', color: '#f0e9d1' }}
          >
            Set Date
          </button>
        </div>
      </div>
    </div>
  );
}

// Time Picker Modal with NIRO styling
function TimePickerModal({ currentValue, onSet, onClose }) {
  const currentTime = currentValue ? currentValue.split(':') : ['12', '00'];
  const [hour, setHour] = useState(parseInt(currentTime[0]) || 12);
  const [minute, setMinute] = useState(parseInt(currentTime[1]) || 0);
  const [period, setPeriod] = useState(hour >= 12 ? 'PM' : 'AM');

  const hours = Array.from({ length: 12 }, (_, i) => i + 1);
  const minutes = Array.from({ length: 60 }, (_, i) => i);

  const handleSet = () => {
    let hour24 = hour;
    if (period === 'AM' && hour === 12) hour24 = 0;
    else if (period === 'PM' && hour !== 12) hour24 = hour + 12;
    
    const timeStr = `${String(hour24).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
    onSet(timeStr);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-[60]">
      <div 
        className="w-full sm:w-96 rounded-t-2xl sm:rounded-2xl p-6"
        style={{ backgroundColor: '#f5f0e3' }}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold" style={{ color: '#5c5c5c' }}>Select Time of Birth</h2>
          <button onClick={onClose} style={{ color: '#9a8a6a' }}>✕</button>
        </div>

        <div className="flex gap-4 mb-6">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Hour</label>
            <select
              value={hour}
              onChange={(e) => setHour(parseInt(e.target.value))}
              className="w-full px-3 py-2 rounded-xl border focus:outline-none"
              style={{ backgroundColor: 'white', borderColor: '#e5d188', color: '#5c5c5c' }}
            >
              {hours.map((h) => <option key={h} value={h}>{String(h).padStart(2, '0')}</option>)}
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Minute</label>
            <select
              value={minute}
              onChange={(e) => setMinute(parseInt(e.target.value))}
              className="w-full px-3 py-2 rounded-xl border focus:outline-none"
              style={{ backgroundColor: 'white', borderColor: '#e5d188', color: '#5c5c5c' }}
            >
              {minutes.map((m) => <option key={m} value={m}>{String(m).padStart(2, '0')}</option>)}
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Period</label>
            <div className="flex gap-1">
              <button
                type="button"
                onClick={() => setPeriod('AM')}
                className="flex-1 py-2 rounded-lg font-medium transition-all"
                style={{
                  backgroundColor: period === 'AM' ? '#d7b870' : 'white',
                  color: period === 'AM' ? '#f0e9d1' : '#5c5c5c'
                }}
              >
                AM
              </button>
              <button
                type="button"
                onClick={() => setPeriod('PM')}
                className="flex-1 py-2 rounded-lg font-medium transition-all"
                style={{
                  backgroundColor: period === 'PM' ? '#d7b870' : 'white',
                  color: period === 'PM' ? '#f0e9d1' : '#5c5c5c'
                }}
              >
                PM
              </button>
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-xl font-medium border"
            style={{ backgroundColor: 'white', borderColor: '#e5d188', color: '#5c5c5c' }}
          >
            Cancel
          </button>
          <button
            onClick={handleSet}
            className="flex-1 py-3 rounded-xl font-medium"
            style={{ backgroundColor: '#d7b870', color: '#f0e9d1' }}
          >
            Set Time
          </button>
        </div>
      </div>
    </div>
  );
}
