import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, MapPin } from 'lucide-react';
import { BACKEND_URL } from '../../config';

const OnboardingScreen = ({ token, onComplete }) => {
  const [formData, setFormData] = useState({
    name: '',
    dob: '',
    tob: '',
    location: '',
    birth_place_lat: null,
    birth_place_lon: null,
    birth_place_tz: 5.5,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [placeSuggestions, setPlaceSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const suggestionsRef = useRef(null);

  // Handle location search with debounce
  const handleLocationSearch = async (value) => {
    setSearchQuery(value);
    setFormData((prev) => ({
      ...prev,
      location: value,
    }));

    // Minimum 2 characters before search
    if (value.length < 2) {
      setPlaceSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      // Use /api/utils/search-cities for worldwide city autocomplete
      const response = await fetch(`${BACKEND_URL}/api/utils/search-cities?query=${encodeURIComponent(value)}&max_results=10`);
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
          tz: city.timezone === 'Asia/Kolkata' ? 5.5 : 0
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Basic validation
    if (!formData.name.trim() || !formData.dob || !formData.tob || !formData.location.trim()) {
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
        return;
      }

      // Call completion callback
      onComplete();
    } catch (err) {
      setError('Network error. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

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
      <div className="w-full max-w-sm">
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

          {/* Date of Birth */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date of Birth
            </label>
            <input
              type="date"
              name="dob"
              value={formData.dob}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-base"
              required
            />
            <p className="text-xs text-gray-500 mt-1">Format: YYYY-MM-DD</p>
          </div>

          {/* Time of Birth */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time of Birth (approx)
            </label>
            <input
              type="time"
              name="tob"
              value={formData.tob}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-base"
              required
            />
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

      {/* Footer */}
      <div className="absolute bottom-4 text-center text-xs text-gray-500">
        <p>Your birth details help us provide personalized insights</p>
      </div>
    </div>
  );
};

export default OnboardingScreen;
