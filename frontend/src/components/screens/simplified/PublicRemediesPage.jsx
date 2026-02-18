import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { colors, shadows } from './theme';
import { CheckIcon, ChevronRightIcon, StarIcon } from './icons';
import PublicNavHeader from './PublicNavHeader';

/**
 * PublicRemediesPage - Publicly accessible remedies catalog (no login required)
 * Shows all remedy products and poojas
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

const REMEDIES = [
  {
    id: 'chakra_balance',
    category: 'healing',
    title: 'Chakra Balance Program',
    subtitle: '3 Guided Sessions',
    description: 'A structured 3-session chakra healing plan to feel calmer, clearer, and more grounded',
    price: 3500,
    rating: 4.9,
    reviews: 156,
    benefits: ['3 × guided chakra healing sessions', 'Daily micro-practice plan', 'Guided meditation support'],
    image: '🧘',
    featured: true,
  },
  {
    id: 'santan_pooja',
    category: 'pooja',
    title: 'Santan / Fertility Pooja',
    description: 'Verified blessing for fertility and conception support',
    price: 2499,
    rating: 4.9,
    reviews: 324,
    benefits: ['Performed by verified priests', 'Includes prasad delivery', '60-day prayer cycle'],
    image: '🙏',
  },
  {
    id: 'shanti_pooja',
    category: 'pooja',
    title: 'Shanti / Peace Pooja',
    description: 'Graha pacification for mental peace and harmony',
    price: 1999,
    rating: 4.8,
    reviews: 567,
    benefits: ['Reduces stress & anxiety', 'Family harmony', 'Planetary balance'],
    image: '🙏',
  },
  {
    id: 'lakshmi_pooja',
    category: 'pooja',
    title: 'Lakshmi Pooja',
    description: 'Blessing for prosperity, wealth, and financial growth',
    price: 2999,
    rating: 4.9,
    reviews: 892,
    benefits: ['Prosperity blessings', 'Business success', 'Financial stability'],
    image: '🪔',
  },
  {
    id: 'navgraha_shanti',
    category: 'pooja',
    title: 'Navgraha Shanti Pooja',
    description: 'Pacification of all nine planets for overall life balance',
    price: 5999,
    rating: 4.9,
    reviews: 445,
    benefits: ['All 9 planetary alignments', 'Life balance', 'Removes obstacles'],
    image: '🌟',
  },
  {
    id: 'neelam_gemstone',
    category: 'gemstone',
    title: 'Blue Sapphire (Neelam)',
    description: 'Certified natural blue sapphire for Saturn influence',
    price: 15000,
    rating: 4.7,
    reviews: 234,
    benefits: ['Saturn pacification', 'Career growth', 'Mental clarity'],
    image: '💎',
  },
  {
    id: 'pukhraj_gemstone',
    category: 'gemstone',
    title: 'Yellow Sapphire (Pukhraj)',
    description: 'Certified natural yellow sapphire for Jupiter blessing',
    price: 12000,
    rating: 4.8,
    reviews: 312,
    benefits: ['Jupiter blessings', 'Wisdom & knowledge', 'Marital harmony'],
    image: '💛',
  },
  {
    id: 'rudraksha_kit',
    category: 'kit',
    title: 'Rudraksha Wellness Kit',
    description: 'Authentic 5-mukhi rudraksha with puja items',
    price: 1499,
    rating: 4.6,
    reviews: 678,
    benefits: ['Stress relief', 'Spiritual protection', 'Complete puja set'],
    image: '📿',
  },
  {
    id: 'meditation_kit',
    category: 'kit',
    title: 'Home Meditation Kit',
    description: 'Essential items for daily meditation practice',
    price: 999,
    rating: 4.5,
    reviews: 456,
    benefits: ['Incense & dhoop', 'Meditation guide', 'Altar setup items'],
    image: '🕯️',
  },
  {
    id: 'havan_ritual',
    category: 'ritual',
    title: 'Home Havan Kit',
    description: 'Complete havan materials with guided instructions',
    price: 799,
    rating: 4.7,
    reviews: 234,
    benefits: ['All havan materials', 'Video guidance', 'Mantras included'],
    image: '🔥',
  },
];

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

  // Filter remedies by category
  const filteredRemedies = selectedCategory === 'all' 
    ? REMEDIES 
    : REMEDIES.filter(r => r.category === selectedCategory);

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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          {filteredRemedies.map((remedy) => (
            <RemedyCard
              key={remedy.id}
              remedy={remedy}
              onSelect={handleRemedySelect}
            />
          ))}
        </div>

        {filteredRemedies.length === 0 && (
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
