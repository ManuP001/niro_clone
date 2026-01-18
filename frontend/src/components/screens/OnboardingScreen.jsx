import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, MapPin, X } from 'lucide-react';
import { BACKEND_URL } from '../../config';

// Custom Date Picker Modal Component
const DatePickerModal = ({ isOpen, onClose, onSet, currentValue }) => {
  const currentDate = currentValue ? new Date(currentValue) : new Date();
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50">
      <div className="w-full sm:w-96 bg-white rounded-t-3xl sm:rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Select Date of Birth</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-8">
          {/* Day Dropdown */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Day</label>
            <select
              value={day}
              onChange={(e) => setDay(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none"
            >
              {days.map((d) => (
                <option key={d} value={d}>{String(d).padStart(2, '0')}</option>
              ))}
            </select>
          </div>

          {/* Month Dropdown */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Month</label>
            <select
              value={month}
              onChange={(e) => setMonth(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none"
            >
              {months.map((m, idx) => (
                <option key={idx} value={idx}>{m}</option>
              ))}
            </select>
          </div>

          {/* Year Dropdown */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Year</label>
            <select
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none"
            >
              {years.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSet}
            className="flex-1 px-4 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors"
          >
            Set Date
          </button>
        </div>
      </div>
    </div>
  );
};

// Custom Time Picker Modal Component
const TimePickerModal = ({ isOpen, onClose, onSet, currentValue }) => {
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50">
      <div className="w-full sm:w-96 bg-white rounded-t-3xl sm:rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Select Time of Birth</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex gap-4 mb-8">
          {/* Hour Dropdown */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Hour</label>
            <select
              value={hour}
              onChange={(e) => setHour(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none"
            >
              {hours.map((h) => (
                <option key={h} value={h}>{String(h).padStart(2, '0')}</option>
              ))}
            </select>
          </div>

          {/* Minute Dropdown */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Minute</label>
            <select
              value={minute}
              onChange={(e) => setMinute(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none"
            >
              {minutes.map((m) => (
                <option key={m} value={m}>{String(m).padStart(2, '0')}</option>
              ))}
            </select>
          </div>

          {/* AM/PM Toggle */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">Period</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setPeriod('AM')}
                className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
                  period === 'AM'
                    ? 'bg-emerald-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                AM
              </button>
              <button
                type="button"
                onClick={() => setPeriod('PM')}
                className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
                  period === 'PM'
                    ? 'bg-emerald-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                PM
              </button>
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSet}
            className="flex-1 px-4 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors"
          >
            Set Time
          </button>
        </div>
      </div>
    </div>
  );
};

const OnboardingScreen = ({ token, onComplete }) => {
  const [formData, setFormData] = useState({
    name: '',
    dob: '1986-01-24',  // Preset: 24/01/1986
    tob: '06:32',       // Preset: 06:32 am
    location: '',
    birth_place_lat: null,
    birth_place_lon: null,
    birth_place_tz: 5.5,
    gender: '',         // NEW: Gender field
    marital_status: '', // NEW: Marital status field
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [placeSuggestions, setPlaceSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const suggestionsRef = useRef(null);

  // Handle location search with debounce
  const handleLocationSearch = async (value) => {
    setSearchQuery(value);
    setFormData((prev) => ({
      ...prev,
      location: value,
    }));

    // Minimum 2 characters before search (improved from 3)
    if (value.length < 2) {
      setPlaceSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      // Use /api/utils/search-cities for worldwide city autocomplete (now powered by Vedic API)
      const response = await fetch(`${BACKEND_URL}/api/utils/search-cities?query=${encodeURIComponent(value)}&max_results=15`);
      const data = await response.json();
      
      // Transform response: map cities to suggestion format
      if (data.cities) {
        const suggestions = data.cities.map((city) => ({
          label: city.display_name || city.name,
          city: city.name,
          state: city.state,
          country: city.country,
          lat: city.lat,
          lon: city.lon,
          // Use tz_offset if available (from Vedic API), otherwise derive from timezone
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

  // Handle place selection - store structured location object
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
    setSearchQuery('');
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // State for the "Loading your stars" animation
  const [loadingStars, setLoadingStars] = useState(false);
  
  // Pre-generate star positions to avoid Math.random in render
  const [starPositions] = useState(() => 
    [...Array(50)].map((_, i) => ({
      id: i,
      width: (i % 3) + 1 + 'px',
      height: (i % 3) + 1 + 'px',
      top: ((i * 17) % 100) + '%',
      left: ((i * 23) % 100) + '%',
      animationDelay: ((i * 0.1) % 2) + 's',
      animationDuration: ((i * 0.15) % 2) + 1 + 's',
      opacity: 0.3 + ((i % 7) * 0.1),
    }))
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Basic validation
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

      // Show "Loading your stars" animation
      setLoading(false);
      setLoadingStars(true);

      // Wait for profile to be saved and prepare personalized data
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Call completion callback
      onComplete();
    } catch (err) {
      console.error('Onboarding error:', err);
      console.error('BACKEND_URL was:', BACKEND_URL);
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Network error. Please check your connection and try again.');
      } else {
        setError(`Network error: ${err.message}. Please try again.`);
      }
      setLoading(false);
    }
  };

  // Loading your stars animation screen
  if (loadingStars) {
    return (
      <div className="h-screen w-full bg-gradient-to-b from-indigo-950 via-purple-950 to-slate-900 flex flex-col items-center justify-center px-4">
        {/* Animated stars background */}
        <div className="absolute inset-0 overflow-hidden">
          {starPositions.map((star) => (
            <div
              key={star.id}
              className="absolute rounded-full bg-white animate-pulse"
              style={{
                width: star.width,
                height: star.height,
                top: star.top,
                left: star.left,
                animationDelay: star.animationDelay,
                animationDuration: star.animationDuration,
                opacity: star.opacity,
              }}
            />
          ))}
        </div>

        {/* Main content */}
        <div className="relative z-10 text-center">
          {/* Animated celestial orb */}
          <div className="relative w-32 h-32 mx-auto mb-8">
            {/* Outer glow ring */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-amber-400/20 via-orange-400/20 to-yellow-400/20 animate-ping" style={{ animationDuration: '2s' }} />
            
            {/* Middle ring */}
            <div className="absolute inset-2 rounded-full bg-gradient-to-r from-amber-500/30 via-orange-500/30 to-yellow-500/30 animate-pulse" />
            
            {/* Inner orb with sun/star symbol */}
            <div className="absolute inset-4 rounded-full bg-gradient-to-br from-amber-400 via-orange-500 to-yellow-500 flex items-center justify-center shadow-lg shadow-orange-500/50">
              <span className="text-4xl">✨</span>
            </div>

            {/* Orbiting elements */}
            <div className="absolute inset-0 animate-spin" style={{ animationDuration: '8s' }}>
              <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1 w-3 h-3 rounded-full bg-blue-400 shadow-lg shadow-blue-400/50" />
            </div>
            <div className="absolute inset-0 animate-spin" style={{ animationDuration: '6s', animationDirection: 'reverse' }}>
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1 w-2 h-2 rounded-full bg-purple-400 shadow-lg shadow-purple-400/50" />
            </div>
            <div className="absolute inset-0 animate-spin" style={{ animationDuration: '10s' }}>
              <div className="absolute top-1/2 right-0 translate-x-1 -translate-y-1/2 w-2.5 h-2.5 rounded-full bg-teal-400 shadow-lg shadow-teal-400/50" />
            </div>
          </div>

          {/* Loading text */}
          <h2 className="text-2xl font-bold text-white mb-3">Loading your stars...</h2>
          <p className="text-indigo-200/80 text-sm max-w-xs mx-auto">
            Mapping your celestial blueprint and preparing your personalized insights
          </p>

          {/* Animated dots */}
          <div className="flex justify-center gap-1.5 mt-6">
            <div className="w-2 h-2 rounded-full bg-amber-400 animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 rounded-full bg-orange-400 animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 rounded-full bg-yellow-400 animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-full bg-white flex flex-col items-center justify-center px-4">
      {/* Header */}
      <div className="mb-12 text-center">
        <div className="w-12 h-12 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-white text-lg font-bold">N</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Complete Your Profile</h1>
        <p className="text-gray-600">Tell us about yourself to personalize your experience</p>
      </div>

      {/* Form container */}
      <div className="w-full max-w-sm pb-8">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Your full name"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-base"
              required
            />
          </div>

          {/* Gender */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gender
            </label>
            <div className="flex gap-3">
              {['Male', 'Female', 'Other'].map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setFormData((prev) => ({ ...prev, gender: option.toLowerCase() }))}
                  className={`flex-1 py-3 rounded-lg font-medium transition-colors border ${
                    formData.gender === option.toLowerCase()
                      ? 'bg-emerald-600 text-white border-emerald-600'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>

          {/* Marital Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Marital Status
            </label>
            <div className="flex gap-3">
              {['Single', 'Married', 'Other'].map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setFormData((prev) => ({ ...prev, marital_status: option.toLowerCase() }))}
                  className={`flex-1 py-3 rounded-lg font-medium transition-colors border ${
                    formData.marital_status === option.toLowerCase()
                      ? 'bg-emerald-600 text-white border-emerald-600'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>

          {/* Date of Birth - Custom Picker */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date of Birth
            </label>
            <button
              type="button"
              onClick={() => setShowDatePicker(true)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-left bg-white hover:bg-gray-50 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-colors"
            >
              <span className={formData.dob ? 'text-gray-900' : 'text-gray-500'}>
                {formData.dob || 'Select date (YYYY-MM-DD)'}
              </span>
            </button>
          </div>

          {/* Time of Birth - Custom Picker */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time of Birth (approx)
            </label>
            <button
              type="button"
              onClick={() => setShowTimePicker(true)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-left bg-white hover:bg-gray-50 focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-colors"
            >
              <span className={formData.tob ? 'text-gray-900' : 'text-gray-500'}>
                {formData.tob || 'Select time (HH:MM)'}
              </span>
            </button>
          </div>

          {/* Location with Autocomplete */}
          <div ref={suggestionsRef} className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Place of Birth
            </label>
            <div className="relative">
              <MapPin className="absolute left-3 top-3.5 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={formData.location}
                onChange={(e) => handleLocationSearch(e.target.value)}
                onFocus={() => formData.location.length >= 2 && setShowSuggestions(true)}
                placeholder="Search city, state, country..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-base"
                required
              />
            </div>

            {/* City Suggestions Dropdown */}
            {showSuggestions && placeSuggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto">
                {placeSuggestions.map((place, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectPlace(place)}
                    className="w-full text-left px-4 py-2 hover:bg-emerald-50 transition-colors border-b border-gray-100 last:border-b-0"
                  >
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{place.label}</p>
                        <p className="text-xs text-gray-500">Lat: {place.lat.toFixed(2)}, Lon: {place.lon.toFixed(2)}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Selected place confirmation */}
            {formData.birth_place_lat && (
              <p className="text-xs text-emerald-600 mt-1">✓ Location confirmed with coordinates</p>
            )}
          </div>

          {/* Error message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Submit button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-emerald-600 text-white py-3 rounded-lg font-medium hover:bg-emerald-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors mt-6"
          >
            {loading ? 'Saving...' : 'Continue to Chat'}
          </button>
        </form>
      </div>

      {/* Date Picker Modal */}
      <DatePickerModal
        isOpen={showDatePicker}
        onClose={() => setShowDatePicker(false)}
        onSet={(dateStr) => setFormData((prev) => ({ ...prev, dob: dateStr }))}
        currentValue={formData.dob}
      />

      {/* Time Picker Modal */}
      <TimePickerModal
        isOpen={showTimePicker}
        onClose={() => setShowTimePicker(false)}
        onSet={(timeStr) => setFormData((prev) => ({ ...prev, tob: timeStr }))}
        currentValue={formData.tob}
      />
    </div>
  );
};

export default OnboardingScreen;
