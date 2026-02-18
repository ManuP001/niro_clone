import React, { useState, useEffect } from 'react';
import { colors, shadows, borderRadius } from './theme';
import { getBackendUrl } from '../../../config';

/**
 * PublicLandingPage - Main entry point for all users
 * Based on niro-final-marquee_1.html design
 * 
 * CTAs:
 * - "Get Your Free 10-Min Call" → Triggers login with intent: free_call
 * - "Begin consultation" (per topic) → Triggers login with intent: consultation:{topic_id}
 */

// Intent storage helpers
export const setUserIntent = (intent) => {
  localStorage.setItem('niro_user_intent', JSON.stringify(intent));
};

export const getUserIntent = () => {
  const intent = localStorage.getItem('niro_user_intent');
  return intent ? JSON.parse(intent) : null;
};

export const clearUserIntent = () => {
  localStorage.removeItem('niro_user_intent');
};

// Life Topics Data
const LIFE_TOPICS = [
  {
    id: 'career',
    title: 'Career, Money & Business',
    description: 'For major professional transitions, business decisions, and understanding what path aligns with your strengths.',
    expertType: 'Vedic Astrologer · Career Timing',
    startingPrice: '₹2,999',
    icon: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
      </svg>
    ),
  },
  {
    id: 'health',
    title: 'Health & Wellness',
    description: 'For periods of low energy, emotional heaviness, or feeling stuck — through understanding your cycles.',
    expertType: 'Vedic Astrologer + Healer',
    startingPrice: '₹2,999',
    icon: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M19.5 13.5L12 21l-7.5-7.5a5.5 5.5 0 0 1 7.5-8 5.5 5.5 0 0 1 7.5 8z" />
        <path d="M12 13l2-3 2 4 2-3" />
      </svg>
    ),
  },
  {
    id: 'love',
    title: 'Love, Marriage & Relationships',
    description: 'For decisions about compatibility, timing, and relationship clarity when you need the right choice.',
    expertType: 'Vedic Astrologer · Compatibility',
    startingPrice: '₹3,999',
    icon: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
      </svg>
    ),
  },
  {
    id: 'fertility',
    title: 'Fertility & Family Planning',
    description: 'For understanding timing, readiness, and navigating the emotional journey toward parenthood.',
    expertType: 'Vedic Astrologer · Fertility Timing',
    startingPrice: '₹3,999',
    icon: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="9" cy="7" r="3" />
        <circle cx="17" cy="7" r="2" />
        <path d="M5 21v-2a4 4 0 0 1 4-4h2" />
        <path d="M15 21v-2a3 3 0 0 1 3-3" />
        <circle cx="12" cy="17" r="2" />
      </svg>
    ),
  },
];

// Testimonials Data
const TESTIMONIALS = [
  {
    text: "The astrologer was knowledgeable and explained things in a very simple, practical way. They listened patiently to my concerns and asked questions wherever needed, instead of rushing through. The remedies suggested were easy to follow and felt realistic.",
    author: "Vishal",
    topic: "Career Transition",
    rating: 5,
  },
  {
    text: "Good guidance and all positives. The astrologer provided helpful direction on my career path.",
    author: "Ajinkya",
    topic: "Career Guidance",
    rating: 4,
  },
  {
    text: "The prework by the astrologer was excellent. Got good clarity on my situation and the path forward.",
    author: "Abhishek",
    topic: "Career Decision",
    rating: 5,
  },
  {
    text: "He explained my past and future in detail and also gave possible remedies to overcome issues. He gave me proper time to discuss everything thoroughly.",
    author: "Jaya",
    topic: "Life Guidance",
    rating: 4,
  },
  {
    text: "The process from the beginning was very structured. It felt good that my astrologer was prepared beforehand. The entire conversation felt professional and I got the clarity I needed.",
    author: "Harshal",
    topic: "Marriage Decision",
    rating: 4,
  },
  {
    text: "The session started with clear expectations. My astrologer discussed Chakras and their relation to my current problem — a lot of things felt absolutely relatable. The Chakra healing advice looks like a great idea to me.",
    author: "Shilpi",
    topic: "Health & Wellness",
    rating: 4,
  },
];

