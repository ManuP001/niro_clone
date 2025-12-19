import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../../config';

const LoginScreen = ({ onLoginSuccess }) => {
  const [identifier, setIdentifier] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    console.log('LoginScreen initialized with BACKEND_URL:', BACKEND_URL);
  }, []);

  const handleContinue = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const url = `${BACKEND_URL}/api/auth/identify`;
      console.log('Identifying user at:', url);

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier }),
      });

      const data = await response.json();
      console.log('Identify response:', response.status, data);

      if (!response.ok || !data.ok) {
        setError(data.detail || 'Failed to login');
        return;
      }

      // Save token and user_id to localStorage
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('user_id', data.user_id);

      console.log('Login successful, calling onLoginSuccess');
      // Call success callback
      onLoginSuccess(data.token, data.user_id);
    } catch (err) {
      setError('Network error. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-full bg-white flex flex-col items-center justify-center px-4">
      {/* Header */}
      <div className="mb-12 text-center">
        <div className="w-12 h-12 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-white text-lg font-bold">N</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Niro.AI</h1>
        <p className="text-gray-600">Your personal astro guide</p>
      </div>

      {/* Login form container */}
      <div className="w-full max-w-sm">
        <form onSubmit={handleContinue} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email or Phone
            </label>
            <input
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="your@email.com or +91 9876543210"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none text-base"
              required
            />
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !identifier.trim()}
            className="w-full bg-emerald-600 text-white py-3 rounded-lg font-medium hover:bg-emerald-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Continuing...' : 'Continue'}
          </button>
        </form>
      </div>

      {/* Footer */}
      <div className="absolute bottom-6 text-center text-xs text-gray-500">
        <p>By continuing, you agree to our Terms & Privacy Policy</p>
      </div>
    </div>
  );
};

export default LoginScreen;
