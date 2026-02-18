import React, { useState } from 'react';
import { colors, shadows } from './theme';
import { RemediesIcon, StarIcon, CheckIcon, ChevronRightIcon, ShieldIcon, GiftIcon } from './icons';
import { BACKEND_URL } from '../../../config';
import { getAuthToken } from '../../../utils/auth';
import ResponsiveHeader from './ResponsiveHeader';

/**
 * RemediesScreen V2 - Full remedies catalog with responsive layout
 * Shows actual remedy products and poojas with Razorpay payment integration
 */

// Load Razorpay script dynamically
const loadRazorpayScript = () => {
  return new Promise((resolve) => {
    if (window.Razorpay) {
      resolve(true);
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
};

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
    benefits: ['3 × guided chakra healing sessions', 'Daily micro-practice plan (5-10 mins)', 'Guided meditation support', 'Diet guidance for energy balance', '24-hour follow-up support'],
    helpsWithList: ['Stress, anxiety, overthinking', 'Emotional heaviness, feeling stuck', 'Low confidence, low energy'],
    expert: {
      name: 'Anu Khanna',
      title: 'Vedic Astrology + Chakra Healing',
      experience: '20+ years',
      languages: 'English/Hindi',
      bio: 'Anu blends chakra healing with yoga and meditation to help you find calm, clarity, and alignment.'
    },
    programOutcome: 'More emotional steadiness and calm, better grounding and clarity, a repeatable daily practice to maintain balance',
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
    title: 'Lakshmi Prosperity Pooja',
    description: 'Weekly prosperity ritual for financial growth',
    price: 2499,
    rating: 4.9,
    reviews: 892,
    benefits: ['Friday Lakshmi routine', 'Wealth attraction', '30-day cycle'],
    image: '🪔',
  },
  {
    id: 'obstacle_removal',
    category: 'pooja',
    title: 'Obstacle Removal Pooja',
    description: 'Ganesha pooja for clearing blocks in career and life',
    price: 1999,
    rating: 4.8,
    reviews: 445,
    benefits: ['Career growth', 'Remove blockers', 'New beginnings'],
    image: '🙏',
  },
  {
    id: 'gemstone_career',
    category: 'gemstone',
    title: 'Career & Abundance Gemstone',
    description: 'Expert-recommended gemstone for professional growth',
    price: 1499,
    rating: 4.7,
    reviews: 234,
    benefits: ['Chart-based selection', 'Certified stones', 'Energization included'],
    image: '💎',
  },
  {
    id: 'gemstone_calm',
    category: 'gemstone',
    title: 'Calm & Grounding Gemstone',
    description: 'Gemstone for stress relief and emotional balance',
    price: 1499,
    rating: 4.8,
    reviews: 189,
    benefits: ['Reduces anxiety', 'Better sleep', 'Emotional stability'],
    image: '💎',
  },
  {
    id: 'gemstone_relationship',
    category: 'gemstone',
    title: 'Relationship Harmony Gemstone',
    description: 'Venus-aligned stone for love and compatibility',
    price: 1499,
    rating: 4.7,
    reviews: 156,
    benefits: ['Improves communication', 'Attracts love', 'Partnership harmony'],
    image: '💎',
  },
  {
    id: 'stress_sleep_kit',
    category: 'kit',
    title: 'Stress & Sleep Kit',
    description: 'Complete wellness kit for better sleep and calm',
    price: 899,
    rating: 4.8,
    reviews: 423,
    benefits: ['21-day routine', 'Natural ingredients', 'Guided practice'],
    image: '🌙',
  },
  {
    id: 'protection_kit',
    category: 'kit',
    title: 'Protection Kit',
    description: 'Evil-eye protection and calming energy kit',
    price: 799,
    rating: 4.7,
    reviews: 356,
    benefits: ['Ward off negativity', 'Confidence boost', 'Grounding practice'],
    image: '🛡️',
  },
  {
    id: 'prosperity_kit',
    category: 'kit',
    title: 'Prosperity Kit',
    description: 'D2C wealth and abundance attraction kit',
    price: 999,
    rating: 4.8,
    reviews: 278,
    benefits: ['Lakshmi routine', 'Wealth affirmations', '30-day practice'],
    image: '✨',
  },
  {
    id: 'vitality_kit',
    category: 'kit',
    title: 'Vitality Kit',
    description: 'Energy restoration and daily wellness kit',
    price: 799,
    rating: 4.7,
    reviews: 198,
    benefits: ['Sun energy boost', 'Morning routine', '14-day reset'],
    image: '☀️',
  },
  {
    id: 'venus_harmony',
    category: 'ritual',
    title: 'Venus Harmony Ritual',
    description: 'Guided 21-day ritual for love and relationships',
    price: 999,
    rating: 4.9,
    reviews: 234,
    benefits: ['Daily prompts', 'Self-love focus', 'Communication tips'],
    image: '💕',
  },
  {
    id: 'mercury_focus',
    category: 'ritual',
    title: 'Mercury Focus Ritual',
    description: 'Concentration and clarity daily practice',
    price: 799,
    rating: 4.7,
    reviews: 167,
    benefits: ['Better focus', 'Clear thinking', 'Decision making'],
    image: '🧠',
  },
  {
    id: 'moon_calm',
    category: 'ritual',
    title: 'Moon-Mercury Calm Ritual',
    description: 'Sleep, anxiety and communication routine',
    price: 899,
    rating: 4.8,
    reviews: 289,
    benefits: ['Better sleep', 'Reduced anxiety', 'Calm communication'],
    image: '🌙',
  },
];

const formatPrice = (price) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
};