// Experts Data
const EXPERTS = [
  { name: 'Prakash Jha', role: 'Vedic Astrologer, Tarot Reader', rating: 4.8, languages: 'Hindi, English', specialties: ['Career timing', 'Job changes', 'Relationship'] },
  { name: 'Sanjai Maharaj', role: 'Vedic Astrologer', rating: 4.9, languages: 'Hindi, English, Marathi', specialties: ['Marriage timing', 'Compatibility', 'Family'] },
  { name: 'Pooja Kapoor', role: 'Vedic Astrologer, Healer', rating: 4.7, languages: 'Hindi, English', specialties: ['Gemstones', 'Pooja', 'Chakra healing'] },
  { name: 'Vikram Rao', role: 'Vedic Astrologer', rating: 4.8, languages: 'Hindi, English, Telugu', specialties: ['Business', 'Finance', 'Career'] },
];

// How It Works Steps
const STEPS = [
  { number: '01', title: 'Choose & Book', items: ['Pick your life topic', 'Share birth details', 'Book a time slot'] },
  { number: '02', title: 'Your Session', items: ['Deep dive into your chart', 'Clarity on your situation', 'Timing guidance for action'] },
  { number: '03', title: 'Stay Supported', items: ['Unlimited chat access', 'Scheduled follow-ups', 'Till you find clarity'] },
  { number: '04', title: 'Remedies Execution', items: ['If recommended by expert', 'Verified service partners', 'Full transparency & proof'] },
];

// What We Offer Features
const OFFER_FEATURES = [
  { title: 'Curated, Verified Astrologers', icon: '✓' },
  { title: 'Situation-Based Packages', icon: '📦' },
  { title: 'Unlimited Chat Till Clarity', icon: '💬' },
  { title: 'No Fear, No Pressure', icon: '🛡️' },
  { title: 'End-to-end Support in Remedies Execution', icon: '🔧' },
];

// Star Rating Component
const StarRating = ({ rating }) => (
  <div className="flex items-center gap-0.5">
    {[...Array(5)].map((_, i) => (
      <svg
        key={i}
        className={`w-4 h-4 ${i < rating ? 'text-yellow-400' : 'text-gray-300'}`}
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
      </svg>
    ))}
  </div>
);

// Testimonial Card Component
const TestimonialCard = ({ testimonial }) => (
  <div
    className="flex-shrink-0 w-80 p-6 rounded-2xl transition-all duration-300 hover:-translate-y-1"
    style={{
      backgroundColor: colors.cream.primary,
      boxShadow: shadows.card,
    }}
  >
    <div className="flex items-center gap-2 mb-3">
      <span className="font-semibold text-sm" style={{ color: colors.text.dark }}>{testimonial.author}</span>
      <span className="text-xs" style={{ color: colors.text.muted }}>· {testimonial.topic}</span>
    </div>
    <StarRating rating={testimonial.rating} />
    <p className="mt-3 text-sm leading-relaxed" style={{ color: colors.text.secondary }}>
      "{testimonial.text}"
    </p>
  </div>
);

// Topic Card Component
const TopicCard = ({ topic, onBeginConsultation }) => (
  <div
    className="p-6 rounded-2xl transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
    style={{
      backgroundColor: '#FFFFFF',
      boxShadow: shadows.card,
      border: `1px solid ${colors.ui.borderDark}`,
    }}
  >
    <div className="flex items-start gap-4">
      <div
        className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: `${colors.teal.primary}15`, color: colors.teal.primary }}
      >
        {topic.icon}
      </div>
      <div className="flex-1">
        <h3 className="font-semibold text-lg mb-2" style={{ color: colors.text.dark }}>
          {topic.title}
        </h3>
        <p className="text-sm mb-4 leading-relaxed" style={{ color: colors.text.secondary }}>
          {topic.description}
        </p>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs" style={{ color: colors.text.muted }}>{topic.expertType}</p>
            <p className="text-sm font-semibold" style={{ color: colors.teal.dark }}>Starting {topic.startingPrice}</p>
          </div>
          <button
            onClick={() => onBeginConsultation(topic.id)}
            className="px-4 py-2 rounded-full text-sm font-medium transition-all hover:shadow-md"
            style={{
              backgroundColor: colors.teal.primary,
              color: '#FFFFFF',
            }}
            data-testid={`begin-consultation-${topic.id}`}
          >
            Begin consultation
          </button>
        </div>
      </div>
    </div>
  </div>
);

