import React, { useState, useEffect } from 'react';
import { apiV2, TOPICS, formatPrice, getBranchLabel } from './utils';

/**
 * RecommendationsScreen - Shows personalized package recommendations
 * 
 * Displays:
 * - Situation summary (what we understood)
 * - Chart insights (trust step)
 * - Primary recommendation
 * - Alternative options
 */
export default function RecommendationsScreen({ 
  token, 
  intakeId, 
  intakeData,
  onSelectPackage,
  onBack 
}) {
  const [loading, setLoading] = useState(true);
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState(null);
  const [showTrustStep, setShowTrustStep] = useState(true);

  useEffect(() => {
    generateRecommendation();
  }, [intakeId]);

  const generateRecommendation = async () => {
    setLoading(true);
    try {
      const response = await apiV2.post('/recommendations/generate', {
        intake_id: intakeId,
        topic: intakeData?.topic,
        urgency: intakeData?.urgency,
        desired_outcome: intakeData?.desired_outcome,
        decision_ownership: intakeData?.decision_ownership,
        key_concerns: [],
        wants_consultation: true,
      }, token);

      if (response.ok) {
        setRecommendation(response);
      } else {
        setError('Failed to generate recommendations');
      }
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-emerald-200 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Analyzing your situation...</p>
          <p className="text-slate-400 text-sm mt-1">Finding the best solutions for you</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="text-center">
          <div className="text-4xl mb-4">😔</div>
          <h2 className="text-xl font-semibold text-slate-800 mb-2">Something went wrong</h2>
          <p className="text-slate-500 mb-6">{error}</p>
          <button
            onClick={generateRecommendation}
            className="bg-emerald-500 text-white px-6 py-3 rounded-xl font-medium"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Trust Step (first view)
  if (showTrustStep) {
    return (
      <div className="min-h-screen bg-white">
        {/* Header */}
        <div className="px-6 pt-12 pb-6">
          <button 
            onClick={onBack}
            className="text-slate-500 mb-4 flex items-center"
          >
            <span className="mr-2">←</span> Back
          </button>
          <h1 className="text-2xl font-semibold text-slate-900">Your Situation</h1>
        </div>

        <div className="px-6 space-y-6 pb-32">
          {/* Situation Summary */}
          <div className="bg-slate-50 rounded-2xl p-5">
            <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-3">
              Here's what I understood
            </h3>
            <p className="text-slate-800 leading-relaxed">
              {recommendation?.situation_summary || 'Analyzing your situation...'}
            </p>
            <div className="flex flex-wrap gap-2 mt-4">
              <span className="bg-white px-3 py-1 rounded-full text-sm text-slate-600 border border-slate-200">
                {TOPICS[intakeData?.topic]?.label || 'General'}
              </span>
              <span className="bg-white px-3 py-1 rounded-full text-sm text-slate-600 border border-slate-200">
                Urgency: {intakeData?.urgency || 'Medium'}
              </span>
            </div>
          </div>

          {/* Chart Insights */}
          {recommendation?.chart_insights?.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wide mb-3">
                From Your Chart
              </h3>
              <div className="space-y-3">
                {recommendation.chart_insights.map((insight, idx) => (
                  <div key={idx} className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-100 rounded-xl p-4">
                    <div className="flex items-start">
                      <span className="text-amber-500 mr-3">🪐</span>
                      <div>
                        <p className="text-slate-800 font-medium">{insight.insight}</p>
                        <p className="text-slate-600 text-sm mt-1">{insight.relevance}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Why This Solution Fits */}
          <div className="bg-emerald-50 border border-emerald-100 rounded-2xl p-5">
            <h3 className="text-sm font-medium text-emerald-700 uppercase tracking-wide mb-3">
              Why this solution fits
            </h3>
            <p className="text-slate-700 leading-relaxed">
              {recommendation?.reasoning || 'Based on your situation and goals, we have personalized recommendations for you.'}
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-100 p-4">
          <button
            onClick={() => setShowTrustStep(false)}
            className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold py-4 rounded-xl hover:shadow-lg transition-all"
          >
            See My Recommendations
          </button>
        </div>
      </div>
    );
  }

  // Recommendations List
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white px-6 pt-12 pb-6 border-b border-slate-100">
        <button 
          onClick={() => setShowTrustStep(true)}
          className="text-slate-500 mb-4 flex items-center"
        >
          <span className="mr-2">←</span> Back
        </button>
        <h1 className="text-2xl font-semibold text-slate-900">Recommended for You</h1>
      </div>

      <div className="p-6 space-y-4 pb-24">
        {/* Primary Package */}
        {recommendation?.primary_package && (
          <div>
            <p className="text-sm font-medium text-emerald-600 mb-2 uppercase tracking-wide">Best Fit for You</p>
            <PackageCard 
              package_={recommendation.primary_package}
              isPrimary={true}
              onClick={() => onSelectPackage(recommendation.primary_package.package_id, recommendation.recommendation_id)}
            />
          </div>
        )}

        {/* Alternative Packages */}
        {recommendation?.alternative_packages?.length > 0 && (
          <div>
            <p className="text-sm font-medium text-slate-500 mb-2 uppercase tracking-wide mt-6">Also Consider</p>
            {recommendation.alternative_packages.map((pkg, idx) => (
              <PackageCard 
                key={pkg.package_id}
                package_={pkg}
                isPrimary={false}
                onClick={() => onSelectPackage(pkg.package_id, recommendation.recommendation_id)}
              />
            ))}
          </div>
        )}

        {/* Save for Later */}
        <button className="w-full text-center text-slate-500 py-3 text-sm">
          💾 Save for later
        </button>
      </div>
    </div>
  );
}

// Package Card Component
function PackageCard({ package_, isPrimary, onClick }) {
  return (
    <div 
      onClick={onClick}
      className={`bg-white rounded-2xl p-5 cursor-pointer transition-all hover:shadow-lg ${
        isPrimary ? 'border-2 border-emerald-200 shadow-md' : 'border border-slate-200'
      }`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          {isPrimary && (
            <span className="text-emerald-600 text-xs font-medium mb-1 flex items-center">
              ⭐ Recommended
            </span>
          )}
          <h3 className="text-lg font-semibold text-slate-800">{package_.name}</h3>
          <p className="text-slate-500 text-sm mt-1">{package_.tagline}</p>
        </div>
      </div>

      {/* Features */}
      <div className="flex flex-wrap gap-2 mb-4">
        {package_.self_guided_items?.length > 0 && (
          <span className="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded-full">
            ✓ Self-guided practices
          </span>
        )}
        {package_.includes_consultation && (
          <span className="bg-emerald-100 text-emerald-700 text-xs px-2 py-1 rounded-full">
            ✓ Unlimited consultation
          </span>
        )}
        {package_.additional_services?.length > 0 && (
          <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full">
            ✓ {package_.additional_services.length} extra services
          </span>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-100">
        <div>
          <span className="text-slate-400 text-sm">{package_.duration_weeks} weeks</span>
          <span className="text-slate-300 mx-2">•</span>
          <span className="text-slate-400 text-sm">{package_.daily_commitment_minutes} min/day</span>
        </div>
        <div className="flex items-center">
          <span className="text-xl font-bold text-slate-800">{formatPrice(package_.price_inr)}</span>
          <span className="text-slate-400 ml-2">→</span>
        </div>
      </div>
    </div>
  );
}