export default function RemediesScreen({ hasBottomNav, onTabChange, onNavigate }) {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedRemedy, setSelectedRemedy] = useState(null);
  const [purchasing, setPurchasing] = useState(false);
  const [purchaseStatus, setPurchaseStatus] = useState(null);

  const filteredRemedies = selectedCategory === 'all' 
    ? REMEDIES 
    : REMEDIES.filter(r => r.category === selectedCategory);

  const handlePurchase = async (remedy) => {
    setPurchasing(true);
    setPurchaseStatus(null);

    try {
      // Load Razorpay script
      const scriptLoaded = await loadRazorpayScript();
      if (!scriptLoaded) {
        throw new Error('Failed to load payment gateway');
      }

      const token = getAuthToken();
      
      // Create order
      const orderResponse = await fetch(`${BACKEND_URL}/api/remedies/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        credentials: 'include',
        body: JSON.stringify({
          remedy_id: remedy.id,
          source: 'direct',
        }),
      });

      const orderData = await orderResponse.json();
      
      if (!orderData.ok) {
        throw new Error(orderData.detail || 'Failed to create order');
      }

      // Open Razorpay checkout
      const options = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: 'INR',
        name: 'Niro',
        description: remedy.title,
        order_id: orderData.razorpay_order_id,
        handler: async function (response) {
          // Verify payment
          try {
            const verifyResponse = await fetch(`${BACKEND_URL}/api/remedies/verify-payment`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
              },
              credentials: 'include',
              body: JSON.stringify({
                remedy_order_id: orderData.remedy_order_id,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              }),
            });

            const verifyData = await verifyResponse.json();
            
            if (verifyData.ok) {
              setPurchaseStatus('success');
              setSelectedRemedy(null);
            } else {
              setPurchaseStatus('failed');
            }
          } catch (err) {
            console.error('Payment verification failed:', err);
            setPurchaseStatus('failed');
          }
        },
        prefill: {},
        theme: {
          color: '#3E827A',
        },
        modal: {
          ondismiss: function () {
            setPurchasing(false);
          },
        },
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (err) {
      console.error('Purchase failed:', err);
      setPurchaseStatus('error');
    } finally {
      setPurchasing(false);
    }
  };

  return (
    <div 
      className={`min-h-screen flex flex-col ${hasBottomNav ? 'pb-20 md:pb-0' : ''}`}
      style={{ 
        backgroundColor: colors.background.primary,
        paddingTop: 'env(safe-area-inset-top)',
      }}
    >
      {/* Responsive Header */}
      <ResponsiveHeader
        title="Remedies"
        showBackButton={false}
        onNavigate={onNavigate}
        onTabChange={onTabChange}
      />

      {/* Header Section */}
      <div className="px-5 md:px-8 pt-6 pb-4 max-w-6xl mx-auto w-full">
        <h1 
          className="text-2xl md:text-3xl font-bold mb-1"
          style={{ color: colors.text.dark }}
        >
          Remedies
        </h1>
        <p className="text-sm md:text-base" style={{ color: colors.text.secondary }}>
          Curated solutions for your life situations
        </p>
      </div>

      {/* Category Pills */}
      <div className="px-5 md:px-8 pb-4 max-w-6xl mx-auto w-full">
        <div className="flex overflow-x-auto gap-2 pb-2 scrollbar-hide">
          {REMEDY_CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className="flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all"
              style={selectedCategory === cat.id
                ? { backgroundColor: colors.teal.primary, color: '#ffffff' }
                : { backgroundColor: '#ffffff', color: colors.text.muted, border: `1px solid ${colors.ui.borderDark}` }
              }
              data-testid={`remedy-filter-${cat.id}`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Remedies List - Responsive Grid */}
      <div className="flex-1 px-5 md:px-8 pb-6 max-w-6xl mx-auto w-full">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRemedies.map((remedy) => (
            <div
              key={remedy.id}
              onClick={() => setSelectedRemedy(remedy)}
              className="rounded-xl p-4 transition-all active:scale-[0.99] cursor-pointer hover:shadow-md"
              style={{ 
                backgroundColor: '#ffffff',
                border: `1px solid ${colors.ui.borderDark}`,
                boxShadow: shadows.sm,
              }}
              data-testid={`remedy-card-${remedy.id}`}
            >
              <div className="flex gap-4">
                {/* Icon */}
                <div 
                  className="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0 text-2xl"
                  style={{ backgroundColor: `${colors.teal.primary}10` }}
                >
                  {remedy.image}
                </div>
                
                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold text-sm md:text-base line-clamp-1" style={{ color: colors.text.dark }}>
                      {remedy.title}
                    </h3>
                    <ChevronRightIcon className="w-5 h-5 flex-shrink-0" style={{ color: colors.text.mutedDark }} />
                  </div>
                  <p className="text-xs md:text-sm mt-1 line-clamp-2" style={{ color: colors.text.secondary }}>
                    {remedy.description}
                  </p>
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center gap-1">
                      <StarIcon className="w-3.5 h-3.5" style={{ color: colors.peach.primary }} filled />
                      <span className="text-xs font-medium" style={{ color: colors.text.dark }}>{remedy.rating}</span>
                      <span className="text-xs" style={{ color: colors.text.mutedDark }}>({remedy.reviews})</span>
                    </div>
                    <span className="font-bold text-sm md:text-base" style={{ color: colors.teal.primary }}>
                      {formatPrice(remedy.price)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Trust Section */}
        <div className="mt-6 p-4 md:p-6 rounded-xl" style={{ backgroundColor: `${colors.teal.primary}08` }}>
          <div className="flex items-center gap-3 mb-3">
            <ShieldIcon className="w-5 h-5 md:w-6 md:h-6" style={{ color: colors.teal.primary }} />
            <span className="font-semibold text-sm md:text-base" style={{ color: colors.text.dark }}>Why Niro Remedies?</span>
          </div>
          <div className="space-y-2 md:grid md:grid-cols-3 md:gap-4 md:space-y-0">
            <div className="flex items-center gap-2">
              <CheckIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              <span className="text-xs md:text-sm" style={{ color: colors.text.secondary }}>All poojas performed by verified priests</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              <span className="text-xs md:text-sm" style={{ color: colors.text.secondary }}>Gemstones certified and energized</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckIcon className="w-4 h-4" style={{ color: colors.teal.primary }} />
              <span className="text-xs md:text-sm" style={{ color: colors.text.secondary }}>100% satisfaction guaranteed on all products</span>
            </div>
          </div>
        </div>
      </div>

      {/* Remedy Detail Modal */}
      {selectedRemedy && (
        <div 
          className="fixed inset-0 z-[60] flex items-end"
          onClick={() => setSelectedRemedy(null)}
        >
          <div 
            className="absolute inset-0"
            style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          />
          <div 
            className="relative w-full rounded-t-3xl p-6 max-h-[80vh] overflow-y-auto"
            style={{ backgroundColor: '#ffffff' }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Handle */}
            <div className="w-12 h-1 rounded-full mx-auto mb-4" style={{ backgroundColor: colors.ui.borderDark }} />
            
            {/* Content */}
            <div className="text-center mb-4">
              <div 
                className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 text-4xl"
                style={{ backgroundColor: `${colors.teal.primary}10` }}
              >
                {selectedRemedy.image}
              </div>
              <h2 className="text-xl font-bold" style={{ color: colors.text.dark }}>{selectedRemedy.title}</h2>
              <p className="text-sm mt-2" style={{ color: colors.text.secondary }}>{selectedRemedy.description}</p>
            </div>

            {/* Rating */}
            <div className="flex items-center justify-center gap-2 mb-4">
              <StarIcon className="w-5 h-5" style={{ color: '#F59E0B' }} filled />
              <span className="font-semibold" style={{ color: colors.text.dark }}>{selectedRemedy.rating}</span>
              <span style={{ color: colors.text.mutedDark }}>({selectedRemedy.reviews} reviews)</span>
            </div>

            {/* Benefits */}
            <div className="mb-6">
              <h3 className="font-semibold text-sm mb-3" style={{ color: colors.text.dark }}>What you get</h3>
              <div className="space-y-2">
                {selectedRemedy.benefits.map((benefit, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <CheckIcon className="w-5 h-5" style={{ color: colors.teal.primary }} />
                    <span className="text-sm" style={{ color: colors.text.secondary }}>{benefit}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* CTA */}
            <button
              onClick={() => handlePurchase(selectedRemedy)}
              disabled={purchasing}
              className="w-full py-4 rounded-xl font-semibold transition-all active:scale-[0.99] disabled:opacity-50"
              style={{ 
                backgroundColor: colors.gold.primary,
                color: colors.text.dark,
                boxShadow: shadows.md,
              }}
            >
              {purchasing ? 'Processing...' : `Buy Now — ${formatPrice(selectedRemedy.price)}`}
            </button>

            {/* Status Messages */}
            {purchaseStatus === 'success' && (
              <div className="mt-3 p-3 bg-green-100 text-green-700 rounded-lg text-center text-sm">
                ✓ Purchase successful! We'll contact you shortly.
              </div>
            )}
            {purchaseStatus === 'failed' && (
              <div className="mt-3 p-3 bg-red-100 text-red-700 rounded-lg text-center text-sm">
                Payment verification failed. Please contact support.
              </div>
            )}
            {purchaseStatus === 'error' && (
              <div className="mt-3 p-3 bg-red-100 text-red-700 rounded-lg text-center text-sm">
                Something went wrong. Please try again.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
