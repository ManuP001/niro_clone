import React, { useState } from 'react';
import { colors } from './theme';
import { ProfileIcon, PackageIcon, AstroIcon, ChevronRightIcon } from './icons';
import BirthDetailsModal from './BirthDetailsModal';

/**
 * AccountScreen - Combined profile/account tab (always visible in BottomNav)
 * Logged out: shows login / register CTA
 * Logged in: shows user info, My Calls, My Kundli, Birth Details (editable), Logout
 */

function formatDob(dob) {
  if (!dob) return null;
  try {
    const d = new Date(dob + 'T00:00:00');
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch {
    return dob;
  }
}

const MenuItem = ({ Icon, label, sublabel, onClick }) => (
  <button
    onClick={onClick}
    className="w-full flex items-center gap-4 px-4 py-4 bg-white rounded-xl border hover:border-teal-300 transition-colors text-left"
    style={{ borderColor: colors.ui.border }}
  >
    <div
      className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
      style={{ backgroundColor: `${colors.teal.primary}15` }}
    >
      <Icon className="w-5 h-5" style={{ color: colors.teal.primary }} />
    </div>
    <div className="flex-1 min-w-0">
      <p className="font-semibold text-sm" style={{ color: colors.text.primary }}>{label}</p>
      {sublabel && <p className="text-xs mt-0.5" style={{ color: colors.text.muted }}>{sublabel}</p>}
    </div>
    <ChevronRightIcon className="w-4 h-4 flex-shrink-0" style={{ color: colors.text.muted }} />
  </button>
);

export default function AccountScreen({ token, user, isAuthenticated, onLoginClick, onLogout, onNavigate, hasBottomNav }) {
  const [showBirthModal, setShowBirthModal] = useState(false);
  const [birthSaved, setBirthSaved] = useState(false);

  const bottomPad = hasBottomNav ? 'pb-24' : 'pb-8';

  // ── Not logged in ──────────────────────────────────────────────────────────
  if (!isAuthenticated) {
    return (
      <div className={`min-h-screen flex flex-col items-center justify-center px-6 ${bottomPad}`}
        style={{ backgroundColor: colors.background.primary }}>
        <div
          className="w-20 h-20 rounded-full flex items-center justify-center mb-6"
          style={{ backgroundColor: `${colors.teal.primary}15` }}
        >
          <ProfileIcon className="w-10 h-10" style={{ color: colors.teal.primary }} />
        </div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: colors.text.primary }}>My Account</h2>
        <p className="text-center mb-8 max-w-xs" style={{ color: colors.text.muted }}>
          Sign in to view your consultations, Kundli chart, and manage your birth details.
        </p>
        <button
          onClick={onLoginClick}
          className="w-full max-w-xs py-3 rounded-xl font-semibold text-white text-base"
          style={{ backgroundColor: colors.teal.primary }}
        >
          Login / Register
        </button>
      </div>
    );
  }

  // ── Logged in ──────────────────────────────────────────────────────────────
  const initial = (user?.name || user?.email || '?')[0].toUpperCase();
  const hasBirthDetails = user?.dob && user?.tob;

  return (
    <div className={`min-h-screen ${bottomPad}`} style={{ backgroundColor: colors.background.primary }}>

      {/* User card */}
      <div
        className="px-4 pt-12 pb-6"
        style={{ background: `linear-gradient(180deg, ${colors.teal.primary} 0%, ${colors.teal.soft} 100%)` }}
      >
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full flex items-center justify-center text-xl font-bold text-white flex-shrink-0"
            style={{ backgroundColor: 'rgba(255,255,255,0.25)' }}>
            {initial}
          </div>
          <div className="min-w-0">
            <p className="font-bold text-lg text-white truncate">{user?.name || 'User'}</p>
            <p className="text-sm text-white/80 truncate">{user?.email || ''}</p>
          </div>
        </div>
      </div>

      {/* Menu items */}
      <div className="px-4 pt-4 space-y-3">

        <MenuItem
          Icon={PackageIcon}
          label="My Calls"
          sublabel="Upcoming & past consultations"
          onClick={() => onNavigate('mypack')}
        />

        <MenuItem
          Icon={AstroIcon}
          label="My Kundli"
          sublabel="Birth chart & planetary positions"
          onClick={() => onNavigate('astro')}
        />

        {/* Birth Details */}
        <div
          className="bg-white rounded-xl border px-4 py-4"
          style={{ borderColor: colors.ui.border }}
        >
          <div className="flex items-center justify-between mb-3">
            <p className="font-semibold text-sm" style={{ color: colors.text.primary }}>Birth Details</p>
            <button
              onClick={() => { setBirthSaved(false); setShowBirthModal(true); }}
              className="text-xs font-medium px-3 py-1 rounded-lg"
              style={{ color: colors.teal.primary, backgroundColor: `${colors.teal.primary}15` }}
            >
              {hasBirthDetails ? 'Edit' : 'Add'}
            </button>
          </div>
          {hasBirthDetails ? (
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Date of Birth', value: formatDob(user.dob) },
                { label: 'Time of Birth', value: user.tob },
                { label: 'Place of Birth', value: typeof user.pob === 'string' ? user.pob : (user.pob?.city || user.pob?.name || '—') },
              ].map(({ label, value }) => (
                <div key={label}>
                  <p className="text-[10px] uppercase tracking-wide mb-0.5" style={{ color: colors.text.muted }}>{label}</p>
                  <p className="text-sm font-medium" style={{ color: colors.text.primary }}>{value || '—'}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm" style={{ color: colors.text.muted }}>
              Add your birth details to view your Kundli chart.
            </p>
          )}
          {birthSaved && (
            <p className="text-xs mt-2 font-medium" style={{ color: colors.teal.primary }}>
              ✓ Birth details saved
            </p>
          )}
        </div>

        {/* Logout */}
        <button
          onClick={onLogout}
          className="w-full py-3 rounded-xl border font-medium text-sm mt-2"
          style={{ borderColor: '#FCA5A5', color: '#DC2626' }}
        >
          Logout
        </button>
      </div>

      {/* Birth Details Modal */}
      <BirthDetailsModal
        token={token}
        isOpen={showBirthModal}
        onClose={() => setShowBirthModal(false)}
        onComplete={() => {
          setShowBirthModal(false);
          setBirthSaved(true);
        }}
        isOnboarding={false}
      />
    </div>
  );
}
