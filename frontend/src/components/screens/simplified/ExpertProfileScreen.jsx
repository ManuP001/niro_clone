import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { apiSimplified, trackEvent } from './utils';
import { getBackendUrl } from '../../../config';
import { colors, shadows } from './theme';
import NiroCertifiedBadge from './NiroCertifiedBadge';

const resolvePhotoUrl = (url) => {
  if (!url) return null;
  if (url.startsWith('/')) return `${getBackendUrl()}${url}`;
  return url;
};

/**
 * ExpertProfileScreen V4 — redesigned to match Niro mockups.
 *
 * Layout:
 *  A. Full-width hero photo with gradient overlay, back btn, Niro badge
 *  B. Name + tagline
 *  C. Info card (experience, credentials, languages, location)
 *  D. "Know Your Astrologer" gallery (if gallery_photos set)
 *  E. Bio
 *  F. Quote card (if quote set)
 *  G. Consultation options inline (free call card + paid sessions)
 *  H. Packages fallback (if no consultations)
 *  I. Remedies
 *  J. Floating "Consult Astrologer" CTA → scrolls to consultations section
 */
export default function ExpertProfileScreen({
  token, expertId: propExpertId, userState, onNavigate, onBack,
  hasBottomNav, onTabChange, isAuthenticated, user, onLoginClick,
  wizardMode = false, wizardTopicId, onBookFreeCall, onBuyPackage,
}) {
  const params = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const expertId = propExpertId || params.expertId;
  const topicId = wizardTopicId || searchParams.get('topicId') || null;

  const [expert, setExpert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expertRemedies, setExpertRemedies] = useState([]);
  const [packages, setPackages] = useState([]);
  const [showBottomSheet, setShowBottomSheet] = useState(false);

  // Fetch expert data
  useEffect(() => {
    if (!expertId) return;
    const load = async () => {
      try {
        const res = await apiSimplified.get(`/experts/${expertId}`, token);
        setExpert(res.expert || null);
        trackEvent('expert_profile_viewed', { expert_id: expertId, flow_version: 'simplified_v4' }, token);
      } catch (err) {
        console.error('Failed to load expert:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [expertId, token]);

  // Fetch remedies
  useEffect(() => {
    if (!expertId) return;
    apiSimplified.get(`/experts/${expertId}/remedies`, token)
      .then(res => setExpertRemedies(res.remedies || []))
      .catch(() => setExpertRemedies([]));
  }, [expertId, token]);

  // Fetch packages (used as fallback when no consultations configured)
  useEffect(() => {
    if (!expertId) return;
    const url = topicId
      ? `/experts/${expertId}/packages?topic_id=${topicId}`
      : `/experts/${expertId}/packages`;
    apiSimplified.get(url, token)
      .then(res => setPackages(res.packages || []))
      .catch(() => setPackages([]));
  }, [expertId, topicId, token]);

  const handleBack = () => {
    if (onBack) onBack();
    else navigate(-1);
  };

  // Free call → scheduling directly. Paid → checkout → scheduling.
  // Auth check is handled by PublicAppLayout.handleNavigate — it will store the expert URL
  // as the post-login redirect so the user returns here after signing in.
  const handleConsultationClick = (consultation) => {
    if (!expert) return;
    if (!consultation || consultation.price_inr === 0 || consultation.is_free) {
      if (wizardMode && onBookFreeCall) { onBookFreeCall(); return; }
      onNavigate?.('schedule', { expertId: expert.expert_id, expertName: expert.name });
      return;
    }
    onNavigate?.('schedule', { expertId: expert.expert_id, expertName: expert.name, consultation });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: colors.background.primary }}>
        <div
          className="w-12 h-12 border-4 rounded-full animate-spin"
          style={{ borderColor: `${colors.teal.primary}30`, borderTopColor: colors.teal.primary }}
        />
      </div>
    );
  }

  if (!expert) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: colors.background.primary }}>
        <div className="text-center">
          <p style={{ color: colors.text.dark }}>Expert not found</p>
          <button onClick={handleBack} className="mt-4 font-medium" style={{ color: colors.teal.primary }}>Go back</button>
        </div>
      </div>
    );
  }

  const years = expert.experience_years || expert.years_experience;
  const languages = Array.isArray(expert.languages) ? expert.languages.join(', ') : expert.languages;
  const hasConsultations = (expert.consultations || []).length > 0 || expert.offers_free_call;

  return (
    <div
      className={`min-h-screen ${hasBottomNav ? 'pb-32 md:pb-28' : 'pb-28'}`}
      style={{ backgroundColor: colors.background.primary }}
    >

      {/* ── A. Hero photo ──────────────────────────────────────────── */}
      <div className="relative w-full" style={{ height: 380 }}>
        {expert.photo_url ? (
          <img
            src={resolvePhotoUrl(expert.photo_url)}
            alt={expert.name}
            className="absolute inset-0 w-full h-full object-cover"
            style={{ objectPosition: 'center 15%' }}
          />
        ) : (
          <div
            className="absolute inset-0 flex items-center justify-center text-8xl font-bold"
            style={{ backgroundColor: colors.teal.soft, color: colors.teal.primary }}
          >
            {expert.name?.charAt(0) || '?'}
          </div>
        )}
        {/* Gradient overlay: transparent → page background */}
        <div
          className="absolute inset-0"
          style={{ background: `linear-gradient(to bottom, transparent 55%, ${colors.background.primary} 100%)` }}
        />
        {/* Back button */}
        <button
          onClick={handleBack}
          className="absolute top-4 left-4 w-10 h-10 rounded-full flex items-center justify-center z-10"
          style={{ backgroundColor: 'rgba(0,0,0,0.45)', backdropFilter: 'blur(4px)' }}
          aria-label="Go back"
        >
          <svg width="20" height="20" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        {/* Niro Certified badge */}
        <div className="absolute top-4 right-4 z-10">
          <NiroCertifiedBadge size="md" />
        </div>
      </div>

      {/* ── B. Name + tagline ──────────────────────────────────────── */}
      <div className="px-5 -mt-4 relative z-10 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold leading-tight" style={{ color: colors.text.dark }}>
          {expert.name}
        </h1>
        <p className="text-sm mt-1" style={{ color: colors.text.secondary }}>
          {expert.tagline || expert.modality_label}
        </p>
      </div>

      {/* ── C. Info card ───────────────────────────────────────────── */}
      <div className="px-4 mt-4 max-w-2xl mx-auto">
        <div className="rounded-2xl overflow-hidden" style={{ backgroundColor: colors.teal.dark || '#2D5C4A' }}>
          {/* Modalities / specialties */}
          {expert.modality_label ? (
            <div className="flex items-start gap-3 px-4 py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
              <span className="text-base mt-0.5">✦</span>
              <span className="text-sm font-medium text-white">{expert.modality_label}</span>
            </div>
          ) : null}
          {years ? (
            <div className="flex items-center gap-3 px-4 py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
              <span className="text-base">⊙</span>
              <span className="text-sm font-medium text-white">{years}+ years of experience</span>
            </div>
          ) : null}
          {expert.credentials ? (
            <div className="flex items-start gap-3 px-4 py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
              <span className="text-base mt-0.5">🎓</span>
              <span className="text-sm" style={{ color: 'rgba(255,255,255,0.88)' }}>{expert.credentials}</span>
            </div>
          ) : null}
          {languages ? (
            <div
              className="flex items-center gap-3 px-4 py-3"
              style={{ borderBottom: (expert.location ? '1px solid rgba(255,255,255,0.1)' : 'none') }}
            >
              <span className="text-base">💬</span>
              <span className="text-sm" style={{ color: 'rgba(255,255,255,0.88)' }}>{languages}</span>
            </div>
          ) : null}
          {expert.location ? (
            <div className="flex items-center gap-3 px-4 py-3">
              <span className="text-base">📍</span>
              <span className="text-sm" style={{ color: 'rgba(255,255,255,0.88)' }}>{expert.location}</span>
            </div>
          ) : null}
        </div>
      </div>

      {/* ── D. "Know Your Astrologer" gallery ──────────────────────── */}
      {(expert.gallery_photos || []).length > 0 && (
        <div className="mt-6 max-w-2xl mx-auto">
          <p className="px-5 text-xs font-bold tracking-widest uppercase mb-3" style={{ color: colors.text.muted }}>
            Know Your Astrologer
          </p>
          <div className="flex gap-3 overflow-x-auto px-5 pb-1 scrollbar-hide">
            {expert.gallery_photos.map((photo, idx) => (
              <div key={idx} className="flex-shrink-0 relative rounded-xl overflow-hidden" style={{ width: 160, height: 200 }}>
                <img
                  src={resolvePhotoUrl(photo.url)}
                  alt={photo.caption || ''}
                  className="w-full h-full object-cover"
                />
                {photo.caption && (
                  <div
                    className="absolute bottom-0 left-0 right-0 px-2 py-1.5"
                    style={{ background: 'linear-gradient(transparent, rgba(0,0,0,0.72))' }}
                  >
                    <p className="text-white text-[10px] leading-tight">{photo.caption}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── E. Bio ─────────────────────────────────────────────────── */}
      {(expert.short_bio || expert.bio) && (
        <div className="px-5 mt-6 max-w-2xl mx-auto">
          <h3 className="font-semibold mb-2 text-sm" style={{ color: colors.text.dark }}>About {expert.name}</h3>
          <div className="space-y-3">
            {(expert.short_bio || expert.bio).split(/\n\n|\n/).filter(p => p.trim()).map((para, i) => (
              <p key={i} className="text-sm leading-relaxed" style={{ color: colors.text.secondary }}>
                {para.trim()}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* ── F. Quote card ──────────────────────────────────────────── */}
      {expert.quote && (
        <div className="px-5 mt-5 max-w-2xl mx-auto">
          <div
            className="rounded-2xl px-5 py-5 text-center"
            style={{ backgroundColor: `${colors.teal.primary}08`, border: `1px solid ${colors.teal.primary}20` }}
          >
            <div className="text-4xl font-serif leading-none mb-2" style={{ color: `${colors.teal.primary}60` }}>"</div>
            <p className="text-sm italic leading-relaxed" style={{ color: colors.text.secondary }}>
              {expert.quote}
            </p>
          </div>
        </div>
      )}

      {/* ── G. Packages fallback (when no consultations) ───────── */}
      {!hasConsultations && packages.length > 0 && (
        <div className="px-5 mt-6 max-w-2xl mx-auto">
          <h3 className="font-semibold mb-3 text-base" style={{ color: colors.text.dark }}>Packages</h3>
          <div className="space-y-3">
            {packages.map((pkg) => (
              <button
                key={pkg.tier_id}
                onClick={() => {
                  if (!isAuthenticated) { onLoginClick?.(); return; }
                  if (onBuyPackage) onBuyPackage(pkg);
                  else onNavigate?.('packageLanding', { packageId: pkg.tier_id });
                }}
                className="w-full text-left rounded-2xl p-4 transition-all active:scale-[0.99] hover:shadow-sm relative overflow-hidden"
                style={{ backgroundColor: colors.peach.soft, border: `1px solid ${colors.ui.borderDark}` }}
              >
                {pkg.popular && (
                  <span className="absolute top-2 right-2 text-[10px] font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: colors.teal.primary, color: '#fff' }}>
                    Popular
                  </span>
                )}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm" style={{ color: colors.text.dark }}>{pkg.name}</p>
                    {pkg.description && (
                      <p className="text-xs mt-1 line-clamp-2" style={{ color: colors.text.secondary }}>{pkg.description}</p>
                    )}
                    <div className="flex flex-wrap gap-2 mt-2">
                      {pkg.calls_included > 0 && (
                        <span className="text-[11px] px-2 py-0.5 rounded-full" style={{ backgroundColor: `${colors.teal.primary}15`, color: colors.teal.dark }}>
                          {pkg.calls_included} session{pkg.calls_included > 1 ? 's' : ''}
                        </span>
                      )}
                      {pkg.duration_days > 0 && (
                        <span className="text-[11px] px-2 py-0.5 rounded-full" style={{ backgroundColor: `${colors.teal.primary}15`, color: colors.teal.dark }}>
                          {pkg.duration_days} days
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <p className="font-bold text-base" style={{ color: colors.teal.primary }}>
                      ₹{pkg.price_inr?.toLocaleString('en-IN')}
                    </p>
                    <p className="text-xs" style={{ color: colors.text.muted }}>Get pack →</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── I. Remedies ────────────────────────────────────────────── */}
      {expertRemedies.length > 0 && (
        <div className="px-5 mt-6 max-w-2xl mx-auto">
          <h3 className="font-semibold mb-3 text-base" style={{ color: colors.text.dark }}>Remedies &amp; rituals</h3>
          <div className="space-y-3">
            {expertRemedies.map((remedy) => (
              <button
                key={remedy.remedy_id}
                onClick={() => onNavigate?.('remedies')}
                className="w-full text-left rounded-2xl p-4 transition-all active:scale-[0.99] hover:shadow-sm"
                style={{ backgroundColor: '#FFF8F0', border: `1px solid ${colors.ui.borderDark}` }}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <span className="text-2xl flex-shrink-0">{remedy.image}</span>
                    <div className="min-w-0">
                      <p className="font-semibold text-sm" style={{ color: colors.text.dark }}>{remedy.title}</p>
                      {remedy.subtitle && (
                        <p className="text-xs mt-0.5 line-clamp-1" style={{ color: colors.text.secondary }}>{remedy.subtitle}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <p className="font-bold text-base" style={{ color: colors.gold?.accent || '#B45309' }}>
                      ₹{remedy.price?.toLocaleString('en-IN')}
                    </p>
                    <p className="text-xs" style={{ color: colors.text.muted }}>View →</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── J. Floating "Consult Astrologer" CTA ───────────────────── */}
      {/* bottom-16 = above the mobile bottom nav (h-16); md:bottom-0 since nav is md:hidden */}
      <div
        className="fixed bottom-16 md:bottom-0 left-0 right-0 p-4 z-40"
        style={{ backgroundColor: colors.background.primary, borderTop: `1px solid ${colors.ui.borderDark}` }}
      >
        <div className="max-w-2xl mx-auto">
          <button
            onClick={() => setShowBottomSheet(true)}
            className="w-full font-semibold py-4 rounded-2xl transition-all active:scale-[0.99] hover:shadow-md"
            style={{ backgroundColor: colors.teal.primary, color: '#ffffff' }}
            data-testid="expert-consult-btn"
          >
            Consult Astrologer
          </button>
        </div>
      </div>

      {/* ── K. Consultation Bottom Sheet ────────────────────────────── */}
      {showBottomSheet && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 z-50"
            style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
            onClick={() => setShowBottomSheet(false)}
          />
          {/* Sheet */}
          <div
            className="fixed bottom-0 left-0 right-0 z-50 rounded-t-3xl max-w-2xl mx-auto"
            style={{ backgroundColor: colors.background.primary }}
          >
            {/* Drag handle */}
            <div className="flex justify-center pt-3 pb-1">
              <div className="w-10 h-1 rounded-full" style={{ backgroundColor: colors.ui.borderDark }} />
            </div>

            <div className="px-5 pt-3 pb-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-lg" style={{ color: colors.text.dark }}>Book a Session</h3>
                <button
                  onClick={() => setShowBottomSheet(false)}
                  className="w-8 h-8 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: colors.background.secondary }}
                >
                  <svg width="16" height="16" fill="none" stroke={colors.text.muted} strokeWidth="2" strokeLinecap="round" viewBox="0 0 24 24">
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-3">
                {/* Free 10-min intro call */}
                {expert.offers_free_call && (
                  <button
                    onClick={() => { setShowBottomSheet(false); handleConsultationClick(null); }}
                    className="w-full text-left rounded-2xl p-4 transition-all active:scale-[0.99]"
                    style={{ backgroundColor: `${colors.teal.primary}10`, border: `1.5px solid ${colors.teal.primary}40` }}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full" style={{ backgroundColor: colors.teal.primary, color: '#fff' }}>
                            10 mins
                          </span>
                          <p className="font-semibold text-sm" style={{ color: colors.teal.dark }}>Free intro call</p>
                        </div>
                        <p className="text-xs mt-1" style={{ color: colors.text.muted }}>
                          Get to know the astrologer before committing
                        </p>
                      </div>
                      <div className="flex-shrink-0 text-right">
                        <p className="font-bold text-base" style={{ color: colors.teal.primary }}>Free</p>
                        <p className="text-xs" style={{ color: colors.text.muted }}>Book →</p>
                      </div>
                    </div>
                  </button>
                )}

                {/* Paid sessions */}
                {(expert.consultations || []).map((c, i) => (
                  <button
                    key={i}
                    onClick={() => { setShowBottomSheet(false); handleConsultationClick(c); }}
                    className="w-full text-left rounded-2xl p-4 transition-all active:scale-[0.99]"
                    style={{ backgroundColor: colors.peach.soft, border: `1px solid ${colors.ui.borderDark}` }}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full" style={{ backgroundColor: `${colors.teal.primary}20`, color: colors.teal.primary }}>
                            {c.duration_mins} mins
                          </span>
                          {c.title && (
                            <p className="font-semibold text-sm" style={{ color: colors.text.dark }}>{c.title}</p>
                          )}
                        </div>
                        {c.what_you_get && (
                          <p className="text-xs mt-1 line-clamp-2" style={{ color: colors.text.secondary }}>
                            {c.what_you_get}
                          </p>
                        )}
                      </div>
                      <div className="flex-shrink-0 text-right">
                        <p className="font-bold text-base" style={{ color: colors.teal.primary }}>
                          ₹{c.price_inr?.toLocaleString('en-IN')}
                        </p>
                        <p className="text-xs" style={{ color: colors.text.muted }}>Book →</p>
                      </div>
                    </div>
                  </button>
                ))}

                {/* No options fallback */}
                {!hasConsultations && (
                  <p className="text-center py-6 text-sm" style={{ color: colors.text.muted }}>
                    No sessions available yet. Check back soon.
                  </p>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
