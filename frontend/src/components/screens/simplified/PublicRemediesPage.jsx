import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { colors, shadows } from './theme';
import { CheckIcon, StarIcon } from './icons';
import PublicNavHeader from './PublicNavHeader';

/**
 * PublicRemediesPage - Publicly accessible remedies catalog (no login required)
 * Shows all remedy products and poojas from the API
 * Login only required for checkout/purchase
 */

const REMEDY_CATEGORIES = [
  { id: 'all', label: 'All Remedies' },
  { id: 'healing', label: 'Healing Programs' },
  { id: 'pooja', label: 'Poojas' },
  { id: 'gemstone', label: 'Gemstones' },
  { id: 'kit', label: 'Wellness Kits' },
  { id: 'ritual', label: 'Rituals' },
];

// Extended remedy details (benefits, description, etc.) - will be merged with API data
const REMEDY_DETAILS = {
  chakra_balance: {
    description: 'A structured 3-session chakra healing plan to feel calmer, clearer, and more grounded',
    benefits: ['3 × guided chakra healing sessions', 'Daily micro-practice plan', 'Guided meditation support'],
    image: '🧘',
    featured: true,
    rating: 4.9,
    reviews: 156,
  },
  santan_pooja: {
    description: 'Verified blessing for fertility and conception support',
    benefits: ['Performed by verified priests', 'Includes prasad delivery', '60-day prayer cycle'],
    image: '🙏',
    rating: 4.9,
    reviews: 324,
  },
  shanti_pooja: {
    description: 'Graha pacification for mental peace and harmony',
    benefits: ['Reduces stress & anxiety', 'Family harmony', 'Planetary balance'],
    image: '🙏',
    rating: 4.8,
    reviews: 567,
  },
  lakshmi_pooja: {
    description: 'Blessing for prosperity, wealth, and financial growth',
    benefits: ['Prosperity blessings', 'Business success', 'Financial stability'],
    image: '🪔',
    rating: 4.9,
    reviews: 892,
  },
  obstacle_removal: {
    description: 'Remove obstacles and blockages from your path',
    benefits: ['Clear obstacles', 'Path clearing', 'Success enablement'],
    image: '🛡️',
    rating: 4.8,
    reviews: 445,
  },
  gemstone_career: {
    description: 'Natural gemstone for career growth and financial abundance',
    benefits: ['Career advancement', 'Financial growth', 'Professional success'],
    image: '💎',
    rating: 4.7,
    reviews: 234,
  },
  gemstone_calm: {
    description: 'Natural gemstone for mental peace and emotional grounding',
    benefits: ['Stress relief', 'Emotional balance', 'Inner calm'],
    image: '💙',
    rating: 4.8,
    reviews: 312,
  },
  gemstone_relationship: {
    description: 'Natural gemstone for harmony in relationships',
    benefits: ['Relationship harmony', 'Love attraction', 'Emotional connection'],
    image: '💛',
    rating: 4.6,
    reviews: 198,
  },
  stress_sleep_kit: {
    description: 'Complete kit for stress relief and better sleep',
    benefits: ['Stress management', 'Improved sleep', 'Relaxation aids'],
    image: '🌙',
    rating: 4.6,
    reviews: 678,
  },
  protection_kit: {
    description: 'Essential items for spiritual protection',
    benefits: ['Spiritual shield', 'Negative energy removal', 'Daily protection'],
    image: '🛡️',
    rating: 4.5,
    reviews: 456,
  },
  prosperity_kit: {
    description: 'Complete prosperity and abundance kit',
    benefits: ['Wealth attraction', 'Prosperity mantras', 'Abundance rituals'],
    image: '💰',
    rating: 4.7,
    reviews: 389,
  },
  vitality_kit: {
    description: 'Energy and vitality boosting kit',
    benefits: ['Energy boost', 'Vitality enhancement', 'Health support'],
    image: '⚡',
    rating: 4.5,
    reviews: 267,
  },
  venus_harmony: {
    description: 'Ritual for love, beauty and relationship harmony',
    benefits: ['Love enhancement', 'Beauty rituals', 'Venus blessings'],
    image: '💕',
    rating: 4.7,
    reviews: 234,
  },
  mercury_focus: {
    description: 'Ritual for mental clarity and communication',
    benefits: ['Mental clarity', 'Better communication', 'Focus enhancement'],
    image: '🧠',
    rating: 4.6,
    reviews: 189,
  },
  moon_calm: {
    description: 'Moon ritual for emotional balance and peace',
    benefits: ['Emotional balance', 'Inner peace', 'Moon blessings'],
    image: '🌙',
    rating: 4.8,
    reviews: 345,
  },
};

// Default details for remedies not in our extended details
const DEFAULT_REMEDY_DETAILS = {
  description: 'Authentic healing remedy curated by our experts',
  benefits: ['Expert-verified', 'Quality assured', 'Traditional methods'],
  image: '✨',
  rating: 4.5,
  reviews: 100,
};

// Format price
const formatPrice = (price) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
};

