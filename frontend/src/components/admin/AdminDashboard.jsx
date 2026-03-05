import React, { useState, useEffect } from 'react';
import { getBackendUrl } from '../../config';
import * as LucideIcons from 'lucide-react';

/**
 * Admin Dashboard - Full featured admin panel
 * 
 * Features:
 * - Dashboard overview with stats
 * - User/Order/Plan management
 * - Hierarchical homepage management (Categories -> Tiles)
 * - Catalog management (Topics, Experts, Remedies, Packages)
 * - Live Homepage Preview
 * - Visual Icon Picker with Lucide icons (matching app style)
 */

const getAdminToken = () => sessionStorage.getItem('niro_admin_token');
const setAdminToken = (token) => sessionStorage.setItem('niro_admin_token', token);
const clearAdminToken = () => sessionStorage.removeItem('niro_admin_token');

const adminFetch = async (endpoint, options = {}) => {
  const token = getAdminToken();
  const backendUrl = getBackendUrl();
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'X-Admin-Token': token }),
    ...options.headers,
  };
  
  const response = await fetch(`${backendUrl}${endpoint}`, { ...options, headers });
  const data = await response.json();
  
  // Only clear token on explicit auth failures, not network errors
  if (response.status === 401 && !endpoint.includes('/login')) {
    console.warn('Admin session expired or invalid');
    clearAdminToken();
    // Don't auto-reload, let the component handle re-login
    throw new Error('Session expired. Please login again.');
  }
  
  if (!response.ok) {
    throw new Error(data.detail || data.message || 'Request failed');
  }
  
  return data;
};

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
  }).format(amount || 0);
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
  });
};

