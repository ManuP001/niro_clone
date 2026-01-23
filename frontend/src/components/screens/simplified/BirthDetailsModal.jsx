import React, { useState, useRef, useEffect } from 'react';
import { BACKEND_URL } from '../../../config';

/**
 * BirthDetailsModal - Collect birth details for Kundli with NIRO V2 styling
 */
export default function BirthDetailsModal({ token, isOpen, onClose, onComplete, isOnboarding = false }) {
  const [formData, setFormData] = useState({
    name: '',
    dob: '',
    tob: '12:00',
    location: '',
    birth_place_lat: null,
    birth_place_lon: null,
    birth_place_tz: 5.5,
    gender: '',
    marital_status: '',
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

    if (!formData.name.trim() || !formData.dob || !formData.tob || !formData.location.trim() || !formData.gender || !formData.marital_status) {
      setError('Please fill in all fields');
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

  if (!isOpen) return null;

  // Teal gradient background (same as login screen)
  const TEAL_GRADIENT = 'linear-gradient(180deg, #3E827A 0%, #5A9A92 30%, #7AB5AD 60%, #A8D5CF 85%, #E8F0ED 100%)';

  // For onboarding, render as full-screen; otherwise render as modal
  if (isOnboarding) {
    return (
      <div 
        className="min-h-screen flex flex-col items-center justify-center p-4"
        style={{ background: TEAL_GRADIENT }}
      >
        <div 
          className="w-full max-w-md rounded-2xl p-6 max-h-[90vh] overflow-y-auto"
          style={{ backgroundColor: 'rgba(255,255,255,0.95)' }}
        >
          {renderFormContent()}
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div 
        className="w-full max-w-md rounded-2xl p-6 max-h-[90vh] overflow-y-auto"
        style={{ backgroundColor: 'rgba(255,255,255,0.95)' }}
      >
        {renderFormContent()}
      </div>
    </div>
  );

  function renderFormContent() {
    return (
      <>
        {/* Header */}
        <div className="text-center mb-6">
          <div 
            className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
            style={{ background: 'linear-gradient(135deg, #3E827A 0%, #5A9A92 100%)' }}
          >
            <span className="text-3xl">🌟</span>
          </div>
          <h2 className="text-xl font-bold" style={{ color: '#3E827A' }}>
            {isOnboarding ? 'Tell us about yourself' : 'Complete Your Profile'}
          </h2>
          <p className="text-sm mt-1" style={{ color: '#5A9A92' }}>
            {isOnboarding ? 'This helps us create your personalized Kundli' : 'Enter your birth details to view your Kundli'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Full Name</label>
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
            <label className="block text-sm font-medium mb-2" style={{ color: '#5c5c5c' }}>Time of Birth (approx)</label>
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
                required
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
          <div className={`flex gap-3 pt-2 ${isOnboarding ? 'flex-col' : ''}`}>
            {!isOnboarding && (
              <button
                type="button"
                onClick={onClose}
                className="flex-1 py-3 rounded-xl font-medium transition-all border"
                style={{ backgroundColor: 'white', borderColor: '#e5d188', color: '#5c5c5c' }}
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 rounded-xl font-medium transition-all"
              style={{ backgroundColor: '#d7b870', color: '#f0e9d1' }}
              data-testid="birth-details-submit"
            >
              {loading ? 'Saving...' : isOnboarding ? 'Continue' : 'Save & View Kundli'}
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
