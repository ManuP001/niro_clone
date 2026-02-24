import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiSimplified, formatPrice, trackEvent } from './utils';
import { colors, shadows } from './theme';

/**
 * ExpertPackagesPage - Full-page package listing for a specific expert
 * Route: /app/expert/:expertId/packages
 */
export default function ExpertPackagesPage({ token, onNavigate }) {
  const { expertId } = useParams();
  const navigate = useNavigate();
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expertName, setExpertName] = useState('');

  useEffect(() => {
    if (!expertId) return;
    const fetchPackages = async () => {
      try {
        const res = await apiSimplified.get(`/experts/${expertId}/packages`, token);
        setPackages(res.packages || []);
        // Try to get expert name from expert list
        const expertsRes = await apiSimplified.get('/experts/all', token);
        const found = expertsRes.experts?.find((e) => e.expert_id === expertId);
        if (found) setExpertName(found.name);
        trackEvent('expert_packages_viewed', { expert_id: expertId }, token);
      } catch {
        setPackages([]);
      } finally {
        setLoading(false);
      }
    };
    fetchPackages();
  }, [expertId, token]);

  const handleGetPack = (pkg) => {
    if (onNavigate) {
      onNavigate('packageLanding', { packageId: pkg.tier_id });
    } else {
      navigate(`/app/package/${pkg.tier_id}`);
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.background.primary }}>
      {/* Header */}
      <header
        className="sticky top-0 z-40 px-4 py-4 flex items-center gap-4"
        style={{ backgroundColor: colors.background.primary }}
      >
        <button
          onClick={() => navigate(-1)}
          className="w-10 h-10 rounded-full flex items-center justify-center transition-all hover:bg-gray-100"
          style={{ backgroundColor: '#FFFFFF', boxShadow: shadows.card }}
        >
          <svg className="w-5 h-5" style={{ color: colors.text.dark }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div>
          <h1 className="text-lg font-semibold" style={{ color: colors.text.dark }}>
            Packages
          </h1>
          {expertName && (
            <p className="text-sm" style={{ color: colors.teal.primary }}>with {expertName}</p>
          )}
        </div>
      </header>

      {/* Content */}
      <div className="px-4 py-2 max-w-lg mx-auto">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div
              className="w-8 h-8 border-4 rounded-full animate-spin"
              style={{ borderColor: `${colors.teal.primary}30`, borderTopColor: colors.teal.primary }}
            />
          </div>
        ) : packages.length === 0 ? (
          <div className="text-center py-16">
            <p style={{ color: colors.text.muted }}>No packages available yet.</p>
          </div>
        ) : (
          <div className="space-y-4 pb-8">
            {packages.map((pkg) => (
              <div
                key={pkg.tier_id}
                className="rounded-2xl overflow-hidden"
                style={{ backgroundColor: '#FFFFFF', boxShadow: shadows.card }}
              >
                {/* Card header */}
                <div
                  className="px-5 py-4"
                  style={{ background: `linear-gradient(135deg, ${colors.teal.primary} 0%, ${colors.teal.dark || '#2d6b63'} 100%)` }}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-lg text-white">{pkg.name}</h3>
                      {pkg.popular && (
                        <span
                          className="text-xs px-2 py-0.5 rounded-full font-medium"
                          style={{ backgroundColor: colors.peach.primary, color: colors.text.dark }}
                        >
                          Most Popular
                        </span>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-white">{formatPrice(pkg.price_inr)}</p>
                      {pkg.duration_days && (
                        <p className="text-xs text-white/70">{pkg.duration_days} days</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Card body */}
                <div className="px-5 py-4">
                  {pkg.description && (
                    <p className="text-sm mb-3" style={{ color: colors.text.secondary }}>
                      {pkg.description}
                    </p>
                  )}

                  {/* Features */}
                  {pkg.features?.length > 0 && (
                    <ul className="space-y-2 mb-4">
                      {pkg.features.map((feature, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <svg
                            className="w-4 h-4 mt-0.5 flex-shrink-0"
                            style={{ color: colors.teal.primary }}
                            fill="none" stroke="currentColor" viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span className="text-sm" style={{ color: colors.text.dark }}>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  )}

                  {/* Meta row */}
                  <div className="flex gap-4 mb-4">
                    {pkg.calls_included > 0 && (
                      <div className="flex items-center gap-1">
                        <svg className="w-4 h-4" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                        </svg>
                        <span className="text-xs" style={{ color: colors.text.muted }}>
                          {pkg.calls_included} call{pkg.calls_included > 1 ? 's' : ''}
                        </span>
                      </div>
                    )}
                    {pkg.duration_days && (
                      <div className="flex items-center gap-1">
                        <svg className="w-4 h-4" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span className="text-xs" style={{ color: colors.text.muted }}>
                          {pkg.duration_days} days
                        </span>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => handleGetPack(pkg)}
                    className="w-full py-3 rounded-xl font-semibold text-sm transition-all hover:shadow-md active:scale-[0.98]"
                    style={{ backgroundColor: colors.teal.primary, color: '#FFFFFF' }}
                  >
                    Get this pack
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
