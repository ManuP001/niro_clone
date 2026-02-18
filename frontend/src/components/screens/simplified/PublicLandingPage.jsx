import React, { useState } from 'react';

/**
 * PublicLandingPage - EXACT implementation of niro-final-marquee_1.html
 * This component matches the HTML file pixel-for-pixel
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

// Render star rating
const StarRating = ({ rating }) => {
  return '★'.repeat(rating) + '☆'.repeat(5 - rating);
};

export default function PublicLandingPage({ 
  isAuthenticated = false,
  user = null,
  onLoginClick,
  onNavigateToApp,
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Handle Free Call CTA
  const handleFreeCallClick = (e) => {
    e.preventDefault();
    setUserIntent({ type: 'free_call' });
    if (isAuthenticated) {
      onNavigateToApp('schedule');
    } else {
      onLoginClick();
    }
  };

  // Handle Begin Consultation CTA
  const handleBeginConsultation = (e, topicId) => {
    e.preventDefault();
    setUserIntent({ type: 'consultation', topicId });
    if (isAuthenticated) {
      onNavigateToApp('topics', { topicId });
    } else {
      onLoginClick();
    }
  };

  // Handle nav Begin button
  const handleNavBegin = (e) => {
    e.preventDefault();
    const topicsSection = document.getElementById('topics');
    if (topicsSection) {
      topicsSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      {/* Inline styles matching the exact HTML */}
      <style>{`
        :root {
          --teal: #4A9B8E;
          --teal-soft: #6AB3A6;
          --teal-dark: #2D5C4A;
          --peach: #E8A87C;
          --peach-soft: #F5C9A8;
          --cream: #FBF8F3;
          --cream-warm: #F5EFE7;
          --sand: #E8DFD1;
          --text-dark: #2D3748;
          --text-med: #5A6C7D;
          --text-light: #8F9BAA;
        }

        .landing-page * { margin: 0; padding: 0; box-sizing: border-box; }

        .landing-page {
          background: var(--cream);
          color: var(--text-dark);
          font-family: 'Lexend', -apple-system, system-ui, sans-serif;
          font-weight: 400;
          line-height: 1.6;
          -webkit-font-smoothing: antialiased;
        }

        /* NAV */
        .landing-nav {
          position: fixed;
          top: 0; left: 0; right: 0;
          z-index: 200;
          padding: 24px 64px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: rgba(251,248,243,0.95);
          backdrop-filter: blur(20px);
        }

        .landing-logo {
          font-family: 'Lexend', sans-serif;
          font-size: 24px;
          font-weight: 600;
          letter-spacing: 0.02em;
          color: var(--teal-dark);
          text-decoration: none;
        }

        .landing-nav ul {
          display: flex;
          gap: 40px;
          list-style: none;
          align-items: center;
        }

        .landing-nav a {
          text-decoration: none;
          color: var(--text-med);
          font-size: 15px;
          font-weight: 500;
          transition: color 0.3s;
        }

        .landing-nav a:hover { color: var(--teal); }

        .nav-btn {
          background: var(--teal) !important;
          color: white !important;
          padding: 12px 28px;
          font-size: 15px !important;
          border-radius: 100px;
          transition: all 0.3s !important;
        }

        .nav-btn:hover { 
          background: var(--teal-soft) !important;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(74,155,142,0.25);
        }

        /* HERO */
        .landing-hero {
          position: relative;
          min-height: 95vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 140px 32px 100px;
          background: linear-gradient(180deg, var(--cream) 0%, var(--cream-warm) 100%);
          overflow: hidden;
        }

        .landing-hero::before {
          content: '';
          position: absolute;
          top: -20%;
          left: 50%;
          transform: translateX(-50%);
          width: 600px;
          height: 600px;
          background: radial-gradient(circle, rgba(232,168,124,0.15) 0%, transparent 70%);
          border-radius: 50%;
        }

        .landing-hero::after {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          background-image: 
            radial-gradient(circle, rgba(74,155,142,0.08) 1px, transparent 1px),
            radial-gradient(circle, rgba(232,168,124,0.06) 1px, transparent 1px);
          background-size: 50px 50px, 80px 80px;
          background-position: 0 0, 40px 40px;
          opacity: 0.4;
          pointer-events: none;
        }

        .hero-shape {
          position: absolute;
          border-radius: 50%;
          opacity: 0.35;
          z-index: 1;
        }

        .shape-1 {
          width: 120px;
          height: 120px;
          background: linear-gradient(135deg, var(--peach-soft), var(--teal-soft));
          top: 15%;
          left: 8%;
          animation: float 6s ease-in-out infinite;
        }

        .shape-2 {
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, var(--teal-soft), var(--peach-soft));
          top: 25%;
          right: 12%;
          animation: float 8s ease-in-out infinite;
        }

        .shape-3 {
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, var(--peach), var(--teal));
          bottom: 20%;
          left: 15%;
          animation: float 7s ease-in-out infinite;
        }

        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }

        .landing-hero h1 {
          font-family: 'Lexend', sans-serif;
          font-size: clamp(56px, 8vw, 96px);
          font-weight: 800;
          line-height: 1.1;
          letter-spacing: -0.02em;
          color: var(--teal-dark);
          margin-bottom: 28px;
          max-width: 1000px;
          position: relative;
          z-index: 2;
        }

        .landing-hero h1 em {
          font-style: italic;
          color: var(--peach);
        }

        .hero-sub {
          font-size: 20px;
          line-height: 1.7;
          color: var(--text-med);
          max-width: 720px;
          margin: 0 auto 32px;
          font-weight: 400;
          position: relative;
          z-index: 2;
        }

        .hero-badges {
          display: flex;
          gap: 16px;
          flex-wrap: wrap;
          justify-content: center;
          margin-bottom: 48px;
          position: relative;
          z-index: 2;
        }

        .hero-badge {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          background: rgba(74,155,142,0.12);
          padding: 12px 24px;
          border-radius: 100px;
          border: 1.5px solid var(--teal);
          font-size: 15px;
          font-weight: 600;
          color: var(--teal-dark);
          white-space: nowrap;
        }

        .hero-badge svg {
          width: 20px;
          height: 20px;
          color: var(--teal);
          flex-shrink: 0;
        }

        .btn-free-call {
          display: inline-flex;
          align-items: center;
          gap: 12px;
          background: linear-gradient(135deg, var(--peach), var(--peach-soft));
          color: white;
          padding: 20px 64px;
          border-radius: 100px;
          font-size: 18px;
          font-weight: 700;
          text-decoration: none;
          transition: all 0.3s;
          box-shadow: 0 12px 32px rgba(232,168,124,0.35);
          position: relative;
          z-index: 2;
          cursor: pointer;
          border: none;
        }

        .btn-free-call:hover {
          transform: translateY(-2px);
          box-shadow: 0 16px 40px rgba(232,168,124,0.45);
        }

        .btn-free-call svg {
          width: 22px;
          height: 22px;
        }

        /* TESTIMONIAL MARQUEE */
        .testimonial-marquee {
          background: white;
          padding: 64px 0;
          overflow: hidden;
          position: relative;
        }

        .testimonial-marquee::before {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          background-image: radial-gradient(circle, rgba(74,155,142,0.04) 1px, transparent 1px);
          background-size: 60px 60px;
          opacity: 0.5;
          pointer-events: none;
        }

        .marquee-label {
          text-align: center;
          font-size: 13px;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: var(--peach);
          font-weight: 600;
          margin-bottom: 16px;
        }

        .marquee-title {
          text-align: center;
          font-size: clamp(28px, 4vw, 40px);
          font-weight: 700;
          color: var(--teal-dark);
          margin-bottom: 48px;
        }

        .marquee-container {
          display: flex;
          overflow: hidden;
          user-select: none;
          gap: 24px;
          mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
        }

        .marquee-content {
          display: flex;
          gap: 24px;
          animation: scroll 40s linear infinite;
          flex-shrink: 0;
        }

        .marquee-content:hover {
          animation-play-state: paused;
        }

        @keyframes scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }

        .marquee-card {
          background: var(--cream);
          border-radius: 24px;
          padding: 32px;
          min-width: 400px;
          max-width: 400px;
          flex-shrink: 0;
          box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        }

        .marquee-card-text {
          font-size: 15px;
          line-height: 1.7;
          color: var(--text-med);
          margin-bottom: 20px;
        }

        .marquee-card-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 20px;
          border-top: 2px solid var(--sand);
        }

        .marquee-card-author {
          font-size: 14px;
          font-weight: 700;
          color: var(--teal-dark);
          margin-bottom: 4px;
        }

        .marquee-card-topic {
          font-size: 12px;
          color: var(--text-light);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .marquee-card-rating {
          color: var(--peach);
          font-size: 16px;
          letter-spacing: 2px;
        }

        /* SECTIONS */
        .landing-section {
          padding: 100px 64px;
          position: relative;
        }

        .section-label {
          font-size: 13px;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: var(--peach);
          font-weight: 600;
          margin-bottom: 16px;
        }

        .landing-section h2 {
          font-family: 'Lexend', sans-serif;
          font-size: clamp(36px, 5vw, 56px);
          font-weight: 700;
          line-height: 1.2;
          color: var(--teal-dark);
          margin-bottom: 20px;
        }

        .landing-section h2 em { 
          font-style: italic; 
          color: var(--peach);
        }

        /* WHAT WE OFFER */
        .offer {
          background: var(--cream-warm);
        }

        .offer::before {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          background-image: radial-gradient(circle, rgba(232,168,124,0.05) 1.5px, transparent 1.5px);
          background-size: 70px 70px;
          opacity: 0.6;
          pointer-events: none;
        }

        .offer-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 80px;
          align-items: start;
          margin-top: 48px;
          position: relative;
          z-index: 1;
        }

        .offer-left p {
          font-size: 18px;
          line-height: 1.8;
          color: var(--text-med);
          margin-top: 20px;
        }

        .offer-features {
          display: grid;
          gap: 20px;
        }

        .offer-feature {
          background: white;
          padding: 24px 28px;
          border-radius: 24px;
          display: flex;
          align-items: center;
          gap: 20px;
          transition: all 0.3s;
          box-shadow: 0 4px 16px rgba(0,0,0,0.03);
        }

        .offer-feature:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(74,155,142,0.15);
        }

        .feature-icon {
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, var(--teal-soft), var(--teal));
          border-radius: 16px;
          flex-shrink: 0;
        }

        .offer-feature h4 {
          font-size: 17px;
          font-weight: 600;
          color: var(--teal-dark);
          line-height: 1.4;
        }

        /* TOPICS */
        .topics {
          background: white;
        }

        .topics::before {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          background-image: radial-gradient(circle, rgba(74,155,142,0.04) 1px, transparent 1px);
          background-size: 60px 60px;
          opacity: 0.5;
          pointer-events: none;
        }

        .topics-header {
          max-width: 720px;
          margin-bottom: 56px;
          position: relative;
          z-index: 1;
        }

        .topic-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 24px;
          position: relative;
          z-index: 1;
        }

        .topic-card {
          background: var(--cream);
          border-radius: 32px;
          padding: 36px;
          text-decoration: none;
          color: inherit;
          display: flex;
          flex-direction: column;
          transition: all 0.3s;
          box-shadow: 0 4px 20px rgba(0,0,0,0.04);
          cursor: pointer;
        }

        .topic-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 40px rgba(74,155,142,0.2);
        }

        .topic-header {
          display: flex;
          align-items: center;
          gap: 20px;
          margin-bottom: 16px;
        }

        .topic-icon {
          width: 64px;
          height: 64px;
          background: linear-gradient(135deg, var(--peach-soft), var(--peach));
          border-radius: 18px;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .topic-card h3 {
          font-size: 24px;
          font-weight: 600;
          color: var(--teal-dark);
          line-height: 1.3;
        }

        .topic-desc {
          font-size: 15px;
          line-height: 1.6;
          color: var(--text-med);
          margin-bottom: 20px;
        }

        .topic-meta {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
          margin-bottom: 20px;
          padding-top: 16px;
          border-top: 2px solid var(--sand);
        }

        .topic-expert {
          font-size: 13px;
          color: var(--text-light);
          font-weight: 500;
        }

        .topic-price {
          font-size: 18px;
          font-weight: 700;
          color: var(--teal);
          white-space: nowrap;
        }

        .topic-cta {
          display: block;
          background: var(--teal);
          color: white;
          text-align: center;
          padding: 14px;
          border-radius: 100px;
          font-size: 15px;
          font-weight: 600;
          transition: all 0.3s;
          border: none;
          cursor: pointer;
          width: 100%;
        }

        .topic-card:hover .topic-cta {
          background: var(--teal-soft);
          transform: translateY(-2px);
        }

        /* HOW IT WORKS */
        .journey {
          background: var(--cream-warm);
        }

        .journey::before {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          background-image: radial-gradient(circle, rgba(232,168,124,0.05) 1.5px, transparent 1.5px);
          background-size: 70px 70px;
          opacity: 0.6;
          pointer-events: none;
        }

        .journey-head {
          max-width: 720px;
          margin-bottom: 56px;
          position: relative;
          z-index: 1;
        }

        .steps {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 24px;
          position: relative;
          z-index: 1;
        }

        .step {
          background: white;
          padding: 32px 24px;
          border-radius: 28px;
          transition: all 0.3s;
          box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        }

        .step:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 40px rgba(74,155,142,0.15);
        }

        .step-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 24px;
        }

        .step-num {
          font-size: 48px;
          font-weight: 700;
          background: linear-gradient(135deg, var(--peach), var(--teal));
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          line-height: 1;
          flex-shrink: 0;
        }

        .step h3 {
          font-size: 20px;
          font-weight: 600;
          color: var(--teal-dark);
          line-height: 1.2;
        }

        .step-items {
          display: flex;
          flex-direction: column;
          gap: 14px;
        }

        .step-item {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 14px;
          line-height: 1.5;
          color: var(--text-med);
        }

        .step-item-icon {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          background: linear-gradient(135deg, rgba(232,168,124,0.2), var(--peach-soft));
        }

        .step-item-icon svg {
          width: 18px;
          height: 18px;
          color: var(--teal-dark);
        }

        /* PRACTITIONERS */
        .practitioners {
          background: white;
        }

        .practitioners::before {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          background-image: radial-gradient(circle, rgba(74,155,142,0.04) 1px, transparent 1px);
          background-size: 60px 60px;
          opacity: 0.5;
          pointer-events: none;
        }

        .practitioners-header {
          max-width: 720px;
          margin-bottom: 48px;
          position: relative;
          z-index: 1;
        }

        .practitioners-header p {
          font-size: 18px;
          color: var(--text-med);
          margin-top: 16px;
        }

        .practitioner-grid {
          display: flex;
          gap: 20px;
          overflow-x: auto;
          padding-bottom: 20px;
          -webkit-overflow-scrolling: touch;
          position: relative;
          z-index: 1;
        }

        .practitioner-card {
          background: var(--cream);
          border-radius: 28px;
          padding: 32px;
          display: flex;
          flex-direction: column;
          transition: all 0.3s;
          min-width: 320px;
          flex-shrink: 0;
          box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        }

        .practitioner-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 40px rgba(232,168,124,0.2);
        }

        .practitioner-header {
          display: flex;
          gap: 20px;
          margin-bottom: 20px;
        }

        .practitioner-avatar {
          width: 68px;
          height: 68px;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--teal-soft), var(--teal));
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          box-shadow: 0 4px 12px rgba(74,155,142,0.2);
        }

        .practitioner-name {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 6px;
          color: var(--teal-dark);
        }

        .practitioner-role {
          font-size: 14px;
          color: var(--text-med);
          font-weight: 500;
        }

        .practitioner-stats {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 16px;
        }

        .star-icon {
          color: var(--peach);
          font-size: 16px;
        }

        .rating-number {
          font-size: 16px;
          font-weight: 700;
          color: var(--text-dark);
        }

        .practitioner-languages {
          font-size: 13px;
          color: var(--text-light);
          margin-bottom: 16px;
          font-weight: 500;
        }

        .practitioner-specialties {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 20px;
        }

        .specialty-tag {
          font-size: 12px;
          padding: 6px 14px;
          background: white;
          border-radius: 100px;
          color: var(--text-med);
          font-weight: 500;
        }

        .niro-certified {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          background: linear-gradient(135deg, var(--peach-soft), var(--peach));
          border-radius: 100px;
          padding: 10px 20px;
          align-self: flex-start;
          margin-top: auto;
          box-shadow: 0 4px 12px rgba(232,168,124,0.2);
        }

        .certified-text {
          font-size: 12px;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: white;
          font-weight: 700;
        }

        .view-all-card {
          background: white;
          border-radius: 28px;
          border: 3px dashed var(--sand);
          min-width: 280px;
          flex-shrink: 0;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 48px 32px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .view-all-card:hover {
          border-color: var(--peach);
          background: var(--cream);
          transform: translateY(-4px);
        }

        .view-all-text {
          font-size: 16px;
          font-weight: 600;
          color: var(--teal-dark);
          text-align: center;
          line-height: 1.5;
        }

        /* FOOTER */
        .landing-footer {
          padding: 48px 64px;
          background: var(--cream-warm);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .footer-logo {
          font-family: 'Lexend', sans-serif;
          font-size: 22px;
          font-weight: 600;
          letter-spacing: 0.02em;
          color: var(--teal-dark);
          text-decoration: none;
        }

        .footer-note {
          font-size: 13px;
          color: var(--text-light);
          max-width: 550px;
          text-align: right;
          line-height: 1.7;
        }

        /* MOBILE MENU */
        .mobile-menu-btn {
          display: none;
          background: none;
          border: none;
          cursor: pointer;
          padding: 8px;
        }

        /* RESPONSIVE */
        @media (max-width: 960px) {
          .landing-nav { padding: 20px 24px; }
          .landing-nav ul { display: none; }
          .mobile-menu-btn { display: block; }
          .landing-section { padding: 72px 24px; }
          .landing-hero { padding: 130px 24px 90px; }
          .hero-badges { flex-direction: column; align-items: center; gap: 12px; }
          .hero-badge { font-size: 13px; padding: 10px 18px; gap: 8px; }
          .hero-badge svg { width: 16px; height: 16px; }
          .testimonial-marquee { padding: 48px 24px; }
          .marquee-card { min-width: 320px; max-width: 320px; }
          .offer-grid { grid-template-columns: 1fr; gap: 48px; }
          .topic-grid { grid-template-columns: 1fr; }
          .topic-header { gap: 16px; }
          .steps { grid-template-columns: 1fr; }
          .step-header { gap: 12px; }
          .step-num { font-size: 40px; }
          .landing-footer { 
            flex-direction: column; 
            gap: 24px; 
            padding: 40px 24px; 
            text-align: center; 
          }
          .footer-note { text-align: center; }
        }

        /* Mobile menu dropdown */
        .mobile-menu {
          display: none;
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: white;
          padding: 24px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }

        .mobile-menu.open {
          display: block;
        }

        .mobile-menu a {
          display: block;
          padding: 12px 0;
          color: var(--text-med);
          text-decoration: none;
          font-size: 16px;
          font-weight: 500;
        }

        .mobile-menu a:hover {
          color: var(--teal);
        }

        .mobile-menu .nav-btn {
          display: block;
          text-align: center;
          margin-top: 16px;
        }
      `}</style>

      <div className="landing-page">
        {/* NAV */}
        <nav className="landing-nav">
          <a href="/" className="landing-logo">niro</a>
          <ul>
            <li><a href="#about">About</a></li>
            <li><a href="#topics">Life Topics</a></li>
            <li><a href="#experts">Our Experts</a></li>
            <li><a href="#how">How It Works</a></li>
            {isAuthenticated && (
              <>
                <li><a href="#" onClick={(e) => { e.preventDefault(); onNavigateToApp('mypack'); }}>My Pack</a></li>
                <li><a href="#" onClick={(e) => { e.preventDefault(); onNavigateToApp('astro'); }}>Astro</a></li>
              </>
            )}
            <li>
              <a 
                href="#topics" 
                className="nav-btn"
                onClick={handleNavBegin}
                data-testid="nav-begin-btn"
              >
                Get a free 10 mins consultation
              </a>
            </li>
          </ul>
          <button 
            className="mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {mobileMenuOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
          <div className={`mobile-menu ${mobileMenuOpen ? 'open' : ''}`}>
            <a href="#about" onClick={() => setMobileMenuOpen(false)}>About</a>
            <a href="#topics" onClick={() => setMobileMenuOpen(false)}>Life Topics</a>
            <a href="#experts" onClick={() => setMobileMenuOpen(false)}>Our Experts</a>
            <a href="#how" onClick={() => setMobileMenuOpen(false)}>How It Works</a>
            {isAuthenticated && (
              <>
                <a href="#" onClick={(e) => { e.preventDefault(); onNavigateToApp('mypack'); setMobileMenuOpen(false); }}>My Pack</a>
                <a href="#" onClick={(e) => { e.preventDefault(); onNavigateToApp('astro'); setMobileMenuOpen(false); }}>Astro</a>
              </>
            )}
            <a 
              href="#topics" 
              className="nav-btn"
              onClick={(e) => { handleNavBegin(e); setMobileMenuOpen(false); }}
            >
              Get a free 10 mins consultation
            </a>
          </div>
        </nav>

        {/* HERO */}
        <section className="landing-hero">
          <div className="hero-shape shape-1"></div>
          <div className="hero-shape shape-2"></div>
          <div className="hero-shape shape-3"></div>

          <h1>Expert astrology guidance,<br/><em>for as long as you need it.</em></h1>

          <p className="hero-sub">
            Experienced Vedic astrologers for your most important life decisions — with full support from first understanding to complete clarity.
          </p>

          <div className="hero-badges">
            <div className="hero-badge">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              Only 4.5+ rated astrologers
            </div>
            <div className="hero-badge">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
              </svg>
              Unlimited chat with experts
            </div>
            <div className="hero-badge">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              Remedies execution support
            </div>
          </div>

          <button 
            className="btn-free-call"
            onClick={handleFreeCallClick}
            data-testid="hero-free-call-btn"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/>
            </svg>
            Get Your Free 10-Min Call
          </button>
        </section>

        {/* TESTIMONIALS MARQUEE */}
        <section className="testimonial-marquee">
          <p className="marquee-label">Customer Feedback</p>
          <h2 className="marquee-title">People found clarity on their biggest decisions.</h2>
          
          <div className="marquee-container">
            <div className="marquee-content">
              {[...TESTIMONIALS, ...TESTIMONIALS].map((t, i) => (
                <div key={i} className="marquee-card">
                  <p className="marquee-card-text">"{t.text}"</p>
                  <div className="marquee-card-footer">
                    <div>
                      <div className="marquee-card-author">{t.author}</div>
                      <div className="marquee-card-topic">{t.topic}</div>
                    </div>
                    <div className="marquee-card-rating">
                      <StarRating rating={t.rating} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* WHAT WE OFFER */}
        <section className="landing-section offer" id="about">
          <p className="section-label">What We Offer</p>
          <div className="offer-grid">
            <div className="offer-left">
              <h2>Guidance built around<br/>your <em>situation,</em><br/>not a clock.</h2>
              <p>
                Experienced Vedic astrologers who understand your situation — and stay with you from first understanding to resolution.
              </p>
            </div>
            <div className="offer-features">
              <div className="offer-feature">
                <div className="feature-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="9" stroke="white" strokeWidth="2"/>
                    <circle cx="12" cy="12" r="3" fill="white"/>
                  </svg>
                </div>
                <h4>Curated, Verified Astrologers</h4>
              </div>
              <div className="offer-feature">
                <div className="feature-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <rect x="4" y="4" width="16" height="16" stroke="white" strokeWidth="2"/>
                    <line x1="4" y1="4" x2="12" y2="12" stroke="white" strokeWidth="1.5"/>
                    <line x1="20" y1="4" x2="12" y2="12" stroke="white" strokeWidth="1.5"/>
                  </svg>
                </div>
                <h4>Situation-Based Packages</h4>
              </div>
              <div className="offer-feature">
                <div className="feature-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke="white" strokeWidth="2"/>
                  </svg>
                </div>
                <h4>Unlimited Chat Till Clarity</h4>
              </div>
              <div className="offer-feature">
                <div className="feature-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2 L20 20 L4 20 Z" stroke="white" strokeWidth="2" fill="none"/>
                    <line x1="12" y1="9" x2="12" y2="14" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                    <circle cx="12" cy="16.5" r="1" fill="white"/>
                  </svg>
                </div>
                <h4>No Fear, No Pressure</h4>
              </div>
              <div className="offer-feature">
                <div className="feature-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke="white" strokeWidth="2" fill="none"/>
                  </svg>
                </div>
                <h4>End-to-end Support in Remedies Execution</h4>
              </div>
            </div>
          </div>
        </section>

        {/* LIFE TOPICS */}
        <section className="landing-section topics" id="topics">
          <div className="topics-header">
            <p className="section-label">Life Topics</p>
            <h2>Choose the area of life<br/>you need clarity <em>on today.</em></h2>
          </div>

          <div className="topic-grid">
            {/* Career */}
            <div className="topic-card" onClick={(e) => handleBeginConsultation(e, 'career')}>
              <div className="topic-header">
                <div className="topic-icon">
                  <svg width="36" height="36" viewBox="0 0 40 40" fill="none">
                    <circle cx="20" cy="20" r="6" stroke="white" strokeWidth="2.5" fill="none"/>
                    <line x1="8" y1="14" x2="32" y2="14" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                    <line x1="8" y1="26" x2="32" y2="26" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                  </svg>
                </div>
                <h3>Career, Money & Business</h3>
              </div>
              <p className="topic-desc">
                For major professional transitions, business decisions, and understanding what path aligns with your strengths.
              </p>
              <div className="topic-meta">
                <span className="topic-expert">Vedic Astrologer · Career Timing</span>
                <span className="topic-price">Starting ₹2,999</span>
              </div>
              <button className="topic-cta" data-testid="begin-consultation-career">Begin consultation</button>
            </div>

            {/* Health */}
            <div className="topic-card" onClick={(e) => handleBeginConsultation(e, 'health')}>
              <div className="topic-header">
                <div className="topic-icon">
                  <svg width="36" height="36" viewBox="0 0 40 40" fill="none">
                    <circle cx="20" cy="20" r="7" fill="white"/>
                    <line x1="20" y1="5" x2="20" y2="9" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                    <line x1="20" y1="31" x2="20" y2="35" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                    <line x1="5" y1="20" x2="9" y2="20" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                    <line x1="31" y1="20" x2="35" y2="20" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                  </svg>
                </div>
                <h3>Health & Wellness</h3>
              </div>
              <p className="topic-desc">
                For periods of low energy, emotional heaviness, or feeling stuck — through understanding your cycles.
              </p>
              <div className="topic-meta">
                <span className="topic-expert">Vedic Astrologer + Healer</span>
                <span className="topic-price">Starting ₹2,999</span>
              </div>
              <button className="topic-cta" data-testid="begin-consultation-health">Begin consultation</button>
            </div>

            {/* Love */}
            <div className="topic-card" onClick={(e) => handleBeginConsultation(e, 'love')}>
              <div className="topic-header">
                <div className="topic-icon">
                  <svg width="36" height="36" viewBox="0 0 40 40" fill="none">
                    <circle cx="20" cy="17" r="7" stroke="white" strokeWidth="2.5" fill="none"/>
                    <line x1="20" y1="24" x2="20" y2="35" stroke="white" strokeWidth="2.5"/>
                    <line x1="15" y1="31" x2="25" y2="31" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                  </svg>
                </div>
                <h3>Love, Marriage & Relationships</h3>
              </div>
              <p className="topic-desc">
                For decisions about compatibility, timing, and relationship clarity when you need the right choice.
              </p>
              <div className="topic-meta">
                <span className="topic-expert">Vedic Astrologer · Compatibility</span>
                <span className="topic-price">Starting ₹3,999</span>
              </div>
              <button className="topic-cta" data-testid="begin-consultation-love">Begin consultation</button>
            </div>

            {/* Fertility */}
            <div className="topic-card" onClick={(e) => handleBeginConsultation(e, 'fertility')}>
              <div className="topic-header">
                <div className="topic-icon">
                  <svg width="36" height="36" viewBox="0 0 40 40" fill="none">
                    <path d="M 20 7 A 11 11 0 0 1 20 33 A 15 15 0 0 0 20 7 Z" fill="white"/>
                  </svg>
                </div>
                <h3>Fertility & Family Planning</h3>
              </div>
              <p className="topic-desc">
                For understanding timing, readiness, and navigating the emotional journey toward parenthood.
              </p>
              <div className="topic-meta">
                <span className="topic-expert">Vedic Astrologer · Fertility Timing</span>
                <span className="topic-price">Starting ₹3,999</span>
              </div>
              <button className="topic-cta" data-testid="begin-consultation-fertility">Begin consultation</button>
            </div>
          </div>

          {/* See More Life Topics CTA */}
          <div className="see-more-topics">
            <button 
              className="see-more-btn"
              onClick={handleSeeMoreTopics}
              data-testid="see-more-life-topics-btn"
            >
              <span>See More life topics</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </button>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section className="landing-section journey" id="how">
          <div className="journey-head">
            <p className="section-label">How It Works</p>
            <h2>Your journey from<br/>confusion to <em>clarity.</em></h2>
          </div>
          <div className="steps">
            <div className="step">
              <div className="step-header">
                <div className="step-num">01</div>
                <h3>Choose & Book</h3>
              </div>
              <div className="step-items">
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                      <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
                    </svg>
                  </div>
                  <span>Pick your life topic</span>
                </div>
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                      <circle cx="12" cy="7" r="4"/>
                    </svg>
                  </div>
                  <span>Share birth details</span>
                </div>
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                      <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
                      <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                  </div>
                  <span>Book a time slot</span>
                </div>
              </div>
            </div>
            <div className="step">
              <div className="step-header">
                <div className="step-num">02</div>
                <h3>Your Session</h3>
              </div>
              <div className="step-items">
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <path d="M12 6v6l4 2"/>
                    </svg>
                  </div>
                  <span>Deep dive into your chart</span>
                </div>
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  </div>
                  <span>Clarity on your situation</span>
                </div>
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                  </div>
                  <span>Timing guidance for action</span>
                </div>
              </div>
            </div>
            <div className="step">
              <div className="step-header">
                <div className="step-num">03</div>
                <h3>Stay Supported</h3>
              </div>
              <div className="step-items">
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
                    </svg>
                  </div>
                  <span>Unlimited chat access</span>
                </div>
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                      <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
                    </svg>
                  </div>
                  <span>Scheduled follow-ups</span>
                </div>
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                  </div>
                  <span>Till you find clarity</span>
                </div>
              </div>
            </div>
            <div className="step">
              <div className="step-header">
                <div className="step-num">04</div>
                <h3>Remedies Execution</h3>
              </div>
              <div className="step-items">
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                    </svg>
                  </div>
                  <span>If recommended by expert</span>
                </div>
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                      <circle cx="8.5" cy="7" r="4"/>
                      <line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/>
                    </svg>
                  </div>
                  <span>Verified service partners</span>
                </div>
                <div className="step-item">
                  <div className="step-item-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  </div>
                  <span>Full transparency & proof</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* PRACTITIONERS */}
        <section className="landing-section practitioners" id="experts">
          <div className="practitioners-header">
            <p className="section-label">Our Experts</p>
            <h2>Experienced astrologers,<br/><em>carefully selected.</em></h2>
            <p>Every expert is Niro Certified — evaluated for astrological knowledge, ethical practice, and communication clarity.</p>
          </div>

          <div className="practitioner-grid">
            {[
              { name: 'Prakash Jha', role: 'Vedic Astrologer, Tarot Reader', rating: 4.8, languages: 'Hindi, English', specialties: ['Career timing', 'Job changes', 'Relationship'] },
              { name: 'Sanjai Maharaj', role: 'Vedic Astrologer', rating: 4.9, languages: 'Hindi, English, Marathi', specialties: ['Marriage timing', 'Compatibility', 'Family'] },
              { name: 'Pooja Kapoor', role: 'Vedic Astrologer, Healer', rating: 4.7, languages: 'Hindi, English', specialties: ['Gemstones', 'Pooja', 'Chakra healing'] },
              { name: 'Vikram Rao', role: 'Vedic Astrologer', rating: 4.8, languages: 'Hindi, English, Telugu', specialties: ['Business', 'Finance', 'Career'] },
            ].map((expert, i) => (
              <div key={i} className="practitioner-card">
                <div className="practitioner-header">
                  <div className="practitioner-avatar">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5" opacity="0.6">
                      <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                      <circle cx="12" cy="7" r="4"/>
                    </svg>
                  </div>
                  <div>
                    <div className="practitioner-name">{expert.name}</div>
                    <div className="practitioner-role">{expert.role}</div>
                  </div>
                </div>
                <div className="practitioner-stats">
                  <span className="star-icon">★</span>
                  <span className="rating-number">{expert.rating}</span>
                </div>
                <div className="practitioner-languages">{expert.languages}</div>
                <div className="practitioner-specialties">
                  {expert.specialties.map((s, j) => (
                    <span key={j} className="specialty-tag">{s}</span>
                  ))}
                </div>
                <div className="niro-certified">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <span className="certified-text">Niro Certified</span>
                </div>
              </div>
            ))}
            
            <div 
              className="view-all-card"
              onClick={() => isAuthenticated ? onNavigateToApp('experts') : onLoginClick()}
            >
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#4A9B8E" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 8 16 12 12 16"/>
                <line x1="8" y1="12" x2="16" y2="12"/>
              </svg>
              <span className="view-all-text">View all<br/>certified experts</span>
            </div>
          </div>
        </section>

        {/* FOOTER */}
        <footer className="landing-footer">
          <a href="/" className="footer-logo">niro</a>
          <p className="footer-note">
            Niro provides astrology-based guidance across Vedic astrology and healing modalities. Our guidance is not a substitute for medical, legal, or financial advice.
          </p>
        </footer>
      </div>
    </>
  );
}
