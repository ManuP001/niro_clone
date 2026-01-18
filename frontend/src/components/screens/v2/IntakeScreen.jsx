import React, { useState } from 'react';
import { apiV2, TOPICS, URGENCY_LEVELS, DECISION_OWNERSHIP } from './utils';

/**
 * IntakeScreen - Situation intake for NIRO V2
 * 
 * Collects:
 * - Topic (life area)
 * - Urgency level
 * - Desired outcome
 * - Decision ownership
 */
export default function IntakeScreen({ token, initialTopic, onComplete, onBack }) {
  const [step, setStep] = useState(1); // 1: topic, 2: details
  const [formData, setFormData] = useState({
    topic: initialTopic || '',
    urgency: '',
    desired_outcome: '',
    decision_ownership: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTopicSelect = (topic) => {
    setFormData(prev => ({ ...prev, topic }));
    setStep(2);
  };

  const handleSubmit = async () => {
    if (!formData.topic || !formData.urgency || !formData.decision_ownership) {
      setError('Please complete all fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiV2.post('/onboarding/intake', formData, token);
      if (response.ok) {
        onComplete(response.intake_id, formData);
      } else {
        setError('Failed to save intake');
      }
    } catch (err) {
      setError('Failed to save. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Step 1: Topic Selection
  if (step === 1) {
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
          <div className="flex items-center justify-between">
            <div>
              <p className="text-emerald-600 text-sm font-medium">Step 1 of 2</p>
              <h1 className="text-2xl font-semibold text-slate-900 mt-1">What brings you here today?</h1>
            </div>
          </div>
        </div>

        {/* Topic Cards */}
        <div className="px-6 space-y-3">
          {Object.entries(TOPICS).map(([key, topic]) => (
            <button
              key={key}
              onClick={() => handleTopicSelect(key)}
              className={`w-full bg-white border-2 rounded-xl p-4 text-left transition-all ${
                formData.topic === key 
                  ? 'border-emerald-500 bg-emerald-50' 
                  : 'border-slate-200 hover:border-emerald-300'
              }`}
            >
              <div className="flex items-center">
                <span className="text-2xl mr-4">{topic.icon}</span>
                <span className="font-medium text-slate-800">{topic.label}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    );
  }

  // Step 2: Details
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="px-6 pt-12 pb-6">
        <button 
          onClick={() => setStep(1)}
          className="text-slate-500 mb-4 flex items-center"
        >
          <span className="mr-2">←</span> Back
        </button>
        <div>
          <p className="text-emerald-600 text-sm font-medium">Step 2 of 2</p>
          <h1 className="text-2xl font-semibold text-slate-900 mt-1">Tell us more</h1>
          <p className="text-slate-500 mt-1">
            About your {TOPICS[formData.topic]?.label.toLowerCase() || 'situation'}
          </p>
        </div>
      </div>

      <div className="px-6 space-y-6 pb-32">
        {/* Urgency */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-3">
            How urgent is this?
          </label>
          <div className="space-y-2">
            {Object.entries(URGENCY_LEVELS).map(([key, urgency]) => (
              <button
                key={key}
                onClick={() => setFormData(prev => ({ ...prev, urgency: key }))}
                className={`w-full border-2 rounded-xl p-4 text-left transition-all ${
                  formData.urgency === key 
                    ? 'border-emerald-500 bg-emerald-50' 
                    : 'border-slate-200 hover:border-emerald-300'
                }`}
              >
                <div className="flex items-center">
                  <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                    formData.urgency === key 
                      ? 'border-emerald-500 bg-emerald-500' 
                      : 'border-slate-300'
                  }`}>
                    {formData.urgency === key && (
                      <div className="w-full h-full flex items-center justify-center">
                        <div className="w-1.5 h-1.5 bg-white rounded-full" />
                      </div>
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-slate-800">{urgency.label}</p>
                    <p className="text-sm text-slate-500">{urgency.description}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Decision Ownership */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-3">
            Who makes this decision?
          </label>
          <div className="space-y-2">
            {Object.entries(DECISION_OWNERSHIP).map(([key, ownership]) => (
              <button
                key={key}
                onClick={() => setFormData(prev => ({ ...prev, decision_ownership: key }))}
                className={`w-full border-2 rounded-xl p-4 text-left transition-all ${
                  formData.decision_ownership === key 
                    ? 'border-emerald-500 bg-emerald-50' 
                    : 'border-slate-200 hover:border-emerald-300'
                }`}
              >
                <div className="flex items-center">
                  <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                    formData.decision_ownership === key 
                      ? 'border-emerald-500 bg-emerald-500' 
                      : 'border-slate-300'
                  }`}>
                    {formData.decision_ownership === key && (
                      <div className="w-full h-full flex items-center justify-center">
                        <div className="w-1.5 h-1.5 bg-white rounded-full" />
                      </div>
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-slate-800">{ownership.label}</p>
                    <p className="text-sm text-slate-500">{ownership.description}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Desired Outcome */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-3">
            What outcome do you want? <span className="text-slate-400">(optional)</span>
          </label>
          <textarea
            value={formData.desired_outcome}
            onChange={(e) => setFormData(prev => ({ ...prev, desired_outcome: e.target.value }))}
            placeholder="e.g., Clarity on whether to switch jobs, Find the right time to start my business..."
            className="w-full border-2 border-slate-200 rounded-xl p-4 text-slate-800 placeholder-slate-400 focus:border-emerald-500 focus:outline-none resize-none"
            rows={3}
          />
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 text-red-700 px-4 py-3 rounded-xl text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Fixed CTA */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-100 p-4">
        <button
          onClick={handleSubmit}
          disabled={loading || !formData.urgency || !formData.decision_ownership}
          className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold py-4 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all"
        >
          {loading ? 'Saving...' : 'Start Conversation'}
        </button>
        <p className="text-center text-xs text-slate-400 mt-2">
          🔒 Your information is private and secure
        </p>
      </div>
    </div>
  );
}
