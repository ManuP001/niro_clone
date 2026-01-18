import React, { useState, useEffect, useCallback } from 'react';
import { AlertCircle, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import { BACKEND_URL } from '../../config';
import DOMPurify from 'dompurify';

// Chart style options
const CHART_STYLES = {
  north: {
    id: 'north',
    label: 'North Indian',
    description: 'Diamond layout - Houses fixed, signs move'
  },
  south: {
    id: 'south', 
    label: 'South Indian',
    description: 'Square layout - Signs fixed, houses move'
  }
};

const KundliScreen = ({ token, userId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [kundliData, setKundliData] = useState(null);
  const [chartStyle, setChartStyle] = useState(() => {
    // Load saved preference or default to 'north'
    return localStorage.getItem('kundli_chart_style') || 'north';
  });
  const [expandedSections, setExpandedSections] = useState({
    ascendant: true,
    houses: false,
    planets: false
  });

  // Fetch kundli with selected style
  const fetchKundli = useCallback(async (style = chartStyle, retries = 3, delay = 1000) => {
    setLoading(true);
    setError(null);

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const url = `${BACKEND_URL}/api/kundli?style=${style}`;
        console.log(`[KundliScreen] Fetching from: ${url} (attempt ${attempt}/${retries})`);

        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        });

        console.log('[KundliScreen] Response status:', response.status);

        const data = await response.json();
        console.log('[KundliScreen] Response data:', data);

        if (response.ok && data.ok) {
          setKundliData(data);
          setLoading(false);
          return;
        }

        // If profile incomplete, retry after delay
        if (data.error === 'PROFILE_INCOMPLETE' && attempt < retries) {
          console.log(`Profile incomplete, retrying in ${delay}ms`);
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }

        if (data.error === 'PROFILE_INCOMPLETE') {
          setError('PROFILE_INCOMPLETE');
          setLoading(false);
          return;
        }

        setError(data.error || 'KUNDLI_FETCH_FAILED');
        setLoading(false);
        return;

      } catch (err) {
        console.error(`[KundliScreen] Error (attempt ${attempt}/${retries}):`, err);
        if (attempt < retries) {
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }
        setError('KUNDLI_FETCH_FAILED');
        setLoading(false);
        return;
      }
    }
  }, [token, chartStyle]);

  useEffect(() => {
    fetchKundli();
  }, [token]); // Only fetch on token change, not style change

  // Handle style change
  const handleStyleChange = async (newStyle) => {
    if (newStyle === chartStyle) return;
    
    setChartStyle(newStyle);
    localStorage.setItem('kundli_chart_style', newStyle);
    await fetchKundli(newStyle);
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Sanitize SVG before rendering
  const getSafeHtml = (svgString) => {
    const clean = DOMPurify.sanitize(svgString, {
      ALLOWED_TAGS: ['svg', 'g', 'path', 'circle', 'rect', 'text', 'line', 'polygon', 'polyline', 'defs', 'style', 'tspan', 'image', 'linearGradient', 'radialGradient', 'stop', 'pattern', 'clipPath', 'mask', 'use', 'symbol', 'marker', 'filter', 'feGaussianBlur', 'feOffset', 'feMerge', 'feMergeNode'],
      ALLOWED_ATTR: ['id', 'class', 'style', 'cx', 'cy', 'r', 'x', 'y', 'x1', 'y1', 'x2', 'y2', 'width', 'height', 'fill', 'stroke', 'stroke-width', 'viewBox', 'd', 'transform', 'points', 'href', 'font-size', 'text-anchor', 'dominant-baseline', 'data-name', 'rx', 'ry', 'xmlns', 'version', 'offset', 'stop-color', 'stop-opacity', 'opacity', 'font-family', 'font-weight', 'font-style', 'patternUnits', 'gradientUnits', 'spreadMethod', 'xlink:href', 'clip-path', 'mask', 'filter', 'stdDeviation', 'dx', 'dy', 'result', 'in', 'in2', 'scale']
    });
    return clean;
  };

  // Planet full names mapping
  const getPlanetFullName = (abbr) => {
    const names = {
      'Su': 'Sun', 'Mo': 'Moon', 'Ma': 'Mars', 'Me': 'Mercury',
      'Ju': 'Jupiter', 'Ve': 'Venus', 'Sa': 'Saturn', 'Ra': 'Rahu', 'Ke': 'Ketu'
    };
    return names[abbr] || abbr;
  };

  if (loading) {
    return (
      <div className="h-screen w-full bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
            <span className="text-white text-lg font-bold">☀</span>
          </div>
          <p className="text-gray-600">Loading your Kundli...</p>
        </div>
      </div>
    );
  }

  if (error === 'PROFILE_INCOMPLETE') {
    return (
      <div className="h-screen w-full bg-white flex flex-col items-center justify-center px-4">
        <AlertCircle className="w-16 h-16 text-orange-500 mb-4" />
        <h2 className="text-xl font-bold text-gray-900 mb-2">Profile Incomplete</h2>
        <p className="text-gray-600 text-center mb-6">
          Complete your profile with birth details to view your Kundli chart.
        </p>
        <button
          onClick={() => fetchKundli()}
          className="px-6 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen w-full bg-white flex flex-col items-center justify-center px-4">
        <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-xl font-bold text-gray-900 mb-2">Unable to Load Kundli</h2>
        <p className="text-gray-600 text-center mb-6">
          There was an issue loading your Kundli chart. Please try again.
        </p>
        <button
          onClick={() => fetchKundli()}
          className="px-6 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!kundliData) {
    return (
      <div className="h-screen w-full bg-white flex items-center justify-center">
        <p className="text-gray-600">No Kundli data available</p>
      </div>
    );
  }

  const { svg, profile, structured, source } = kundliData;
  const safeHtml = getSafeHtml(svg);
  const currentStyle = source?.style || chartStyle;

  return (
    <div className="h-screen w-full bg-white overflow-y-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white p-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Your Kundli</h1>
            <p className="text-sm text-emerald-100 mt-1">
              {profile.name} • {profile.dob}
            </p>
          </div>
          <button
            onClick={() => fetchKundli()}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
            title="Refresh chart"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 max-w-4xl mx-auto">
        
        {/* Chart Style Toggle */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-700">Chart Style</h3>
          </div>
          <div className="flex gap-2">
            {Object.values(CHART_STYLES).map((style) => (
              <button
                key={style.id}
                onClick={() => handleStyleChange(style.id)}
                className={`flex-1 py-3 px-4 rounded-lg border-2 transition-all ${
                  currentStyle === style.id
                    ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                    : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                }`}
              >
                <div className="font-semibold text-sm">{style.label}</div>
                <div className="text-xs opacity-70 mt-1">{style.description}</div>
              </button>
            ))}
          </div>
        </div>
        
        {/* SVG Chart Container */}
        <div className="mb-8 bg-gray-50 rounded-lg border border-gray-200 p-4 overflow-x-auto">
          <div className="min-h-[400px] flex items-center justify-center">
            <div
              className="w-full max-w-lg"
              dangerouslySetInnerHTML={{ __html: safeHtml }}
              style={{
                maxWidth: '100%',
                height: 'auto',
              }}
            />
          </div>
        </div>

        {/* Chart Style Info */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-6">
          <p className="text-sm text-amber-800">
            <strong>{CHART_STYLES[currentStyle]?.label}:</strong>{' '}
            {currentStyle === 'north' 
              ? 'Houses are fixed diamond positions. The sign numbers (1-12) shown indicate which zodiac sign occupies each house based on your ascendant.'
              : 'Signs are fixed square positions. House numbers (H1-H12) are shown based on your ascendant sign. Planets are placed by their zodiac sign.'}
          </p>
        </div>

        {/* Profile Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-blue-900 mb-2">Birth Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-blue-700 font-medium">Date of Birth</p>
              <p className="text-blue-900">{profile.dob}</p>
            </div>
            <div>
              <p className="text-blue-700 font-medium">Time of Birth</p>
              <p className="text-blue-900">{profile.tob}</p>
            </div>
            <div className="col-span-2">
              <p className="text-blue-700 font-medium">Place of Birth</p>
              <p className="text-blue-900">{profile.location}</p>
            </div>
          </div>
        </div>

        {/* Ascendant */}
        <div className="bg-white border border-gray-200 rounded-lg mb-4 overflow-hidden">
          <button
            onClick={() => toggleSection('ascendant')}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <h3 className="font-semibold text-gray-900">Ascendant (Lagna)</h3>
            {expandedSections.ascendant ? (
              <ChevronUp className="w-5 h-5 text-emerald-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          {expandedSections.ascendant && (
            <div className="px-4 pb-4 border-t border-gray-200">
              {structured.ascendant ? (
                <div className="grid grid-cols-3 gap-4 pt-3">
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold">Sign</p>
                    <p className="text-lg font-bold text-emerald-600">
                      {structured.ascendant.sign || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold">Degree</p>
                    <p className="text-lg font-bold text-emerald-600">
                      {(structured.ascendant.degree || 0).toFixed(1)}°
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold">House</p>
                    <p className="text-lg font-bold text-emerald-600">
                      {structured.ascendant.house || 1}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 pt-3">No ascendant data available</p>
              )}
            </div>
          )}
        </div>

        {/* Houses */}
        <div className="bg-white border border-gray-200 rounded-lg mb-4 overflow-hidden">
          <button
            onClick={() => toggleSection('houses')}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <h3 className="font-semibold text-gray-900">Houses (12)</h3>
            {expandedSections.houses ? (
              <ChevronUp className="w-5 h-5 text-emerald-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          {expandedSections.houses && (
            <div className="px-4 pb-4 border-t border-gray-200">
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 pt-3">
                {structured.houses && structured.houses.map((house, idx) => (
                  <div key={idx} className="bg-gray-50 rounded-lg p-3 text-center">
                    <p className="text-xs text-gray-500 font-semibold">House {house.house}</p>
                    <p className="text-sm font-bold text-gray-900 mt-1">
                      {house.sign || 'N/A'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Sign #{house.sign_num || idx + 1}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Planets */}
        <div className="bg-white border border-gray-200 rounded-lg mb-8 overflow-hidden">
          <button
            onClick={() => toggleSection('planets')}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <h3 className="font-semibold text-gray-900">Planets (9)</h3>
            {expandedSections.planets ? (
              <ChevronUp className="w-5 h-5 text-emerald-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>
          {expandedSections.planets && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-t border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">Planet</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">Sign</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">Degree</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">House</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700">Retro</th>
                  </tr>
                </thead>
                <tbody>
                  {structured.planets && structured.planets.length > 0 ? (
                    structured.planets.map((planet, idx) => (
                      <tr key={idx} className="border-t border-gray-100 hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium text-gray-900">
                          {planet.full_name || getPlanetFullName(planet.name) || 'Unknown'}
                          <span className="text-xs text-gray-400 ml-1">({planet.name})</span>
                        </td>
                        <td className="px-4 py-3 text-gray-700">
                          {planet.sign || 'N/A'}
                        </td>
                        <td className="px-4 py-3 text-gray-700">
                          {(planet.degree || 0).toFixed(1)}°
                        </td>
                        <td className="px-4 py-3 text-gray-700">
                          {planet.house || '-'}
                        </td>
                        <td className="px-4 py-3 text-gray-700">
                          {planet.retrograde ? (
                            <span className="text-red-600 font-medium">R</span>
                          ) : '-'}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="px-4 py-3 text-center text-gray-500">
                        No planet data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Source Info */}
        <div className="text-xs text-gray-500 text-center pb-4">
          <p>
            Chart Type: {source?.chart_type || 'birth_chart'} • 
            Style: {CHART_STYLES[currentStyle]?.label || 'North Indian'} • 
            Vendor: {source?.vendor || 'VedicAstroAPI'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default KundliScreen;
