import React, { useState, useEffect } from 'react';
import { apiV2, formatPrice, getRemedyCategoryIcon, getRemedyCategoryLabel } from './utils';

/**
 * RemedyCatalogScreen - Browse and purchase remedy add-ons
 */
export default function RemedyCatalogScreen({ 
  token,
  planId,
  onPurchase,
  onBack 
}) {
  const [loading, setLoading] = useState(true);
  const [remedies, setRemedies] = useState([]);
  const [activeCategory, setActiveCategory] = useState('all');
  const [selectedRemedy, setSelectedRemedy] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRemedies();
  }, []);

  const loadRemedies = async () => {
    try {
      const response = await apiV2.get('/catalog/remedies', token);
      if (response.ok) {
        setRemedies(response.remedies);
      }
    } catch (err) {
      setError('Failed to load remedies');
    } finally {
      setLoading(false);
    }
  };

  const filteredRemedies = activeCategory === 'all' 
    ? remedies 
    : remedies.filter(r => r.category === activeCategory);

  const categories = [
    { id: 'all', label: 'All' },
    { id: 'astrological', label: 'Astrological' },
    { id: 'spiritual', label: 'Spiritual' },
    { id: 'healing', label: 'Healing' },
  ];

  // Loading
  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-emerald-200 border-t-emerald-500 rounded-full animate-spin" />
      </div>
    );
  }

  // Remedy Detail Modal
  if (selectedRemedy) {
    return (
      <div className="min-h-screen bg-white">
        <div className="px-6 pt-12 pb-6">
          <button 
            onClick={() => setSelectedRemedy(null)}
            className="text-slate-500 mb-4 flex items-center"
          >
            <span className="mr-2">←</span> Back
          </button>
        </div>

        <div className="px-6 pb-40">
          {/* Header */}
          <div className="text-center mb-6">
            <span className="text-5xl mb-4 block">{getRemedyCategoryIcon(selectedRemedy.category)}</span>
            <h1 className="text-2xl font-bold text-slate-800">{selectedRemedy.name}</h1>
            <p className="text-slate-500 mt-2">{selectedRemedy.description}</p>
            <span className="inline-block mt-3 bg-slate-100 text-slate-600 text-sm px-3 py-1 rounded-full">
              {getRemedyCategoryLabel(selectedRemedy.category)}
            </span>
          </div>

          {/* What's Included */}
          <div className="bg-emerald-50 rounded-2xl p-5 mb-4">
            <h3 className="font-semibold text-slate-800 mb-3">What's Included</h3>
            <ul className="space-y-2">
              {selectedRemedy.what_included?.map((item, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-emerald-500 mr-2">✓</span>
                  <span className="text-slate-700 text-sm">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* How It Works */}
          <div className="bg-slate-50 rounded-2xl p-5 mb-4">
            <h3 className="font-semibold text-slate-800 mb-3">How It Works</h3>
            <ol className="space-y-3">
              {selectedRemedy.how_it_works?.map((step, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="w-6 h-6 bg-white rounded-full flex items-center justify-center text-xs font-medium text-slate-600 mr-3 flex-shrink-0">
                    {idx + 1}
                  </span>
                  <span className="text-slate-700 text-sm">{step}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Delivery Info */}
          <div className="flex items-center justify-between p-4 bg-blue-50 rounded-xl">
            <div className="flex items-center">
              <span className="text-blue-500 mr-2">⏰</span>
              <span className="text-slate-700 text-sm">Delivery: {selectedRemedy.delivery_timeline}</span>
            </div>
          </div>
        </div>

        {/* Fixed CTA */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-100 p-4">
          <button
            onClick={() => onPurchase(selectedRemedy.remedy_id, planId)}
            className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-white font-semibold py-4 rounded-xl hover:shadow-lg transition-all"
          >
            Add to My Plan • {formatPrice(selectedRemedy.price_inr)}
          </button>
        </div>
      </div>
    );
  }

  // Catalog List
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white px-6 pt-12 pb-4 border-b border-slate-100">
        <button 
          onClick={onBack}
          className="text-slate-500 mb-4 flex items-center"
        >
          <span className="mr-2">←</span> Back
        </button>
        <h1 className="text-2xl font-semibold text-slate-900">Remedy Add-Ons</h1>
        <p className="text-slate-500 text-sm mt-1">Enhance your journey with personalized remedies</p>
      </div>

      {/* Category Tabs */}
      <div className="bg-white px-6 py-3 border-b border-slate-100 overflow-x-auto">
        <div className="flex space-x-2">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                activeCategory === cat.id
                  ? 'bg-emerald-500 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Remedy List */}
      <div className="p-6 space-y-3">
        {filteredRemedies.map(remedy => (
          <div 
            key={remedy.remedy_id}
            onClick={() => setSelectedRemedy(remedy)}
            className="bg-white rounded-2xl p-5 border border-slate-100 cursor-pointer hover:shadow-md transition-all"
          >
            <div className="flex items-start">
              <span className="text-3xl mr-4">{getRemedyCategoryIcon(remedy.category)}</span>
              <div className="flex-1">
                <h3 className="font-semibold text-slate-800">{remedy.name}</h3>
                <p className="text-slate-500 text-sm mt-1 line-clamp-2">{remedy.description}</p>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full">
                    {getRemedyCategoryLabel(remedy.category)}
                  </span>
                  <span className="font-semibold text-slate-800">{formatPrice(remedy.price_inr)}</span>
                </div>
              </div>
              <span className="text-slate-400 ml-2">→</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