// Expert Card Component
const ExpertCard = ({ expert }) => (
  <div
    className="flex-shrink-0 w-64 p-5 rounded-2xl transition-all duration-300 hover:-translate-y-1"
    style={{
      backgroundColor: colors.cream.primary,
      boxShadow: shadows.card,
    }}
  >
    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-teal-100 to-teal-200 mb-3 flex items-center justify-center">
      <span className="text-2xl font-bold" style={{ color: colors.teal.dark }}>
        {expert.name.charAt(0)}
      </span>
    </div>
    <h4 className="font-semibold" style={{ color: colors.text.dark }}>{expert.name}</h4>
    <p className="text-xs mb-2" style={{ color: colors.text.muted }}>{expert.role}</p>
    <div className="flex items-center gap-1 mb-2">
      <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
      </svg>
      <span className="text-sm font-medium">{expert.rating}</span>
    </div>
    <p className="text-xs mb-2" style={{ color: colors.text.muted }}>{expert.languages}</p>
    <div className="flex flex-wrap gap-1">
      {expert.specialties.map((s, i) => (
        <span
          key={i}
          className="text-xs px-2 py-0.5 rounded-full"
          style={{ backgroundColor: `${colors.teal.primary}15`, color: colors.teal.dark }}
        >
          {s}
        </span>
      ))}
    </div>
    <div className="mt-3 flex items-center gap-1 text-xs" style={{ color: colors.peach.primary }}>
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
      Niro Certified
    </div>
  </div>
);

