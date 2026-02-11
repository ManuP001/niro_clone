import React, { useState, useEffect } from 'react';
import { getBackendUrl } from '../../config';

/**
 * Admin Dashboard - Full featured admin panel
 * 
 * Features:
 * - Dashboard overview with stats
 * - User/Order/Plan management
 * - Hierarchical homepage management (Categories -> Tiles)
 * - Catalog management (Topics, Experts, Remedies, Packages)
 * - Live Homepage Preview
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
          <button
            onClick={handleSeedData}
            disabled={seeding}
            className="px-4 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 disabled:opacity-50"
          >
            {seeding ? 'Refreshing...' : '🔄 Refresh Catalog'}
          </button>
        </div>
      )}
      
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
        <a
          href={`${BACKEND_URL}/api/admin/export/users?source=${source}`}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm"
          onClick={(e) => {
            e.preventDefault();
            const token = getAdminToken();
            window.open(`${BACKEND_URL}/api/admin/export/users?source=${source}`, '_blank');
          }}
        >
          Export CSV
        </a>
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
          onClick={() => window.open(`${BACKEND_URL}/api/admin/export/orders`, '_blank')}
          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm"
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
      
      // Clean up form data - remove empty strings for optional fields, keep only changed values
      const cleanedData = {};
      for (const [key, value] of Object.entries(formData)) {
        // Skip empty strings (treat as "no change" for PUT)
        if (value === '' || value === null || value === undefined) continue;
        // For arrays, skip empty arrays
        if (Array.isArray(value) && value.length === 0) continue;
        cleanedData[key] = value;
      }
      
      if (editItem) {
        // For updates, only send fields that have values
        await adminFetch(`/api/admin/${entityType}/${editItem[idField]}`, {
          method: 'PUT',
          body: JSON.stringify(cleanedData),
        });
      } else {
        // For creates, send all data including required fields
        await adminFetch(`/api/admin/${entityType}`, {
          method: 'POST',
          body: JSON.stringify(cleanedData),
        });
      }
      setShowModal(false);
      loadItems();
    } catch (err) {
      setError(err.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (item) => {
    const idField = formFields.find(f => f.isId)?.name || `${entityType.slice(0, -1)}_id`;
    if (!window.confirm(`Are you sure you want to deactivate this item?`)) return;
    try {
      await adminFetch(`/api/admin/${entityType}/${item[idField]}`, { method: 'DELETE' });
      loadItems();
    } catch (err) {
      alert('Failed to delete: ' + err.message);
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

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              {columns.map(col => (
                <th key={col.key} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{col.label}</th>
              ))}
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td colSpan={columns.length + 1} className="px-4 py-8 text-center text-gray-500">Loading...</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={columns.length + 1} className="px-4 py-8 text-center text-gray-500">No items found. Click "Seed Data" to initialize catalog.</td></tr>
            ) : (
              items.map((item, idx) => (
                <tr key={idx} className={`hover:bg-gray-50 ${item.active === false ? 'opacity-50' : ''}`}>
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
              ))
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
                      value={formData[field.name] || 0}
                      onChange={(e) => setFormData({ ...formData, [field.name]: parseInt(e.target.value) || 0 })}
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

// Topics Manager
const TopicsManager = () => (
  <CatalogManager
    entityType="topics"
    title="Topics"
    icon="📌"
    columns={[
      { key: 'topic_id', label: 'ID' },
      { key: 'icon', label: 'Icon' },
      { key: 'label', label: 'Name' },
      { key: 'tagline', label: 'Tagline' },
      { key: 'order', label: 'Order' },
      { key: 'active', label: 'Active', render: (v) => v === false ? '❌' : '✅' },
    ]}
    formFields={[
      { name: 'topic_id', label: 'Topic ID', isId: true, hint: 'Unique identifier (e.g., career, money, vastu)' },
      { name: 'label', label: 'Display Name' },
      { name: 'icon', label: 'Icon (emoji)', default: '📌' },
      { name: 'tagline', label: 'Tagline' },
      { name: 'color', label: 'Color', default: 'teal' },
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

// Tiles Manager (Homepage tiles, grouped under categories) - With Category Dropdown
const TilesManager = () => {
  const [categories, setCategories] = useState([]);
  
  useEffect(() => {
    // Fetch categories for dropdown
    adminFetch('/api/admin/categories')
      .then(data => setCategories(data.categories || []))
      .catch(err => console.error('Failed to load categories:', err));
  }, []);

  const categoryOptions = [
    { value: '', label: '-- Select Category --' },
    ...categories.map(c => ({ value: c.category_id, label: c.title }))
  ];

  return (
    <CatalogManager
      entityType="tiles"
      title="Homepage Tiles"
      icon="🎯"
      columns={[
        { key: 'tile_id', label: 'ID' },
        { key: 'short_title', label: 'Short Title' },
        { key: 'full_title', label: 'Full Title' },
        { key: 'category_id', label: 'Category' },
        { key: 'icon_type', label: 'Icon' },
        { key: 'order', label: 'Order' },
        { key: 'active', label: 'Active', render: (v) => v === false ? '❌' : '✅' },
      ]}
      formFields={[
        { name: 'tile_id', label: 'Tile ID', isId: true, hint: 'Unique identifier (e.g., relationship_healing)' },
        { name: 'category_id', label: 'Category', type: 'select', options: categoryOptions, hint: 'Select parent category' },
        { name: 'short_title', label: 'Short Title', hint: 'Shown on tile (e.g., Healing)' },
        { name: 'full_title', label: 'Full Title', hint: 'Full name (e.g., Relationship Healing)' },
        { name: 'icon_type', label: 'Icon Type', hint: 'Icon name: healing, heart, rings, chat, family, breakup, compass, briefcase, wallet, clock, stress, office, energy, sleep, emotional, wellness' },
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
      { name: 'rating', label: 'Rating', type: 'number', default: 4.5 },
      { name: 'total_consults', label: 'Total Consults', type: 'number', default: 0 },
      { name: 'topics', label: 'Topics', type: 'array', hint: 'Topic IDs this expert can serve' },
      { name: 'photo_url', label: 'Photo URL' },
      { name: 'tags', label: 'Tags', type: 'array' },
      { name: 'active', label: 'Active', type: 'checkbox', default: true },
    ]}
  />
);

// Remedies Manager
const RemediesCatalogManager = () => (
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
      { name: 'expert_name', label: 'Expert Name (optional)' },
      { name: 'expert_title', label: 'Expert Title (optional)' },
      { name: 'expert_bio', label: 'Expert Bio (optional)', type: 'textarea' },
      { name: 'featured', label: 'Featured', type: 'checkbox', default: false },
      { name: 'active', label: 'Active', type: 'checkbox', default: true },
    ]}
  />
);

// Tiers Manager
const TiersManager = () => (
  <CatalogManager
    entityType="tiers"
    title="Packages / Tiers"
    icon="📦"
    columns={[
      { key: 'tier_id', label: 'ID' },
      { key: 'name', label: 'Name' },
      { key: 'topic_id', label: 'Topic' },
      { key: 'price', label: 'Price', render: (v) => formatCurrency(v) },
      { key: 'duration_weeks', label: 'Duration' },
      { key: 'calls_included', label: 'Calls' },
      { key: 'popular', label: 'Popular', render: (v) => v ? '⭐' : '' },
      { key: 'active', label: 'Active', render: (v) => v === false ? '❌' : '✅' },
    ]}
    formFields={[
      { name: 'tier_id', label: 'Tier ID', isId: true, hint: 'Unique identifier (e.g., career_focussed)' },
      { name: 'name', label: 'Display Name', hint: 'e.g., Focussed, Supported, Comprehensive' },
      { name: 'topic_id', label: 'Topic ID', hint: 'Which topic this tier belongs to' },
      { name: 'price', label: 'Price (INR)', type: 'number' },
      { name: 'duration_weeks', label: 'Duration (weeks)', type: 'number', default: 4 },
      { name: 'calls_included', label: 'Calls Included', type: 'number', default: 2 },
      { name: 'call_duration_mins', label: 'Call Duration (mins)', type: 'number', default: 30 },
      { name: 'features', label: 'Features', type: 'array', hint: 'Comma-separated feature list' },
      { name: 'description', label: 'Description', type: 'textarea' },
      { name: 'popular', label: 'Mark as Popular', type: 'checkbox', default: false },
      { name: 'active', label: 'Active', type: 'checkbox', default: true },
    ]}
  />
);

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