// Remedy Card Component
function RemedyCard({ remedy, onSelect }) {
  return (
    <div
      onClick={() => onSelect(remedy)}
      className="rounded-xl p-5 cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1 active:scale-[0.98]"
      style={{ 
        backgroundColor: '#ffffff',
        border: remedy.featured ? `2px solid ${colors.peach.primary}` : `1px solid ${colors.ui.borderDark}`,
        boxShadow: shadows.card,
      }}
      data-testid={`remedy-card-${remedy.id}`}
    >
      {/* Featured Badge */}
      {remedy.featured && (
        <div 
          className="inline-block text-xs font-semibold px-3 py-1 rounded-full mb-3"
          style={{ backgroundColor: colors.peach.soft, color: colors.text.dark }}
        >
          Popular
        </div>
      )}
      
      {/* Icon & Title */}
      <div className="flex items-start gap-3 mb-3">
        <div 
          className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
          style={{ backgroundColor: `${colors.teal.primary}10` }}
        >
          {remedy.image}
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-base" style={{ color: colors.text.dark }}>
            {remedy.title}
          </h3>
          {remedy.subtitle && (
            <p className="text-xs" style={{ color: colors.teal.primary }}>{remedy.subtitle}</p>
          )}
        </div>
      </div>
      
      {/* Description */}
      <p className="text-sm mb-3 line-clamp-2" style={{ color: colors.text.secondary }}>
        {remedy.description}
      </p>
      
      {/* Benefits */}
      <div className="space-y-1.5 mb-4">
        {remedy.benefits.slice(0, 3).map((benefit, idx) => (
          <div key={idx} className="flex items-start gap-2">
            <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
            <span className="text-xs" style={{ color: colors.text.secondary }}>{benefit}</span>
          </div>
        ))}
      </div>
      
      {/* Rating & Price */}
      <div className="flex items-center justify-between pt-3 border-t" style={{ borderColor: colors.ui.borderDark }}>
        <div className="flex items-center gap-1.5">
          <StarIcon className="w-4 h-4" style={{ color: '#F59E0B' }} filled />
          <span className="text-sm font-medium" style={{ color: colors.text.dark }}>{remedy.rating}</span>
          <span className="text-xs" style={{ color: colors.text.muted }}>({remedy.reviews})</span>
        </div>
        <div className="text-right">
          <p className="font-bold" style={{ color: colors.teal.primary }}>{formatPrice(remedy.price)}</p>
        </div>
      </div>
    </div>
  );
}