// Main Component
export default function PublicLandingPage({ 
  isAuthenticated = false,
  user = null,
  onLoginClick,
  onNavigateToApp,
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Handle Free Call CTA
  const handleFreeCallClick = () => {
    setUserIntent({ type: 'free_call' });
    if (isAuthenticated) {
      onNavigateToApp('schedule');
    } else {
      onLoginClick();
    }
  };

  // Handle Begin Consultation CTA
  const handleBeginConsultation = (topicId) => {
    setUserIntent({ type: 'consultation', topicId });
    if (isAuthenticated) {
      // Check if user has pack for this topic - handled in SimplifiedApp
      onNavigateToApp('topics', { topicId });
    } else {
      onLoginClick();
    }
  };

  // Scroll to section
  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.cream.primary, fontFamily: "'Lexend', sans-serif" }}>
      {/* Navigation */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 px-4 md:px-8 py-4"
        style={{
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          borderBottom: `1px solid ${colors.ui.borderDark}`,
        }}
      >
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          {/* Logo */}
          <a href="/" className="text-2xl font-bold" style={{ color: colors.teal.dark }}>
            niro
          </a>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center gap-8">
            <button onClick={() => scrollToSection('about')} className="text-sm font-medium transition-colors hover:text-teal-600" style={{ color: colors.text.secondary }}>
              About
            </button>
            <button onClick={() => scrollToSection('topics')} className="text-sm font-medium transition-colors hover:text-teal-600" style={{ color: colors.text.secondary }}>
              Life Topics
            </button>
            <button onClick={() => scrollToSection('experts')} className="text-sm font-medium transition-colors hover:text-teal-600" style={{ color: colors.text.secondary }}>
              Our Experts
            </button>
            <button onClick={() => scrollToSection('how')} className="text-sm font-medium transition-colors hover:text-teal-600" style={{ color: colors.text.secondary }}>
              How It Works
            </button>
          </div>

          {/* Desktop CTA & Auth */}
          <div className="hidden md:flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <button
                  onClick={() => onNavigateToApp('mypack')}
                  className="text-sm font-medium transition-colors hover:text-teal-600"
                  style={{ color: colors.text.secondary }}
                >
                  My Pack
                </button>
                <button
                  onClick={() => onNavigateToApp('profile')}
                  className="w-9 h-9 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: colors.teal.primary, color: '#FFFFFF' }}
                >
                  {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                </button>
              </>
            ) : null}
            <button
              onClick={handleFreeCallClick}
              className="px-5 py-2.5 rounded-full text-sm font-semibold transition-all hover:shadow-lg"
              style={{
                backgroundColor: colors.teal.primary,
                color: '#FFFFFF',
                boxShadow: shadows.button,
              }}
              data-testid="nav-free-call-btn"
            >
              Get a free 10 mins consultation
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2"
            style={{ color: colors.text.dark }}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t" style={{ borderColor: colors.ui.borderDark }}>
            <div className="flex flex-col gap-3 pt-4">
              <button onClick={() => scrollToSection('about')} className="text-left px-2 py-2 text-sm font-medium" style={{ color: colors.text.secondary }}>
                About
              </button>
              <button onClick={() => scrollToSection('topics')} className="text-left px-2 py-2 text-sm font-medium" style={{ color: colors.text.secondary }}>
                Life Topics
              </button>
              <button onClick={() => scrollToSection('experts')} className="text-left px-2 py-2 text-sm font-medium" style={{ color: colors.text.secondary }}>
                Our Experts
              </button>
              <button onClick={() => scrollToSection('how')} className="text-left px-2 py-2 text-sm font-medium" style={{ color: colors.text.secondary }}>
                How It Works
              </button>
              {isAuthenticated && (
                <>
                  <button onClick={() => onNavigateToApp('mypack')} className="text-left px-2 py-2 text-sm font-medium" style={{ color: colors.teal.primary }}>
                    My Pack
                  </button>
                  <button onClick={() => onNavigateToApp('astro')} className="text-left px-2 py-2 text-sm font-medium" style={{ color: colors.teal.primary }}>
                    Astro
                  </button>
                </>
              )}
              <button
                onClick={handleFreeCallClick}
                className="mt-2 px-5 py-3 rounded-full text-sm font-semibold text-center"
                style={{ backgroundColor: colors.teal.primary, color: '#FFFFFF' }}
              >
                Get a free 10 mins consultation
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section
        className="pt-24 pb-16 px-4 md:px-8"
        style={{
          background: `linear-gradient(180deg, ${colors.teal.primary} 0%, ${colors.teal.soft} 100%)`,
        }}
      >
        <div className="max-w-4xl mx-auto text-center pt-12 pb-8">
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6 leading-tight" style={{ color: '#FFFFFF' }}>
            Expert astrology guidance,{' '}
            <span style={{ fontStyle: 'italic', fontWeight: 400 }}>for as long as you need it.</span>
          </h1>
          <p className="text-base md:text-lg mb-8 max-w-2xl mx-auto" style={{ color: 'rgba(255,255,255,0.9)' }}>
            Experienced Vedic astrologers for your most important life decisions — with full support from first understanding to complete clarity.
          </p>

          {/* Trust Badges */}
          <div className="flex flex-wrap items-center justify-center gap-6 mb-8 text-sm" style={{ color: 'rgba(255,255,255,0.85)' }}>
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              Only 4.5+ rated astrologers
            </span>
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Unlimited chat with experts
            </span>
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Remedies execution support
            </span>
          </div>

          {/* Primary CTA */}
          <button
            onClick={handleFreeCallClick}
            className="inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-base transition-all hover:shadow-xl hover:-translate-y-0.5"
            style={{
              backgroundColor: colors.peach.primary,
              color: colors.text.dark,
              boxShadow: shadows.peach,
            }}
            data-testid="hero-free-call-btn"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
            </svg>
            Get Your Free 10-Min Call
          </button>
        </div>
      </section>

      {/* Testimonials Marquee */}
      <section className="py-12 overflow-hidden" style={{ backgroundColor: colors.cream.warm }}>
        <div className="mb-6 text-center">
          <p className="text-sm font-medium" style={{ color: colors.text.muted }}>Customer Feedback</p>
          <h2 className="text-xl md:text-2xl font-semibold mt-2" style={{ color: colors.text.dark }}>
            People found clarity on their biggest decisions.
          </h2>
        </div>
        <div className="flex gap-6 animate-marquee">
          {[...TESTIMONIALS, ...TESTIMONIALS].map((t, i) => (
            <TestimonialCard key={i} testimonial={t} />
          ))}
        </div>
      </section>

      {/* What We Offer Section */}
      <section id="about" className="py-16 px-4 md:px-8" style={{ backgroundColor: '#FFFFFF' }}>
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-sm font-medium mb-2" style={{ color: colors.teal.primary }}>What We Offer</p>
              <h2 className="text-2xl md:text-3xl font-bold mb-4 leading-tight" style={{ color: colors.text.dark }}>
                Guidance built around your <span style={{ fontStyle: 'italic' }}>situation,</span> not a clock.
              </h2>
              <p className="text-base" style={{ color: colors.text.secondary }}>
                Experienced Vedic astrologers who understand your situation — and stay with you from first understanding to resolution.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {OFFER_FEATURES.map((feature, i) => (
                <div
                  key={i}
                  className="p-4 rounded-xl transition-all hover:-translate-y-1"
                  style={{ backgroundColor: colors.cream.primary, boxShadow: shadows.card }}
                >
                  <span className="text-2xl mb-2 block">{feature.icon}</span>
                  <h4 className="font-medium text-sm" style={{ color: colors.text.dark }}>{feature.title}</h4>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Life Topics Section */}
      <section id="topics" className="py-16 px-4 md:px-8" style={{ backgroundColor: colors.cream.primary }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-sm font-medium mb-2" style={{ color: colors.teal.primary }}>Life Topics</p>
            <h2 className="text-2xl md:text-3xl font-bold" style={{ color: colors.text.dark }}>
              Choose the area of life you need clarity <span style={{ fontStyle: 'italic' }}>on today.</span>
            </h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {LIFE_TOPICS.map((topic) => (
              <TopicCard key={topic.id} topic={topic} onBeginConsultation={handleBeginConsultation} />
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how" className="py-16 px-4 md:px-8" style={{ backgroundColor: '#FFFFFF' }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-sm font-medium mb-2" style={{ color: colors.teal.primary }}>How It Works</p>
            <h2 className="text-2xl md:text-3xl font-bold" style={{ color: colors.text.dark }}>
              Your journey from confusion to <span style={{ fontStyle: 'italic' }}>clarity.</span>
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {STEPS.map((step) => (
              <div
                key={step.number}
                className="p-6 rounded-2xl transition-all hover:-translate-y-1"
                style={{ backgroundColor: '#FFFFFF', boxShadow: shadows.card, border: `1px solid ${colors.ui.borderDark}` }}
              >
                <span className="text-3xl font-bold" style={{ color: colors.teal.soft }}>{step.number}</span>
                <h3 className="font-semibold mt-2 mb-3" style={{ color: colors.text.dark }}>{step.title}</h3>
                <ul className="space-y-1">
                  {step.items.map((item, i) => (
                    <li key={i} className="text-sm" style={{ color: colors.text.secondary }}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Our Experts Section */}
      <section id="experts" className="py-16 px-4 md:px-8" style={{ backgroundColor: colors.cream.primary }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <p className="text-sm font-medium mb-2" style={{ color: colors.teal.primary }}>Our Experts</p>
            <h2 className="text-2xl md:text-3xl font-bold mb-2" style={{ color: colors.text.dark }}>
              Experienced astrologers, <span style={{ fontStyle: 'italic' }}>carefully selected.</span>
            </h2>
            <p className="text-sm" style={{ color: colors.text.secondary }}>
              Every expert is Niro Certified — evaluated for astrological knowledge, ethical practice, and communication clarity.
            </p>
          </div>
          <div className="flex gap-6 overflow-x-auto pb-4 -mx-4 px-4 scrollbar-hide">
            {EXPERTS.map((expert, i) => (
              <ExpertCard key={i} expert={expert} />
            ))}
            {/* View All Card */}
            <div
              className="flex-shrink-0 w-64 p-5 rounded-2xl flex flex-col items-center justify-center cursor-pointer transition-all hover:-translate-y-1"
              style={{
                border: `2px dashed ${colors.teal.soft}`,
                backgroundColor: 'transparent',
              }}
              onClick={() => isAuthenticated ? onNavigateToApp('experts') : onLoginClick()}
            >
              <div className="w-12 h-12 rounded-full flex items-center justify-center mb-3" style={{ backgroundColor: `${colors.teal.primary}15` }}>
                <svg className="w-6 h-6" style={{ color: colors.teal.primary }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
              <span className="font-medium text-sm" style={{ color: colors.teal.primary }}>View all</span>
              <span className="text-xs" style={{ color: colors.text.muted }}>certified experts</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 md:px-8" style={{ backgroundColor: colors.teal.dark }}>
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div>
              <a href="/" className="text-2xl font-bold" style={{ color: '#FFFFFF' }}>niro</a>
              <p className="mt-2 text-sm max-w-md" style={{ color: 'rgba(255,255,255,0.7)' }}>
                Niro provides astrology-based guidance across Vedic astrology and healing modalities. Our guidance is not a substitute for medical, legal, or financial advice.
              </p>
            </div>
            <div className="flex flex-col items-center md:items-end gap-4">
              {/* Social Icons */}
              <div className="flex items-center gap-4">
                <a href="#" className="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-white/10" style={{ color: 'rgba(255,255,255,0.7)' }}>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
                </a>
                <a href="#" className="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-white/10" style={{ color: 'rgba(255,255,255,0.7)' }}>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                </a>
                <a href="#" className="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-white/10" style={{ color: 'rgba(255,255,255,0.7)' }}>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                </a>
                <a href="#" className="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-white/10" style={{ color: 'rgba(255,255,255,0.7)' }}>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
                </a>
              </div>
              {/* Footer Links */}
              <div className="flex items-center gap-6 text-sm" style={{ color: 'rgba(255,255,255,0.7)' }}>
                <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
                <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
                <a href="#" className="hover:text-white transition-colors">Contact Us</a>
              </div>
            </div>
          </div>
        </div>
      </footer>

      {/* CSS for marquee animation */}
      <style>{`
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-marquee {
          animation: marquee 30s linear infinite;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
}
