import React, { useState, useEffect } from 'react';
import { apiV2, formatPrice, getRemedyCategoryIcon, getRemedyCategoryLabel } from './utils';

/**
 * PackageLandingScreen - Detailed package page with 4 sections
 * 
 * Sections:
 * 3a) Self-guided solutions
 * 3b) Consultation policy (if included)
 * 3c) Additional services
 * 3d) Remedy add-ons (optional, charged extra)
 */
export default function PackageLandingScreen({ 
  token, 
  packageId,
  recommendationId,
  onCheckout,
  onBack 
}) {
  const [loading, setLoading] = useState(true);
  const [package_, setPackage] = useState(null);
  const [selectedRemedies, setSelectedRemedies] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPackage();
  }, [packageId]);

  const loadPackage = async () => {
    try {
      const response = await apiV2.get(`/catalog/packages/${packageId}`, token);
      if (response.ok) {
        setPackage(response.package);
      } else {
        setError('Package not found');
      }
    } catch (err) {
      setError('Failed to load package');
    } finally {
      setLoading(false);
    }
  };

  const toggleRemedy = (remedyId) => {
    setSelectedRemedies(prev => 
      prev.includes(remedyId) 
        ? prev.filter(id => id !== remedyId)
        : [...prev, remedyId]
    );
  };

  const calculateTotal = () => {
    let total = package_?.price_inr || 0;
    selectedRemedies.forEach(remedyId => {
      const remedy = package_?.suggested_remedies?.find(r => r.remedy_id === remedyId);
      if (remedy) {
        total += remedy.price_inr;
      }
    });
    return total;
  };

  const handleCheckout = () => {
    onCheckout(packageId, selectedRemedies, recommendationId);
  };

  // Loading
  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-emerald-200 border-t-emerald-500 rounded-full animate-spin" />
      </div>
    );
  }

  // Error
  if (error || !package_) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="text-center">
          <p className="text-slate-600">{error || 'Package not found'}</p>
          <button onClick={onBack} className="text-emerald-600 mt-4">Go Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 pb-40">
      {/* Header */}
      <div className="bg-gradient-to-br from-emerald-500 to-teal-600 text-white">
        <div className="px-6 pt-12 pb-8">
          <button 
            onClick={onBack}
            className="text-emerald-100 mb-4 flex items-center"
          >
            <span className="mr-2">←</span> Back
          </button>
          
          <h1 className="text-2xl font-bold">{package_.name}</h1>
          <p className="text-emerald-100 mt-2">{package_.tagline}</p>
          
          <div className="flex items-center mt-4 text-emerald-100 text-sm">
            <span>{package_.duration_weeks} weeks</span>
            <span className="mx-2">•</span>
            <span>{package_.daily_commitment_minutes} min/day</span>
          </div>
          
          <div className="mt-4">
            <span className="text-3xl font-bold">{formatPrice(package_.price_inr)}</span>
          </div>
        </div>
      </div>

      {/* Sections */}
      <div className="px-6 -mt-4">
        
        {/* Section 3a: Self-Guided Solutions */}
        <Section 
          title="Self-Guided Solutions" 
          subtitle="Tools and practices to help you navigate this on your own"
          icon="🎯"
        >
          <div className="space-y-3">
            {package_.self_guided_items?.map((item, idx) => (
              <div key={idx} className="flex items-start">
                <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
                  <span className="text-emerald-600 text-sm">✓</span>
                </div>
                <div>
                  <p className="font-medium text-slate-800">{item.name}</p>
                  <p className="text-slate-500 text-sm">{item.description}</p>
                  <p className="text-slate-400 text-xs mt-1">{item.duration_minutes} min • {item.content_type}</p>
                </div>
              </div>
            ))}
          </div>
        </Section>

        {/* Section 3b: Consultation Policy */}
        {package_.includes_consultation && package_.consult_policy && (
          <Section 
            title="Unlimited Consultation" 
            subtitle="Expert guidance throughout your plan"
            icon="💬"
          >
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
                  <span className="text-blue-600">📹</span>
                </div>
                <div>
                  <p className="font-medium text-slate-800">Video Sessions</p>
                  <p className="text-slate-500 text-sm">
                    Up to {package_.consult_policy.live_sessions?.max_minutes_per_session || 60} min each • 
                    Max {package_.consult_policy.live_sessions?.sessions_per_week_limit || 1} per week
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
                  <span className="text-blue-600">💬</span>
                </div>
                <div>
                  <p className="font-medium text-slate-800">Chat Support</p>
                  <p className="text-slate-500 text-sm">
                    Unlimited messages • Response within {package_.consult_policy.chat?.sla_hours || 12} hours
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
                  <span className="text-blue-600">⏱️</span>
                </div>
                <div>
                  <p className="font-medium text-slate-800">Validity</p>
                  <p className="text-slate-500 text-sm">
                    {package_.consult_policy.validity_weeks} weeks • Full access until plan completion
                  </p>
                </div>
              </div>
              
              <div className="bg-blue-50 rounded-xl p-3 mt-2">
                <p className="text-blue-700 text-sm">
                  {package_.consult_policy.fair_use_summary}
                </p>
              </div>
            </div>
          </Section>
        )}

        {/* Section 3c: Additional Services */}
        {package_.additional_services?.length > 0 && (
          <Section 
            title="Additional Services" 
            subtitle="Extra support included in this package"
            icon="🎁"
          >
            <div className="space-y-3">
              {package_.additional_services.map((service, idx) => (
                <div key={idx} className="flex items-start">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
                    <span className="text-purple-600 text-sm">✓</span>
                  </div>
                  <div>
                    <p className="font-medium text-slate-800">{service.name}</p>
                    <p className="text-slate-500 text-sm">{service.description}</p>
                    <p className="text-slate-400 text-xs mt-1">{service.delivery_timeline}</p>
                  </div>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Section 3d: Remedy Add-Ons */}
        {package_.suggested_remedies?.length > 0 && (
          <Section 
            title="Remedy Add-Ons" 
            subtitle="Optional — charged extra"
            icon="✨"
            highlight={true}
          >
            <p className="text-slate-500 text-sm mb-4">
              Enhance your journey with personalized remedies
            </p>
            <div className="space-y-3">
              {package_.suggested_remedies.map((remedy) => (
                <div 
                  key={remedy.remedy_id}
                  onClick={() => toggleRemedy(remedy.remedy_id)}
                  className={`border-2 rounded-xl p-4 cursor-pointer transition-all ${
                    selectedRemedies.includes(remedy.remedy_id)
                      ? 'border-amber-400 bg-amber-50'
                      : 'border-slate-200 hover:border-amber-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start flex-1">
                      <span className="text-xl mr-3">{getRemedyCategoryIcon(remedy.category)}</span>
                      <div>
                        <p className="font-medium text-slate-800">{remedy.name}</p>
                        <p className="text-slate-500 text-sm">{remedy.description}</p>
                        <span className="text-xs text-slate-400 mt-1 inline-block">
                          {getRemedyCategoryLabel(remedy.category)}
                        </span>
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <p className="font-semibold text-slate-800">{formatPrice(remedy.price_inr)}</p>
                      <div className={`w-5 h-5 rounded border-2 mt-2 ml-auto ${
                        selectedRemedies.includes(remedy.remedy_id)
                          ? 'bg-amber-500 border-amber-500'
                          : 'border-slate-300'
                      }`}>
                        {selectedRemedies.includes(remedy.remedy_id) && (
                          <span className="text-white text-xs flex items-center justify-center h-full">✓</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Section>
        )}
      </div>

      {/* Fixed Checkout Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 p-4 shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-sm text-slate-500">Total</p>
            <p className="text-2xl font-bold text-slate-800">{formatPrice(calculateTotal())}</p>
          </div>
          {selectedRemedies.length > 0 && (
            <div className="text-right">
              <p className="text-xs text-slate-400">Package: {formatPrice(package_.price_inr)}</p>
              <p className="text-xs text-amber-600">+ {selectedRemedies.length} remedy add-on(s)</p>
            </div>
          )}
        </div>
        <button
          onClick={handleCheckout}
          className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold py-4 rounded-xl hover:shadow-lg transition-all"
        >
          Get This Package
        </button>
        <p className="text-center text-xs text-slate-400 mt-2">
          🔒 Secure payment • Refund if not started
        </p>
      </div>
    </div>
  );
}

// Section Component
function Section({ title, subtitle, icon, children, highlight }) {
  return (
    <div className={`bg-white rounded-2xl p-5 mt-4 ${
      highlight ? 'border-2 border-amber-200' : 'border border-slate-100'
    }`}>
      <div className="flex items-center mb-4">
        <span className="text-xl mr-2">{icon}</span>
        <div>
          <h3 className="font-semibold text-slate-800">{title}</h3>
          {subtitle && <p className="text-slate-500 text-sm">{subtitle}</p>}
        </div>
      </div>
      {children}
    </div>
  );
}
