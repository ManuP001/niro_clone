import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../../config';

/**
 * Admin Dashboard - Main entry point
 * Routes between login, dashboard, users, orders, plans, remedies
 */

// Store admin token in sessionStorage
const getAdminToken = () => sessionStorage.getItem('niro_admin_token');
const setAdminToken = (token) => sessionStorage.setItem('niro_admin_token', token);
const clearAdminToken = () => sessionStorage.removeItem('niro_admin_token');

// API helper
const adminFetch = async (endpoint, options = {}) => {
  const token = getAdminToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'X-Admin-Token': token }),
    ...options.headers,
  };
  
  const response = await fetch(`${BACKEND_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  if (response.status === 401) {
    clearAdminToken();
    window.location.reload();
  }
  
  return response.json();
};

// Format currency
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
  }).format(amount);
};

// Format date
const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// ============================================================================
// LOGIN COMPONENT
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
          <h1 className="text-2xl font-bold text-gray-800">🔒 Niro Admin</h1>
          <p className="text-gray-500 mt-2">Enter your credentials to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              placeholder="Enter username"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              placeholder="Enter password"
              required
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm text-center bg-red-50 p-2 rounded">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-teal-600 text-white font-semibold rounded-lg hover:bg-teal-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};

// ============================================================================
// STATS CARDS
// ============================================================================
const StatCard = ({ title, value, icon, color = 'teal' }) => (
  <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-500 text-sm">{title}</p>
        <p className={`text-2xl font-bold text-${color}-600 mt-1`}>{value}</p>
      </div>
      <div className={`w-12 h-12 bg-${color}-100 rounded-xl flex items-center justify-center text-2xl`}>
        {icon}
      </div>
    </div>
  </div>
);

// ============================================================================
// DASHBOARD HOME
// ============================================================================
const DashboardHome = ({ stats, environment, onNavigate }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Dashboard Overview</h2>
        <span className="text-sm text-gray-500">
          Showing: <span className="font-medium text-teal-600">{environment}</span> data
        </span>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Users" value={stats?.total_users || 0} icon="👥" />
        <StatCard title="Total Orders" value={stats?.total_orders || 0} icon="💰" />
        <StatCard title="Active Plans" value={stats?.active_plans || 0} icon="📦" />
        <StatCard title="Revenue" value={formatCurrency(stats?.total_revenue_inr || 0)} icon="💵" color="green" />
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard title="Users Today" value={stats?.users_today || 0} icon="🆕" color="blue" />
        <StatCard title="Chat Threads" value={stats?.total_threads || 0} icon="💬" color="purple" />
        <StatCard title="Remedy Orders" value={stats?.remedy_orders || 0} icon="🙏" color="orange" />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <button
          onClick={() => onNavigate('users')}
          className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:border-teal-300 transition-colors text-left"
        >
          <span className="text-2xl">👥</span>
          <p className="font-medium text-gray-800 mt-2">View Users</p>
        </button>
        <button
          onClick={() => onNavigate('orders')}
          className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:border-teal-300 transition-colors text-left"
        >
          <span className="text-2xl">💰</span>
          <p className="font-medium text-gray-800 mt-2">View Orders</p>
        </button>
        <button
          onClick={() => onNavigate('plans')}
          className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:border-teal-300 transition-colors text-left"
        >
          <span className="text-2xl">📦</span>
          <p className="font-medium text-gray-800 mt-2">View Plans</p>
        </button>
        <button
          onClick={() => onNavigate('remedies')}
          className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:border-teal-300 transition-colors text-left"
        >
          <span className="text-2xl">🙏</span>
          <p className="font-medium text-gray-800 mt-2">Remedy Orders</p>
        </button>
      </div>
    </div>
  );
};

// ============================================================================
// USERS LIST
// ============================================================================
const UsersList = ({ environment }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});
  const [search, setSearch] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await adminFetch(
        `/api/admin/users?page=${page}&limit=20&environment=${environment}${search ? `&search=${search}` : ''}`
      );
      setUsers(data.users || []);
      setPagination(data.pagination || {});
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [page, environment]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadUsers();
  };

  const exportCSV = () => {
    window.open(`${BACKEND_URL}/api/admin/export/users?environment=${environment}&x-admin-token=${getAdminToken()}`, '_blank');
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Users ({pagination.total || 0})</h2>
        <button
          onClick={exportCSV}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
        >
          Export CSV
        </button>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by email or name..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
        />
        <button type="submit" className="px-4 py-2 bg-teal-600 text-white rounded-lg">
          Search
        </button>
      </form>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">DOB</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Purchases</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-500">Loading...</td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-500">No users found</td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr
                    key={user.user_id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedUser(user)}
                  >
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{user.name || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{user.email || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{user.dob || '-'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${user.profile_complete ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                        {user.profile_complete ? 'Complete' : 'Incomplete'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{user.purchase_count || 0}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{formatDate(user.created_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination.pages > 1 && (
          <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-600">
              Page {page} of {pagination.pages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(pagination.pages, p + 1))}
              disabled={page === pagination.pages}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* User Detail Modal */}
      {selectedUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedUser(null)}>
          <div className="bg-white rounded-xl max-w-lg w-full max-h-[80vh] overflow-y-auto p-6" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold">User Details</h3>
              <button onClick={() => setSelectedUser(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Name</p>
                  <p className="font-medium">{selectedUser.name || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Email</p>
                  <p className="font-medium">{selectedUser.email || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Date of Birth</p>
                  <p className="font-medium">{selectedUser.dob || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Time of Birth</p>
                  <p className="font-medium">{selectedUser.tob || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Place of Birth</p>
                  <p className="font-medium">{selectedUser.pob || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Gender</p>
                  <p className="font-medium capitalize">{selectedUser.gender || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Marital Status</p>
                  <p className="font-medium capitalize">{selectedUser.marital_status || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Total Spent</p>
                  <p className="font-medium text-green-600">{formatCurrency(selectedUser.total_spent || 0)}</p>
                </div>
              </div>
              
              <div className="pt-4 border-t">
                <p className="text-xs text-gray-500">User ID</p>
                <p className="font-mono text-sm">{selectedUser.user_id}</p>
              </div>
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
const OrdersList = ({ environment }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});
  const [revenue, setRevenue] = useState(0);

  const loadOrders = async () => {
    setLoading(true);
    try {
      const data = await adminFetch(`/api/admin/orders?page=${page}&limit=20&environment=${environment}`);
      setOrders(data.orders || []);
      setPagination(data.pagination || {});
      setRevenue(data.revenue_inr || 0);
    } catch (err) {
      console.error('Failed to load orders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, [page, environment]);

  const exportCSV = () => {
    window.open(`${BACKEND_URL}/api/admin/export/orders?environment=${environment}&x-admin-token=${getAdminToken()}`, '_blank');
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-800">Package Orders ({pagination.total || 0})</h2>
          <p className="text-sm text-green-600 font-medium">Total Revenue: {formatCurrency(revenue)}</p>
        </div>
        <button
          onClick={exportCSV}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
        >
          Export CSV
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tier</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-gray-500">Loading...</td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-gray-500">No orders found</td>
                </tr>
              ) : (
                orders.map((order) => (
                  <tr key={order.order_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-600">{order.order_id}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{order.user_email || order.user_name || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 capitalize">{order.topic_id || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 capitalize">{order.tier_level || '-'}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{formatCurrency((order.amount || 0) / 100)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        order.status === 'paid' ? 'bg-green-100 text-green-700' :
                        order.status === 'created' ? 'bg-yellow-100 text-yellow-700' :
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
          <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-600">Page {page} of {pagination.pages}</span>
            <button
              onClick={() => setPage(p => Math.min(pagination.pages, p + 1))}
              disabled={page === pagination.pages}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// PLANS LIST
// ============================================================================
const PlansList = ({ environment }) => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});

  const loadPlans = async () => {
    setLoading(true);
    try {
      const data = await adminFetch(`/api/admin/plans?page=${page}&limit=20&environment=${environment}`);
      setPlans(data.plans || []);
      setPagination(data.pagination || {});
    } catch (err) {
      console.error('Failed to load plans:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlans();
  }, [page, environment]);

  const exportCSV = () => {
    window.open(`${BACKEND_URL}/api/admin/export/plans?environment=${environment}&x-admin-token=${getAdminToken()}`, '_blank');
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Plans ({pagination.total || 0})</h2>
        <button
          onClick={exportCSV}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
        >
          Export CSV
        </button>
      </div>

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
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-gray-500">Loading...</td>
                </tr>
              ) : plans.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-gray-500">No plans found</td>
                </tr>
              ) : (
                plans.map((plan) => (
                  <tr key={plan.plan_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-600">{plan.plan_id}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{plan.user_email || plan.user_name || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 capitalize">{plan.topic_id || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 capitalize">{plan.tier_level || '-'}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{formatCurrency(plan.price_paid_inr || 0)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        plan.status === 'active' ? 'bg-green-100 text-green-700' :
                        plan.status === 'expired' ? 'bg-gray-100 text-gray-700' :
                        'bg-red-100 text-red-700'
                      }`}>
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

        {pagination.pages > 1 && (
          <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-600">Page {page} of {pagination.pages}</span>
            <button
              onClick={() => setPage(p => Math.min(pagination.pages, p + 1))}
              disabled={page === pagination.pages}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// REMEDY ORDERS LIST
// ============================================================================
const RemedyOrdersList = ({ environment }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});

  const loadOrders = async () => {
    setLoading(true);
    try {
      const data = await adminFetch(`/api/admin/remedy-orders?page=${page}&limit=20&environment=${environment}`);
      setOrders(data.orders || []);
      setPagination(data.pagination || {});
    } catch (err) {
      console.error('Failed to load remedy orders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrders();
  }, [page, environment]);

  const exportCSV = () => {
    window.open(`${BACKEND_URL}/api/admin/export/remedies?environment=${environment}&x-admin-token=${getAdminToken()}`, '_blank');
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Remedy Orders ({pagination.total || 0})</h2>
        <button
          onClick={exportCSV}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
        >
          Export CSV
        </button>
      </div>

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
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan="8" className="px-4 py-8 text-center text-gray-500">Loading...</td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-4 py-8 text-center text-gray-500">No remedy orders found</td>
                </tr>
              ) : (
                orders.map((order) => (
                  <tr key={order.remedy_order_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-600">{order.remedy_order_id}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{order.user_email || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{order.remedy_name || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 capitalize">{order.remedy_category || '-'}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{formatCurrency(order.price_inr || 0)}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 capitalize">{order.source || 'direct'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        order.status === 'paid' ? 'bg-green-100 text-green-700' :
                        order.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-blue-100 text-blue-700'
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
          <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-600">Page {page} of {pagination.pages}</span>
            <button
              onClick={() => setPage(p => Math.min(pagination.pages, p + 1))}
              disabled={page === pagination.pages}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
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
  const [environment, setEnvironment] = useState('all');
  const [loading, setLoading] = useState(true);

  // Check if already logged in
  useEffect(() => {
    const checkAuth = async () => {
      const token = getAdminToken();
      if (token) {
        try {
          const data = await adminFetch('/api/admin/verify');
          if (data.ok) {
            setIsLoggedIn(true);
          }
        } catch (err) {
          clearAdminToken();
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  // Load stats when logged in
  useEffect(() => {
    if (isLoggedIn) {
      loadStats();
    }
  }, [isLoggedIn, environment]);

  const loadStats = async () => {
    try {
      const data = await adminFetch(`/api/admin/stats?environment=${environment}`);
      setStats(data.stats);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleLogout = () => {
    clearAdminToken();
    setIsLoggedIn(false);
    setCurrentPage('dashboard');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (!isLoggedIn) {
    return <AdminLogin onLogin={() => setIsLoggedIn(true)} />;
  }

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'users', label: 'Users', icon: '👥' },
    { id: 'orders', label: 'Orders', icon: '💰' },
    { id: 'plans', label: 'Plans', icon: '📦' },
    { id: 'remedies', label: 'Remedies', icon: '🙏' },
  ];

  const renderContent = () => {
    switch (currentPage) {
      case 'users':
        return <UsersList environment={environment} />;
      case 'orders':
        return <OrdersList environment={environment} />;
      case 'plans':
        return <PlansList environment={environment} />;
      case 'remedies':
        return <RemedyOrdersList environment={environment} />;
      default:
        return <DashboardHome stats={stats} environment={environment} onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold">Niro Admin</h1>
        </div>
        
        <nav className="flex-1 p-4">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition-colors ${
                currentPage === item.id ? 'bg-teal-600' : 'hover:bg-gray-800'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800 capitalize">{currentPage}</h2>
          
          {/* Environment Filter */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Environment:</span>
            <select
              value={environment}
              onChange={(e) => setEnvironment(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-teal-500"
            >
              <option value="all">All</option>
              <option value="production">Production</option>
              <option value="preview">Preview</option>
            </select>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}
