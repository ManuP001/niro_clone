// Determine backend URL based on environment
// In production (getniro.ai), use same origin for API calls
// In development/preview, use REACT_APP_BACKEND_URL
const getBackendUrl = () => {
  const currentOrigin = window.location.origin;
  
  // Production domains - use same origin
  if (currentOrigin.includes('getniro.ai') || currentOrigin.includes('.emergent.host')) {
    return currentOrigin;
  }
  
  // Preview/development - use env variable or localhost
  return process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
};

export const BACKEND_URL = getBackendUrl();
