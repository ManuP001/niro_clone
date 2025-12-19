/**
 * Auth helper utilities for managing JWT tokens and authenticated API calls.
 */

const AUTH_TOKEN_KEY = 'auth_token';
const USER_ID_KEY = 'user_id';

/**
 * Get the stored JWT token
 */
export const getAuthToken = () => {
  return localStorage.getItem(AUTH_TOKEN_KEY);
};

/**
 * Get the stored user ID
 */
export const getUserId = () => {
  return localStorage.getItem(USER_ID_KEY);
};

/**
 * Save auth token and user ID
 */
export const setAuthToken = (token, userId) => {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
  localStorage.setItem(USER_ID_KEY, userId);
};

/**
 * Clear auth tokens (logout)
 */
export const clearAuthToken = () => {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(USER_ID_KEY);
};

/**
 * Check if user is logged in
 */
export const isAuthenticated = () => {
  return !!getAuthToken();
};

/**
 * Make an authenticated API call
 * Automatically adds Authorization header with Bearer token
 */
export const authenticatedFetch = async (url, options = {}) => {
  const token = getAuthToken();
  
  if (!token) {
    throw new Error('Not authenticated');
  }

  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
  };

  return fetch(url, {
    ...options,
    headers,
  });
};

/**
 * Get current user info from backend
 */
export const getCurrentUser = async (backendUrl) => {
  const token = getAuthToken();
  
  if (!token) {
    return null;
  }

  try {
    const response = await authenticatedFetch(`${backendUrl}/api/auth/me`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      clearAuthToken();
      return null;
    }

    const data = await response.json();
    return data.ok ? data.user : null;
  } catch (err) {
    console.error('Error getting current user:', err);
    return null;
  }
};

/**
 * Get user profile
 */
export const getUserProfile = async (backendUrl, token) => {
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${backendUrl}/api/profile/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    return data.ok ? data.profile : null;
  } catch (err) {
    console.error('Error getting profile:', err);
    return null;
  }
};
