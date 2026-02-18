import React, { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../../../config';
import DOMPurify from 'dompurify';
import BirthDetailsModal from './BirthDetailsModal';
import { colors, shadows } from './theme';
import ResponsiveHeader from './ResponsiveHeader';

// Teal gradient background (same as login screen)
const TEAL_GRADIENT = `linear-gradient(180deg, ${colors.teal.primary} 0%, ${colors.teal.soft} 100%)`;

// Chart style options
const CHART_STYLES = {
  north: {
    id: 'north',
    label: 'North Indian',
    description: 'Diamond layout'
  },
  south: {
    id: 'south', 
    label: 'South Indian',
    description: 'Square layout'
  }
};

/**
 * KundliScreenSimplified V2 - Kundli view with ResponsiveHeader
 * Shows for both new and returning users
 * If birth details missing, shows collection modal
 */
const KundliScreenSimplified = ({ token, userId, hasBottomNav, onNavigate, onTabChange }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [kundliData, setKundliData] = useState(null);
  const [chartStyle, setChartStyle] = useState(() => {
    return localStorage.getItem('kundli_chart_style') || 'north';
  });
  const [expandedSections, setExpandedSections] = useState({
    ascendant: true,
    houses: false,
    planets: false
  });
  const [showBirthModal, setShowBirthModal] = useState(false);

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

        const data = await response.json();

        if (response.ok && data.ok) {
          setKundliData(data);
          setLoading(false);
          return;
        }

        if (data.error === 'PROFILE_INCOMPLETE' && attempt < retries) {
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
  }, [token]);

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

  const handleBirthDetailsComplete = () => {
    setShowBirthModal(false);
    fetchKundli();
  };

  // Sanitize SVG before rendering
  const getSafeHtml = (svgString) => {
    const clean = DOMPurify.sanitize(svgString, {
      ALLOWED_TAGS: ['svg', 'g', 'path', 'circle', 'rect', 'text', 'line', 'polygon', 'polyline', 'defs', 'style', 'tspan', 'image', 'linearGradient', 'radialGradient', 'stop', 'pattern', 'clipPath', 'mask', 'use', 'symbol', 'marker', 'filter', 'feGaussianBlur', 'feOffset', 'feMerge', 'feMergeNode'],
      ALLOWED_ATTR: ['id', 'class', 'style', 'cx', 'cy', 'r', 'x', 'y', 'x1', 'y1', 'x2', 'y2', 'width', 'height', 'fill', 'stroke', 'stroke-width', 'viewBox', 'd', 'transform', 'points', 'href', 'font-size', 'text-anchor', 'dominant-baseline', 'data-name', 'rx', 'ry', 'xmlns', 'version', 'offset', 'stop-color', 'stop-opacity', 'opacity', 'font-family', 'font-weight', 'font-style', 'patternUnits', 'gradientUnits', 'spreadMethod', 'xlink:href', 'clip-path', 'mask', 'filter', 'stdDeviation', 'dx', 'dy', 'result', 'in', 'in2', 'scale']
    });
    return clean;
  };

  const getPlanetFullName = (abbr) => {
    const names = {
      'Su': 'Sun', 'Mo': 'Moon', 'Ma': 'Mars', 'Me': 'Mercury',
      'Ju': 'Jupiter', 'Ve': 'Venus', 'Sa': 'Saturn', 'Ra': 'Rahu', 'Ke': 'Ketu'
    };
    return names[abbr] || abbr;
  };

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${hasBottomNav ? 'pb-20' : ''}`} style={{ background: TEAL_GRADIENT }}>
        <div className="text-center">
          <div 
            className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
            style={{ backgroundColor: 'rgba(255,255,255,0.9)' }}
          >
            <span className="text-2xl animate-pulse">🌟</span>
          </div>
          <p style={{ color: 'white' }}>Loading your Kundli...</p>
        </div>
      </div>
    );
  }

  // Profile incomplete - show birth details collection modal
  if (error === 'PROFILE_INCOMPLETE') {
    return (
      <div className={`min-h-screen flex flex-col items-center justify-center px-6 ${hasBottomNav ? 'pb-20' : ''}`} style={{ background: TEAL_GRADIENT }}>
        <div 
          className="w-24 h-24 rounded-full flex items-center justify-center mb-6"
          style={{ backgroundColor: 'rgba(255,255,255,0.9)' }}
        >
          <span className="text-4xl">🌟</span>
        </div>
        <h2 className="text-2xl font-bold mb-2 text-center" style={{ color: 'white' }}>Your Kundli Awaits</h2>
        <p className="text-center mb-6 max-w-xs" style={{ color: 'rgba(255,255,255,0.85)' }}>
          Complete your birth details to unlock your personalized Kundli chart and astrological insights.
        </p>
        <button
          onClick={() => setShowBirthModal(true)}
          className="px-8 py-4 rounded-xl font-semibold text-lg transition-all shadow-lg hover:shadow-xl"
          style={{ backgroundColor: 'white', color: '#3E827A' }}
        >
          Add Birth Details
        </button>
        
        {/* Birth Details Modal */}
        <BirthDetailsModal
          token={token}
          isOpen={showBirthModal}
          onClose={() => setShowBirthModal(false)}
          onComplete={handleBirthDetailsComplete}
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen flex flex-col items-center justify-center px-6 ${hasBottomNav ? 'pb-20' : ''}`} style={{ background: TEAL_GRADIENT }}>
        <div 
          className="w-20 h-20 rounded-full flex items-center justify-center mb-6"
          style={{ backgroundColor: 'rgba(255,255,255,0.9)' }}
        >
          <span className="text-4xl">⚠️</span>
        </div>
        <h2 className="text-xl font-bold mb-2" style={{ color: 'white' }}>Unable to Load Kundli</h2>
        <p className="text-center mb-6 max-w-xs" style={{ color: 'rgba(255,255,255,0.85)' }}>
          The astrology service is temporarily unavailable. Please try again in a few minutes.
        </p>
        <button
          onClick={() => fetchKundli()}
          className="px-6 py-3 rounded-xl font-medium transition-all"
          style={{ backgroundColor: 'white', color: '#3E827A' }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!kundliData) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${hasBottomNav ? 'pb-20 md:pb-0' : ''}`} style={{ background: TEAL_GRADIENT }}>
        <p style={{ color: 'rgba(255,255,255,0.85)' }}>No Kundli data available</p>
      </div>
    );
  }

  const { svg, profile, structured, source } = kundliData;
  const safeHtml = getSafeHtml(svg);
  const currentStyle = source?.style || chartStyle;

  return (
    <div className={`min-h-screen ${hasBottomNav ? 'pb-20 md:pb-0' : ''}`} style={{ backgroundColor: colors.background.primary }}>
      {/* Responsive Header */}
      <ResponsiveHeader
        title="Your Kundli"
        showBackButton={false}
        onNavigate={onNavigate}
        onTabChange={onTabChange}
      />

      {/* Hero Section */}
      <div 
        className="px-6 md:px-8 pt-4 pb-6"
        style={{ background: `linear-gradient(135deg, ${colors.teal.primary} 0%, ${colors.teal.dark} 100%)` }}
      >
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-white">Your Kundli</h1>
            <p className="text-sm md:text-base mt-1 text-white/80">
              {profile?.name} • {profile?.dob}
            </p>
          </div>
          <button
            onClick={() => fetchKundli()}
            className="w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center transition-all hover:bg-white/30"
            style={{ backgroundColor: 'rgba(255,255,255,0.2)' }}
            title="Refresh chart"
            data-testid="refresh-kundli-btn"
          >
            <span className="text-lg md:text-xl">🔄</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 md:p-8 max-w-4xl mx-auto">
        
        {/* Chart Style Toggle */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold mb-2" style={{ color: '#5c5c5c' }}>Chart Style</h3>
          <div className="flex gap-2">
            {Object.values(CHART_STYLES).map((style) => (
              <button
                key={style.id}
                onClick={() => handleStyleChange(style.id)}
                className="flex-1 py-3 px-4 rounded-xl border-2 transition-all"
                style={{
                  backgroundColor: currentStyle === style.id ? 'rgba(215,184,112,0.15)' : 'white',
                  borderColor: currentStyle === style.id ? '#d7b870' : '#e5d188',
                  color: currentStyle === style.id ? '#5c5c5c' : '#9a8a6a'
                }}
              >
                <div className="font-semibold text-sm">{style.label}</div>
                <div className="text-xs opacity-70 mt-1">{style.description}</div>
              </button>
            ))}
          </div>
        </div>
        
        {/* SVG Chart Container */}
        <div 
          className="mb-6 rounded-2xl p-4 overflow-x-auto"
          style={{ backgroundColor: 'white', border: '1px solid #e5d188' }}
        >
          <div className="min-h-[350px] flex items-center justify-center">
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
        <div 
          className="rounded-xl p-3 mb-6"
          style={{ backgroundColor: 'rgba(215,184,112,0.15)', border: '1px solid rgba(215,184,112,0.3)' }}
        >
          <p className="text-sm" style={{ color: '#7a6a4a' }}>
            <strong style={{ color: '#5c5c5c' }}>{CHART_STYLES[currentStyle]?.label}:</strong>{' '}
            {currentStyle === 'north' 
              ? 'Houses are fixed diamond positions. Sign numbers indicate zodiac positions.'
              : 'Signs are fixed square positions. House numbers shown based on ascendant.'}
          </p>
        </div>

        {/* Profile Info */}
        <div 
          className="rounded-xl p-4 mb-4"
          style={{ backgroundColor: 'white', border: '1px solid #e5d188' }}
        >
          <h3 className="font-semibold mb-3" style={{ color: '#5c5c5c' }}>Birth Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="font-medium" style={{ color: '#d7b870' }}>Date of Birth</p>
              <p style={{ color: '#5c5c5c' }}>{profile?.dob}</p>
            </div>
            <div>
              <p className="font-medium" style={{ color: '#d7b870' }}>Time of Birth</p>
              <p style={{ color: '#5c5c5c' }}>{profile?.tob}</p>
            </div>
            <div className="col-span-2">
              <p className="font-medium" style={{ color: '#d7b870' }}>Place of Birth</p>
              <p style={{ color: '#5c5c5c' }}>{profile?.location}</p>
            </div>
          </div>
        </div>

        {/* Ascendant */}
        <div 
          className="rounded-xl mb-4 overflow-hidden"
          style={{ backgroundColor: 'white', border: '1px solid #e5d188' }}
        >
          <button
            onClick={() => toggleSection('ascendant')}
            className="w-full flex items-center justify-between p-4 transition-colors"
            style={{ backgroundColor: expandedSections.ascendant ? 'rgba(215,184,112,0.1)' : 'white' }}
          >
            <h3 className="font-semibold" style={{ color: '#5c5c5c' }}>Ascendant (Lagna)</h3>
            <span style={{ color: '#d7b870' }}>{expandedSections.ascendant ? '▲' : '▼'}</span>
          </button>
          {expandedSections.ascendant && (
            <div className="px-4 pb-4 border-t" style={{ borderColor: '#e5d188' }}>
              {structured?.ascendant ? (
                <div className="grid grid-cols-3 gap-4 pt-3">
                  <div className="text-center">
                    <p className="text-xs uppercase font-semibold" style={{ color: '#9a8a6a' }}>Sign</p>
                    <p className="text-lg font-bold" style={{ color: '#d7b870' }}>
                      {structured.ascendant.sign || 'N/A'}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs uppercase font-semibold" style={{ color: '#9a8a6a' }}>Degree</p>
                    <p className="text-lg font-bold" style={{ color: '#d7b870' }}>
                      {(structured.ascendant.degree || 0).toFixed(1)}°
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs uppercase font-semibold" style={{ color: '#9a8a6a' }}>House</p>
                    <p className="text-lg font-bold" style={{ color: '#d7b870' }}>
                      {structured.ascendant.house || 1}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="pt-3" style={{ color: '#9a8a6a' }}>No ascendant data available</p>
              )}
            </div>
          )}
        </div>

        {/* Houses */}
        <div 
          className="rounded-xl mb-4 overflow-hidden"
          style={{ backgroundColor: 'white', border: '1px solid #e5d188' }}
        >
          <button
            onClick={() => toggleSection('houses')}
            className="w-full flex items-center justify-between p-4 transition-colors"
            style={{ backgroundColor: expandedSections.houses ? 'rgba(215,184,112,0.1)' : 'white' }}
          >
            <h3 className="font-semibold" style={{ color: '#5c5c5c' }}>Houses (12)</h3>
            <span style={{ color: '#d7b870' }}>{expandedSections.houses ? '▲' : '▼'}</span>
          </button>
          {expandedSections.houses && (
            <div className="px-4 pb-4 border-t" style={{ borderColor: '#e5d188' }}>
              <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 pt-3">
                {structured?.houses?.map((house, idx) => (
                  <div 
                    key={idx} 
                    className="rounded-lg p-2 text-center"
                    style={{ backgroundColor: 'rgba(215,184,112,0.1)' }}
                  >
                    <p className="text-xs font-semibold" style={{ color: '#9a8a6a' }}>House {house.house}</p>
                    <p className="text-sm font-bold mt-1" style={{ color: '#5c5c5c' }}>
                      {house.sign || 'N/A'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Planets */}
        <div 
          className="rounded-xl mb-6 overflow-hidden"
          style={{ backgroundColor: 'white', border: '1px solid #e5d188' }}
        >
          <button
            onClick={() => toggleSection('planets')}
            className="w-full flex items-center justify-between p-4 transition-colors"
            style={{ backgroundColor: expandedSections.planets ? 'rgba(215,184,112,0.1)' : 'white' }}
          >
            <h3 className="font-semibold" style={{ color: '#5c5c5c' }}>Planets (9)</h3>
            <span style={{ color: '#d7b870' }}>{expandedSections.planets ? '▲' : '▼'}</span>
          </button>
          {expandedSections.planets && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead style={{ backgroundColor: 'rgba(215,184,112,0.1)' }}>
                  <tr>
                    <th className="px-3 py-2 text-left font-semibold" style={{ color: '#5c5c5c' }}>Planet</th>
                    <th className="px-3 py-2 text-left font-semibold" style={{ color: '#5c5c5c' }}>Sign</th>
                    <th className="px-3 py-2 text-left font-semibold" style={{ color: '#5c5c5c' }}>Degree</th>
                    <th className="px-3 py-2 text-left font-semibold" style={{ color: '#5c5c5c' }}>House</th>
                    <th className="px-3 py-2 text-left font-semibold" style={{ color: '#5c5c5c' }}>R</th>
                  </tr>
                </thead>
                <tbody>
                  {structured?.planets?.length > 0 ? (
                    structured.planets.map((planet, idx) => (
                      <tr key={idx} className="border-t" style={{ borderColor: '#e5d188' }}>
                        <td className="px-3 py-2 font-medium" style={{ color: '#5c5c5c' }}>
                          {planet.full_name || getPlanetFullName(planet.name) || 'Unknown'}
                        </td>
                        <td className="px-3 py-2" style={{ color: '#7a6a4a' }}>
                          {planet.sign || 'N/A'}
                        </td>
                        <td className="px-3 py-2" style={{ color: '#7a6a4a' }}>
                          {(planet.degree || 0).toFixed(1)}°
                        </td>
                        <td className="px-3 py-2" style={{ color: '#7a6a4a' }}>
                          {planet.house || '-'}
                        </td>
                        <td className="px-3 py-2">
                          {planet.retrograde ? (
                            <span className="font-medium" style={{ color: '#c9a85a' }}>R</span>
                          ) : '-'}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="px-3 py-3 text-center" style={{ color: '#9a8a6a' }}>
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
        <div className="text-xs text-center pb-4" style={{ color: '#9a8a6a' }}>
          <p>
            Chart: {source?.chart_type || 'birth_chart'} • 
            Style: {CHART_STYLES[currentStyle]?.label || 'North Indian'} • 
            Source: {source?.vendor || 'VedicAstroAPI'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default KundliScreenSimplified;