export default function PublicRemediesPage({ isAuthenticated }) {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedRemedy, setSelectedRemedy] = useState(null);
  const [remedies, setRemedies] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch remedies from API
  useEffect(() => {
    const fetchRemedies = async () => {
      try {
        const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
        const response = await fetch(`${backendUrl}/api/remedies/catalog`);
        if (response.ok) {
          const data = await response.json();
          if (data.ok && data.remedies) {
            // Merge API data with extended details
            const enrichedRemedies = data.remedies.map(r => {
              const details = REMEDY_DETAILS[r.remedy_id] || DEFAULT_REMEDY_DETAILS;
              return {
                id: r.remedy_id,
                title: r.name,
                price: r.price,
                category: r.category,
                ...details,
              };
            });
            setRemedies(enrichedRemedies);
          }
        }
      } catch (err) {
        console.error('Failed to load remedies:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchRemedies();
  }, []);

  // Filter remedies by category
  const filteredRemedies = selectedCategory === 'all' 
    ? remedies 
    : remedies.filter(r => r.category === selectedCategory);

  // Handle remedy selection
  const handleRemedySelect = (remedy) => {
    setSelectedRemedy(remedy);
  };

  // Handle purchase - requires login
  const handlePurchase = (remedy) => {
    if (isAuthenticated) {
      // Navigate to app remedies for purchase
      navigate('/app/remedies');
    } else {
      // Store intent and redirect to login
      localStorage.setItem('niro_user_intent', JSON.stringify({ 
        type: 'purchase_remedy',
        remedyId: remedy.id,
        returnTo: '/app/remedies'
      }));
      navigate('/login');
    }
  };

  // Close detail modal
  const closeDetailModal = () => {
    setSelectedRemedy(null);
  };

  return (
    <div 
      className="min-h-screen"
      style={{ backgroundColor: colors.background.primary }}
    >
      {/* Header with Navigation */}
      <PublicNavHeader isAuthenticated={isAuthenticated} />

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 md:px-8 py-8">
        {/* Page Header */}
        <div className="text-center mb-8">
          <h1 
            className="text-2xl md:text-3xl lg:text-4xl font-bold mb-2"
            style={{ color: colors.text.dark }}
          >
            Remedies & Healing
          </h1>
          <p 
            className="text-sm md:text-base max-w-2xl mx-auto"
            style={{ color: colors.text.secondary }}
          >
            Discover authentic healing programs, poojas, gemstones, and wellness kits curated by our experts.
          </p>
        </div>

        {/* Category Filter */}
        <div className="flex gap-2 overflow-x-auto pb-4 mb-6 scrollbar-hide">
          {REMEDY_CATEGORIES.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className="px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all"
              style={{
                backgroundColor: selectedCategory === category.id ? colors.teal.primary : '#ffffff',
                color: selectedCategory === category.id ? '#ffffff' : colors.text.secondary,
                border: `1px solid ${selectedCategory === category.id ? colors.teal.primary : colors.ui.borderDark}`,
              }}
              data-testid={`category-${category.id}`}
            >
              {category.label}
            </button>
          ))}
        </div>

        {/* Remedies Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="rounded-xl p-5 animate-pulse"
                style={{ backgroundColor: '#ffffff', border: `1px solid ${colors.ui.borderDark}` }}
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-12 h-12 rounded-xl" style={{ backgroundColor: `${colors.teal.primary}10` }}></div>
                  <div className="flex-1">
                    <div className="h-4 rounded" style={{ backgroundColor: 'rgba(0,0,0,0.1)', width: '70%' }}></div>
                    <div className="h-3 rounded mt-2" style={{ backgroundColor: 'rgba(0,0,0,0.05)', width: '50%' }}></div>
                  </div>
                </div>
                <div className="space-y-2 mb-4">
                  <div className="h-3 rounded" style={{ backgroundColor: 'rgba(0,0,0,0.05)' }}></div>
                  <div className="h-3 rounded" style={{ backgroundColor: 'rgba(0,0,0,0.05)', width: '80%' }}></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {filteredRemedies.map((remedy) => (
              <RemedyCard
                key={remedy.id}
                remedy={remedy}
                onSelect={handleRemedySelect}
              />
            ))}
          </div>
        )}

        {!loading && filteredRemedies.length === 0 && (
          <div className="text-center py-12">
            <p className="text-lg" style={{ color: colors.text.muted }}>No remedies found in this category</p>
          </div>
        )}
      </div>

      {/* Remedy Detail Modal */}
      {selectedRemedy && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={closeDetailModal}
        >
          <div 
            className="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between" style={{ borderColor: colors.ui.borderDark }}>
              <h2 className="text-xl font-bold" style={{ color: colors.text.dark }}>{selectedRemedy.title}</h2>
              <button
                onClick={closeDetailModal}
                className="p-2 rounded-full hover:bg-black/5"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {/* Icon & Subtitle */}
              <div className="flex items-center gap-4 mb-4">
                <div 
                  className="w-16 h-16 rounded-xl flex items-center justify-center text-3xl"
                  style={{ backgroundColor: `${colors.teal.primary}10` }}
                >
                  {selectedRemedy.image}
                </div>
                <div>
                  <p className="text-sm" style={{ color: colors.teal.primary }}>{selectedRemedy.subtitle || selectedRemedy.category}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <StarIcon className="w-4 h-4" style={{ color: '#F59E0B' }} filled />
                    <span className="text-sm font-medium">{selectedRemedy.rating}</span>
                    <span className="text-xs" style={{ color: colors.text.muted }}>({selectedRemedy.reviews} reviews)</span>
                  </div>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm mb-6" style={{ color: colors.text.secondary }}>
                {selectedRemedy.description}
              </p>

              {/* Benefits */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold mb-3" style={{ color: colors.text.dark }}>What's included:</h3>
                <div className="space-y-2">
                  {selectedRemedy.benefits.map((benefit, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <CheckIcon className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: colors.teal.primary }} />
                      <span className="text-sm" style={{ color: colors.text.secondary }}>{benefit}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Price & CTA */}
              <div className="flex items-center justify-between pt-4 border-t" style={{ borderColor: colors.ui.borderDark }}>
                <div>
                  <p className="text-2xl font-bold" style={{ color: colors.teal.primary }}>
                    {formatPrice(selectedRemedy.price)}
                  </p>
                </div>
                <button
                  onClick={() => handlePurchase(selectedRemedy)}
                  className="px-6 py-3 rounded-full font-semibold text-base transition-all hover:shadow-lg hover:-translate-y-0.5"
                  style={{ 
                    backgroundColor: colors.peach.primary,
                    color: colors.text.dark,
                    boxShadow: shadows.peach,
                  }}
                  data-testid="purchase-remedy-btn"
                >
                  {isAuthenticated ? 'Purchase Now' : 'Login to Purchase'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer 
        className="py-8 px-6 text-center"
        style={{ 
          backgroundColor: colors.background.secondary,
          borderTop: `1px solid ${colors.ui.borderDark}`,
        }}
      >
        <p className="text-2xl font-bold mb-2" style={{ color: colors.teal.dark }}>niro</p>
        <p className="text-sm" style={{ color: colors.text.muted }}>
          Niro provides astrology-based guidance across Vedic astrology and healing modalities.
        </p>
        <p className="text-xs mt-4" style={{ color: colors.text.muted }}>
          Our guidance is not a substitute for medical, legal, or financial advice.
        </p>
      </footer>
    </div>
  );
}