// ============================================================================
// HOMEPAGE PREVIEW MODAL
// ============================================================================
const HomepagePreview = ({ isOpen, onClose }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      fetchPreviewData();
    }
  }, [isOpen]);

  const fetchPreviewData = async () => {
    setLoading(true);
    try {
      const backendUrl = getBackendUrl();
      const response = await fetch(`${backendUrl}/api/admin/public/homepage-data`);
      const data = await response.json();
      if (data.ok && data.data) {
        setCategories(data.data);
      }
    } catch (err) {
      console.error('Failed to fetch preview data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  // Mini icon component for preview
  const PreviewIcon = ({ type }) => {
    const icons = {
      heart: '❤️', healing: '💚', rings: '💍', chat: '💬', family: '👨‍👩‍👧', breakup: '💔',
      compass: '🧭', briefcase: '💼', wallet: '💰', clock: '⏰', stress: '😰', office: '🏢',
      energy: '⚡', sleep: '🌙', emotional: '🎭', wellness: '🌿', star: '⭐'
    };
    return <span className="text-xl">{icons[type] || icons.star}</span>;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b bg-gray-50">
          <div>
            <h3 className="font-semibold text-gray-800">Homepage Preview</h3>
            <p className="text-xs text-gray-500">Live preview of user-facing homepage</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Mobile Preview Frame */}
        <div className="flex-1 overflow-y-auto bg-gray-100 p-4">
          <div 
            className="mx-auto rounded-3xl overflow-hidden shadow-xl"
            style={{ 
              maxWidth: '375px',
              background: 'linear-gradient(145deg, #3E827A 0%, #4A9F95 50%, #5AB5A8 100%)',
            }}
          >
            {/* Phone Header */}
            <div className="px-4 pt-6 pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                    <span className="text-white text-sm">✨</span>
                  </div>
                  <span className="text-white font-semibold">Niro</span>
                </div>
                <div className="w-8 h-8 rounded-full bg-white/20"></div>
              </div>
              <p className="text-white/90 text-sm mt-3">What brings you here today?</p>
            </div>

            {/* Content Area */}
            <div className="px-3 pb-4">
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin w-8 h-8 border-2 border-white/30 border-t-white rounded-full mx-auto"></div>
                  <p className="text-white/70 text-sm mt-2">Loading preview...</p>
                </div>
              ) : categories.length === 0 ? (
                <div className="text-center py-8 bg-white/10 rounded-xl">
                  <p className="text-white/70 text-sm">No categories found</p>
                  <p className="text-white/50 text-xs mt-1">Add categories in the admin panel</p>
                </div>
              ) : (
                categories.map((category) => (
                  <div 
                    key={category.id}
                    className="bg-white/95 rounded-xl p-3 mb-3"
                    style={{ backdropFilter: 'blur(8px)' }}
                  >
                    <h4 className="text-sm font-semibold text-gray-800 mb-2">{category.title}</h4>
                    <div className="grid grid-cols-3 gap-2">
                      {category.tiles?.slice(0, 6).map((tile) => (
                        <div 
                          key={tile.id}
                          className="bg-white rounded-lg p-2 text-center border border-gray-100 hover:shadow-md transition-shadow cursor-pointer"
                        >
                          <PreviewIcon type={tile.iconType} />
                          <p className="text-[10px] font-medium text-gray-700 mt-1 truncate">
                            {tile.shortTitle}
                          </p>
                        </div>
                      ))}
                    </div>
                    {category.tiles?.length > 6 && (
                      <p className="text-xs text-gray-400 mt-2 text-center">
                        +{category.tiles.length - 6} more tiles
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* Mock Bottom Nav */}
            <div className="bg-white px-4 py-3 flex justify-around border-t">
              {['🏠', '🌟', '📦', '👤'].map((icon, i) => (
                <div key={i} className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                  <span className="text-lg">{icon}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t bg-gray-50 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            Live data from database
          </div>
          <div className="flex gap-2">
            <button
              onClick={fetchPreviewData}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
            <button
              onClick={onClose}
              className="px-4 py-1.5 text-sm bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// LOGIN
// ============================================================================
const AdminLogin = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await adminFetch('/api/admin/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      if (data.ok && data.token) {
        setAdminToken(data.token);
        onLogin();
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      setError('Connection error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-800">Niro Admin</h1>
          <p className="text-gray-500 mt-2">Enter your credentials</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg"
            placeholder="Username"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg"
            placeholder="Password"
            required
          />
          {error && <div className="text-red-500 text-sm text-center bg-red-50 p-2 rounded">{error}</div>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-teal-600 text-white font-semibold rounded-lg hover:bg-teal-700 disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};

// ============================================================================
// STAT CARD
// ============================================================================
const StatCard = ({ title, value, subtitle }) => (
  <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
    <p className="text-gray-500 text-sm">{title}</p>
    <p className="text-2xl font-bold text-gray-800 mt-1">{value}</p>
    {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
  </div>
);

// ============================================================================
// DASHBOARD HOME
// ============================================================================
const DashboardHome = ({ stats, onNavigate, environment, onSeedData }) => {
  const [seeding, setSeeding] = useState(false);
  const [catalogStats, setCatalogStats] = useState(null);

  useEffect(() => {
    // Fetch catalog stats to show if data exists
    const fetchCatalogStats = async () => {
      try {
        const [categories, tiles, topics, experts] = await Promise.all([
          adminFetch('/api/admin/categories'),
          adminFetch('/api/admin/tiles'),
          adminFetch('/api/admin/topics'),
          adminFetch('/api/admin/experts'),
        ]);
        setCatalogStats({
          categories: categories.count || 0,
          tiles: tiles.count || 0,
          topics: topics.count || 0,
          experts: experts.count || 0,
        });
      } catch (err) {
        console.error('Failed to fetch catalog stats:', err);
      }
    };
    fetchCatalogStats();
  }, [seeding]);

  const handleSeedData = async () => {
    if (!window.confirm('This will seed/refresh all catalog data (Categories, Tiles, Topics, Experts, Remedies, Packages). Continue?')) return;
    setSeeding(true);
    try {
      const result = await adminFetch('/api/admin/seed-catalog?force=true', { method: 'POST' });
      alert(`✅ Catalog seeded successfully!\n\nResults:\n- Categories: ${result.results?.categories || 0}\n- Tiles: ${result.results?.tiles || 0}\n- Topics: ${result.results?.topics || 0}\n- Experts: ${result.results?.experts || 0}\n- Remedies: ${result.results?.remedies || 0}\n- Packages: ${result.results?.tiers || 0}`);
    } catch (err) {
      alert('❌ Seed failed: ' + err.message);
    } finally {
      setSeeding(false);
    }
  };

  const handleCleanDuplicates = async () => {
    if (!window.confirm('This will remove duplicate entries from all catalog collections. Continue?')) return;
    setSeeding(true);
    try {
      const result = await adminFetch('/api/admin/clean-duplicates', { method: 'POST' });
      alert(`✅ Duplicates cleaned!\n\nRemoved:\n- Categories: ${result.removed?.categories || 0}\n- Tiles: ${result.removed?.tiles || 0}\n- Topics: ${result.removed?.topics || 0}\n- Experts: ${result.removed?.experts || 0}\n- Tiers: ${result.removed?.tiers || 0}`);
    } catch (err) {
      alert('❌ Clean failed: ' + err.message);
    } finally {
      setSeeding(false);
    }
  };

  const handleCleanOrphaned = async () => {
    if (!window.confirm('This will remove entries with missing IDs (e.g., categories created without a category_id). Continue?')) return;
    setSeeding(true);
    try {
      const result = await adminFetch('/api/admin/clean-orphaned', { method: 'POST' });
      alert(`Orphaned entries cleaned!\n\nRemoved:\n- Categories: ${result.removed?.categories || 0}\n- Tiles: ${result.removed?.tiles || 0}\n- Topics: ${result.removed?.topics || 0}\n- Tiers: ${result.removed?.tiers || 0}`);
    } catch (err) {
      alert('Clean failed: ' + err.message);
    } finally {
      setSeeding(false);
    }
  };


  const needsSeeding = catalogStats && (catalogStats.categories === 0 || catalogStats.topics === 0 || catalogStats.experts === 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Dashboard Overview</h2>
        {environment !== 'all' && (
          <span className="px-3 py-1 bg-teal-100 text-teal-700 rounded-full text-sm">
            Showing: {environment} data
          </span>
        )}
      </div>
      
      {/* Seed Data Banner - Show prominently if catalog is empty */}
      {needsSeeding && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="font-semibold text-red-800">⚠️ Catalog data is empty!</p>
            <p className="text-sm text-red-600 mt-1">Click "Seed Catalog Data" to populate Categories, Tiles, Topics, Experts, Remedies, and Packages.</p>
          </div>
          <button
            onClick={handleSeedData}
            disabled={seeding}
            className="px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center gap-2"
          >
            {seeding ? (
              <>
                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Seeding...
              </>
            ) : (
              <>🌱 Seed Catalog Data</>
            )}
          </button>
        </div>
      )}
      
      {/* Catalog Stats */}
      {catalogStats && !needsSeeding && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="font-semibold text-green-800">✅ Catalog data loaded</p>
            <p className="text-sm text-green-600 mt-1">
              {catalogStats.categories} categories, {catalogStats.tiles} tiles, {catalogStats.topics} topics, {catalogStats.experts} experts
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCleanOrphaned}
              disabled={seeding}
              className="px-4 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 disabled:opacity-50"
              title="Remove entries with missing IDs"
              data-testid="clean-orphaned-btn"
            >
              {seeding ? 'Cleaning...' : 'Clean Orphaned'}
            </button>
            <button
              onClick={handleCleanDuplicates}
              disabled={seeding}
              className="px-4 py-2 text-sm bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 disabled:opacity-50"
              title="Remove duplicate entries"
            >
              {seeding ? 'Cleaning...' : '🧹 Clean Duplicates'}
            </button>
            <button
              onClick={handleSeedData}
              disabled={seeding}
              className="px-4 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 disabled:opacity-50"
            >
              {seeding ? 'Refreshing...' : '🔄 Refresh Catalog'}
            </button>
          </div>
        </div>
      )}
      
      {/* How Changes Work Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800">
        <strong>💡 How changes work:</strong>
        <ul className="mt-2 space-y-1 list-disc list-inside">
          <li>Changes to Categories, Tiles, Topics, etc. are saved to the database instantly</li>
          <li>Use "Preview Homepage" button to see how changes will look</li>
          <li>Changes go live immediately on this environment's homepage</li>
          <li><strong>For production:</strong> Deploy from Emergent, then seed data on production admin</li>
        </ul>
      </div>
      
      {/* Info Banner for Preview Environment */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
        <strong>Note:</strong> This preview environment contains test data only. Production payment data (actual paying customers) will be visible after deployment when connected to the production MongoDB instance.
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Users" value={stats?.total_users || 0} subtitle={`${stats?.google_users || 0} Google + ${stats?.legacy_users || 0} Legacy`} />
        <StatCard title="With Profiles" value={stats?.profiles_count || 0} />
        <StatCard title="Total Orders" value={stats?.total_orders || 0} subtitle={`${stats?.paid_orders || 0} paid`} />
        <StatCard title="Revenue" value={formatCurrency(stats?.total_revenue_inr)} />
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Simplified Orders" value={stats?.simplified_orders || 0} />
        <StatCard title="V2 Orders" value={stats?.v2_orders || 0} />
        <StatCard title="Active Plans" value={stats?.active_plans || 0} />
        <StatCard title="Remedy Orders" value={stats?.remedy_orders || 0} />
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { id: 'users', label: 'View Users', icon: '👥' },
          { id: 'orders', label: 'View Orders', icon: '💰' },
          { id: 'plans', label: 'View Plans', icon: '📦' },
          { id: 'remedies', label: 'Remedy Orders', icon: '🙏' },
        ].map(item => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:border-teal-300 text-left"
          >
            <span className="text-2xl">{item.icon}</span>
            <p className="font-medium text-gray-800 mt-2">{item.label}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// USERS LIST
// ============================================================================
const UsersList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});
  const [search, setSearch] = useState('');
  const [source, setSource] = useState('all');
  const [profileStatus, setProfileStatus] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedUser, setSelectedUser] = useState(null);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page, limit: 20, source, profile_status: profileStatus, sort_by: sortBy, sort_order: sortOrder,
        ...(search && { search })
      });
      const data = await adminFetch(`/api/admin/users?${params}`);
      setUsers(data.users || []);
      setPagination(data.pagination || {});
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadUsers(); }, [page, source, profileStatus, sortBy, sortOrder]);

  const handleSearch = (e) => { e.preventDefault(); setPage(1); loadUsers(); };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h2 className="text-xl font-bold text-gray-800">Users ({pagination.total || 0})</h2>
        <button
          data-testid="export-users-csv-btn"
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm"
          onClick={async () => {
            try {
              const token = getAdminToken();
              const res = await fetch(`${getBackendUrl()}/api/admin/export/users?source=${source}`, {
                headers: { 'X-Admin-Token': token }
              });
              if (!res.ok) throw new Error('Export failed');
              const blob = await res.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `niro_users_${new Date().toISOString().slice(0,10)}.csv`;
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
            } catch (err) {
              alert('Export failed: ' + err.message);
            }
          }}
        >
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-xl shadow-sm space-y-3">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by email or name..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
          />
          <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded-lg">Search</button>
        </form>
        <div className="flex flex-wrap gap-3">
          <select value={source} onChange={(e) => { setSource(e.target.value); setPage(1); }} className="px-3 py-2 border rounded-lg text-sm">
            <option value="all">All Sources</option>
            <option value="google">Google Only</option>
            <option value="legacy">Legacy Only</option>
          </select>
          <select value={profileStatus} onChange={(e) => { setProfileStatus(e.target.value); setPage(1); }} className="px-3 py-2 border rounded-lg text-sm">
            <option value="all">All Profiles</option>
            <option value="complete">Complete</option>
            <option value="incomplete">Incomplete</option>
          </select>
          <select value={sortBy} onChange={(e) => { setSortBy(e.target.value); setPage(1); }} className="px-3 py-2 border rounded-lg text-sm">
            <option value="created_at">Sort by Date</option>
            <option value="name">Sort by Name</option>
            <option value="email">Sort by Email</option>
          </select>
          <select value={sortOrder} onChange={(e) => { setSortOrder(e.target.value); setPage(1); }} className="px-3 py-2 border rounded-lg text-sm">
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">DOB</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profile</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Orders</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Spent</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr><td colSpan="8" className="px-4 py-8 text-center text-gray-500">Loading...</td></tr>
              ) : users.length === 0 ? (
                <tr><td colSpan="8" className="px-4 py-8 text-center text-gray-500">No users found</td></tr>
              ) : (
                users.map((user) => (
                  <tr key={user.user_id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedUser(user)}>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{user.name || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{user.email || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{user.dob || '-'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${user.auth_source === 'google' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'}`}>
                        {user.auth_source || 'legacy'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${user.profile_complete ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                        {user.profile_complete ? 'Complete' : 'Incomplete'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{user.order_count || 0}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatCurrency(user.total_spent)}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatDate(user.created_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {pagination.pages > 1 && (
          <div className="px-4 py-3 border-t flex items-center justify-between">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border rounded disabled:opacity-50">Previous</button>
            <span className="text-sm text-gray-600">Page {page} of {pagination.pages}</span>
            <button onClick={() => setPage(p => Math.min(pagination.pages, p + 1))} disabled={page === pagination.pages} className="px-3 py-1 border rounded disabled:opacity-50">Next</button>
          </div>
        )}
      </div>

      {/* User Modal */}
      {selectedUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedUser(null)}>
          <div className="bg-white rounded-xl max-w-lg w-full max-h-[80vh] overflow-y-auto p-6" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold">User Details</h3>
              <button onClick={() => setSelectedUser(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                ['Name', selectedUser.name],
                ['Email', selectedUser.email],
                ['DOB', selectedUser.dob],
                ['TOB', selectedUser.tob],
                ['Place of Birth', selectedUser.pob],
                ['Gender', selectedUser.gender],
                ['Marital Status', selectedUser.marital_status],
                ['Auth Source', selectedUser.auth_source],
                ['Orders', selectedUser.order_count],
                ['Total Spent', formatCurrency(selectedUser.total_spent)],
              ].map(([label, value]) => (
                <div key={label}>
                  <p className="text-xs text-gray-500">{label}</p>
                  <p className="font-medium">{value || '-'}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t">
              <p className="text-xs text-gray-500">User ID</p>
              <p className="font-mono text-sm">{selectedUser.user_id}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// ORDERS LIST
// ============================================================================
const OrdersList = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});
  const [summary, setSummary] = useState({});
  const [status, setStatus] = useState('all');
  const [orderType, setOrderType] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');

  const loadOrders = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page, limit: 20, status, order_type: orderType, sort_by: sortBy, sort_order: sortOrder
      });
      const data = await adminFetch(`/api/admin/orders?${params}`);
      setOrders(data.orders || []);
      setPagination(data.pagination || {});
      setSummary(data.summary || {});
    } catch (err) {
      console.error('Failed to load orders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadOrders(); }, [page, status, orderType, sortBy, sortOrder]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h2 className="text-xl font-bold text-gray-800">Orders ({pagination.total || 0})</h2>
          <p className="text-sm text-gray-500">
            Total: {formatCurrency(summary.total_amount_inr)} | Paid: {formatCurrency(summary.paid_amount_inr)}
          </p>
        </div>
        <button
          data-testid="export-orders-csv-btn"
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm"
          onClick={async () => {
            try {
              const token = getAdminToken();
              const res = await fetch(`${getBackendUrl()}/api/admin/export/orders`, {
                headers: { 'X-Admin-Token': token }
              });
              if (!res.ok) throw new Error('Export failed');
              const blob = await res.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `niro_orders_${new Date().toISOString().slice(0,10)}.csv`;
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
            } catch (err) {
              alert('Export failed: ' + err.message);
            }
          }}
        >
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-xl shadow-sm flex flex-wrap gap-3">
        <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }} className="px-3 py-2 border rounded-lg text-sm">
          <option value="all">All Statuses</option>
          <option value="created">Created</option>
          <option value="pending">Pending</option>
          <option value="paid">Paid</option>
          <option value="failed">Failed</option>
        </select>
        <select value={orderType} onChange={(e) => { setOrderType(e.target.value); setPage(1); }} className="px-3 py-2 border rounded-lg text-sm">
          <option value="all">All Types</option>
          <option value="simplified">Simplified</option>
          <option value="v2">V2</option>
        </select>
        <select value={sortBy} onChange={(e) => { setSortBy(e.target.value); setPage(1); }} className="px-3 py-2 border rounded-lg text-sm">
          <option value="created_at">Sort by Date</option>
          <option value="amount">Sort by Amount</option>
        </select>
        <select value={sortOrder} onChange={(e) => { setSortOrder(e.target.value); setPage(1); }} className="px-3 py-2 border rounded-lg text-sm">
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Package</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr><td colSpan="7" className="px-4 py-8 text-center text-gray-500">Loading...</td></tr>
              ) : orders.length === 0 ? (
                <tr><td colSpan="7" className="px-4 py-8 text-center text-gray-500">No orders found</td></tr>
              ) : (
                orders.map((order) => (
                  <tr key={order.order_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-600">{order.order_id?.slice(0, 15)}...</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${order.order_type === 'v2' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
                        {order.order_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{order.user_name || order.user_email || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{order.tier_id || order.package_id || '-'}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{formatCurrency(order.amount_display)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        order.status === 'paid' ? 'bg-green-100 text-green-700' :
                        order.status === 'pending' || order.status === 'created' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {order.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatDate(order.created_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {pagination.pages > 1 && (
          <div className="px-4 py-3 border-t flex items-center justify-between">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 border rounded disabled:opacity-50">Previous</button>
            <span className="text-sm text-gray-600">Page {page} of {pagination.pages}</span>
            <button onClick={() => setPage(p => Math.min(pagination.pages, p + 1))} disabled={page === pagination.pages} className="px-3 py-1 border rounded disabled:opacity-50">Next</button>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// PLANS LIST
// ============================================================================
const PlansList = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});

  useEffect(() => {
    const loadPlans = async () => {
      setLoading(true);
      try {
        const data = await adminFetch(`/api/admin/plans?page=${page}&limit=20`);
        setPlans(data.plans || []);
        setPagination(data.pagination || {});
      } catch (err) {
        console.error('Failed to load plans:', err);
      } finally {
        setLoading(false);
      }
    };
    loadPlans();
  }, [page]);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800">Plans ({pagination.total || 0})</h2>
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tier</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expires</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr><td colSpan="7" className="px-4 py-8 text-center text-gray-500">Loading...</td></tr>
              ) : plans.length === 0 ? (
                <tr><td colSpan="7" className="px-4 py-8 text-center text-gray-500">No plans found</td></tr>
              ) : (
                plans.map((plan) => (
                  <tr key={plan.plan_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-600">{plan.plan_id}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{plan.user_name || plan.user_email || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 capitalize">{plan.topic_id || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 capitalize">{plan.tier_level || '-'}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{formatCurrency(plan.price_paid_inr)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${plan.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                        {plan.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatDate(plan.expires_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// REMEDY ORDERS LIST
// ============================================================================
const RemedyOrdersList = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});

  useEffect(() => {
    const loadOrders = async () => {
      setLoading(true);
      try {
        const data = await adminFetch(`/api/admin/remedy-orders?page=${page}&limit=20`);
        setOrders(data.orders || []);
        setPagination(data.pagination || {});
      } catch (err) {
        console.error('Failed to load remedy orders:', err);
      } finally {
        setLoading(false);
      }
    };
    loadOrders();
  }, [page]);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800">Remedy Orders ({pagination.total || 0})</h2>
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Remedy</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr><td colSpan="7" className="px-4 py-8 text-center text-gray-500">Loading...</td></tr>
              ) : orders.length === 0 ? (
                <tr><td colSpan="7" className="px-4 py-8 text-center text-gray-500">No remedy orders found</td></tr>
              ) : (
                orders.map((order) => (
                  <tr key={order.remedy_order_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-600">{order.remedy_order_id}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{order.user_name || order.user_email || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{order.remedy_name || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 capitalize">{order.remedy_category || '-'}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{formatCurrency(order.price_inr)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${order.status === 'paid' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                        {order.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatDate(order.created_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// WEEKLY AVAILABILITY EDITOR
// ============================================================================
const DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
const DAY_LABELS = { monday: 'Mon', tuesday: 'Tue', wednesday: 'Wed', thursday: 'Thu', friday: 'Fri', saturday: 'Sat', sunday: 'Sun' };

const WeeklyAvailabilityEditor = ({ value = {}, onChange }) => {
  const getSlots = (day) => (Array.isArray(value[day]) ? value[day] : []);

  const handleToggle = (day, enabled) => {
    const next = { ...value };
    next[day] = enabled ? [{ start: '09:00', end: '10:00' }] : [];
    onChange(next);
  };

  const handleAddSlot = (day) => {
    const slots = getSlots(day);
    onChange({ ...value, [day]: [...slots, { start: '18:00', end: '19:00' }] });
  };

  const handleRemoveSlot = (day, idx) => {
    const slots = getSlots(day).filter((_, i) => i !== idx);
    onChange({ ...value, [day]: slots });
  };

  const handleTime = (day, idx, field, val) => {
    const slots = getSlots(day).map((s, i) => i === idx ? { ...s, [field]: val } : s);
    onChange({ ...value, [day]: slots });
  };

  return (
    <div className="space-y-3 border border-gray-200 rounded-lg p-3">
      {DAYS_OF_WEEK.map(day => {
        const slots = getSlots(day);
        const enabled = slots.length > 0;
        return (
          <div key={day}>
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={enabled}
                onChange={e => handleToggle(day, e.target.checked)}
                className="w-4 h-4"
              />
              <span className="w-8 text-sm font-semibold text-gray-700">{DAY_LABELS[day]}</span>
              {enabled && (
                <button
                  type="button"
                  onClick={() => handleAddSlot(day)}
                  className="ml-auto text-xs text-teal-600 hover:text-teal-800 font-medium"
                >
                  + Add slot
                </button>
              )}
            </div>
            {enabled && slots.map((slot, idx) => (
              <div key={idx} className="flex items-center gap-2 mt-1 ml-7">
                <input
                  type="time"
                  value={slot.start}
                  onChange={e => handleTime(day, idx, 'start', e.target.value)}
                  className="px-2 py-1 border border-gray-300 rounded text-sm"
                />
                <span className="text-gray-400 text-sm">–</span>
                <input
                  type="time"
                  value={slot.end}
                  onChange={e => handleTime(day, idx, 'end', e.target.value)}
                  className="px-2 py-1 border border-gray-300 rounded text-sm"
                />
                {slots.length > 1 && (
                  <button
                    type="button"
                    onClick={() => handleRemoveSlot(day, idx)}
                    className="text-red-400 hover:text-red-600 text-lg leading-none ml-1"
                    title="Remove slot"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
};

// ============================================================================
// CATALOG MANAGER - Generic CRUD Component
// ============================================================================
const CatalogManager = ({ entityType, title, icon, columns, formFields, dataKey }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [formData, setFormData] = useState({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [includeInactive, setIncludeInactive] = useState(false);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [bulkProcessing, setBulkProcessing] = useState(false);

  // Use dataKey or derive from entityType (remove hyphens)
  const responseKey = dataKey || entityType.replace(/-/g, '_').replace('_catalog', '');

  const loadItems = async () => {
    setLoading(true);
    try {
      const data = await adminFetch(`/api/admin/${entityType}?include_inactive=${includeInactive}`);
      setItems(data[responseKey] || data[entityType] || data.items || []);
    } catch (err) {
      console.error(`Failed to load ${entityType}:`, err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadItems(); }, [includeInactive]);

  const handleCreate = () => {
    setEditItem(null);
    const defaultData = {};
    formFields.forEach(f => { defaultData[f.name] = f.default || ''; });
    setFormData(defaultData);
    setShowModal(true);
    setError('');
  };

  const handleEdit = (item) => {
    setEditItem(item);
    setFormData({ ...item });
    setShowModal(true);
    setError('');
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      const idField = formFields.find(f => f.isId)?.name || `${entityType.slice(0, -1)}_id`;
      
      // Clean up form data - remove empty strings for optional fields, keep booleans and numbers
      const cleanedData = {};
      for (const [key, value] of Object.entries(formData)) {
        // Skip null/undefined
        if (value === null || value === undefined) continue;
        // Skip empty strings (treat as "no change" for PUT), but keep for ID fields on create
        if (value === '' && !(key === idField && !editItem)) continue;
        // For arrays, skip empty arrays
        if (Array.isArray(value) && value.length === 0) continue;
        // Keep false values (important for active toggle), keep 0 values
        cleanedData[key] = value;
      }
      
      if (editItem) {
        const itemId = editItem[idField];
        if (!itemId) {
          setError(`Cannot update: missing ${idField}. Try refreshing the page.`);
          setSaving(false);
          return;
        }
        await adminFetch(`/api/admin/${entityType}/${itemId}`, {
          method: 'PUT',
          body: JSON.stringify(cleanedData),
        });
      } else {
        // Validate required ID field on create
        if (!cleanedData[idField]) {
          setError(`${idField.replace(/_/g, ' ')} is required.`);
          setSaving(false);
          return;
        }
        await adminFetch(`/api/admin/${entityType}`, {
          method: 'POST',
          body: JSON.stringify(cleanedData),
        });
      }
      setShowModal(false);
      loadItems();
    } catch (err) {
      // Map technical errors to user-friendly messages
      const msg = err.message || 'Failed to save';
      if (msg.includes('already exists')) {
        setError(`This ID is already taken. Please choose a different one.`);
      } else if (msg.includes('not found')) {
        setError(`Item not found in database. It may have been deleted. Try refreshing.`);
      } else if (msg.includes('No fields to update')) {
        setError(`No changes detected. Modify at least one field.`);
      } else if (msg.includes('Cannot activate')) {
        setError(msg); // This message is already descriptive
      } else if (msg.includes('Session expired')) {
        setError('Your session has expired. Please log in again.');
      } else {
        setError(msg);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (item, hardDelete = false) => {
    // Find the correct ID field from form fields or derive it
    const idField = formFields.find(f => f.isId)?.name || 
                    (entityType === 'categories' ? 'category_id' : 
                     entityType === 'tiles' ? 'tile_id' :
                     entityType === 'topics' ? 'topic_id' :
                     entityType === 'experts' ? 'expert_id' :
                     entityType === 'remedies-catalog' ? 'remedy_id' :
                     entityType === 'tiers' ? 'tier_id' : 'id');
    
    const itemId = item[idField];
    if (!itemId) {
      alert(`Error: Could not find ID field (${idField}) in item`);
      console.error('Item:', item, 'ID Field:', idField);
      return;
    }
    
    const action = hardDelete ? 'permanently delete' : (item.active === false ? 'permanently delete' : 'deactivate');
    if (!window.confirm(`Are you sure you want to ${action} "${item.title || item.name || item.label || itemId}"?`)) return;
    try {
      const useHardDelete = hardDelete || item.active === false;
      await adminFetch(`/api/admin/${entityType}/${itemId}?hard_delete=${useHardDelete}`, { method: 'DELETE' });
      loadItems();
    } catch (err) {
      const msg = err.message || 'Failed to delete';
      if (msg.includes('not found')) {
        alert(`Item not found. It may have already been removed. Refreshing list...`);
        loadItems();
      } else {
        alert('Failed: ' + msg);
      }
    }
  };

  const handleSeedData = async () => {
    if (!window.confirm('This will seed/refresh ALL catalog data (Categories, Tiles, Topics, Experts, Remedies, Packages). Any existing catalog data will be replaced. Continue?')) return;
    try {
      const result = await adminFetch('/api/admin/seed-catalog?force=true', { method: 'POST' });
      alert(`✅ Catalog seeded successfully!\n\nResults:\n- Categories: ${result.results?.categories || 0}\n- Tiles: ${result.results?.tiles || 0}\n- Topics: ${result.results?.topics || 0}\n- Experts: ${result.results?.experts || 0}\n- Remedies: ${result.results?.remedies || 0}\n- Packages: ${result.results?.tiers || 0}`);
      loadItems();
    } catch (err) {
      alert('Seed failed: ' + err.message);
    }
  };

  // Bulk selection helpers
  const getIdField = () => formFields.find(f => f.isId)?.name || 
    (entityType === 'categories' ? 'category_id' : 
     entityType === 'tiles' ? 'tile_id' :
     entityType === 'topics' ? 'topic_id' :
     entityType === 'experts' ? 'expert_id' :
     entityType === 'remedies-catalog' ? 'remedy_id' :
     entityType === 'tiers' ? 'tier_id' : 'id');

  const toggleSelect = (itemId) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(itemId) ? next.delete(itemId) : next.add(itemId);
      return next;
    });
  };

  const toggleSelectAll = () => {
    const idField = getIdField();
    if (selectedIds.size === items.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(items.map(i => i[idField])));
    }
  };

  const handleBulkDeactivate = async () => {
    if (selectedIds.size === 0) return;
    if (!window.confirm(`Deactivate ${selectedIds.size} item(s)?`)) return;
    setBulkProcessing(true);
    let success = 0, failed = 0;
    for (const id of selectedIds) {
      try {
        await adminFetch(`/api/admin/${entityType}/${id}`, { method: 'DELETE' });
        success++;
      } catch { failed++; }
    }
    setBulkProcessing(false);
    setSelectedIds(new Set());
    loadItems();
    alert(`Deactivated: ${success}${failed ? `, Failed: ${failed}` : ''}`);
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!window.confirm(`PERMANENTLY delete ${selectedIds.size} item(s)? This cannot be undone.`)) return;
    setBulkProcessing(true);
    let success = 0, failed = 0;
    for (const id of selectedIds) {
      try {
        await adminFetch(`/api/admin/${entityType}/${id}?hard_delete=true`, { method: 'DELETE' });
        success++;
      } catch { failed++; }
    }
    setBulkProcessing(false);
    setSelectedIds(new Set());
    loadItems();
    alert(`Deleted: ${success}${failed ? `, Failed: ${failed}` : ''}`);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">{icon} {title}</h2>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input type="checkbox" checked={includeInactive} onChange={(e) => setIncludeInactive(e.target.checked)} />
            Show inactive
          </label>
          {entityType === 'topics' && (
            <button onClick={handleSeedData} className="px-4 py-2 text-sm bg-amber-100 text-amber-700 rounded-lg hover:bg-amber-200">
              Seed Data
            </button>
          )}
          <button onClick={handleCreate} className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700">
            + Add New
          </button>
        </div>
      </div>

      {/* Bulk Action Bar */}
      {selectedIds.size > 0 && (
        <div className="flex items-center gap-3 bg-blue-50 border border-blue-200 rounded-lg px-4 py-2" data-testid="bulk-action-bar">
          <span className="text-sm font-medium text-blue-700">{selectedIds.size} selected</span>
          <button
            onClick={handleBulkDeactivate}
            disabled={bulkProcessing}
            className="px-3 py-1 text-sm bg-amber-500 text-white rounded hover:bg-amber-600 disabled:opacity-50"
            data-testid="bulk-deactivate-btn"
          >
            {bulkProcessing ? 'Processing...' : 'Deactivate'}
          </button>
          <button
            onClick={handleBulkDelete}
            disabled={bulkProcessing}
            className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
            data-testid="bulk-delete-btn"
          >
            {bulkProcessing ? 'Processing...' : 'Delete Permanently'}
          </button>
          <button
            onClick={() => setSelectedIds(new Set())}
            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
          >
            Clear
          </button>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-3 w-10">
                <input
                  type="checkbox"
                  checked={items.length > 0 && selectedIds.size === items.length}
                  onChange={toggleSelectAll}
                  className="w-4 h-4 accent-teal-600"
                  data-testid="bulk-select-all"
                />
              </th>
              {columns.map(col => (
                <th key={col.key} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{col.label}</th>
              ))}
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td colSpan={columns.length + 2} className="px-4 py-8 text-center text-gray-500">Loading...</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={columns.length + 2} className="px-4 py-8 text-center text-gray-500">No items found. Click "Seed Data" to initialize catalog.</td></tr>
            ) : (
              items.map((item, idx) => {
                const itemId = item[getIdField()];
                return (
                  <tr key={idx} className={`hover:bg-gray-50 ${item.active === false ? 'opacity-50' : ''} ${selectedIds.has(itemId) ? 'bg-blue-50' : ''}`}>
                    <td className="px-3 py-3">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(itemId)}
                        onChange={() => toggleSelect(itemId)}
                        className="w-4 h-4 accent-teal-600"
                        data-testid={`bulk-select-${itemId}`}
                      />
                    </td>
                    {columns.map(col => (
                      <td key={col.key} className="px-4 py-3 text-sm text-gray-900">
                        {col.render ? col.render(item[col.key], item) : (
                          Array.isArray(item[col.key]) ? item[col.key].join(', ') : String(item[col.key] ?? '-')
                        )}
                      </td>
                    ))}
                    <td className="px-4 py-3 text-right">
                      <button onClick={() => handleEdit(item)} className="text-blue-600 hover:text-blue-800 mr-3">Edit</button>
                      <button onClick={() => handleDelete(item)} className="text-red-600 hover:text-red-800">{item.active === false ? 'Delete' : 'Deactivate'}</button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowModal(false)}>
          <div className="bg-white rounded-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">{editItem ? 'Edit' : 'Create'} {title.slice(0, -1)}</h3>
            {error && <div className="text-red-600 text-sm bg-red-50 p-2 rounded mb-4">{error}</div>}
            <div className="space-y-4">
              {formFields.map(field => (
                <div key={field.name}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{field.label}</label>
                  {field.type === 'textarea' ? (
                    <textarea
                      value={formData[field.name] || ''}
                      onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      rows={3}
                      disabled={field.isId && editItem}
                    />
                  ) : field.type === 'icon-picker' ? (
                    <IconPicker
                      value={formData[field.name] || ''}
                      onChange={(val) => setFormData({ ...formData, [field.name]: val })}
                      label=""
                    />
                  ) : field.type === 'tile-icon-picker' ? (
                    <TileIconPicker
                      value={formData[field.name] || ''}
                      onChange={(val) => setFormData({ ...formData, [field.name]: val })}
                    />
                  ) : field.type === 'select' ? (
                    <select
                      value={formData[field.name] || ''}
                      onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    >
                      {field.options?.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                    </select>
                  ) : field.type === 'checkbox' ? (
                    <input
                      type="checkbox"
                      checked={formData[field.name] || false}
                      onChange={(e) => setFormData({ ...formData, [field.name]: e.target.checked })}
                      className="w-5 h-5"
                    />
                  ) : field.type === 'number' ? (
                    <input
                      type="number"
                      step={field.decimal ? '0.1' : '1'}
                      min={field.min}
                      max={field.max}
                      value={formData[field.name] || 0}
                      onChange={(e) => setFormData({ ...formData, [field.name]: field.decimal ? (parseFloat(e.target.value) || 0) : (parseInt(e.target.value) || 0) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  ) : field.type === 'array' ? (
                    <input
                      type="text"
                      value={Array.isArray(formData[field.name]) ? formData[field.name].join(', ') : formData[field.name] || ''}
                      onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="Comma-separated values"
                    />
                  ) : field.type === 'expert-multi-select' ? (
                    <ExpertMultiSelect
                      experts={field.experts || []}
                      selectedIds={formData[field.name] || []}
                      onChange={(ids) => setFormData({ ...formData, [field.name]: ids })}
                    />
                  ) : field.type === 'tag-multi-select' ? (
                    <TagMultiSelect
                      tagType={field.tagType}
                      selectedTags={formData[field.name] || []}
                      onChange={(tags) => setFormData({ ...formData, [field.name]: tags })}
                      maxTags={field.maxTags}
                    />
                  ) : field.type === 'image-upload' ? (
                    <div className="space-y-2">
                      {formData[field.name] && (
                        <div className="w-16 h-16 rounded-full overflow-hidden border border-gray-200">
                          <img src={formData[field.name].startsWith('/') ? `${getBackendUrl()}${formData[field.name]}` : formData[field.name]} alt="Preview" className="w-full h-full object-cover" onError={(e) => { e.target.style.display='none'; }} />
                        </div>
                      )}
                      <div className="flex gap-2 items-center">
                        <input
                          type="file"
                          accept="image/jpeg,image/png,image/webp,image/gif"
                          data-testid={`image-upload-${field.name}`}
                          className="text-sm"
                          onChange={async (e) => {
                            const file = e.target.files?.[0];
                            if (!file) return;
                            try {
                              const fd = new FormData();
                              fd.append('file', file);
                              const token = getAdminToken();
                              const res = await fetch(`${getBackendUrl()}/api/admin/upload/image`, {
                                method: 'POST',
                                headers: { 'X-Admin-Token': token },
                                body: fd,
                              });
                              const data = await res.json();
                              if (data.ok) {
                                setFormData(prev => ({ ...prev, [field.name]: data.url }));
                              } else {
                                alert(data.detail || 'Upload failed');
                              }
                            } catch (err) {
                              alert('Upload failed: ' + err.message);
                            }
                          }}
                        />
                        <span className="text-xs text-gray-400">or</span>
                        <input
                          type="text"
                          value={formData[field.name] || ''}
                          onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                          className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                          placeholder="Paste URL"
                        />
                      </div>
                    </div>
                  ) : field.type === 'consultation-list' ? (
                    <ConsultationEditor
                      value={formData[field.name] || []}
                      onChange={(val) => setFormData({ ...formData, [field.name]: val })}
                    />
                  ) : field.type === 'package-content' ? (
                    <PackageContentEditor
                      content={formData[field.name] || {}}
                      onChange={(content) => setFormData({ ...formData, [field.name]: content })}
                    />
                  ) : field.type === 'weekly-availability' ? (
                    <WeeklyAvailabilityEditor
                      value={formData[field.name] || {}}
                      onChange={(val) => setFormData({ ...formData, [field.name]: val })}
                    />
                  ) : (
                    <input
                      type="text"
                      value={formData[field.name] || ''}
                      onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      disabled={field.isId && editItem}
                    />
                  )}
                  {field.hint && <p className="text-xs text-gray-500 mt-1">{field.hint}</p>}
                </div>
              ))}
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-gray-600 hover:text-gray-800">Cancel</button>
              <button onClick={handleSave} disabled={saving} className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50">
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Icon options for Topics and Tiles - matching the app's existing icons
// Comprehensive Lucide icon list organized by category
const LUCIDE_ICONS = {
  // Love & Relationships
  love: [
    'Heart', 'HeartHandshake', 'HeartPulse', 'HeartCrack', 'HeartOff',
    'Users', 'UserPlus', 'UserCheck', 'UsersRound', 'Baby',
    'Gem', 'Sparkles', 'Star', 'Stars', 'Flower', 'Flower2',
  ],
  // Career & Money
  career: [
    'Briefcase', 'Building', 'Building2', 'Landmark', 'Factory',
    'Wallet', 'Banknote', 'CreditCard', 'PiggyBank', 'TrendingUp',
    'Target', 'Award', 'Trophy', 'Medal', 'Crown',
    'Lightbulb', 'Rocket', 'Compass', 'Navigation', 'Map',
  ],
  // Health & Wellness
  health: [
    'Activity', 'Dumbbell', 'Apple', 'Salad', 'Cookie',
    'Brain', 'Eye', 'Ear', 'Hand', 'Footprints',
    'Moon', 'Sun', 'Sunrise', 'Sunset', 'CloudSun',
    'Leaf', 'TreePine', 'Flower', 'Sprout', 'Clover',
    'Zap', 'Battery', 'BatteryFull', 'Flame', 'Droplet',
  ],
  // Communication
  communication: [
    'MessageCircle', 'MessageSquare', 'MessagesSquare', 'Mail', 'Send',
    'Phone', 'PhoneCall', 'Video', 'Mic', 'Volume2',
    'Bell', 'BellRing', 'Megaphone', 'Radio', 'Podcast',
  ],
  // Time & Planning
  time: [
    'Clock', 'Clock1', 'Clock12', 'Timer', 'Hourglass',
    'Calendar', 'CalendarDays', 'CalendarCheck', 'CalendarClock', 'CalendarHeart',
    'AlarmClock', 'Watch', 'History', 'TimerReset', 'Undo2',
  ],
  // Spiritual & Astrology
  spiritual: [
    'Sparkle', 'Sparkles', 'Star', 'Stars', 'Sun', 'Moon',
    'CircleDot', 'Orbit', 'Globe', 'Globe2', 'Earth',
    'Eye', 'ScanEye', 'Focus', 'Crosshair', 'Scan',
    'Infinity', 'RotateCcw', 'RefreshCw', 'Repeat', 'Shuffle',
  ],
  // Home & Family
  home: [
    'Home', 'House', 'Building', 'Castle', 'Tent',
    'Sofa', 'Bed', 'BedDouble', 'Armchair', 'Lamp',
    'Key', 'Lock', 'LockKeyhole', 'Shield', 'ShieldCheck',
    'Dog', 'Cat', 'Bird', 'Fish', 'Rabbit',
  ],
  // Education & Growth
  education: [
    'GraduationCap', 'BookOpen', 'Book', 'BookMarked', 'Library',
    'Pencil', 'PenTool', 'Highlighter', 'FileText', 'ScrollText',
    'Scale', 'Ruler', 'Calculator', 'Binary', 'Code',
  ],
  // Travel & Movement
  travel: [
    'Plane', 'PlaneTakeoff', 'Car', 'Bus', 'Train',
    'Ship', 'Sailboat', 'Bike', 'MapPin', 'Route',
    'Luggage', 'Backpack', 'Tent', 'Mountain', 'Palmtree',
  ],
  // Emotions & Feelings
  emotions: [
    'Smile', 'Frown', 'Meh', 'Laugh', 'Angry',
    'ThumbsUp', 'ThumbsDown', 'HandHeart', 'HeartHandshake', 'Handshake',
    'PartyPopper', 'Gift', 'Cake', 'Candy', 'IceCream',
  ],
  // Generic & Misc
  misc: [
    'Circle', 'Square', 'Triangle', 'Hexagon', 'Octagon',
    'Plus', 'Minus', 'X', 'Check', 'CheckCircle',
    'Info', 'HelpCircle', 'AlertCircle', 'AlertTriangle', 'Ban',
    'Settings', 'Sliders', 'Filter', 'Search', 'Maximize',
  ],
};

// Flatten all icons for the picker
const ALL_ICONS = Object.entries(LUCIDE_ICONS).flatMap(([category, icons]) => 
  icons.map(icon => ({ name: icon, category }))
);

// Icon Picker Component
const IconPicker = ({ value, onChange, label }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const filteredIcons = ALL_ICONS.filter(icon => {
    const matchesSearch = icon.name.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || icon.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const IconComponent = value ? LucideIcons[value] : null;

  return (
    <div className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg flex items-center gap-2 bg-white hover:bg-gray-50"
      >
        {IconComponent ? (
          <>
            <IconComponent className="w-5 h-5 text-teal-600" />
            <span>{value}</span>
          </>
        ) : (
          <span className="text-gray-400">Select an icon...</span>
        )}
        <LucideIcons.ChevronDown className="w-4 h-4 ml-auto text-gray-400" />
      </button>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-xl max-h-96 overflow-hidden">
          {/* Search and Category Filter */}
          <div className="p-2 border-b sticky top-0 bg-white">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Search icons..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="flex-1 px-2 py-1 text-sm border border-gray-200 rounded"
              />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-2 py-1 text-sm border border-gray-200 rounded"
              >
                <option value="all">All</option>
                {Object.keys(LUCIDE_ICONS).map(cat => (
                  <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Icons Grid */}
          <div className="p-2 overflow-y-auto max-h-72 grid grid-cols-6 gap-1">
            {/* Clear option */}
            <button
              type="button"
              onClick={() => { onChange(''); setIsOpen(false); }}
              className="p-2 rounded hover:bg-gray-100 flex flex-col items-center justify-center text-gray-400"
              title="Clear"
            >
              <LucideIcons.X className="w-5 h-5" />
              <span className="text-[9px] mt-1">None</span>
            </button>
            {filteredIcons.map(({ name }) => {
              const Icon = LucideIcons[name];
              if (!Icon) return null;
              return (
                <button
                  key={name}
                  type="button"
                  onClick={() => { onChange(name); setIsOpen(false); }}
                  className={`p-2 rounded hover:bg-teal-50 flex flex-col items-center justify-center ${value === name ? 'bg-teal-100 ring-2 ring-teal-500' : ''}`}
                  title={name}
                >
                  <Icon className="w-5 h-5 text-teal-600" />
                  <span className="text-[9px] mt-1 truncate w-full text-center">{name}</span>
                </button>
              );
            })}
          </div>
          
          {/* Close button */}
          <div className="p-2 border-t bg-gray-50">
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="w-full px-3 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// SVG Icon types for Tiles (matching HomeScreen icons - these are custom SVG names)
const TILE_ICON_OPTIONS = [
  { value: '', label: '-- Select Icon --' },
  // Love category icons
  { value: 'heart', label: 'Heart (Dating)' },
  { value: 'healing', label: 'Healing' },
  { value: 'rings', label: 'Rings (Marriage)' },
  { value: 'chat', label: 'Chat (Trust)' },
  { value: 'family', label: 'Family' },
  { value: 'breakup', label: 'Breakup (Closure)' },
  // Career category icons
  { value: 'compass', label: 'Compass (Clarity)' },
  { value: 'briefcase', label: 'Briefcase (Job)' },
  { value: 'wallet', label: 'Wallet (Money)' },
  { value: 'clock', label: 'Clock (Timing)' },
  { value: 'stress', label: 'Stress' },
  { value: 'office', label: 'Office' },
  // Health category icons
  { value: 'energy', label: 'Energy (Lightning)' },
  { value: 'sleep', label: 'Sleep (Moon)' },
  { value: 'emotional', label: 'Emotional' },
  { value: 'wellness', label: 'Wellness (Plant)' },
  // Generic
  { value: 'star', label: 'Star' },
];

// Tile Icon Picker with visual preview (uses app's custom SVG icons)
const TileIconPicker = ({ value, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  // Map tile icon names to Lucide equivalents for preview
  const iconMap = {
    heart: LucideIcons.Heart,
    healing: LucideIcons.HeartPulse,
    rings: LucideIcons.Gem,
    chat: LucideIcons.MessageCircle,
    family: LucideIcons.Users,
    breakup: LucideIcons.HeartCrack,
    compass: LucideIcons.Compass,
    briefcase: LucideIcons.Briefcase,
    wallet: LucideIcons.Wallet,
    clock: LucideIcons.Clock,
    stress: LucideIcons.Frown,
    office: LucideIcons.Building,
    energy: LucideIcons.Zap,
    sleep: LucideIcons.Moon,
    emotional: LucideIcons.Smile,
    wellness: LucideIcons.Leaf,
    star: LucideIcons.Star,
  };

  const IconComponent = iconMap[value];

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg flex items-center gap-2 bg-white hover:bg-gray-50"
      >
        {IconComponent ? (
          <>
            <IconComponent className="w-5 h-5 text-teal-600" />
            <span>{TILE_ICON_OPTIONS.find(o => o.value === value)?.label || value}</span>
          </>
        ) : (
          <span className="text-gray-400">Select an icon...</span>
        )}
        <LucideIcons.ChevronDown className="w-4 h-4 ml-auto text-gray-400" />
      </button>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-xl">
          <div className="p-2 grid grid-cols-4 gap-2 max-h-64 overflow-y-auto">
            {/* Clear option */}
            <button
              type="button"
              onClick={() => { onChange(''); setIsOpen(false); }}
              className="p-2 rounded hover:bg-gray-100 flex flex-col items-center justify-center text-gray-400 border border-dashed"
            >
              <LucideIcons.X className="w-5 h-5" />
              <span className="text-[10px] mt-1">None</span>
            </button>
            {TILE_ICON_OPTIONS.filter(o => o.value).map(({ value: iconVal, label }) => {
              const Icon = iconMap[iconVal];
              return (
                <button
                  key={iconVal}
                  type="button"
                  onClick={() => { onChange(iconVal); setIsOpen(false); }}
                  className={`p-2 rounded hover:bg-teal-50 flex flex-col items-center justify-center border ${value === iconVal ? 'bg-teal-100 border-teal-500' : 'border-gray-100'}`}
                >
                  {Icon && <Icon className="w-5 h-5 text-teal-600" />}
                  <span className="text-[10px] mt-1 text-center leading-tight">{label.split(' ')[0]}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

// Expert Multi-Select Component for assigning astrologers to packages
const ExpertMultiSelect = ({ experts, selectedIds, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');

  const toggleExpert = (expertId) => {
    const newSelection = selectedIds.includes(expertId)
      ? selectedIds.filter(id => id !== expertId)
      : [...selectedIds, expertId];
    onChange(newSelection);
  };

  const filteredExperts = experts.filter(e => 
    e.name?.toLowerCase().includes(search.toLowerCase()) ||
    e.modality?.toLowerCase().includes(search.toLowerCase())
  );

  const selectedExperts = experts.filter(e => selectedIds.includes(e.expert_id));

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg flex items-center gap-2 bg-white hover:bg-gray-50 text-left"
      >
        {selectedExperts.length > 0 ? (
          <div className="flex flex-wrap gap-1 flex-1">
            {selectedExperts.slice(0, 3).map(e => (
              <span key={e.expert_id} className="px-2 py-0.5 bg-teal-100 text-teal-700 text-xs rounded">
                {e.name}
              </span>
            ))}
            {selectedExperts.length > 3 && (
              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                +{selectedExperts.length - 3} more
              </span>
            )}
          </div>
        ) : (
          <span className="text-gray-400 flex-1">Select astrologers...</span>
        )}
        <LucideIcons.ChevronDown className="w-4 h-4 text-gray-400" />
      </button>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-xl max-h-80 overflow-hidden">
          {/* Search */}
          <div className="p-2 border-b sticky top-0 bg-white">
            <input
              type="text"
              placeholder="Search experts..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-2 py-1 text-sm border border-gray-200 rounded"
            />
          </div>
          
          {/* Expert List */}
          <div className="p-2 overflow-y-auto max-h-56">
            {filteredExperts.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-2">No experts found</p>
            ) : (
              filteredExperts.map(expert => (
                <label
                  key={expert.expert_id}
                  className={`flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-gray-50 ${
                    selectedIds.includes(expert.expert_id) ? 'bg-teal-50' : ''
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(expert.expert_id)}
                    onChange={() => toggleExpert(expert.expert_id)}
                    className="w-4 h-4 text-teal-600"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">{expert.name}</p>
                    <p className="text-xs text-gray-500">{expert.modality_label || expert.modality} • ⭐ {expert.rating}</p>
                  </div>
                </label>
              ))
            )}
          </div>
          
          {/* Footer */}
          <div className="p-2 border-t bg-gray-50 flex justify-between items-center">
            <span className="text-xs text-gray-500">{selectedIds.length} selected</span>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="px-3 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Tag Multi-Select Component for expert tags (life-situation, method, remedy)
const TagMultiSelect = ({ tagType, selectedTags, onChange, maxTags }) => {
  const [tagOptions, setTagOptions] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const loadTags = async () => {
      try {
        const data = await adminFetch('/api/admin/tag-options');
        setTagOptions(data.tag_options || {});
      } catch (err) {
        console.error('Failed to load tag options:', err);
      }
    };
    loadTags();
  }, []);

  if (!tagOptions) return <p className="text-xs text-gray-400">Loading tags...</p>;

  const rawOptions = tagOptions[tagType];
  // life_situation is grouped by category, method & remedy_support are flat arrays
  const isGrouped = rawOptions && !Array.isArray(rawOptions);
  
  let flatOptions = [];
  if (isGrouped) {
    Object.entries(rawOptions).forEach(([category, tags]) => {
      tags.forEach(tag => flatOptions.push({ category, tag }));
    });
  } else if (Array.isArray(rawOptions)) {
    flatOptions = rawOptions.map(tag => ({ category: null, tag }));
  }

  const filtered = search.trim()
    ? flatOptions.filter(o => o.tag.toLowerCase().includes(search.toLowerCase()))
    : flatOptions;

  const toggleTag = (tag) => {
    const current = selectedTags || [];
    if (current.includes(tag)) {
      onChange(current.filter(t => t !== tag));
    } else {
      if (maxTags && current.length >= maxTags) return;
      onChange([...current, tag]);
    }
  };

  const selected = selectedTags || [];

  return (
    <div className="relative">
      {/* Selected tags display */}
      <div
        className="min-h-[40px] w-full px-3 py-2 border border-gray-300 rounded-lg cursor-pointer flex flex-wrap gap-1 items-center"
        onClick={() => setIsOpen(!isOpen)}
        data-testid={`tag-select-${tagType}`}
      >
        {selected.length > 0 ? selected.map(tag => (
          <span key={tag} className="inline-flex items-center gap-1 px-2 py-0.5 bg-teal-100 text-teal-700 text-xs rounded-full">
            {tag}
            <button onClick={(e) => { e.stopPropagation(); toggleTag(tag); }} className="hover:text-red-500">&times;</button>
          </span>
        )) : (
          <span className="text-sm text-gray-400">
            Select tags{maxTags ? ` (max ${maxTags})` : ''}...
          </span>
        )}
      </div>
      
      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-hidden">
          <div className="p-2 border-b">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search tags..."
              className="w-full px-2 py-1.5 text-sm border border-gray-200 rounded"
              autoFocus
            />
          </div>
          <div className="overflow-y-auto max-h-48">
            {isGrouped ? (
              // Grouped display for life_situation tags
              Object.entries(
                filtered.reduce((acc, o) => { (acc[o.category] = acc[o.category] || []).push(o.tag); return acc; }, {})
              ).map(([category, tags]) => (
                <div key={category}>
                  <p className="px-3 py-1 text-[10px] font-bold text-gray-400 uppercase bg-gray-50 sticky top-0">{category}</p>
                  {tags.map(tag => (
                    <label key={tag} className={`flex items-center gap-2 px-3 py-1.5 text-sm cursor-pointer hover:bg-gray-50 ${selected.includes(tag) ? 'bg-teal-50' : ''} ${maxTags && selected.length >= maxTags && !selected.includes(tag) ? 'opacity-40 cursor-not-allowed' : ''}`}>
                      <input type="checkbox" checked={selected.includes(tag)} onChange={() => toggleTag(tag)} className="w-3.5 h-3.5 accent-teal-600" disabled={maxTags && selected.length >= maxTags && !selected.includes(tag)} />
                      <span className="truncate">{tag}</span>
                    </label>
                  ))}
                </div>
              ))
            ) : (
              // Flat display for method/remedy tags
              filtered.map(o => (
                <label key={o.tag} className={`flex items-center gap-2 px-3 py-1.5 text-sm cursor-pointer hover:bg-gray-50 ${selected.includes(o.tag) ? 'bg-teal-50' : ''} ${maxTags && selected.length >= maxTags && !selected.includes(o.tag) ? 'opacity-40 cursor-not-allowed' : ''}`}>
                  <input type="checkbox" checked={selected.includes(o.tag)} onChange={() => toggleTag(o.tag)} className="w-3.5 h-3.5 accent-teal-600" disabled={maxTags && selected.length >= maxTags && !selected.includes(o.tag)} />
                  <span className="truncate">{o.tag}</span>
                </label>
              ))
            )}
            {filtered.length === 0 && <p className="text-sm text-gray-400 text-center py-3">No tags match</p>}
          </div>
          <div className="border-t px-3 py-1.5 flex justify-between items-center bg-gray-50">
            <span className="text-xs text-gray-500">{selected.length} selected{maxTags ? ` / ${maxTags} max` : ''}</span>
            <button onClick={() => setIsOpen(false)} className="text-xs text-teal-600 font-medium">Done</button>
          </div>
        </div>
      )}
    </div>
  );
};



// Topics Manager - with visual Lucide icon picker
const TopicsManager = () => (
  <CatalogManager
    entityType="topics"
    title="Topics"
    icon="📌"
    columns={[
      { key: 'topic_id', label: 'ID' },
      { key: 'icon', label: 'Icon', render: (v) => {
        const Icon = LucideIcons[v];
        return Icon ? <Icon className="w-5 h-5 text-teal-600" /> : v;
      }},
      { key: 'label', label: 'Name' },
      { key: 'tagline', label: 'Tagline' },
      { key: 'order', label: 'Order' },
      { key: 'active', label: 'Active', render: (v) => v === false ? '❌' : '✅' },
    ]}
    formFields={[
      { name: 'topic_id', label: 'Topic ID', isId: true, hint: 'Unique identifier (e.g., career, money, vastu)' },
      { name: 'label', label: 'Display Name' },
      { name: 'icon', label: 'Icon', type: 'icon-picker', default: 'Star' },
      { name: 'tagline', label: 'Tagline' },
      { name: 'color', label: 'Color', type: 'select', options: [
        { value: 'teal', label: 'Teal' },
        { value: 'blue', label: 'Blue' },
        { value: 'purple', label: 'Purple' },
        { value: 'pink', label: 'Pink' },
        { value: 'orange', label: 'Orange' },
        { value: 'green', label: 'Green' },
        { value: 'red', label: 'Red' },
      ], default: 'teal' },
      { name: 'order', label: 'Display Order', type: 'number', default: 99 },
      { name: 'modalities', label: 'Modalities', type: 'array', hint: 'Expert types: vedic_astrologer, numerologist, life_coach' },
      { name: 'active', label: 'Active', type: 'checkbox', default: true },
    ]}
  />
);

// Categories Manager (Homepage groupings)
const CategoriesManager = () => (
  <CatalogManager
    entityType="categories"
    title="Homepage Categories"
    icon="📂"
    columns={[
      { key: 'category_id', label: 'ID' },
      { key: 'title', label: 'Title' },
      { key: 'helper_copy', label: 'Helper Copy' },
      { key: 'order', label: 'Order' },
      { key: 'active', label: 'Active', render: (v) => v === false ? '❌' : '✅' },
    ]}
    formFields={[
      { name: 'category_id', label: 'Category ID', isId: true, hint: 'Unique identifier (e.g., love, career, health)' },
      { name: 'title', label: 'Display Title', hint: 'e.g., Love & Relationships' },
      { name: 'helper_copy', label: 'Helper Copy', hint: 'Subtitle shown under category' },
      { name: 'order', label: 'Display Order', type: 'number', default: 1 },
      { name: 'active', label: 'Active', type: 'checkbox', default: true },
    ]}
  />
);

// Tiles Manager (Homepage tiles, grouped under categories) - With Category, Package & Icon
const TilesManager = () => {
  const [categories, setCategories] = useState([]);
  const [packages, setPackages] = useState([]);
  const [topics, setTopics] = useState([]);
  
  useEffect(() => {
    // Fetch all needed data for dropdowns
    Promise.all([
      adminFetch('/api/admin/categories'),
      adminFetch('/api/admin/tiers'),
      adminFetch('/api/admin/topics'),
    ]).then(([catData, tierData, topicData]) => {
      setCategories(catData.categories || []);
      setPackages(tierData.tiers || []);
      setTopics(topicData.topics || []);
    }).catch(err => console.error('Failed to load data:', err));
  }, []);

  const categoryOptions = [
    { value: '', label: '-- Select Category --' },
    ...categories.map(c => ({ value: c.category_id, label: c.title }))
  ];

  const packageOptions = [
    { value: '', label: '-- No Direct Package (Optional) --' },
    ...packages.map(p => ({ value: p.tier_id, label: `${p.name} (₹${p.price}) - ${p.topic_id || 'No Topic'}` }))
  ];

  const topicOptions = [
    { value: '', label: '-- No Topic Link (Optional) --' },
    ...topics.map(t => ({ value: t.topic_id, label: `${t.label} ${t.icon || ''}` }))
  ];

  return (
    <CatalogManager
      entityType="tiles"
      title="Homepage Tiles"
      icon="🎯"
      columns={[
        { key: 'tile_id', label: 'ID' },
        { key: 'short_title', label: 'Short Title' },
        { key: 'category_id', label: 'Category' },
        { key: 'linked_package_id', label: 'Package', render: (v) => v || '-' },
        { key: 'linked_topic_id', label: 'Topic', render: (v) => v || '-' },
        { key: 'order', label: 'Order' },
        { key: 'active', label: 'Active', render: (v) => v === false ? '❌' : '✅' },
      ]}
      formFields={[
        { name: 'tile_id', label: 'Tile ID', isId: true, hint: 'Unique identifier (e.g., relationship_healing)' },
        { name: 'category_id', label: 'Category', type: 'select', options: categoryOptions, hint: 'Required: Select parent category' },
        { name: 'short_title', label: 'Short Title', hint: 'Shown on tile (e.g., Healing)' },
        { name: 'full_title', label: 'Full Title', hint: 'Full name (e.g., Relationship Healing)' },
        { name: 'icon_type', label: 'Icon', type: 'tile-icon-picker', hint: 'Visual icon shown on tile' },
        { name: 'linked_package_id', label: 'Link to Package', type: 'select', options: packageOptions, hint: 'Optional: Link tile directly to a specific package' },
        { name: 'linked_topic_id', label: 'Link to Topic', type: 'select', options: topicOptions, hint: 'Optional: Link tile to a topic (shows all packages for that topic)' },
        { name: 'order', label: 'Order in Category', type: 'number', default: 1 },
        { name: 'active', label: 'Active', type: 'checkbox', default: true },
      ]}
    />
  );
};

// Experts Manager
const ExpertsManager = () => (
  <CatalogManager
    entityType="experts"
    title="Experts"
    icon="👤"
    columns={[
      { key: 'expert_id', label: 'ID' },
      { key: 'name', label: 'Name' },
      { key: 'modality', label: 'Modality' },
      { key: 'topics', label: 'Topics' },
      { key: 'life_situation_tags', label: 'Best For', render: (v) => Array.isArray(v) && v.length > 0 ? v.slice(0, 2).join(', ') + (v.length > 2 ? '...' : '') : '-' },
      { key: 'rating', label: 'Rating' },
      { key: 'active', label: 'Active', render: (v) => v === false ? '❌' : '✅' },
    ]}
    formFields={[
      { name: 'expert_id', label: 'Expert ID', isId: true, hint: 'Unique identifier' },
      { name: 'name', label: 'Full Name' },
      { name: 'modality', label: 'Primary Modality', hint: 'e.g., vedic_astrologer, numerologist, tarot' },
      { name: 'modality_label', label: 'Modality Display Name', hint: 'e.g., Vedic Astrologer' },
      { name: 'bio', label: 'Bio', type: 'textarea' },
      { name: 'languages', label: 'Languages', default: 'Hindi, English' },
      { name: 'years_experience', label: 'Years Experience', type: 'number', default: 5 },
      { name: 'rating', label: 'Rating (1–5)', type: 'number', decimal: true, min: 1, max: 5, default: 4.5 },
      { name: 'total_consults', label: 'Total Consults', type: 'number', default: 0 },
      { name: 'topics', label: 'Topics', type: 'array', hint: 'Topic IDs this expert can serve' },
      { name: 'photo_url', label: 'Photo', type: 'image-upload' },
      { name: 'life_situation_tags', label: 'Best For Tags (Life Situations)', type: 'tag-multi-select', tagType: 'life_situation', maxTags: 5, hint: '3-5 tags shown on profile as "Best for"' },
      { name: 'method_tags', label: 'Method Tags', type: 'tag-multi-select', tagType: 'method', maxTags: 3, hint: '1-3 tags for how the expert works' },
      { name: 'remedy_tags', label: 'Remedy/Support Tags', type: 'tag-multi-select', tagType: 'remedy_support', maxTags: 2, hint: '0-2 tags for additional services' },
      { name: 'active', label: 'Active', type: 'checkbox', default: true },
      { name: 'consultations', label: 'Consultation Options', type: 'consultation-list', hint: 'Add 1–4 paid session options (duration, price, what the user gets)' },
      { name: 'offers_free_call', label: 'Offers Free Consultation Call', type: 'checkbox', default: false, hint: 'If enabled, this expert appears in the free call onboarding wizard' },
      { name: 'timezone', label: 'Timezone', type: 'select', default: 'Asia/Kolkata', options: [
        { value: 'Asia/Kolkata', label: 'India (IST, UTC+5:30)' },
        { value: 'Asia/Dubai', label: 'Dubai (GST, UTC+4)' },
        { value: 'UTC', label: 'UTC' },
      ]},
      { name: 'weekly_availability', label: 'Weekly Availability', type: 'weekly-availability', hint: 'Days and hours this expert accepts free consultation bookings' },
    ]}
  />
);

// Remedies Manager
const RemediesCatalogManager = () => {
  const [experts, setExperts] = useState([]);
  useEffect(() => {
    adminFetch('/api/admin/experts')
      .then(data => setExperts(data.experts || []))
      .catch(err => console.error('Failed to load experts:', err));
  }, []);

  return (
    <CatalogManager
      entityType="remedies-catalog"
      dataKey="remedies"
      title="Remedies Catalog"
      icon="🙏"
      columns={[
        { key: 'remedy_id', label: 'ID' },
        { key: 'image', label: '' },
        { key: 'title', label: 'Title' },
        { key: 'category', label: 'Category' },
        { key: 'price', label: 'Price', render: (v) => formatCurrency(v) },
        { key: 'expert_ids', label: 'Experts', render: (v) => Array.isArray(v) && v.length > 0 ? `${v.length} expert${v.length > 1 ? 's' : ''}` : '-' },
        { key: 'featured', label: 'Featured', render: (v) => v ? '⭐' : '' },
        { key: 'active', label: 'Active', render: (v) => v === false ? '❌' : '✅' },
      ]}
      formFields={[
        { name: 'remedy_id', label: 'Remedy ID', isId: true, hint: 'Unique identifier (e.g., chakra_balance)' },
        { name: 'title', label: 'Title' },
        { name: 'subtitle', label: 'Subtitle' },
        { name: 'category', label: 'Category', type: 'select', options: [
          { value: 'healing', label: 'Healing Programs' },
          { value: 'pooja', label: 'Pooja' },
          { value: 'gemstone', label: 'Gemstone' },
          { value: 'kit', label: 'Kit' },
          { value: 'ritual', label: 'Ritual' },
        ]},
        { name: 'price', label: 'Price (INR)', type: 'number' },
        { name: 'description', label: 'Description', type: 'textarea' },
        { name: 'benefits', label: 'Benefits', type: 'array', hint: 'Comma-separated benefits' },
        { name: 'helps_with', label: 'Helps With', type: 'array', hint: 'What problems it solves' },
        { name: 'image', label: 'Icon (emoji)', default: '✨' },
        { name: 'expert_ids', label: 'Experts offering this remedy', type: 'expert-multi-select', experts, hint: 'Select which experts offer this remedy on their profile' },
        { name: 'featured', label: 'Featured', type: 'checkbox', default: false },
        { name: 'active', label: 'Active', type: 'checkbox', default: true },
      ]}
    />
  );
};

// Consultation Editor - per-expert session options
const DURATION_OPTIONS = [15, 30, 45, 60];
const emptyConsultation = () => ({ duration_mins: 30, price_inr: '', title: '', what_you_get: '' });

const ConsultationEditor = ({ value = [], onChange }) => {
  const add = () => onChange([...value, emptyConsultation()]);
  const remove = (i) => onChange(value.filter((_, idx) => idx !== i));
  const update = (i, field, val) => {
    const next = value.map((c, idx) => idx === i ? { ...c, [field]: val } : c);
    onChange(next);
  };

  return (
    <div className="space-y-3">
      {value.map((c, i) => (
        <div key={i} className="border border-gray-200 rounded-lg p-3 space-y-2 bg-gray-50">
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="text-xs text-gray-500">Duration</label>
              <select
                value={c.duration_mins}
                onChange={(e) => update(i, 'duration_mins', parseInt(e.target.value))}
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm"
              >
                {DURATION_OPTIONS.map(d => <option key={d} value={d}>{d} mins</option>)}
              </select>
            </div>
            <div className="flex-1">
              <label className="text-xs text-gray-500">Price (₹)</label>
              <input
                type="number"
                value={c.price_inr}
                onChange={(e) => update(i, 'price_inr', parseInt(e.target.value) || '')}
                placeholder="e.g. 1200"
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm"
              />
            </div>
            <button onClick={() => remove(i)} className="mt-5 text-red-400 hover:text-red-600 text-lg font-bold">×</button>
          </div>
          <div>
            <label className="text-xs text-gray-500">Session title</label>
            <input
              type="text"
              value={c.title}
              onChange={(e) => update(i, 'title', e.target.value)}
              placeholder="e.g. Clarity Session"
              className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500">What you get</label>
            <textarea
              value={c.what_you_get}
              onChange={(e) => update(i, 'what_you_get', e.target.value)}
              placeholder="e.g. Birth chart reading + answer to your question + remedy guidance"
              rows={2}
              className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm resize-none"
            />
          </div>
        </div>
      ))}
      {value.length < 4 && (
        <button
          onClick={add}
          className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-500 hover:border-teal-400 hover:text-teal-600 transition-colors"
        >
          + Add consultation option
        </button>
      )}
    </div>
  );
};

// Package Content Editor - Full rich content editor for packages
const PackageContentEditor = ({ content, onChange }) => {
  const [expanded, setExpanded] = useState({
    hero: true,
    overview: false,
    helps: false,
    analysis: false,
    deliverables: false,
    custom: false
  });

  const toggleSection = (section) => {
    setExpanded(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const updateContent = (path, value) => {
    const newContent = { ...content };
    const keys = path.split('.');
    let obj = newContent;
    for (let i = 0; i < keys.length - 1; i++) {
      if (!obj[keys[i]]) obj[keys[i]] = {};
      obj = obj[keys[i]];
    }
    obj[keys[keys.length - 1]] = value;
    onChange(newContent);
  };

  const addHelpSection = () => {
    const sections = content?.help_sections || [];
    updateContent('help_sections', [...sections, { title: '', items: [] }]);
  };

  const updateHelpSection = (index, field, value) => {
    const sections = [...(content?.help_sections || [])];
    sections[index] = { ...sections[index], [field]: value };
    updateContent('help_sections', sections);
  };

  const removeHelpSection = (index) => {
    const sections = (content?.help_sections || []).filter((_, i) => i !== index);
    updateContent('help_sections', sections);
  };

  const addAnalysisSection = () => {
    const sections = content?.analysis_sections || [];
    updateContent('analysis_sections', [...sections, { title: '', items: [] }]);
  };

  const updateAnalysisSection = (index, field, value) => {
    const sections = [...(content?.analysis_sections || [])];
    sections[index] = { ...sections[index], [field]: value };
    updateContent('analysis_sections', sections);
  };

  const removeAnalysisSection = (index) => {
    const sections = (content?.analysis_sections || []).filter((_, i) => i !== index);
    updateContent('analysis_sections', sections);
  };

  const SectionHeader = ({ title, section, hasContent }) => (
    <button
      type="button"
      onClick={() => toggleSection(section)}
      className={`w-full flex items-center justify-between p-3 rounded-lg text-left ${
        hasContent ? 'bg-teal-50 border border-teal-200' : 'bg-gray-50 border border-gray-200'
      }`}
    >
      <span className="font-medium text-gray-800">{title}</span>
      <div className="flex items-center gap-2">
        {hasContent && <span className="text-xs text-teal-600">✓ Has content</span>}
        <LucideIcons.ChevronDown className={`w-4 h-4 transition-transform ${expanded[section] ? 'rotate-180' : ''}`} />
      </div>
    </button>
  );

  return (
    <div className="space-y-3 border border-gray-200 rounded-lg p-3 bg-gray-50">
      <p className="text-sm font-medium text-gray-700 mb-2">📝 Rich Package Content</p>
      
      {/* Hero Section */}
      <div>
        <SectionHeader 
          title="1️⃣ Hero Section" 
          section="hero" 
          hasContent={content?.hero_title || content?.hero_subtitle}
        />
        {expanded.hero && (
          <div className="mt-2 p-3 bg-white rounded-lg border space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Hero Title</label>
              <input
                type="text"
                value={content?.hero_title || ''}
                onChange={(e) => updateContent('hero_title', e.target.value)}
                placeholder="e.g., Not Official Yet"
                className="w-full px-3 py-2 border rounded text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Hero Subtitle</label>
              <textarea
                value={content?.hero_subtitle || ''}
                onChange={(e) => updateContent('hero_subtitle', e.target.value)}
                placeholder="e.g., You're dating. It feels meaningful. But it's still undefined."
                className="w-full px-3 py-2 border rounded text-sm"
                rows={2}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Trust Line</label>
              <input
                type="text"
                value={content?.trust_line || ''}
                onChange={(e) => updateContent('trust_line', e.target.value)}
                placeholder="e.g., Senior experts • Unlimited follow-ups • Private & secure"
                className="w-full px-3 py-2 border rounded text-sm"
              />
            </div>
          </div>
        )}
      </div>

      {/* Package Overview */}
      <div>
        <SectionHeader 
          title="2️⃣ Package Overview" 
          section="overview" 
          hasContent={content?.overview_title || content?.overview_description}
        />
        {expanded.overview && (
          <div className="mt-2 p-3 bg-white rounded-lg border space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Overview Title</label>
              <input
                type="text"
                value={content?.overview_title || ''}
                onChange={(e) => updateContent('overview_title', e.target.value)}
                placeholder="e.g., Unlimited Guidance (7 Days)"
                className="w-full px-3 py-2 border rounded text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Overview Description</label>
              <textarea
                value={content?.overview_description || ''}
                onChange={(e) => updateContent('overview_description', e.target.value)}
                placeholder="Describe what the package offers..."
                className="w-full px-3 py-2 border rounded text-sm"
                rows={4}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Includes (one per line)</label>
              <textarea
                value={(content?.includes || []).join('\n')}
                onChange={(e) => updateContent('includes', e.target.value.split('\n').filter(Boolean))}
                placeholder="Structured relationship analysis&#10;Unlimited chat for 7 days&#10;Written clarity note"
                className="w-full px-3 py-2 border rounded text-sm font-mono"
                rows={5}
              />
            </div>
          </div>
        )}
      </div>

      {/* What This Helps With */}
      <div>
        <SectionHeader 
          title="3️⃣ What This Helps With" 
          section="helps" 
          hasContent={(content?.help_sections || []).length > 0}
        />
        {expanded.helps && (
          <div className="mt-2 p-3 bg-white rounded-lg border space-y-3">
            {(content?.help_sections || []).map((section, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded border">
                <div className="flex justify-between items-center mb-2">
                  <input
                    type="text"
                    value={section.title || ''}
                    onChange={(e) => updateHelpSection(idx, 'title', e.target.value)}
                    placeholder="Section title (e.g., CLARITY, TIMELINE, SUPPORT)"
                    className="flex-1 px-2 py-1 border rounded text-sm font-medium"
                  />
                  <button
                    type="button"
                    onClick={() => removeHelpSection(idx)}
                    className="ml-2 p-1 text-red-500 hover:bg-red-50 rounded"
                  >
                    <LucideIcons.Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <textarea
                  value={(section.items || []).join('\n')}
                  onChange={(e) => updateHelpSection(idx, 'items', e.target.value.split('\n').filter(Boolean))}
                  placeholder="Bullet points (one per line)&#10;Is this moving toward commitment?&#10;Are there hidden red flags?"
                  className="w-full px-2 py-1 border rounded text-sm font-mono"
                  rows={4}
                />
              </div>
            ))}
            <button
              type="button"
              onClick={addHelpSection}
              className="w-full py-2 border-2 border-dashed border-gray-300 rounded text-sm text-gray-500 hover:border-teal-400 hover:text-teal-600"
            >
              + Add Help Section (e.g., Clarity, Timeline, Support)
            </button>
          </div>
        )}
      </div>

      {/* How We Analyse */}
      <div>
        <SectionHeader 
          title="4️⃣ How We Analyse" 
          section="analysis" 
          hasContent={content?.analysis_intro || (content?.analysis_sections || []).length > 0}
        />
        {expanded.analysis && (
          <div className="mt-2 p-3 bg-white rounded-lg border space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Intro Text</label>
              <textarea
                value={content?.analysis_intro || ''}
                onChange={(e) => updateContent('analysis_intro', e.target.value)}
                placeholder="Your guidance is based on structured Vedic analysis, not guesswork."
                className="w-full px-3 py-2 border rounded text-sm"
                rows={2}
              />
            </div>
            {(content?.analysis_sections || []).map((section, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded border">
                <div className="flex justify-between items-center mb-2">
                  <input
                    type="text"
                    value={section.title || ''}
                    onChange={(e) => updateAnalysisSection(idx, 'title', e.target.value)}
                    placeholder="Section title (e.g., We look at:, If partner details available:)"
                    className="flex-1 px-2 py-1 border rounded text-sm font-medium"
                  />
                  <button
                    type="button"
                    onClick={() => removeAnalysisSection(idx)}
                    className="ml-2 p-1 text-red-500 hover:bg-red-50 rounded"
                  >
                    <LucideIcons.Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <textarea
                  value={(section.items || []).join('\n')}
                  onChange={(e) => updateAnalysisSection(idx, 'items', e.target.value.split('\n').filter(Boolean))}
                  placeholder="Analysis points (one per line)&#10;5th house (romance & bonding)&#10;7th house (commitment potential)"
                  className="w-full px-2 py-1 border rounded text-sm font-mono"
                  rows={4}
                />
              </div>
            ))}
            <button
              type="button"
              onClick={addAnalysisSection}
              className="w-full py-2 border-2 border-dashed border-gray-300 rounded text-sm text-gray-500 hover:border-teal-400 hover:text-teal-600"
            >
              + Add Analysis Section
            </button>
          </div>
        )}
      </div>

      {/* Deliverables */}
      <div>
        <SectionHeader 
          title="5️⃣ What You Receive" 
          section="deliverables" 
          hasContent={(content?.deliverables || []).length > 0}
        />
        {expanded.deliverables && (
          <div className="mt-2 p-3 bg-white rounded-lg border">
            <label className="block text-xs font-medium text-gray-600 mb-1">Deliverables (one per line)</label>
            <textarea
              value={(content?.deliverables || []).join('\n')}
              onChange={(e) => updateContent('deliverables', e.target.value.split('\n').filter(Boolean))}
              placeholder="Clear direction: Invest / Slow Down / Reconsider&#10;A written clarity summary&#10;A timing window table&#10;Unlimited topic-specific chat for 7 days"
              className="w-full px-3 py-2 border rounded text-sm font-mono"
              rows={5}
            />
          </div>
        )}
      </div>

      {/* Custom Sections - Add unlimited additional sections */}
      <div>
        <SectionHeader 
          title="➕ Custom Sections" 
          section="custom" 
          hasContent={(content?.custom_sections || []).length > 0}
        />
        {expanded.custom && (
          <div className="mt-2 p-3 bg-white rounded-lg border space-y-3">
            <p className="text-xs text-gray-500 mb-2">Add any additional sections you need. Each section can have a title and content (bullet points or paragraphs).</p>
            
            {(content?.custom_sections || []).map((section, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded border">
                <div className="flex justify-between items-start gap-2 mb-2">
                  <div className="flex-1 space-y-2">
                    <input
                      type="text"
                      value={section.title || ''}
                      onChange={(e) => {
                        const sections = [...(content?.custom_sections || [])];
                        sections[idx] = { ...sections[idx], title: e.target.value };
                        updateContent('custom_sections', sections);
                      }}
                      placeholder="Section Title (e.g., PRICING OPTIONS, FAQ, GUARANTEE)"
                      className="w-full px-2 py-1 border rounded text-sm font-medium"
                    />
                    <select
                      value={section.type || 'bullets'}
                      onChange={(e) => {
                        const sections = [...(content?.custom_sections || [])];
                        sections[idx] = { ...sections[idx], type: e.target.value };
                        updateContent('custom_sections', sections);
                      }}
                      className="px-2 py-1 border rounded text-xs"
                    >
                      <option value="bullets">Bullet Points</option>
                      <option value="text">Paragraph Text</option>
                      <option value="numbered">Numbered List</option>
                    </select>
                  </div>
                  <div className="flex gap-1">
                    {idx > 0 && (
                      <button
                        type="button"
                        onClick={() => {
                          const sections = [...(content?.custom_sections || [])];
                          [sections[idx-1], sections[idx]] = [sections[idx], sections[idx-1]];
                          updateContent('custom_sections', sections);
                        }}
                        className="p-1 text-gray-500 hover:bg-gray-200 rounded"
                        title="Move Up"
                      >
                        <LucideIcons.ChevronUp className="w-4 h-4" />
                      </button>
                    )}
                    {idx < (content?.custom_sections || []).length - 1 && (
                      <button
                        type="button"
                        onClick={() => {
                          const sections = [...(content?.custom_sections || [])];
                          [sections[idx], sections[idx+1]] = [sections[idx+1], sections[idx]];
                          updateContent('custom_sections', sections);
                        }}
                        className="p-1 text-gray-500 hover:bg-gray-200 rounded"
                        title="Move Down"
                      >
                        <LucideIcons.ChevronDown className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => {
                        const sections = (content?.custom_sections || []).filter((_, i) => i !== idx);
                        updateContent('custom_sections', sections);
                      }}
                      className="p-1 text-red-500 hover:bg-red-50 rounded"
                      title="Delete Section"
                    >
                      <LucideIcons.Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <textarea
                  value={section.type === 'text' 
                    ? (section.content || '') 
                    : (section.items || []).join('\n')}
                  onChange={(e) => {
                    const sections = [...(content?.custom_sections || [])];
                    if (section.type === 'text') {
                      sections[idx] = { ...sections[idx], content: e.target.value };
                    } else {
                      sections[idx] = { ...sections[idx], items: e.target.value.split('\n').filter(Boolean) };
                    }
                    updateContent('custom_sections', sections);
                  }}
                  placeholder={section.type === 'text' 
                    ? "Enter paragraph text..." 
                    : "Enter items (one per line)..."}
                  className="w-full px-2 py-1 border rounded text-sm font-mono"
                  rows={4}
                />
              </div>
            ))}
            
            <button
              type="button"
              onClick={() => {
                const sections = content?.custom_sections || [];
                updateContent('custom_sections', [...sections, { title: '', type: 'bullets', items: [] }]);
              }}
              className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-500 hover:border-teal-400 hover:text-teal-600 flex items-center justify-center gap-2"
            >
              <LucideIcons.Plus className="w-4 h-4" />
              Add Custom Section
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Tiers Manager - with Expert Assignment
const TiersManager = () => {
  const [experts, setExperts] = useState([]);
  const [topics, setTopics] = useState([]);
  
  useEffect(() => {
    Promise.all([
      adminFetch('/api/admin/experts'),
      adminFetch('/api/admin/topics'),
    ]).then(([expertData, topicData]) => {
      setExperts(expertData.experts || []);
      setTopics(topicData.topics || []);
    }).catch(err => console.error('Failed to load data:', err));
  }, []);

  const topicOptions = [
    { value: '', label: '-- No Topic (Standalone Package) --' },
    ...topics.map(t => ({ value: t.topic_id, label: `${t.label} ${t.icon || ''}` }))
  ];

  return (
    <CatalogManager
      entityType="tiers"
      title="Packages / Tiers"
      icon="📦"
      columns={[
        { key: 'tier_id', label: 'ID' },
        { key: 'name', label: 'Name' },
        { key: 'topic_id', label: 'Topic', render: (v) => v || '(Standalone)' },
        { key: 'price', label: 'Price', render: (v) => formatCurrency(v) },
        { key: 'duration_days', label: 'Days', render: (v, item) => v || (item.duration_weeks ? `${item.duration_weeks}w` : '-') },
        { key: 'expert_ids', label: 'Experts', render: (v) => Array.isArray(v) && v.length > 0 ? `${v.length} assigned` : '-' },
        { key: 'content', label: 'Content', render: (v) => v?.hero_title ? '📝' : '-' },
        { key: 'active', label: 'Active', render: (v) => v === false ? '❌' : '✅' },
      ]}
      formFields={[
        { name: 'tier_id', label: 'Package ID', isId: true, hint: 'Unique identifier (e.g., not_official_yet)' },
        { name: 'name', label: 'Display Name', hint: 'e.g., Not Official Yet, Unlimited Guidance' },
        { name: 'topic_id', label: 'Link to Topic', type: 'select', options: topicOptions, hint: 'Optional: Link to a topic or leave as standalone package' },
        { name: 'price', label: 'Base Price (₹ paid to expert)', type: 'number', hint: 'What the expert earns for this package' },
        { name: 'niro_margin_pct', label: 'Niro Margin (%)', type: 'number', default: 0, hint: 'Added on top of base price. Customer pays: base × (1 + margin%). E.g. base ₹2,000 + 50% = ₹3,000 shown to customer.' },
        { name: 'duration_days', label: 'Duration (days)', type: 'number', default: 7, hint: 'e.g., 7 for a week' },
        { name: 'duration_weeks', label: 'Duration (weeks)', type: 'number', default: 0, hint: 'Alternative to days' },
        { name: 'calls_included', label: 'Calls Included', type: 'number', default: 0, hint: '0 = no calls, unlimited chat' },
        { name: 'call_duration_mins', label: 'Call Duration (mins)', type: 'number', default: 30 },
        { name: 'features', label: 'Quick Features', type: 'array', hint: 'Short bullet points for card display' },
        { name: 'description', label: 'Short Description', type: 'textarea', hint: 'Brief overview for listings' },
        { name: 'expert_ids', label: 'Assigned Astrologers', type: 'expert-multi-select', experts: experts, hint: 'Select astrologers for this package' },
        { name: 'popular', label: 'Mark as Popular', type: 'checkbox', default: false },
        { name: 'active', label: 'Active', type: 'checkbox', default: true },
        { name: 'content', label: 'Full Package Content', type: 'package-content', hint: 'Rich content for package detail page' },
      ]}
    />
  );
};

// ============================================================================
// BULK UPLOAD
// ============================================================================
const BulkUpload = () => {
  const [jsonInput, setJsonInput] = useState('');
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const downloadTemplate = async () => {
    try {
      const data = await adminFetch('/api/admin/bulk-upload/template');
      if (data.ok) {
        const blob = new Blob([JSON.stringify(data.template, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'niro_bulk_upload_template.json';
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      setError('Failed to download template: ' + err.message);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target.result;
      setJsonInput(text);
      try {
        const parsed = JSON.parse(text);
        setPreview(parsed);
        setError('');
      } catch (err) {
        setError('Invalid JSON file. Please check the format.');
        setPreview(null);
      }
    };
    reader.readAsText(file);
  };

  const handleTextParse = () => {
    try {
      const parsed = JSON.parse(jsonInput);
      setPreview(parsed);
      setError('');
    } catch (err) {
      setError('Invalid JSON. Please check syntax.');
      setPreview(null);
    }
  };

  const handleUpload = async () => {
    if (!preview) return;
    setUploading(true);
    setError('');
    setResult(null);
    try {
      const data = await adminFetch('/api/admin/bulk-upload', {
        method: 'POST',
        body: JSON.stringify(preview),
      });
      setResult(data);
    } catch (err) {
      setError('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800" data-testid="bulk-upload-title">Bulk Upload</h2>
        <button
          onClick={downloadTemplate}
          className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center gap-2"
          data-testid="download-template-btn"
        >
          <LucideIcons.Download className="w-4 h-4" />
          Download Template
        </button>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800">
        <strong>How it works:</strong>
        <ol className="mt-2 space-y-1 list-decimal list-inside">
          <li>Download the JSON template and fill in your data</li>
          <li>Upload the file or paste JSON below</li>
          <li>Preview what will be created</li>
          <li>Click "Upload" to create everything in one go</li>
        </ol>
        <p className="mt-2 text-xs text-blue-600">Creates a category + tiles + packages with all content in a single upload. Existing items with the same ID will be updated.</p>
      </div>

      {/* File Upload */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="font-semibold text-gray-800 mb-3">Upload JSON File</h3>
        <div className="flex items-center gap-4">
          <label className="flex-1 border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer hover:border-teal-400 hover:bg-teal-50/30 transition-colors">
            <LucideIcons.Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
            <p className="text-sm text-gray-600">Click to upload JSON file</p>
            <p className="text-xs text-gray-400 mt-1">.json files only</p>
            <input
              type="file"
              accept=".json"
              onChange={handleFileUpload}
              className="hidden"
              data-testid="bulk-upload-file-input"
            />
          </label>
        </div>

        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Or paste JSON directly:</h4>
          <textarea
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg font-mono text-sm"
            rows={8}
            placeholder='{"category": {...}, "tiles": [...], "packages": [...]}'
            data-testid="bulk-upload-json-input"
          />
          <button
            onClick={handleTextParse}
            className="mt-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm"
            data-testid="bulk-upload-parse-btn"
          >
            Parse JSON
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700" data-testid="bulk-upload-error">
          {error}
        </div>
      )}

      {/* Preview */}
      {preview && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100" data-testid="bulk-upload-preview">
          <h3 className="font-semibold text-gray-800 mb-4">Preview — What will be created:</h3>

          {preview.category && (
            <div className="mb-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
              <h4 className="text-sm font-semibold text-purple-800 mb-1">Category</h4>
              <p className="text-sm text-purple-700">
                <strong>{preview.category.title}</strong> (ID: {preview.category.category_id}) — Order: {preview.category.order ?? '?'}
              </p>
            </div>
          )}

          {preview.tiles?.length > 0 && (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="text-sm font-semibold text-blue-800 mb-2">Tiles ({preview.tiles.length})</h4>
              <div className="space-y-1">
                {preview.tiles.map((t, i) => (
                  <p key={i} className="text-sm text-blue-700">
                    {i + 1}. <strong>{t.short_title}</strong> (ID: {t.tile_id})
                    {t.linked_package_id && <span className="text-blue-500"> → links to {t.linked_package_id}</span>}
                  </p>
                ))}
              </div>
            </div>
          )}

          {preview.packages?.length > 0 && (
            <div className="mb-4 p-3 bg-green-50 rounded-lg border border-green-200">
              <h4 className="text-sm font-semibold text-green-800 mb-2">Packages ({preview.packages.length})</h4>
              <div className="space-y-1">
                {preview.packages.map((p, i) => (
                  <p key={i} className="text-sm text-green-700">
                    {i + 1}. <strong>{p.name}</strong> (ID: {p.tier_id}) — {formatCurrency(p.price)} / {p.duration_days || 7} days
                    {p.content?.hero_title && <span className="text-green-500"> — has rich content</span>}
                  </p>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full mt-4 py-3 bg-teal-600 text-white font-semibold rounded-lg hover:bg-teal-700 disabled:opacity-50 flex items-center justify-center gap-2"
            data-testid="bulk-upload-submit-btn"
          >
            {uploading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <LucideIcons.Upload className="w-4 h-4" />
                Upload & Create All
              </>
            )}
          </button>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className={`rounded-xl p-4 border ${result.ok ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`} data-testid="bulk-upload-result">
          <h3 className={`font-semibold mb-2 ${result.ok ? 'text-green-800' : 'text-red-800'}`}>
            {result.ok ? 'Upload Successful' : 'Upload Failed'}
          </h3>
          <p className="text-sm text-gray-700 mb-2">{result.message}</p>
          {result.results && (
            <div className="text-sm space-y-1">
              <p>Category: {result.results.category_created ? 'Created/Updated' : 'Not included'}</p>
              <p>Tiles: {result.results.tiles_created} created/updated</p>
              <p>Packages: {result.results.packages_created} created/updated</p>
              {result.results.errors?.length > 0 && (
                <div className="mt-2 p-2 bg-red-100 rounded text-red-700">
                  <p className="font-medium">Errors:</p>
                  {result.results.errors.map((e, i) => <p key={i} className="text-xs">{e}</p>)}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ============================================================================
// MAIN ADMIN DASHBOARD
// ============================================================================
export default function AdminDashboard() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [environment, setEnvironment] = useState('all');
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = getAdminToken();
      if (token) {
        try {
          const data = await adminFetch('/api/admin/verify');
          if (data.ok) setIsLoggedIn(true);
        } catch (err) {
          clearAdminToken();
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  useEffect(() => {
    if (isLoggedIn) {
      adminFetch('/api/admin/stats').then(data => setStats(data.stats)).catch(console.error);
    }
  }, [isLoggedIn]);

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-gray-100"><p>Loading...</p></div>;
  if (!isLoggedIn) return <AdminLogin onLogin={() => setIsLoggedIn(true)} />;

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'users', label: 'Users', icon: '👥' },
    { id: 'orders', label: 'Orders', icon: '💰' },
    { id: 'plans', label: 'Plans', icon: '📦' },
    { id: 'remedies', label: 'Remedy Orders', icon: '🙏' },
    { id: 'divider1', label: '─── Homepage ───', icon: '' },
    { id: 'manage-categories', label: 'Categories (3)', icon: '📂' },
    { id: 'manage-tiles', label: 'Tiles (18)', icon: '🎯' },
    { id: 'divider2', label: '─── Catalog ───', icon: '' },
    { id: 'manage-topics', label: 'Topics', icon: '📌' },
    { id: 'manage-experts', label: 'Experts', icon: '👤' },
    { id: 'manage-remedies', label: 'Remedies', icon: '✨' },
    { id: 'manage-tiers', label: 'Packages', icon: '🎁' },
    { id: 'divider3', label: '─── Tools ───', icon: '' },
    { id: 'bulk-upload', label: 'Bulk Upload', icon: '📤' },
  ];

  const renderContent = () => {
    switch (currentPage) {
      case 'users': return <UsersList environment={environment} />;
      case 'orders': return <OrdersList environment={environment} />;
      case 'plans': return <PlansList environment={environment} />;
      case 'remedies': return <RemedyOrdersList environment={environment} />;
      case 'manage-categories': return <CategoriesManager />;
      case 'manage-tiles': return <TilesManager />;
      case 'manage-topics': return <TopicsManager />;
      case 'manage-experts': return <ExpertsManager />;
      case 'manage-remedies': return <RemediesCatalogManager />;
      case 'manage-tiers': return <TiersManager />;
      case 'bulk-upload': return <BulkUpload />;
      default: return <DashboardHome stats={stats} onNavigate={setCurrentPage} environment={environment} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <div className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6 border-b border-gray-800"><h1 className="text-xl font-bold">Niro Admin</h1></div>
        <nav className="flex-1 p-4">
          {navItems.map((item) => (
            item.id.startsWith('divider') ? (
              <div key={item.id} className="text-xs text-gray-500 px-4 py-3 mt-2">{item.label}</div>
            ) : (
              <button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 ${currentPage === item.id ? 'bg-teal-600' : 'hover:bg-gray-800'}`}
              >
                <span>{item.icon}</span><span>{item.label}</span>
              </button>
            )
          ))}
        </nav>
        <div className="p-4 border-t border-gray-800">
          <button onClick={() => { clearAdminToken(); setIsLoggedIn(false); }} className="w-full px-4 py-2 text-red-400 hover:bg-gray-800 rounded-lg">Logout</button>
        </div>
      </div>
      <div className="flex-1 flex flex-col">
        <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800 capitalize">{currentPage.replace('manage-', '').replace('-', ' ')}</h2>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowPreview(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-teal-500 to-teal-600 text-white rounded-lg hover:from-teal-600 hover:to-teal-700 transition-all shadow-sm"
              data-testid="preview-homepage-btn"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Preview Homepage
            </button>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Environment:</span>
              <select
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm"
              >
                <option value="all">All</option>
                <option value="production">Production</option>
                <option value="preview">Preview</option>
              </select>
            </div>
          </div>
        </header>
        <main className="flex-1 p-6 overflow-y-auto">{renderContent()}</main>
      </div>
      
      {/* Homepage Preview Modal */}
      <HomepagePreview isOpen={showPreview} onClose={() => setShowPreview(false)} />
    </div>
  );
}
