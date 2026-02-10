// Determine backend URL based on environment
// In production (getniro.ai), use same origin for API calls
// In development/preview, use REACT_APP_BACKEND_URL

// Use a getter function to ensure window is available
export const getBackendUrl = () => {
  // Check if window is available (for SSR compatibility)
  if (typeof window === 'undefined') {
    return process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
  }
  
  const currentOrigin = window.location.origin;
  
  // Production domains - use same origin
  if (currentOrigin.includes('getniro.ai') || currentOrigin.includes('.emergent.host')) {
    return currentOrigin;
  }
  
  // Preview/development - use env variable or localhost
  return process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
};

// Export as a constant for backwards compatibility, but also export the function
export const BACKEND_URL = getBackendUrl();
